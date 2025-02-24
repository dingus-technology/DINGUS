"""utils.py

Ths module contais utility functions to be used across the app."""

import time


def stream_data(content: str):
    for word in content.split(" "):
        yield word + " "
        time.sleep(0.04)
