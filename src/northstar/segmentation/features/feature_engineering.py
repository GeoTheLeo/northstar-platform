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

    # Fixed denominator, not a per-batch max: assign_cluster() builds a
    # single-row DataFrame, where a batch max is just that row's own value and
    # every ratio would collapse to 1.0. Scores are 0-100, so 100 is the max.
    max_score = 100.0

    engineered["attendance_ratio"] = engineered["attendance"] / max_score

    engineered["engagement_ratio"] = engineered["engagement_score"] / max_score

    engineered["assessment_ratio"] = engineered["assessment_score"] / max_score

    return engineered