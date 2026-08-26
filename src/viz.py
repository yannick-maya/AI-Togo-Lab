"""Visualisations Plotly reutilisables."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
	return px.line(long_data, x="year", y="value", color="indicator")


def sector_emissions_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure des emissions par secteur et par gaz."""
	return px.bar(
		data,
		x="secteur",
		y="emissions_gg",
		color="type",
		barmode="group",
		labels={"secteur": "Secteur", "emissions_gg": "Emissions (Gg)"},
	)


def cooking_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure de cuisson propre et traditionnelle."""
	long_data = data.melt(
		id_vars="year",
		value_vars=["wood_charcoal_dependence", "clean_cooking_access"],
		var_name="indicator",
		value_name="value",
	)
	return px.line(long_data, x="year", y="value", color="indicator")


def temperature_figure(data: pd.DataFrame) -> go.Figure:
	"""Construit la figure des temperatures annuelles par ville."""
	return px.line(
		data,
		x="annee",
		y="temperature_moyenne",
		color="villes",
		labels={"annee": "Annee", "temperature_moyenne": "Temperature moyenne"},
	)
