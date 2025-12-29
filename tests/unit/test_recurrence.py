"""Unit-Tests fuer kenobase.analysis.recurrence.

Diese Tests verifizieren die HYP-006 Implementierung:
- Wiederholungsanalyse zwischen Ziehungen
- GK1-Korrelation
- Paar-Stabilitaet

Granularity: per-draw
Target Metric: pattern-predictability
"""

from datetime import datetime, timedelta

import pytest

from kenobase.analysis.recurrence import (
    GK1CorrelationResult,
    PairStabilityResult,
    RecurrenceResult,
    RecurrenceDaysResult,
    WeeklyCycleResult,
    analyze_number_streaks,
    analyze_pair_stability,
    analyze_recurrence,
    analyze_recurrence_days,
    analyze_weekly_cycle,
    calculate_gk1_correlation,
    generate_recurrence_report,
)
from kenobase.core.data_loader import DrawResult, GameType


# ============================================================================
# Test Fixtures
# ============================================================================


def make_draw(date: datetime, numbers: list[int]) -> DrawResult:
    """Helper to create DrawResult objects."""
    return DrawResult(
        date=date,
        numbers=numbers,
        game_type=GameType.KENO,
    )


@pytest.fixture
def sequential_draws() -> list[DrawResult]:
    """Draws with known recurrence pattern."""
    base_date = datetime(2024, 1, 1)
    return [
        make_draw(base_date, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        make_draw(base_date + timedelta(days=1), [1, 2, 3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),  # 3 recurring
        make_draw(base_date + timedelta(days=2), [1, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]),  # 1 recurring
        make_draw(base_date + timedelta(days=3), [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 1, 2, 3, 4, 5, 6]),  # 0 from previous, but has 1
    ]


@pytest.fixture
def no_recurrence_draws() -> list[DrawResult]:
    """Draws with no recurrence."""
    base_date = datetime(2024, 1, 1)
    return [
        make_draw(base_date, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        make_draw(base_date + timedelta(days=1), [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]),
        make_draw(base_date + timedelta(days=2), [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]),
    ]


@pytest.fixture
def high_recurrence_draws() -> list[DrawResult]:
    """Draws with high recurrence (many overlapping numbers)."""
    base_date = datetime(2024, 1, 1)
    # Each draw shares 15 numbers with previous
    return [
        make_draw(base_date, list(range(1, 21))),  # 1-20
        make_draw(base_date + timedelta(days=1), list(range(6, 26))),  # 6-25 (15 recurring: 6-20)
        make_draw(base_date + timedelta(days=2), list(range(11, 31))),  # 11-30 (15 recurring: 11-25)
    ]


# ============================================================================
# Test: analyze_recurrence
# ============================================================================


class TestAnalyzeRecurrence:
    """Tests fuer analyze_recurrence Funktion."""

    def test_basic_recurrence_calculation(self, sequential_draws: list[DrawResult]) -> None:
        """Test basic recurrence rate calculation."""
        result = analyze_recurrence(sequential_draws, window=1)

        assert isinstance(result, RecurrenceResult)
        assert result.total_draws == 3  # 4 draws - 1 (first has no previous)
        # Draw 2: 3 recurring, Draw 3: 1 recurring, Draw 4: 1 recurring
        assert result.draws_with_recurrence == 3  # All have at least 1 recurrence
        assert result.recurrence_rate == 1.0  # All have recurrence

    def test_no_recurrence(self, no_recurrence_draws: list[DrawResult]) -> None:
        """Test with no recurrence between draws."""
        result = analyze_recurrence(no_recurrence_draws, window=1)

        assert result.total_draws == 2  # 3 draws - 1
        assert result.draws_with_recurrence == 0
        assert result.recurrence_rate == 0.0
        assert result.avg_recurrence_count == 0.0

    def test_high_recurrence(self, high_recurrence_draws: list[DrawResult]) -> None:
        """Test with high recurrence rate."""
        result = analyze_recurrence(high_recurrence_draws, window=1)

        assert result.total_draws == 2
        assert result.draws_with_recurrence == 2
        assert result.recurrence_rate == 1.0
        # 15 recurring per draw
        assert result.avg_recurrence_count == 15.0
        assert result.max_recurrence_count == 15

    def test_window_parameter(self, sequential_draws: list[DrawResult]) -> None:
        """Test window parameter affects lookback."""
        result_w1 = analyze_recurrence(sequential_draws, window=1)
        result_w2 = analyze_recurrence(sequential_draws, window=2)

        # With window=2, we look back 2 draws, so more potential recurrence
        assert result_w2.total_draws == 2  # 4 - 2
        assert result_w2.avg_recurrence_count >= result_w1.avg_recurrence_count

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        result = analyze_recurrence([], window=1)

        assert result.total_draws == 0
        assert result.recurrence_rate == 0.0

    def test_single_draw(self) -> None:
        """Test with single draw (insufficient for analysis)."""
        draws = [make_draw(datetime(2024, 1, 1), list(range(1, 21)))]
        result = analyze_recurrence(draws, window=1)

        # Single draw means 0 analyzable draws (need at least 2 for comparison)
        assert result.total_draws == 0
        assert result.draws_with_recurrence == 0
        assert result.recurrence_rate == 0.0

    def test_recurrence_by_number_tracking(self, high_recurrence_draws: list[DrawResult]) -> None:
        """Test that individual number recurrence is tracked."""
        result = analyze_recurrence(high_recurrence_draws, window=1)

        assert len(result.recurrence_by_number) > 0
        # Numbers 11-20 should appear in both recurrence checks
        for num in range(11, 21):
            assert num in result.recurrence_by_number

    def test_recurrence_percentage_property(self, sequential_draws: list[DrawResult]) -> None:
        """Test recurrence_percentage property."""
        result = analyze_recurrence(sequential_draws, window=1)

        assert result.recurrence_percentage == result.recurrence_rate * 100


# ============================================================================
# Test: analyze_pair_stability
# ============================================================================


class TestAnalyzePairStability:
    """Tests fuer analyze_pair_stability Funktion."""

    def test_pair_counting(self) -> None:
        """Test that pairs are counted correctly."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw(base_date + timedelta(days=1), [1, 2, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),
            make_draw(base_date + timedelta(days=2), [1, 2, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]),
        ]

        result = analyze_pair_stability(draws, min_occurrences=3, top_n=10)

        # Pair (1, 2) appears in all 3 draws
        assert (1, 2) in result.pair_frequencies
        assert result.pair_frequencies[(1, 2)] == 3

    def test_stable_pairs_filter(self) -> None:
        """Test that stable pairs are filtered by min_occurrences."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, [1, 2, 3, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]),
            make_draw(base_date + timedelta(days=1), [1, 2, 4, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]),
            make_draw(base_date + timedelta(days=2), [1, 2, 5, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]),
        ]

        result = analyze_pair_stability(draws, min_occurrences=3)

        # Only (1, 2) meets threshold
        stable_pair_tuples = [p for p, _ in result.stable_pairs]
        assert (1, 2) in stable_pair_tuples
        # Other pairs with 1 or 2 should not be stable
        assert (1, 3) not in stable_pair_tuples
        assert (1, 4) not in stable_pair_tuples

    def test_top_pairs_ordering(self) -> None:
        """Test that top_pairs are ordered by frequency."""
        base_date = datetime(2024, 1, 1)
        # Create draws where (1,2) appears 3x, (3,4) appears 2x
        draws = [
            make_draw(base_date, [1, 2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]),
            make_draw(base_date + timedelta(days=1), [1, 2, 3, 4, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]),
            make_draw(base_date + timedelta(days=2), [1, 2, 5, 6, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57]),
        ]

        result = analyze_pair_stability(draws, min_occurrences=2, top_n=10)

        # (1, 2) should be first with count 3
        assert result.top_pairs[0][0] == (1, 2)
        assert result.top_pairs[0][1] == 3

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        result = analyze_pair_stability([], min_occurrences=3)

        assert result.total_pairs_analyzed == 0
        assert result.stability_score == 0.0
        assert len(result.stable_pairs) == 0

    def test_stability_score_calculation(self) -> None:
        """Test stability score is ratio of stable to total pairs."""
        base_date = datetime(2024, 1, 1)
        # Single draw with 20 numbers = C(20,2) = 190 pairs
        draws = [make_draw(base_date, list(range(1, 21)))]

        result = analyze_pair_stability(draws, min_occurrences=1)

        # All pairs meet threshold (min=1, each appears exactly once)
        assert result.total_pairs_analyzed == 190  # C(20,2)
        assert len(result.stable_pairs) == 190
        assert result.stability_score == 1.0


# ============================================================================
# Test: calculate_gk1_correlation
# ============================================================================


class TestCalculateGK1Correlation:
    """Tests fuer calculate_gk1_correlation Funktion."""

    def test_basic_gk1_correlation(self) -> None:
        """Test basic GK1 correlation calculation."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, list(range(1, 21))),
            make_draw(base_date + timedelta(days=1), [1, 2, 3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),  # 3 recurring
            make_draw(base_date + timedelta(days=2), [1, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]),  # 1 recurring
        ]
        gk1_dates = [base_date + timedelta(days=1)]  # GK1 on day 2

        result = calculate_gk1_correlation(draws, gk1_dates, window=1)

        assert isinstance(result, GK1CorrelationResult)
        assert result.total_gk1_events == 1
        assert result.gk1_with_prior_recurrence == 1  # Day 2 has recurrence from day 1
        assert result.correlation_rate == 1.0

    def test_no_gk1_events(self) -> None:
        """Test with no matching GK1 events."""
        base_date = datetime(2024, 1, 1)
        draws = [make_draw(base_date, list(range(1, 21)))]
        gk1_dates = [datetime(2025, 1, 1)]  # No matching date

        result = calculate_gk1_correlation(draws, gk1_dates, window=1)

        assert result.total_gk1_events == 0
        assert result.correlation_rate == 0.0

    def test_gk1_without_prior_recurrence(self) -> None:
        """Test GK1 event without prior recurrence."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, list(range(1, 21))),
            make_draw(base_date + timedelta(days=1), list(range(21, 41))),  # No overlap
        ]
        gk1_dates = [base_date + timedelta(days=1)]

        result = calculate_gk1_correlation(draws, gk1_dates, window=1)

        assert result.total_gk1_events == 1
        assert result.gk1_with_prior_recurrence == 0
        assert result.correlation_rate == 0.0

    def test_baseline_rate_included(self) -> None:
        """Test that baseline recurrence rate is included."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, list(range(1, 21))),
            make_draw(base_date + timedelta(days=1), [1, 2, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),
            make_draw(base_date + timedelta(days=2), [1, 2, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]),
        ]
        gk1_dates = [base_date + timedelta(days=1)]

        result = calculate_gk1_correlation(draws, gk1_dates, window=1)

        # Both draws after first have recurrence, so baseline = 100%
        assert result.baseline_recurrence_rate == 1.0

    def test_empty_inputs(self) -> None:
        """Test with empty inputs."""
        result = calculate_gk1_correlation([], [], window=1)

        assert result.total_gk1_events == 0
        assert result.correlation_rate == 0.0


# ============================================================================
# Test: analyze_number_streaks
# ============================================================================


class TestAnalyzeNumberStreaks:
    """Tests fuer analyze_number_streaks Funktion."""

    def test_identifies_streaks(self) -> None:
        """Test that consecutive appearances are tracked."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw(base_date + timedelta(days=1), [1, 2, 3, 4, 5, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]),
            make_draw(base_date + timedelta(days=2), [1, 2, 3, 4, 5, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]),
            make_draw(base_date + timedelta(days=3), [1, 2, 3, 4, 5, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]),
        ]

        streaks = analyze_number_streaks(draws, min_streak=3)

        # Numbers 1-5 appear in all 4 draws consecutively
        for num in range(1, 6):
            assert num in streaks
            assert any(length >= 4 for _, _, length in streaks[num])

    def test_min_streak_filter(self) -> None:
        """Test that short streaks are filtered."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, [1, 2, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]),
            make_draw(base_date + timedelta(days=1), [1, 2, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]),
            make_draw(base_date + timedelta(days=2), [3, 4, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]),
        ]

        streaks = analyze_number_streaks(draws, min_streak=3)

        # Numbers 1, 2 only appear 2x consecutively - should not be in result
        assert 1 not in streaks or all(length < 3 for _, _, length in streaks.get(1, []))
        assert 2 not in streaks or all(length < 3 for _, _, length in streaks.get(2, []))

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        streaks = analyze_number_streaks([], min_streak=3)
        assert streaks == {}


# ============================================================================
# Test: analyze_weekly_cycle (7-Tage-Zyklus)
# ============================================================================


class TestAnalyzeWeeklyCycle:
    """Tests fuer analyze_weekly_cycle Funktion (HYP-006 7-Tage-Zyklus)."""

    def test_basic_weekly_cycle(self) -> None:
        """Test basic weekly cycle calculation."""
        base_date = datetime(2024, 1, 1)  # Monday
        draws = [
            make_draw(base_date, list(range(1, 21))),  # Monday
            make_draw(base_date + timedelta(days=1), [1, 2, 3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),  # Tuesday, 3 recurring
            make_draw(base_date + timedelta(days=2), list(range(38, 58))),  # Wednesday, 0 recurring
        ]

        result = analyze_weekly_cycle(draws)

        assert isinstance(result, WeeklyCycleResult)
        assert result.total_draws == 2  # Excludes first draw (no prior)
        # Tuesday (day 1) has recurrence, Wednesday (day 2) does not
        assert result.draws_by_weekday[1] == 1  # Tuesday
        assert result.draws_by_weekday[2] == 1  # Wednesday
        assert result.recurrence_by_weekday[1] == 1.0  # Tuesday: 100% recurrence
        assert result.recurrence_by_weekday[2] == 0.0  # Wednesday: 0% recurrence

    def test_best_worst_weekday(self) -> None:
        """Test best and worst weekday identification."""
        base_date = datetime(2024, 1, 1)  # Monday
        draws = [
            make_draw(base_date, list(range(1, 21))),
            make_draw(base_date + timedelta(days=1), [1, 2, 3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),  # Tuesday, has recurrence
            make_draw(base_date + timedelta(days=2), list(range(38, 58))),  # Wednesday, no recurrence
        ]

        result = analyze_weekly_cycle(draws)

        assert result.best_weekday == 1  # Tuesday
        assert result.worst_weekday == 2  # Wednesday

    def test_weekday_names(self) -> None:
        """Test weekday name mapping."""
        base_date = datetime(2024, 1, 1)
        draws = [make_draw(base_date, list(range(1, 21)))]

        result = analyze_weekly_cycle(draws)

        assert result.weekday_names[0] == "Montag"
        assert result.weekday_names[6] == "Sonntag"

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        result = analyze_weekly_cycle([])

        assert result.total_draws == 0
        assert result.best_weekday is None
        assert result.worst_weekday is None

    def test_single_draw(self) -> None:
        """Test with single draw."""
        draws = [make_draw(datetime(2024, 1, 1), list(range(1, 21)))]
        result = analyze_weekly_cycle(draws)

        assert result.total_draws == 1  # Single draw (no prior for comparison)
        # But no recurrence can be calculated


# ============================================================================
# Test: analyze_recurrence_days (7-Tage-Lookback)
# ============================================================================


class TestAnalyzeRecurrenceDays:
    """Tests fuer analyze_recurrence_days Funktion (HYP-006 7-Tage-Zyklus)."""

    def test_7day_recurrence(self) -> None:
        """Test 7-day recurrence calculation."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, list(range(1, 21))),  # Day 0
            make_draw(base_date + timedelta(days=3), [1, 2, 3, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),  # Day 3: within 7 days, 3 recurring
            make_draw(base_date + timedelta(days=8), list(range(38, 58))),  # Day 8: outside 7-day window from day 3
        ]

        result = analyze_recurrence_days(draws, days=7)

        assert isinstance(result, RecurrenceDaysResult)
        assert result.days == 7
        assert result.total_draws >= 1
        # Day 3 draw should have recurrence from day 0 (within 7 days)
        assert result.draws_with_recurrence >= 1

    def test_different_day_windows(self) -> None:
        """Test different day window values."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, list(range(1, 21))),
            make_draw(base_date + timedelta(days=5), [1, 2, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),  # 2 recurring
        ]

        result_3d = analyze_recurrence_days(draws, days=3)
        result_7d = analyze_recurrence_days(draws, days=7)

        # 3-day window: draw at day 5 is outside window from day 0
        # 7-day window: draw at day 5 is within window
        assert result_7d.draws_with_recurrence >= result_3d.draws_with_recurrence

    def test_multiple_draws_in_window(self) -> None:
        """Test with multiple draws within the lookback window."""
        base_date = datetime(2024, 1, 1)
        draws = [
            make_draw(base_date, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw(base_date + timedelta(days=1), [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]),
            make_draw(base_date + timedelta(days=2), [1, 21, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]),  # 1 from day 0, 1 from day 1
        ]

        result = analyze_recurrence_days(draws, days=7)

        # Day 2 draw has recurrence from both day 0 (1) and day 1 (21)
        assert result.total_draws >= 1
        assert 1 in result.recurrence_by_number or 21 in result.recurrence_by_number

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        result = analyze_recurrence_days([], days=7)

        assert result.days == 7
        assert result.total_draws == 0
        assert result.recurrence_rate == 0.0

    def test_single_draw(self) -> None:
        """Test with single draw."""
        draws = [make_draw(datetime(2024, 1, 1), list(range(1, 21)))]
        result = analyze_recurrence_days(draws, days=7)

        assert result.total_draws == 0  # No analyzable draws


# ============================================================================
# Test: generate_recurrence_report
# ============================================================================


class TestGenerateRecurrenceReport:
    """Tests fuer generate_recurrence_report Funktion."""

    def test_report_structure(self, sequential_draws: list[DrawResult]) -> None:
        """Test that report has expected structure."""
        report = generate_recurrence_report(sequential_draws)

        assert "metadata" in report
        assert "recurrence" in report
        assert "pair_stability" in report
        assert "streaks" in report
        assert "weekly_cycle" in report
        assert "recurrence_7d" in report
        assert "acceptance_criteria" in report

    def test_metadata_content(self, sequential_draws: list[DrawResult]) -> None:
        """Test metadata section content."""
        report = generate_recurrence_report(sequential_draws)

        assert report["metadata"]["hypothesis"] == "HYP-006"
        assert report["metadata"]["total_draws"] == len(sequential_draws)
        assert "generated_at" in report["metadata"]
        assert "config" in report["metadata"]

    def test_acceptance_criteria_included(self, sequential_draws: list[DrawResult]) -> None:
        """Test that acceptance criteria are included."""
        report = generate_recurrence_report(sequential_draws)
        ac = report["acceptance_criteria"]

        assert "AC1_recurrence_rate_calculated" in ac
        assert "AC2_pair_stability_measured" in ac
        assert "AC3_gk1_correlation_computed" in ac
        assert "AC4_streaks_identified" in ac
        assert "AC5_7day_recurrence_calculated" in ac
        assert "AC6_weekly_cycle_analyzed" in ac

    def test_with_gk1_dates(self, sequential_draws: list[DrawResult]) -> None:
        """Test report with GK1 dates included."""
        gk1_dates = [sequential_draws[1].date]
        report = generate_recurrence_report(sequential_draws, gk1_dates)

        assert "gk1_correlation" in report
        assert report["gk1_correlation"]["total_gk1_events"] == 1

    def test_custom_config(self, sequential_draws: list[DrawResult]) -> None:
        """Test report with custom config."""
        config = {
            "window": 2,
            "min_occurrences": 5,
            "min_streak": 4,
            "top_n": 10,
            "recurrence_days": 14,
        }
        report = generate_recurrence_report(sequential_draws, config=config)

        assert report["metadata"]["config"]["window"] == 2
        assert report["metadata"]["config"]["min_occurrences"] == 5
        assert report["metadata"]["config"]["recurrence_days"] == 14

    def test_weekly_cycle_in_report(self, sequential_draws: list[DrawResult]) -> None:
        """Test weekly_cycle section in report."""
        report = generate_recurrence_report(sequential_draws)

        wc = report["weekly_cycle"]
        assert "total_draws" in wc
        assert "draws_by_weekday" in wc
        assert "recurrence_by_weekday" in wc
        assert "best_weekday" in wc
        assert "worst_weekday" in wc

    def test_recurrence_7d_in_report(self, sequential_draws: list[DrawResult]) -> None:
        """Test recurrence_7d section in report."""
        report = generate_recurrence_report(sequential_draws)

        r7d = report["recurrence_7d"]
        assert "days" in r7d
        assert r7d["days"] == 7  # Default
        assert "total_draws" in r7d
        assert "draws_with_recurrence" in r7d
        assert "recurrence_rate" in r7d
        assert "avg_recurrence_count" in r7d
        assert "max_recurrence_count" in r7d
        assert "top_recurring_numbers" in r7d
