"""Tests des chargeurs de donnees."""

import pandas as pd

from src.cleaning import clean_temperature_data, normalize_column_names
from src.data_loader import load_energy_emissions, load_world_bank_indicators
from src.indicators import extract_key_indicators


def test_load_world_bank_indicators_removes_metadata_row(tmp_path) -> None:
    """La ligne de codes de metadata est exclue et les types sont convertis."""
    source = tmp_path / "indicators.csv"
    source.write_text(
        "Country Name,Country ISO3,Year,Indicator Name,Indicator Code,Value\n"
        "#country+name,#country+code,#date+year,#indicator+name,#indicator+code,#indicator+value+num\n"
        "Togo,TGO,2020,Access to electricity (%),EG.ELC.ACCS.ZS,55.5\n",
        encoding="utf-8",
    )

    data = load_world_bank_indicators(source)

    assert len(data) == 1
    assert data.loc[0, "year"] == 2020
    assert data.loc[0, "value"] == 55.5


def test_load_energy_emissions_converts_empty_value_to_nan(tmp_path) -> None:
    """Une valeur vide de la serie CO2 devient un NaN numerique."""
    source = tmp_path / "emissions.csv"
    source.write_text(
        "indicator,country,countryiso3code,date,value,unit,obs_status,decimal\n"
        "CO2,Togo,TGO,2023,,, ,1\n",
        encoding="utf-8",
    )

    data = load_energy_emissions(source)

    assert pd.isna(data.loc[0, "value"])
    assert str(data["date"].dtype) == "Int64"


def test_clean_temperature_data_parses_valid_and_invalid_periods() -> None:
    """Les periodes mensuelles sont parsees et les valeurs invalides neutralisees."""
    source = pd.DataFrame(
        {"Date": ["2013M1", "2013M13", "invalide"], "Value": ["34", "", "x"]}
    )

    data = clean_temperature_data(source)

    assert data.loc[0, "annee"] == 2013
    assert data.loc[0, "mois"] == 1
    assert data.loc[0, "date_mois"] == pd.Timestamp("2013-01-01")
    assert pd.isna(data.loc[1, "mois"])
    assert pd.isna(data.loc[2, "value"])


def test_normalize_column_names_removes_accents() -> None:
    """Les noms accentues sont convertis en noms ASCII homogenes."""
    data = normalize_column_names(pd.DataFrame({"Libellés régionaux": ["Nord"]}))

    assert list(data.columns) == ["libelles_regionaux"]


def test_extract_key_indicators_returns_four_families() -> None:
    """Les familles metier sont extraites avec un schema commun."""
    data = extract_key_indicators(load_world_bank_indicators())

    assert set(data) == {"electrification", "cooking", "forest", "energy_emissions"}
    assert all(not table.empty for table in data.values())
    assert all(
        list(table.columns) == ["year", "indicator", "indicator_code", "value"]
        for table in data.values()
    )
