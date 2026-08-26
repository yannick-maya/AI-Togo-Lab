"""Page d'analyse des emissions."""

import streamlit as st

from dashboard.common import load_key_data, render_global_filters
from src.analysis import analyze_emissions
from src.viz import sector_emissions_figure

st.set_page_config(page_title="Emissions", layout="wide")
st.title("Emissions de gaz a effet de serre")
data = load_key_data()
render_global_filters(data)
table = analyze_emissions(data["ghg"])
st.plotly_chart(sector_emissions_figure(table), use_container_width=True)
st.caption("Les emissions sont exprimees en Gg et agregees par secteur et par gaz pour 2018.")
st.dataframe(table, use_container_width=True, hide_index=True)
