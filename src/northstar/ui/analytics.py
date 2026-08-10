"""
NorthStar Analytics Workspace.
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

    if recommendation.priority == "HIGH":

        st.error(
            f"### {recommendation.title}\n\n"
            f"{recommendation.rationale}\n\n"
            f"**Recommended Action**\n\n"
            f"{recommendation.action}"
        )

    elif recommendation.priority == "MEDIUM":

        st.warning(
            f"### {recommendation.title}\n\n"
            f"{recommendation.rationale}\n\n"
            f"**Recommended Action**\n\n"
            f"{recommendation.action}"
        )

    else:

        st.success(
            f"### {recommendation.title}\n\n"
            f"{recommendation.rationale}\n\n"
            f"**Recommended Action**\n\n"
            f"{recommendation.action}"
        )


def render_analytics(
    dashboard: DashboardData,
) -> None:

    st.header("📊 Analytics Workspace")

    st.markdown(
        """
Institution-wide analytics supporting executive
decision making through learner performance,
engagement analysis and behavioral segmentation.
"""
    )

    # --------------------------------------------------
    # Executive Analytics Brief
    # --------------------------------------------------

    if dashboard.executive_insight is not None:

        with st.container(border=True):

            st.subheader(
                "🧠 Executive Analytics Brief"
            )

            st.markdown(
                f"### {dashboard.executive_insight.headline}"
            )

            st.write(
                dashboard.executive_insight.summary
            )

            st.progress(
                dashboard.executive_insight.confidence
            )

            st.caption(
                f"Confidence Score: "
                f"{dashboard.executive_insight.confidence:.0%}"
            )

    st.divider()

    # --------------------------------------------------
    # Executive Analytics
    # --------------------------------------------------

    left, right = st.columns(
        2,
        gap="large",
    )

    attendance_chart = px.histogram(
        dashboard.learner_df,
        x="attendance",
        title="Attendance Distribution",
    )

    attendance_chart.update_layout(
        height=SMALL_CHART_HEIGHT,
    )

    segment_chart = px.histogram(
        dashboard.segments_df,
        x="cluster",
        title="Learner Segment Distribution",
    )

    segment_chart.update_layout(
        height=SMALL_CHART_HEIGHT,
    )

    with left:

        st.plotly_chart(
            cast(object, attendance_chart),
            use_container_width=True,
        )

    with right:

        st.plotly_chart(
            cast(object, segment_chart),
            use_container_width=True,
        )

    st.divider()

    # --------------------------------------------------
    # Engagement Analytics
    # --------------------------------------------------

    engagement_chart = px.scatter(
        dashboard.learner_df,
        x="engagement_score",
        y="assessment_score",
        title="Engagement vs Assessment",
    )

    engagement_chart.update_layout(
        height=LARGE_CHART_HEIGHT,
    )

    st.plotly_chart(
        cast(object, engagement_chart),
        use_container_width=True,
    )

    st.divider()

    # --------------------------------------------------
    # Executive Recommendation Engine
    # --------------------------------------------------

    st.subheader(
        "🚀 Executive Recommendation Engine"
    )

    for recommendation in dashboard.recommendations:

        _render_recommendation(
            recommendation,
        )