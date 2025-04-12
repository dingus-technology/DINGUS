"""startup.py

Script to run on API startup."""

import logging

from fastapi import FastAPI

from dingus.database.vector_db import get_qdrant_client
from dingus.scheduler import get_report_scheduler
from dingus.tools.vectors import upsert_logs

logger = logging.getLogger(__name__)


def preprocess(app: FastAPI):

    logger.info("FastAPI startup: Setting up QdrantDatabaseClient")
    app.state.qdrant_client = get_qdrant_client()
    logger.info("FastAPI startup: QdrantDatabaseClient setup - completed")

    logger.info("FastAPI starup: Upserting Loki Logs to Qdrant.")
    upsert_logs(log_source="loki", vector_db="qdrant")
    logger.info("FastAPI starup: Upserting Loki Logs to Qdrant - completed")

    logger.info("FastAPI startup: Initializing report scheduler")
    app.state.report_scheduler = get_report_scheduler()
    logger.info("FastAPI startup: Report scheduler initialized")
