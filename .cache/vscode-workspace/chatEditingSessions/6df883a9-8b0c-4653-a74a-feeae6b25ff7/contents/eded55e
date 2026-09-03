"""Fonctions d'analyse des cinq axes du projet."""

import pandas as pd

from src.cleaning import parse_temperature_period


def _pivot_indicators(data: pd.DataFrame) -> pd.DataFrame:
	"""Met les indicateurs en colonnes, sans inventer les valeurs absentes."""
	return (
		data.pivot_table(
			index="year", columns="indicator", values="value", aggfunc="mean"
		)
		.reset_index()
		.rename_axis(None, axis=1)
	)


def analyze_electrification(data: pd.DataFrame) -> pd.DataFrame:
	"""Calcule l'acces a l'electricite et l'ecart rural-urbain par annee."""
	table = _pivot_indicators(data)
	rural = next(
		(column for column in table if "rural" in str(column).lower()), None
	)
	urban = next(
		(column for column in table if "urban" in str(column).lower()), None
	)
	table["rural_urban_gap"] = table[urban] - table[rural] if rural and urban else pd.NA
	return table


def project_electrification_2030(data: pd.DataFrame) -> dict[str, float | None]:
	"""Projette lineairement les taux rural et urbain jusqu'en 2030.

	La projection est une extrapolation descriptive, pas une prevision causale.
	"""
	table = analyze_electrification(data).dropna(subset=["year"])
	result: dict[str, float | None] = {}
	for label in ("rural", "urban"):
		column = next((c for c in table if label in str(c).lower()), None)
		if column is None:
			result[f"{label}_2030"] = None
			continue
		points = table[["year", column]].dropna()
		if len(points) < 2:
			result[f"{label}_2030"] = None
			continue
		model = points.set_index("year")[column].sort_index()
		slope = (model.iloc[-1] - model.iloc[0]) / (model.index[-1] - model.index[0])
		result[f"{label}_2030"] = float(model.iloc[-1] + slope * (2030 - model.index[-1]))
	return result


def prepare_electrification_projection(data: pd.DataFrame) -> pd.DataFrame:
	"""Prepare les trajectoires observees et extrapolees jusqu'en 2030."""
	table = analyze_electrification(data)
	series = table[["year"] + [c for c in table if "rural" in str(c).lower() or "urban" in str(c).lower()]].copy()
	projection = project_electrification_2030(data)
	last_year = int(table["year"].dropna().max()) if not table["year"].dropna().empty else 2023
	for label in ("rural", "urban"):
		column = next((c for c in series if label in str(c).lower()), None)
		if column is None:
			continue
		series[f"{label}_projection"] = series[column]
		end = projection[f"{label}_2030"]
		if end is not None:
			future = pd.DataFrame({"year": range(last_year + 1, 2031)})
			start = series.loc[series["year"] == last_year, column].dropna()
			if not start.empty:
				future[f"{label}_projection"] = start.iloc[0] + (end - start.iloc[0]) * (future["year"] - last_year) / (2030 - last_year)
				series = series.merge(future, on="year", how="outer", suffixes=("", "_future"))
				series[f"{label}_projection"] = series[f"{label}_projection"].fillna(series.pop(f"{label}_projection_future"))
	return series.sort_values("year")


def analyze_cooking(data: pd.DataFrame) -> pd.DataFrame:
	"""Calcule la dependance au bois/charbon et l'acces a la cuisson propre."""
	table = _pivot_indicators(data)
	wood = next((column for column in table if "fuel: wood" in str(column).lower()), None)
	charcoal = next(
		(column for column in table if "fuel: charcoal" in str(column).lower()), None
	)
	clean = next(
		(column for column in table if "clean fuels" in str(column).lower()), None
	)
	table["wood_charcoal_dependence"] = sum(
		(table[column].fillna(0) for column in (wood, charcoal) if column),
		start=0,
	)
	table["clean_cooking_access"] = table[clean] if clean else pd.NA
	return table


def prepare_cooking_forest_series(
	 cooking_data: pd.DataFrame, forest_data: pd.DataFrame
) -> pd.DataFrame:
	"""Assemble les tendances cuisson et surface forestiere par annee."""
	cooking = analyze_cooking(cooking_data)
	forest = _pivot_indicators(forest_data)
	forest_column = next((c for c in forest if "forest area (sq. km)" in str(c).lower()), None)
	if forest_column is None:
		forest["forest_area_sq_km"] = pd.NA
	else:
		forest["forest_area_sq_km"] = forest[forest_column]
	return cooking.merge(forest[["year", "forest_area_sq_km"]], on="year", how="outer").sort_values("year")


def prepare_cooking_composition(data: pd.DataFrame) -> pd.DataFrame:
	"""Prepare la composition des combustibles pour la derniere annee disponible."""
	table = _pivot_indicators(data)
	if table.empty:
		return pd.DataFrame(columns=["fuel", "share"])
	fuel_columns = [column for column in table.columns if "main cooking fuel:" in str(column).lower()]
	if not fuel_columns:
		return pd.DataFrame(columns=["fuel", "share"])
	available = table.dropna(subset=fuel_columns, how="all").sort_values("year")
	if available.empty:
		return pd.DataFrame(columns=["fuel", "share"])
	latest = available.iloc[-1]
	result = pd.DataFrame(
		{
			"fuel": [str(column).split(":", 1)[1].split("(", 1)[0].strip().title() for column in fuel_columns],
			"share": [latest[column] for column in fuel_columns],
		}
	).dropna(subset=["share"])
	return result.sort_values("share", ascending=False)


def analyze_emissions(data: pd.DataFrame) -> pd.DataFrame:
	"""Agrege les GES 2018 par secteur et par type de gaz."""
	required = {"secteur", "type", "value"}
	missing = required.difference(data.columns)
	if missing:
		raise KeyError(f"Colonnes absentes: {', '.join(sorted(missing))}")
	return (
		data.groupby(["secteur", "type"], dropna=False, as_index=False)["value"]
		.sum(min_count=1)
		.rename(columns={"value": "emissions_gg"})
	)


def summarize_emission_sectors(data: pd.DataFrame) -> pd.DataFrame:
	"""Ajoute total et part de chaque secteur dans le bilan GES."""
	result = analyze_emissions(data)
	sector_totals = result.groupby("secteur", as_index=False)["emissions_gg"].sum()
	sector_totals["part_total"] = sector_totals["emissions_gg"] / sector_totals["emissions_gg"].sum() * 100
	return sector_totals.sort_values("emissions_gg", ascending=False)


def analyze_temperature_trends(data: pd.DataFrame) -> pd.DataFrame:
	"""Resume les temperatures mensuelles par ville et par annee."""
	parsed = parse_temperature_period(data)
	required = {"villes", "annee", "value"}
	missing = required.difference(parsed.columns)
	if missing:
		raise KeyError(f"Colonnes absentes: {', '.join(sorted(missing))}")
	return (
		parsed.groupby(["villes", "annee"], dropna=False, as_index=False)["value"]
		.agg(temperature_moyenne="mean", observations="count")
	)


def prepare_temperature_heatmap(data: pd.DataFrame) -> pd.DataFrame:
	"""Calcule les temperatures moyennes par ville et par mois."""
	parsed = parse_temperature_period(data)
	return (
		parsed.dropna(subset=["villes", "mois", "value"])
		.groupby(["villes", "mois"], as_index=False)["value"]
		.mean()
		.rename(columns={"value": "temperature_moyenne"})
	)


def summarize_temperature_gradient(data: pd.DataFrame) -> pd.DataFrame:
	"""Resume la temperature moyenne par ville pour lire le gradient nord-sud."""
	parsed = parse_temperature_period(data)
	return (
		parsed.groupby("villes", as_index=False)["value"]
		.mean()
		.rename(columns={"value": "temperature_moyenne"})
		.sort_values("temperature_moyenne", ascending=False)
	)


def prepare_temperature_anomalies(data: pd.DataFrame) -> pd.DataFrame:
	"""Calcule l'anomalie mensuelle par rapport a la moyenne de chaque ville."""
	parsed = parse_temperature_period(data).dropna(subset=["villes", "date_mois", "value"])
	parsed["ville_mean"] = parsed.groupby("villes")["value"].transform("mean")
	parsed["anomaly"] = parsed["value"] - parsed["ville_mean"]
	return parsed[["villes", "date_mois", "value", "anomaly"]].sort_values("date_mois")


def summarize_protected_areas(data: pd.DataFrame) -> pd.DataFrame:
	"""Resume les zones protegees par region et prefecture."""
	required = {"region_nom_bdd", "prefecture_nom_bdd", "surface_km2"}
	missing = required.difference(data.columns)
	if missing:
		raise KeyError(f"Colonnes absentes: {', '.join(sorted(missing))}")
	return (
		data.groupby(["region_nom_bdd", "prefecture_nom_bdd"], as_index=False)
		.agg(
			zones_protegees=("surface_km2", "size"),
			surface_protegee_km2=("surface_km2", "sum"),
		)
		.sort_values("surface_protegee_km2", ascending=False)
	)


def add_vulnerability_score(data: pd.DataFrame) -> pd.DataFrame:
	"""Ajoute un score relatif combinant surface et densite de zones protegees."""
	result = data.copy()
	result["surface_score"] = _min_max_scale(result["surface_km2"].fillna(0))
	result["zone_count_score"] = _min_max_scale(
		result.groupby("region_nom_bdd")["region_nom_bdd"].transform("size")
	)
	result["vulnerability_score"] = (
		0.7 * result["surface_score"] + 0.3 * result["zone_count_score"]
	)
	return result


def summarize_vulnerability(data: pd.DataFrame) -> pd.DataFrame:
	"""Agrege le score de vulnerabilite par region et prefecture."""
	result = add_vulnerability_score(data)
	return (
		result.groupby(["region_nom_bdd", "prefecture_nom_bdd"], as_index=False)
		.agg(vulnerability_score=("vulnerability_score", "mean"), surface_km2=("surface_km2", "sum"), zones_protegees=("etab_nom", "size"))
		.sort_values("vulnerability_score", ascending=False)
	)


def summarize_creation_years(data: pd.DataFrame) -> pd.DataFrame:
	"""Resume les zones par annee de creation quand celle-ci est exploitable."""
	result = data.copy()
	result["creation_year"] = pd.to_numeric(
		result["etab_creation_date"].astype("string").str.extract(r"(\d{4})")[0],
		errors="coerce",
	).astype("Int64")
	return (
		result.dropna(subset=["creation_year"])
		.groupby("creation_year", as_index=False)
		.size()
		.rename(columns={"size": "zones"})
		.sort_values("creation_year")
	)


def _min_max_scale(values: pd.Series) -> pd.Series:
	"""Normalise une serie entre 0 et 1; une constante vaut zero."""
	minimum, maximum = values.min(), values.max()
	if pd.isna(minimum) or maximum == minimum:
		return pd.Series(0.0, index=values.index)
	return (values - minimum) / (maximum - minimum)


def build_forest_pressure_index(data: pd.DataFrame) -> pd.DataFrame:
	"""Construit un score relatif de pression forestiere par prefecture.

	Le score utilise uniquement la surface des zones protegees disponible a
	l'echelle infranationale. Les donnees fournies ne contiennent pas de taux
	d'electrification ni de dependance a la cuisson par region ou prefecture;
	aucune valeur nationale n'est dupliquee artificiellement. Le score est donc
	un outil de reperage de la pression forestiere, pas un indice multi-facteurs
	ni une priorisation villageoise.
	"""
	required = {"region_nom_bdd", "prefecture_nom_bdd", "surface_km2"}
	missing = required.difference(data.columns)
	if missing:
		raise KeyError(f"Colonnes absentes: {', '.join(sorted(missing))}")
	grouped = (
		data.groupby(["region_nom_bdd", "prefecture_nom_bdd"], as_index=False)
		.agg(forest_pressure=("surface_km2", "sum"), zones_protegees=("surface_km2", "size"))
	)
	grouped["forest_pressure_score"] = _min_max_scale(grouped["forest_pressure"])
	return grouped.sort_values("forest_pressure_score", ascending=False).reset_index(drop=True)


def prepare_recommendation_table(data: pd.DataFrame) -> pd.DataFrame:
	"""Construit la table de classement de pression forestiere."""
	return build_forest_pressure_index(data)
