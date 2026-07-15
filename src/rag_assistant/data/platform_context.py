import pandas as pd

from bi.metrics.risk_metrics import (
    calculate_risk_metrics,
)

from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)


def get_platform_context():

    risk = calculate_risk_metrics()

    segments = (
        calculate_segmentation_metrics()
    )

    return f"""
NorthStar Live Platform Metrics

At-Risk Learners:
{risk["at_risk_students"]}

Risk Percentage:
{risk["risk_percentage"]}%

Active Segments:
{segments["total_segments"]}

Largest Segment:
{segments["largest_segment"]}
"""