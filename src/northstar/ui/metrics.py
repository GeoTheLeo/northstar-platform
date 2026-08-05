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

    st.subheader("📈 Executive KPI Command Center")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Retention",
        f"{dashboard.retention_rate:.1f}%",
    )

    col2.metric(
        "Churn",
        f"{dashboard.churn_rate:.1f}%",
    )

    col3.metric(
        "Intervention",
        f"{dashboard.intervention_rate:.1f}%",
    )

    st.divider()

    st.markdown("### Platform Health")

    statuses = calculate_platform_health(
        dashboard,
    )

    columns = st.columns(
        len(statuses),
    )

    total_score = 0.0

    for column, status in zip(
        columns,
        statuses,
    ):

        total_score += status.score

        with column:

            st.metric(
                status.label,
                f"{status.score:.1f}%",
                status.trend,
            )

            st.write(
                f"{_status_icon(status.status)} "
                f"{status.status}"
            )

    st.divider()

    platform_score = round(
        total_score / len(statuses),
        1,
    )

    if platform_score >= 90:

        st.success(
            f"Overall Platform Health: {platform_score:.1f}%"
        )

    elif platform_score >= 80:

        st.warning(
            f"Overall Platform Health: {platform_score:.1f}%"
        )

    else:

        st.error(
            f"Overall Platform Health: {platform_score:.1f}%"
        )