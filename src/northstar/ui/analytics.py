"""
NorthStar Analytics View
"""

from typing import cast

import plotly.express as px
import streamlit as st

from northstar.advisor.recommendation import Recommendation
from northstar.config import (
    LARGE_CHART_HEIGHT,
    SMALL_CHART_HEIGHT,
)
from northstar.models.dashboard_data import DashboardData


def _render_recommendation(
    recommendation: Recommendation,
) -> None:
    """
    Render a single executive recommendation.
    """

    priority = recommendation.priority.upper()

    if priority == "HIGH":
        container = st.error
    elif priority == "MEDIUM":
        container = st.warning
    else:
        container = st.success

    container(
        (
            f"**{recommendation.title}**\n\n"
            f"**Reason:** {recommendation.rationale}\n\n"
            f"**Recommended Action:** {recommendation.action}"
        )
    )


def render_analytics(
    dashboard: DashboardData,
) -> None:
    """
    Render the Executive Analytics workspace.
    """

    st.subheader("📊 Executive Analytics")

    summary = dashboard.executive_summary

    severity = summary.severity.lower()

    if severity == "success":
        st.success(summary.headline)

    elif severity == "warning":
        st.warning(summary.headline)

    else:
        st.error(summary.headline)

    st.write(summary.recommendation)

    st.divider()

    # ----------------------------------------------------------
    # Executive Recommendation Engine
    # ----------------------------------------------------------

    st.markdown("## 🧠 Executive Recommendation Engine")

    for recommendation in dashboard.recommendations:

        _render_recommendation(
            recommendation,
        )

    st.divider()

    # ----------------------------------------------------------
    # Analytics
    # ----------------------------------------------------------

    attendance_chart = px.histogram(
        dashboard.learner_df,
        x="attendance",
        title="Attendance Distribution",
    )

    attendance_chart.update_layout(
        height=SMALL_CHART_HEIGHT,
    )

    engagement_chart = px.scatter(
        dashboard.learner_df,
        x="engagement_score",
        y="assessment_score",
        title="Engagement vs Assessment",
    )

    engagement_chart.update_layout(
        height=LARGE_CHART_HEIGHT,
    )

    segment_chart = px.histogram(
        dashboard.segments_df,
        x="cluster",
        title="Learner Segment Distribution",
    )

    segment_chart.update_layout(
        height=LARGE_CHART_HEIGHT,
    )

    st.plotly_chart(
        cast(object, attendance_chart),
        use_container_width=True,
    )

    st.plotly_chart(
        cast(object, engagement_chart),
        use_container_width=True,
    )

    st.plotly_chart(
        cast(object, segment_chart),
        use_container_width=True,
    )