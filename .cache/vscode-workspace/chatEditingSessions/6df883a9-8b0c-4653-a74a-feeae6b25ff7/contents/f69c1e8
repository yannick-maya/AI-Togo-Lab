"""Traitements geographiques des zones protegees."""

from typing import Any

import geopandas as gpd
import pandas as pd
from shapely import wkt


SOURCE_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:32631"


def parse_wkt_geometry(value: Any) -> Any:
	"""Parse une geometrie WKT et renvoie None si elle est absente ou invalide."""
	if pd.isna(value) or not isinstance(value, str) or not value.strip():
		return None
	try:
		return wkt.loads(value)
	except (TypeError, ValueError):
		return None


def build_protected_areas_geodataframe(data: pd.DataFrame) -> gpd.GeoDataFrame:
	"""Construit un GeoDataFrame WGS84 a partir d'une table de zones protegees.

	Args:
		data: Table contenant une colonne ``geometry`` en WKT lon/lat.

	Returns:
		GeoDataFrame avec geometries parsees et CRS EPSG:4326.
	"""
	if "geometry" not in data.columns:
		raise KeyError("La colonne geometry est obligatoire")
	result = data.copy()
	result["geometry"] = result["geometry"].map(parse_wkt_geometry)
	return gpd.GeoDataFrame(result, geometry="geometry", crs=SOURCE_CRS)


def add_area_and_centroids(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
	"""Ajoute surface en km2 et centroide lon/lat aux zones.

	La surface est calculee dans le CRS UTM 31N, adapte au Togo, puis les
	centroïdes sont exprimes en coordonnees geographiques WGS84.
	"""
	if data.crs is None:
		raise ValueError("Le GeoDataFrame doit avoir un CRS defini")
	result = data.copy()
	projected = result.to_crs(METRIC_CRS)
	result["surface_km2"] = projected.geometry.area / 1_000_000
	centroids = projected.geometry.centroid.to_crs(SOURCE_CRS)
	result["centroid_lon"] = centroids.x
	result["centroid_lat"] = centroids.y
	return result
