"""chat.py
Chat endpoint in the FastAPI
"""

import logging

from fastapi import APIRouter, Depends, status

from app.chat_with_logs import ChatWithLogs, get_chat_with_logs
from app.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse, responses={status.HTTP_400_BAD_REQUEST: {}})
def chat_controller(request: ChatRequest, chat_with_logs: ChatWithLogs = Depends(get_chat_with_logs)) -> ChatResponse:
    messages: list[dict[str, str]] = request.messages

    messages = chat_with_logs.generate_response(messages=messages)
    return ChatResponse(response=str(messages[-1]["content"]))
