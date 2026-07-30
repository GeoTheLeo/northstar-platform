"""
Risk Metrics.

Calculates learner risk statistics.
"""

from typing import TypedDict

import pandas as pd


class RiskMetrics(TypedDict):
    """
    Summary metrics describing learner risk.
    """

    total_students: int
    at_risk_students: int
    risk_percentage: float


def calculate_risk_metrics(
    predictions: pd.DataFrame,
) -> RiskMetrics:
    """
    Calculate dashboard risk metrics.
    """

    total_students = len(predictions)

    at_risk_students = int(
        (predictions["risk_prediction"] == 1).sum()
    )

    risk_percentage = (
        round(
            at_risk_students / total_students * 100,
            1,
        )
        if total_students > 0
        else 0.0
    )

    return RiskMetrics(
        total_students=total_students,
        at_risk_students=at_risk_students,
        risk_percentage=risk_percentage,
    )