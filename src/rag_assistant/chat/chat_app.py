import sys
from pathlib import Path

project_root = (
    Path(__file__).resolve().parents[3]
)

sys.path.append(
    str(project_root / "src")
)

import streamlit as st

from rag_assistant.chat.assistant import (
    ask_assistant,
)

st.set_page_config(
    page_title="NorthStar AI Assistant",
    layout="wide",
)

st.title(
    "NorthStar AI Knowledge Assistant"
)

st.markdown(
    """
    Ask questions about:

    - Early Warning System
    - Learner Segmentation
    - BI Metrics
    - Student Success Strategies
    - NorthStar Platform
    """
)

if "messages" not in st.session_state:

    st.session_state.messages = []

for message in (
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

question = st.chat_input(
    "Ask NorthStar..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(question)

    response = ask_assistant(
        question
    )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )