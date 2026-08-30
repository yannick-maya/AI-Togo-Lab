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


def _chunk(items: list, size: int = 4) -> list[list]:
    """Decoupe une liste en sous-listes de taille au plus `size`."""
    return [items[i : i + size] for i in range(0, len(items), size)]


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
    """Affiche uniquement les filtres pertinents pour une page, dans le corps.

    Les contrôles sont rendus dans une barre horizontale (.filter-navbar) sous
    l'en-tête, et plus dans le sidebar. Les clés de session_state et le
    comportement de filtrage restent strictement identiques a l'ancienne
    version sidebar.
    """
    st.markdown(
        '<div class="filter-navbar__title">Filtres</div>', unsafe_allow_html=True
    )
    with st.container(key="filter_navbar"):
        controls: list[tuple[str, callable]] = []
        indicators = data["indicators"]
        years = year_options or sorted(
            indicators["electrification"]["year"].dropna().astype(int).unique().tolist()
        )
        selected_year = None
        if show_year:
            year_choices = ["Toutes les années"] + [int(y) for y in years]
            def _year():
                return st.selectbox(
                    "Année de référence",
                    year_choices,
                    index=len(year_choices) - 1 if years else 0,
                    key=year_key,
                )
            controls.append(("Année de référence", _year))
        if show_city:
            cities = sorted(data["temperatures"]["villes"].dropna().unique().tolist())
            def _city():
                return st.selectbox("Ville", ["Toutes"] + cities, key="global_city")
            controls.append(("Ville", _city))
        if show_region:
            regions = sorted(data["areas"]["region_nom_bdd"].dropna().unique().tolist())
            def _region():
                return st.selectbox("Région", ["Toutes"] + regions, key="global_region")
            controls.append(("Région", _region))
        if display_modes:
            def _mode():
                return st.radio("Mode d'affichage", display_modes, key="display_mode", horizontal=True)
            controls.append(("Mode d'affichage", _mode))
        if fuel_options:
            fuel_choices = ["Tous"] + fuel_options
            def _fuels():
                return st.multiselect(
                    "Combustibles à afficher",
                    fuel_choices,
                    default=fuel_options,
                    key="selected_fuels",
                )
            controls.append(("Combustibles", _fuels))
        if sector_filter:
            sectors = sorted(data["ghg"]["secteur"].dropna().unique().tolist())
            sector_choices = ["Tous"] + sectors
            def _sectors():
                return st.multiselect(
                    "Secteurs", sector_choices, default=sectors, key="selected_sectors"
                )
            controls.append(("Secteurs", _sectors))
        if gas_filter:
            gases = sorted(data["ghg"]["type"].dropna().unique().tolist())
            gas_choices = ["Tous"] + gases
            def _gases():
                return st.multiselect(
                    "Types de gaz", gas_choices, default=gases, key="selected_gases"
                )
            controls.append(("Types de gaz", _gases))
        if month_filter:
            def _months():
                return st.slider(
                    "Mois inclus",
                    min_value=1,
                    max_value=12,
                    value=(1, 12),
                    key="selected_months",
                )
            controls.append(("Mois inclus", _months))
        if prefecture_filter:
            def _prefecture():
                filtered_areas = data["areas"]
                if st.session_state.get("global_region", "Toutes") != "Toutes":
                    filtered_areas = filtered_areas[
                        filtered_areas["region_nom_bdd"]
                        == st.session_state.get("global_region", "Toutes")
                    ]
                prefectures = sorted(
                    filtered_areas["prefecture_nom_bdd"].dropna().unique().tolist()
                )
                return st.selectbox(
                    "Préfecture", ["Toutes"] + prefectures, key="selected_prefecture"
                )
            controls.append(("Préfecture", _prefecture))
        if surface_filter:
            maximum = float(data["areas"]["surface_km2"].max())
            def _surface():
                return st.slider(
                    "Surface minimale (km²)",
                    min_value=0.0,
                    max_value=maximum,
                    value=0.0,
                    step=max(maximum / 100, 0.01),
                    key="minimum_surface",
                )
            controls.append(("Surface minimale (km²)", _surface))
        if top_n_filter:
            def _topn():
                return st.slider(
                    "Préfectures affichées",
                    min_value=5,
                    max_value=20,
                    value=10,
                    key="top_n",
                )
            controls.append(("Préfectures affichées", _topn))

        # Valeurs retournees pour les trois filtres communs.
        city_value = "Toutes"
        region_value = "Toutes"
        for row in _chunk(controls):
            cols = st.columns(len(row))
            for col, (label, render) in zip(cols, row):
                with col:
                    value = render()
                if label == "Année de référence":
                    selected_year = None if value == "Toutes les années" else value
                elif label == "Ville":
                    city_value = value
                elif label == "Région":
                    region_value = value
    return (
        selected_year,
        None if city_value == "Toutes" else city_value,
        None if region_value == "Toutes" else region_value,
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
