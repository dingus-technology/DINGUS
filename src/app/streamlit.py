import os

import pandas as pd
import requests
import streamlit as st

from app.fake_data import CAPTION, cpu_df
from app.utils import stream_data

st.set_page_config(page_title="Chat with Dingus", page_icon="assets/logo-light.png")

CHAT_API_URL = os.getenv("CHAT_API_URL")
CHAT_API_ENDPOINT_URL = os.path.join(CHAT_API_URL, "chat")

st.title("Chat with Dingus 💬 ")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    content = message["content"]
    with st.chat_message(message["role"]):
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

    assistant_message = [
        response_text,
        cpu_df,
        CAPTION,
        "[Click here to see the incident in Grafana ⚠️](http://localhost:3000/d/decr3hjw5l4owb/new-dashboard?orgId=1&from=2025-02-11T14:57:08.404Z&to=2025-02-11T15:01:20.512Z&timezone=browser&editPanel=1)",
    ]

    with st.chat_message("assistant", avatar="assets/logo-light.png"):

        for content in assistant_message:
            if isinstance(content, str):
                st.write_stream(stream_data(content))
            elif isinstance(content, pd.DataFrame):
                st.line_chart(content)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
