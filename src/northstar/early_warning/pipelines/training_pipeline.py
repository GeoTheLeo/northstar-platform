"""
Early Warning training pipeline.
"""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from northstar.early_warning.models.train_model import (
    train_model,
)

DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "raw"
    / "student_data.csv"
)


def run_pipeline() -> RandomForestClassifier:
    """
    Execute the Early Warning training pipeline.
    """

    df = pd.read_csv(DATA_PATH)

    return train_model(df)


if __name__ == "__main__":
    run_pipeline()
