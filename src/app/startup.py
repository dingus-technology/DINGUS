"""startup.py

Script to run on API startup."""

import logging

from fastapi import FastAPI

from app.database.vector_db import QdrantDatabaseClient
from app.scheduler import Scheduler
from app import settings as app_settings

logger = logging.getLogger(__name__)


def preprocess(app: FastAPI):
    logger.info("FastAPI startup: Setting up QdrantDatabaseClient")
    app.state.qdrant_client = QdrantDatabaseClient().setup()
    logger.info("FastAPI startup: QdrantDatabaseClient setup - completed")

    # Initialize in-memory runtime configuration (editable via API/UI)
    app.state.config = {
        "loki_base_url": app_settings.LOKI_URL,
        "job_name": app_settings.LOKI_JOB_NAME,
        "kube_config_path": app_settings.KUBE_CONFIG_PATH,
        "open_ai_api_key": app_settings.OPENAI_API_KEY,
        "openai_model": app_settings.OPENAI_MODEL,
    }
    logger.info("FastAPI startup: Runtime config initialized in app.state.config")

    # Initialize scheduler with runtime config so dependencies get correct API key
    logger.info("FastAPI startup: Initializing report scheduler")
    app.state.scheduler = Scheduler(
        loki_base_url=app.state.config["loki_base_url"],
        job_name=app.state.config["job_name"],
        open_ai_api_key=app.state.config["open_ai_api_key"],
        kube_config_path=app.state.config["kube_config_path"],
    )
    logger.info("FastAPI startup: Report scheduler initialized")
