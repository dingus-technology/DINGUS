"""log_scanner.py
This file is used to parse logs for bugs.
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta

from app.connectors import fetch_loki_logs
from app.database.vector_db import QdrantDatabaseClient
from app.settings import OPENAI_MODEL
from app.tools.k8_client import KubernetesClient
from app.tools.llm_client import OpenAIChatClient
from app.tools.loki_client import LokiClient

logger = logging.getLogger(__name__)

BUGS_DIR = "/data/bugs/"
LOG_EXPERT_SYSTEM_PROMPT = (
    "You are an expert at analysinig logs and identifying issues in production monitoring systems."
)
LOG_SCANNER_SYSTEM_PROMPT = """
You are a debugging expert.
From the following logs, identify exactly one bug (the most recent or most critical).
If you find a bug, return your answer as a JSON object, and always encase your response in triple backticks with 'json' (i.e., ```json ... ```).
Do not provide an explaination, only JSON.
The JSON must have the following fields:
 - file (str, file the error occurred)
 - line (int, line the error occurred)
 - summary (str, very short human-friendly outline of the issue)
 - human_explanation (str, a detailed human-friendly explanation and fix)
 - evidence (list, log lines, up to 10, most relevant, without the boring bits)
 - message (str, the actual core log message that caused the bug the user needs to know)
 - bug_found_time (str, ISO8601, when the bug occurred in the logs)

If no bug is found, return {no_bug: true}.
Example:
```json
{
    file: route/to/main.py,
    line: 42,
    summary: Null pointer exception,
    human_explanation: This error occurs when...,
    evidence: ["[ERROR] service: Null pointer exception at line 42", "[WARN] service: High CPU usage detected"],
    message: [ERROR] monitoring-app: {"timestamp": "2025-07-26 14:29:47", "level": "ERROR", "filename": "log_data.py", "line": 54, "message": "Kubernetes pod in danger"},
    bug_found_time: 2024-06-01T12:00:00
}
```
"""  # noqa: E501


class LogScanner(LokiClient, KubernetesClient):
    def __init__(self, loki_base_url, job_name, open_ai_api_key, kube_config_path=None, log_limit=100):
        LokiClient.__init__(self, loki_base_url=loki_base_url, job_name=job_name)
        # Initialize Kubernetes only if a path is provided; otherwise, skip
        self.k8s_enabled = bool(kube_config_path)
        if self.k8s_enabled:
            KubernetesClient.__init__(self, kube_config_path=kube_config_path)
            # If init failed, api_client will be None per KubernetesClient
            self.k8s_enabled = getattr(self, "api_client", None) is not None
        else:
            # Provide a stub so any accidental calls won't break
            self.api_client = None
        self.log_limit = log_limit
        self.openai_client = OpenAIChatClient(api_key=open_ai_api_key, model=OPENAI_MODEL)
        self.vector_db = QdrantDatabaseClient()
        self.last_bug_signature = None
        self._running = False

    async def run_once(self):
        logger.info("Running LogScanner once")
        try:
            now = datetime.now()
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            logs = []
            for level in ["ERROR", "WARN"]:
                streams = fetch_loki_logs(
                    loki_base_url=self.loki_base_url,
                    job_name=self.job_name,
                    start_time=start_time,
                    end_time=end_time,
                    limit=self.log_limit,
                    level=level,
                )
                if streams:
                    logs.extend(streams)
            vector_logs = self._get_recent_logs_from_vector_db()
            bug_info = self._analyze_logs_with_llm(logs + vector_logs)
            if bug_info:
                self._save_if_new_bug(bug_info)
        except Exception as e:
            logger.error(f"Error in LogScanner run_once: {e}")

    def stop(self):
        self._running = False

    def _get_recent_logs_from_vector_db(self):
        # TODO: Make query_text configurable or smarter
        query_text = "ERROR OR WARN OR bug OR exception"
        logs = self.vector_db.search(query_text=query_text, limit=self.log_limit)
        # TODO: Format logs as needed for LLM prompt
        return logs

    def _extract_log_messages(self, logs):
        """Extract actual log messages from Loki log structure, returning both full and message-only."""
        log_messages = []
        for log_entry in logs:
            if isinstance(log_entry, dict):
                # Handle Loki log structure
                if "values" in log_entry and "stream" in log_entry:
                    for timestamp, message in log_entry["values"]:
                        stream_info = log_entry["stream"]
                        level = stream_info.get("level", "INFO")
                        service = stream_info.get("service", "unknown")
                        full = f"[{level}] {service}: {message}"
                        log_messages.append({"full": full, "message": message})
                # Handle vector DB logs (already formatted)
                elif "message" in log_entry:
                    msg = str(log_entry["message"])
                    log_messages.append({"full": msg, "message": msg})
                # Handle simple string logs
                elif isinstance(log_entry, str):
                    log_messages.append({"full": log_entry, "message": log_entry})
                # Handle other dict formats
                else:
                    msg = str(log_entry)
                    log_messages.append({"full": msg, "message": msg})
            elif isinstance(log_entry, str):
                log_messages.append({"full": log_entry, "message": log_entry})
            else:
                msg = str(log_entry)
                log_messages.append({"full": msg, "message": msg})
        return log_messages

    def _format_logs_for_llm(self, log_messages):
        """Format log messages for LLM analysis."""
        formatted_logs = []
        for i, msg in enumerate(log_messages, 1):
            # Use the full log line for LLM context
            formatted_logs.append(f"Log {i}: {msg['full']}")
        return "\n".join(formatted_logs)

    def _analyze_logs_with_llm(self, logs):
        # Extract actual log messages for evidence
        log_messages = self._extract_log_messages(logs)
        evidence = log_messages[-10:] if len(log_messages) > 10 else log_messages  # last 10 logs as evidence

        # Format logs for LLM analysis
        formatted_logs = self._format_logs_for_llm(log_messages)

        messages = [
            {
                "role": "system",
                "content": LOG_SCANNER_SYSTEM_PROMPT,
            },
            {"role": "user", "content": f"Please analyze the following logs:\n\n{formatted_logs}"},
        ]
        response = self.openai_client.chat(messages, max_tokens=1500)
        try:
            # Extract the JSON block from the LLM response
            import re as _re

            match = _re.search(r"```json\s*(\{[\s\S]+?\})\s*```", response)
            if match:
                json_str = match.group(1)
                bug_info = json.loads(json_str)
            else:
                bug_info = json.loads(response)  # fallback if not encased
            if bug_info.get("no_bug"):
                return None
            bug_info["scan_time"] = datetime.now().isoformat()
            bug_info["raw_response"] = response
            # Ensure evidence contains the actual log messages (dicts)
            bug_info["evidence"] = evidence
        except Exception:
            bug_info = self._extract_bug_info_from_response(response)
            bug_info["raw_response"] = response
            bug_info["evidence"] = evidence
            bug_info["human_explanation"] = self._extract_human_explanation_from_response(response)
            bug_info["scan_time"] = datetime.now().isoformat()
            bug_info["bug_found_time"] = bug_info["scan_time"]
        try:
            ai_insights_prompt = f"""
Given the following bug and logs, provide the following in markdown format:
(do not write 'markdown' in your response)
- Root cause analysis (short paragraph)
- Step-by-step fix instructions (numbered list)
- Potential impact if not fixed (short paragraph)
- Any related files or log lines to check (list)
- Avoid starting with '- **Root Cause Analysis**'.

Bug: {json.dumps(bug_info)}\n\nLogs:\n{formatted_logs}
                """
            ai_insights_response = self.openai_client.chat(
                [
                    {"role": "system", "content": LOG_EXPERT_SYSTEM_PROMPT},
                    {"role": "user", "content": ai_insights_prompt},
                ],
                max_tokens=200,
            )
            bug_info["ai_insights"] = ai_insights_response
        except Exception as e:
            bug_info["ai_insights"] = f"Failed to get AI insights: {e}"
        return bug_info

    def _extract_bug_info_from_response(self, response):
        bug_info = {}
        file_line_match = re.search(r"(File|file)[\s:]+([\w/\\.]+)[\s,;:]+(line|Line)[\s:]+(\d+)", response)
        if file_line_match:
            bug_info["file"] = file_line_match.group(2)
            bug_info["line"] = int(file_line_match.group(4))
        summary_match = re.search(r"(Summary|summary|Issue|issue)[\s:]+(.+?)(?:Explanation:|$)", response, re.DOTALL)
        if summary_match:
            bug_info["summary"] = summary_match.group(2).strip()
        else:
            bug_info["summary"] = response.strip()
        return bug_info

    def _extract_human_explanation_from_response(self, response):
        explanation_match = re.search(r"Explanation:(.+)", response, re.DOTALL)
        if explanation_match:
            return explanation_match.group(1).strip()
        return "No explanation provided."

    def _save_if_new_bug(self, bug_info):
        os.makedirs(BUGS_DIR, exist_ok=True)
        bug_signature = f"{bug_info.get('file','')}-{bug_info.get('line','')}-{bug_info.get('summary','')[:50]}"
        if bug_signature and bug_signature != self.last_bug_signature:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bug_{timestamp}.json"
            filepath = os.path.join(BUGS_DIR, filename)
            with open(filepath, "w") as f:
                json.dump(bug_info, f)
            self.last_bug_signature = bug_signature
