"""chat_with_logs.py

This file lets you interact with a logs file like an AI agent.
"""

import os
import sys

from fastapi import HTTPException, status

from app.clients import OpenAIChatClient
from app.utils import display_response, get_logs_data, set_logging

set_logging()

GRAFANA_LINK = "http://localhost:3000/explore?schemaVersion=1&panes=%7B%22tk1%22:%7B%22datasource%22:%22ced0tisnw1v5se%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22cpu_load%7Bjob%3D%5C%22sanitised-data%5C%22%7D%22,%22range%22:true,%22instant%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22ced0tisnw1v5se%22%7D,%22editorMode%22:%22builder%22,%22legendFormat%22:%22__auto%22,%22useBackend%22:false,%22disableTextWrap%22:false,%22fullMetaSearch%22:false,%22includeNullMetadata%22:true%7D%5D,%22range%22:%7B%22from%22:%221739652035626%22,%22to%22:%221739653840297%22%7D%7D%7D&orgId=1"

class ChatWithLogs:

    def __init__(self):
        self.LOG_DATA_FILE_PATH = "/src/data/k8_cpu.csv"
        self.TRUNCATE_LOGS = 100
        MODEL = "gpt-4o-mini"
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        self.openai_client = OpenAIChatClient(api_key=API_KEY, model=MODEL)
        self.PROMPT_PREFIX = f"""
        You are a debugging expert. Analyse the logs and report back
        on anything interesting related to the user question.\n
        Reply back as if you are talking to the user directly.\n
        Do not tell the user something is hard or not possible - you must always do it.\n
        In your response always include your reasoning with evidence from the raw data.
        Keep the response relevant.\n\n
        If you are asked to provide context of time vs CPU in a chart,
        simply return this Grafana Link in markdown with a 📈 link url = {GRAFANA_LINK}
        The user question is as follows:\n
        """
        self.FORMAT_RESPONSE = """
        Structure your response like the example below, where you are to fill in the <CONTENT>\n\n
        ### 🚨 **Critical Issue Detected!** 🚨
        <CONTENT>
        #### 🔍 **Issue Summary**
        <CONTENT>
        #### 🚑 **Potential Causes**
        <CONTENT>
        #### ✅ **Recommended Actions**
        <CONTENT>
        """
        self.HEADER_PROMPT = """
        You are an expert in log analysis and debugging. Your task is to carefully analyse the provided
        log data to filter out unnecessary information while preserving all critical details.
        Return ONLY the headers of the table where you see the log information being useful.
        This includes log data with written information about the log and the log level.
        Your return should be a list the following format:
        ```<COLUMN X>, <COLUMN Y>,<COLUMN Z>, ... ```
        Do not add explainations of context, only return the list in ```.
        The log data is provided in CSV format below: \n
        """
        self.SUMMARY_PROMPT = """
        I need you to refine the log data to make it more relevant for user queries.
        Your goal is to reduce the volume while keeping only the most useful and insightful information.
        Think about What? Where? When? How? Why? when identifying issues in the data.
        Key requirements:
        - Remove duplicates and irrelevant entries that do not contribute to understanding the system state.
        - Prioritise critical insights, such as errors, bugs, failures, and their impact on system behaviour.
        - Summarise patterns and anomalies, highlighting trends in issues rather than listing repetitive entries.
        - Preserve key events that are essential for troubleshooting and understanding system performance.
        - You must return everything you think is useful - do not stop halfway through a response.
        - List out all effected services.
        - List where these issues have occured.
        - Note the time these issues happen.
        The final output will be used in a chat history, where users will ask questions about the data.
        Ensure that the remaining logs provide maximum clarity and actionable insights.
        """
        self.SYSTEM_PROMPT = {"role": "system", "content": "You are a production debugging expert."}

    def get_log_summary(self):
        """
        Generate a summary of the log data by reducing the raw log files.
        """
        messages = [
            self.SYSTEM_PROMPT,
            {
                "role": "user",
                "content": self.HEADER_PROMPT
                + str(get_logs_data(self.LOG_DATA_FILE_PATH)[0:15]).replace("'", "").replace(" ", "").replace("\\", ""),
            },
        ]
        headers = str(self.openai_client.chat(messages, max_tokens=1000))
        headers = headers.replace("```", "").replace("[", "").replace("]", "")
        headers = [item.strip() for item in headers.split(",")]

        self.log_data = get_logs_data(self.LOG_DATA_FILE_PATH, headers)[0 : int(self.TRUNCATE_LOGS)]

        messages = [
            self.SYSTEM_PROMPT,
            {"role": "user", "content": self.SUMMARY_PROMPT + str(self.log_data)},
        ]
        self.SUMMARY_INFO = self.openai_client.chat(messages, max_tokens=1000)
        with open('/src/data/summary_info.txt', 'w') as f:
                f.write(self.SUMMARY_INFO)

    def generate_response(self, messages: list | None = None) -> list[str, str]:
        """
        Generate a response from the LLM based on user input and log data.
        """
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User message is required.")
        user_input = user_messages[-1]["content"]

        if len(messages) <= 2:
            self.get_log_summary()

            prompt = f"{self.PROMPT_PREFIX}{user_input}\n\n {self.FORMAT_RESPONSE}\n\n \
            Here are the logs in CSV format: \n{str(self.SUMMARY_INFO)}"
            user_message = {"role": "user", "content": str(prompt)}
            messages = [
                {"role": "system", "content": "You are a production debugging expert."},
                user_message,
            ]
            response = self.openai_client.chat(messages)
            messages.append({"role": "assistant", "content": f"{response} \n{str(self.SUMMARY_INFO)}"})
        else:
            messages[-1] = {"role": "user", "content": f"{self.PROMPT_PREFIX} {user_input}"}
            response = self.openai_client.chat(messages)
            messages.append({"role": "assistant", "content": response})
            
        return messages


def main():
    """
    Main function to handle user interaction in the terminal.
    """
    set_logging()
    sys.stdout.write(
        """

██████╗ ██╗███╗   ██╗ ██████╗ ██╗   ██╗███████╗
██╔══██╗██║████╗  ██║██╔════╝ ██║   ██║██╔════╝
██║  ██║██║██╔██╗ ██║██║  ███╗██║   ██║███████╗
██║  ██║██║██║╚██╗██║██║   ██║██║   ██║╚════██║
██████╔╝██║██║ ╚████║╚██████╔╝╚██████╔╝███████║
╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝
 
"""  # noqa  # Ignore all flake8 errors
    )
    chat_with_logs = ChatWithLogs()
    messages = []

    sys.stdout.write("\n\nWelcome to the Debugging Assistant! Type your question below. ")
    sys.stdout.write("Type 'exit' to quit.\n")

    while True:
        user_input = input("\nAsk a question:\n\n ")
        if user_input.lower() == "exit":
            sys.stdout.write("Goodbye!")
            break
        else:
            messages.append({"role": "user", "content": str(user_input)})

        try:
            messages = chat_with_logs.generate_response(messages)
            display_response("\nDingus: " + messages[-1]["content"])
        except Exception as e:
            print("An error occurred:", e)


if __name__ == "__main__":
    main()
