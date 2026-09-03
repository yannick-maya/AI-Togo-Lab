"""Page d'analyse de l'electrification."""

import streamlit as st

from dashboard.common import (
	load_key_data,
	render_filters,
	render_page_header,
	render_source,
	show_empty_message,
)
from src.analysis import analyze_electrification, project_electrification_2030
from src.viz import electricity_gap_figure, electrification_gap_area_figure

st.set_page_config(page_title="Électrification | Togo AI Lab", page_icon="⚡", layout="wide")
render_page_header("Électrification", "Mesurer la fracture entre territoires urbains et ruraux.")
data = load_key_data()
selected_year, _, _ = render_filters(data, show_city=False, show_region=False)
table = analyze_electrification(data["indicators"]["electrification"])
if selected_year is not None:
	table = table[table["year"] <= selected_year]
if table.empty:
	show_empty_message()
else:
	projection = project_electrification_2030(data["indicators"]["electrification"])
	national_columns = [c for c in table if str(c).strip() == "Access to electricity (% of population)"]
	national = table[national_columns[0]].dropna().iloc[-1] if national_columns and not table[national_columns[0]].dropna().empty else None
	gap = table["rural_urban_gap"].dropna().iloc[-1] if not table["rural_urban_gap"].dropna().empty else None
	col1, col2, col3 = st.columns(3)
	col1.metric("Accès national", f"{national:.1f} %" if national is not None else "Donnée absente")
	col2.metric("Écart urbain-rural", f"{gap:.1f} points" if gap is not None else "Donnée absente")
	col3.metric("Projection rurale 2030", f"{projection['rural_2030']:.1f} %" if projection['rural_2030'] is not None else "Non estimable")
	st.plotly_chart(electricity_gap_figure(table), width="stretch")
	st.plotly_chart(electrification_gap_area_figure(table), width="stretch")
	st.caption("Lecture : l'écart est calculé comme le taux urbain moins le taux rural. La projection 2030 prolonge linéairement la tendance observée; elle ne constitue pas une prévision causale.")
	render_source("indicators-tgo.csv, Banque mondiale")
