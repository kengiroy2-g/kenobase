"""Unit tests for HOUSE-004 near-miss analysis."""

from __future__ import annotations

import pandas as pd
import pytest

from kenobase.analysis.house004_near_miss import analyze_house004


@pytest.mark.unit
def test_house004_self_context_computes_expected_ratios() -> None:
    df = pd.DataFrame(
        [
            {"Datum": "2023-01-01", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 0},
            {"Datum": "2023-01-01", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 9, "Anzahl der Gewinner": 4},
            {"Datum": "2023-01-02", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 1},
            {"Datum": "2023-01-02", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 9, "Anzahl der Gewinner": 2},
            {"Datum": "2023-01-03", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 2},
            {"Datum": "2023-01-03", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 9, "Anzahl der Gewinner": 1},
            {"Datum": "2023-01-04", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 0},
            {"Datum": "2023-01-04", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 9, "Anzahl der Gewinner": 3},
        ]
    )

    result = analyze_house004(df, keno_type=10, context="self", n_sim=0)

    assert result.overall.jackpot_winners_total == 3
    assert result.overall.near_winners_total == 10
    assert result.overall.ratio == pytest.approx(10 / 3)

    assert result.in_context.days == 2
    assert result.in_context.jackpot_winners_total == 3
    assert result.in_context.near_winners_total == 3
    assert result.in_context.ratio == pytest.approx(1.0)

    # Out-of-context has 0 jackpot winners -> ratio undefined
    assert result.out_context.jackpot_winners_total == 0
    assert result.out_context.ratio is None
    assert result.diff_in_minus_out is None


@pytest.mark.unit
def test_house004_gk1_context_splits_days() -> None:
    df = pd.DataFrame(
        [
            # Type 4 near/jackpot categories
            {"Datum": "2023-01-01", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": 10},
            {"Datum": "2023-01-01", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 100},
            {"Datum": "2023-01-02", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": 10},
            {"Datum": "2023-01-02", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 80},
            {"Datum": "2023-01-03", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": 10},
            {"Datum": "2023-01-03", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 110},
            {"Datum": "2023-01-04", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": 10},
            {"Datum": "2023-01-04", "Keno-Typ": 4, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 90},
            # GK1 flag via type 10 (10/10) on days 2 and 4
            {"Datum": "2023-01-02", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 1},
            {"Datum": "2023-01-04", "Keno-Typ": 10, "Anzahl richtiger Zahlen": 10, "Anzahl der Gewinner": 1},
        ]
    )

    result = analyze_house004(df, keno_type=4, context="gk1", n_sim=0)

    assert result.in_context.days == 2
    assert result.out_context.days == 2

    assert result.in_context.ratio == pytest.approx((80 + 90) / (10 + 10))
    assert result.out_context.ratio == pytest.approx((100 + 110) / (10 + 10))
    assert result.diff_in_minus_out == pytest.approx(8.5 - 10.5)

