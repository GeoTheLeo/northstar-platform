"""
NorthStar Executive Copilot View

Renders the Executive Copilot interface.
"""

import streamlit as st

from rag_assistant.chat.copilot import (
    generate_executive_brief,
)


def render_copilot() -> None:
    """
    Render the executive copilot.
    """

    st.subheader(
        "NorthStar Executive Copilot"
    )

    if st.button(
        "Generate Executive Briefing"
    ):

        briefing = (
            generate_executive_brief()
        )

        st.text_area(
            "Executive Briefing",
            briefing,
            height=300,
        )