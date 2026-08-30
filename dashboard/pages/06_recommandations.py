"""Page des recommandations."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, recommendation, render_main_header, render_table
from src.analysis import prepare_recommendation_table
from src.viz import prioritization_bar_figure, prioritization_components_figure, prioritization_scatter_figure, priority_zones_figure

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
	n_total = len(table)
	mean_score = table["forest_pressure_score"].mean()
	score_range = table["forest_pressure_score"].max() - table["forest_pressure_score"].min()
	kpi_row_1 = st.columns(3)
	with kpi_row_1[0]:
		kpi_card("Préfecture la plus exposée", str(best["prefecture_nom_bdd"]), source="Score forestier", accent="emissions")
	with kpi_row_1[1]:
		kpi_card("Score de pression forestière", f"{best['forest_pressure_score']:.2f}", source="Score forestier", accent="cooking")
	with kpi_row_1[2]:
		kpi_card("Préfectures dans le classement", str(n_total), source="Score forestier", accent="primary")
	kpi_row_2 = st.columns(3)
	with kpi_row_2[0]:
		kpi_card("Score moyen (sélection)", f"{mean_score:.2f}", source="Score forestier", accent="primary")
	with kpi_row_2[1]:
		kpi_card("Écart score min-max", f"{score_range:.2f}", source="Score forestier", accent="primary")
	with kpi_row_2[2]:
		kpi_card("Pression forestière max", f"{best['forest_pressure']:,.0f} km²", source="Surface zones protégées", accent="emissions")
	figures = [
		(prioritization_scatter_figure(table), "Le nuage met en relation la pression forestière et le score retenu pour classer les préfectures.", "warning"),
		(prioritization_bar_figure(table), "Le classement horizontal rend immédiatement visibles les préfectures en tête de priorisation.", ""),
		(prioritization_components_figure(table), "Décompose le score en sa composante de surface protégée; toutes les préfectures retenues partagent la même composante, seule la valeur varie.", ""),
		(priority_zones_figure(table), "Le nombre de zones protégées donne un repère opérationnel pour organiser les diagnostics des préfectures prioritaires.", ""),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"recommendations_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	rank_table = table.rename(columns={
		"region_nom_bdd": "Région",
		"prefecture_nom_bdd": "Préfecture",
		"forest_pressure": "Pression forestière (km²)",
		"zones_protegees": "Zones protégées",
		"forest_pressure_score": "Score (0-1)",
	})
	render_table(rank_table, caption="Classement des préfectures par pression forestière")
	recommendation(
		"Recommandation",
		f"Engager en priorité les diagnostics de terrain sur {best['prefecture_nom_bdd']} "
		f"(score {best['forest_pressure_score']:.2f}), la préfecture la plus exposée de la sélection. "
		"Vérifier l'emprise et l'affectation réelles des zones protégées classées avant d'allouer des "
		"moyens de conservation, car ce score ne reflète que la pression forestière relative."
	)
	render_source("indicators-tgo.csv et fichier géographique des zones protégées")
