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
        "Operational view of registered machine learning models."
    )

    for model in registry.all():

        with st.container(border=True):

            st.markdown(f"## {model.name}")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Status",
                    model.status,
                )

                st.metric(
                    "Stage",
                    model.stage,
                )

                st.metric(
                    "Version",
                    model.version,
                )

            with col2:

                st.metric(
                    "Algorithm",
                    model.algorithm,
                )

                st.metric(
                    "Task",
                    model.task,
                )

                st.metric(
                    "Artifact",
                    model.artifact,
                )

            with col3:

                st.metric(
                    "Loads",
                    model.load_count,
                )

                st.metric(
                    "Inferences",
                    model.inference_count,
                )

                st.metric(
                    "Registered",
                    model.registered_at.strftime(
                        "%Y-%m-%d",
                    ),
                )

            st.markdown("**Description**")

            st.write(
                model.description,
            )

            st.success(
                "Production Ready"
            )