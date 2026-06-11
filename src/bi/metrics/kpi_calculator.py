import pandas as pd


def calculate_kpis(df: pd.DataFrame):

    total_students = len(df)

    average_attendance = round(
        df["attendance"].mean(),
        2,
    )

    average_engagement = round(
        df["engagement_score"].mean(),
        2,
    )

    average_assessment = round(
        df["assessment_score"].mean(),
        2,
    )

    return {
        "total_students": total_students,
        "average_attendance": average_attendance,
        "average_engagement": average_engagement,
        "average_assessment": average_assessment,
    }