"""
NorthStar AI Insights Workspace.

Provides executive AI analysis generated from
NorthStar platform intelligence.
"""

import streamlit as st

from northstar.models.dashboard_data import DashboardData


def render_ai_insights(
    dashboard: DashboardData,
) -> None:
    """
    Render the AI Insights workspace.
    """

    st.header("🧠 AI Insights")

    st.markdown(
        """
AI-generated institutional intelligence derived from
predictive analytics, behavioral segmentation and
executive decision support models.
"""
    )

    st.write("")

    # --------------------------------------------------
    # Executive AI Analysis
    # --------------------------------------------------

    if dashboard.executive_insight is not None:

        with st.container(
            border=True,
        ):

            st.subheader(
                "Executive AI Analysis"
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
    # AI Findings
    # --------------------------------------------------

    left, right = st.columns(
        2,
        gap="large",
    )

    with left:

        with st.container(
            border=True,
        ):

            st.subheader(
                "🎯 Predictive Risk"
            )

            st.metric(
                "Retention Rate",
                f"{dashboard.retention_rate:.1f}%",
                border=True,
            )

            st.metric(
                "At-Risk Learners",
                dashboard.at_risk_learners,
                border=True,
            )

    with right:

        with st.container(
            border=True,
        ):

            st.subheader(
                "👥 Behavioral Segmentation"
            )

            st.metric(
                "Active Segments",
                dashboard.segment_metrics.get(
                    "total_segments",
                    0,
                ),
                border=True,
            )

            st.metric(
                "Recommendations",
                len(
                    dashboard.recommendations,
                ),
                border=True,
            )

    st.divider()

    # --------------------------------------------------
    # Strategic Recommendations
    # --------------------------------------------------

    st.subheader(
        "🚀 Strategic Recommendations"
    )

    priority_icons = {
        "HIGH": "🔴",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }

    for recommendation in dashboard.recommendations:

        icon = priority_icons.get(
            recommendation.priority,
            "⚪",
        )

        with st.container(
            border=True,
        ):

            st.markdown(
                f"## {icon} {recommendation.title}"
            )

            st.write(
                recommendation.rationale
            )

            st.markdown(
                "**Recommended Action**"
            )

            st.write(
                recommendation.action
            )