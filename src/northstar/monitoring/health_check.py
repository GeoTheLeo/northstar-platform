"""
NorthStar Platform Health Check Model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class HealthCheck:
    """
    Represents the health of a single platform component.
    """

    component: str

    healthy: bool

    message: str