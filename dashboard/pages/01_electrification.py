"""Page d'analyse de l'electrification."""

import streamlit as st

from dashboard.common import (
	load_key_data,
	render_filters,
	render_source,
	show_empty_message,
)
from dashboard.components import initialize_page, insight, kpi_card, render_main_header
from src.analysis import (
	ELECTRIFICATION_GAP_MARKED_THRESHOLD,
	analyze_electrification,
	build_electrification_insights,
	prepare_electrification_projection,
	project_electrification_2030,
)
from src.viz import electricity_gap_figure, electrification_gap_area_figure, electrification_projection_figure, national_electricity_figure


def _projection_stats_text(projection: dict) -> str:
	"""Resume les statistiques de regression des projections rurales et urbaines."""
	lines: list[str] = []
	for label, name in (("rural", "Rural"), ("urban", "Urbain")):
		n = projection.get(f"{label}_n")
		slope = projection.get(f"{label}_slope")
		if slope is None:
			lines.append(
				f"- {name} : projection 2030 non estimable "
				f"(données insuffisantes, n = {n})."
			)
			continue
		r2 = projection.get(f"{label}_r2")
		p_value = projection.get(f"{label}_p_value")
		target_value = projection[f"{label}_2030"]
		target = f"{target_value:.1f} %" if target_value is not None else "n.c."
		text = (
			f"- {name} : 2030 ≈ {target} ; pente = {slope:+.2f} pts/an "
			f"(R² = {r2:.2f}, p = {p_value:.2f}, n = {int(n)} années)."
		)
		if target_value is not None and target_value > 100:
			text += (
				" <span style='color:inherit'>⚠ projection dépassant 100 % : "
				"l'extrapolation linéaire dépasse le plafond physique — "
				"elle est statistiquement possible mais irréaliste, "
				"indice d'un modèle saturé.</span>"
			)
		lines.append(text)
	return "<br>".join(lines)

st.set_page_config(page_title="Électrification | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Électrification", "Mesurer la fracture entre territoires urbains et ruraux.")
data = load_key_data()
selected_year, _, _ = render_filters(
	data,
	show_city=False,
	show_region=False,
	display_modes=["Taux national", "Urbain vs rural", "Écart uniquement"],
)
table = analyze_electrification(data["indicators"]["electrification"])
if selected_year is not None:
	table = table[table["year"] <= selected_year]
projection_data = data["indicators"]["electrification"]
if selected_year is not None:
	projection_data = projection_data[projection_data["year"] <= selected_year]
if table.empty:
	show_empty_message()
else:
	projection = project_electrification_2030(data["indicators"]["electrification"])
	national_columns = [c for c in table if str(c).strip() == "Access to electricity (% of population)"]
	national = table[national_columns[0]].dropna().iloc[-1] if national_columns and not table[national_columns[0]].dropna().empty else None
	gap = table["rural_urban_gap"].dropna().iloc[-1] if not table["rural_urban_gap"].dropna().empty else None
	col1, col2, col3 = st.columns(3)
	with col1:
		kpi_card("Accès national", f"{national:.1f} %" if national is not None else "Donnée absente", source="Banque mondiale", accent="primary")
	with col2:
		kpi_card("Écart urbain-rural", f"{gap:.1f} points" if gap is not None else "Donnée absente", source="Banque mondiale", accent="cooking")
	with col3:
		kpi_card("Projection rurale 2030", f"{projection['rural_2030']:.1f} %" if projection['rural_2030'] is not None else "Non estimable", source="Régression OLS descriptive", accent="forest")
	display_mode = st.session_state.get("display_mode", "Urbain vs rural")
	primary_figure = {
		"Taux national": national_electricity_figure(table),
		"Urbain vs rural": electricity_gap_figure(table),
		"Écart uniquement": electrification_gap_area_figure(table),
	}[display_mode]
	for figure_index, (figure, text, kind) in enumerate([
		(primary_figure, f"Le mode « {display_mode} » adapte la lecture à l'indicateur choisi et utilise les données jusqu'en {int(table['year'].max())}.", "warning"),
		(electrification_gap_area_figure(table), "Une aire positive persistante signifie que la convergence rurale n'a pas encore rejoint le niveau urbain.", "warning"),
		(electrification_projection_figure(prepare_electrification_projection(projection_data)), "La trajectoire est une extrapolation linéaire; elle doit être interprétée comme un scénario indicatif, non comme une prévision.", ""),
		(national_electricity_figure(table), "Le niveau national complète l'écart: il indique la couverture absolue de la population togolaise.", ""),
	]):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"electrification_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	insights = build_electrification_insights(table)
	if insights:
		insight("<br>".join(f"- {line}" for line in insights))
		insight(_projection_stats_text(projection))
		st.caption(
			f"Statistiques de la projection : régression linéaire OLS sur toutes "
			"les années disponibles (rural/urbain séparément), R² et p-value "
			"affichés ici ; bande d'incertitude = ± 1,96 × erreur type de la pente "
			"× distance d'extrapolation. Seuil descriptif d'écart : "
			f"{ELECTRIFICATION_GAP_MARKED_THRESHOLD:.0f} points = fracture marquée."
		)
	render_source("indicators-tgo.csv, Banque mondiale")
