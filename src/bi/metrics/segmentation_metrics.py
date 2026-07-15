import pandas as pd


def calculate_segmentation_metrics():

    segments = pd.read_csv(
        "src/segmentation/data/segment_assignments.csv"
    )

    total_segments = (
        segments["cluster"]
        .nunique()
    )

    largest_segment = (
        segments["cluster"]
        .value_counts()
        .idxmax()
    )

    largest_segment_size = (
        segments["cluster"]
        .value_counts()
        .max()
    )

    return {
        "total_segments": total_segments,
        "largest_segment": largest_segment,
        "largest_segment_size": largest_segment_size,
    }