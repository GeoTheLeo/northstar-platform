"""
NorthStar Executive Platform

Application entry point for the NorthStar Applied AI Platform.

Responsibilities
----------------
- Configure the Streamlit application
- Initialize the platform controller
- Load shared UI theme
- Delegate rendering to UI components

Business logic intentionally lives outside this module.
"""

# ---------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------

import streamlit as st

# ---------------------------------------------------------------------
# NorthStar imports
# ---------------------------------------------------------------------

from northstar.config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
    APP_NAME,
    CAPTION,
)

from northstar.controller import NorthStarController

from northstar.ui.theme import load_theme
from northstar.ui.metrics import render_metrics
from northstar.ui.analytics import render_analytics
from northstar.ui.copilot import render_copilot
from northstar.ui.assistant import render_assistant


def main() -> None:
    """
    Launch the NorthStar Executive Platform.
    """

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE,
    )

    load_theme()

    st.title(APP_NAME)

    st.markdown(
        """
        Unified Applied AI Platform integrating:

        - Early Warning System
        - Learner Segmentation
        - Executive Business Intelligence
        - Retrieval-Augmented Generation (RAG)
        - Executive Copilot
        - MLOps Foundation
        """
    )

    controller = NorthStarController()

    dashboard = controller.dashboard()

    render_metrics(dashboard)

    st.divider()

    render_analytics(dashboard)

    st.divider()

    render_copilot()

    st.divider()

    render_assistant()

    st.caption(CAPTION)


if __name__ == "__main__":
    main()