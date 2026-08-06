"""
Executive Demo Mode.
"""

import streamlit as st

from northstar.demo.demo_scenarios import (
    DEMO_SCENARIOS,
    DemoScenario,
)


def render_demo_selector() -> DemoScenario:
    """
    Render the executive demo selector.
    """

    names = [
        scenario.name
        for scenario in DEMO_SCENARIOS
    ]

    index = names.index(
        "⚖️ Typical Institution"
    )

    selected = st.sidebar.selectbox(
        "Executive Demo",
        names,
        index=index,
    )

    for scenario in DEMO_SCENARIOS:

        if scenario.name == selected:
            return scenario

    return DEMO_SCENARIOS[index]