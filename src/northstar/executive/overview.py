"""
Executive Overview workspace.
"""

import streamlit as st

from northstar.models.dashboard_data import DashboardData


def render_executive_overview(
    dashboard: DashboardData,
) -> None:
    """
    Render a concise executive summary.
    """

    st.subheader("🎯 Executive Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Retention",
        f"{dashboard.retention_rate:.1f}%",
    )

    col2.metric(
        "At-Risk Learners",
        dashboard.at_risk_learners,
    )

    col3.metric(
        "Active Recommendations",
        len(
            dashboard.recommendations,
        ),
    )

    st.divider()

    if dashboard.executive_insight is not None:

        st.info(
            f"""
### 🧠 Executive AI Insight

**{dashboard.executive_insight.headline}**

{dashboard.executive_insight.summary}

**Confidence:** {dashboard.executive_insight.confidence:.0%}
"""
        )

    st.divider()

    st.markdown(
        "### 🚀 Top Recommendations"
    )

    for recommendation in dashboard.recommendations[:3]:

        st.markdown(
            f"""
**{recommendation.priority}** — {recommendation.title}

{recommendation.action}
"""
        )