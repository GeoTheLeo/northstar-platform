"""
NorthStar Platform Services View.
"""

import math

import streamlit as st

from northstar.monitoring import PlatformMonitor


def render_platform_health() -> None:
    """
    Render platform operational services.
    """

    monitor = PlatformMonitor()

    checks = monitor.run()

    healthy = sum(
        check.healthy
        for check in checks
    )

    score = round(
        healthy / len(checks) * 100,
        1,
    )

    # --------------------------------------------------
    # Platform Status Banner
    # --------------------------------------------------

    if score == 100:

        st.success(
            f"🟢 All platform services operational ({score:.0f}%)"
        )

    elif score >= 80:

        st.warning(
            f"🟡 Platform operational with warnings ({score:.0f}%)"
        )

    else:

        st.error(
            f"🔴 Platform requires attention ({score:.0f}%)"
        )

    st.write("")

    # --------------------------------------------------
    # Platform Services
    # --------------------------------------------------

    st.subheader("🖥 Platform Services")

    columns_per_row = 2

    total_rows = math.ceil(
        len(checks) / columns_per_row
    )

    for row in range(total_rows):

        left, right = st.columns(
            2,
            gap="large",
        )

        row_checks = checks[
            row * columns_per_row:
            (row + 1) * columns_per_row
        ]

        for column, check in zip(
            [left, right],
            row_checks,
        ):

            with column:

                with st.container(
                    border=True,
                ):

                    status = (
                        "🟢 Online"
                        if check.healthy
                        else "🔴 Offline"
                    )

                    st.markdown(
                        f"### {check.component}"
                    )

                    st.markdown(
                        f"**Status:** {status}"
                    )

                    st.caption(
                        check.message
                    )