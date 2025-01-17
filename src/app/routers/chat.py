"""chat.py
Chat endpoint in the FastAPI
"""

from fastapi import APIRouter, status, HTTPException

router = APIRouter(tags=["chat"])

@router.post("/chat", responses={status.HTTP_400_BAD_REQUEST: {}})
def chat_controller(user_input: str) -> str:
    if not user_input:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is required.")
    return user_input