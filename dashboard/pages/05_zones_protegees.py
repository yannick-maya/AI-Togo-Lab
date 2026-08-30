"""Page de cartographie des zones protegees."""

import pandas as pd
import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, recommendation, render_main_header, render_table
from src.analysis import add_vulnerability_score, summarize_creation_years, summarize_protected_areas, summarize_vulnerability
from src.viz import creation_year_figure, protected_areas_map_figure, regional_zone_count_figure, vulnerability_bar_figure

st.set_page_config(page_title="Zones protégées | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Zones protégées", "Localiser les 53 zones classées et comparer leur emprise par région.")
all_data = load_key_data()
data = all_data["areas"]
selected_region = render_filters(all_data, show_year=False, show_city=False, prefecture_filter=True, surface_filter=True)[2]
if selected_region is not None:
	data = data[data["region_nom_bdd"] == selected_region]
selected_prefecture = st.session_state.get("selected_prefecture", "Toutes")
minimum_surface = st.session_state.get("minimum_surface", 0.0)
if selected_prefecture != "Toutes":
	data = data[data["prefecture_nom_bdd"] == selected_prefecture]
data = data[data["surface_km2"] >= minimum_surface]
data = add_vulnerability_score(data)
if data.empty:
	show_empty_message()
else:
	vulnerability = summarize_vulnerability(data)
	creation = summarize_creation_years(data)
	n_zones = len(data)
	total_surface = data["surface_km2"].sum()
	mean_surface = total_surface / n_zones if n_zones else None
	n_prefectures = data["prefecture_nom_bdd"].nunique() if "prefecture_nom_bdd" in data else None
	creation_years = creation["creation_year"].dropna()
	oldest = int(creation_years.min()) if not creation_years.empty else None
	kpi_row_1 = st.columns(3)
	with kpi_row_1[0]:
		kpi_card("Zones affichées", f"{n_zones}", source="Données géographiques", accent="forest")
	with kpi_row_1[1]:
		kpi_card("Surface protégée", f"{total_surface:.1f} km²", source="Calcul UTM 31N", accent="forest")
	with kpi_row_1[2]:
		kpi_card("Préfectures représentées", str(n_prefectures) if n_prefectures is not None else "Donnée absente", source="Données géographiques", accent="forest")
	kpi_row_2 = st.columns(3)
	with kpi_row_2[0]:
		kpi_card("Surface moyenne / zone", f"{mean_surface:.1f} km²" if mean_surface is not None else "Donnée absente", source="Calcul UTM 31N", accent="forest")
	with kpi_row_2[1]:
		kpi_card("Zone la plus ancienne", str(oldest) if oldest is not None else "Non renseignée", source="Date de création", accent="forest")
	with kpi_row_2[2]:
		kpi_card("Vulnérabilité moyenne", f"{data['vulnerability_score'].mean():.2f}", source="Score relatif 0-1", accent="cooking")
	figures = [
		(protected_areas_map_figure(data), "La carte combine taille des bulles et couleur de vulnérabilité relative pour repérer les emprises les plus importantes.", ""),
		(regional_zone_count_figure(data), "Le nombre de zones montre la concentration administrative de la protection par région.", ""),
		(vulnerability_bar_figure(vulnerability), "Le classement par préfecture rend le score comparable et facilite la priorisation des diagnostics de terrain.", "warning"),
		(creation_year_figure(creation), "Seules les années de création renseignées sont affichées; les valeurs `Nsp` sont exclues plutôt que transformées en zéro.", ""),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"protected_areas_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	render_source("file-zones-protegees-forets-classees-*.csv, données géographiques WGS84")
	region_table = (
		summarize_protected_areas(data)
		.groupby("region_nom_bdd", as_index=False)
		.agg(nombre_zones=("zones_protegees", "sum"), surface_cumulee_km2=("surface_protegee_km2", "sum"))
	)
	region_vuln = summarize_vulnerability(data).groupby("region_nom_bdd", as_index=False)["vulnerability_score"].mean()
	region_table = region_table.merge(region_vuln, on="region_nom_bdd").sort_values("surface_cumulee_km2", ascending=False)
	region_table = region_table.rename(columns={"region_nom_bdd": "Région", "nombre_zones": "Zones", "surface_cumulee_km2": "Surface cumulée (km²)", "vulnerability_score": "Vulnérabilité moyenne"})
	render_table(region_table, caption="Zones protégées par région")
	recommendation(
		"Recommandation",
		"Concentrer les efforts de gestion et de diagnostic de terrain sur les régions cumulant le plus "
		"grand nombre de zones et la vulnérabilité moyenne la plus élevée. Renforcer la connexion entre "
		"les zones isolées et la stratégie forestière nationale pour éviter une protection fragmentée."
	)
