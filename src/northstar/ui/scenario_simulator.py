"""
Executive Scenario Simulator.
"""

import streamlit as st

from northstar.models.dashboard_data import DashboardData
from northstar.simulation import (
    Scenario,
    ScenarioSimulator,
)


def render_scenario_simulator(
    dashboard: DashboardData,
) -> None:
    """
    Render executive simulator.
    """

    st.header(
        "🎮 Executive Scenario Simulator"
    )

    attendance = st.slider(
        "Attendance Change (%)",
        -30,
        30,
        0,
    )

    engagement = st.slider(
        "Engagement Change (%)",
        -30,
        30,
        0,
    )

    assessment = st.slider(
        "Assessment Change (%)",
        -30,
        30,
        0,
    )

    if not st.button(
        "Run Simulation",
    ):
        return

    simulator = ScenarioSimulator()

    simulated_dashboard = simulator.analyse(
        dashboard.learner_df,
        Scenario(
            attendance_delta=attendance / 100,
            engagement_delta=engagement / 100,
            assessment_delta=assessment / 100,
        ),
    )

    st.subheader(
        "Executive Impact"
    )

    before, after = st.columns(2)

    with before:

        st.metric(
            "Retention",
            f"{dashboard.retention_rate:.1f}%",
        )

        st.metric(
            "At-Risk Learners",
            dashboard.at_risk_learners,
        )

    with after:

        st.metric(
            "Retention",
            f"{simulated_dashboard.retention_rate:.1f}%",
        )

        st.metric(
            "At-Risk Learners",
            simulated_dashboard.at_risk_learners,
        )

    st.divider()

    if simulated_dashboard.executive_insight:

        insight = simulated_dashboard.executive_insight

        st.info(
            f"""
### Executive Assessment

**{insight.headline}**

{insight.summary}

Confidence:
{insight.confidence:.0%}
"""
        )

    st.divider()

    st.markdown(
        "### Top Recommendations"
    )

    for recommendation in simulated_dashboard.recommendations[:3]:

        st.markdown(
            f"""
**{recommendation.priority}**

{recommendation.title}

{recommendation.action}
"""
        )