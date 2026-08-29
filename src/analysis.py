"""Fonctions d'analyse des cinq axes du projet."""

import pandas as pd
from scipy import stats

from src.cleaning import parse_temperature_period


ELECTRIFICATION_GAP_MARKED_THRESHOLD = 50.0
ELECTRIFICATION_RECENT_OBSERVATIONS = 5
TREND_MIN_OBSERVATIONS = 3
TREND_P_VALUE_THRESHOLD = 0.10


def compute_linear_trend(x: pd.Series, y: pd.Series) -> dict[str, float | int | None]:
	"""Regression lineaire OLS sur (x, y), apres suppression des paires incompletes.

	Retourne slope, intercept, r_value, p_value, std_err et n (taille de
	l'echantillon utilise). Retourne des valeurs None si n < 3 (une droite
	passe toujours par 2 points, ce n'est pas une regression exploitable).
	"""
	paired = pd.DataFrame({"x": x, "y": y}).dropna()
	n = len(paired)
	if n < TREND_MIN_OBSERVATIONS:
		return {"slope": None, "intercept": None, "r_value": None, "p_value": None, "std_err": None, "n": n}
	result = stats.linregress(paired["x"], paired["y"])
	return {
		"slope": result.slope,
		"intercept": result.intercept,
		"r_value": result.rvalue,
		"p_value": result.pvalue,
		"std_err": result.stderr,
		"n": n,
	}


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


def build_electrification_insights(table: pd.DataFrame) -> list[str]:
	"""Retourne les interpretations chiffrees de l'electrification.

	Le seuil de 50 points est une convention descriptive pour qualifier une
	fracture marquee. La tendance utilise les cinq dernieres observations
	annuelles disponibles afin de limiter la lecture a un bruit ponctuel.
	"""
	lines: list[str] = []
	if table.empty or "year" not in table:
		return lines
	ordered = table.dropna(subset=["year"]).sort_values("year")
	national = next(
		(
			column
			for column in ordered
			if str(column).strip() == "Access to electricity (% of population)"
		),
		None,
	)
	if "rural_urban_gap" in ordered:
		gaps = ordered.dropna(subset=["rural_urban_gap"])
		if not gaps.empty:
			latest = gaps.iloc[-1]
			qualification = (
				"fracture marquee"
				if latest["rural_urban_gap"] >= ELECTRIFICATION_GAP_MARKED_THRESHOLD
				else "ecart modere"
			)
			lines.append(
				f"En {int(latest['year'])}, l'ecart urbain-rural atteint "
				f"{latest['rural_urban_gap']:.1f} points : {qualification}."
			)
			trend = compute_linear_trend(gaps["year"], gaps["rural_urban_gap"])
			qualif_text = _qualify_gap_trend(trend)
			if trend["slope"] is not None:
				lines.append(
					f"Sur les {trend['n']} annees disponibles, la tendance de "
					f"l'ecart est de {trend['slope']:+.2f} points/an "
					f"(R² = {trend['r_value']**2:.2f}) — {qualif_text}."
				)
			else:
				lines.append(
					f"Donnees insuffisantes ({trend['n']} annee(s)) pour estimer une "
					f"tendance fiable de l'ecart urbain-rural."
				)
	if national is not None:
		values = ordered.dropna(subset=[national])
		if not values.empty:
			latest = values.iloc[-1]
			lines.append(
				f"Le taux national atteint {latest[national]:.1f} % en "
				f"{int(latest['year'])}; aucune cible officielle 2030 n'est fournie."
			)
	return lines[:3]


def _qualify_gap_trend(trend: dict[str, float | int | None]) -> str:
	"""Qualifie la tendance de l'ecart selon son signe et sa significativite.

	Un ecart est considere non signifiant si la p-value depasse
	TREND_P_VALUE_THRESHOLD (0.10) : la pente observee est alors trop
	incertaine pour etre presentee comme une direction etablie. R2 faible et
	p_valeure non significative sont signales plutot que masques.
	"""
	if trend["slope"] is None:
		return "donnees insuffisantes"
	slope = trend["slope"]
	p_value = trend["p_value"]
	r2 = trend["r_value"] ** 2
	if p_value is not None and p_value > TREND_P_VALUE_THRESHOLD:
		return (
			"tendance non significative (p = "
			f"{p_value:.2f} > {TREND_P_VALUE_THRESHOLD:.2f}) : "
			"la direction lue n'est pas statistiquement etablie"
		)
	if r2 < 0.5:
		return "tendance a confirmer (R² faible)"
	return "hausse recente qui se confirme" if slope > 0 else (
		"baisse recente qui se confirme" if slope < 0 else "stabilite"
	)


_PROJECTION_TARGET_YEAR = 2030
_PROJECTION_CI_Z = 1.96


def project_electrification_2030(data: pd.DataFrame) -> dict[str, float | None]:
	"""Projette lineairement les taux rural et urbain jusqu'en 2030.

	La projection utilise une regression OLS sur TOUTES les annees disponibles
	(via compute_linear_trend), et non les deux points extremes. Elle inclut la
	pente, le R², la p-value, le nombre d'observations et une borne d'incertitude
	en 2030.

	Borne d'incertitude : demi-largeur = 1.96 * std_err * distance d'extrapolation,
	ou std_err est l'erreur type de la pente et la distance vaut (2030 - derniere
	annee observee). C'est une approximation descriptive de l'incertitude
	d'extrapolation, suffisante pour afficher une fourchette indicative, sans
	pretendre a un intervalle de prevision formel.

	La projection est une extrapolation descriptive, pas une prevision causale.
	"""
	table = analyze_electrification(data).dropna(subset=["year"])
	result: dict[str, float | None] = {}
	for label in ("rural", "urban"):
		column = next((c for c in table if label in str(c).lower()), None)
		key_base = f"{label}_{_PROJECTION_TARGET_YEAR}"
		for key in (
			key_base,
			f"{key_base}_low",
			f"{key_base}_high",
			f"{label}_slope",
			f"{label}_intercept",
			f"{label}_r2",
			f"{label}_p_value",
			f"{label}_n",
		):
			result[key] = None
		if column is None:
			continue
		points = table[["year", column]].dropna()
		trend = compute_linear_trend(points["year"], points[column])
		if trend["slope"] is None:
			continue
		target = _PROJECTION_TARGET_YEAR
		proj_target = trend["intercept"] + trend["slope"] * target
		last_year = int(points["year"].max())
		half_width = _PROJECTION_CI_Z * trend["std_err"] * (target - last_year)
		result[key_base] = float(proj_target)
		result[f"{key_base}_low"] = float(proj_target - half_width)
		result[f"{key_base}_high"] = float(proj_target + half_width)
		result[f"{label}_slope"] = float(trend["slope"])
		result[f"{label}_intercept"] = float(trend["intercept"])
		result[f"{label}_r2"] = float(trend["r_value"] ** 2)
		result[f"{label}_p_value"] = float(trend["p_value"])
		result[f"{label}_n"] = int(trend["n"])
	return result


def prepare_electrification_projection(data: pd.DataFrame) -> pd.DataFrame:
	"""Prepare les trajectoires observees et extrapolees jusqu'en 2030.

	Pour chaque zone, la projection est la droite de regression calculee sur
	toutes les annees observees (et non le segment entre les deux extremes).
	Les colonnes *_projection_low/high propagent une bande d'incertitude qui
	s'elargit avec la distance d'extrapolation a partir de la derniere annee
	observee (largeur nulle a la derniere annee observee).
	"""
	table = analyze_electrification(data)
	series = table[["year"] + [c for c in table if "rural" in str(c).lower() or "urban" in str(c).lower()]].copy()
	last_year = int(table["year"].dropna().max()) if not table["year"].dropna().empty else 2023
	for label in ("rural", "urban"):
		column = next((c for c in series if label in str(c).lower()), None)
		if column is None:
			continue
		trend = compute_linear_trend(series["year"], series[column])
		series[f"{label}_projection"] = series[column]
		series[f"{label}_projection_low"] = float("nan")
		series[f"{label}_projection_high"] = float("nan")
		if trend["slope"] is None:
			continue
		slope, intercept, std_err = trend["slope"], trend["intercept"], trend["std_err"]
		fitted = series.loc[series[column].notna(), "year"]
		last_fitted_year = int(fitted.max())
		future_years = range(last_year + 1, _PROJECTION_TARGET_YEAR + 1)
		extrapolated_years = sorted(set(fitted.tolist()) | set(future_years))
		rows: list[tuple[int, float, float, float]] = []
		for year in extrapolated_years:
			fitted_value = intercept + slope * year
			half_width = _PROJECTION_CI_Z * std_err * max(year - last_fitted_year, 0)
			rows.append((year, fitted_value, fitted_value - half_width, fitted_value + half_width))
		future = pd.DataFrame(rows, columns=["year", f"{label}_projection", f"{label}_projection_low", f"{label}_projection_high"])
		merged = series.merge(future, on="year", how="outer", suffixes=("", "_new"))
		for col in (f"{label}_projection", f"{label}_projection_low", f"{label}_projection_high"):
			merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(merged.pop(f"{col}_new"))
		series = merged
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
	available_fuels = [column for column in (wood, charcoal) if column]
	if available_fuels:
		table["wood_charcoal_dependence"] = table[available_fuels].sum(axis=1, min_count=1)
	else:
		table["wood_charcoal_dependence"] = pd.NA
	table["clean_cooking_access"] = table[clean] if clean else pd.NA
	return table


def filter_cooking_fuels(
	table: pd.DataFrame, selected_fuels: list[str]
) -> pd.DataFrame:
	"""Recalcule les series de cuisson selon les combustibles selectionnes."""
	result = table.copy()
	selected_columns = {
		"Bois": next((c for c in result if "fuel: wood" in str(c).lower()), None),
		"Charbon": next((c for c in result if "fuel: charcoal" in str(c).lower()), None),
	}
	traditional = [selected_columns[fuel] for fuel in selected_fuels if selected_columns.get(fuel)]
	result["wood_charcoal_dependence"] = (
		result[traditional].sum(axis=1, min_count=1) if traditional else pd.NA
	)
	clean_column = next((c for c in result if "clean fuels" in str(c).lower()), None)
	result["clean_cooking_access"] = (
		result[clean_column] if "Cuisson propre" in selected_fuels and clean_column else pd.NA
	)
	return result


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
