"""Tests fuer kenobase/analysis/payout_inference.py (DIST-003)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from kenobase.analysis.payout_inference import (
    EXPECTED_ODDS,
    NumberUnpopularityResult,
    PayoutInferenceResult,
    calculate_payout_inference,
    calculate_winner_statistics,
    identify_low_popularity_days,
)


@pytest.fixture
def sample_quote_df() -> pd.DataFrame:
    """Sample Quote Details DataFrame."""
    data = [
        # Datum, Keno-Typ, Matches, Gewinner, Gewinn/1Eur, Auszahlung
        {"Datum": datetime(2023, 1, 1), "Keno-Typ": 2, "Anzahl richtiger Zahlen": 2, "Anzahl der Gewinner": 100, "Gewinn/1Eur": 6, "Auszahlung": 600},
        {"Datum": datetime(2023, 1, 1), "Keno-Typ": 3, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 50, "Gewinn/1Eur": 16, "Auszahlung": 800},
        {"Datum": datetime(2023, 1, 2), "Keno-Typ": 2, "Anzahl richtiger Zahlen": 2, "Anzahl der Gewinner": 200, "Gewinn/1Eur": 6, "Auszahlung": 1200},
        {"Datum": datetime(2023, 1, 2), "Keno-Typ": 3, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 100, "Gewinn/1Eur": 16, "Auszahlung": 1600},
        {"Datum": datetime(2023, 1, 3), "Keno-Typ": 2, "Anzahl richtiger Zahlen": 2, "Anzahl der Gewinner": 150, "Gewinn/1Eur": 6, "Auszahlung": 900},
        {"Datum": datetime(2023, 1, 3), "Keno-Typ": 3, "Anzahl richtiger Zahlen": 3, "Anzahl der Gewinner": 75, "Gewinn/1Eur": 16, "Auszahlung": 1200},
    ]
    return pd.DataFrame(data)


@pytest.fixture
def extended_quote_df() -> pd.DataFrame:
    """Extended Quote Details DataFrame with more variance for stats."""
    import numpy as np

    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    data = []
    for date in dates:
        # Keno-Typ 2, Matches 2
        winners_2 = int(np.random.normal(150, 30))
        data.append({
            "Datum": date,
            "Keno-Typ": 2,
            "Anzahl richtiger Zahlen": 2,
            "Anzahl der Gewinner": max(10, winners_2),
            "Gewinn/1Eur": 6,
            "Auszahlung": max(10, winners_2) * 6,
        })
        # Keno-Typ 3, Matches 3
        winners_3 = int(np.random.normal(80, 20))
        data.append({
            "Datum": date,
            "Keno-Typ": 3,
            "Anzahl richtiger Zahlen": 3,
            "Anzahl der Gewinner": max(10, winners_3),
            "Gewinn/1Eur": 16,
            "Auszahlung": max(10, winners_3) * 16,
        })
    return pd.DataFrame(data)


class TestExpectedOdds:
    """Tests fuer EXPECTED_ODDS Konstanten."""

    def test_keno_type_2_odds(self):
        """Keno-Typ 2, 2 Richtige = 6x."""
        assert EXPECTED_ODDS[(2, 2)] == 6.0

    def test_keno_type_10_jackpot(self):
        """Keno-Typ 10, 10 Richtige = 100000x."""
        assert EXPECTED_ODDS[(10, 10)] == 100000.0

    def test_keno_type_8_zero(self):
        """Keno-Typ 8, 0 Richtige = 1x (Sonderwette)."""
        assert EXPECTED_ODDS[(8, 0)] == 1.0

    def test_all_expected_odds_positive(self):
        """Alle erwarteten Quoten sind positiv."""
        for key, value in EXPECTED_ODDS.items():
            assert value > 0, f"Expected odds for {key} should be positive"


class TestCalculatePayoutInference:
    """Tests fuer calculate_payout_inference()."""

    def test_basic_inference(self, sample_quote_df: pd.DataFrame):
        """Grundlegende Inference-Berechnung."""
        results = calculate_payout_inference(sample_quote_df)
        assert len(results) == 6

    def test_result_structure(self, sample_quote_df: pd.DataFrame):
        """PayoutInferenceResult hat korrekte Struktur."""
        results = calculate_payout_inference(sample_quote_df)
        r = results[0]

        assert isinstance(r, PayoutInferenceResult)
        assert r.date == "2023-01-01"
        assert r.keno_type == 2
        assert r.matches == 2
        assert r.winners == 100
        assert r.expected_payout == 600.0  # 100 * 6
        assert r.actual_payout == 600.0
        assert r.payout_per_winner == 6.0

    def test_normal_payout_classification(self, sample_quote_df: pd.DataFrame):
        """Korrekte Auszahlung wird als NORMAL klassifiziert."""
        results = calculate_payout_inference(sample_quote_df)
        # Alle Sample-Daten haben exakt erwartete Auszahlung
        for r in results:
            assert r.anomaly_score == 0.0
            assert r.popularity_class == "NORMAL"

    def test_anomaly_detection(self):
        """Anomalie wird erkannt bei Abweichung."""
        df = pd.DataFrame([{
            "Datum": datetime(2023, 1, 1),
            "Keno-Typ": 2,
            "Anzahl richtiger Zahlen": 2,
            "Anzahl der Gewinner": 100,
            "Gewinn/1Eur": 6,
            "Auszahlung": 700,  # 100 mehr als erwartet (600)
        }])
        results = calculate_payout_inference(df, anomaly_threshold=0.1)
        r = results[0]

        assert r.expected_payout == 600.0
        assert r.actual_payout == 700.0
        assert r.anomaly_score > 0.1
        assert r.popularity_class == "LOW_POPULARITY"  # Mehr Auszahlung als erwartet

    def test_zero_winners(self):
        """Keine Gewinner: payout_per_winner = 0."""
        df = pd.DataFrame([{
            "Datum": datetime(2023, 1, 1),
            "Keno-Typ": 7,
            "Anzahl richtiger Zahlen": 7,
            "Anzahl der Gewinner": 0,
            "Gewinn/1Eur": 1000,
            "Auszahlung": 0,
        }])
        results = calculate_payout_inference(df)
        r = results[0]

        assert r.winners == 0
        assert r.payout_per_winner == 0.0
        assert r.expected_payout == 0.0
        assert r.popularity_class == "NORMAL"


class TestCalculateWinnerStatistics:
    """Tests fuer calculate_winner_statistics()."""

    def test_basic_statistics(self, extended_quote_df: pd.DataFrame):
        """Berechnet korrekte Statistiken."""
        stats = calculate_winner_statistics(extended_quote_df)

        assert (2, 2) in stats
        assert (3, 3) in stats

        stat_2_2 = stats[(2, 2)]
        assert "mean" in stat_2_2
        assert "std" in stat_2_2
        assert "cv" in stat_2_2
        assert "n" in stat_2_2
        assert stat_2_2["n"] == 50

    def test_cv_calculation(self, extended_quote_df: pd.DataFrame):
        """CV wird korrekt berechnet."""
        stats = calculate_winner_statistics(extended_quote_df)
        stat_2_2 = stats[(2, 2)]

        # CV = std / mean
        expected_cv = stat_2_2["std"] / stat_2_2["mean"]
        assert abs(stat_2_2["cv"] - expected_cv) < 0.01

    def test_skips_small_samples(self, sample_quote_df: pd.DataFrame):
        """Ignoriert Kombinationen mit < 10 Eintraegen."""
        stats = calculate_winner_statistics(sample_quote_df)
        # sample_quote_df hat nur 3 Eintraege pro Kombination
        assert len(stats) == 0


class TestIdentifyLowPopularityDays:
    """Tests fuer identify_low_popularity_days()."""

    def test_identifies_low_popularity(self, extended_quote_df: pd.DataFrame):
        """Identifiziert Tage mit wenigen Gewinnern."""
        # Fuege einen Tag mit sehr wenigen Gewinnern hinzu
        low_pop_row = pd.DataFrame([{
            "Datum": datetime(2023, 3, 1),
            "Keno-Typ": 2,
            "Anzahl richtiger Zahlen": 2,
            "Anzahl der Gewinner": 50,  # Weit unter Durchschnitt (~150)
            "Gewinn/1Eur": 6,
            "Auszahlung": 300,
        }])
        df = pd.concat([extended_quote_df, low_pop_row], ignore_index=True)

        stats = calculate_winner_statistics(df)
        low_days = identify_low_popularity_days(df, stats, z_threshold=-1.5)

        # Der hinzugefuegte Tag sollte erkannt werden
        dates_found = [d for d, kt, m, z in low_days if d == "2023-03-01"]
        assert len(dates_found) >= 1

    def test_z_score_threshold(self, extended_quote_df: pd.DataFrame):
        """Z-Score Threshold wird respektiert."""
        stats = calculate_winner_statistics(extended_quote_df)

        # Mit sehr strengem Threshold (-3.0) sollte weniger gefunden werden
        low_strict = identify_low_popularity_days(extended_quote_df, stats, z_threshold=-3.0)
        low_lenient = identify_low_popularity_days(extended_quote_df, stats, z_threshold=-1.0)

        assert len(low_strict) <= len(low_lenient)


class TestNumberUnpopularityResult:
    """Tests fuer NumberUnpopularityResult Struktur."""

    def test_structure(self):
        """NumberUnpopularityResult hat korrekte Felder."""
        result = NumberUnpopularityResult(
            number=42,
            low_popularity_count=10,
            total_count=100,
            unpopularity_ratio=0.1,
        )

        assert result.number == 42
        assert result.low_popularity_count == 10
        assert result.total_count == 100
        assert result.unpopularity_ratio == 0.1


class TestIntegration:
    """Integrationstests."""

    def test_full_pipeline(self, extended_quote_df: pd.DataFrame):
        """Vollstaendiger Pipeline-Durchlauf."""
        # 1. Berechne Statistiken
        stats = calculate_winner_statistics(extended_quote_df)
        assert len(stats) >= 2

        # 2. Identifiziere Low-Popularity Tage
        low_days = identify_low_popularity_days(extended_quote_df, stats)
        # Kann 0 sein bei normalverteilten Daten

        # 3. Berechne Inference
        results = calculate_payout_inference(extended_quote_df)
        assert len(results) == 100  # 50 Tage * 2 Keno-Typen

        # 4. Klassifikation sollte hauptsaechlich NORMAL sein (exakte Quoten)
        normal_count = sum(1 for r in results if r.popularity_class == "NORMAL")
        assert normal_count == len(results)  # Alle sollten NORMAL sein
