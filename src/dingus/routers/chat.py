"""chat.py
Chat endpoint in the FastAPI
"""

from fastapi import APIRouter, Depends, status

from dingus.chat_with_logs import ChatWithLogs
from dingus.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


def get_chat_with_logs():
    if not hasattr(get_chat_with_logs, "instance"):
        get_chat_with_logs.instance = ChatWithLogs()
    return get_chat_with_logs.instance


@router.post("/chat", response_model=ChatResponse, responses={status.HTTP_400_BAD_REQUEST: {}})
def chat_controller(request: ChatRequest, chat_with_logs: ChatWithLogs = Depends(get_chat_with_logs)) -> ChatResponse:
    messages: list[dict[str, str]] = request.messages

    messages = chat_with_logs.generate_response(messages=messages)
    return ChatResponse(response=str(messages[-1]["content"]))
