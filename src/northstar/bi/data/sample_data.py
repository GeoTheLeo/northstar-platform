"""
NorthStar Sample Data Loader.
"""

from pandas import DataFrame
import pandas as pd


def load_dashboard_data() -> DataFrame:
    """
    Load the learner dashboard dataset.
    """

    return pd.read_csv("data/raw/student_data.csv")