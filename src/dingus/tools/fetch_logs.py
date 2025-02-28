"""fetch_logs.py

Get log data from a database source."""

import logging
from datetime import datetime, timedelta

from dingus.connectors import fetch_loki_logs
from dingus.settings import LOKI_END_HOURS_AGO, LOKI_JOB_NAME, LOKI_URL

logger = logging.getLogger(__name__)


def get_loki_streams() -> tuple[list, list]:
    """
    Get Loki Log Streams.
    """
    now = datetime.now()
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    start_time = (now - timedelta(hours=LOKI_END_HOURS_AGO)).strftime("%Y-%m-%d %H:%M:%S")
    streams = fetch_loki_logs(
        loki_base_url=LOKI_URL,
        job_name=LOKI_JOB_NAME,
        start_time=start_time,
        end_time=end_time,
        limit=50,
        level=None,
        search_word=None,
    )

    if not streams:
        logger.error("No streams fetched from Loki.")
        raise ValueError("No streams fetched from Loki.")
    try:
        data: list[None | str] = [log.get("stream", {}).get("message") for log in streams]
        payloads: list[None | dict] = [log.get("stream") for log in streams]
    except TypeError as e:
        logger.error(f"Failed to extract streams from Loki: {e}")
        raise TypeError(f"Failed to extract streams from Loki: {e}") from e

    return data, payloads
