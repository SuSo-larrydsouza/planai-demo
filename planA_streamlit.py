import hmac
import os
from typing import cast

import streamlit as st
from canopy.chat_engine import ChatEngine
from canopy.context_engine import ContextEngine
from canopy.knowledge_base import KnowledgeBase
from canopy.models.api_models import (
    StreamingChatResponse,
)
from canopy.models.data_models import UserMessage, AssistantMessage
from canopy.tokenizer import Tokenizer


###################################################################################################
# Scrappy password protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

###################################################################################################
# Main Streamlit app starts here
st.title("♻️ PlanAI")

planAI_avatar = "img/planA_logo.jpg"

# Initialize canopy library
Tokenizer.initialize()
kb = KnowledgeBase(index_name=os.getenv("PINECONE_INDEX_NAME"))
kb.connect()
context_engine = ContextEngine(kb)
chat_engine = ChatEngine(context_engine)

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(str(message.role), avatar=planAI_avatar if isinstance(message, AssistantMessage) else "user"):
        st.markdown(message.content)

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append(UserMessage(content=prompt))
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=planAI_avatar):
        message_placeholder = st.empty()
        full_response = ""
        canopy_response = chat_engine.chat(messages=st.session_state.messages, stream=True)
        for response in cast(StreamingChatResponse, canopy_response).chunks:
            full_response += (response.choices[0].delta["content"] or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(AssistantMessage(content=full_response))
