"""
llm_clients.py

This file contains the OpenAIChatClient class.
"""

import logging

from openai import OpenAI

from dingus.logger import set_logging
from dingus.settings import MODEL_PRICING

set_logging()

logger = logging.getLogger(__name__)


class OpenAIChatClient:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the OpenAIChatClient.

        :param api_key: The API key for OpenAI.
        :param model: The model to use for the chat (default is "gpt-4").
        """
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.MODEL_PRICING = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "o1-mini": {"input": 0.003, "output": 0.012},
        }

    def _get_price(self, response):
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        pricing = MODEL_PRICING.get(self.model, {"input": 0.01, "output": 0.03})
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])

        logger.info(
            f"OpenAI API Cost: ${cost:.4f} | Model: {self.model} | "
            f"Input Tokens: {input_tokens} | Output Tokens: {output_tokens} | Total Tokens: {total_tokens}"
        )

    def chat(self, messages: list, temperature: float = 0.0, max_tokens: int = 4000) -> str:
        """
        Send a chat message to the OpenAI API and log cost.

        :param messages: A list of messages in OpenAI format.
        :param temperature: Sampling temperature (default 0.7).
        :param max_tokens: Max tokens to generate (default 500).
        :return: The assistant's response as a string.
        """
        for message in messages:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise ValueError(f"Invalid message structure: {message}")

        try:
            logger.info(f"OpenAI call with {len(str(messages))} characters.")

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens
            )
            self._get_price(response=response)
            content = response.choices[0].message.content if response.choices[0].message.content is not None else ""
            return content.strip()
        except Exception as e:
            logger.error(f"Error during API call: {e}")
            return f"Error during API call: {e}"
