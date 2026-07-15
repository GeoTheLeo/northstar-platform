"""
NorthStar Metrics View
"""

import streamlit as st

from platform.models.dashboard_data import DashboardData


def _metric_card(title: str, value) -> None:

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


def render_metrics(
    dashboard: DashboardData,
) -> None:

    st.subheader(
        "Executive Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        _metric_card(
            "Students",
            dashboard.kpis["total_students"],
        )

    with col2:

        _metric_card(
            "At-Risk Learners",
            dashboard.risk_metrics[
                "at_risk_students"
            ],
        )

    with col3:

        _metric_card(
            "Active Segments",
            dashboard.segment_metrics[
                "total_segments"
            ],
        )

    with col4:

        _metric_card(
            "Risk Percentage",
            f'{dashboard.risk_metrics["risk_percentage"]}%',
        )