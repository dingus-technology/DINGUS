"""connectors.py

Ths module contains connections to external data sources."""

import logging
import os
from urllib.parse import urljoin

import requests  # type: ignore

from dingus.settings import LOKI_QUERY_RANGE_ENDPOINT
from dingus.utils import datetime_to_timestamp

logger = logging.getLogger(__name__)


def build_loki_query(job_name: str, level: str | None = None, search_word: str | None = None) -> str:
    """
    Build a Loki query string to filter logs by level and search word.

    Args:
        job_name (str): The job name to query for logs. Defaults to "cpu_monitor".
        level (str): The log level to filter by. Defaults to None.
        search_word (str): The search word to filter by. Defaults to None.

    Returns:
        str: The Loki query string.
    """
    # TODO: unit tests
    level_filter = f' | level="{level.upper()}"' if level else ""
    search_filter = f' |~ "(?i){search_word}"' if search_word else ""
    logQL = f'{{job="{job_name}"}} | json {level_filter}{search_filter}'
    return logQL


def fetch_loki_logs(
    loki_base_url: str,
    job_name: str,
    start_time: str,
    end_time: str,
    limit: int = 100,
    level: str | None = None,
    search_word: str | None = None,
) -> list[dict] | None:
    """
    Fetch logs from the Loki API within a specified time range and for a specific job.

    Args:
        loki_url (str): The URL of the Loki server.
        job_name (str): The job name to query for logs. Defaults to "cpu_monitor".
        start_time (str): The start time in "%Y-%m-%d %H:%M:%S" format.
        end_time (str): The end time in "%Y-%m-%d %H:%M:%S" format.
        limit (int): The maximum number of log entries to retrieve. Defaults to 100. Max 5000.
        level (str): The log level to filter by. Defaults to "info".
        search_word (str): The search word to filter by.

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

    logQL = build_loki_query(level=level, search_word=search_word, job_name=job_name)

    params = {
        "query": logQL,
        "start": start_time_ts,
        "end": end_time_ts,
        "limit": limit,
        "direction": "backward",
    }
    url = urljoin(loki_base_url, LOKI_QUERY_RANGE_ENDPOINT)

    logger.info(f"Fetching Loki logs: {params}, from {url}")

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
    import json

    from dingus.logger import set_logging

    set_logging()

    start_time = "2025-02-22 01:00:00"
    end_time = "2025-02-24 15:34:56"
    job_name = os.getenv("LOKI_JOB_NAME", "cpu_monitor")
    loki_base_url = os.getenv("LOKI_URL", "http://host.docker.internal:3100")
    level = None
    limit = 50
    search_word = None

    streams = fetch_loki_logs(
        loki_base_url=loki_base_url,
        job_name=job_name,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        level=level,
        search_word=search_word,
    )

    if streams:
        with open("/data/loki_stream.json", mode="w") as file:
            json.dump(streams, file, indent=4)
        logger.info("Written streams to file.")
    else:
        logger.error("No streams to write.")
