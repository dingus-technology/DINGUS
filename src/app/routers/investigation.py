"""investigation.py

Router for handling investigation endpoints.
"""

import json
import logging
import os
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.tools.investigation_agent import InvestigationAgent

router = APIRouter(tags=["Investigation"])
logger = logging.getLogger(__name__)

INVESTIGATIONS_DIR = "/data/investigations/"


@router.post("/investigation/start")
def start_investigation(payload: dict[str, Any], request: Request):
    """Start a new investigation for a bug."""
    try:
        bug_info = payload.get("bug_info", {})
        if not bug_info:
            return JSONResponse(status_code=400, content={"status": "error", "reason": "bug_info is required"})

        # Create investigations directory if it doesn't exist
        os.makedirs(INVESTIGATIONS_DIR, exist_ok=True)

        # Start investigation
        # Optionally set runtime API key/model for the agent from app.state.config
        agent = InvestigationAgent()
        try:
            cfg = getattr(request.app.state, "config", {})
            if cfg and cfg.get("open_ai_api_key"):
                agent.llm_client.client.api_key = cfg.get("open_ai_api_key")  # type: ignore[attr-defined]
        except Exception:
            pass
        investigation_result = agent.start_investigation(bug_info)

        # Save investigation result
        investigation_id = investigation_result["investigation_id"]
        filename = f"{investigation_id}.json"
        filepath = os.path.join(INVESTIGATIONS_DIR, filename)

        with open(filepath, "w") as f:
            json.dump(investigation_result, f, indent=2)

        # Try to update the bug file with the investigation ID
        try:
            bug_filename = payload.get("bug_filename")
            if bug_filename:
                bug_filepath = os.path.join("/data/bugs/", bug_filename)
                if os.path.exists(bug_filepath):
                    with open(bug_filepath, "r") as f:
                        bug_data = json.load(f)

                    # Add investigation ID to bug data
                    bug_data["investigation_id"] = investigation_id

                    with open(bug_filepath, "w") as f:
                        json.dump(bug_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not update bug file with investigation ID: {e}")

        logger.info(f"Investigation {investigation_id} completed and saved")

        return {"status": "success", "investigation_id": investigation_id, "result": investigation_result}

    except Exception as e:
        logger.error(f"Error starting investigation: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})


@router.get("/investigation/{investigation_id}")
def get_investigation(investigation_id: str):
    """Get investigation results by ID."""
    try:
        filename = f"{investigation_id}.json"
        filepath = os.path.join(INVESTIGATIONS_DIR, filename)

        if not os.path.exists(filepath):
            return JSONResponse(status_code=404, content={"status": "error", "reason": "Investigation not found"})

        with open(filepath, "r") as f:
            investigation_result = json.load(f)

        return {"status": "success", "investigation": investigation_result}

    except Exception as e:
        logger.error(f"Error retrieving investigation {investigation_id}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})


@router.get("/investigations")
def list_investigations():
    """List all investigations."""
    try:
        if not os.path.exists(INVESTIGATIONS_DIR):
            return {"investigations": []}

        files = [f for f in os.listdir(INVESTIGATIONS_DIR) if f.endswith(".json")]
        files.sort(reverse=True)

        investigations = []
        for fname in files:
            path = os.path.join(INVESTIGATIONS_DIR, fname)
            try:
                with open(path, "r") as f:
                    investigation = json.load(f)
                investigations.append({"filename": fname, "investigation": investigation})
            except Exception as e:
                investigations.append({"filename": fname, "error": str(e)})

        return {"investigations": investigations}

    except Exception as e:
        logger.error(f"Error listing investigations: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})


@router.delete("/investigation/{investigation_id}")
def delete_investigation(investigation_id: str):
    """Delete an investigation by ID."""
    try:
        filename = f"{investigation_id}.json"
        filepath = os.path.join(INVESTIGATIONS_DIR, filename)

        if not os.path.exists(filepath):
            return JSONResponse(status_code=404, content={"status": "error", "reason": "Investigation not found"})

        os.remove(filepath)
        logger.info(f"Deleted investigation {investigation_id}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error deleting investigation {investigation_id}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(e)})
