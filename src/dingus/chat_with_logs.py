"""chat_with_logs.py

This file lets you interact with a logs file like an AI agent.
"""

import logging

from fastapi import HTTPException, status

from dingus.database.vector_db import get_qdrant_client
from dingus.llm_clients import OpenAIChatClient
from dingus.prompts import (
    FORMAT_RESPONSE,
    HEADER_PROMPT,
    PROMPT_PREFIX,
    SUMMARY_PROMPT,
    SYSTEM_PROMPT,
    VECTOR_DB_PROMPT,
)
from dingus.settings import (
    LOG_DATA_FILE_PATH,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    QDRANT_COLLECTION_NAME,
    TRUNCATE_LOGS,
)
from dingus.utils import get_logs_data

logger = logging.getLogger(__name__)


class ChatWithLogs:

    def __init__(self, use_qdrant: bool = True):
        logger.info("ChatWithLogs instance created")
        self.LOG_DATA_FILE_PATH = LOG_DATA_FILE_PATH
        self.TRUNCATE_LOGS = TRUNCATE_LOGS

        if not OPENAI_API_KEY:
            raise ValueError("The OPENAI_API_KEY environment variable is not set in .env file.")

        self.openai_client = OpenAIChatClient(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        self.qdrant_client = get_qdrant_client()
        self.use_qdrant = use_qdrant

    def get_vector_db_summary(self):
        """
        Generate a summary of the vector database.
        """
        query_text = "CPU"  # TODO: dynamic searchs
        vector_search = self.qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME, query_text=query_text, limit=20
        )
        logger.info(f"Vector search length: {len(vector_search)}")

        messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": VECTOR_DB_PROMPT + str(vector_search)},
        ]

        self.SUMMARY_INFO = self.openai_client.chat(messages, max_tokens=1000)
        logger.info(f"SUMMARY_INFO: {self.SUMMARY_INFO}")

    def get_log_summary(self):
        """
        Generate a summary of the log data by reducing the raw log files.
        """
        messages = [
            SYSTEM_PROMPT,
            {
                "role": "user",
                "content": HEADER_PROMPT
                + str(get_logs_data(self.LOG_DATA_FILE_PATH)[0:15]).replace("'", "").replace(" ", "").replace("\\", ""),
            },
        ]
        headers = str(self.openai_client.chat(messages, max_tokens=1000))
        headers = headers.replace("```", "").replace("[", "").replace("]", "")
        headers = [item.strip() for item in headers.split(",")]

        self.log_data = get_logs_data(self.LOG_DATA_FILE_PATH, headers)[0 : self.TRUNCATE_LOGS]  # noqa: E203

        messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": SUMMARY_PROMPT + str(self.log_data)},
        ]
        self.SUMMARY_INFO = self.openai_client.chat(messages, max_tokens=1000)
        with open("/data/summary_info.txt", "w") as f:
            f.write(self.SUMMARY_INFO)

    def generate_response(self, messages: list) -> list:
        """
        Generate a response from the LLM based on user input and log data.
        """
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User message is required.")
        user_input = user_messages[-1]["content"]

        if len(messages) <= 2:
            if self.use_qdrant:
                self.get_vector_db_summary()
            else:
                self.get_log_summary()

            prompt = f"{PROMPT_PREFIX}{user_input}\n\n {FORMAT_RESPONSE}\n\n \
            Here is a summary of the logs you can use fro info: \n{str(self.SUMMARY_INFO)}"
            user_message = {"role": "user", "content": str(prompt)}
            messages = [
                {"role": "system", "content": "You are a production debugging expert."},
                user_message,
            ]
            response = self.openai_client.chat(messages)
            messages.append({"role": "assistant", "content": f"{response} \n{str(self.SUMMARY_INFO)}"})
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
