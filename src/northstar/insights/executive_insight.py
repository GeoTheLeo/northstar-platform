"""
Executive Insight domain model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ExecutiveInsight:
    """
    AI-generated executive insight.
    """

    headline: str

    summary: str

    confidence: float