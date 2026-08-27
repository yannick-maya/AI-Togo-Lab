"""Utilitaires partages par les pages Streamlit."""

import streamlit as st

from src.data_loader import (
    load_energy_emissions,
    load_ghg_by_sector,
    load_protected_areas,
    load_renewable_energy,
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
        "renewable_energy": load_renewable_energy(),
    }


def render_global_filters(data: dict) -> tuple[int | None, str | None, str | None]:
    """Affiche les filtres communs et retourne leurs valeurs selectionnees."""
    return render_filters(data)


def render_filters(
    data: dict,
    show_year: bool = True,
    show_city: bool = True,
    show_region: bool = True,
    display_modes: list[str] | None = None,
    fuel_options: list[str] | None = None,
    sector_filter: bool = False,
    gas_filter: bool = False,
    month_filter: bool = False,
    prefecture_filter: bool = False,
    surface_filter: bool = False,
    top_n_filter: bool = False,
    year_options: list[int] | None = None,
    year_key: str = "global_year",
) -> tuple[int | None, str | None, str | None]:
    """Affiche uniquement les filtres pertinents pour une page."""
    st.sidebar.divider()
    st.sidebar.markdown('<div class="sidebar-section-title">Filtres</div>', unsafe_allow_html=True)
    indicators = data["indicators"]
    years = year_options or sorted(
        indicators["electrification"]["year"].dropna().astype(int).unique().tolist()
    )
    selected_year = None
    if show_year:
        selected_year = st.sidebar.selectbox(
            "Année de référence",
            years,
            index=len(years) - 1 if years else None,
            key=year_key,
        )
    cities = sorted(data["temperatures"]["villes"].dropna().unique().tolist())
    selected_city = "Toutes"
    if show_city:
        selected_city = st.sidebar.selectbox("Ville", ["Toutes"] + cities, key="global_city")
    regions = sorted(data["areas"]["region_nom_bdd"].dropna().unique().tolist())
    selected_region = "Toutes"
    display_modes: list[str] | None = None,
    fuel_options: list[str] | None = None,
    sector_filter: bool = False,
    gas_filter: bool = False,
    month_filter: bool = False,
    prefecture_filter: bool = False,
    surface_filter: bool = False,
    top_n_filter: bool = False,
    if show_region:
        selected_region = st.sidebar.selectbox(
            "Région", ["Toutes"] + regions, key="global_region"
        )
    if display_modes:
        st.session_state["display_mode"] = st.sidebar.radio(
            "Mode d'affichage", display_modes, key="display_mode"
        )
    if fuel_options:
        st.session_state["selected_fuels"] = st.sidebar.multiselect(
            "Combustibles à afficher",
            fuel_options,
            default=fuel_options,
            key="selected_fuels",
        )
    if sector_filter:
        sectors = sorted(data["ghg"]["secteur"].dropna().unique().tolist())
        st.session_state["selected_sectors"] = st.sidebar.multiselect(
            "Secteurs", sectors, default=sectors, key="selected_sectors"
        )
    if gas_filter:
        gases = sorted(data["ghg"]["type"].dropna().unique().tolist())
        st.session_state["selected_gases"] = st.sidebar.multiselect(
            "Types de gaz", gases, default=gases, key="selected_gases"
        )
    if month_filter:
        st.session_state["selected_months"] = st.sidebar.slider(
            "Mois inclus",
            min_value=1,
            max_value=12,
            value=(1, 12),
            key="selected_months",
        )
    if prefecture_filter:
        filtered_areas = data["areas"]
        if selected_region != "Toutes":
            filtered_areas = filtered_areas[
                filtered_areas["region_nom_bdd"] == selected_region
            ]
        prefectures = sorted(
            filtered_areas["prefecture_nom_bdd"].dropna().unique().tolist()
        )
        st.session_state["selected_prefecture"] = st.sidebar.selectbox(
            "Préfecture", ["Toutes"] + prefectures, key="selected_prefecture"
        )
    if surface_filter:
        maximum = float(data["areas"]["surface_km2"].max())
        st.session_state["minimum_surface"] = st.sidebar.slider(
            "Surface minimale (km²)",
            min_value=0.0,
            max_value=maximum,
            value=0.0,
            step=max(maximum / 100, 0.01),
            key="minimum_surface",
        )
    if top_n_filter:
        st.session_state["top_n"] = st.sidebar.slider(
            "Préfectures affichées",
            min_value=5,
            max_value=20,
            value=10,
            key="top_n",
        )
    st.sidebar.caption("Les filtres modifient les données affichées sur cette page.")
    return (
        selected_year,
        None if selected_city == "Toutes" else selected_city,
        None if selected_region == "Toutes" else selected_region,
    )


def render_page_header(title: str, context: str) -> None:
    """Affiche l'en-tête commun d'une page d'analyse."""
    st.markdown(f"## {title}\n\n_{context}_")


def render_source(source: str) -> None:
    """Affiche la source d'un visuel ou d'une section."""
    st.caption(f"Source : {source}")

def show_empty_message() -> None:
    """Explique explicitement une selection sans observation."""
    st.info("Aucune donnée pour cette sélection.")
