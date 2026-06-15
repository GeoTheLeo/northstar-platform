import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

sys.path.append(
    str(project_root / "src")
)

import pandas as pd
import plotly.express as px
import streamlit as st

from bi.data.sample_data import (
    load_dashboard_data,
)

from bi.metrics.kpi_calculator import (
    calculate_kpis,
)

from bi.metrics.risk_metrics import (
    calculate_risk_metrics,
)

from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)

from rag_assistant.chat.assistant import (
    ask_assistant,
)

from rag_assistant.chat.copilot import (
    generate_executive_brief,
)

st.set_page_config(
    page_title="NorthStar Executive Platform",
    layout="wide",
)

st.markdown(
    """
    <style>

    .metric-card {
        background: linear-gradient(
            135deg,
            rgba(17,24,39,0.95),
            rgba(30,41,59,0.95)
        );

        padding: 24px;

        border-radius: 16px;

        box-shadow:
            0px 8px 24px rgba(0,0,0,0.35);

        border: 1px solid rgba(255,255,255,0.08);

        text-align: center;

        margin-bottom: 10px;
    }

    .metric-title {
        font-size: 14px;
        color: #BFC7D5;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title(
    "NorthStar Executive Platform"
)

st.markdown(
    """
    Unified AI Learning Intelligence Platform integrating:

    - Early Warning System
    - Learner Segmentation Engine
    - BI Decision Command Center
    - Semantic RAG Knowledge Assistant
    - Executive Copilot
    - MLOps Foundation
    """
)

# =====================================================
# KPI SECTION
# =====================================================

df = load_dashboard_data()

kpis = calculate_kpis(df)

risk_metrics = calculate_risk_metrics()

segment_metrics = (
    calculate_segmentation_metrics()
)

segments_df = pd.read_csv(
    "src/segmentation/data/segment_assignments.csv"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Students
            </div>
            <div class="metric-value">
                {kpis["total_students"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                At-Risk Learners
            </div>
            <div class="metric-value">
                {risk_metrics["at_risk_students"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Active Segments
            </div>
            <div class="metric-value">
                {segment_metrics["total_segments"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Risk Percentage
            </div>
            <div class="metric-value">
                {risk_metrics["risk_percentage"]}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# =====================================================
# ANALYTICS SECTION
# =====================================================

st.subheader(
    "Analytics Command Center"
)

attendance_chart = px.histogram(
    df,
    x="attendance",
    title="Attendance Distribution",
)

attendance_chart.update_layout(
    height=450,
)

engagement_chart = px.scatter(
    df,
    x="engagement_score",
    y="assessment_score",
    title="Engagement vs Assessment",
)

engagement_chart.update_layout(
    height=500,
)

segment_chart = px.histogram(
    segments_df,
    x="cluster",
    title="Learner Segment Distribution",
)

segment_chart.update_layout(
    height=500,
)

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

st.divider()

# =====================================================
# EXECUTIVE COPILOT
# =====================================================

st.subheader(
    "NorthStar Executive Copilot"
)

if st.button(
    "Generate Executive Briefing"
):

    briefing = (
        generate_executive_brief()
    )

    st.text_area(
        "Executive Briefing",
        briefing,
        height=300,
    )

st.divider()

# =====================================================
# AI KNOWLEDGE ASSISTANT
# =====================================================

st.subheader(
    "NorthStar Knowledge Assistant"
)

if "messages" not in st.session_state:

    st.session_state.messages = []

for message in (
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

question = st.chat_input(
    "Ask NorthStar..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    response = ask_assistant(
        question
    )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            response
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

st.caption(
    "NorthStar AI Learning Intelligence Platform"
)