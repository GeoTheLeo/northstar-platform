import pandas as pd


def calculate_risk_metrics():

    predictions = pd.read_csv(
        "src/early_warning/data/predictions.csv"
    )

    total_students = len(predictions)

    at_risk_students = (
        predictions["risk_prediction"] == 1
    ).sum()

    risk_percentage = round(
        (at_risk_students / total_students) * 100,
        1,
    )

    return {
        "total_students": total_students,
        "at_risk_students": at_risk_students,
        "risk_percentage": risk_percentage,
    }