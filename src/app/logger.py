"""logger.py

This module sets up the logger to be used in the app."""

import logging


def set_logging(level: int = logging.INFO):

    logging.basicConfig(
        level=level,
        encoding="utf-8",
        format="{asctime} - {levelname} - {pathname}:{lineno} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
