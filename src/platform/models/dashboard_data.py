"""
Dashboard Domain Model

Defines the application data returned by the
DashboardService and consumed by the UI layer.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class DashboardData:
    """
    Aggregated dashboard information.

    The UI should depend only on this object,
    not on dictionaries or storage details.
    """

    learner_df: pd.DataFrame
    segments_df: pd.DataFrame

    kpis: dict
    risk_metrics: dict
    segment_metrics: dict