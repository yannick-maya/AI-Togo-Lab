"""Utilitaires partages par les pages Streamlit."""

import streamlit as st

from src.data_loader import (
    load_energy_emissions,
    load_ghg_by_sector,
    load_protected_areas,
    load_temperatures,
    load_world_bank_indicators,
)
from src.geo import add_area_and_centroids, build_protected_areas_geodataframe
from src.indicators import extract_key_indicators


@st.cache_data
def load_key_data() -> dict:
    """Charge et met en cache les donnees necessaires au dashboard."""
    return {
        "indicators": extract_key_indicators(load_world_bank_indicators()),
        "ghg": load_ghg_by_sector(),
        "temperatures": load_temperatures(),
        "areas": add_area_and_centroids(
            build_protected_areas_geodataframe(load_protected_areas())
        ),
        "energy_emissions": load_energy_emissions(),
    }
