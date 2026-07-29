"""
NorthStar Configuration
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------
# Streamlit UI Configuration
# ---------------------------------------------------------------------

PAGE_TITLE = "NorthStar Executive Platform"

PAGE_ICON = "⭐"

LAYOUT = "wide"

INITIAL_SIDEBAR_STATE = "expanded"

APP_NAME = "NorthStar Executive Platform"

CAPTION = "NorthStar Applied AI Platform • " "Architecture • Analytics • MLOps • RAG"

# ---------------------------------------------------------------------
# Chart Configuration
# ---------------------------------------------------------------------

SMALL_CHART_HEIGHT = 350

LARGE_CHART_HEIGHT = 500

# ---------------------------------------------------------------------
# Application Settings
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    """
    Application configuration.
    """

    dashboard_repository: str = "csv"


settings = Settings()
