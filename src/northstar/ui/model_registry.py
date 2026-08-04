"""
NorthStar MLOps Operations View.
"""

import streamlit as st

from northstar.mlops.registry import registry


def render_model_registry() -> None:
    """
    Render registered model information.
    """

    st.subheader("⚙️ MLOps Operations")

    st.caption(
        "Machine learning models currently registered "
        "within the NorthStar platform."
    )

    for model in registry.all():

        with st.container(border=True):

            st.markdown(f"### {model.name}")

            left, right = st.columns(2)

            with left:

                st.metric(
                    "Version",
                    model.version,
                )

                st.metric(
                    "Algorithm",
                    model.algorithm,
                )

                st.metric(
                    "Task",
                    model.task,
                )

            with right:

                st.metric(
                    "Registered",
                    model.registered_at.strftime(
                        "%Y-%m-%d",
                    ),
                )

                st.write("Description")

                st.write(
                    model.description,
                )

            st.code(
                str(model.path),
                language="text",
            )