"""
NorthStar Executive Platform

Application entry point.
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
from northstar.navigation import render_workspace_selector
from northstar.ui.analytics import render_analytics
from northstar.ui.assistant import render_assistant
from northstar.ui.copilot import render_copilot
from northstar.ui.dashboard import render_dashboard
from northstar.ui.model_registry import render_model_registry
from northstar.ui.platform_health import render_platform_health
from northstar.ui.theme import load_theme


def main() -> None:
    """
    Launch NorthStar.
    """

    logger.info("NorthStar started.")

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=cast(
            Literal["centered", "wide"],
            LAYOUT,
        ),
        initial_sidebar_state=cast(
            Literal[
                "auto",
                "expanded",
                "collapsed",
            ],
            INITIAL_SIDEBAR_STATE,
        ),
    )

    load_theme()

    st.title(APP_NAME)

    controller = NorthStarController()

    dashboard = controller.dashboard()

    workspace = render_workspace_selector()

    if workspace == "🏠 Executive Dashboard":

        render_dashboard(
            dashboard,
        )

    elif workspace == "📊 Analytics":

        render_analytics(
            dashboard,
        )

    elif workspace == "🧠 AI Insights":

        render_analytics(
            dashboard,
        )

    elif workspace == "🤖 Executive Copilot":

        render_copilot()

    elif workspace == "💬 Knowledge Assistant":

        render_assistant()

    elif workspace == "📦 Model Registry":

        render_model_registry()

    elif workspace == "🖥 Platform Health":

        render_platform_health()

    elif workspace == "📈 Activity Timeline":

        from northstar.ui.activity import render_activity

        render_activity()

    st.caption(CAPTION)


if __name__ == "__main__":
    main()