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
    Render the Executive Scenario Simulator.
    """

    st.header(
        "🎮 Executive Scenario Simulator"
    )

    st.markdown(
        """
Model the impact of strategic interventions before
implementation. Adjust key institutional variables and
evaluate the projected effect on learner retention and
risk.
"""
    )

    st.divider()

    # --------------------------------------------------
    # Scenario Controls
    # --------------------------------------------------

    left, right = st.columns(
        [3, 2],
        gap="large",
    )

    with left:

        st.subheader(
            "Scenario Inputs"
        )

        attendance = st.slider(
            "Attendance Change (%)",
            -30,
            30,
            0,
            help="Simulate improvements or declines in learner attendance.",
        )

        engagement = st.slider(
            "Engagement Change (%)",
            -30,
            30,
            0,
            help="Adjust overall learner engagement.",
        )

        assessment = st.slider(
            "Assessment Change (%)",
            -30,
            30,
            0,
            help="Model changes in assessment performance.",
        )

        run = st.button(
            "🚀 Run Executive Simulation",
            use_container_width=True,
        )

    with right:

        st.subheader(
            "Simulation Overview"
        )

        st.metric(
            "Current Retention",
            f"{dashboard.retention_rate:.1f}%",
            border=True,
        )

        st.metric(
            "Current At-Risk",
            dashboard.at_risk_learners,
            border=True,
        )

        st.info(
            """
The simulator projects how operational
changes may influence institutional
performance before implementation.
"""
        )

    if not run:
        return

    # --------------------------------------------------
    # Execute Simulation
    # --------------------------------------------------

    with st.spinner(
        "Running executive simulation..."
    ):

        simulator = ScenarioSimulator()

        simulated_dashboard = simulator.analyse(
            dashboard.learner_df,
            Scenario(
                attendance_delta=attendance / 100,
                engagement_delta=engagement / 100,
                assessment_delta=assessment / 100,
            ),
        )

    st.success(
        "Simulation completed successfully."
    )

    st.divider()

    # --------------------------------------------------
    # Before vs After
    # --------------------------------------------------

    st.subheader(
        "📈 Projected Institutional Impact"
    )

    before, after = st.columns(
        2,
        gap="large",
    )

    with before:

        with st.container(border=True):

            st.markdown(
                "### Current State"
            )

            st.metric(
                "Retention",
                f"{dashboard.retention_rate:.1f}%",
            )

            st.metric(
                "At-Risk Learners",
                dashboard.at_risk_learners,
            )

    with after:

        with st.container(border=True):

            st.markdown(
                "### Simulated Outcome"
            )

            st.metric(
                "Retention",
                f"{simulated_dashboard.retention_rate:.1f}%",
                delta=(
                    f"{simulated_dashboard.retention_rate - dashboard.retention_rate:+.1f}%"
                ),
            )

            st.metric(
                "At-Risk Learners",
                simulated_dashboard.at_risk_learners,
                delta=(
                    simulated_dashboard.at_risk_learners
                    - dashboard.at_risk_learners
                ),
            )

    st.divider()

    # --------------------------------------------------
    # Executive Assessment
    # --------------------------------------------------

    if simulated_dashboard.executive_insight:

        insight = simulated_dashboard.executive_insight

        with st.container(border=True):

            st.subheader(
                "🧠 Executive Assessment"
            )

            st.markdown(
                f"### {insight.headline}"
            )

            st.write(
                insight.summary
            )

            st.progress(
                insight.confidence
            )

            st.caption(
                f"Confidence Score: "
                f"{insight.confidence:.0%}"
            )

    st.divider()

    # --------------------------------------------------
    # Recommended Actions
    # --------------------------------------------------

    st.subheader(
        "🚀 Recommended Actions"
    )

    priority_icons = {
        "HIGH": "🔴",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }

    for recommendation in simulated_dashboard.recommendations[:3]:

        icon = priority_icons.get(
            recommendation.priority,
            "⚪",
        )

        with st.container(border=True):

            st.markdown(
                f"### {icon} {recommendation.title}"
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