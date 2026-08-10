"""
Activity Timeline.
"""

import streamlit as st

from northstar.activity import activity_log


def render_activity() -> None:
    """
    Render platform activity.
    """

    events = activity_log.recent()

    if not events:

        st.info(
            "No activity recorded."
        )

        return

    for event in events:

        with st.container(
            border=True,
        ):

            left, right = st.columns(
                [1, 7],
                gap="medium",
            )

            with left:

                st.markdown("### ⏱")

                st.caption(
                    event.timestamp.strftime(
                        "%H:%M"
                    )
                )

            with right:

                st.markdown(
                    f"**{event.category}**"
                )

                st.write(
                    event.message
                )