"""
NorthStar Analytics View.

Executive analytics workspace for the
NorthStar AI Learning Intelligence Platform.
"""

import plotly.express as px
import streamlit as st

from northstar.config import (
    LARGE_CHART_HEIGHT,
    SMALL_CHART_HEIGHT,
)
from northstar.models.dashboard_data import (
    DashboardData,
)
from northstar.services.advisor_service import (
    AdvisorService,
)


def render_analytics(
    dashboard: DashboardData,
) -> None:
    """
    Render the Executive Analytics workspace.
    """

    advisor = AdvisorService()

    recommendations = advisor.advise(
        dashboard,
    )

    st.subheader("📊 Executive Analytics Command Center")

    summary = dashboard.executive_summary

    if summary.severity == "success":

        st.success(summary.headline)

    elif summary.severity == "warning":

        st.warning(summary.headline)

    else:

        st.error(summary.headline)

    st.write(summary.recommendation)

    st.divider()

    st.markdown("## Executive Performance Snapshot")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Retention",
            f"{dashboard.retention_rate:.1f}%",
        )

    with col2:

        st.metric(
            "Churn",
            f"{dashboard.churn_rate:.1f}%",
        )

    with col3:

        st.metric(
            "Intervention",
            f"{dashboard.intervention_rate:.1f}%",
        )

    st.divider()

    st.markdown("## Key Business Observations")

    observations: list[str] = []

    if dashboard.retention_rate >= 90:

        observations.append(
            "Retention currently exceeds institutional targets."
        )

    else:

        observations.append(
            "Retention has fallen below the desired target."
        )

    if dashboard.at_risk_learners > 0:

        observations.append(
            f"{dashboard.at_risk_learners:,} learners require intervention."
        )

    if dashboard.intervention_rate > 10:

        observations.append(
            "Advisor workload is increasing."
        )

    for observation in observations:

        st.write(f"• {observation}")

    st.divider()

    st.markdown("## 🧠 Executive AI Advisor")

    for recommendation in recommendations:

        with st.container(border=True):

            left, right = st.columns(
                [2, 1],
            )

            with left:

                st.markdown(
                    f"### {recommendation.title}"
                )

                st.write(
                    recommendation.explanation
                )

                st.info(
                    recommendation.action
                )

            with right:

                st.metric(
                    "Priority",
                    recommendation.priority,
                )

                st.metric(
                    "Confidence",
                    f"{recommendation.confidence:.0%}",
                )

                st.metric(
                    "Business Impact",
                    recommendation.business_impact,
                )

                st.metric(
                    "Expected Benefit",
                    recommendation.expected_time,
                )

    st.divider()

    st.markdown("## Learner Analytics")

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
        attendance_chart,
        use_container_width=True,
    )

    st.plotly_chart(
        engagement_chart,
        use_container_width=True,
    )

    st.plotly_chart(
        segment_chart,
        use_container_width=True,
    )