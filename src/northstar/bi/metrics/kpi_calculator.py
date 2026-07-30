"""
Business Intelligence KPI calculations.
"""

from typing import TypedDict

import pandas as pd


class KPIResults(TypedDict):
    """
    Business Intelligence KPI summary.
    """

    total_students: int
    average_attendance: float
    average_engagement: float
    average_assessment: float


def calculate_kpis(df: pd.DataFrame) -> KPIResults:
    """
    Calculate executive dashboard KPIs.
    """

    total_students = len(df)

    average_attendance = round(
        float(df["attendance"].mean()),
        2,
    )

    average_engagement = round(
        float(df["engagement_score"].mean()),
        2,
    )

    average_assessment = round(
        float(df["assessment_score"].mean()),
        2,
    )

    return {
        "total_students": total_students,
        "average_attendance": average_attendance,
        "average_engagement": average_engagement,
        "average_assessment": average_assessment,
    }
