"""
Platform context for the Executive Copilot.

Uses the same services as the Executive Dashboard so that
briefings reflect the current platform state.
"""

from northstar.controller import NorthStarController


def get_platform_context() -> str:
    """
    Build a live platform summary.
    """

    controller = NorthStarController()

    dashboard = controller.dashboard()

    largest_segment = dashboard.segment_metrics.get(
        "largest_segment",
        "N/A",
    )

    total_segments = dashboard.segment_metrics.get(
        "total_segments",
        0,
    )

    return f"""
NorthStar Live Platform Metrics

Retention Rate:
{dashboard.retention_rate:.1f}%

At-Risk Learners:
{dashboard.at_risk_learners}

Intervention Rate:
{dashboard.intervention_rate:.1f}%

Total Segments:
{total_segments}

Largest Segment:
{largest_segment}

Active Recommendations:
{len(dashboard.recommendations)}
"""