"""grafana_url.py
This file will produce a link a Grafana dashboard.
"""

import json
import time
import urllib.parse
from datetime import datetime


def generate_grafana_url(prometheus_uid, queries, from_time, to_time, org_id=1):
    """
    Generate a structured and readable Grafana Explore URL with minimal encoding.

    Args:
    - prometheus_uid (str): The UID of the Prometheus data source.
    - queries (list of dict): List of query objects, e.g., [{"refId": "A", "expr": "cpu_load{job='sanitised-data'}"}]
    - from_time (str): Start time in "YYYY-MM-DD HH:MM:SS" format or "now-1h".
    - to_time (str): End time in "YYYY-MM-DD HH:MM:SS" format or "now".
    - org_id (int): Grafana organization ID.

    Returns:
    - str: A clean and legible Grafana URL.
    """

    def convert_to_timestamp(time_str):
        """Convert absolute time to Unix timestamp (ms), else return relative Grafana time format."""
        if "now" in time_str:
            return time_str
        return str(int(time.mktime(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timetuple()) * 1000))

    from_timestamp = convert_to_timestamp(from_time)
    to_timestamp = convert_to_timestamp(to_time)

    pane_id = "qyv"
    grafana_query = {
        "schemaVersion": 1,
        "panes": {
            pane_id: {
                "datasource": prometheus_uid,
                "queries": [
                    {
                        "refId": q["refId"],
                        "expr": q["expr"],
                        "range": True,
                        "instant": True,
                        "datasource": {"type": "prometheus", "uid": prometheus_uid},
                        "editorMode": "builder",
                        "legendFormat": "__auto",
                        "useBackend": False,
                        "disableTextWrap": False,
                        "fullMetaSearch": False,
                        "includeNullMetadata": True,
                    }
                    for q in queries
                ],
                "range": {"from": from_timestamp, "to": to_timestamp},
            }
        },
        "orgId": org_id,
    }

    base_url = "http://localhost:3000/explore"
    url_params = {"schemaVersion": 1, "orgId": org_id, "panes": json.dumps(grafana_query["panes"])}

    final_url = f"{base_url}?" + "&".join(
        f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in url_params.items()
    )

    return final_url
