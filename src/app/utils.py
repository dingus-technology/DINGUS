"""utils.py

This module contains common utility funtions."""

import csv
import logging
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


def singleton(cls: type) -> Any:
    """Decorator to make a class a singleton."""
    instances: dict[Any, Any] = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def display_response(response: str, type_speed: float = 0.01):
    """
    Simulate typing the response to the terminal, character by character.
    """
    for char in response:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(type_speed)
    sys.stdout.write("\n")


def get_logs_data(log_file_path: str, keep_headers: list[str] | None = None):
    """
    Reads a CSV file and keeps only specified headers if provided.

    :param log_file_path: Path to the log CSV file.
    :param keep_headers: List of headers to keep. If None, keep all.
    :return: Filtered log data as a list of lists.
    """
    with open(log_file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        if keep_headers:
            keep_indexes = [header.index(col) for col in keep_headers if col in header]
            log_data = [[header[i] for i in keep_indexes]]
        else:
            keep_indexes = list(range(len(header)))
            log_data = [header]

        for row in csv_reader:
            log_data.append([row[i] for i in keep_indexes])

    return log_data


def datetime_to_timestamp(datetime_str: str) -> int | None:
    """
    Converts a datetime string to a Unix timestamp.

    Args:
        datetime_str (str): The datetime string in the format "%Y-%m-%d %H:%M:%S".

    Returns:
        int: The Unix timestamp, or None if conversion fails.

    Raises:
        ValueError: If the datetime string is in an incorrect format.
    """
    try:
        dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return int(dt_obj.timestamp())
    except ValueError as e:
        logger.error(f"Invalid datetime format: {datetime_str}. Expected format: 'YYYY-MM-DD HH:MM:SS'.")
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected format: 'YYYY-MM-DD HH:MM:SS'.") from e
