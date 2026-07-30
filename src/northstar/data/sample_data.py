"""
NorthStar Sample Data Loader.
"""

import pandas as pd
from pandas import DataFrame


def load_dashboard_data() -> DataFrame:
    """
    Load the learner dashboard dataset.
    """

    return pd.read_csv("data/raw/student_data.csv")
