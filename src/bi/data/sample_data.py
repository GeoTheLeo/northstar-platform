import pandas as pd


def load_dashboard_data():

    return pd.read_csv(
        "data/raw/student_data.csv"
    )