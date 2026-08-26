"""Page des recommandations."""

import streamlit as st

from dashboard.common import load_key_data
from src.analysis import build_prioritization_index

st.set_page_config(page_title="Recommandations", layout="wide")
st.title("Recommandations et priorisation")
st.warning("Le score est un proxy regional ou prefectoral : les donnees ne permettent pas une priorisation village par village.")
table = build_prioritization_index(load_key_data()["areas"])
st.dataframe(table, use_container_width=True, hide_index=True)
st.caption("Le score combine ecart d'electrification, dependance a la cuisson traditionnelle et pression forestiere, avec les variables disponibles.")
