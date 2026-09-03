"""Page des recommandations."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, render_main_header
from src.analysis import prepare_recommendation_table
from src.viz import prioritization_bar_figure, prioritization_scatter_figure, priority_zones_figure

st.set_page_config(page_title="Recommandations | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Recommandations", "Transformer les signaux disponibles en priorités d'action explicites.")
st.warning("Le score classe uniquement la pression forestiere relative par prefecture. Les donnees ne permettent pas une priorisation village par village ni un score multi-facteurs.")
data = load_key_data()
selected_region = render_filters(data, show_year=False, show_city=False, top_n_filter=True)[2]
areas = data["areas"]
if selected_region is not None:
	areas = areas[areas["region_nom_bdd"] == selected_region]
table = prepare_recommendation_table(areas)
table = table.head(st.session_state.get("top_n", 10))
if table.empty:
	show_empty_message()
else:
	best = table.iloc[0]
	col1, col2 = st.columns(2)
	with col1:
		kpi_card("Préfecture la plus exposée", str(best["prefecture_nom_bdd"]), source="Score forestier", accent="emissions")
	with col2:
		kpi_card("Score de pression forestière", f"{best['forest_pressure_score']:.2f}", source="Score forestier", accent="cooking")
	figures = [
		(prioritization_scatter_figure(table), "Le nuage met en relation la pression forestière et le score retenu pour classer les préfectures.", "warning"),
		(prioritization_bar_figure(table), "Le classement horizontal rend immédiatement visibles les préfectures en tête de priorisation.", ""),
		(priority_zones_figure(table), "Le nombre de zones protégées donne un repère opérationnel pour organiser les diagnostics des préfectures prioritaires.", ""),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"recommendations_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	st.dataframe(table, width="stretch", hide_index=True)
	render_source("indicators-tgo.csv et fichier géographique des zones protégées")
