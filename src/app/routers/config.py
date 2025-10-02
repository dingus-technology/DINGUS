"""config.py
Router for admin management, connection checks, and scheduler control."""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.connectors import fetch_loki_logs
from app.tools.k8_client import KubernetesClient
from app.tools.llm_client import OpenAIChatClient

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Configuration"])


@router.post("/update_config")
async def update_config(payload: dict, request: Request):
    app = request.app
    if hasattr(app.state, "scheduler") and app.state.scheduler is not None:

        app.state.config.update(
            {
                "loki_base_url": payload["loki_base_url"],
                "job_name": payload["job_name"],
                "kube_config_path": payload["kube_config_path"],
                "open_ai_api_key": payload["open_ai_api_key"],
            }
        )
        await app.state.scheduler.update_config(
            loki_base_url=payload["loki_base_url"],
            job_name=payload["job_name"],
            open_ai_api_key=payload["open_ai_api_key"],
            kube_config_path=payload["kube_config_path"],
        )
        return {"status": "success"}
    else:
        return JSONResponse(status_code=500, content={"status": "fail", "reason": "Scheduler not initialized"})


@router.get("/config")
def get_config(request: Request):
    """Return current runtime configuration."""
    try:
        app = request.app
        cfg = getattr(app.state, "config", {})
        return {
            "status": "success",
            "config": {
                "loki_base_url": cfg.get("loki_base_url"),
                "job_name": cfg.get("job_name"),
                "kube_config_path": cfg.get("kube_config_path"),
                "open_ai_api_key": bool(cfg.get("open_ai_api_key")),
                "openai_model": cfg.get("openai_model"),
            },
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})


@router.get("/check_loki")
def check_loki(request: Request):
    """Check Loki connection with current config or provided params."""
    try:
        loki_url = request.query_params.get("loki_url")
        loki_job = request.query_params.get("loki_job_name")
        now = datetime.now()
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        streams = fetch_loki_logs(
            loki_base_url=str(loki_url),
            job_name=str(loki_job),
            start_time=start_time,
            end_time=end_time,
            limit=1,
        )
        if streams is not None:
            return {"status": "success"}
        else:
            return JSONResponse(status_code=400, content={"status": "fail", "reason": "No data from Loki"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "fail", "reason": str(e)})


@router.get("/check_k8s")
def check_k8s(request: Request):
    """Check K8s connection with current config or provided param."""
    try:
        kube_config = request.query_params.get("kube_config_path")
        kube = KubernetesClient(kube_config_path=kube_config)
        pods = kube.list_pods()
        if pods:
            return {"status": "success"}
        else:
            return JSONResponse(status_code=400, content={"status": "fail", "reason": "No pods found"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "fail", "reason": str(e)})


@router.post("/check_openai")
def check_openai(payload: dict):
    """Check OpenAI connection with provided API key."""
    try:
        api_key = payload.get("openai_api_key")
        if not api_key:
            return JSONResponse(status_code=400, content={"status": "fail", "reason": "No API key provided"})

        test_client = OpenAIChatClient(api_key=api_key)
        test_client.client.api_key = api_key
        response = test_client.client.models.list()
        if response:
            return {"status": "success"}
        else:
            return JSONResponse(status_code=400, content={"status": "fail", "reason": "Invalid API key"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "fail", "reason": str(e)})
