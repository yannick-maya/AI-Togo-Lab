"""Chargement et normalisation des fichiers de donnees."""

from pathlib import Path
import re
import unicodedata

import pandas as pd

from config import RAW_DATA_DIR


def _snake_case(value: str) -> str:
	"""Convertit un nom de colonne en snake_case ASCII."""
	normalized = unicodedata.normalize("NFKD", str(value))
	without_accents = normalized.encode("ascii", "ignore").decode("ascii")
	return re.sub(r"[^a-zA-Z0-9]+", "_", without_accents).strip("_").lower()


def _read_csv(path: Path, **kwargs: object) -> pd.DataFrame:
	"""Lit un CSV UTF-8 et utilise latin-1 comme repli d'encodage."""
	try:
		return pd.read_csv(path, encoding="utf-8", **kwargs)
	except UnicodeDecodeError:
		return pd.read_csv(path, encoding="latin-1", **kwargs)


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
	"""Normalise les noms de colonnes d'une table."""
	result = data.copy()
	result.columns = [_snake_case(column) for column in result.columns]
	return result


def _resolve_path(path: Path | str | None, filename: str) -> Path:
	"""Retourne le chemin fourni ou celui de la source standard."""
	return Path(path) if path is not None else RAW_DATA_DIR / filename


def load_world_bank_indicators(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge les indicateurs Banque mondiale du Togo.

	Args:
		path: Chemin optionnel du fichier source.

	Returns:
		Table normalisee avec une valeur numerique nullable et une annee entiere.
	"""
	data = _read_csv(
		_resolve_path(path, "indicators-tgo.csv"),
		skiprows=[1],
		na_values=["", "NA", "N/A", ".."],
	)
	data = _normalize_columns(data)
	data["year"] = pd.to_numeric(data["year"], errors="coerce").astype("Int64")
	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	return data


def load_energy_emissions(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge les emissions de CO2 du secteur de l'energie."""
	data = _normalize_columns(
		_read_csv(_resolve_path(path, "emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv"))
	)
	data["date"] = pd.to_numeric(data["date"], errors="coerce").astype("Int64")
	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	return data


def load_renewable_energy(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge la part des combustibles renouvelables et des dechets."""
	data = _normalize_columns(
		_read_csv(_resolve_path(path, "energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv"))
	)
	data["date"] = pd.to_numeric(data["date"], errors="coerce").astype("Int64")
	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	return data


def load_ghg_by_sector(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge le bilan des emissions de GES par secteur et par gaz."""
	data = _normalize_columns(
		_read_csv(_resolve_path(path, "observationdata-xorttne.csv"))
	)
	data["date"] = pd.to_numeric(data["date"], errors="coerce").astype("Int64")
	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	return data


def load_temperatures(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge les temperatures mensuelles des villes togolaises."""
	data = _normalize_columns(
		_read_csv(_resolve_path(path, "observationdata-yvlucze.csv"))
	)
	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	return data


def load_protected_areas(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge les zones protegees et forets classees en WKT."""
	return _normalize_columns(
		_read_csv(
			_resolve_path(
				path,
				"file-zones-protegees-forets-classees-23-12-2024-09-53-17.csv",
			)
		)
	)


def load_protected_areas_dictionary(path: Path | str | None = None) -> pd.DataFrame:
	"""Charge le dictionnaire de donnees des zones protegees."""
	return _normalize_columns(
		_read_csv(_resolve_path(path, "zones-protegees-forets-classees.csv"))
	)
