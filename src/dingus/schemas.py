"""schemas.py

This module contains the pydantic data classes."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    messages: list[dict[str, str]] = Field(
        ...,
        title="Chat Messages",
        description="A list of messages in the conversation, each containing 'role' and 'content'.",
        examples=[[{"role": "user", "content": "How are my logs?"}]],
    )


class ChatResponse(BaseModel):
    response: str = Field(title="The Dingus response.")
