"""Page d'analyse de l'electrification."""

import streamlit as st

from dashboard.common import load_key_data
from src.analysis import analyze_electrification
from src.viz import electricity_gap_figure

st.set_page_config(page_title="Electrification", layout="wide")
st.title("Electrification")
table = analyze_electrification(load_key_data()["indicators"]["electrification"])
st.plotly_chart(electricity_gap_figure(table), use_container_width=True)
st.caption("L'ecart rural-urbain est calcule comme le taux urbain moins le taux rural.")
st.dataframe(table, use_container_width=True, hide_index=True)
