import pandas as pd

from early_warning.models.train_model import (
    train_model,
)


def run_pipeline():

    df = pd.read_csv(
        "data/raw/student_data.csv"
    )

    model = train_model(df)

    return model


if __name__ == "__main__":
    run_pipeline()