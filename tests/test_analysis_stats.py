"""Tests des fonctions statistiques ajoutees au fond analytique."""

import numpy as np
import pandas as pd
import pytest

from src.analysis import (
    TREND_MIN_OBSERVATIONS,
    compute_cooking_forest_correlation,
    compute_linear_trend,
)


def test_compute_linear_trend_recovers_known_perfect_line() -> None:
    """Une droite parfaite connue est retrouvee exactement par l'OLS."""
    x = pd.Series([2000, 2001, 2002, 2003, 2004], dtype="float64")
    y = pd.Series([10.0, 13.0, 16.0, 19.0, 22.0], dtype="float64")

    result = compute_linear_trend(x, y)

    assert result["n"] == 5
    assert result["slope"] == pytest.approx(3.0, abs=1e-9)
    assert result["intercept"] == pytest.approx(10.0 - 3.0 * 2000, abs=1e-6)
    # Une droite parfaite => correlation = 1 et R2 = 1
    assert result["r_value"] == pytest.approx(1.0, abs=1e-9)
    assert result["p_value"] is not None
    assert result["std_err"] == pytest.approx(0.0, abs=1e-9)


def test_compute_linear_trend_returns_none_when_n_below_threshold() -> None:
    """Avec moins de TREND_MIN_OBSERVATIONS paires, aucune regression exploitable."""
    x = pd.Series([2000.0, 2001.0])
    y = pd.Series([5.0, 7.0])

    result = compute_linear_trend(x, y)

    assert result["n"] == 2
    assert result["n"] < TREND_MIN_OBSERVATIONS
    assert result["slope"] is None
    assert result["intercept"] is None
    assert result["r_value"] is None
    assert result["p_value"] is None
    assert result["std_err"] is None


def test_compute_linear_trend_drops_incomplete_pairs() -> None:
    """Les paires incompletes sont retirees avant la regression."""
    x = pd.Series([2000.0, 2001.0, 2002.0, 2003.0])
    y = pd.Series([10.0, np.nan, 14.0, 16.0])

    result = compute_linear_trend(x, y)

    assert result["n"] == 3
    assert result["slope"] == pytest.approx(2.0, abs=1e-9)
    assert result["r_value"] == pytest.approx(1.0, abs=1e-9)


def test_compute_cooking_forest_correlation_levels_and_changes() -> None:
    """Sur des series synthetiques, niveaux et variations sont calcules.

    Dependance bois/charbon en baisse et surface forestiere en hausse :
    la correlation est nettement negative, tant sur les niveaux que sur les
    variations annuelles. On verifie le signe et l'ordre de grandeur des r,
    et que les p-values sont definies.
    """
    series = pd.DataFrame(
        {
            "year": np.arange(2000, 2006),
            "wood_charcoal_dependence": [80.0, 77.0, 74.0, 72.0, 69.0, 66.0],
            "forest_area_sq_km": [960.0, 972.0, 981.0, 990.0, 1004.0, 1013.0],
        }
    )

    result = compute_cooking_forest_correlation(series)

    assert result["levels_n"] >= TREND_MIN_OBSERVATIONS
    assert result["levels_r"] is not None and result["levels_r"] < -0.9
    assert result["levels_p"] is not None
    assert result["changes_n"] >= TREND_MIN_OBSERVATIONS
    assert result["changes_r"] is not None and result["changes_r"] < 0
    assert result["changes_p"] is not None


def test_compute_cooking_forest_correlation_insufficient_years() -> None:
    """Moins de trois annees de chevauchement => correlation non exploitable."""
    series = pd.DataFrame(
        {
            "year": [2014, 2017],
            "wood_charcoal_dependence": [90.3, 89.4],
            "forest_area_sq_km": [12270.3, 12181.5],
        }
    )

    result = compute_cooking_forest_correlation(series)

    assert result["levels_n"] < TREND_MIN_OBSERVATIONS
    assert result["levels_r"] is None
    assert result["levels_p"] is None
    assert result["changes_n"] < TREND_MIN_OBSERVATIONS
    assert result["changes_r"] is None
    assert result["changes_p"] is None
