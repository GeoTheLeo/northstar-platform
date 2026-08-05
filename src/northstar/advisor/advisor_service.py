"""
Executive Advisor.

Generates business recommendations from
dashboard intelligence.
"""

from northstar.advisor.recommendation import Recommendation
from northstar.models.dashboard_data import DashboardData


class ExecutiveAdvisor:
    """
    AI-inspired recommendation engine.
    """

    def advise(
        self,
        dashboard: DashboardData,
    ) -> list[Recommendation]:
        """
        Produce executive recommendations.
        """

        recommendations: list[Recommendation] = []

        # --------------------------------------------------
        # Retention
        # --------------------------------------------------

        if dashboard.retention_rate < 80:

            recommendations.append(
                Recommendation(
                    priority="HIGH",
                    title="Critical Retention Risk",
                    rationale=(
                        f"Retention has fallen to "
                        f"{dashboard.retention_rate:.1f}%."
                    ),
                    action=(
                        "Launch immediate intervention "
                        "campaign for high-risk learners."
                    ),
                )
            )

        elif dashboard.retention_rate < 90:

            recommendations.append(
                Recommendation(
                    priority="MEDIUM",
                    title="Retention Monitoring",
                    rationale=(
                        f"Retention is "
                        f"{dashboard.retention_rate:.1f}%."
                    ),
                    action=(
                        "Increase proactive coaching "
                        "for medium-risk cohorts."
                    ),
                )
            )

        else:

            recommendations.append(
                Recommendation(
                    priority="LOW",
                    title="Retention Performing Well",
                    rationale=(
                        f"Retention is "
                        f"{dashboard.retention_rate:.1f}%."
                    ),
                    action=(
                        "Maintain current learner "
                        "engagement strategy."
                    ),
                )
            )

        # --------------------------------------------------
        # Early Warning
        # --------------------------------------------------

        if dashboard.at_risk_learners > 0:

            recommendations.append(
                Recommendation(
                    priority="HIGH",
                    title="Early Warning Alert",
                    rationale=(
                        f"{dashboard.at_risk_learners} learners "
                        "have been identified as at risk."
                    ),
                    action=(
                        "Schedule advisor outreach within "
                        "the next 48 hours."
                    ),
                )
            )

        # --------------------------------------------------
        # Segmentation
        # --------------------------------------------------

        recommendations.append(
            Recommendation(
                priority="MEDIUM",
                title="Review Learner Segments",
                rationale=(
                    "Behavioral segmentation has been updated."
                ),
                action=(
                    "Evaluate intervention strategies "
                    "for each learner cluster."
                ),
            )
        )

        return recommendations