"""
Recommendation domain model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Recommendation:
    """
    Represents an executive recommendation.
    """

    priority: str

    title: str

    explanation: str

    action: str

    confidence: float

    business_impact: str

    expected_time: str