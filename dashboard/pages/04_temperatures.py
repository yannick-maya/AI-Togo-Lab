"""Page d'analyse des temperatures."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_page_header, render_source, show_empty_message
from src.analysis import analyze_temperature_trends, prepare_temperature_heatmap, summarize_temperature_gradient
from src.viz import temperature_figure, temperature_heatmap_figure

st.set_page_config(page_title="Climat | Togo AI Lab", page_icon="☀", layout="wide")
render_page_header("Climat", "Comparer les températures mensuelles des dix villes, du Sud au Nord.")
data = load_key_data()
selected_year, selected_city, _ = render_filters(data, show_region=False)
raw = data["temperatures"]
if selected_year is not None:
	raw = raw[raw["date"].astype(str).str.startswith(str(selected_year))]
if selected_city is not None:
	raw = raw[raw["villes"] == selected_city]
table = analyze_temperature_trends(raw)
heatmap = prepare_temperature_heatmap(raw)
if selected_city is not None:
	table = table[table["villes"] == selected_city]
if table.empty:
	show_empty_message()
else:
	gradient = summarize_temperature_gradient(raw)
	col1, col2 = st.columns(2)
	col1.metric("Villes analysées", f"{gradient['villes'].nunique()}")
	col2.metric("Température moyenne", f"{table['temperature_moyenne'].mean():.1f} °C")
	st.plotly_chart(temperature_figure(table), width="stretch")
	st.plotly_chart(temperature_heatmap_figure(heatmap), width="stretch")
	st.caption("Lecture : la heatmap restitue la saisonnalité moyenne; le filtre année est appliqué avant les deux graphiques.")
	render_source("observationdata-yvlucze.csv, températures mensuelles des villes")
