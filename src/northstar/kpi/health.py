"""
Platform KPI calculations.
"""

from northstar.kpi.status import KPIStatus
from northstar.models.dashboard_data import DashboardData


def _status(
    value: float,
) -> tuple[str, str]:
    """
    Convert a KPI value into
    status and trend.
    """

    if value >= 90:

        return (
            "Excellent",
            "▲",
        )

    if value >= 80:

        return (
            "Healthy",
            "►",
        )

    if value >= 70:

        return (
            "Warning",
            "▼",
        )

    return (
        "Critical",
        "▼",
    )


def calculate_platform_health(
    dashboard: DashboardData,
) -> list[KPIStatus]:
    """
    Calculate executive KPI health.
    """

    retention = dashboard.retention_rate

    intervention = (
        100
        - dashboard.intervention_rate
    )

    risk = (
        100
        - dashboard.churn_rate
    )

    statuses: list[KPIStatus] = []

    for label, value in [

        (
            "Retention",
            retention,
        ),

        (
            "Risk",
            risk,
        ),

        (
            "Intervention",
            intervention,
        ),

    ]:

        state, trend = _status(
            value,
        )

        statuses.append(

            KPIStatus(

                label=label,

                score=round(
                    value,
                    1,
                ),

                status=state,

                trend=trend,

            )

        )

    return statuses