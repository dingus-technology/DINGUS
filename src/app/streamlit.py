import os
import time

import requests
import streamlit as st

# Load API URL from environment variable (set this in your .env file or deployment config)
CHAT_API_URL = "http://host.docker.internal:8000"  # os.getenv("CHAT_API_URL")
CHAT_API_ENDPOINT_URL = os.path.join(CHAT_API_URL, "chat")

st.title("Chat with AI")

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send chat history (excluding the latest user input) to FastAPI
    response_text = "..."
    try:
        response = requests.post(CHAT_API_ENDPOINT_URL, json={"messages": st.session_state.messages})
        response.raise_for_status()
        response_text = response.json().get("response", "🤖 No response from Dingus.")
        print(response_text)
    except requests.exceptions.RequestException as e:
        response_text = f"⚠️ Error: {str(e)}"

    # Display assistant response with a typing effect
    with st.chat_message("assistant"):
        message_placeholder = st.empty()  # Create an empty container
        response_so_far = ""  # Initialize response accumulator

        # Replace newline characters with HTML <br> tag for new lines
        response_text = response_text.replace("\n", "<br>")

        for word in response_text.split():
            response_so_far += word + " "  # Add word with space
            message_placeholder.markdown(response_so_far, unsafe_allow_html=True)  # Update displayed text with HTML
            time.sleep(0.05)  # Delay for typing effect

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
