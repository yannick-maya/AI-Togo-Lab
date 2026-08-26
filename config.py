"""Configuration centrale du projet Togo Energie & Forets."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
REPORTS_DIR = PROJECT_ROOT / "reports"

COLORS = {
    "electricity": "#007C91",
    "cooking": "#D97706",
    "forest": "#2F6B3B",
    "emissions": "#B42318",
    "temperature": "#C2410C",
    "neutral": "#475467",
    "background": "#F8FAFC",
}

DEFAULT_COUNTRY = "Togo"
COUNTRY_ISO3 = "TGO"
