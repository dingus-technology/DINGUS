"""app.py

This file supports the streamlit frontend"""

import os

import pandas as pd
import requests
import streamlit as st

from src.utils import stream_data

st.set_page_config(page_title="Chat with Dingus", page_icon="/assets/logo-light.png")

CHAT_API_URL = os.getenv("CHAT_API_URL")
CHAT_API_ENDPOINT_URL = os.path.join(CHAT_API_URL, "chat")
ASSISTANT_AVATAR_URL = "/assets/logo-light.png"

st.title("Chat with Dingus 💬")
st.text(
    "Dingus will identify issues, find causes and provide actions for problems that currently exist in your infrastructure."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    content = message["content"]
    role = message["role"]
    avatar_icon = ASSISTANT_AVATAR_URL if role == "assistant" else None
    with st.chat_message(role, avatar=avatar_icon):
        if isinstance(content, str):
            st.write(content)
        elif isinstance(content, pd.DataFrame):
            st.line_chart(content)

if prompt := st.chat_input("How are my logs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Fetching..."):
        try:
            response = requests.post(CHAT_API_ENDPOINT_URL, json={"messages": st.session_state.messages})
            response.raise_for_status()
            response_text = response.json().get("response", "🤖 No response from Dingus.")

        except requests.exceptions.RequestException as e:
            response_text = f"⚠️ Error: {str(e)}"
        except Exception as e:
            print(e)

    assistant_message = [response_text]
    for content in assistant_message:
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR_URL):
            if isinstance(content, str):
                st.write_stream(stream_data(content))

            st.session_state.messages.append({"role": "assistant", "content": content})
