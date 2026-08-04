"""
Business recommendation rules.
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
                    "Institutional retention is below the target threshold."
                ),
                action=(
                    "Increase learner intervention efforts."
                ),
                confidence=0.97,
                business_impact="Very High",
                expected_time="2-4 Weeks",
            )
        )

    if dashboard.at_risk_learners > 10:

        recommendations.append(
            Recommendation(
                priority="High",
                title="High Learner Risk",
                explanation=(
                    "Multiple learners require immediate support."
                ),
                action=(
                    "Prioritize advisor outreach."
                ),
                confidence=0.94,
                business_impact="High",
                expected_time="1-2 Weeks",
            )
        )

    if dashboard.intervention_rate > 10:

        recommendations.append(
            Recommendation(
                priority="Medium",
                title="Growing Intervention Demand",
                explanation=(
                    "Support workload is increasing."
                ),
                action=(
                    "Review staffing and automation opportunities."
                ),
                confidence=0.90,
                business_impact="Medium",
                expected_time="3-6 Weeks",
            )
        )

    if not recommendations:

        recommendations.append(
            Recommendation(
                priority="Low",
                title="Platform Healthy",
                explanation=(
                    "Current KPIs remain within expected limits."
                ),
                action=(
                    "Continue monitoring."
                ),
                confidence=0.99,
                business_impact="Low",
                expected_time="Continuous",
            )
        )

    return recommendations