"""Page d'analyse de la cuisson et des forets."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_page_header, render_source, show_empty_message
from src.analysis import prepare_cooking_forest_series
from src.viz import cooking_figure, cooking_forest_figure

st.set_page_config(page_title="Cuisson et forêts | Togo AI Lab", page_icon="🌿", layout="wide")
render_page_header("Cuisson et forêts", "Relier les pratiques de cuisson à la pression potentielle sur le couvert forestier.")
data = load_key_data()
selected_year, _, _ = render_filters(data, show_city=False, show_region=False)
table = prepare_cooking_forest_series(data["indicators"]["cooking"], data["indicators"]["forest"])
if selected_year is not None:
	table = table[table["year"] <= selected_year]
if table.empty:
	show_empty_message()
else:
	latest = table.dropna(subset=["wood_charcoal_dependence"])
	value = latest["wood_charcoal_dependence"].iloc[-1] if not latest.empty else None
	col1, col2 = st.columns(2)
	col1.metric("Bois + charbon", f"{value:.1f} %" if value is not None else "Donnée absente")
	col2.metric("Année affichée", str(int(table["year"].max())) if not table["year"].dropna().empty else "Donnée absente")
	st.plotly_chart(cooking_figure(table), width="stretch")
	st.plotly_chart(cooking_forest_figure(table), width="stretch")
	st.caption("Lecture : le croisement met en regard des indicateurs nationaux de cuisson et de surface forestière; il décrit une évolution parallèle, sans établir une causalité.")
	render_source("indicators-tgo.csv, Banque mondiale")
