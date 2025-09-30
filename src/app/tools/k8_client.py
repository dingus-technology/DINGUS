"""k8_client.py
This file contains tool calls to interact with kubernetes."""

import logging

from kubernetes import client, config

logger = logging.getLogger(__name__)


class KubernetesClient:
    def __init__(self, kube_config_path=None):
        """
        Initialize the Kubernetes client.

        Args:
            kube_config_path (str | None): Path to the kubeconfig file.
                If None, it attempts to use the in-cluster config.

        Raises:
            RuntimeError: If the client fails to initialize.
        """
        self.api_client = None
        try:
            if kube_config_path:
                config.load_kube_config(kube_config_path)
            else:
                config.load_incluster_config()
            logger.info("Kubernetes client configuration added")
            try:
                self.api_client = client.CoreV1Api()
                logger.info("Kubernetes client initialised")
            except Exception as e:
                logger.warning(f"Kubernetes CoreV1Api init failed, continuing without k8s: {e}")
        except Exception as e:
            logger.warning(f"Kubernetes config not available yet, continuing without k8s: {e}")

    def list_pods(self, namespace: str = "default") -> list | str | None:
        """
        List all pod names in the given namespace.

        Args:
            namespace (str): The Kubernetes namespace to query. Defaults to "default".

        Returns:
            list | str: A list of pod names or an error message.
        """
        if not self.api_client:
            logger.warning("Kubernetes client not initialised; list_pods returning None")
            return None
        try:
            pods = self.api_client.list_namespaced_pod(namespace)
            return [pod.metadata.name for pod in pods.items]
        except Exception as e:
            logger.error(f"Error listing pods: {e}")
            return None

    def get_pod_logs(self, pod_name: str, namespace: str = "default") -> list | str:
        """
        Retrieve logs for a specific pod.

        Args:
            pod_name (str): The name of the pod.
            namespace (str): The namespace of the pod. Defaults to "default".

        Returns:
            list | str: The pod logs or an error dictionary.
        """
        if not self.api_client:
            return "Kubernetes client not initialised"
        try:
            logs = self.api_client.read_namespaced_pod_log(pod_name, namespace)
            return logs
        except Exception as e:
            return f"Error retrieving logs: {e}"

    def get_pod_health(self, pod_name: str, namespace: str = "default") -> dict:
        """
        Check the health status of a specific pod.

        Args:
            pod_name (str): The name of the pod.
            namespace (str): The namespace of the pod. Defaults to "default".

        Returns:
            dict | str: A dictionary containing pod status details, including container statuses.
        """
        if not self.api_client:
            return {"error": "Kubernetes client not initialised"}
        try:
            pod = self.api_client.read_namespaced_pod(name=pod_name, namespace=namespace)
            phase = pod.status.phase

            return {"pod": pod_name, "phase": phase}

        except Exception as e:
            logger.error(f"Error checking pod health: {e}")
            return {"error": f"Error checking pod health: {e}"}
