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
    Render the Executive Copilot workspace.
    """

    st.header("🤖 Executive Copilot")

    st.markdown(
        """
AI-powered executive decision support that transforms
institutional intelligence into concise leadership briefings.

Use the Copilot to generate an executive summary based on
the current platform intelligence.
"""
    )

    st.write("")

    left, right = st.columns(
        [3, 1],
        gap="large",
    )

    with left:

        generate = st.button(
            "🚀 Generate Executive Briefing",
            use_container_width=True,
        )

    with right:

        st.metric(
            label="AI Engine",
            value="Ready",
            delta="Online",
            border=True,
        )

    st.divider()

    if generate:

        with st.spinner(
            "Generating executive briefing..."
        ):

            briefing = generate_executive_brief()

        st.success(
            "Executive briefing generated successfully."
        )

        with st.container(
            border=True,
        ):

            st.subheader(
                "📋 Executive Briefing"
            )

            st.text_area(
                label="",
                value=briefing,
                height=420,
            )

    else:

        st.info(
            """
Press **Generate Executive Briefing** to create an
AI-generated executive summary based on the latest
NorthStar platform intelligence.
"""
        )