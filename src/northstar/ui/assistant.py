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
    Render the NorthStar Knowledge Assistant.
    """

    st.header("💬 Knowledge Assistant")

    st.markdown(
        """
Ask questions about the NorthStar platform using
Retrieval-Augmented Generation (RAG).

The assistant retrieves relevant institutional knowledge
before generating each response.
"""
    )

    st.write("")

    left, right = st.columns(
        [4, 1],
        gap="large",
    )

    with left:

        st.info(
            """
**Capabilities**

• Semantic search

• Retrieval-Augmented Generation (RAG)

• Context-aware responses

• Institutional knowledge retrieval
"""
        )

    with right:

        st.metric(
            label="Knowledge Base",
            value="Online",
            delta="Indexed",
            border=True,
        )

    st.divider()

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
        "Ask NorthStar a question..."
    )

    if not question:

        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    with st.spinner(
        "Searching institutional knowledge..."
    ):

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