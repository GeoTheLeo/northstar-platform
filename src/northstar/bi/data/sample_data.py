"""
Sample data loader.
"""

import pandas as pd
from pandas import DataFrame

from northstar.core.paths import STUDENT_DATA_PATH


def load_dashboard_data() -> DataFrame:
    """
    Load the dashboard dataset.
    """

    return pd.read_csv(STUDENT_DATA_PATH)