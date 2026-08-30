"""Page d'analyse des emissions."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, recommendation, render_main_header, render_table
from src.analysis import analyze_emissions, summarize_emission_sectors
from src.viz import emissions_share_figure, emissions_treemap_figure, energy_emissions_figure, sector_emissions_figure

st.set_page_config(page_title="Émissions | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Émissions", "Comparer le poids des secteurs et des gaz dans le bilan national 2018.")
data = load_key_data()
render_filters(data, show_year=False, show_city=False, show_region=False, sector_filter=True, gas_filter=True)
selected_sectors = st.session_state.get("selected_sectors", [])
selected_gases = st.session_state.get("selected_gases", [])
filtered_ghg = data["ghg"]
if selected_sectors:
	filtered_ghg = filtered_ghg[filtered_ghg["secteur"].isin(selected_sectors)]
if selected_gases:
	filtered_ghg = filtered_ghg[filtered_ghg["type"].isin(selected_gases)]
table = analyze_emissions(filtered_ghg)
summary = summarize_emission_sectors(filtered_ghg)
if table.empty:
	show_empty_message()
else:
	energy = summary.loc[summary["secteur"].str.lower() == "energie", "part_total"]
	n_sectors = summary["secteur"].nunique()
	n_gases = table["type"].nunique()
	cum_top2 = summary["part_total"].head(2).sum()
	kpi_row_1 = st.columns(3)
	with kpi_row_1[0]:
		kpi_card("Émissions totales", f"{summary['emissions_gg'].sum():,.0f} Gg", source="Inventaire 2018", accent="emissions")
	with kpi_row_1[1]:
		kpi_card("Part de l'énergie", f"{energy.iloc[0]:.1f} %" if not energy.empty else "Donnée absente", source="Inventaire 2018", accent="cooking")
	with kpi_row_1[2]:
		kpi_card("Secteurs suivis", str(n_sectors), source="Inventaire 2018", accent="emissions")
	kpi_row_2 = st.columns(3)
	with kpi_row_2[0]:
		kpi_card("Types de gaz suivis", str(n_gases), source="Inventaire 2018", accent="emissions")
	with kpi_row_2[1]:
		kpi_card("Part cumulée (2 premiers secteurs)", f"{cum_top2:.1f} %", source="Calcul sur le bilan", accent="emissions")
	with kpi_row_2[2]:
		kpi_card("Inventaire", "2018", source="Observationdata", accent="primary")
	figures = [
		(sector_emissions_figure(table), "Les barres empilées distinguent la contribution de chaque gaz dans les secteurs du bilan.", ""),
		(emissions_treemap_figure(table), "La surface de chaque bloc permet de repérer rapidement les secteurs et gaz dominants.", ""),
		(energy_emissions_figure(data["energy_emissions"]), "La série longue suit les émissions de CO2 de la production électrique jusqu'à 2023, en excluant les années sans valeur.", "warning"),
		(emissions_share_figure(summary), "La part sectorielle met en évidence le poids relatif de l'Énergie dans le bilan total disponible.", "alert"),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"emissions_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	sector_table = summary.rename(columns={"secteur": "Secteur", "emissions_gg": "Émissions (Gg)", "part_total": "Part du total (%)"})
	render_table(sector_table, caption="Bilan GES 2018 par secteur (toutes sélections de gaz/secteurs appliquées)")
	top_sector = summary.iloc[0]["secteur"] if not summary.empty else "n.d."
	top_part = summary.iloc[0]["part_total"] if not summary.empty else 0
	recommendation(
		"Recommandation",
		f"Le secteur « {top_sector} » concentre {top_part:.1f} % du bilan 2018 : toute stratégie de réduction "
		"des émissions doit d'abord cibler les postes dominants (production d'énergie, procédés) avant de "
		"traiter les sources diffuses. Les leviers les plus efficaces sont l'efficacité énergétique, la "
		"substitution des combustibles et l'électrification des usages fossiles."
	)
	render_source("observationdata-xorttne.csv et série CO2 énergie")
