"""Page des recommandations."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_page_header, render_source, show_empty_message
from src.analysis import build_prioritization_index
from src.viz import prioritization_scatter_figure

st.set_page_config(page_title="Recommandations | Togo AI Lab", page_icon="✓", layout="wide")
st.title("Recommandations | Togo AI Lab")
render_page_header("Recommandations", "Transformer les signaux disponibles en priorités d'action explicites.")
st.warning("Le score est un proxy regional ou prefectoral : les donnees ne permettent pas une priorisation village par village.")
data = load_key_data()
selected_region = render_filters(data, show_year=False, show_city=False)[2]
areas = data["areas"]
if selected_region is not None:
	areas = areas[areas["region_nom_bdd"] == selected_region]
table = build_prioritization_index(areas)
table["zones_protegees"] = areas.groupby("prefecture_nom_bdd").size().reindex(table["prefecture_nom_bdd"]).fillna(0).to_numpy()
if table.empty:
	show_empty_message()
else:
	st.plotly_chart(prioritization_scatter_figure(table), width="stretch")
	st.dataframe(table, width="stretch", hide_index=True)
	st.caption("Lecture : le score combine écart d'électrification, dépendance à la cuisson traditionnelle et pression forestière; les composantes non disponibles localement sont conservées à zéro et doivent être complétées par une enquête.")
	render_source("indicators-tgo.csv et fichier géographique des zones protégées")
