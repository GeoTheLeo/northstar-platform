"""
NorthStar Metrics View
"""

from typing import Any

import streamlit as st

from northstar.models.dashboard_data import DashboardData


def _metric_card(
    title: str,
    value: Any,
) -> None:
    """
    Render a single executive KPI card.
    """

    html = (
        f'<div class="metric-card">'
        f'<div class="metric-title">{title}</div>'
        f'<div class="metric-value">{value}</div>'
        f"</div>"
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_metrics(
    dashboard: DashboardData,
) -> None:
    """
    Render the Executive KPI overview.
    """

    st.subheader("Executive Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _metric_card(
            "Learners",
            dashboard.total_learners,
        )

    with col2:
        _metric_card(
            "At-Risk Learners",
            dashboard.at_risk_learners,
        )

    with col3:
        _metric_card(
            "Retention",
            f"{dashboard.retention_rate:.1f}%",
        )

    with col4:
        _metric_card(
            "Churn",
            f"{dashboard.churn_rate:.1f}%",
        )
