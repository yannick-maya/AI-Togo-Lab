"""Page d'analyse des temperatures."""

import streamlit as st

from dashboard.common import load_key_data
from src.analysis import analyze_temperature_trends
from src.viz import temperature_figure

st.set_page_config(page_title="Temperatures", layout="wide")
st.title("Evolution des temperatures")
table = analyze_temperature_trends(load_key_data()["temperatures"])
st.plotly_chart(temperature_figure(table), use_container_width=True)
st.caption("Les moyennes sont calculees a partir des observations mensuelles disponibles par ville.")
