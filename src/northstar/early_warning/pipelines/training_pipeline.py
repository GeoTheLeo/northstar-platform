"""
Early Warning training pipeline.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from northstar.core.paths import STUDENT_DATA_PATH
from northstar.early_warning.models.train_model import (
    train_model,
)


def run_pipeline() -> RandomForestClassifier:
    """
    Execute the Early Warning training pipeline.
    """

    df = pd.read_csv(STUDENT_DATA_PATH)

    return train_model(df)


if __name__ == "__main__":
    run_pipeline()
