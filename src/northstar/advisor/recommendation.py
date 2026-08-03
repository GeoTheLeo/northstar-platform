"""
Executive Recommendation domain model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Recommendation:
    """
    Represents a recommendation produced by the
    Executive AI Advisor.
    """

    priority: str

    title: str

    explanation: str

    action: str