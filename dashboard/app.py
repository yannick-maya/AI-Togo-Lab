"""Point d'entree de l'application Streamlit."""

import sys
from pathlib import Path

# Permet de lancer Streamlit depuis la racine ou depuis dashboard/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from config import LOGO_PATH

st.set_page_config(page_title="Togo Energie & Forets", page_icon="⚡", layout="wide")
if LOGO_PATH.exists():
    st.logo(str(LOGO_PATH), size="small")

pages = [
    st.Page("pages/00_accueil.py", title="Accueil", icon="⚡"),
    st.Page("pages/01_electrification.py", title="Électrification", icon="🔌"),
    st.Page("pages/02_cuisson_forets.py", title="Cuisson et forêts", icon="🌿"),
    st.Page("pages/03_emissions.py", title="Émissions", icon="◉"),
    st.Page("pages/04_temperatures.py", title="Climat", icon="☀"),
    st.Page("pages/05_zones_protegees.py", title="Zones protégées", icon="🌳"),
    st.Page("pages/06_recommandations.py", title="Recommandations", icon="✓"),
]
navigation = st.navigation(pages)
navigation.run()
