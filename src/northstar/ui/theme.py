"""
Platform Theme

Loads the shared stylesheet used throughout the
NorthStar Streamlit application.
"""

from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[3]


def load_theme() -> None:
    """
    Load the shared application stylesheet.
    """

    css = (
        BASE_DIR
        / "assets"
        / "styles.css"
    ).read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )