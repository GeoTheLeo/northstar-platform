"""
Executive Workspace Navigation.
"""

import streamlit as st


WORKSPACES = [
    "🏠 Executive Dashboard",
    "📊 Analytics",
    "🧠 AI Insights",
    "🎮 Scenario Simulator",
    "🤖 Executive Copilot",
    "💬 Knowledge Assistant",
    "📦 Model Registry",
    "🖥 Platform Health",
    "📈 Activity Timeline",
]


def render_workspace_selector() -> str:
    """
    Render the sidebar workspace selector.
    """

    st.sidebar.title(
        "NorthStar"
    )

    st.sidebar.caption(
        "Executive Navigation"
    )

    return st.sidebar.radio(
        "Workspace",
        WORKSPACES,
    )