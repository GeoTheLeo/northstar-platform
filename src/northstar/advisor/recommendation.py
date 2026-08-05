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

    rationale: str

    action: str