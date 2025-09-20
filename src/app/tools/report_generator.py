"""report_generator.py

This module handles the generation of SRE reports from log analysis.
"""

import logging
import os
from datetime import datetime

from app.database.vector_db import QdrantDatabaseClient
from app.prompts import SRE_REPORT_PROMPT, get_sre_analysis_prompt
from app.tools.k8_client import KubernetesClient
from app.tools.llm_client import OpenAIChatClient
from app.tools.loki_client import LokiClient

logger = logging.getLogger(__name__)


class LogReportGenerator:
    def __init__(
        self,
        openai_client: OpenAIChatClient,
        kube_client: KubernetesClient,
        loki_client: LokiClient,
        max_logs: int = 20,
    ):
        self.openai_client = openai_client
        self.kube_client = kube_client
        self.loki_client = loki_client
        self.database_client = QdrantDatabaseClient()
        self.max_logs = max_logs

        self.reports_dir = "/reports"

        os.makedirs(self.reports_dir, exist_ok=True)

        logger.info(f"Reports will be saved to: {self.reports_dir}")
        logger.info(f"Maximum logs to analyze: {self.max_logs}")

    def _format_markdown(self, report: dict) -> str:
        """Format the report as markdown."""
        timestamp = datetime.fromisoformat(report["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")

        markdown = f"""# SRE Log Analysis Report
Generated on: {date_str} at {time_str}
Time Period: {report['time_period']}

## Log Analysis
{report['log_analysis']}

## Pod Statuses
"""

        pod_statuses = report.get("pod_statuses", {})
        if not pod_statuses:
            markdown += "\nNo pod status information available.\n"
        else:
            for pod, status in pod_statuses.items():
                markdown += f"\n### {pod}\n"
                if isinstance(status, dict):
                    markdown += f"Status: {status.get('phase', 'Unknown')}\n"
                    if "error" in status:
                        markdown += f"Error: {status['error']}\n"
                else:
                    markdown += f"Status: {status}\n"

        markdown += "\n## Summary\n"
        markdown += f"Issues Found: {'Yes' if report.get('issues_found', False) else 'No'}\n"

        return markdown

    def _save_report(self, markdown: str, timestamp: datetime):
        """Save the report as a markdown file."""
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H-%M-%S")
        filename = f"report_{date_str}_{time_str}.md"
        filepath = os.path.join(self.reports_dir, filename)

        try:
            with open(filepath, "w") as f:
                f.write(markdown)
        except IOError as e:
            logger.error(f"Failed to save report to {filepath}: {e}")
            raise

        logger.info(f"Report saved to {filepath}")
        return filepath

    def _analyze_logs(self, logs: list[dict]) -> str:
        """Analyze logs using LLM to identify issues and generate insights."""
        if len(logs) > self.max_logs:
            logs = logs[: self.max_logs]
            logger.info(f"Limiting logs to {self.max_logs} entries to reduce token usage")

        pod_health_data = self._get_pod_status()

        messages = [
            {"role": "system", "content": SRE_REPORT_PROMPT},
            {
                "role": "user",
                "content": get_sre_analysis_prompt(logs, pod_health_data),
            },
        ]

        return self.openai_client.chat(messages)

    def _get_pod_status(self, namespace: str = "default") -> dict:
        """Get current status of all pods in the namespace."""
        pods = self.kube_client.list_pods(namespace)
        if pods is None:
            logger.error("No pods found")
            return {"pods": "No pods found"}

        pod_statuses = {}

        for pod in pods:
            status = self.kube_client.get_pod_health(pod, namespace)
            pod_statuses[pod] = status

        return pod_statuses

    def generate_report(self, hours: int = 1, namespace: str = "default") -> dict:
        """Generate a comprehensive SRE report."""
        logger.info(f"Generating report for the last {hours} hours")

        # TODO: More detailed vector db search
        recent_logs = self.database_client.search(query_text="CPU", limit=100)

        pod_statuses = self._get_pod_status(namespace)

        analysis = self._analyze_logs(recent_logs)

        timestamp = datetime.now()
        report = {
            "timestamp": timestamp.isoformat(),
            "time_period": f"Last {hours} hours",
            "log_analysis": analysis,
            "pod_statuses": pod_statuses,
            "issues_found": len(recent_logs) > 0,
        }

        markdown = self._format_markdown(report)
        self._save_report(markdown, timestamp)

        logger.info("Report generation completed")
        return report
