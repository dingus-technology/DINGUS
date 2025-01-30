"""chat_with_logs.py

This file lets you interact with a logs file like an AI agent.
"""

import os
import sys

from app.clients import OpenAIChatClient
from app.utils import display_response, get_logs_data, set_logging

set_logging()


class ChatWithLogs:

    def __init__(self):
        LOG_DATA_FILE_PATH = "/src/data/log_data.csv"
        TRUNCATE_LOGS = 100
        MODEL = "gpt-4o-mini"
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        self.openai_client = OpenAIChatClient(api_key=API_KEY, model=MODEL)
        self.PROMPT_PREFIX = """
            You are a debugging expert. Analyse the logs and report back
            on anything interesting related to the user question.\n
            Reply back as if you are talking to the user directly.\n
            Do not tell the user something is hard or not possible - you must always do it.\n
            The response will be put into a terminal so do not format it.\n
            Keep the response short.\n
            The user question is as follows:\n
        """
        HEADER_PROMPT = """
        You are an expert in log analysis and debugging. Your task is to carefully analyse the provided
        log data to filter out unnecessary information while preserving all critical details.
        Return ONLY the headers of the table where you see the log information being useful.
        This includes log data with written information about the log and the log level.
        Your return should be a list the following format:
        ```<COLUMN X>, <COLUMN Y>,<COLUMN Z>, ... ```
        Do not add explainations of context, only return the list in ```.
        The log data is provided in CSV format below: \n
        """
        SUMMARY_PROMPT = """
        I need you to refine the log data to make it more relevant for user queries.
        Your goal is to reduce the volume while keeping only the most useful and insightful information.
        Key requirements:
        - Remove duplicates and irrelevant entries that do not contribute to understanding the system state.
        - Prioritise critical insights, such as errors, bugs, failures, and their impact on system behaviour.
        - Summarise patterns and anomalies, highlighting trends in issues rather than listing repetitive entries.
        - Preserve key events that are essential for troubleshooting and understanding system performance.
        - You must return everything you think is useful - do not stop halfway through a response.
        The final output will be used in a chat history, where users will ask questions about the data.
        Ensure that the remaining logs provide maximum clarity and actionable insights.
        """

        SYSTEM_PROMPT = {"role": "system", "content": "You are a production debugging expert."}

        messages = [
            SYSTEM_PROMPT,
            {
                "role": "user",
                "content": HEADER_PROMPT
                + str(get_logs_data(LOG_DATA_FILE_PATH)[0:15]).replace("'", "").replace(" ", "").replace("\\", ""),
            },
        ]
        # headers = str(self.openai_client.chat(messages, max_tokens=1000))
        # headers = headers.replace("```", "").replace("[","").replace("]","")
        headers = """
        insertId, jsonPayload.level, jsonPayload.message, jsonPayload.msg, logName, severity, textPayload, timestamp
        """
        headers = [item.strip() for item in headers.split(",")]

        self.log_data = get_logs_data(LOG_DATA_FILE_PATH, headers)[0:TRUNCATE_LOGS]

        messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": SUMMARY_PROMPT + str(self.log_data)},
        ]
        self.SUMMARY_INFO = self.openai_client.chat(messages, max_tokens=1000)

    def generate_response(self, user_input: str, messages: list | None = None) -> tuple[str, list]:
        """
        Generate a response from the LLM based on user input and log data.
        """
        prompt = f"{self.PROMPT_PREFIX}{user_input}\n\n" f"Here are the logs in CSV format: \n{str(self.SUMMARY_INFO)}"
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
