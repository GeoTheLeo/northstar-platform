"""
Executive Overview workspace.
"""

import streamlit as st

from northstar.models.dashboard_data import DashboardData


def render_executive_overview(
    dashboard: DashboardData,
) -> None:
    """
    Render the executive AI briefing.
    """

    if dashboard.executive_insight is not None:

        with st.container(
            border=True,
        ):

            st.markdown(
                "## 🧠 Executive AI Briefing"
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

    st.write("")

    st.markdown(
        "## 🚀 Priority Actions"
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

            left, right = st.columns(
                [1, 8],
            )

            with left:

                st.markdown(
                    f"# {icon}"
                )

            with right:

                st.markdown(
                    f"### {recommendation.title}"
                )

                st.caption(
                    recommendation.priority
                )

                st.write(
                    recommendation.rationale
                )

                st.markdown(
                    f"**Recommended Action**"
                )

                st.write(
                    recommendation.action
                )