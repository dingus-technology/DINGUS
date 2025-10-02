"""loki_client.py

Get log data from a database source."""

import logging
from datetime import datetime, timedelta

from app.connectors import fetch_loki_logs
from app.database.vector_db import QdrantDatabaseClient
from app.settings import LOKI_END_HOURS_AGO

logger = logging.getLogger(__name__)


class LokiClient:
    def __init__(self, loki_base_url: str, job_name: str):
        self.loki_base_url = loki_base_url
        self.job_name = job_name
        self.database_client = QdrantDatabaseClient()

    def upsert_logs(self) -> None:
        """
        Fetch logs from a specified source and upsert them into a vector database.
        """
        logger.info("Getting Logs for Upserting")
        data, payloads = self.get_loki_streams()

        if data is None:
            logger.error("No data to upsert")
            return

        self.database_client.upsert(data_to_embed=data, payloads=payloads)

    def get_loki_streams(self) -> tuple[list, list]:
        """
        Get Loki Log Streams.
        """
        now = datetime.now()
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        start_time = (now - timedelta(hours=LOKI_END_HOURS_AGO)).strftime("%Y-%m-%d %H:%M:%S")
        streams = fetch_loki_logs(
            loki_base_url=self.loki_base_url,
            job_name=self.job_name,
            start_time=start_time,
            end_time=end_time,
            limit=50,
            level=None,
            search_word=None,
        )

        if not streams:
            logger.error("No streams fetched from Loki.")
            return [], []
        try:
            data: list[None | str] = [log.get("stream", {}).get("message") for log in streams]
            payloads: list[None | dict] = [log.get("stream") for log in streams]
        except TypeError as e:
            logger.error(f"Failed to extract streams from Loki: {e}")
            raise TypeError(f"Failed to extract streams from Loki: {e}") from e

        return data, payloads
