"""utils.py

This module contains common utility funtions."""

import time


def stream_data(content: str):
    for word in content.split(" "):
        yield word + " "
        time.sleep(0.04)
