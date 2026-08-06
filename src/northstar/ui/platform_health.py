"""
NorthStar Platform Health View.
"""

import streamlit as st

from northstar.monitoring import PlatformMonitor


def render_platform_health() -> None:
    """
    Render platform operational status.
    """

    monitor = PlatformMonitor()

    checks = monitor.run()

    st.subheader(
        "🖥️ Platform Health"
    )

    healthy = sum(
        check.healthy
        for check in checks
    )

    score = round(
        healthy
        / len(checks)
        * 100,
        1,
    )

    if score == 100:

        st.success(
            f"Overall Platform Health: {score:.0f}%"
        )

    elif score >= 80:

        st.warning(
            f"Overall Platform Health: {score:.0f}%"
        )

    else:

        st.error(
            f"Overall Platform Health: {score:.0f}%"
        )

    st.divider()

    for check in checks:

        icon = (
            "🟢"
            if check.healthy
            else "🔴"
        )

        st.write(
            f"{icon} "
            f"**{check.component}**"
        )

        st.caption(
            check.message
        )