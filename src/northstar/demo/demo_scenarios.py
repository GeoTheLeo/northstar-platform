"""
Built-in executive demo scenarios.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DemoScenario:
    """
    Represents a demonstration scenario.
    """

    name: str

    attendance_delta: float

    engagement_delta: float

    assessment_delta: float


DEMO_SCENARIOS = [

    DemoScenario(
        "🎓 High Performing Institution",
        0.08,
        0.08,
        0.08,
    ),

    DemoScenario(
        "⚖️ Typical Institution",
        0.0,
        0.0,
        0.0,
    ),

    DemoScenario(
        "⚠️ At-Risk Institution",
        -0.10,
        -0.08,
        -0.08,
    ),

    DemoScenario(
        "🚨 Crisis Institution",
        -0.20,
        -0.18,
        -0.15,
    ),
]