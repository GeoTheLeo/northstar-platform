"""
Activity logging.
"""

from datetime import datetime

from northstar.activity.event import ActivityEvent


class ActivityLog:
    """
    Stores recent platform activity.
    """

    def __init__(
        self,
    ) -> None:

        self._events: list[ActivityEvent] = []

    def record(
        self,
        category: str,
        message: str,
    ) -> None:

        self._events.insert(
            0,
            ActivityEvent(
                timestamp=datetime.now(),
                category=category,
                message=message,
            ),
        )

        self._events = self._events[:50]

    def recent(
        self,
    ) -> list[ActivityEvent]:

        return self._events.copy()


activity_log = ActivityLog()