import logging
import os
from urllib.parse import urljoin

import requests  # type: ignore

from dingus.utils import datetime_to_timestamp

logger = logging.getLogger(__name__)


LOKI_QUERY_RANGE_ENDPOINT = "/loki/api/v1/query_range"


def fetch_loki_logs(
    loki_base_url: str, job_name: str, start_time: str, end_time: str, limit: int = 100
) -> list[dict] | None:
    """
    Fetch logs from the Loki API within a specified time range and for a specific job.

    Args:
        loki_url (str): The URL of the Loki server.
        job_name (str): The job name to query for logs. Defaults to "cpu_monitor".
        start_time (str): The start time in "%Y-%m-%d %H:%M:%S" format.
        end_time (str): The end time in "%Y-%m-%d %H:%M:%S" format.
        limit (int): The maximum number of log entries to retrieve. Defaults to 100.

    Returns:
    list[dict]: A list of log entries in the format:
        [
            {
                "stream": {
                    "job": str,
                    "level": str,
                    "logger": str,
                    "service": str,
                    "service_name": str
                },
                "values": [
                    [str, str],
                    ...
                ]
            },
            ...
        ]
    """
    start_time_ts = datetime_to_timestamp(start_time)
    end_time_ts = datetime_to_timestamp(end_time)

    if start_time_ts is None or end_time_ts is None:
        logger.error("Invalid time format, cannot fetch logs.")
        return None

    params = {
        "query": f'{{job="{job_name}"}}',
        "start": start_time_ts,
        "end": end_time_ts,
        "limit": limit,
        "direction": "backward",
    }
    url = urljoin(loki_base_url, LOKI_QUERY_RANGE_ENDPOINT)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching logs from Loki: {e}")
        return None

    try:
        data = response.json()
        return data.get("data", {}).get("result", [])

    except ValueError as e:
        logger.error(f"Error in JSON from Loki: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


if __name__ == "__main__":

    from dingus.logger import set_logging

    set_logging()
    start_time = "2025-02-21 00:00:00"
    end_time = "2025-02-21 12:34:56"
    job_name = "cpu_monitor"
    loki_base_url = os.getenv("LOKI_URL", "http://localhost:3100")

    streams = fetch_loki_logs(loki_base_url, job_name, start_time, end_time)
    logger.info(f"Streams: {streams}")
