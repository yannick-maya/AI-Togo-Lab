"""Page des recommandations."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, render_main_header
from src.analysis import prepare_recommendation_table
from src.viz import prioritization_bar_figure, prioritization_components_figure, prioritization_scatter_figure, priority_zones_figure

st.set_page_config(page_title="Recommandations | Togo AI Lab", page_icon="✓", layout="wide")
initialize_page()
render_main_header("Recommandations", "Transformer les signaux disponibles en priorités d'action explicites.")
st.warning("Le score est un proxy regional ou prefectoral : les donnees ne permettent pas une priorisation village par village.")
data = load_key_data()
selected_region = render_filters(data, show_year=False, show_city=False)[2]
areas = data["areas"]
if selected_region is not None:
	areas = areas[areas["region_nom_bdd"] == selected_region]
table = prepare_recommendation_table(areas)
if table.empty:
	show_empty_message()
else:
	best = table.iloc[0]
	col1, col2 = st.columns(2)
	with col1:
		kpi_card("Préfecture prioritaire", str(best["prefecture_nom_bdd"]), source="Indice proxy", accent="emissions")
	with col2:
		kpi_card("Score prioritaire", f"{best['priority_score']:.2f}", source="Indice proxy", accent="cooking")
	figures = [
		(prioritization_scatter_figure(table), "Le nuage met en relation la pression forestière et le score retenu pour classer les préfectures.", "warning"),
		(prioritization_bar_figure(table), "Le classement horizontal rend immédiatement visibles les préfectures en tête de priorisation.", ""),
		(prioritization_components_figure(table), "Les composantes affichent explicitement les variables disponibles; les composantes locales absentes restent nulles.", "alert"),
		(priority_zones_figure(table), "Le nombre de zones protégées donne un repère opérationnel pour organiser les diagnostics des préfectures prioritaires.", ""),
	]
	for figure, text, kind in figures:
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch")
		with insight_col:
			insight(text, kind)
	st.dataframe(table, width="stretch", hide_index=True)
	render_source("indicators-tgo.csv et fichier géographique des zones protégées")
