"""
Activity event model.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ActivityEvent:
    """
    Represents a platform activity.
    """

    timestamp: datetime

    category: str

    message: str