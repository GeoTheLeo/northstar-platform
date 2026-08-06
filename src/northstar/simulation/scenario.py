"""
Scenario configuration.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Scenario:
    """
    Executive simulation scenario.
    """

    attendance_delta: float

    engagement_delta: float

    assessment_delta: float