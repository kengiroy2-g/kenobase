"""Unit-Tests fuer HYP-001: Gewinnklassen-Verteilungsmuster.

Testet:
1. Verteilungsanalyse (distribution.py)
2. Near-Miss Analyse (near_miss.py)
3. Gewinnklassen-Matrix (analyze_hyp001_complete.py)
4. Zeitliche Korrelation (analyze_hyp001_complete.py)

AC6: Mindestens 3 Tests muessen PASSED sein.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from kenobase.analysis.distribution import (
    DistributionResult,
    DistributionSummary,
    PayoutRatioResult,
    analyze_distribution,
    analyze_payout_ratio,
    create_summary,
    detect_anomalies,
    detect_payout_ratio_anomalies,
    load_gq_data,
)
from kenobase.analysis.near_miss import (
    NearMissResult,
    analyze_all_near_miss,
    analyze_near_miss,
    calculate_expected_ratio,
    count_significant_anomalies,
)


@pytest.fixture
def sample_gq_data() -> pd.DataFrame:
    """Erstellt Beispiel-GQ-Daten fuer Tests."""
    rows = []

    # 50 Ziehungstage
    dates = pd.date_range("2023-01-01", periods=50, freq="D")

    for date in dates:
        # Keno-Typ 2
        winners_2_2 = np.random.randint(200, 400)
        rows.append({
            "Datum": date,
            "Keno-Typ": 2,
            "Anzahl richtiger Zahlen": 2,
            "Anzahl der Gewinner": winners_2_2,
            "1 Euro Gewinn": "6 EUR",
            "Auszahlung": winners_2_2 * 6,  # payout = winners * quote
        })
        winners_2_1 = np.random.randint(2000, 4000)
        rows.append({
            "Datum": date,
            "Keno-Typ": 2,
            "Anzahl richtiger Zahlen": 1,
            "Anzahl der Gewinner": winners_2_1,
            "1 Euro Gewinn": "1 EUR",
            "Auszahlung": winners_2_1 * 1,
        })

        # Keno-Typ 10
        winners_10_10 = 1 if np.random.random() < 0.02 else 0
        rows.append({
            "Datum": date,
            "Keno-Typ": 10,
            "Anzahl richtiger Zahlen": 10,
            "Anzahl der Gewinner": winners_10_10,
            "1 Euro Gewinn": "100000 EUR",
            "Auszahlung": winners_10_10 * 100000,
        })
        winners_10_9 = np.random.randint(1, 5)
        rows.append({
            "Datum": date,
            "Keno-Typ": 10,
            "Anzahl richtiger Zahlen": 9,
            "Anzahl der Gewinner": winners_10_9,
            "1 Euro Gewinn": "10000 EUR",
            "Auszahlung": winners_10_9 * 10000,
        })
        winners_10_8 = np.random.randint(10, 50)
        rows.append({
            "Datum": date,
            "Keno-Typ": 10,
            "Anzahl richtiger Zahlen": 8,
            "Anzahl der Gewinner": winners_10_8,
            "1 Euro Gewinn": "1000 EUR",
            "Auszahlung": winners_10_8 * 1000,
        })
        winners_10_0 = np.random.randint(500, 1000)
        rows.append({
            "Datum": date,
            "Keno-Typ": 10,
            "Anzahl richtiger Zahlen": 0,
            "Anzahl der Gewinner": winners_10_0,
            "1 Euro Gewinn": "2 EUR",
            "Auszahlung": winners_10_0 * 2,
        })

        # Keno-Typ 8
        winners_8_8 = 1 if np.random.random() < 0.05 else 0
        rows.append({
            "Datum": date,
            "Keno-Typ": 8,
            "Anzahl richtiger Zahlen": 8,
            "Anzahl der Gewinner": winners_8_8,
            "1 Euro Gewinn": "10000 EUR",
            "Auszahlung": winners_8_8 * 10000,
        })
        winners_8_7 = np.random.randint(5, 20)
        rows.append({
            "Datum": date,
            "Keno-Typ": 8,
            "Anzahl richtiger Zahlen": 7,
            "Anzahl der Gewinner": winners_8_7,
            "1 Euro Gewinn": "100 EUR",
            "Auszahlung": winners_8_7 * 100,
        })

        # Keno-Typ 9
        winners_9_9 = 1 if np.random.random() < 0.03 else 0
        rows.append({
            "Datum": date,
            "Keno-Typ": 9,
            "Anzahl richtiger Zahlen": 9,
            "Anzahl der Gewinner": winners_9_9,
            "1 Euro Gewinn": "50000 EUR",
            "Auszahlung": winners_9_9 * 50000,
        })
        winners_9_8 = np.random.randint(2, 10)
        rows.append({
            "Datum": date,
            "Keno-Typ": 9,
            "Anzahl richtiger Zahlen": 8,
            "Anzahl der Gewinner": winners_9_8,
            "1 Euro Gewinn": "1000 EUR",
            "Auszahlung": winners_9_8 * 1000,
        })

    df = pd.DataFrame(rows)
    return df


class TestDistributionAnalysis:
    """Tests fuer Verteilungsanalyse."""

    def test_analyze_distribution_returns_results(self, sample_gq_data: pd.DataFrame):
        """Test 1: analyze_distribution gibt Liste von DistributionResult zurueck."""
        results = analyze_distribution(sample_gq_data)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, DistributionResult) for r in results)

    def test_analyze_distribution_calculates_cv(self, sample_gq_data: pd.DataFrame):
        """Test 2: CV (Variationskoeffizient) wird korrekt berechnet."""
        results = analyze_distribution(sample_gq_data, keno_type=2, matches=2)

        assert len(results) == 1
        result = results[0]

        assert result.cv >= 0  # CV muss positiv sein
        assert result.mean_winners > 0
        assert result.std_winners >= 0

        # CV = std / mean
        expected_cv = result.std_winners / result.mean_winners if result.mean_winners > 0 else 0
        assert abs(result.cv - expected_cv) < 0.01

    def test_analyze_distribution_filter_by_keno_type(self, sample_gq_data: pd.DataFrame):
        """Test 3: Filterung nach Keno-Typ funktioniert."""
        results_all = analyze_distribution(sample_gq_data)
        results_type10 = analyze_distribution(sample_gq_data, keno_type=10)

        # Gefilterte Ergebnisse sollten weniger sein
        assert len(results_type10) <= len(results_all)
        # Alle gefilterten Ergebnisse sollten Typ 10 sein
        assert all(r.keno_type == 10 for r in results_type10)

    def test_load_gq_data_parses_scraped_2025_dates_and_filters_noise(self, tmp_path: Path) -> None:
        """load_gq_data supports scraped 'So, 28.12.' date format and filters non-hit rows."""
        csv_path = tmp_path / "Keno_GQ_2025.csv"
        csv_path.write_text(
            "\n".join(
                [
                    "Datum,Keno-Typ,Anzahl richtiger Zahlen,Anzahl der Gewinner,1 Euro Gewinn",
                    "\"So, 28.12.\",2,2,320,6ÿ?",
                    "\"So, 28.12.\",2,Gewinnklasse1(5-stellige Gewinnzahl),0,\"Gewinnquote5.000,00ÿ?\"",
                ]
            ),
            encoding="utf-8",
        )

        df = load_gq_data(str(csv_path))
        assert len(df) == 1
        assert df.iloc[0]["Keno-Typ"] == 2
        assert df.iloc[0]["Anzahl richtiger Zahlen"] == 2
        assert df.iloc[0]["Anzahl der Gewinner"] == 320
        assert float(df.iloc[0]["1 Euro Gewinn"]) == pytest.approx(6.0)
        assert df.iloc[0]["Datum"].year == 2025


class TestNearMissAnalysis:
    """Tests fuer Near-Miss Analyse."""

    def test_analyze_near_miss_returns_result(self, sample_gq_data: pd.DataFrame):
        """Test 4: analyze_near_miss gibt NearMissResult zurueck."""
        result = analyze_near_miss(sample_gq_data, keno_type=10)

        assert isinstance(result, NearMissResult)
        assert result.keno_type == 10
        assert result.max_matches == 10
        assert result.near_miss_matches == 9

    def test_analyze_all_near_miss_covers_all_types(self, sample_gq_data: pd.DataFrame):
        """Test 5: analyze_all_near_miss analysiert alle verfuegbaren Keno-Typen."""
        results = analyze_all_near_miss(sample_gq_data)

        assert isinstance(results, list)
        assert len(results) > 0

        # Sollte alle Keno-Typen abdecken die in den Daten vorhanden sind
        types_in_data = set(sample_gq_data["Keno-Typ"].unique())
        types_analyzed = {r.keno_type for r in results}

        # Mindestens Typ 8, 9, 10 sollten analysiert werden
        assert 8 in types_analyzed or 8 not in types_in_data
        assert 9 in types_analyzed or 9 not in types_in_data
        assert 10 in types_analyzed or 10 not in types_in_data

    def test_calculate_expected_ratio_valid_types(self):
        """Test 6: Expected Ratio wird fuer alle gueltigen Typen berechnet."""
        for keno_type in range(2, 11):
            ratio = calculate_expected_ratio(keno_type)

            assert isinstance(ratio, float)
            assert ratio > 0  # Ratio muss positiv sein


class TestDetectAnomalies:
    """Tests fuer Anomalie-Erkennung."""

    def test_detect_anomalies_high_cv(self):
        """Test 7: Hoher CV wird als Anomalie erkannt."""
        results = [
            DistributionResult(
                keno_type=10,
                matches=9,
                mean_winners=100.0,
                std_winners=150.0,  # CV = 1.5 > 1.0
                cv=1.5,
                skewness=0.5,
                kurtosis=0.0,
                min_winners=10,
                max_winners=500,
                n_draws=50,
            ),
        ]

        anomalies = detect_anomalies(results, cv_threshold=1.0)

        assert len(anomalies) == 1
        assert anomalies[0][0] == 10  # keno_type
        assert anomalies[0][1] == 9   # matches
        assert "cv" in anomalies[0][2].lower()

    def test_detect_anomalies_high_skewness(self):
        """Test 8: Hohe Schiefe wird als Anomalie erkannt."""
        results = [
            DistributionResult(
                keno_type=8,
                matches=8,
                mean_winners=5.0,
                std_winners=3.0,
                cv=0.6,
                skewness=3.5,  # |skew| > 2.0
                kurtosis=0.0,
                min_winners=0,
                max_winners=20,
                n_draws=50,
            ),
        ]

        anomalies = detect_anomalies(results, skew_threshold=2.0)

        assert len(anomalies) == 1
        assert "skew" in anomalies[0][2].lower()

    def test_detect_anomalies_no_anomalies(self):
        """Test 9: Keine Anomalien bei normalen Werten."""
        results = [
            DistributionResult(
                keno_type=2,
                matches=2,
                mean_winners=300.0,
                std_winners=50.0,
                cv=0.17,  # < 1.0
                skewness=0.3,  # < 2.0
                kurtosis=0.1,
                min_winners=200,
                max_winners=400,
                n_draws=50,
            ),
        ]

        anomalies = detect_anomalies(results)

        assert len(anomalies) == 0


class TestCountSignificantAnomalies:
    """Tests fuer Zaehlung signifikanter Anomalien."""

    def test_count_significant_anomalies(self):
        """Test 10: Signifikante Anomalien werden korrekt gezaehlt."""
        results = [
            NearMissResult(
                keno_type=8,
                max_matches=8,
                near_miss_matches=7,
                near_miss_ratio=5.0,
                expected_ratio=4.0,
                chi2_stat=10.0,
                p_value=0.001,  # Signifikant
                is_significant=True,
                n_draws=50,
            ),
            NearMissResult(
                keno_type=9,
                max_matches=9,
                near_miss_matches=8,
                near_miss_ratio=2.0,
                expected_ratio=2.1,
                chi2_stat=0.5,
                p_value=0.5,  # Nicht signifikant
                is_significant=False,
                n_draws=50,
            ),
            NearMissResult(
                keno_type=10,
                max_matches=10,
                near_miss_matches=9,
                near_miss_ratio=10.0,
                expected_ratio=5.0,
                chi2_stat=15.0,
                p_value=0.0001,  # Signifikant
                is_significant=True,
                n_draws=50,
            ),
        ]

        count = count_significant_anomalies(results)

        assert count == 2


class TestCreateSummary:
    """Tests fuer Summary-Erstellung."""

    def test_create_summary_structure(self):
        """Test 11: Summary hat korrekte Struktur."""
        results = [
            DistributionResult(
                keno_type=2,
                matches=2,
                mean_winners=300.0,
                std_winners=50.0,
                cv=0.17,
                skewness=0.3,
                kurtosis=0.1,
                min_winners=200,
                max_winners=400,
                n_draws=50,
            ),
        ]

        anomalies = [
            (10, 9, "high_cv=1.5"),
        ]

        summary = create_summary(results, anomalies)

        assert isinstance(summary, DistributionSummary)
        assert summary.results == results
        assert len(summary.anomalies) == 1
        assert summary.overall_cv > 0


class TestIntegration:
    """Integrationstests."""

    def test_full_pipeline(self, sample_gq_data: pd.DataFrame):
        """Test 12: Vollstaendige Pipeline funktioniert."""
        # 1. Verteilungsanalyse
        dist_results = analyze_distribution(sample_gq_data)
        assert len(dist_results) > 0

        # 2. Anomalien erkennen
        anomalies = detect_anomalies(dist_results)
        # Anomalien koennen 0 sein

        # 3. Summary erstellen
        summary = create_summary(dist_results, anomalies)
        assert isinstance(summary, DistributionSummary)

        # 4. Near-Miss Analyse
        near_miss = analyze_all_near_miss(sample_gq_data)
        assert len(near_miss) > 0

        # 5. Signifikante zaehlen
        sig_count = count_significant_anomalies(near_miss)
        assert sig_count >= 0


class TestPayoutRatioAnalysis:
    """Tests fuer DIST-002: Auszahlung-Gewinner Ratio Analyse."""

    def test_analyze_payout_ratio_returns_results(self, sample_gq_data: pd.DataFrame):
        """Test DIST-002-1: analyze_payout_ratio gibt Liste von PayoutRatioResult zurueck."""
        results = analyze_payout_ratio(sample_gq_data)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, PayoutRatioResult) for r in results)

    def test_analyze_payout_ratio_calculates_correctly(self, sample_gq_data: pd.DataFrame):
        """Test DIST-002-2: payout_per_winner wird korrekt berechnet."""
        results = analyze_payout_ratio(sample_gq_data, keno_type=2, matches=2)

        # Keno-Typ 2/2 hat Quote 6, also sollte mean_payout_per_winner ~6 sein
        assert len(results) == 1
        result = results[0]

        # Bei festen Quoten sollte mean_payout_per_winner = Quote
        assert 5.5 <= result.mean_payout_per_winner <= 6.5
        # CV sollte sehr niedrig sein bei konstanter Quote
        assert result.cv < 0.1

    def test_analyze_payout_ratio_handles_zero_winners(self, sample_gq_data: pd.DataFrame):
        """Test DIST-002-3: Division by zero bei Gewinner=0 wird korrekt behandelt."""
        results = analyze_payout_ratio(sample_gq_data, keno_type=10, matches=10)

        # Keno 10/10 hat viele 0-Gewinner Ziehungen
        if len(results) > 0:
            result = results[0]
            assert result.zero_winner_draws >= 0
            # n_draws sollte nur Ziehungen MIT Gewinnern zaehlen
            assert result.n_draws >= 0

    def test_analyze_payout_ratio_filter_by_keno_type(self, sample_gq_data: pd.DataFrame):
        """Test DIST-002-4: Filterung nach Keno-Typ funktioniert."""
        results_all = analyze_payout_ratio(sample_gq_data)
        results_type2 = analyze_payout_ratio(sample_gq_data, keno_type=2)

        # Gefilterte Ergebnisse sollten nur Typ 2 enthalten
        assert all(r.keno_type == 2 for r in results_type2)
        # und weniger sein als alle
        assert len(results_type2) <= len(results_all)

    def test_detect_payout_ratio_anomalies_high_cv(self):
        """Test DIST-002-5: Hoher CV wird als Anomalie erkannt."""
        results = [
            PayoutRatioResult(
                keno_type=10,
                matches=9,
                mean_payout_per_winner=10000.0,
                std_payout_per_winner=2000.0,  # CV = 0.2 > 0.1
                cv=0.2,
                min_payout_per_winner=8000.0,
                max_payout_per_winner=12000.0,
                n_draws=50,
                zero_winner_draws=5,
            ),
        ]

        anomalies = detect_payout_ratio_anomalies(results, cv_threshold=0.1)

        assert len(anomalies) == 1
        assert anomalies[0][0] == 10  # keno_type
        assert anomalies[0][1] == 9   # matches
        assert "cv" in anomalies[0][2].lower()

    def test_detect_payout_ratio_anomalies_no_anomalies(self):
        """Test DIST-002-6: Keine Anomalien bei konstanter Quote."""
        results = [
            PayoutRatioResult(
                keno_type=2,
                matches=2,
                mean_payout_per_winner=6.0,  # Konstante Quote
                std_payout_per_winner=0.0,
                cv=0.0,
                min_payout_per_winner=6.0,
                max_payout_per_winner=6.0,
                n_draws=50,
                zero_winner_draws=0,
            ),
        ]

        anomalies = detect_payout_ratio_anomalies(results)

        assert len(anomalies) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
