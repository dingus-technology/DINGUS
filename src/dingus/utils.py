import csv
import logging
import sys
import time


def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename="/logs/dingus.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {pathname}:{lineno} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
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



