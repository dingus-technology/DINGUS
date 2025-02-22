"""settings.py

Settings for the Dingus app.
"""
import os

MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
}
LOKI_QUERY_RANGE_ENDPOINT = "/loki/api/v1/query_range"
LOGGING_FILE = "/logs/dingus.log"
APP_TITLE = "DINGUS | Chat with Logs"
LOG_DATA_FILE_PATH = "/data/loki_stream.json"
TRUNCATE_LOGS = int(100)
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")