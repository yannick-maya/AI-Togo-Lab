"""Page de cartographie des zones protegees."""

import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, render_main_header
from src.analysis import add_vulnerability_score, summarize_creation_years, summarize_protected_areas, summarize_vulnerability
from src.viz import creation_year_figure, protected_areas_map_figure, regional_zone_count_figure, vulnerability_bar_figure

st.set_page_config(page_title="Zones protégées | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Zones protégées", "Localiser les 53 zones classées et comparer leur emprise par région.")
all_data = load_key_data()
data = all_data["areas"]
selected_region = render_filters(all_data, show_year=False, show_city=False)[2]
if selected_region is not None:
	data = data[data["region_nom_bdd"] == selected_region]
data = add_vulnerability_score(data)
if data.empty:
	show_empty_message()
else:
	vulnerability = summarize_vulnerability(data)
	creation = summarize_creation_years(data)
	col1, col2 = st.columns(2)
	with col1:
		kpi_card("Zones affichées", f"{len(data)}", source="Données géographiques", accent="forest")
	with col2:
		kpi_card("Surface protégée", f"{data['surface_km2'].sum():.1f} km²", source="Calcul UTM 31N", accent="forest")
	figures = [
		(protected_areas_map_figure(data), "La carte combine taille des bulles et couleur de vulnérabilité relative pour repérer les emprises les plus importantes.", ""),
		(regional_zone_count_figure(data), "Le nombre de zones montre la concentration administrative de la protection par région.", ""),
		(vulnerability_bar_figure(vulnerability), "Le classement par préfecture rend le score comparable et facilite la priorisation des diagnostics de terrain.", "warning"),
		(creation_year_figure(creation), "Seules les années de création renseignées sont affichées; les valeurs `Nsp` sont exclues plutôt que transformées en zéro.", ""),
	]
	for figure, text, kind in figures:
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch")
		with insight_col:
			insight(text, kind)
	render_source("file-zones-protegees-forets-classees-*.csv, données géographiques WGS84")
st.dataframe(summarize_protected_areas(data), width="stretch", hide_index=True)
