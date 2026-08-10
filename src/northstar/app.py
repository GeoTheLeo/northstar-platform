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
from northstar.demo import render_demo_selector
from northstar.logging import logger
from northstar.navigation import render_workspace_selector
from northstar.status import render_status_bar
from northstar.ui.activity import render_activity
from northstar.ui.ai_insights import (
    render_ai_insights,
)
from northstar.ui.analytics import (
    render_analytics,
)
from northstar.ui.assistant import (
    render_assistant,
)
from northstar.ui.copilot import (
    render_copilot,
)
from northstar.ui.dashboard import (
    render_dashboard,
)
from northstar.ui.model_registry import (
    render_model_registry,
)
from northstar.ui.platform_health import (
    render_platform_health,
)
from northstar.ui.scenario_simulator import (
    render_scenario_simulator,
)
from northstar.ui.theme import (
    load_theme,
)


def main() -> None:
    """
    Launch the NorthStar Executive Platform.
    """

    logger.info(
        "NorthStar application started."
    )

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=cast(
            Literal[
                "centered",
                "wide",
            ],
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

    st.title(
        APP_NAME,
    )

    render_status_bar()

    controller = NorthStarController()

    #
    # Release Candidate:
    # Demo mode exists but is not yet wired into
    # the dashboard pipeline.
    #
    demo = render_demo_selector()

    # Reserved for Release Candidate 2
    _ = demo

    dashboard = controller.dashboard()

    workspace = render_workspace_selector()

    # --------------------------------------------------
    # Executive Dashboard
    # --------------------------------------------------

    if workspace == "🏠 Executive Dashboard":

        render_dashboard(
            dashboard,
        )

    # --------------------------------------------------
    # Analytics
    # --------------------------------------------------

    elif workspace == "📊 Analytics":

        render_analytics(
            dashboard,
        )

    # --------------------------------------------------
    # AI Insights
    # --------------------------------------------------

    elif workspace == "🧠 AI Insights":

        render_ai_insights(
            dashboard,
        )

    # --------------------------------------------------
    # Scenario Simulator
    # --------------------------------------------------

    elif workspace == "🎮 Scenario Simulator":

        render_scenario_simulator(
            dashboard,
        )

    # --------------------------------------------------
    # Executive Copilot
    # --------------------------------------------------

    elif workspace == "🤖 Executive Copilot":

        render_copilot()

    # --------------------------------------------------
    # Knowledge Assistant
    # --------------------------------------------------

    elif workspace == "💬 Knowledge Assistant":

        render_assistant()

    # --------------------------------------------------
    # Model Registry
    # --------------------------------------------------

    elif workspace == "📦 Model Registry":

        render_model_registry()

    # --------------------------------------------------
    # Platform Services
    # --------------------------------------------------

    elif workspace == "🖥 Platform Health":

        render_platform_health()

    # --------------------------------------------------
    # Activity Timeline
    # --------------------------------------------------

    elif workspace == "📈 Activity Timeline":

        render_activity()

    st.caption(
        CAPTION,
    )


if __name__ == "__main__":
    main()