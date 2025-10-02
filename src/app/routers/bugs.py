import asyncio
import json
import logging
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.tools.log_scanner import LogScanner

router = APIRouter(tags=["Bug Management"])
logger = logging.getLogger(__name__)

BUGS_DIR = "/data/bugs/"


@router.get("/bugs")
def list_bugs():
    logger.info("Listing Bugs...")
    try:
        if not os.path.exists(BUGS_DIR):
            return {"bugs": []}
        files = [f for f in os.listdir(BUGS_DIR) if f.endswith(".json")]
        logger.info(files)
        files.sort(reverse=True)
        bugs = []
        for fname in files:
            path = os.path.join(BUGS_DIR, fname)
            try:
                with open(path, "r") as f:
                    bug = json.load(f)
                bugs.append({"filename": fname, "bug": bug})
            except Exception as e:
                bugs.append({"filename": fname, "error": str(e)})
        return {"bugs": bugs}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})


@router.post("/scan")
def scan(payload: dict = {}, request: Request = None):
    """Trigger a Scan for bugs (manual log scan)."""
    try:
        # Use config from payload or app.state.config (no defaults from settings)
        cfg = getattr(request.app.state, "config", {}) if request else {}
        loki_base_url = payload.get("loki_base_url") or cfg.get("loki_base_url")
        job_name = payload.get("job_name") or cfg.get("job_name")
        kube_config_path = payload.get("kube_config_path") or cfg.get("kube_config_path")
        open_ai_api_key = payload.get("open_ai_api_key") or cfg.get("open_ai_api_key")
        log_limit = payload.get("log_limit", 100)

        scanner = LogScanner(loki_base_url, job_name, open_ai_api_key, kube_config_path, log_limit)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scanner.run_once())
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "fail", "reason": str(e)})


@router.delete("/bug/{filename}")
def delete_bug(filename: str):
    """Delete a bug JSON file by filename."""
    try:
        path = os.path.join(BUGS_DIR, filename)
        if not os.path.exists(path):
            return JSONResponse(status_code=404, content={"status": "error", "reason": "File not found"})
        os.remove(path)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})
