"""
Dashboard Service.

Loads learner data and delegates analysis.
"""

import pandas as pd

from northstar.analysis import DashboardAnalysisService
from northstar.demo.demo_scenarios import DemoScenario
from northstar.logging import logger
from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)
from northstar.simulation import (
    Scenario,
    ScenarioSimulator,
)


class DashboardService:
    """
    Coordinates dashboard generation.
    """

    def __init__(
        self,
        repository: CsvDashboardRepository | None = None,
        analysis: DashboardAnalysisService | None = None,
    ) -> None:

        self.repository = (
            repository
            if repository is not None
            else CsvDashboardRepository()
        )

        self.analysis = (
            analysis
            if analysis is not None
            else DashboardAnalysisService()
        )

        self.simulator = (
            ScenarioSimulator()
        )

    def load_dashboard(
        self,
        demo: DemoScenario | None = None,
    ) -> DashboardData:
        """
        Load dashboard.
        """

        logger.info(
            "Loading dashboard."
        )

        learner_df = (
            self.repository.load_dashboard_data()
        )

        if demo is not None:

            learner_df = self.simulator.apply(
                learner_df,
                Scenario(
                    attendance_delta=demo.attendance_delta,
                    engagement_delta=demo.engagement_delta,
                    assessment_delta=demo.assessment_delta,
                ),
            )

        return self.analysis.analyse(
            learner_df,
        )