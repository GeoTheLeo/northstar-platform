"""
NorthStar Executive Metrics View.
"""

import streamlit as st

from northstar.kpi import calculate_platform_health
from northstar.models.dashboard_data import DashboardData


def _status_icon(status: str) -> str:
    """
    Return an icon representing KPI health.
    """

    return {
        "Excellent": "🟢",
        "Healthy": "🟢",
        "Warning": "🟡",
        "Critical": "🔴",
    }.get(status, "⚪")


def render_metrics(
    dashboard: DashboardData,
) -> None:
    """
    Render executive KPI metrics.
    """

    # --------------------------------------------------
    # Executive KPI Command Center
    # --------------------------------------------------

    retention_col, churn_col, intervention_col = st.columns(
        3,
        gap="large",
    )

    with retention_col:

        st.metric(
            label="🎯 Retention Rate",
            value=f"{dashboard.retention_rate:.1f}%",
            delta="Target 90%",
            border=True,
        )

    with churn_col:

        st.metric(
            label="📉 Churn Rate",
            value=f"{dashboard.churn_rate:.1f}%",
            delta="Lower is better",
            border=True,
        )

    with intervention_col:

        st.metric(
            label="🚀 Intervention Rate",
            value=f"{dashboard.intervention_rate:.1f}%",
            delta="Learner Success",
            border=True,
        )

    st.write("")

    # --------------------------------------------------
    # Platform Health
    # --------------------------------------------------

    st.subheader("🖥 Platform Health Overview")

    statuses = calculate_platform_health(
        dashboard,
    )

    columns = st.columns(
        len(statuses),
        gap="large",
    )

    total_score = 0.0

    for column, status in zip(
        columns,
        statuses,
    ):

        total_score += status.score

        with column:

            st.metric(
                label=status.label,
                value=f"{status.score:.1f}%",
                delta=status.trend,
                border=True,
            )

            st.caption(
                f"{_status_icon(status.status)} "
                f"{status.status}"
            )

    st.write("")

    # --------------------------------------------------
    # Overall Platform Score
    # --------------------------------------------------

    platform_score = round(
        total_score / len(statuses),
        1,
    )

    if platform_score >= 90:

        st.success(
            f"🟢 Overall Platform Health: {platform_score:.1f}%"
        )

    elif platform_score >= 80:

        st.warning(
            f"🟡 Overall Platform Health: {platform_score:.1f}%"
        )

    else:

        st.error(
            f"🔴 Overall Platform Health: {platform_score:.1f}%"
        )