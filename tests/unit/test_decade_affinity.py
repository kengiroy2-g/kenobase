"""Unit tests for kenobase.analysis.decade_affinity module (HYP-005)."""

from __future__ import annotations

from datetime import datetime

import pytest

from kenobase.analysis.decade_affinity import (
    DECADES,
    NUM_DECADES,
    DecadeAffinityResult,
    analyze_decade_affinity,
    calculate_expected_pair_frequency,
    chi_square_test_single_pair,
    count_decade_occurrences,
    decade_pair_to_name,
    generate_affinity_report,
    get_anti_affinity_pairs,
    get_decade,
    get_top_affinity_pairs,
    run_hyp005_analysis,
)
from kenobase.core.data_loader import DrawResult, GameType


class TestDecadeConstants:
    """Tests for decade constants."""

    def test_num_decades(self):
        """Should have 7 decades for KENO."""
        assert NUM_DECADES == 7

    def test_decades_coverage(self):
        """Decades should cover 1-70."""
        all_numbers = set()
        for decade_range in DECADES.values():
            all_numbers.update(decade_range)

        assert all_numbers == set(range(1, 71))

    def test_decades_non_overlapping(self):
        """Decades should not overlap."""
        for i, range_i in DECADES.items():
            for j, range_j in DECADES.items():
                if i != j:
                    assert set(range_i).isdisjoint(set(range_j))


class TestGetDecade:
    """Tests for get_decade function."""

    def test_decade_0(self):
        """Numbers 1-10 should be decade 0."""
        for n in range(1, 11):
            assert get_decade(n) == 0

    def test_decade_1(self):
        """Numbers 11-20 should be decade 1."""
        for n in range(11, 21):
            assert get_decade(n) == 1

    def test_decade_6(self):
        """Numbers 61-70 should be decade 6."""
        for n in range(61, 71):
            assert get_decade(n) == 6

    def test_boundary_values(self):
        """Test boundary values."""
        assert get_decade(1) == 0
        assert get_decade(10) == 0
        assert get_decade(11) == 1
        assert get_decade(70) == 6

    def test_invalid_number_low(self):
        """Should raise ValueError for numbers < 1."""
        with pytest.raises(ValueError):
            get_decade(0)

    def test_invalid_number_high(self):
        """Should raise ValueError for numbers > 70."""
        with pytest.raises(ValueError):
            get_decade(71)


class TestCountDecadeOccurrences:
    """Tests for count_decade_occurrences function."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Create sample draws for testing."""
        return [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 5, 11, 15, 21, 25, 31, 35, 41, 45, 51, 55, 61, 65, 2, 3, 4, 6, 7, 8],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=[1, 11, 21, 31, 41, 51, 61, 2, 12, 22, 32, 42, 52, 62, 3, 13, 23, 33, 43, 53],
                game_type=GameType.KENO,
            ),
        ]

    def test_empty_draws(self):
        """Empty draws should return empty counters."""
        single, pairs = count_decade_occurrences([])
        assert len(single) == 0
        assert len(pairs) == 0

    def test_single_counts(self, sample_draws):
        """Single decade counts should be calculated correctly."""
        single, _ = count_decade_occurrences(sample_draws)

        # All decades appear in both draws
        for decade in range(NUM_DECADES):
            assert single[decade] == 2

    def test_pair_counts(self, sample_draws):
        """Pair counts should be calculated correctly."""
        _, pairs = count_decade_occurrences(sample_draws)

        # Since all decades appear in both draws, all pairs should have count 2
        for decade_a in range(NUM_DECADES):
            for decade_b in range(decade_a + 1, NUM_DECADES):
                assert pairs[(decade_a, decade_b)] == 2


class TestCalculateExpectedPairFrequency:
    """Tests for expected pair frequency calculation."""

    def test_zero_draws(self):
        """Zero draws should return 0."""
        from collections import Counter
        result = calculate_expected_pair_frequency(Counter(), 0, 0, 1)
        assert result == 0.0

    def test_perfect_independence(self):
        """Expected = N * P(A) * P(B)."""
        from collections import Counter

        # If decade 0 appears in 50% of draws and decade 1 in 50% of draws
        # Expected pair frequency = 100 * 0.5 * 0.5 = 25
        single = Counter({0: 50, 1: 50})
        result = calculate_expected_pair_frequency(single, 100, 0, 1)
        assert result == pytest.approx(25.0)

    def test_different_frequencies(self):
        """Test with different single frequencies."""
        from collections import Counter

        # Decade 0: 80%, Decade 1: 40%
        # Expected = 100 * 0.8 * 0.4 = 32
        single = Counter({0: 80, 1: 40})
        result = calculate_expected_pair_frequency(single, 100, 0, 1)
        assert result == pytest.approx(32.0)


class TestChiSquareTestSinglePair:
    """Tests for Chi-square test."""

    def test_expected_equals_observed(self):
        """No difference should give p close to 1."""
        chi2, p_value = chi_square_test_single_pair(100, 100.0)
        assert chi2 == pytest.approx(0.0)
        assert p_value == pytest.approx(1.0)

    def test_large_deviation(self):
        """Large deviation should give low p-value."""
        # Observed 200, expected 100 -> strong deviation
        chi2, p_value = chi_square_test_single_pair(200, 100.0)
        assert chi2 > 0
        assert p_value < 0.05

    def test_small_expected(self):
        """Small expected values should return p=1."""
        chi2, p_value = chi_square_test_single_pair(10, 3.0)
        assert chi2 == 0.0
        assert p_value == 1.0


class TestAnalyzeDecadeAffinity:
    """Tests for main analysis function."""

    @pytest.fixture
    def many_draws(self) -> list[DrawResult]:
        """Create many draws for testing."""
        import random
        random.seed(42)

        draws = []
        for i in range(100):
            numbers = sorted(random.sample(range(1, 71), 20))
            draws.append(
                DrawResult(
                    date=datetime(2024, 1, i % 28 + 1, hour=i // 28),
                    numbers=numbers,
                    game_type=GameType.KENO,
                )
            )
        return draws

    def test_empty_draws(self):
        """Empty draws should return empty list."""
        result = analyze_decade_affinity([])
        assert result == []

    def test_result_count(self, many_draws):
        """Should return 21 pairs (7 choose 2)."""
        result = analyze_decade_affinity(many_draws)
        assert len(result) == 21  # C(7,2) = 21

    def test_result_structure(self, many_draws):
        """Each result should have correct structure."""
        results = analyze_decade_affinity(many_draws)

        for r in results:
            assert isinstance(r, DecadeAffinityResult)
            assert isinstance(r.pair, tuple)
            assert len(r.pair) == 2
            assert 0 <= r.pair[0] < NUM_DECADES
            assert 0 <= r.pair[1] < NUM_DECADES
            assert r.pair[0] < r.pair[1]
            assert r.observed >= 0
            assert r.expected >= 0
            assert 0 <= r.p_value <= 1
            assert isinstance(r.is_significant, bool)

    def test_sorted_by_affinity_score(self, many_draws):
        """Results should be sorted by affinity score descending."""
        results = analyze_decade_affinity(many_draws)

        for i in range(len(results) - 1):
            assert results[i].affinity_score >= results[i + 1].affinity_score


class TestGetTopAffinityPairs:
    """Tests for top pairs functions."""

    @pytest.fixture
    def sample_results(self) -> list[DecadeAffinityResult]:
        """Create sample results."""
        return [
            DecadeAffinityResult((0, 1), 100, 80.0, 0.25, 0.01, True),
            DecadeAffinityResult((0, 2), 90, 85.0, 0.06, 0.20, False),
            DecadeAffinityResult((1, 2), 60, 70.0, -0.14, 0.30, False),
            DecadeAffinityResult((2, 3), 50, 75.0, -0.33, 0.02, True),
            DecadeAffinityResult((3, 4), 40, 80.0, -0.50, 0.001, True),
        ]

    def test_top_n(self, sample_results):
        """Should return top N pairs."""
        top = get_top_affinity_pairs(sample_results, n=2)
        assert len(top) == 2
        assert top[0].pair == (0, 1)
        assert top[1].pair == (0, 2)

    def test_only_significant(self, sample_results):
        """Should filter to only significant pairs."""
        top = get_top_affinity_pairs(sample_results, n=5, only_significant=True)
        assert len(top) == 3  # Only 3 are significant
        assert all(r.is_significant for r in top)


class TestGetAntiAffinityPairs:
    """Tests for anti-affinity pairs."""

    @pytest.fixture
    def sample_results(self) -> list[DecadeAffinityResult]:
        """Create sample results."""
        return [
            DecadeAffinityResult((0, 1), 100, 80.0, 0.25, 0.01, True),
            DecadeAffinityResult((2, 3), 50, 75.0, -0.33, 0.02, True),
            DecadeAffinityResult((3, 4), 40, 80.0, -0.50, 0.001, True),
        ]

    def test_anti_pairs(self, sample_results):
        """Should return pairs with lowest affinity."""
        anti = get_anti_affinity_pairs(sample_results, n=2)
        assert len(anti) == 2
        assert anti[0].pair == (3, 4)  # Lowest affinity
        assert anti[1].pair == (2, 3)


class TestDecadePairToName:
    """Tests for decade pair naming."""

    def test_pair_0_1(self):
        """Test naming for pair (0, 1)."""
        name = decade_pair_to_name((0, 1))
        assert name == "(1-10, 11-20)"

    def test_pair_5_6(self):
        """Test naming for pair (5, 6)."""
        name = decade_pair_to_name((5, 6))
        assert name == "(51-60, 61-70)"


class TestGenerateAffinityReport:
    """Tests for report generation."""

    def test_report_content(self):
        """Report should contain key information."""
        results = [
            DecadeAffinityResult((0, 1), 100, 80.0, 0.25, 0.01, True),
            DecadeAffinityResult((2, 3), 50, 75.0, -0.33, 0.02, True),
        ]

        report = generate_affinity_report(results, n_draws=100)

        assert "HYP-005" in report
        assert "Zehnergruppen" in report
        assert "100" in report  # n_draws
        assert "Affinitaets-Paare" in report


class TestRunHyp005Analysis:
    """Tests for complete analysis function."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Create sample draws."""
        import random
        random.seed(42)

        return [
            DrawResult(
                date=datetime(2024, 1, i % 28 + 1),
                numbers=sorted(random.sample(range(1, 71), 20)),
                game_type=GameType.KENO,
            )
            for i in range(50)
        ]

    def test_result_structure(self, sample_draws):
        """Should return correct structure."""
        result = run_hyp005_analysis(sample_draws)

        assert "results" in result
        assert "top_pairs" in result
        assert "anti_pairs" in result
        assert "summary" in result

    def test_summary_keys(self, sample_draws):
        """Summary should contain expected keys."""
        result = run_hyp005_analysis(sample_draws)
        summary = result["summary"]

        expected_keys = [
            "n_draws",
            "n_pairs_total",
            "n_pairs_significant",
            "alpha",
            "mean_affinity_score",
            "std_affinity_score",
            "max_affinity_score",
            "min_affinity_score",
        ]

        for key in expected_keys:
            assert key in summary

    def test_top_pairs_count(self, sample_draws):
        """Should return 5 top pairs."""
        result = run_hyp005_analysis(sample_draws)
        assert len(result["top_pairs"]) == 5

    def test_anti_pairs_count(self, sample_draws):
        """Should return 5 anti pairs."""
        result = run_hyp005_analysis(sample_draws)
        assert len(result["anti_pairs"]) == 5
