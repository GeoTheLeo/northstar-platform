"""
Reusable Feature Engineering
"""

import pandas as pd


def build_engagement_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    engineered = df.copy()

    engineered["attendance_ratio"] = (
        engineered["attendance"] / 100
    )

    engineered["engagement_gap"] = (
        engineered["engagement_score"]
        - engineered["assessment_score"]
    )

    engineered["performance_index"] = (
        engineered["attendance"]
        + engineered["assessment_score"]
        + engineered["engagement_score"]
    ) / 3

    return engineered