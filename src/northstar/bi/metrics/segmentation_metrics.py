"""
Segmentation Metrics.

Calculates learner segmentation statistics.
"""

from typing import TypedDict

import pandas as pd


class SegmentationMetrics(TypedDict):
    """
    Summary metrics describing learner segmentation.
    """

    total_segments: int
    largest_segment: int
    largest_segment_size: int


def calculate_segmentation_metrics(
    segments: pd.DataFrame,
) -> SegmentationMetrics:
    """
    Calculate summary statistics for learner segmentation.
    """

    cluster_counts = segments["cluster"].value_counts()

    return SegmentationMetrics(
        total_segments=int(segments["cluster"].nunique()),
        largest_segment=int(cluster_counts.idxmax()),
        largest_segment_size=int(cluster_counts.max()),
    )