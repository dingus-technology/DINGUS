"""scheduler.py

This module handles the scheduling of periodic tasks.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from app.tools.k8_client import KubernetesClient
from app.tools.llm_client import OpenAIChatClient
from app.tools.log_scanner import LogScanner
from app.tools.loki_client import LokiClient
from app.tools.report_generator import LogReportGenerator

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self,
        loki_base_url: str,
        job_name: str,
        open_ai_api_key: str,
        kube_config_path: str,
        frequency_in_hours: int | None = 1,
    ):
        logger.info("Creating new Scheduler instance with default dependencies")
        openai_client = OpenAIChatClient(api_key=open_ai_api_key, model="gpt-4o")
        kube_client = KubernetesClient(kube_config_path=kube_config_path)
        loki_client = LokiClient(loki_base_url=loki_base_url, job_name=job_name)
        report_generator = LogReportGenerator(
            openai_client=openai_client, kube_client=kube_client, loki_client=loki_client
        )
        log_scanner = LogScanner(
            loki_base_url=loki_base_url,
            job_name=job_name,
            open_ai_api_key=open_ai_api_key,
            kube_config_path=kube_config_path,
            log_limit=100,
        )
        log_scanner.openai_client = openai_client
        frequency_in_hours = frequency_in_hours or 1

        self.report_generator = report_generator
        self.log_scanner = log_scanner
        self.loki_client = loki_client
        self.frequency = frequency_in_hours * 60 * 60
        self._task = None
        self._running = False

    async def start(self):
        """Start the periodic scheduler."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info("Scheduler started")

    async def stop(self):
        """Stop the scheduler."""
        if not self._running:
            logger.warning("Scheduler is not running")
            return
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def update_config(
        self,
        loki_base_url: str,
        job_name: str,
        open_ai_api_key: str,
        kube_config_path: str,
        frequency_in_hours: int | None = 1,
    ):
        """Update the scheduler's configuration and dependencies."""
        openai_client = OpenAIChatClient(api_key=open_ai_api_key, model="gpt-4o")
        kube_client = KubernetesClient(kube_config_path=kube_config_path)
        loki_client = LokiClient(loki_base_url=loki_base_url, job_name=job_name)
        report_generator = LogReportGenerator(
            openai_client=openai_client, kube_client=kube_client, loki_client=loki_client
        )
        log_scanner = LogScanner(
            loki_base_url=loki_base_url,
            job_name=job_name,
            kube_config_path=kube_config_path,
            open_ai_api_key=open_ai_api_key,
            log_limit=100,
        )
        log_scanner.openai_client = openai_client

        frequency_in_hours = frequency_in_hours or 1
        self.report_generator = report_generator
        self.log_scanner = log_scanner
        self.loki_client = loki_client
        self.frequency = frequency_in_hours * 60 * 60
        logger.info("Scheduler configuration updated.")

    async def _run_scheduler(self):
        """Run the scheduler loop."""
        runs = 0
        while self._running:
            try:
                await asyncio.sleep(self.frequency)
                await self.log_scanner.run_once()
                self.report_generator.generate_report()
                logger.info(f"Scheduler run completed at {datetime.now()}")
                runs += 1
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)
