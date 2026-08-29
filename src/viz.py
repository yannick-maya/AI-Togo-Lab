"""Visualisations Plotly reutilisables."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS
from dashboard.components import apply_layout


def _styled(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
	"""Applique le layout graphique commun."""
	return apply_layout(fig, title=title, height=height)


def electricity_gap_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure de l'ecart rural-urbain."""
	long_data = data.melt(
		id_vars="year",
		value_vars=[
			column
			for column in data.columns
			if "rural" in str(column).lower() or "urban" in str(column).lower()
		],
		var_name="indicator",
		value_name="value",
	)
	return _styled(px.line(
		long_data,
		x="year",
		y="value",
		color="indicator",
		title="Accès à l'électricité : urbain contre rural",
		labels={"year": "Année", "value": "Population couverte (%)", "indicator": "Zone"},
		color_discrete_sequence=[COLORS["electricity"], COLORS["electricity_light"]],
	), "Accès à l'électricité : urbain contre rural")


def electrification_gap_area_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit l'aire de l'ecart rural-urbain."""
	return _styled(px.area(
		data,
		x="year",
		y="rural_urban_gap",
		title="Écart d'accès à l'électricité",
		labels={"year": "Année", "rural_urban_gap": "Écart (points de pourcentage)"},
		color_discrete_sequence=[COLORS["cooking"]],
	), "Écart d'accès à l'électricité")


def national_electricity_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la courbe du niveau national d'acces."""
	column = next((c for c in data if str(c).strip() == "Access to electricity (% of population)"), None)
	if column is None:
		return _styled(go.Figure(), "Accès national à l'électricité")
	return _styled(px.line(data, x="year", y=column, markers=True, labels={"year": "Année", column: "Population couverte (%)"}), "Niveau national d'accès à l'électricité")


def electrification_projection_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit les trajectoires extrapolees vers 2030 avec bande d'incertitude."""
	figure = go.Figure()
	for label, name, color in (("rural", "Rural", COLORS["electricity"]), ("urban", "Urbain", COLORS["electricity_light"])):
		column = next((c for c in data if label in str(c).lower() and "projection" not in str(c).lower()), None)
		projection = f"{label}_projection"
		low = f"{label}_projection_low"
		high = f"{label}_projection_high"
		if column:
			figure.add_trace(go.Scatter(x=data["year"], y=data[column], name=f"{name} observé", mode="lines+markers", line={"color": color}))
		if projection in data and low in data and high in data:
			valid = data[data[low].notna() & data[high].notna()].sort_values("year")
			if not valid.empty:
				band_color = color.replace("0x", "#") if color.startswith("0x") else color
				figure.add_trace(go.Scatter(
					x=valid["year"],
					y=valid[high],
					name=f"{name} projeté (borne haute)",
					mode="lines",
					line={"width": 0},
					showlegend=False,
					hoverinfo="skip",
				))
				figure.add_trace(go.Scatter(
					x=valid["year"],
					y=valid[low],
					name=f"{name} bande d'incertitude",
					mode="lines",
					line={"width": 0},
					fill="tonexty",
					fillcolor="rgba(180,180,200,0.25)",
					legendgroup=name,
					showlegend=True,
				))
				figure.add_trace(go.Scatter(x=valid["year"], y=valid[projection], name=f"{name} projeté", mode="lines", line={"color": color, "dash": "dash"}, legendgroup=name, showlegend=False))
		elif projection in data:
			figure.add_trace(go.Scatter(x=data["year"], y=data[projection], name=f"{name} projeté", mode="lines", line={"color": color, "dash": "dash"}))
	figure.update_xaxes(title="Année")
	figure.update_yaxes(title="Population couverte (%)", rangemode="tozero")
	return _styled(figure, "Trajectoire indicative vers 2030")


def sector_emissions_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure des emissions par secteur et par gaz."""
	return _styled(px.bar(
		data,
		x="secteur",
		y="emissions_gg",
		color="type",
		barmode="stack",
		title="Émissions de GES par secteur et par gaz",
		labels={"secteur": "Secteur", "emissions_gg": "Emissions (Gg)"},
	), "Émissions de GES par secteur et par gaz")


def emissions_treemap_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit une hierarchie secteur puis type de gaz."""
	data = data.dropna(subset=["secteur", "type", "emissions_gg"])
	data = data[data["emissions_gg"] > 0]
	return _styled(px.treemap(
		data,
		path=["secteur", "type"],
		values="emissions_gg",
		color="emissions_gg",
		title="Hiérarchie des émissions par secteur et par gaz",
		labels={"emissions_gg": "Émissions (Gg)"},
		color_continuous_scale=[COLORS["background"], COLORS["emissions"]],
	), "Hiérarchie des émissions par secteur et par gaz")


def energy_emissions_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la serie longue des emissions CO2 du secteur electrique."""
	return _styled(px.line(data.dropna(subset=["date", "value"]).sort_values("date"), x="date", y="value", markers=True, title="CO2 du secteur électrique", labels={"date": "Année", "value": "Émissions (Mt CO2e)"}), "CO2 du secteur électrique")


def emissions_share_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le partage des emissions entre secteurs."""
	return _styled(px.pie(data, names="secteur", values="emissions_gg", hole=0.55, title="Part des émissions par secteur", labels={"secteur": "Secteur", "emissions_gg": "Émissions (Gg)"}), "Part des émissions par secteur")


def cooking_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure de cuisson propre et traditionnelle."""
	long_data = data.melt(
		id_vars="year",
		value_vars=["wood_charcoal_dependence", "clean_cooking_access"],
		var_name="indicator",
		value_name="value",
	)
	return _styled(px.line(
		long_data,
		x="year",
		y="value",
		color="indicator",
		title="Cuisson traditionnelle et cuisson propre",
		labels={"year": "Année", "value": "Ménages (%)", "indicator": "Indicateur"},
	), "Cuisson traditionnelle et cuisson propre")


def cooking_forest_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la comparaison cuisson et surface forestiere normalisee."""
	figure = go.Figure()
	for column, name, color in (
		("wood_charcoal_dependence", "Bois + charbon (%)", COLORS["cooking"]),
		("clean_cooking_access", "Cuisson propre (%)", COLORS["electricity"]),
	):
		if column in data:
			figure.add_trace(go.Scatter(x=data["year"], y=data[column], name=name, line={"color": color}))
	if "forest_area_sq_km" in data:
		figure.add_trace(go.Scatter(x=data["year"], y=data["forest_area_sq_km"], name="Surface forestière (km²)", yaxis="y2", line={"color": COLORS["forest"]}))
	figure.update_layout(
		title="Combustibles de cuisson et surface forestière",
		xaxis_title="Année",
		yaxis_title="Ménages (%)",
		yaxis2={"title": "Surface forestière (km²)", "overlaying": "y", "side": "right"},
		hovermode="x unified",
	)
	return _styled(figure)


def renewable_share_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit l'evolution de la part des combustibles renouvelables."""
	return _styled(px.line(data.sort_values("date"), x="date", y="value", markers=True, title="Part des combustibles renouvelables dans l'énergie", labels={"date": "Année", "value": "Part de l'énergie (%)"}), "Part des combustibles renouvelables dans l'énergie")


def cooking_composition_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la composition des combustibles de cuisson."""
	return _styled(px.bar(data, x="fuel", y="share", color="fuel", title="Combustibles de cuisson à la dernière année disponible", labels={"fuel": "Combustible", "share": "Ménages (%)"}), "Combustibles de cuisson à la dernière année disponible")


def temperature_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure des temperatures annuelles par ville."""
	return _styled(px.line(
		data,
		x="annee",
		y="temperature_moyenne",
		color="villes",
		labels={"annee": "Annee", "temperature_moyenne": "Temperature moyenne"},
	), "Évolution des températures moyennes")


def temperature_heatmap_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la heatmap ville par mois."""
	return _styled(px.density_heatmap(
		data,
		x="mois",
		y="villes",
		z="temperature_moyenne",
		title="Température moyenne par ville et par mois",
		labels={"mois": "Mois", "villes": "Ville", "temperature_moyenne": "Température (°C)"},
		color_continuous_scale="YlOrRd",
	), "Température moyenne par ville et par mois")


def temperature_gradient_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le classement thermique moyen des villes."""
	return _styled(px.bar(data.sort_values("temperature_moyenne"), x="temperature_moyenne", y="villes", orientation="h", color="temperature_moyenne", title="Gradient thermique moyen entre les villes", labels={"temperature_moyenne": "Température moyenne (°C)", "villes": "Ville"}, color_continuous_scale="YlOrRd"), "Gradient thermique moyen entre les villes")


def temperature_anomaly_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit l'evolution des anomalies de temperature."""
	return _styled(px.line(data, x="date_mois", y="anomaly", color="villes", title="Anomalies par rapport à la moyenne de chaque ville", labels={"date_mois": "Date", "anomaly": "Anomalie (°C)", "villes": "Ville"}), "Anomalies par rapport à la moyenne de chaque ville")


def protected_areas_map_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la carte Plotly des zones protegees."""
	return _styled(px.scatter_mapbox(
		data,
		lat="centroid_lat",
		lon="centroid_lon",
		size="surface_km2",
		color="vulnerability_score",
		hover_name="etab_nom",
		hover_data={"region_nom_bdd": True, "prefecture_nom_bdd": True, "surface_km2": ":.2f", "vulnerability_score": ":.2f"},
		zoom=5.8,
		mapbox_style="open-street-map",
		title="Zones protégées : surface et vulnérabilité relative",
		color_continuous_scale="YlOrRd",
	), "Zones protégées : surface et vulnérabilité relative", height=520)


def regional_zone_count_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le nombre de zones protegees par region."""
	counts = data.groupby("region_nom_bdd", as_index=False).size().rename(columns={"size": "zones"})
	return _styled(px.bar(counts, x="region_nom_bdd", y="zones", title="Nombre de zones protégées par région", labels={"region_nom_bdd": "Région", "zones": "Zones"}, color_discrete_sequence=[COLORS["forest"]]), "Nombre de zones protégées par région")


def vulnerability_bar_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le classement des prefectures par vulnerabilite."""
	return _styled(px.bar(data.sort_values("vulnerability_score"), x="vulnerability_score", y="prefecture_nom_bdd", color="vulnerability_score", orientation="h", title="Vulnérabilité relative par préfecture", labels={"vulnerability_score": "Score relatif", "prefecture_nom_bdd": "Préfecture"}, color_continuous_scale="YlOrRd"), "Vulnérabilité relative par préfecture")


def creation_year_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la distribution des zones par annee de creation."""
	return _styled(px.bar(data, x="creation_year", y="zones", title="Zones protégées par année de création renseignée", labels={"creation_year": "Année", "zones": "Nombre de zones"}, color_discrete_sequence=[COLORS["forest_light"]]), "Zones protégées par année de création renseignée")


def prioritization_scatter_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le nuage de points du classement de priorite."""
	return _styled(px.scatter(
		data,
		x="forest_pressure",
		y="forest_pressure_score",
		size="zones_protegees" if "zones_protegees" in data else None,
		color="region_nom_bdd" if "region_nom_bdd" in data else None,
		hover_name="prefecture_nom_bdd" if "prefecture_nom_bdd" in data else None,
		title="Pression forestière et score relatif",
		labels={"forest_pressure": "Surface forestière protégée (km²)", "forest_pressure_score": "Score relatif"},
	), "Pression forestière et score relatif")


def prioritization_bar_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le classement des prefectures par score."""
	return _styled(px.bar(data.sort_values("forest_pressure_score"), x="forest_pressure_score", y="prefecture_nom_bdd", orientation="h", color="forest_pressure_score", title="Classement des préfectures par pression forestière", labels={"forest_pressure_score": "Score relatif", "prefecture_nom_bdd": "Préfecture"}, color_continuous_scale="YlOrRd"), "Classement des préfectures par pression forestière")


def prioritization_components_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la decomposition des composantes du score."""
	long_data = data.melt(id_vars="prefecture_nom_bdd", value_vars=["forest_pressure"], var_name="component", value_name="value")
	return _styled(px.bar(long_data, x="value", y="prefecture_nom_bdd", color="component", orientation="h", barmode="group", title="Composantes du score par préfecture", labels={"value": "Valeur de la composante", "prefecture_nom_bdd": "Préfecture", "component": "Composante"}), "Composantes du score par préfecture")


def priority_zones_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit le nombre de zones des prefectures prioritaires."""
	return _styled(px.bar(data.sort_values("zones_protegees"), x="zones_protegees", y="prefecture_nom_bdd", orientation="h", color="forest_pressure_score", title="Zones protégées par préfecture exposée", labels={"zones_protegees": "Nombre de zones", "prefecture_nom_bdd": "Préfecture"}, color_continuous_scale="YlOrRd"), "Zones protégées par préfecture exposée")
