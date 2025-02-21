import logging
import sys

LOGGING_FILE = "/logs/dingus.log"


def set_logging(
    level: int = logging.INFO, log_file_path: str = LOGGING_FILE, to_stdout: bool = True, to_log_file: bool = True
):
    if logging.getLogger().hasHandlers():
        logging.warning("Overwriting Logging configuration.")

    handler_list: list[logging.Handler] = []
    if to_stdout:
        handler_list.append(logging.StreamHandler(sys.stdout))
    if to_log_file:
        handler_list.append(logging.FileHandler(log_file_path, mode="a", encoding="utf-8"))

    logging.basicConfig(
        level=level,
        encoding="utf-8",
        format="{asctime} - {levelname} - {pathname}:{lineno} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handler_list,
    )
