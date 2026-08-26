"""Nettoyage et harmonisation des donnees."""

import re
import unicodedata

import pandas as pd


def normalize_column_names(data: pd.DataFrame) -> pd.DataFrame:
	"""Retourne une copie dont les noms de colonnes sont en snake_case.

	Args:
		data: Table source a normaliser.

	Returns:
		Copie de la table avec des noms de colonnes homogenes.
	"""
	result = data.copy()
	names = []
	for column in result.columns:
		normalized = unicodedata.normalize("NFKD", str(column))
		ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
		names.append(re.sub(r"[^a-zA-Z0-9]+", "_", ascii_name).strip("_").lower())
	result.columns = names
	return result


def coerce_numeric_columns(
	data: pd.DataFrame, columns: list[str]
) -> pd.DataFrame:
	"""Convertit des colonnes en numerique en preservant les valeurs absentes.

	Args:
		data: Table a nettoyer.
		columns: Colonnes a convertir.

	Returns:
		Copie nettoyee avec des valeurs non convertibles remplacees par NaN.
	"""
	result = data.copy()
	for column in columns:
		if column not in result.columns:
			raise KeyError(f"Colonne absente: {column}")
		result[column] = pd.to_numeric(result[column], errors="coerce")
	return result


def parse_temperature_period(data: pd.DataFrame) -> pd.DataFrame:
	"""Parse une periode temperature telle que ``2013M1``.

	Args:
		data: Table contenant une colonne ``date`` au format AAAAMM.

	Returns:
		Copie avec les colonnes ``annee``, ``mois`` et ``date_mois``.
	"""
	if "date" not in data.columns:
		raise KeyError("La colonne date est obligatoire")

	result = data.copy()
	periods = result["date"].astype("string").str.extract(
		r"^(?P<annee>\d{4})M(?P<mois>\d{1,2})$"
	)
	result["annee"] = pd.to_numeric(periods["annee"], errors="coerce").astype("Int64")
	result["mois"] = pd.to_numeric(periods["mois"], errors="coerce").astype("Int64")
	valid_month = result["mois"].between(1, 12) | result["mois"].isna()
	result.loc[~valid_month, ["annee", "mois"]] = pd.NA
	date_parts = (
		result["annee"].astype("string")
		+ "-"
		+ result["mois"].astype("string").str.zfill(2)
		+ "-01"
	)
	result["date_mois"] = pd.to_datetime(date_parts, errors="coerce")
	return result


def clean_temperature_data(data: pd.DataFrame) -> pd.DataFrame:
	"""Normalise et nettoie la table des temperatures mensuelles."""
	result = normalize_column_names(data)
	result = parse_temperature_period(result)
	return coerce_numeric_columns(result, ["value"])
