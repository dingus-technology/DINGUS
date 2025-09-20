"""investigation_tools.py

This module contains tools for the debugging agent to investigate issues.
"""

import logging
import os
import socket
import time
from datetime import datetime
from typing import Any, Optional

import requests  # type: ignore

logger = logging.getLogger(__name__)


class InvestigationTools:
    """Tools for the debugging agent to investigate system issues."""

    def __init__(self):
        self.investigation_results = []

    def add_investigation_step(self, step_name: str, result: Any, success: bool = True, error: Optional[str] = None):
        """Add an investigation step result."""
        step = {
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "result": result,
            "error": error,
        }
        self.investigation_results.append(step)
        logger.info(f"Investigation step '{step_name}' completed: {'SUCCESS' if success else 'FAILED'}")

    def get_investigation_summary(self) -> dict[str, Any]:
        """Get a summary of all investigation steps."""
        return {
            "total_steps": len(self.investigation_results),
            "successful_steps": len([s for s in self.investigation_results if s["success"]]),
            "failed_steps": len([s for s in self.investigation_results if not s["success"]]),
            "steps": self.investigation_results,
        }

    def check_loki_connectivity(self, loki_url: str = "http://host.docker.internal:3100") -> dict[str, Any]:
        """Check if Loki is reachable and responding."""
        try:
            start_time = time.time()
            response = requests.get(f"{loki_url}/ready", timeout=5)
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = {"status": "connected", "response_time_ms": round(response_time * 1000, 2), "url": loki_url}
                self.add_investigation_step("Loki Connectivity Check", result, True)
            else:
                result = {"status": "failed", "status_code": response.status_code, "url": loki_url}
                self.add_investigation_step(
                    "Loki Connectivity Check", result, False, f"Status code: {response.status_code}"
                )

            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e), "url": loki_url}
            self.add_investigation_step("Loki Connectivity Check", result, False, str(e))
            return result

    def check_grafana_connectivity(self, grafana_url: str = "http://host.docker.internal:3000") -> dict[str, Any]:
        """Check if Grafana is reachable and responding."""
        try:
            start_time = time.time()
            response = requests.get(f"{grafana_url}/api/health", timeout=5)
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = {"status": "connected", "response_time_ms": round(response_time * 1000, 2), "url": grafana_url}
                self.add_investigation_step("Grafana Connectivity Check", result, True)
            else:
                result = {"status": "failed", "status_code": response.status_code, "url": grafana_url}
                self.add_investigation_step(
                    "Grafana Connectivity Check", result, False, f"Status code: {response.status_code}"
                )

            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e), "url": grafana_url}
            self.add_investigation_step("Grafana Connectivity Check", result, False, str(e))
            return result

    def check_network_connectivity(self, host: str = "8.8.8.8", port: int = 53) -> dict[str, Any]:
        """Check network connectivity to a specific host."""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result_code = sock.connect_ex((host, port))
            sock.close()
            response_time = time.time() - start_time

            if result_code == 0:
                result = {
                    "status": "connected",
                    "response_time_ms": round(response_time * 1000, 2),
                    "host": host,
                    "port": port,
                }
                self.add_investigation_step("Network Connectivity Check", result, True)
            else:
                result = {"status": "failed", "error_code": result_code, "host": host, "port": port}
                self.add_investigation_step(
                    "Network Connectivity Check", result, False, f"Connection failed with code {result_code}"
                )

            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e), "host": host, "port": port}
            self.add_investigation_step("Network Connectivity Check", result, False, str(e))
            return result

    def check_service_health(self, service_url: str) -> dict[str, Any]:
        """Check if a service is responding to HTTP requests."""
        try:
            start_time = time.time()
            response = requests.get(service_url, timeout=5)
            response_time = time.time() - start_time

            result = {
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "url": service_url,
            }
            self.add_investigation_step("Service Health Check", result, True)
            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e), "url": service_url}
            self.add_investigation_step("Service Health Check", result, False, str(e))
            return result

    def check_environment_variables(self, required_vars: Optional[list[str]] = None) -> dict[str, Any]:
        """Check if required environment variables are set."""
        if required_vars is None:
            required_vars = ["OPENAI_API_KEY", "OPENAI_MODEL", "DATABASE_URL", "REDIS_URL"]

        try:
            env_status = {}
            missing_vars = []

            for var in required_vars:
                value = os.getenv(var)
                if value:
                    env_status[var] = "set"
                else:
                    env_status[var] = "missing"
                    missing_vars.append(var)

            result = {
                "status": "success" if not missing_vars else "failed",
                "environment_variables": env_status,
                "missing_variables": missing_vars,
                "total_checked": len(required_vars),
                "total_missing": len(missing_vars),
            }

            self.add_investigation_step("Environment Variables Check", result, not missing_vars)
            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e)}
            self.add_investigation_step("Environment Variables Check", result, False, str(e))
            return result

    def get_code_context(self, file_path: str, line_number: int, context_lines: int = 10) -> dict[str, Any]:
        """Get code context around the error line."""
        try:
            # Try to read the file locally first
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    lines = f.readlines()

                start_line = max(0, line_number - context_lines - 1)
                end_line = min(len(lines), line_number + context_lines)

                code_context = lines[start_line:end_line]
                line_numbers = list(range(start_line + 1, end_line + 1))

                result = {
                    "file_path": file_path,
                    "error_line": line_number,
                    "context_lines": context_lines,
                    "code_snippet": code_context,
                    "line_numbers": line_numbers,
                    "source": "local_file",
                }
                self.add_investigation_step("Code Context Analysis", result, True)
                return result

            # If local file doesn't exist, try GitHub API (placeholder)
            else:
                result = {
                    "file_path": file_path,
                    "error_line": line_number,
                    "status": "file_not_found",
                    "message": f"File {file_path} not found locally",
                }
                self.add_investigation_step("Code Context Analysis", result, False, "File not found")
                return result

        except Exception as e:
            result = {"file_path": file_path, "error_line": line_number, "status": "error", "error": str(e)}
            self.add_investigation_step("Code Context Analysis", result, False, str(e))
            return result

    def check_kubernetes_pod_logs(self, pod_name: Optional[str] = None, namespace: str = "default") -> dict[str, Any]:
        """Get recent logs from Kubernetes pods."""
        try:
            import subprocess

            if pod_name is None:
                # Try to get pod name from kubectl
                result = subprocess.run(
                    ["kubectl", "get", "pods", "-n", namespace, "--no-headers", "-o", "custom-columns=:metadata.name"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    pod_names = result.stdout.strip().split("\n")
                    pod_name = pod_names[0] if pod_names else None

            if not pod_name:
                return {"status": "no_data", "error": "No pod name available"}

            result = subprocess.run(
                ["kubectl", "logs", pod_name, "-n", namespace, "--tail=50"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                logs = result.stdout.strip().split("\n")
                return {
                    "status": "success",
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "logs": logs,
                    "log_count": len(logs),
                }
            else:
                return {
                    "status": "failed",
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "error": result.stderr,
                }

        except Exception as e:
            return {"status": "no_data", "error": str(e)}

    def check_database_connection(
        self, db_host: str = "localhost", db_port: int = 5432, db_name: str = "postgres"
    ) -> dict[str, Any]:
        """Test database connectivity."""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result_code = sock.connect_ex((db_host, db_port))
            sock.close()
            response_time = time.time() - start_time

            if result_code == 0:
                result = {
                    "status": "connected",
                    "response_time_ms": round(response_time * 1000, 2),
                    "host": db_host,
                    "port": db_port,
                    "database": db_name,
                }
                self.add_investigation_step("Database Connection Test", result, True)
            else:
                result = {
                    "status": "failed",
                    "error_code": result_code,
                    "host": db_host,
                    "port": db_port,
                    "database": db_name,
                }
                self.add_investigation_step(
                    "Database Connection Test", result, False, f"Connection failed with code {result_code}"
                )

            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e), "host": db_host, "port": db_port, "database": db_name}
            self.add_investigation_step("Database Connection Test", result, False, str(e))
            return result

    def check_kubernetes_pod_status(self, pod_name: Optional[str] = None, namespace: str = "default") -> dict[str, Any]:
        """Check Kubernetes pod status and health."""
        try:
            import subprocess

            if pod_name is None:
                # Get all pods in the namespace
                result = subprocess.run(
                    ["kubectl", "get", "pods", "-n", namespace, "-o", "wide"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            else:
                # Get specific pod status
                result = subprocess.run(
                    ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "wide"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    pod_info = lines[1].split()
                    if len(pod_info) >= 6:
                        return {
                            "pod_name": pod_info[0],
                            "ready": pod_info[1],
                            "status": pod_info[2],
                            "restarts": pod_info[3],
                            "age": pod_info[4],
                            "ip": pod_info[5],
                            "node": pod_info[6] if len(pod_info) > 6 else "N/A",
                        }
                    else:
                        return {"status": "failed", "error": "Unexpected pod info format"}
                else:
                    return {"status": "no_data", "error": "No pods found"}
            else:
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            return {"status": "no_data", "error": str(e)}

    def check_system_resources(self) -> dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            result = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "status": "success",
            }
            self.add_investigation_step("System Resources Check", result, True)
            return result

        except Exception as e:
            result = {"status": "no_data", "error": str(e)}
            self.add_investigation_step("System Resources Check", result, False, str(e))
            return result

    def check_recent_changes(self, hours_back: int = 24) -> dict[str, Any]:
        """Check for recent changes (deploys, commits, etc.)."""
        try:
            # This is a placeholder - in a real system, you'd check:
            # - Recent git commits
            # - Recent Kubernetes deployments
            # - Recent config changes
            # - Recent infrastructure changes

            result = {
                "hours_back": hours_back,
                "message": "Recent changes analysis not implemented in this demo",
                "status": "not_implemented",
            }
            self.add_investigation_step("Recent Changes Check", result, True)
            return result

        except Exception as e:
            result = {"hours_back": hours_back, "status": "no_data", "error": str(e)}
            self.add_investigation_step("Recent Changes Check", result, False, str(e))
            return result
