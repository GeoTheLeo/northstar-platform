"""
Feature engineering for learner segmentation.
"""

import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features used by the clustering model.

    Parameters
    ----------
    df:
        Input learner DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame containing engineered features.
    """

    engineered = df.copy()

    engineered["attendance_ratio"] = (
        engineered["attendance"] / engineered["attendance"].max()
    )

    engineered["engagement_ratio"] = (
        engineered["engagement_score"]
        / engineered["engagement_score"].max()
    )

    engineered["assessment_ratio"] = (
        engineered["assessment_score"]
        / engineered["assessment_score"].max()
    )

    return engineered