import csv
import logging
import sys
import time


def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename="/src/logs/app.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {pathname}:{lineno} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


def display_response(response: str, type_speed: float = 0.01):
    """
    Simulate typing the response to the terminal, character by character.
    """
    for char in response:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(type_speed)
    sys.stdout.write("\n")


def get_logs_data(LOG_DATA_FILE_PATH):
    """_summary_

    Args:
        LOG_DATA_FILE_PATH (str): File path to the logs.

    Returns:
        list: The log data as a list.
    """
    with open(LOG_DATA_FILE_PATH, mode="r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        log_data = [header]
        for row in csv_reader:
            str(row).replace("\'\',", "")
            log_data.append(row)
        return log_data
