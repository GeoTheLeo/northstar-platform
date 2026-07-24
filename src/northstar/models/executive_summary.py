"""
Executive Summary Domain Model
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveSummary:
    """
    Executive AI summary presented to leadership.
    """

    headline: str

    recommendation: str

    severity: str