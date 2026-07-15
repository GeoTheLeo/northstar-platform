"""
NorthStar Metrics View

Responsible for rendering executive KPI cards.

This module contains presentation logic only.
No business calculations are performed here.
"""

import streamlit as st


def _metric_card(title: str, value) -> None:
    """
    Render a single KPI card.
    """

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-title">
                {title}
            </div>

            <div class="metric-value">
                {value}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(dashboard: dict) -> None:
    """
    Render the executive KPI section.
    """

    st.subheader("Executive Overview")

    kpis = dashboard["kpis"]
    risk_metrics = dashboard["risk_metrics"]
    segment_metrics = dashboard["segment_metrics"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _metric_card(
            "Students",
            kpis["total_students"],
        )

    with col2:
        _metric_card(
            "At-Risk Learners",
            risk_metrics["at_risk_students"],
        )

    with col3:
        _metric_card(
            "Active Segments",
            segment_metrics["total_segments"],
        )

    with col4:
        _metric_card(
            "Risk Percentage",
            f'{risk_metrics["risk_percentage"]}%',
        )