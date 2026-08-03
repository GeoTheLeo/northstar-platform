"""
Business rules used by the Executive AI Advisor.
"""

from northstar.advisor.recommendation import Recommendation
from northstar.models.dashboard_data import DashboardData


def generate_recommendations(
    dashboard: DashboardData,
) -> list[Recommendation]:
    """
    Generate executive recommendations.
    """

    recommendations: list[Recommendation] = []

    if dashboard.retention_rate < 85:

        recommendations.append(
            Recommendation(
                priority="High",
                title="Retention Below Target",
                explanation=(
                    "Institutional retention has fallen below "
                    "the desired operating threshold."
                ),
                action=(
                    "Increase learner intervention efforts and "
                    "advisor outreach."
                ),
            )
        )

    if dashboard.at_risk_learners > 10:

        recommendations.append(
            Recommendation(
                priority="High",
                title="Elevated Learner Risk",
                explanation=(
                    "A significant number of learners are "
                    "currently predicted to be at risk."
                ),
                action=(
                    "Review Early Warning predictions and "
                    "prioritize coaching resources."
                ),
            )
        )

    if dashboard.intervention_rate > 10:

        recommendations.append(
            Recommendation(
                priority="Medium",
                title="Intervention Demand Increasing",
                explanation=(
                    "The current intervention workload "
                    "continues to grow."
                ),
                action=(
                    "Review staffing capacity and automate "
                    "routine learner follow-ups."
                ),
            )
        )

    if not recommendations:

        recommendations.append(
            Recommendation(
                priority="Low",
                title="Platform Is Performing Well",
                explanation=(
                    "Current KPIs remain within expected "
                    "operational thresholds."
                ),
                action=(
                    "Continue monitoring all key performance "
                    "indicators."
                ),
            )
        )

    return recommendations