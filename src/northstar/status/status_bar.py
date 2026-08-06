"""
Global Executive Status Bar.
"""

from datetime import datetime

import streamlit as st


VERSION = "NorthStar v1.0"


def render_status_bar() -> None:
    """
    Render the global platform status bar.
    """

    platform_col, ai_col, model_col, refresh_col, version_col = st.columns(5)

    platform_col.metric(
        "Platform",
        "🟢 Healthy",
    )

    ai_col.metric(
        "AI Services",
        "🟢 Online",
    )

    model_col.metric(
        "Models",
        "2 Loaded",
    )

    refresh_col.metric(
        "Last Refresh",
        datetime.now().strftime("%H:%M"),
    )

    version_col.metric(
        "Version",
        VERSION,
    )

    st.divider()