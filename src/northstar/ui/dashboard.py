"""
NorthStar Executive Dashboard View.
"""

import streamlit as st

from northstar.models.dashboard_data import DashboardData
from northstar.ui.metrics import render_metrics


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

    st.markdown(
        """
Welcome to **NorthStar**.

Use the navigation menu on the left to explore:

- 📊 Executive Analytics
- 🧠 AI Insights
- 🤖 Executive Copilot
- 💬 Knowledge Assistant
- 📦 Model Registry
- 🖥 Platform Health
- 📈 Activity Timeline
"""
    )