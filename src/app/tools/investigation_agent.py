"""investigation_agent.py

This module contains the investigation agent that performs systematic debugging.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from app.settings import OPENAI_API_KEY, OPENAI_MODEL
from app.tools.investigation_tools import InvestigationTools
from app.tools.llm_client import OpenAIChatClient

logger = logging.getLogger(__name__)

INVESTIGATION_SYSTEM_PROMPT = """
You are an expert SRE (Site Reliability Engineer) debugging agent.
Your job is to systematically investigate issues in production systems.

When given a bug report, you will:
1. Analyze the bug description and error message
2. Determine what investigation steps are needed
3. Execute those steps using available tools
4. Correlate findings to identify root causes
5. Provide a comprehensive analysis and recommendations

Available investigation tools:
- check_database_connectivity: Test database connections
- check_system_resources: Check CPU, memory, disk usage
- check_network_connectivity: Test network connectivity
- check_service_health: Check if services are responding
- check_docker_containers: Check Docker container status
- check_kubernetes_pods: Check Kubernetes pod status
- check_log_patterns: Search for specific patterns in logs
- check_disk_space: Check disk space usage
- check_process_status: Check if specific processes are running
- check_environment_variables: Check if required env vars are set

Always follow a systematic approach:
1. Start with basic system health checks
2. Check specific services mentioned in the error
3. Look for correlations between different issues
4. Provide actionable recommendations

Your response should be structured and include:
- Investigation steps taken
- Findings and correlations
- Root cause analysis
- Recommended fixes
- Prevention measures
"""


class InvestigationAgent:
    """Agent that performs systematic debugging investigations."""

    def __init__(self):
        self.tools = InvestigationTools()
        self.llm_client = OpenAIChatClient(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        self.investigation_id = None

    def start_investigation(self, bug_info: dict[str, Any]) -> dict[str, Any]:
        """Start a new investigation for a bug."""
        self.investigation_id = f"investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create investigation context
        investigation_context = {
            "investigation_id": self.investigation_id,
            "bug_info": bug_info,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
        }

        logger.info(f"Starting investigation {self.investigation_id} for bug: {bug_info.get('summary', 'Unknown')}")

        # Perform systematic investigation
        investigation_results = self._perform_investigation(bug_info)

        logger.info("Investigation completed, generating analysis...")
        logger.info(f"Investigation results structure: {list(investigation_results.keys())}")

        # Generate comprehensive analysis
        analysis = self._generate_analysis(bug_info, investigation_results)

        logger.info(f"Analysis completed. Severity: {analysis.get('severity', {}).get('level', 'Unknown')}")

        # Complete investigation
        investigation_context.update(
            {
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                "investigation_results": investigation_results,
                "analysis": analysis,
            }
        )

        return investigation_context

    def _determine_investigation_steps(
        self, summary: str, message: str, evidence: list[str], bug_info: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Determine what investigation steps to perform based on the bug."""

        # Create context for LLM to understand the bug
        bug_context = {
            "summary": summary,
            "message": message,
            "evidence": evidence,
            "file": bug_info.get("file", ""),
            "line": bug_info.get("line", 0),
            "bug_info": bug_info,
        }

        # Use LLM to determine investigation strategy
        investigation_strategy = self._generate_investigation_strategy(bug_context)

        # Parse the LLM response to get ordered steps
        steps = self._parse_investigation_strategy(investigation_strategy, bug_context)

        return steps

    def _generate_investigation_strategy(self, bug_context: dict[str, Any]) -> str:
        """Use LLM to generate investigation strategy and explanations."""

        strategy_prompt = f"""
You are an expert SRE (Site Reliability Engineer) debugging agent.
Analyze this bug and determine the optimal investigation strategy.

BUG CONTEXT:
{json.dumps(bug_context, indent=2)}

AVAILABLE INVESTIGATION TOOLS:
1. Environment Variables Check - Check if required environment variables are set
2. Code Context Analysis - Analyze code around the error line
3. Network Connectivity Check - Test basic network connectivity
4. Loki Connectivity Check - Check if Loki log aggregation is reachable
5. Grafana Connectivity Check - Check if Grafana is reachable
6. Service Health Check - Check service health and response
7. Database Connection Test - Test database connectivity
8. Kubernetes Pod Status - Check Kubernetes pod status and health
9. Kubernetes Pod Logs - Get recent logs from Kubernetes pods
10. System Resources Check - Check system resource usage
11. Recent Changes Check - Check for recent deployments or changes

INVESTIGATION PRINCIPLES:
- Start with basic context gathering (environment, code)
- Move to infrastructure checks (network, services)
- Check dependencies (databases, external services)
- Check resources and performance
- Look for recent changes that might have caused the issue
- Always explain WHY each step is important for this specific bug

Please provide a JSON response with this structure:
{{
    "investigation_strategy": "brief description of the overall approach",
    "steps": [
        {{
            "name": "tool_name",
            "description": "what this tool does",
            "explanation": "why this tool is important for this specific bug",
            "priority": "high/medium/low",
            "params": {{}} // if needed
        }}
    ],
    "expected_correlations": "what patterns or relationships we expect to find"
}}

Focus on tools that are most relevant to this specific bug type. Explain the reasoning behind each step.
"""

        try:
            response = self.llm_client.chat(
                messages=[
                    {"role": "system", "content": INVESTIGATION_SYSTEM_PROMPT},
                    {"role": "user", "content": strategy_prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            return response

        except Exception as e:
            logger.error(f"Error generating investigation strategy: {e}")
            # Fallback to basic strategy
            return self._generate_fallback_strategy(bug_context)

    def _generate_fallback_strategy(self, bug_context: dict[str, Any]) -> str:
        """Generate a fallback investigation strategy when LLM fails."""

        summary = bug_context["summary"].lower()
        message = bug_context["message"].lower()

        steps = []

        # Always start with basic context
        steps.append(
            {
                "name": "Environment Variables Check",
                "description": "Check if required environment variables are set",
                "explanation": "Environment variables are often the root cause of configuration issues",
                "priority": "high",
            }
        )

        # Code context is always useful
        if bug_context.get("file") and bug_context.get("line"):
            steps.append(
                {
                    "name": "Code Context Analysis",
                    "description": f"Analyze code around line {bug_context['line']} in {bug_context['file']}",
                    "explanation": "Understanding the code context helps identify the exact failure point",
                    "priority": "high",
                    "params": json.dumps({"file_path": bug_context["file"], "line_number": bug_context["line"]}),
                }
            )

        # Network connectivity
        steps.append(
            {
                "name": "Network Connectivity Check",
                "description": "Test basic network connectivity",
                "explanation": "Network issues are common causes of service failures",
                "priority": "high",
            }
        )

        # Add specific tools based on bug type
        if any(keyword in summary or keyword in message for keyword in ["kubernetes", "k8s", "pod", "deployment"]):
            steps.extend(
                [
                    {
                        "name": "Kubernetes Pod Status",
                        "description": "Check Kubernetes pod status and health",
                        "explanation": "Kubernetes issues require checking pod health and status",
                        "priority": "high",
                    },
                    {
                        "name": "Kubernetes Pod Logs",
                        "description": "Get recent logs from Kubernetes pods",
                        "explanation": "Pod logs provide detailed error information for Kubernetes issues",
                        "priority": "high",
                    },
                ]
            )

        if any(keyword in summary or keyword in message for keyword in ["database", "db", "postgres", "mysql"]):
            steps.append(
                {
                    "name": "Database Connection Test",
                    "description": "Test database connectivity",
                    "explanation": "Database connection issues are common and need direct testing",
                    "priority": "high",
                }
            )

        if any(keyword in summary or keyword in message for keyword in ["memory", "cpu", "disk", "resource"]):
            steps.append(
                {
                    "name": "System Resources Check",
                    "description": "Check system resource usage",
                    "explanation": "Resource exhaustion can cause various service failures",
                    "priority": "medium",
                }
            )

        if any(keyword in summary or keyword in message for keyword in ["service", "api", "http", "endpoint"]):
            steps.append(
                {
                    "name": "Service Health Check",
                    "description": "Check service health and response",
                    "explanation": "Service health checks verify if the application is responding correctly",
                    "priority": "medium",
                }
            )

        if any(keyword in summary or keyword in message for keyword in ["monitoring", "grafana", "prometheus"]):
            steps.append(
                {
                    "name": "Grafana Connectivity Check",
                    "description": "Check if Grafana is reachable",
                    "explanation": "Monitoring system issues affect our ability to track the problem",
                    "priority": "medium",
                }
            )

        steps.append(
            {
                "name": "Loki Connectivity Check",
                "description": "Check if Loki log aggregation is reachable",
                "explanation": "Log aggregation system health affects our debugging capabilities",
                "priority": "medium",
            }
        )

        steps.append(
            {
                "name": "Recent Changes Check",
                "description": "Check for recent deployments or changes",
                "explanation": "Recent changes often correlate with new issues",
                "priority": "low",
            }
        )

        return json.dumps(
            {
                "investigation_strategy": "Systematic debugging approach focusing on infrastructure and dependencies",
                "steps": steps,
                "expected_correlations": "Looking for patterns between infrastructure health and the reported issue",
            }
        )

    def _parse_investigation_strategy(
        self, strategy_response: str, bug_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Parse the LLM response to extract investigation steps."""

        try:
            # Try to parse as JSON
            strategy_data = json.loads(strategy_response)
            return strategy_data.get("steps", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM strategy response as JSON, using fallback")
            fallback_strategy = self._generate_fallback_strategy(bug_context)
            try:
                fallback_data = json.loads(fallback_strategy)
                return fallback_data.get("steps", [])
            except json.JSONDecodeError:
                return []

    def _execute_investigation_step(self, step_name: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute a specific investigation step."""
        try:
            if step_name == "Environment Variables Check":
                return self.tools.check_environment_variables()
            elif step_name == "Loki Connectivity Check":
                return self.tools.check_loki_connectivity()
            elif step_name == "Network Connectivity Check":
                return self.tools.check_network_connectivity()
            elif step_name == "Grafana Connectivity Check":
                return self.tools.check_grafana_connectivity()
            elif step_name == "Service Health Check":
                return self.tools.check_service_health("http://host.docker.internal:8000/health")
            elif step_name == "Code Context Analysis":
                file_path = params.get("file_path", "") if params else ""
                line_number = params.get("line_number", 0) if params else 0
                return self.tools.get_code_context(file_path, line_number)
            elif step_name == "Kubernetes Pod Status":
                return self.tools.check_kubernetes_pod_status()
            elif step_name == "Kubernetes Pod Logs":
                return self.tools.check_kubernetes_pod_logs()
            elif step_name == "Database Connection Test":
                return self.tools.check_database_connection()
            elif step_name == "System Resources Check":
                return self.tools.check_system_resources()
            elif step_name == "Recent Changes Check":
                return self.tools.check_recent_changes()
            else:
                return {"error": f"Unknown investigation step: {step_name}"}
        except Exception as e:
            logger.error(f"Error executing investigation step {step_name}: {e}")
            return {"error": str(e)}

    def _perform_investigation(self, bug_info: dict[str, Any]) -> dict[str, Any]:
        """Perform systematic investigation steps based on the bug."""

        # Extract key information from bug
        summary = bug_info.get("summary", "").lower()
        message = bug_info.get("message", "").lower()
        evidence = bug_info.get("evidence", [])

        # Determine investigation steps based on bug type
        investigation_steps = self._determine_investigation_steps(summary, message, evidence, bug_info)

        # Get the investigation strategy for display
        bug_context = {
            "summary": summary,
            "message": message,
            "evidence": evidence,
            "file": bug_info.get("file", ""),
            "line": bug_info.get("line", 0),
            "bug_info": bug_info,
        }
        investigation_strategy = self._generate_investigation_strategy(bug_context)

        logger.info(f"Starting investigation with {len(investigation_steps)} steps")

        # Execute investigation steps
        for i, step in enumerate(investigation_steps, 1):
            try:
                step_name = step["name"]
                step_explanation = step.get("explanation", "No explanation provided")
                logger.info(f"Executing investigation step {i}/{len(investigation_steps)}: {step_name}")
                logger.info(f"Reason: {step_explanation}")

                step["result"] = self._execute_investigation_step(step_name, step.get("params"))
                step["success"] = "error" not in step["result"]
                step["step_number"] = i
                step["total_steps"] = len(investigation_steps)

                logger.info(f"Step {step_name} completed: {'SUCCESS' if step['success'] else 'FAILED'}")
            except Exception as e:
                logger.error(f"Error executing investigation step {step_name}: {e}")
                step["result"] = {"error": str(e)}
                step["success"] = False
                step["step_number"] = i
                step["total_steps"] = len(investigation_steps)

        logger.info("Investigation completed, generating analysis...")

        # Parse strategy to get strategy description and correlations
        strategy_data = {}
        try:
            strategy_data = json.loads(investigation_strategy)
        except json.JSONDecodeError:
            strategy_data = {
                "investigation_strategy": "Systematic debugging approach",
                "expected_correlations": "Looking for patterns between infrastructure health and the reported issue",
            }

        return {
            "steps": investigation_steps,
            "summary": self.tools.get_investigation_summary(),
            "investigation_strategy": strategy_data.get("investigation_strategy", "Systematic debugging approach"),
            "expected_correlations": strategy_data.get(
                "expected_correlations", "Looking for patterns between infrastructure health and the reported issue"
            ),
        }

    def _generate_analysis(self, bug_info: dict[str, Any], investigation_results: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive analysis using LLM."""

        logger.info(f"Generating analysis for bug: {bug_info.get('summary', 'Unknown')}")
        logger.info(f"Investigation results keys: {list(investigation_results.keys())}")

        # Create prompt for analysis
        analysis_prompt = f"""
Based on the following bug report and investigation results, provide a comprehensive analysis:

BUG REPORT:
{json.dumps(bug_info, indent=2)}

INVESTIGATION RESULTS:
{json.dumps(investigation_results, indent=2)}

Please provide:
1. Severity assessment (Critical/High/Medium/Low) with confidence level
2. Root cause analysis
3. Correlations found between different issues
4. Recommended fixes
5. Prevention measures
6. Overall confidence level in the analysis

Format your response as JSON with the following structure:
{{
    "severity": {{
        "level": "Critical/High/Medium/Low",
        "confidence": "high/medium/low",
        "reasoning": "explanation of why this severity level was chosen"
    }},
    "root_cause": "description of the root cause",
    "correlations": ["list of correlations found"],
    "recommended_fixes": ["list of specific fixes"],
    "prevention_measures": ["list of prevention measures"],
    "confidence_level": "high/medium/low",
    "summary": "brief summary of findings"
}}
"""

        try:
            logger.info("Calling LLM for analysis...")
            response = self.llm_client.chat(
                messages=[
                    {"role": "system", "content": INVESTIGATION_SYSTEM_PROMPT},
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            logger.info(f"LLM Analysis Response: {response[:200]}...")

            # Try to parse JSON response
            try:
                analysis = json.loads(response)
                logger.info("Successfully parsed LLM analysis as JSON")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                logger.warning(f"Raw response: {response}")

                # Try to extract JSON from the response if it's wrapped in markdown
                import re

                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError:
                        analysis = None
                else:
                    analysis = None

                if not analysis:
                    # Create a structured response based on the raw text
                    analysis = {
                        "severity": {
                            "level": "Medium",
                            "confidence": "low",
                            "reasoning": "Unable to parse LLM response, using default assessment",
                        },
                        "root_cause": f"Analysis failed to parse properly. Raw response: {response[:200]}...",
                        "correlations": [],
                        "recommended_fixes": [],
                        "prevention_measures": [],
                        "confidence_level": "low",
                        "summary": "LLM analysis failed to generate proper JSON response",
                    }

            logger.info(f"Final analysis structure: {list(analysis.keys())}")
            return analysis

        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return {
                "severity": {
                    "level": "Medium",
                    "confidence": "low",
                    "reasoning": f"Error generating severity analysis: {str(e)}",
                },
                "root_cause": f"Error generating analysis: {str(e)}",
                "correlations": [],
                "recommended_fixes": [],
                "prevention_measures": [],
                "confidence_level": "low",
                "summary": f"Analysis failed due to error: {str(e)}",
            }
