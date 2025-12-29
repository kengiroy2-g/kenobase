"""Unit tests for kenobase.analysis.jackpot_correlation module (HYP-015).

Tests the jackpot-number type correlation analysis functionality.
"""

from datetime import datetime
from unittest.mock import MagicMock

import numpy as np
import pytest

from kenobase.analysis.jackpot_correlation import (
    BIRTHDAY_MAX,
    BIRTHDAY_MIN,
    DECADES,
    HIGH_MAX,
    HIGH_MIN,
    GK1Event,
    JackpotAnalysisSummary,
    JackpotCorrelationResult,
    NumberTypeStats,
    analyze_jackpot_correlation,
    calculate_draw_type_features,
    calculate_number_type_stats,
    calculate_type_ratios,
    chi_square_test,
    classify_number_type,
    get_decade,
    get_jackpot_dates,
    load_gk1_events,
)


class MockDrawResult:
    """Mock DrawResult for testing."""

    def __init__(self, date: datetime, numbers: list[int]):
        self.date = date
        self.numbers = sorted(numbers)


class TestConstants:
    """Test module constants."""

    def test_birthday_range(self):
        """Birthday numbers should be 1-31."""
        assert BIRTHDAY_MIN == 1
        assert BIRTHDAY_MAX == 31

    def test_high_range(self):
        """High numbers should be 32-70."""
        assert HIGH_MIN == 32
        assert HIGH_MAX == 70

    def test_decades_coverage(self):
        """Decades should cover all KENO numbers 1-70."""
        assert len(DECADES) == 7
        all_numbers = set()
        for low, high in DECADES:
            for n in range(max(1, low), high + 1):
                all_numbers.add(n)
        assert all_numbers == set(range(1, 71))


class TestClassifyNumberType:
    """Test classify_number_type function."""

    def test_birthday_number(self):
        """Numbers 1-31 should be classified as birthday."""
        result = classify_number_type(15)
        assert result["birthday"] is True
        assert result["high"] is False

    def test_high_number(self):
        """Numbers 32-70 should be classified as high."""
        result = classify_number_type(50)
        assert result["birthday"] is False
        assert result["high"] is True

    def test_boundary_31(self):
        """31 is the last birthday number."""
        result = classify_number_type(31)
        assert result["birthday"] is True
        assert result["high"] is False

    def test_boundary_32(self):
        """32 is the first high number."""
        result = classify_number_type(32)
        assert result["birthday"] is False
        assert result["high"] is True

    def test_even_odd(self):
        """Even/odd classification."""
        even_result = classify_number_type(10)
        assert even_result["even"] is True
        assert even_result["odd"] is False

        odd_result = classify_number_type(11)
        assert odd_result["even"] is False
        assert odd_result["odd"] is True


class TestGetDecade:
    """Test get_decade function."""

    def test_first_decade(self):
        """Numbers 1-9 are decade 0."""
        assert get_decade(1) == 0
        assert get_decade(9) == 0

    def test_second_decade(self):
        """Numbers 10-19 are decade 1."""
        assert get_decade(10) == 1
        assert get_decade(19) == 1

    def test_last_decade(self):
        """Numbers 60-70 are decade 6."""
        assert get_decade(60) == 6
        assert get_decade(70) == 6


class TestGetJackpotDates:
    """Test get_jackpot_dates function."""

    def test_extracts_unique_dates(self):
        """Should extract unique dates from GK1 events."""
        events = [
            GK1Event(
                datum=datetime(2022, 1, 31, 10, 0),
                keno_typ=10,
                anzahl_gewinner=10,
                vergangene_tage=0,
            ),
            GK1Event(
                datum=datetime(2022, 1, 31, 15, 0),  # Same day, different time
                keno_typ=9,
                anzahl_gewinner=5,
                vergangene_tage=0,
            ),
            GK1Event(
                datum=datetime(2022, 2, 19),
                keno_typ=9,
                anzahl_gewinner=2,
                vergangene_tage=19,
            ),
        ]

        dates = get_jackpot_dates(events)

        # Should have 2 unique dates (Jan 31 and Feb 19)
        assert len(dates) == 2
        assert datetime(2022, 1, 31) in dates
        assert datetime(2022, 2, 19) in dates

    def test_empty_events(self):
        """Empty events should return empty set."""
        dates = get_jackpot_dates([])
        assert len(dates) == 0


class TestCalculateTypeRatios:
    """Test calculate_type_ratios function."""

    def test_all_birthday_numbers(self):
        """All birthday numbers should give ratio 1.0."""
        draws = [
            MockDrawResult(datetime(2022, 1, 1), list(range(1, 21))),  # 1-20
        ]

        ratios = calculate_type_ratios(draws)

        assert ratios["birthday"] == 1.0
        # "high" key not present when no high numbers exist
        assert ratios.get("high", 0.0) == 0.0

    def test_all_high_numbers(self):
        """All high numbers should give ratio 1.0."""
        draws = [
            MockDrawResult(datetime(2022, 1, 1), list(range(51, 71))),  # 51-70
        ]

        ratios = calculate_type_ratios(draws)

        # "birthday" key not present when no birthday numbers exist
        assert ratios.get("birthday", 0.0) == 0.0
        assert ratios["high"] == 1.0

    def test_mixed_numbers(self):
        """Mixed numbers should give proportional ratios."""
        # 10 birthday (1-10) + 10 high (61-70)
        draws = [
            MockDrawResult(datetime(2022, 1, 1), list(range(1, 11)) + list(range(61, 71))),
        ]

        ratios = calculate_type_ratios(draws)

        assert ratios["birthday"] == 0.5
        assert ratios["high"] == 0.5

    def test_empty_draws(self):
        """Empty draws should return empty dict."""
        ratios = calculate_type_ratios([])
        assert ratios == {}


class TestCalculateDrawTypeFeatures:
    """Test calculate_draw_type_features function."""

    def test_identifies_jackpot_draws(self):
        """Should correctly identify draws on jackpot dates."""
        jackpot_dates = {datetime(2022, 1, 31)}

        draws = [
            MockDrawResult(datetime(2022, 1, 31), list(range(1, 21))),  # Jackpot day
            MockDrawResult(datetime(2022, 2, 1), list(range(1, 21))),  # Normal day
        ]

        ratios, indicators = calculate_draw_type_features(draws, jackpot_dates)

        assert len(ratios) == 2
        assert len(indicators) == 2
        assert indicators[0] == 1  # First draw is jackpot
        assert indicators[1] == 0  # Second draw is normal

    def test_calculates_birthday_ratio(self):
        """Should calculate correct birthday ratio per draw."""
        jackpot_dates = set()

        # 10 birthday numbers out of 20
        draws = [
            MockDrawResult(
                datetime(2022, 1, 1),
                list(range(1, 11)) + list(range(61, 71)),  # 10 birthday + 10 high
            ),
        ]

        ratios, _ = calculate_draw_type_features(draws, jackpot_dates)

        assert len(ratios) == 1
        assert ratios[0] == 0.5  # 10/20 = 0.5


class TestChiSquareTest:
    """Test chi_square_test function."""

    def test_identical_distributions(self):
        """Identical distributions should have high p-value."""
        # Same distribution in both groups
        jackpot = [MockDrawResult(datetime(2022, 1, i), list(range(1, 21))) for i in range(1, 11)]
        normal = [MockDrawResult(datetime(2022, 2, i), list(range(1, 21))) for i in range(1, 11)]

        chi2, p, dof = chi_square_test(jackpot, normal)

        # Identical distributions should have chi2 close to 0, p close to 1
        assert p > 0.05

    def test_different_distributions(self):
        """Very different distributions should have low p-value."""
        # Jackpot: all birthday numbers (use valid dates: 1-28)
        jackpot = [
            MockDrawResult(datetime(2022, 1, i), list(range(1, 21)))
            for i in range(1, 29)
        ]
        # Normal: all high numbers (use valid dates: 1-28)
        normal = [
            MockDrawResult(datetime(2022, 2, i), list(range(51, 71)))
            for i in range(1, 29)
        ]

        chi2, p, dof = chi_square_test(jackpot, normal)

        # Very different distributions should have significant chi2
        assert chi2 > 0
        assert p < 0.05

    def test_empty_groups(self):
        """Empty groups should return default values."""
        chi2, p, dof = chi_square_test([], [])

        assert chi2 == 0.0
        assert p == 1.0
        assert dof == 1


class TestAnalyzeJackpotCorrelation:
    """Test analyze_jackpot_correlation function."""

    def test_returns_result_type(self):
        """Should return JackpotCorrelationResult."""
        draws = [
            MockDrawResult(datetime(2022, 1, 31), list(range(1, 21))),
        ]
        jackpot_dates = {datetime(2022, 1, 31)}

        result = analyze_jackpot_correlation(draws, jackpot_dates)

        assert isinstance(result, JackpotCorrelationResult)

    def test_counts_draws_correctly(self):
        """Should count jackpot and normal draws correctly."""
        draws = [
            MockDrawResult(datetime(2022, 1, 31), list(range(1, 21))),
            MockDrawResult(datetime(2022, 2, 1), list(range(1, 21))),
            MockDrawResult(datetime(2022, 2, 2), list(range(1, 21))),
        ]
        jackpot_dates = {datetime(2022, 1, 31)}

        result = analyze_jackpot_correlation(draws, jackpot_dates)

        assert result.n_jackpot_draws == 1
        assert result.n_normal_draws == 2
        assert result.n_total_draws == 3

    def test_empty_inputs(self):
        """Empty inputs should return default result."""
        result = analyze_jackpot_correlation([], set())

        assert result.is_significant is False
        assert result.n_jackpot_draws == 0
        assert result.n_normal_draws == 0


class TestCalculateNumberTypeStats:
    """Test calculate_number_type_stats function."""

    def test_returns_stats_list(self):
        """Should return list of NumberTypeStats."""
        jackpot = [MockDrawResult(datetime(2022, 1, 1), list(range(1, 21)))]
        normal = [MockDrawResult(datetime(2022, 2, 1), list(range(1, 21)))]

        stats = calculate_number_type_stats(jackpot, normal)

        assert isinstance(stats, list)
        assert all(isinstance(s, NumberTypeStats) for s in stats)

    def test_includes_all_categories(self):
        """Should include birthday, even, odd, and decade categories."""
        # Use mixed numbers to get both birthday and high categories
        mixed_numbers = list(range(1, 11)) + list(range(51, 61))  # 10 birthday + 10 high
        jackpot = [MockDrawResult(datetime(2022, 1, 1), mixed_numbers)]
        normal = [MockDrawResult(datetime(2022, 2, 1), mixed_numbers)]

        stats = calculate_number_type_stats(jackpot, normal)
        categories = {s.category for s in stats}

        assert "birthday" in categories
        assert "high" in categories
        assert "even" in categories
        assert "odd" in categories


class TestLoadGk1Events:
    """Test load_gk1_events function."""

    def test_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_gk1_events(tmp_path / "nonexistent.csv")

    def test_loads_valid_csv(self, tmp_path):
        """Should load valid GK1 CSV file."""
        csv_content = """Datum,Keno-Typ,Anzahl der Gewinner,Vergangene Tage seit dem letzten Gewinnklasse 1
31.01.2022,10,10.0,0
19.02.2022,9,2.0,19
"""
        csv_file = tmp_path / "test_gk1.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        events = load_gk1_events(csv_file)

        assert len(events) == 2
        assert events[0].keno_typ == 10
        assert events[0].anzahl_gewinner == 10
        assert events[1].keno_typ == 9
        assert events[1].vergangene_tage == 19


class TestGK1Event:
    """Test GK1Event dataclass."""

    def test_creation(self):
        """Should create GK1Event with all fields."""
        event = GK1Event(
            datum=datetime(2022, 1, 31),
            keno_typ=10,
            anzahl_gewinner=10,
            vergangene_tage=0,
        )

        assert event.datum == datetime(2022, 1, 31)
        assert event.keno_typ == 10
        assert event.anzahl_gewinner == 10
        assert event.vergangene_tage == 0


class TestJackpotCorrelationResult:
    """Test JackpotCorrelationResult dataclass."""

    def test_creation(self):
        """Should create result with all fields."""
        result = JackpotCorrelationResult(
            pearson_r=0.15,
            pearson_p=0.03,
            spearman_r=0.12,
            spearman_p=0.05,
            chi_square_stat=5.2,
            chi_square_p=0.02,
            chi_square_dof=1,
            is_significant=True,
            n_jackpot_draws=20,
            n_normal_draws=1000,
            n_total_draws=1020,
        )

        assert result.pearson_r == 0.15
        assert result.is_significant is True


class TestNumberTypeStats:
    """Test NumberTypeStats dataclass."""

    def test_creation(self):
        """Should create stats with all fields."""
        stats = NumberTypeStats(
            category="birthday",
            jackpot_ratio=0.45,
            normal_ratio=0.44,
            difference=0.01,
            z_score=0.5,
        )

        assert stats.category == "birthday"
        assert stats.difference == 0.01
