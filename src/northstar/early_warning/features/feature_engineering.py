import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering for Early Warning System.
    """

    engineered = df.copy()

    # Fixed denominator, not a per-batch max: predict()/assign_cluster() build a
    # single-row DataFrame, where a batch max is just that row's own value and
    # every ratio would collapse to 1.0. Scores are 0-100, so 100 is the max.
    max_score = 100.0

    engineered["attendance_ratio"] = engineered["attendance"] / max_score

    engineered["engagement_ratio"] = engineered["engagement_score"] / max_score

    engineered["assessment_ratio"] = engineered["assessment_score"] / max_score

    return engineered
