"""
NorthStar Knowledge Assistant View

Provides the conversational interface for the
NorthStar RAG assistant.
"""

import streamlit as st

from rag_assistant.chat.assistant import (
    ask_assistant,
)


def render_assistant() -> None:
    """
    Render the conversational assistant.
    """

    st.subheader(
        "NorthStar Knowledge Assistant"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    question = st.chat_input(
        "Ask NorthStar..."
    )

    if not question:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    response = ask_assistant(
        question
    )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            response
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )