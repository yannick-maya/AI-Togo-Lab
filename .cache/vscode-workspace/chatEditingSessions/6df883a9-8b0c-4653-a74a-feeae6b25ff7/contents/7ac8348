"""Page d'analyse des emissions."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_page_header, render_source, show_empty_message
from src.analysis import summarize_emission_sectors, analyze_emissions
from src.viz import emissions_treemap_figure, sector_emissions_figure

st.set_page_config(page_title="Émissions | Togo AI Lab", page_icon="◉", layout="wide")
render_page_header("Émissions", "Comparer le poids des secteurs et des gaz dans le bilan national 2018.")
data = load_key_data()
render_filters(data, show_year=False, show_city=False, show_region=False)
table = analyze_emissions(data["ghg"])
summary = summarize_emission_sectors(data["ghg"])
if table.empty:
	show_empty_message()
else:
	energy = summary.loc[summary["secteur"].str.lower() == "energie", "part_total"]
	col1, col2 = st.columns(2)
	col1.metric("Émissions totales", f"{summary['emissions_gg'].sum():,.0f} Gg")
	col2.metric("Part de l'énergie", f"{energy.iloc[0]:.1f} %" if not energy.empty else "Donnée absente")
	st.plotly_chart(sector_emissions_figure(table), width="stretch")
	st.plotly_chart(emissions_treemap_figure(table), width="stretch")
	st.caption("Lecture : le secteur Énergie est comparé aux autres secteurs sur la coupe disponible de 2018. Les données manquantes sont exclues des agrégations.")
	render_source("observationdata-xorttne.csv, inventaire national des GES")
