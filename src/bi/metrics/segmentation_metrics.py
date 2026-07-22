"""
Segmentation Metrics

Calculates learner segmentation statistics from an in-memory DataFrame.
"""

import pandas as pd


def calculate_segmentation_metrics(
    segments: pd.DataFrame,
) -> dict:
    """
    Calculate summary statistics for learner segmentation.
    """

    cluster_counts = segments["cluster"].value_counts()

    return {
        "total_segments": segments["cluster"].nunique(),
        "largest_segment": cluster_counts.idxmax(),
        "largest_segment_size": cluster_counts.max(),
    }