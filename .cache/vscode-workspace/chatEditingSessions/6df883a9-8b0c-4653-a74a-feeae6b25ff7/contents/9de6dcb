"""Page d'analyse de la cuisson et des forets."""

import streamlit as st

from dashboard.common import load_key_data
from src.analysis import analyze_cooking
from src.viz import cooking_figure

st.set_page_config(page_title="Cuisson et forets", layout="wide")
st.title("Cuisson et forets")
data = load_key_data()
table = analyze_cooking(data["indicators"]["cooking"])
st.plotly_chart(cooking_figure(table), use_container_width=True)
st.caption("La dependance combine les menages declarant le bois ou le charbon comme combustible principal.")
st.dataframe(table, use_container_width=True, hide_index=True)
