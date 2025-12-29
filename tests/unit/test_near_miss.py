"""Unit tests for kenobase.analysis.near_miss module (HYP-001)."""

from __future__ import annotations

import pytest
import pandas as pd
import numpy as np
import math

from kenobase.analysis.near_miss import (
    NearMissResult,
    KENO_PROBABILITIES,
    calculate_expected_ratio,
    analyze_near_miss,
    analyze_all_near_miss,
    count_significant_anomalies,
)


class TestKenoProbabilities:
    """Tests for KENO_PROBABILITIES constants."""

    def test_keno_types_coverage(self):
        """Should cover Keno-Typ 2-10."""
        expected_types = set(range(2, 11))
        actual_types = set(KENO_PROBABILITIES.keys())
        assert actual_types == expected_types

    def test_probabilities_sum_reasonable(self):
        """Each Keno-Typ probabilities should sum to ~1.0."""
        for keno_type, probs in KENO_PROBABILITIES.items():
            total = sum(probs.values())
            assert total == pytest.approx(1.0, abs=1e-12)

    def test_max_matches_exists(self):
        """Each Keno-Typ should have max_matches = keno_type."""
        for keno_type, probs in KENO_PROBABILITIES.items():
            assert keno_type in probs, f"Keno-Typ {keno_type} missing max_matches"

    def test_near_miss_matches_exists(self):
        """Each Keno-Typ should have near_miss_matches = keno_type - 1."""
        for keno_type, probs in KENO_PROBABILITIES.items():
            near_miss = keno_type - 1
            assert near_miss in probs, f"Keno-Typ {keno_type} missing near_miss {near_miss}"


class TestCalculateExpectedRatio:
    """Tests for calculate_expected_ratio function."""

    def test_keno_type_2(self):
        """Keno-Typ 2: expected ratio P(1)/P(2) (hypergeometric)."""
        result = calculate_expected_ratio(2)

        def p(k: int, m: int) -> float:
            return math.comb(k, m) * math.comb(70 - k, 20 - m) / math.comb(70, 20)

        expected = p(2, 1) / p(2, 2)
        assert result == pytest.approx(expected, rel=0.01)

    def test_keno_type_10(self):
        """Keno-Typ 10: expected ratio P(9)/P(10) (hypergeometric)."""
        result = calculate_expected_ratio(10)

        def p(k: int, m: int) -> float:
            return math.comb(k, m) * math.comb(70 - k, 20 - m) / math.comb(70, 20)

        expected = p(10, 9) / p(10, 10)
        assert result == pytest.approx(expected, rel=0.01)

    def test_invalid_keno_type_returns_1(self):
        """Invalid Keno-Typ should return 1.0."""
        assert calculate_expected_ratio(1) == 1.0
        assert calculate_expected_ratio(11) == 1.0
        assert calculate_expected_ratio(0) == 1.0

    def test_all_keno_types_positive_ratio(self):
        """All valid Keno-Typen should have positive ratio."""
        for keno_type in range(2, 11):
            ratio = calculate_expected_ratio(keno_type)
            assert ratio > 0, f"Keno-Typ {keno_type} has non-positive ratio"

    def test_near_miss_more_likely_than_max(self):
        """Near-Miss should generally be more likely than max."""
        for keno_type in range(2, 11):
            ratio = calculate_expected_ratio(keno_type)
            assert ratio > 1.0, f"Keno-Typ {keno_type}: expected near-miss > max"


class TestNearMissResult:
    """Tests for NearMissResult dataclass."""

    def test_dataclass_creation(self):
        """Should create NearMissResult correctly."""
        result = NearMissResult(
            keno_type=5,
            max_matches=5,
            near_miss_matches=4,
            near_miss_ratio=6.5,
            expected_ratio=6.0,
            chi2_stat=1.5,
            p_value=0.22,
            is_significant=False,
            n_draws=100,
        )
        assert result.keno_type == 5
        assert result.max_matches == 5
        assert result.near_miss_matches == 4
        assert result.near_miss_ratio == 6.5
        assert result.expected_ratio == 6.0
        assert result.chi2_stat == 1.5
        assert result.p_value == 0.22
        assert result.is_significant is False
        assert result.n_draws == 100

    def test_significant_when_p_low(self):
        """is_significant should be True when p < 0.05."""
        result = NearMissResult(
            keno_type=5,
            max_matches=5,
            near_miss_matches=4,
            near_miss_ratio=10.0,
            expected_ratio=6.0,
            chi2_stat=15.0,
            p_value=0.001,
            is_significant=True,
            n_draws=100,
        )
        assert result.is_significant is True


class TestAnalyzeNearMiss:
    """Tests for analyze_near_miss function."""

    @pytest.fixture
    def sample_gq_data(self) -> pd.DataFrame:
        """Create sample GQ data for testing."""
        # Simulate GQ data with Keno-Typ, Datum, Anzahl richtiger Zahlen, Anzahl der Gewinner
        data = []
        for i in range(100):
            date = f"2024-01-{(i % 28) + 1:02d}"
            for keno_type in [5]:
                # Add max winners (5 matches)
                data.append({
                    "Datum": date,
                    "Keno-Typ": keno_type,
                    "Anzahl richtiger Zahlen": 5,
                    "Anzahl der Gewinner": 10,
                })
                # Add near-miss winners (4 matches)
                data.append({
                    "Datum": date,
                    "Keno-Typ": keno_type,
                    "Anzahl richtiger Zahlen": 4,
                    "Anzahl der Gewinner": 60,  # ~6x more than max
                })
                # Add other match levels
                for matches in [0, 1, 2, 3]:
                    data.append({
                        "Datum": date,
                        "Keno-Typ": keno_type,
                        "Anzahl richtiger Zahlen": matches,
                        "Anzahl der Gewinner": 100 + matches * 50,
                    })
        return pd.DataFrame(data)

    def test_analyze_keno_type_5(self, sample_gq_data):
        """Should analyze Keno-Typ 5 correctly."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        assert isinstance(result, NearMissResult)
        assert result.keno_type == 5
        assert result.max_matches == 5
        assert result.near_miss_matches == 4

    def test_near_miss_ratio_calculated(self, sample_gq_data):
        """near_miss_ratio should be near_winners / max_winners."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        # Based on fixture: 60 near-miss winners, 10 max winners per draw
        # 100 draws * 60 = 6000 near-miss, 100 * 10 = 1000 max
        expected_ratio = 6000 / 1000  # = 6.0
        assert result.near_miss_ratio == pytest.approx(expected_ratio, rel=0.01)

    def test_expected_ratio_set(self, sample_gq_data):
        """expected_ratio should be from KENO_PROBABILITIES."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        expected = calculate_expected_ratio(5)
        assert result.expected_ratio == pytest.approx(expected, rel=0.01)

    def test_n_draws_counted(self, sample_gq_data):
        """n_draws should count unique dates."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        # 100 draws but only 28 unique dates in fixture
        assert result.n_draws <= 100

    def test_chi2_stat_calculated(self, sample_gq_data):
        """chi2_stat should be calculated."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        assert result.chi2_stat >= 0

    def test_p_value_in_range(self, sample_gq_data):
        """p_value should be between 0 and 1."""
        result = analyze_near_miss(sample_gq_data, keno_type=5)

        assert 0 <= result.p_value <= 1

    def test_empty_keno_type(self):
        """Should handle missing Keno-Typ gracefully."""
        df = pd.DataFrame({
            "Datum": ["2024-01-01"],
            "Keno-Typ": [3],
            "Anzahl richtiger Zahlen": [3],
            "Anzahl der Gewinner": [100],
        })

        result = analyze_near_miss(df, keno_type=5)

        # Should return 0 n_draws
        assert result.n_draws == 0

    def test_no_max_winners(self):
        """Should handle zero max winners."""
        df = pd.DataFrame({
            "Datum": ["2024-01-01", "2024-01-01"],
            "Keno-Typ": [5, 5],
            "Anzahl richtiger Zahlen": [4, 3],  # No max (5)
            "Anzahl der Gewinner": [100, 200],
        })

        result = analyze_near_miss(df, keno_type=5)

        assert result.near_miss_ratio == 0.0
        assert result.p_value == 1.0


class TestAnalyzeAllNearMiss:
    """Tests for analyze_all_near_miss function."""

    @pytest.fixture
    def multi_keno_data(self) -> pd.DataFrame:
        """Create multi-Keno-Typ data."""
        data = []
        for i in range(50):
            date = f"2024-01-{(i % 28) + 1:02d}"
            for keno_type in range(2, 11):
                for matches in range(keno_type + 1):
                    data.append({
                        "Datum": date,
                        "Keno-Typ": keno_type,
                        "Anzahl richtiger Zahlen": matches,
                        "Anzahl der Gewinner": 100 * (keno_type - matches + 1),
                    })
        return pd.DataFrame(data)

    def test_returns_list(self, multi_keno_data):
        """Should return list of NearMissResult."""
        results = analyze_all_near_miss(multi_keno_data)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, NearMissResult) for r in results)

    def test_all_keno_types_analyzed(self, multi_keno_data):
        """Should analyze all available Keno-Typen."""
        results = analyze_all_near_miss(multi_keno_data)

        keno_types_analyzed = {r.keno_type for r in results}
        expected_types = set(range(2, 11))
        assert keno_types_analyzed == expected_types

    def test_empty_dataframe(self):
        """Should handle empty DataFrame."""
        df = pd.DataFrame({
            "Datum": [],
            "Keno-Typ": [],
            "Anzahl richtiger Zahlen": [],
            "Anzahl der Gewinner": [],
        })
        # Add column types
        df["Keno-Typ"] = df["Keno-Typ"].astype(int)

        results = analyze_all_near_miss(df)

        assert results == []


class TestCountSignificantAnomalies:
    """Tests for count_significant_anomalies function."""

    def test_empty_list(self):
        """Empty list should return 0."""
        assert count_significant_anomalies([]) == 0

    def test_no_significant(self):
        """No significant results should return 0."""
        results = [
            NearMissResult(5, 5, 4, 6.0, 6.0, 0.1, 0.75, False, 100),
            NearMissResult(6, 6, 5, 6.0, 6.0, 0.2, 0.65, False, 100),
        ]
        assert count_significant_anomalies(results) == 0

    def test_all_significant(self):
        """All significant results should return count."""
        results = [
            NearMissResult(5, 5, 4, 10.0, 6.0, 15.0, 0.001, True, 100),
            NearMissResult(6, 6, 5, 12.0, 6.0, 20.0, 0.0001, True, 100),
        ]
        assert count_significant_anomalies(results) == 2

    def test_mixed_significance(self):
        """Mixed results should count only significant."""
        results = [
            NearMissResult(5, 5, 4, 10.0, 6.0, 15.0, 0.001, True, 100),
            NearMissResult(6, 6, 5, 6.0, 6.0, 0.2, 0.65, False, 100),
            NearMissResult(7, 7, 6, 15.0, 6.0, 25.0, 0.0001, True, 100),
            NearMissResult(8, 8, 7, 6.0, 6.0, 0.1, 0.80, False, 100),
        ]
        assert count_significant_anomalies(results) == 2


class TestChiSquareStatistic:
    """Tests for Chi-Square calculation edge cases."""

    def test_perfect_match_to_expected(self):
        """If observed matches expected, chi2 should be ~0."""
        # Create data where near_miss_ratio matches expected_ratio
        expected_ratio = calculate_expected_ratio(5)  # ~6.0

        data = []
        for i in range(100):
            date = f"2024-01-{(i % 28) + 1:02d}"
            # Set winners to match expected ratio
            max_winners = 100
            near_winners = int(max_winners * expected_ratio)
            data.extend([
                {"Datum": date, "Keno-Typ": 5, "Anzahl richtiger Zahlen": 5, "Anzahl der Gewinner": max_winners},
                {"Datum": date, "Keno-Typ": 5, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": near_winners},
            ])

        df = pd.DataFrame(data)
        result = analyze_near_miss(df, keno_type=5)

        # Chi2 should be small when observed ~= expected
        assert result.chi2_stat < 5.0  # Reasonable threshold
        assert result.p_value > 0.05  # Not significant

    def test_large_deviation_is_significant(self):
        """Large deviation from expected should be significant."""
        data = []
        for i in range(100):
            date = f"2024-01-{(i % 28) + 1:02d}"
            # Create 10x more near-misses than expected
            data.extend([
                {"Datum": date, "Keno-Typ": 5, "Anzahl richtiger Zahlen": 5, "Anzahl der Gewinner": 10},
                {"Datum": date, "Keno-Typ": 5, "Anzahl richtiger Zahlen": 4, "Anzahl der Gewinner": 600},
            ])

        df = pd.DataFrame(data)
        result = analyze_near_miss(df, keno_type=5)

        # Should be very significant
        assert result.is_significant is True
        assert result.p_value < 0.01
