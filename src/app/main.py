"""main.py

Main FastAPI entrypoint
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.logger import set_logging
from app.routers.bugs import router as bugs_router
from app.routers.config import router as config_router
from app.routers.investigation import router as investigation_router
from app.settings import APP_TITLE
from app.startup import preprocess

set_logging()

logger = logging.getLogger(__name__)

logger.info("Creating FastAPI app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI startup: Running setup.")
    preprocess(app)

    # Start the scheduler
    logger.info("FastAPI startup: Starting report scheduler")
    await app.state.scheduler.start()
    logger.info("FastAPI startup: Report scheduler started")
    yield

    # Stop the  scheduler
    logger.info("FastAPI shutdown: Stopping report scheduler")
    await app.state.scheduler.stop()
    logger.info("FastAPI shutdown: Report scheduler stopped")


routes = [config_router, bugs_router, investigation_router]

app = FastAPI(docs_url=None, redoc_url=None, title=APP_TITLE, lifespan=lifespan)
for r in routes:
    app.include_router(r)
app.mount("/assets", StaticFiles(directory="/assets"), name="assets")


@app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title=APP_TITLE, swagger_favicon_url="/assets/favicon.ico")


@app.get("/health")
def health_controller():
    return {"status": "Healthy"}


@app.get("/", include_in_schema=False)
def docs_redirect_controller():
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)
