"""Page d'analyse des temperatures."""

import pandas as pd
import streamlit as st

from dashboard.common import load_key_data, render_filters, render_source, show_empty_message
from dashboard.components import initialize_page, insight, kpi_card, recommendation, render_main_header, render_table
from src.analysis import analyze_temperature_trends, compute_national_temperature_trend, prepare_temperature_anomalies, prepare_temperature_heatmap, summarize_temperature_gradient
from src.viz import temperature_anomaly_figure, temperature_figure, temperature_gradient_figure, temperature_heatmap_figure


def _temperature_trend_qualification(trend: dict) -> str:
	"""Qualifie la tendance de temperature selon sa significativite statistique."""
	if trend["p_value"] is not None and trend["p_value"] > 0.10:
		return (
			f"Mais la tendance est <b>non significative</b> "
			f"(p = {trend['p_value']:.2f} > 0.10) : la direction lue n'est pas "
			"statistiquement etablie sur ces 7 annees."
		)
	if trend["r2"] < 0.5:
		return "Tendance a confirmer (R² faible sur une fenetre courte)."
	if trend["slope_degc_an"] > 0:
		return "Réchauffement en hausse qui se confirme."
	if trend["slope_degc_an"] < 0:
		return "Refroidissement en baisse qui se confirme."
	return "Stabilite thermique."

st.set_page_config(page_title="Climat | Togo AI Lab", layout="wide")
initialize_page()
render_main_header("Climat", "Comparer les températures mensuelles des dix villes, du Sud au Nord.")
data = load_key_data()
temperature_years = sorted(
	data["temperatures"]["date"].astype("string").str.extract(r"^(\d{4})")[0]
	.dropna()
	.astype(int)
	.unique()
	.tolist()
)
selected_year, selected_city, _ = render_filters(
	data, show_region=False, month_filter=True, year_options=temperature_years, year_key="temperature_year"
)
raw = data["temperatures"]
if selected_year is not None:
	raw = raw[raw["date"].astype("string").str.startswith(str(selected_year))]
if selected_city is not None:
	raw = raw[raw["villes"] == selected_city]
selected_months = st.session_state.get("selected_months", (1, 12))
month_values = raw["date"].astype("string").str.extract(r"M(\d{1,2})")[0].astype(int)
raw = raw[month_values.between(selected_months[0], selected_months[1])]
table = analyze_temperature_trends(raw)
heatmap = prepare_temperature_heatmap(raw)
anomalies = prepare_temperature_anomalies(raw)
if selected_city is not None:
	table = table[table["villes"] == selected_city]
if table.empty:
	show_empty_message()
else:
	gradient = summarize_temperature_gradient(raw)
	n_years = int(raw["date"].astype("string").str.extract(r"^(\d{4})")[0].dropna().nunique())
	city_means = raw.groupby("villes", dropna=False)["value"].mean()
	city_std = float(city_means.std()) if len(city_means) > 1 else None
	month_national = (
		raw.copy()
	).assign(_mois=raw["date"].astype("string").str.extract(r"M(\d{1,2})")[0].astype(int))
	hottest = month_national.groupby("_mois")["value"].mean().idxmax()
	coldest = month_national.groupby("_mois")["value"].mean().idxmin()
	kpi_row_1 = st.columns(3)
	with kpi_row_1[0]:
		kpi_card("Villes analysées", f"{gradient['villes'].nunique()}", source="Série températures", accent="temperature")
	with kpi_row_1[1]:
		kpi_card("Température moyenne", f"{table['temperature_moyenne'].mean():.1f} °C", source="Série températures", accent="temperature")
	with kpi_row_1[2]:
		kpi_card("Années couvertes", str(n_years), source="Série températures", accent="temperature")
	kpi_row_2 = st.columns(3)
	with kpi_row_2[0]:
		kpi_card("Écart-type (villes)", f"{city_std:.1f} °C" if city_std is not None else "Donnée absente", source="Moyennes par ville", accent="temperature")
	with kpi_row_2[1]:
		kpi_card("Mois le plus chaud (moy. nat.)", str(hottest), source="Moyennes mensuelles", accent="temperature")
	with kpi_row_2[2]:
		kpi_card("Mois le plus froid (moy. nat.)", str(coldest), source="Moyennes mensuelles", accent="temperature")
	figures = [
		(temperature_figure(table), "La courbe compare les niveaux thermiques annuels des villes retenues par le filtre.", ""),
		(temperature_heatmap_figure(heatmap), "La heatmap révèle les mois les plus chauds et les plus frais pour chaque ville.", ""),
		(temperature_gradient_figure(gradient), "Le classement thermique fournit une lecture synthétique du gradient Sud-Nord; il est ordonné par température moyenne faute de latitude dans la source.", "warning"),
		(temperature_anomaly_figure(anomalies), "Une anomalie positive indique un mois plus chaud que la moyenne historique de la ville; une anomalie négative indique l'inverse.", ""),
	]
	for figure_index, (figure, text, kind) in enumerate(figures):
		fig_col, insight_col = st.columns([2.5, 1])
		with fig_col:
			st.plotly_chart(figure, width="stretch", key=f"temperature_figure_{figure_index}")
		with insight_col:
			insight(text, kind)
	trend = compute_national_temperature_trend(raw)
	if trend["slope_degc_an"] is None:
		insight(
			f"Tendance nationale : <b>données insuffisantes</b> "
			f"({trend['n']} annee(s) exploitables, il en faut au moins 3) pour "
			"estimer une direction fiable. Nous ne l'inventons pas."
		)
	else:
		qualification = _temperature_trend_qualification(trend)
		insight(
			f"Tendance nationale (moyenne des villes, niveau le plus robuste) : "
			f"pente = <b>{trend['slope_degc_an']:+.3f} °C/an</b>, soit "
			f"{trend['slope_degc_dec']:+.2f} °C/décennie, sur "
			f"n = {trend['n']} années — R² = {trend['r2']:.2f}, "
			f"p = {trend['p_value']:.2f}. {qualification}"
		)
	city_stats = (
		raw.dropna(subset=["villes", "value"])
		.groupby("villes", dropna=False)["value"]
		.agg(temp_moyenne="mean", temp_min="min", temp_max="max")
		.reset_index()
	)
	city_stats["amplitude"] = city_stats["temp_max"] - city_stats["temp_min"]
	city_stats = city_stats.sort_values("temp_moyenne", ascending=False)
	city_stats = city_stats.rename(columns={"villes": "Ville", "temp_moyenne": "Moyenne (°C)", "temp_min": "Min (°C)", "temp_max": "Max (°C)", "amplitude": "Amplitude (°C)"})
	render_table(city_stats, caption="Températures par ville (valeurs mensuelles de la sélection)")
	recommendation(
		"Recommandation",
		"Intégrer le gradient thermique observé et la tendance nationale dans la planification "
		"(urbanisme, santé publique, gestion de l'eau et de l'énergie). Suivre la fenêtre d'observation "
		"et l'ensemble des villes pour distinguer une tendance robuste d'un simple bruit saisonnier, "
		"plutôt que de réagir à un seul mois extrême."
	)
	render_source("observationdata-yvlucze.csv, températures mensuelles des villes")
