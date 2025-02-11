"""chat.py
Chat endpoint in the FastAPI
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.chat_with_logs import ChatWithLogs
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


def get_chat_service() -> ChatWithLogs:
    return ChatWithLogs()


@router.post("/chat", response_model=ChatResponse, responses={status.HTTP_400_BAD_REQUEST: {}})
def chat_controller(
    request: ChatRequest,
    chat_with_logs: ChatWithLogs = Depends(get_chat_service),
) -> str:
    messages: list[dict[str, str]] = request.messages

    user_messages = [msg for msg in messages if msg["role"] == "user"]
    if not user_messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User message is required.")

    user_input = user_messages[-1]["content"]
    messages = [msg for msg in messages if msg != user_messages[-1]]

    response, _ = chat_with_logs.generate_response(user_input, messages)
    return ChatResponse(response=str(response))
