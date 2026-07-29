import pandas as pd


def create_features(df: pd.DataFrame):

    engineered = df.copy()

    engineered["attendance_ratio"] = (
        engineered["attendance"] / engineered["attendance"].max()
    )

    engineered["engagement_ratio"] = (
        engineered["engagement_score"] / engineered["engagement_score"].max()
    )

    engineered["assessment_ratio"] = (
        engineered["assessment_score"] / engineered["assessment_score"].max()
    )

    return engineered
