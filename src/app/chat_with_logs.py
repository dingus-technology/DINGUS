"""chat_with_logs.py

This file lets you interact with a logs file like an AI agent.
"""

import logging

from fastapi import HTTPException, status

from app.prompts import PROMPT_PREFIX
from app.settings import (
    KUBE_CONFIG_PATH,
    LOG_DATA_FILE_PATH,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from app.tools.consolidators import (
    create_response,
    get_csv_summary,
    get_k8_summary,
    get_vector_db_summary,
)
from app.tools.llm_client import OpenAIChatClient

logger = logging.getLogger(__name__)


class ChatWithLogs:

    def __init__(self, use_vector_db: bool = True, vector_db: str = "qdrant", use_k8: bool = True):
        logger.info("ChatWithLogs instance created")
        if not OPENAI_API_KEY:
            raise ValueError("The OPENAI_API_KEY environment variable is not set in .env file.")

        self.openai_client = OpenAIChatClient(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        self.vector_db = vector_db
        self.use_vector_db = use_vector_db
        self.use_k8 = use_k8

    def generate_response(self, messages: list) -> list:
        """
        Generate a response from the LLM based on user input and log data.
        """
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User message is required.")
        user_input = user_messages[-1]["content"]

        if len(messages) <= 2:
            k8_summary = (
                get_k8_summary(openai_client=self.openai_client, kube_config_path=KUBE_CONFIG_PATH)
                if self.use_k8
                else None
            )

            if self.use_vector_db:
                summary = get_vector_db_summary(query_text="CPU", openai_client=self.openai_client)
            else:
                summary = get_csv_summary(openai_client=self.openai_client, log_file_path=LOG_DATA_FILE_PATH)

            response = create_response(user_input=user_input, summary=summary, openai_client=self.openai_client)
            messages.append({"role": "assistant", "content": f"{response} \n{str(summary)}\n\n{str(k8_summary)}"})

        else:
            messages[-1] = {"role": "user", "content": f"{PROMPT_PREFIX} {user_input}"}
            response = self.openai_client.chat(messages)
            messages.append({"role": "assistant", "content": response})
        return messages


def get_chat_with_logs():
    if not hasattr(get_chat_with_logs, "instance"):
        get_chat_with_logs.instance = ChatWithLogs()
        logger.info("ChatWithLogs instance created")
    return get_chat_with_logs.instance
