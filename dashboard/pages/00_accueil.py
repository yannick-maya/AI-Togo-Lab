"""Page d'accueil du dashboard."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source
from dashboard.components import initialize_page, insight, kpi_card, render_main_header
from dashboard.content import (
    APPROACH_TEXT,
    APPROACH_TITLE,
    CONTEXT_TEXT,
    CONTEXT_TITLE,
    EXPLORE_TEXT,
)
from src.analysis import analyze_electrification
from src.viz import electricity_gap_figure

st.set_page_config(page_title="Accueil | Togo AI Lab", page_icon="⚡", layout="wide")
initialize_page()
render_main_header(
    "Togo Energie & Forets",
    "Eclairer la transition energetique et la protection des forets au Togo.",
)
data = load_key_data()
selected_year, _, _ = render_filters(data, show_city=False, show_region=False)
electrification = analyze_electrification(data["indicators"]["electrification"])
selected = electrification[electrification["year"] == selected_year]
coverage_columns = [
    column
    for column in selected
    if str(column).strip() == "Access to electricity (% of population)"
]
coverage = selected[coverage_columns].stack().dropna() if coverage_columns else None
gap = selected["rural_urban_gap"].dropna()

st.markdown(f"### {CONTEXT_TITLE}")
st.write(CONTEXT_TEXT)
st.markdown(f"### {APPROACH_TITLE}")
st.write(APPROACH_TEXT)

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Accès national", f"{coverage.iloc[0]:.1f} %" if coverage is not None and not coverage.empty else "Donnée absente", source="Banque mondiale", accent="primary")
with col2:
    kpi_card("Écart rural-urbain", f"{gap.iloc[0]:.1f} points" if not gap.empty else "Donnée absente", source="Banque mondiale", accent="cooking")
with col3:
    kpi_card("Indicateurs disponibles", f"{sum(len(table) for table in data['indicators'].values()):,}", source="Sources du projet", accent="electricity")
with col4:
    kpi_card("Zones protégées", f"{len(data['areas'])}", source="Données géographiques", accent="forest")

st.markdown("### Vue d'ensemble")
st.plotly_chart(electricity_gap_figure(electrification), width="stretch")
insight("La courbe donne le premier signal de la fracture territoriale; les pages détaillées permettent d'explorer ses déterminants et les zones de conservation.")
render_source("indicators-tgo.csv et fichier géographique des zones protégées")
st.info(EXPLORE_TEXT)
