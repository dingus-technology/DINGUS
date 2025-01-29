"""main.py

Main FastAPI entrypoint
"""

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from app.routers.chat import router as chat_router

app = FastAPI()


app.include_router(chat_router)


@app.get("/health")
def health_controller():
    return {"status": "Healthy"}


@app.get("/", include_in_schema=False)
def docs_redirect_controller():
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)
