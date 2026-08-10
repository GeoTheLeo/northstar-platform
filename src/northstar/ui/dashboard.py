"""
NorthStar Executive Dashboard View.
"""

import streamlit as st

from northstar.executive import render_executive_overview
from northstar.models.dashboard_data import DashboardData
from northstar.ui.activity import render_activity
from northstar.ui.metrics import render_metrics
from northstar.ui.platform_health import render_platform_health


def render_dashboard(
    dashboard: DashboardData,
) -> None:
    """
    Render the Executive Dashboard landing page.
    """

    st.header("🏠 Executive Dashboard")

    st.markdown(
        """
Executive summary of institutional performance,
AI-generated insights,
platform health,
and operational activity.
"""
    )

    st.write("")

    # ==================================================
    # Executive Hero Area
    # ==================================================

    left, right = st.columns(
        [5, 4],
        gap="large",
    )

    with left:

        st.subheader(
            "📊 Executive KPI Command Center"
        )

        render_metrics(
            dashboard,
        )

    with right:

        st.subheader(
            "🧠 Executive Summary"
        )

        render_executive_overview(
            dashboard,
        )

    st.divider()

    # ==================================================
    # Operations
    # ==================================================

    operations, activity = st.columns(
        [2, 3],
        gap="large",
    )

    with operations:

        render_platform_health()

    with activity:

        st.subheader(
            "📈 Recent Platform Activity"
        )

        render_activity()