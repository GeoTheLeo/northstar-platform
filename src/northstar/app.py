"""
NorthStar Executive Platform

Application entry point for the NorthStar Applied AI Platform.
"""

from typing import Literal, cast

import streamlit as st

from northstar.config import (
    APP_NAME,
    CAPTION,
    INITIAL_SIDEBAR_STATE,
    LAYOUT,
    PAGE_ICON,
    PAGE_TITLE,
)
from northstar.controller import NorthStarController
from northstar.logging import logger
from northstar.ui.activity import render_activity
from northstar.ui.analytics import render_analytics
from northstar.ui.assistant import render_assistant
from northstar.ui.copilot import render_copilot
from northstar.ui.metrics import render_metrics
from northstar.ui.model_registry import render_model_registry
from northstar.ui.theme import load_theme


def main() -> None:
    """
    Launch the NorthStar Executive Platform.
    """

    logger.info("NorthStar application started.")

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=cast(
            Literal["centered", "wide"],
            LAYOUT,
        ),
        initial_sidebar_state=cast(
            Literal["auto", "expanded", "collapsed"],
            INITIAL_SIDEBAR_STATE,
        ),
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

    # Executive KPI Command Center

    render_metrics(
        dashboard,
    )

    st.divider()

    # Analytics

    render_analytics(
        dashboard,
    )

    st.divider()

    # Executive Copilot

    render_copilot()

    st.divider()

    # Knowledge Assistant

    render_assistant()

    st.divider()

    # MLOps Operations

    render_model_registry()

    st.divider()

    # Platform Activity

    render_activity()

    st.caption(
        CAPTION,
    )


if __name__ == "__main__":
    main()