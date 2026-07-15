"""
NorthStar Analytics View

Responsible for rendering executive analytics.

Presentation logic only.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_analytics(dashboard: dict) -> None:
    """
    Render the analytics dashboard.
    """

    st.subheader("Analytics Command Center")

    learner_df = dashboard["learner_df"]

    segments_df = pd.read_csv(
        "src/segmentation/data/segment_assignments.csv"
    )

    attendance_chart = px.histogram(
        learner_df,
        x="attendance",
        title="Attendance Distribution",
    )

    attendance_chart.update_layout(height=450)

    engagement_chart = px.scatter(
        learner_df,
        x="engagement_score",
        y="assessment_score",
        title="Engagement vs Assessment",
    )

    engagement_chart.update_layout(height=500)

    segment_chart = px.histogram(
        segments_df,
        x="cluster",
        title="Learner Segment Distribution",
    )

    segment_chart.update_layout(height=500)

    st.plotly_chart(
        attendance_chart,
        use_container_width=True,
    )

    st.plotly_chart(
        engagement_chart,
        use_container_width=True,
    )

    st.plotly_chart(
        segment_chart,
        use_container_width=True,
    )