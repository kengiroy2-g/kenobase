"""Unit tests for kenobase.analysis.cycle_phases module.

Tests Zyklus-Phasen Labeling basierend auf Jackpot-Events:
- Phase boundaries (COOLDOWN: 0-30d, GROWTH: 31-60d, HOT: >60d)
- Edge cases (keine Jackpots, mehrere Jackpots nah beieinander)
- Integration mit DrawResult und jackpot_dates
"""

from datetime import datetime

import pytest

from kenobase.analysis.cycle_phases import (
    COOLDOWN_MAX_DAYS,
    GROWTH_MAX_DAYS,
    Phase,
    PhaseLabel,
    filter_draws_by_phase,
    get_phase_for_date,
    get_phase_for_days,
    get_phase_statistics,
    label_phases,
)
from kenobase.core.data_loader import DrawResult, GameType


class TestGetPhaseForDays:
    """Tests for get_phase_for_days function."""

    def test_none_returns_unknown(self):
        """None days should return UNKNOWN phase."""
        assert get_phase_for_days(None) == Phase.UNKNOWN

    def test_zero_days_is_cooldown(self):
        """Day 0 (jackpot day itself) is COOLDOWN."""
        assert get_phase_for_days(0) == Phase.COOLDOWN

    def test_boundary_30_is_cooldown(self):
        """Day 30 is still COOLDOWN (boundary inclusive)."""
        assert get_phase_for_days(30) == Phase.COOLDOWN
        assert get_phase_for_days(COOLDOWN_MAX_DAYS) == Phase.COOLDOWN

    def test_day_31_is_growth(self):
        """Day 31 transitions to GROWTH."""
        assert get_phase_for_days(31) == Phase.GROWTH

    def test_boundary_60_is_growth(self):
        """Day 60 is still GROWTH (boundary inclusive)."""
        assert get_phase_for_days(60) == Phase.GROWTH
        assert get_phase_for_days(GROWTH_MAX_DAYS) == Phase.GROWTH

    def test_day_61_is_hot(self):
        """Day 61 transitions to HOT."""
        assert get_phase_for_days(61) == Phase.HOT

    def test_high_days_is_hot(self):
        """Very high days (e.g., 100+) remain HOT."""
        assert get_phase_for_days(100) == Phase.HOT
        assert get_phase_for_days(365) == Phase.HOT


class TestGetPhaseForDate:
    """Tests for get_phase_for_date function."""

    def test_empty_jackpots_returns_unknown(self):
        """No jackpot dates should return UNKNOWN."""
        target = datetime(2023, 6, 15)
        result = get_phase_for_date(target, set())
        assert result.phase == Phase.UNKNOWN
        assert result.days_since_jackpot is None
        assert result.last_jackpot_date is None

    def test_date_before_all_jackpots_returns_unknown(self):
        """Date before all jackpots should return UNKNOWN."""
        jackpots = {datetime(2023, 6, 1)}
        target = datetime(2023, 5, 15)
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.UNKNOWN
        assert result.days_since_jackpot is None

    def test_same_day_as_jackpot_is_cooldown_day_0(self):
        """Jackpot day itself should be COOLDOWN with days_since=0."""
        jackpots = {datetime(2023, 6, 1)}
        target = datetime(2023, 6, 1)
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.COOLDOWN
        assert result.days_since_jackpot == 0
        assert result.last_jackpot_date == datetime(2023, 6, 1)

    def test_10_days_after_jackpot_is_cooldown(self):
        """10 days after jackpot should be COOLDOWN."""
        jackpots = {datetime(2023, 6, 1)}
        target = datetime(2023, 6, 11)  # 10 days later
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.COOLDOWN
        assert result.days_since_jackpot == 10

    def test_45_days_after_jackpot_is_growth(self):
        """45 days after jackpot should be GROWTH."""
        jackpots = {datetime(2023, 6, 1)}
        target = datetime(2023, 7, 16)  # 45 days later
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.GROWTH
        assert result.days_since_jackpot == 45

    def test_90_days_after_jackpot_is_hot(self):
        """90 days after jackpot should be HOT."""
        jackpots = {datetime(2023, 6, 1)}
        target = datetime(2023, 8, 30)  # 90 days later
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.HOT
        assert result.days_since_jackpot == 90

    def test_multiple_jackpots_uses_most_recent(self):
        """With multiple jackpots, should use most recent one before target."""
        jackpots = {
            datetime(2023, 1, 1),
            datetime(2023, 6, 1),
            datetime(2023, 12, 1),
        }
        target = datetime(2023, 6, 15)  # 14 days after June jackpot
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.COOLDOWN
        assert result.days_since_jackpot == 14
        assert result.last_jackpot_date == datetime(2023, 6, 1)

    def test_close_jackpots_resets_phase(self):
        """Jackpots close together should reset the phase counter."""
        jackpots = {
            datetime(2023, 6, 1),
            datetime(2023, 6, 10),  # Only 9 days after first
        }
        # 5 days after second jackpot
        target = datetime(2023, 6, 15)
        result = get_phase_for_date(target, jackpots)
        assert result.phase == Phase.COOLDOWN
        assert result.days_since_jackpot == 5
        assert result.last_jackpot_date == datetime(2023, 6, 10)


class TestLabelPhases:
    """Tests for label_phases function."""

    def _make_draw(self, date: datetime) -> DrawResult:
        """Create a minimal DrawResult for testing."""
        return DrawResult(
            date=date,
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            game_type=GameType.KENO,
        )

    def test_empty_draws_returns_empty_dict(self):
        """Empty draw list should return empty dict."""
        jackpots = {datetime(2023, 6, 1)}
        result = label_phases([], jackpots)
        assert result == {}

    def test_empty_jackpots_all_unknown(self):
        """No jackpots should label all draws as UNKNOWN."""
        draws = [
            self._make_draw(datetime(2023, 6, 1)),
            self._make_draw(datetime(2023, 6, 15)),
        ]
        result = label_phases(draws, set())
        assert len(result) == 2
        for label in result.values():
            assert label.phase == Phase.UNKNOWN

    def test_labels_multiple_draws_correctly(self):
        """Multiple draws should be labeled with correct phases."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 6, 1)),   # Day 0 - COOLDOWN
            self._make_draw(datetime(2023, 6, 15)),  # Day 14 - COOLDOWN
            self._make_draw(datetime(2023, 7, 5)),   # Day 34 - GROWTH
            self._make_draw(datetime(2023, 8, 15)),  # Day 75 - HOT
        ]
        result = label_phases(draws, jackpots)

        assert len(result) == 4

        # Check each draw's phase
        d1 = datetime(2023, 6, 1)
        d2 = datetime(2023, 6, 15)
        d3 = datetime(2023, 7, 5)
        d4 = datetime(2023, 8, 15)

        assert result[d1].phase == Phase.COOLDOWN
        assert result[d2].phase == Phase.COOLDOWN
        assert result[d3].phase == Phase.GROWTH
        assert result[d4].phase == Phase.HOT

    def test_draws_before_jackpot_are_unknown(self):
        """Draws before the first jackpot should be UNKNOWN."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 5, 1)),   # Before jackpot - UNKNOWN
            self._make_draw(datetime(2023, 5, 15)),  # Before jackpot - UNKNOWN
            self._make_draw(datetime(2023, 6, 5)),   # After jackpot - COOLDOWN
        ]
        result = label_phases(draws, jackpots)

        d1 = datetime(2023, 5, 1)
        d2 = datetime(2023, 5, 15)
        d3 = datetime(2023, 6, 5)

        assert result[d1].phase == Phase.UNKNOWN
        assert result[d2].phase == Phase.UNKNOWN
        assert result[d3].phase == Phase.COOLDOWN

    def test_boundary_day_30_is_cooldown(self):
        """Day 30 boundary should be COOLDOWN."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [self._make_draw(datetime(2023, 7, 1))]  # Exactly 30 days
        result = label_phases(draws, jackpots)

        d = datetime(2023, 7, 1)
        assert result[d].phase == Phase.COOLDOWN
        assert result[d].days_since_jackpot == 30

    def test_boundary_day_31_is_growth(self):
        """Day 31 boundary should be GROWTH."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [self._make_draw(datetime(2023, 7, 2))]  # 31 days
        result = label_phases(draws, jackpots)

        d = datetime(2023, 7, 2)
        assert result[d].phase == Phase.GROWTH
        assert result[d].days_since_jackpot == 31

    def test_boundary_day_60_is_growth(self):
        """Day 60 boundary should be GROWTH."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [self._make_draw(datetime(2023, 7, 31))]  # 60 days
        result = label_phases(draws, jackpots)

        d = datetime(2023, 7, 31)
        assert result[d].phase == Phase.GROWTH
        assert result[d].days_since_jackpot == 60

    def test_boundary_day_61_is_hot(self):
        """Day 61 boundary should be HOT."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [self._make_draw(datetime(2023, 8, 1))]  # 61 days
        result = label_phases(draws, jackpots)

        d = datetime(2023, 8, 1)
        assert result[d].phase == Phase.HOT
        assert result[d].days_since_jackpot == 61


class TestFilterDrawsByPhase:
    """Tests for filter_draws_by_phase function."""

    def _make_draw(self, date: datetime) -> DrawResult:
        """Create a minimal DrawResult for testing."""
        return DrawResult(
            date=date,
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            game_type=GameType.KENO,
        )

    def test_filter_cooldown(self):
        """Should filter only COOLDOWN draws."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 6, 5)),   # COOLDOWN
            self._make_draw(datetime(2023, 7, 5)),   # GROWTH
            self._make_draw(datetime(2023, 8, 15)),  # HOT
        ]
        labels = label_phases(draws, jackpots)
        filtered = filter_draws_by_phase(draws, labels, Phase.COOLDOWN)

        assert len(filtered) == 1
        assert filtered[0].date == datetime(2023, 6, 5)

    def test_filter_hot(self):
        """Should filter only HOT draws."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 6, 5)),   # COOLDOWN
            self._make_draw(datetime(2023, 8, 15)),  # HOT
            self._make_draw(datetime(2023, 9, 1)),   # HOT
        ]
        labels = label_phases(draws, jackpots)
        filtered = filter_draws_by_phase(draws, labels, Phase.HOT)

        assert len(filtered) == 2

    def test_filter_unknown(self):
        """Should filter only UNKNOWN draws."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 5, 1)),   # UNKNOWN
            self._make_draw(datetime(2023, 5, 15)),  # UNKNOWN
            self._make_draw(datetime(2023, 6, 5)),   # COOLDOWN
        ]
        labels = label_phases(draws, jackpots)
        filtered = filter_draws_by_phase(draws, labels, Phase.UNKNOWN)

        assert len(filtered) == 2


class TestGetPhaseStatistics:
    """Tests for get_phase_statistics function."""

    def _make_draw(self, date: datetime) -> DrawResult:
        """Create a minimal DrawResult for testing."""
        return DrawResult(
            date=date,
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            game_type=GameType.KENO,
        )

    def test_statistics_empty_labels(self):
        """Empty labels should return zero counts."""
        stats = get_phase_statistics({})
        assert stats["total_draws"] == 0
        for phase in Phase:
            assert stats["phase_distribution"][phase.value]["count"] == 0

    def test_statistics_counts_phases(self):
        """Should correctly count draws per phase."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 6, 5)),   # COOLDOWN
            self._make_draw(datetime(2023, 6, 10)),  # COOLDOWN
            self._make_draw(datetime(2023, 7, 5)),   # GROWTH
            self._make_draw(datetime(2023, 8, 15)),  # HOT
        ]
        labels = label_phases(draws, jackpots)
        stats = get_phase_statistics(labels)

        assert stats["total_draws"] == 4
        assert stats["phase_distribution"]["COOLDOWN"]["count"] == 2
        assert stats["phase_distribution"]["GROWTH"]["count"] == 1
        assert stats["phase_distribution"]["HOT"]["count"] == 1
        assert stats["phase_distribution"]["UNKNOWN"]["count"] == 0

    def test_statistics_ratios(self):
        """Should correctly calculate phase ratios."""
        jackpots = {datetime(2023, 6, 1)}
        draws = [
            self._make_draw(datetime(2023, 6, 5)),
            self._make_draw(datetime(2023, 6, 10)),
            self._make_draw(datetime(2023, 7, 5)),
            self._make_draw(datetime(2023, 8, 15)),
        ]
        labels = label_phases(draws, jackpots)
        stats = get_phase_statistics(labels)

        assert stats["phase_distribution"]["COOLDOWN"]["ratio"] == pytest.approx(0.5)
        assert stats["phase_distribution"]["GROWTH"]["ratio"] == pytest.approx(0.25)
        assert stats["phase_distribution"]["HOT"]["ratio"] == pytest.approx(0.25)


class TestPhaseEnum:
    """Tests for Phase enum."""

    def test_phase_is_string_enum(self):
        """Phase should be string enum for easy serialization."""
        assert Phase.COOLDOWN.value == "COOLDOWN"
        assert Phase.GROWTH.value == "GROWTH"
        assert Phase.HOT.value == "HOT"
        assert Phase.UNKNOWN.value == "UNKNOWN"

    def test_phase_string_comparison(self):
        """Phase enum should support string comparison."""
        assert Phase.COOLDOWN == "COOLDOWN"
        assert Phase.HOT == "HOT"


class TestPhaseLabelDataclass:
    """Tests for PhaseLabel dataclass."""

    def test_frozen_dataclass(self):
        """PhaseLabel should be immutable."""
        label = PhaseLabel(
            date=datetime(2023, 6, 1),
            phase=Phase.COOLDOWN,
            days_since_jackpot=0,
            last_jackpot_date=datetime(2023, 6, 1),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            label.phase = Phase.HOT

    def test_unknown_label_has_none_values(self):
        """UNKNOWN phase should have None for jackpot-related fields."""
        label = PhaseLabel(
            date=datetime(2023, 5, 1),
            phase=Phase.UNKNOWN,
            days_since_jackpot=None,
            last_jackpot_date=None,
        )
        assert label.days_since_jackpot is None
        assert label.last_jackpot_date is None
