"""
Scenario Simulator.
"""

import pandas as pd

from northstar.analysis import DashboardAnalysisService
from northstar.models.dashboard_data import DashboardData
from northstar.simulation.scenario import Scenario


class ScenarioSimulator:
    """
    Executive scenario simulator.
    """

    def __init__(
        self,
    ) -> None:

        self.analysis = (
            DashboardAnalysisService()
        )

    def apply(
        self,
        learner_df: pd.DataFrame,
        scenario: Scenario,
    ) -> pd.DataFrame:
        """
        Apply a scenario.
        """

        simulated = learner_df.copy()

        simulated["attendance"] *= (
            1.0
            + scenario.attendance_delta
        )

        simulated["engagement_score"] *= (
            1.0
            + scenario.engagement_delta
        )

        simulated["assessment_score"] *= (
            1.0
            + scenario.assessment_delta
        )

        return simulated

    def analyse(
        self,
        learner_df: pd.DataFrame,
        scenario: Scenario,
    ) -> DashboardData:
        """
        Analyse simulated data.
        """

        simulated = self.apply(
            learner_df,
            scenario,
        )

        return self.analysis.analyse(
            simulated,
        )