"""startup.py

Script to run on API startup."""

import logging

from fastapi import FastAPI

from app.database.vector_db import QdrantDatabaseClient
from app.scheduler import Scheduler

logger = logging.getLogger(__name__)


def preprocess(app: FastAPI):
    logger.info("FastAPI startup: Setting up QdrantDatabaseClient")
    app.state.qdrant_client = QdrantDatabaseClient().setup()
    logger.info("FastAPI startup: QdrantDatabaseClient setup - completed")

    logger.info("FastAPI startup: Initializing report scheduler")
    app.state.scheduler = Scheduler()
    logger.info("FastAPI startup: Report scheduler initialized")
