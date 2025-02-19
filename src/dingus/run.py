"""run.py

Contains the CLI for the Dingus chatbot."""

import sys

from dingus.chat_with_logs import ChatWithLogs
from dingus.utils import display_response, set_logging

set_logging()


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
