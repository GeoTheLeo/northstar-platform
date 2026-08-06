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

    render_metrics(
        dashboard,
    )

    st.divider()

    render_executive_overview(
        dashboard,
    )

    st.divider()

    st.subheader("🖥 Platform Status")

    render_platform_health()

    st.divider()

    st.subheader("📈 Recent Activity")

    render_activity()