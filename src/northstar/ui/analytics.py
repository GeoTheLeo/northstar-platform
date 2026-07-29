"""
NorthStar Analytics View
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


def render_analytics(
    dashboard: DashboardData,
) -> None:
    """
    Render the Executive Analytics workspace.
    """

    st.subheader("📊 Analytics Command Center")

    # --------------------------------------------------
    # Executive Intelligence
    # --------------------------------------------------

    st.markdown("### Executive Intelligence")

    summary = dashboard.executive_summary

    if summary.severity == "success":
        st.success(summary.headline)

    elif summary.severity == "warning":
        st.warning(summary.headline)

    else:
        st.error(summary.headline)

    st.write(summary.recommendation)

    observations = []

    if dashboard.retention_rate >= 90:
        observations.append("✅ Retention is currently exceeding target.")
    else:
        observations.append("⚠ Retention has fallen below the desired target.")

    if dashboard.at_risk_learners > 0:
        observations.append(
            f"⚠ {dashboard.at_risk_learners:,} learners "
            "are currently identified as at risk."
        )

    if dashboard.intervention_rate > 0:
        observations.append(f"📈 Intervention rate: {dashboard.intervention_rate:.1f}%")

    st.markdown("#### Key Business Observations")

    for observation in observations:
        st.write(observation)

    st.markdown("#### Recommended Next Action")

    if dashboard.retention_rate >= 90:
        st.success(
            "Maintain current learner engagement "
            "strategies while monitoring early "
            "warning indicators."
        )
    elif dashboard.retention_rate >= 80:
        st.warning("Increase proactive coaching for medium-risk learner segments.")
    else:
        st.error(
            "Prioritize immediate intervention "
            "for high-risk learners and review "
            "engagement strategy."
        )

    st.divider()

    # --------------------------------------------------
    # Visual Analytics
    # --------------------------------------------------

    attendance_chart = px.histogram(
        dashboard.learner_df,
        x="attendance",
        title="Attendance Distribution",
    )

    attendance_chart.update_layout(height=SMALL_CHART_HEIGHT)

    engagement_chart = px.scatter(
        dashboard.learner_df,
        x="engagement_score",
        y="assessment_score",
        title="Engagement vs Assessment",
    )

    engagement_chart.update_layout(height=LARGE_CHART_HEIGHT)

    segment_chart = px.histogram(
        dashboard.segments_df,
        x="cluster",
        title="Learner Segment Distribution",
    )

    segment_chart.update_layout(height=LARGE_CHART_HEIGHT)

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
