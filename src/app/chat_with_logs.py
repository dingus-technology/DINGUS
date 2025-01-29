"""chat_with_logs.py

This file lets you interact with a logs file like an AI agent.
"""

import os
import sys

from app.clients import OpenAIChatClient
from app.utils import display_response, get_logs_data, set_logging


class ChatWithLogs:

    def __init__(self):
        MODEL = "gpt-4o"
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        LOG_DATA_FILE_PATH = "/src/data/log_data.csv"
        TRUNCATE_LOGS = 1

        SUMMARY_PROMPT = """
        You are an expert in log analysis and debugging. Your task is to carefully analyse the provided
        log data to filter out unnecessary information while preserving all critical details.
        The summarised output will be used as context for an AI debugging agent to assist users.
        Make sure your response meets the following requirements:

        Identify and retain all relevant information such as error messages, warnings, timestamps, and critical events.
        Filter out repetitive or non-essential data unless it helps identify patterns or recurring issues.
        Provide a concise and structured summary of the logs, highlighting any anomalies, root causes,
        or unusual behaviour.
        Ensure the output is well-formatted and easy to interpret for downstream tasks.
        The log data is provided in CSV format below: \n
        """

        self.openai_client = OpenAIChatClient(api_key=API_KEY, model=MODEL)
        self.log_data = get_logs_data(LOG_DATA_FILE_PATH)[0:TRUNCATE_LOGS]
        messages = [
            {"role": "system", "content": "You are a production debugging expert."},
            {"role": "user", "content": SUMMARY_PROMPT + str(self.log_data)},
        ]

        self.LOG_DATA_SUMMARY = self.openai_client.chat(messages, max_tokens=1000)

        self.PROMPT_PREFIX = """
            You are a debugging expert.Analyse the logs and report back
            on anything interesting related to the user question.\n
            Reply back as if you are talking to the user directly.\n
            The response will be put into a terminal so do not format it.\n
            Keep the response short.\n
            The user question is as follows:\n
        """

    def generate_response(self, user_input: str, messages: list | None = None) -> tuple[str, list]:
        """
        Generate a response from the LLM based on user input and log data.
        """
        prompt = (
            f"{self.PROMPT_PREFIX}{user_input}\n\n"
            f"Here is a summary of the logs: \n{self.LOG_DATA_SUMMARY}\n\n"
            f"Here are the logs in CSV format: \n{str(self.log_data)}"
        )
        user_message = {"role": "user", "content": str(prompt)}
        if messages:
            messages.append(user_message)
        else:
            messages = [
                {"role": "system", "content": "You are a production debugging expert."},
                user_message,
            ]

        response = self.openai_client.chat(messages)
        messages.append({"role": "assistant", "content": response})
        return response, messages


def main():
    """
    Main function to handle user interaction in the terminal.
    """
    set_logging()
    sys.stdout.write(
        """
  _____ _____ _   _  _____ _    _  _____ 
 |  __ \_   _| \ | |/ ____| |  | |/ ____|
 | |  | || | |  \| | |  __| |  | | (___  
 | |  | || | | .   | | |_ | |  | |\___ \ 
 | |__| || |_| |\  | |__| | |__| |____) |
 |_____/_____|_| \_|\_____|\____/|_____/ 

"""  # noqa  # Ignore all flake8 errors
    )
    chat_with_logs = ChatWithLogs()
    messages = []

    sys.stdout.write("\n\nWelcome to the Debugging Assistant! Type your question below.")
    sys.stdout.write("Type 'exit' to quit.\n")

    while True:
        user_input = input("\nAsk a question about your logs: ")
        if user_input.lower() == "exit":
            sys.stdout.write("Goodbye!")
            break

        try:
            response, messages = chat_with_logs.generate_response(user_input, messages)
            display_response("\nDingus: " + response)
        except Exception as e:
            print("An error occurred:", e)


if __name__ == "__main__":
    main()
