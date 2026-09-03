"""Page d'analyse des temperatures."""

import streamlit as st

from dashboard.common import load_key_data, render_global_filters
from src.analysis import analyze_temperature_trends
from src.viz import temperature_figure

st.set_page_config(page_title="Temperatures", layout="wide")
st.title("Evolution des temperatures")
data = load_key_data()
_, selected_city, _ = render_global_filters(data)
table = analyze_temperature_trends(data["temperatures"])
if selected_city is not None:
	table = table[table["villes"] == selected_city]
st.plotly_chart(temperature_figure(table), use_container_width=True)
st.caption("Les moyennes sont calculees a partir des observations mensuelles disponibles par ville.")
