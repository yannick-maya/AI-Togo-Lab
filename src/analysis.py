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


def _min_max_scale(values: pd.Series) -> pd.Series:
	"""Normalise une serie entre 0 et 1; une constante vaut zero."""
	minimum, maximum = values.min(), values.max()
	if pd.isna(minimum) or maximum == minimum:
		return pd.Series(0.0, index=values.index)
	return (values - minimum) / (maximum - minimum)


def build_prioritization_index(
	data: pd.DataFrame,
	weights: dict[str, float] | None = None,
) -> pd.DataFrame:
	"""Construit un indice de priorisation regional ou prefectoral.

	Les variables sont normalisees entre 0 et 1 puis combinees. Par defaut,
	``electrification_gap``, ``cooking_dependence`` et ``forest_pressure``
	recoivent respectivement 40 %, 35 % et 25 %. Les donnees fournies ne
	mesurent pas ces facteurs a l'echelle locale : en leur absence, la surface
	et le nombre de zones protegees servent uniquement de proxy de pression
	de conservation. Le score ne classe donc pas des villages et ne remplace
	pas une enquete de terrain.
	"""
	group_columns = [
		column
		for column in ("region", "prefecture", "region_nom_bdd", "prefecture_nom_bdd")
		if column in data.columns
	]
	if not group_columns:
		raise KeyError("Une colonne region ou prefecture est obligatoire")
	result = data.copy()
	if "surface_km2" in result.columns:
		result["forest_pressure"] = result["surface_km2"]
	elif "forest_pressure" not in result.columns:
		result["forest_pressure"] = 0.0
	if "cooking_dependence" not in result.columns:
		result["cooking_dependence"] = 0.0
	if "electrification_gap" not in result.columns:
		result["electrification_gap"] = 0.0
	grouped = result.groupby(group_columns, as_index=False).agg(
		electrification_gap=("electrification_gap", "mean"),
		cooking_dependence=("cooking_dependence", "mean"),
		forest_pressure=("forest_pressure", "sum"),
	)
	weights = weights or {
		"electrification_gap": 0.40,
		"cooking_dependence": 0.35,
		"forest_pressure": 0.25,
	}
	grouped["priority_score"] = sum(
		weights.get(column, 0.0) * _min_max_scale(grouped[column])
		for column in ("electrification_gap", "cooking_dependence", "forest_pressure")
	)
	return grouped.sort_values("priority_score", ascending=False).reset_index(drop=True)
