"""connectors.py: Contains the connectors external connections."""

import requests
import os

LOKI_ENDPOINT = os.environ.get("LOKI_URL")+"/loki/api/v1/query_range"
print(LOKI_ENDPOINT)
LOKI_JOB_NAME = os.environ.get("LOKI_JOB_NAME")

start_time="2024-02-19T00:00:00Z"
end_time="2024-02-19T23:59:59Z"

params = {
    "query": '{job="cpu_monitor"}',
    "start": start_time,
    "end": end_time,
    "limit": 100,
    "direction": "backward"
}

try:
    response = requests.get(LOKI_ENDPOINT, params=params)
    response.raise_for_status()

    data = response.json()
    print(data)
    streams = data.get("data", {}).get("result", [])
    
    for stream in streams:
        print(f"Labels: {stream['stream']}")
        for log in stream.get("values", []):
            timestamp, message = log
            print(f"{timestamp}: {message}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching logs: {e}")
