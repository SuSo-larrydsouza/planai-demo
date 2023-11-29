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
