"""
KPI Status model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class KPIStatus:
    """
    Represents the status of a KPI.
    """

    label: str

    score: float

    status: str

    trend: str