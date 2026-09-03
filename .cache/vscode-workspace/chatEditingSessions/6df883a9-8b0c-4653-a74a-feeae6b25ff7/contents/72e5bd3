"""Point d'entree de l'application Streamlit."""

import sys
from pathlib import Path

# Permet de lancer Streamlit depuis la racine ou depuis dashboard/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.components import render_sidebar_brand
from dashboard.style import inject_global_css

st.set_page_config(page_title="Togo Energie & Forets", layout="wide")
inject_global_css()
render_sidebar_brand()

pages = [
    st.Page("pages/00_accueil.py", title="Accueil"),
    st.Page("pages/01_electrification.py", title="Électrification"),
    st.Page("pages/03_emissions.py", title="Émissions"),
    st.Page("pages/04_temperatures.py", title="Climat"),
    st.Page("pages/02_cuisson_forets.py", title="Cuisson et forêts"),
    st.Page("pages/05_zones_protegees.py", title="Zones protégées"),
    st.Page("pages/06_recommandations.py", title="Recommandations"),
]
navigation = st.navigation(pages)
navigation.run()
