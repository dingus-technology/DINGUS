"""main.py

Main FastAPI entrypoint
"""

from fastapi import FastAPI, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from dingus.routers.chat import router as chat_router

APP_TITLE = "DINGUS | Chat with Logs"

app = FastAPI(docs_url=None, redoc_url=None, title=APP_TITLE)
app.include_router(chat_router)
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
