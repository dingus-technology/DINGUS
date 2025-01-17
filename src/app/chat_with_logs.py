import csv
import os

from app.clients import OpenAIChatClient

MODEL = "gpt-4o"
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

openai_client = OpenAIChatClient(api_key=API_KEY, model=MODEL)

with open("data/log_data.csv", mode="r") as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    data = [header]
    for row in csv_reader:
        data.append(row)

PROMPT_PREFIX = "You are a debugging expert, analyse the logs and report back on anything interesting realted to the use question.\n the user question is as follow: "


def main(user_input: str):

    prompt = PROMPT_PREFIX + user_input + "\nHere are the logs: \n" + str(data[0:100])

    messages = [
        {"role": "system", "content": "You a production debugging expert."},
        {"role": "user", "content": prompt},
    ]
    response = openai_client.chat(messages)
    return response
