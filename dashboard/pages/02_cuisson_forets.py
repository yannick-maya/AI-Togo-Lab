"""Page d'analyse de la cuisson et des forets."""

import pandas as pd
import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, recommendation, render_main_header, render_table
from src.analysis import (
	build_cooking_forest_correlation_insight,
	compute_cooking_forest_correlation,
	filter_cooking_fuels,
	prepare_cooking_composition,
	prepare_cooking_forest_series,
)
from src.viz import cooking_composition_figure, cooking_figure, cooking_forest_figure, renewable_share_figure

st.set_page_config(page_title="Cuisson et forêts | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Cuisson et forêts", "Relier les pratiques de cuisson à la pression potentielle sur le couvert forestier.")
data = load_key_data()
selected_year, _, _ = render_filters(
	data,
	show_city=False,
	show_region=False,
	fuel_options=["Bois", "Charbon", "Cuisson propre"],
)
table = prepare_cooking_forest_series(data["indicators"]["cooking"], data["indicators"]["forest"])
table = filter_cooking_fuels(table, st.session_state.get("selected_fuels", ["Bois", "Charbon", "Cuisson propre"]))
renewable = data["renewable_energy"]
composition_data = data["indicators"]["cooking"]
if selected_year is not None:
	table = table[table["year"] <= selected_year]
	composition_data = composition_data[composition_data["year"] <= selected_year]
trenewable = renewable[renewable["date"] <= selected_year] if selected_year is not None else renewable
if table.empty:
	show_empty_message()
else:
	latest = table.dropna(subset=["wood_charcoal_dependence"])
	value = latest["wood_charcoal_dependence"].iloc[-1] if not latest.empty else None
	corr = compute_cooking_forest_correlation(table)
	clean = table.dropna(subset=["clean_cooking_access"])
	clean_value = clean["clean_cooking_access"].iloc[-1] if not clean.empty else None
	kpi_row_1 = st.columns(3)
	with kpi_row_1[0]:
		kpi_card("Bois + charbon", f"{value:.1f} %" if value is not None else "Donnée absente", source="Banque mondiale", accent="cooking")
	with kpi_row_1[1]:
		kpi_card("Corrélation (niveaux)", f"r = {corr['levels_r']:.2f}" if corr["levels_r"] is not None else "Donnée absente", source="Pearson, n niveaux", accent="forest")
	with kpi_row_1[2]:
		kpi_card("Corrélation (variations)", f"r = {corr['changes_r']:.2f}" if corr["changes_r"] is not None else "Donnée absente", source="Pearson, .diff()", accent="forest")
	kpi_row_2 = st.columns(3)
	with kpi_row_2[0]:
		kpi_card("Cuisson propre", f"{clean_value:.1f} %" if clean_value is not None else "Donnée absente", source="Banque mondiale", accent="cooking")
	with kpi_row_2[1]:
		kpi_card("Année affichée", str(int(table["year"].max())) if not table["year"].dropna().empty else "Donnée absente", source="Banque mondiale", accent="forest")
	with kpi_row_2[2]:
		kpi_card("Observations couplées", f"n = {corr['levels_n']}", source="Séries cuisson/forêt", accent="primary")
	figures = [
		(cooking_figure(table), "La part bois-charbon reste le signal direct de dépendance aux combustibles traditionnels.", "warning"),
		(cooking_forest_figure(table), "Les séries nationales évoluent en parallèle; une analyse statistique de leur corrélation suit ci-dessous.", "warning"),
		(renewable_share_figure(trenewable), "La part des combustibles renouvelables situe la biomasse dans le mix énergétique global.", ""),
		(cooking_composition_figure(prepare_cooking_composition(composition_data)), "Cette composition identifie les combustibles dominants à la dernière année observée dans la sélection.", ""),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"cooking_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	insight(build_cooking_forest_correlation_insight(table), "warning")
	summary_rows = []
	for col, label in (("wood_charcoal_dependence", "Dépendance bois+charbon (%)"), ("forest_area_sq_km", "Surface forestière (km²)")):
		if col in table:
			s = pd.to_numeric(table[col], errors="coerce").dropna()
			if not s.empty:
				summary_rows.append({
					"Indicateur": label,
					"Min": s.min(),
					"Max": s.max(),
					"Moyenne": s.mean(),
					"Dernière valeur": s.iloc[-1],
					"N années": int(s.size),
				})
	if summary_rows:
		render_table(pd.DataFrame(summary_rows), caption="Cuisson et forêt — synthèse de la période")
	recommendation(
		"Recommandation",
		"Le remplacement progressif des combustibles bois-charbon par des solutions de cuisson propre "
		"représente le levier principal pour réduire à la fois l'exposition domestique et la pression sur "
		"le couvert forestier. Une corrélation significative entre la dépendance au bois-charbon et la "
		"superficie forestière plaiderait pour inscrire la cuisson propre dans la stratégie de protection des forêts."
	)
	render_source("indicators-tgo.csv et série énergie renouvelable")
