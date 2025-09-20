"""settings.py
This module contains the settings for the frontend.
"""

import os

API_URL = os.getenv("CHAT_API_URL", "http://localhost:8000")
