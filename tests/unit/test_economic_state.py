"""Unit tests for economic_state module."""

from datetime import datetime

import numpy as np
import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.economic_state import (
    EconomicState,
    classify_economic_state,
    compute_rolling_cv,
    compute_state_distribution,
    extract_economic_states,
    get_bet_recommendation,
    parse_jackpot,
    parse_spieleinsatz,
)


class TestParseSpielEinsatz:
    """Tests for parse_spieleinsatz function."""

    def test_parse_float(self):
        """Test parsing float value."""
        assert parse_spieleinsatz({"spieleinsatz": 1000.0}) == 1000.0

    def test_parse_int(self):
        """Test parsing int value."""
        assert parse_spieleinsatz({"spieleinsatz": 1000}) == 1000.0

    def test_parse_german_format(self):
        """Test parsing German number format (1.234.567,89)."""
        assert parse_spieleinsatz({"spieleinsatz": "1.234.567,89"}) == 1234567.89

    def test_parse_simple_string(self):
        """Test parsing simple string number."""
        assert parse_spieleinsatz({"spieleinsatz": "1000"}) == 1000.0

    def test_parse_missing(self):
        """Test parsing missing value."""
        assert parse_spieleinsatz({}) is None

    def test_parse_none(self):
        """Test parsing None value."""
        assert parse_spieleinsatz({"spieleinsatz": None}) is None

    def test_parse_invalid_string(self):
        """Test parsing invalid string."""
        assert parse_spieleinsatz({"spieleinsatz": "invalid"}) is None


class TestParseJackpot:
    """Tests for parse_jackpot function."""

    def test_parse_float(self):
        """Test parsing float value."""
        assert parse_jackpot({"jackpot": 5000000.0}) == 5000000.0

    def test_parse_german_format(self):
        """Test parsing German number format."""
        assert parse_jackpot({"jackpot": "10.000.000,00"}) == 10000000.0

    def test_parse_missing(self):
        """Test parsing missing value."""
        assert parse_jackpot({}) is None


class TestComputeRollingCV:
    """Tests for compute_rolling_cv function."""

    def _make_draw(self, date: datetime, numbers: list[int]) -> DrawResult:
        """Helper to create a DrawResult."""
        return DrawResult(
            date=date,
            numbers=sorted(numbers),
            bonus=[],
            game_type=GameType.KENO,
            metadata={},
        )

    def test_insufficient_draws(self):
        """Test with fewer draws than window."""
        draws = [
            self._make_draw(datetime(2024, 1, i), [1, 2, 3, 4, 5])
            for i in range(1, 5)
        ]
        cvs = compute_rolling_cv(draws, window=10)
        assert cvs == [None, None, None, None]

    def test_cv_computed(self):
        """Test that CV is computed correctly for typical draws."""
        import datetime as dt
        # Create draws with typical KENO pattern (20 numbers from 1-70)
        draws = []
        for i in range(30):
            nums = list(range((i % 14) + 1, (i % 14) + 21))[:20]
            draws.append(
                self._make_draw(datetime(2024, 1, 1) + dt.timedelta(days=i), nums)
            )

        cvs = compute_rolling_cv(draws, window=30, numbers_range=(1, 70))
        # Last value should be computed
        assert cvs[-1] is not None
        # CV should be positive (some variation exists)
        assert cvs[-1] > 0.0
        # CV should be finite
        assert np.isfinite(cvs[-1])

    def test_first_values_none(self):
        """Test that first (window-1) values are None."""
        draws = [
            self._make_draw(
                datetime(2024, 1, 1) + __import__("datetime").timedelta(days=i),
                list(range(1, 21)),
            )
            for i in range(50)
        ]
        cvs = compute_rolling_cv(draws, window=30)
        # First 29 should be None
        assert all(cv is None for cv in cvs[:29])
        # Rest should be computed
        assert all(cv is not None for cv in cvs[29:])


class TestClassifyEconomicState:
    """Tests for classify_economic_state function."""

    def test_normal_state(self):
        """Test classification of normal state."""
        state = classify_economic_state(
            spieleinsatz=1000000,
            jackpot=5000000,
            rolling_cv=0.3,
            spieleinsatz_baseline=1000000,
        )
        assert state == "NORMAL"

    def test_cooldown_state(self):
        """Test classification of cooldown state (multiple indicators)."""
        state = classify_economic_state(
            spieleinsatz=500000,  # 50% of baseline
            jackpot=1000000,  # Low jackpot (recently hit)
            rolling_cv=0.6,  # High CV
            spieleinsatz_baseline=1000000,
        )
        assert state == "COOLDOWN"

    def test_hot_state(self):
        """Test classification of hot state."""
        state = classify_economic_state(
            spieleinsatz=1500000,  # 150% of baseline
            jackpot=15000000,  # High jackpot
            rolling_cv=0.3,  # Normal CV
            spieleinsatz_baseline=1000000,
            jackpot_high_threshold=10000000,
        )
        assert state == "HOT"

    def test_recovery_state(self):
        """Test classification of recovery state (single indicator)."""
        state = classify_economic_state(
            spieleinsatz=750000,  # Only slightly low (not triggering cooldown)
            jackpot=8000000,  # Medium jackpot
            rolling_cv=0.6,  # High CV (1 cooldown indicator)
            spieleinsatz_baseline=1000000,
        )
        assert state == "RECOVERY"

    def test_all_none(self):
        """Test classification with all None values."""
        state = classify_economic_state(
            spieleinsatz=None,
            jackpot=None,
            rolling_cv=None,
        )
        assert state == "NORMAL"


class TestExtractEconomicStates:
    """Tests for extract_economic_states function."""

    def _make_draw(
        self, date: datetime, numbers: list[int], spieleinsatz: float = None, jackpot: float = None
    ) -> DrawResult:
        """Helper to create a DrawResult with metadata."""
        metadata = {}
        if spieleinsatz is not None:
            metadata["spieleinsatz"] = spieleinsatz
        if jackpot is not None:
            metadata["jackpot"] = jackpot
        return DrawResult(
            date=date,
            numbers=sorted(numbers),
            bonus=[],
            game_type=GameType.KENO,
            metadata=metadata,
        )

    def test_extract_states(self):
        """Test extracting economic states from draws."""
        import datetime as dt
        draws = [
            self._make_draw(
                datetime(2024, 1, 1) + dt.timedelta(days=i),
                list(range(1, 21)),
                spieleinsatz=1000000.0,
                jackpot=5000000.0,
            )
            for i in range(50)
        ]

        states = extract_economic_states(draws, window=30)

        assert len(states) == 50
        assert all(isinstance(s, EconomicState) for s in states)
        # First 29 should have None rolling_cv
        assert all(s.rolling_cv is None for s in states[:29])
        # All should have spieleinsatz
        assert all(s.spieleinsatz == 1000000.0 for s in states)

    def test_empty_draws(self):
        """Test with empty draws list."""
        states = extract_economic_states([])
        assert states == []


class TestGetBetRecommendation:
    """Tests for get_bet_recommendation function."""

    def test_cooldown_recommendation(self):
        """Test recommendation for COOLDOWN state."""
        state = EconomicState(
            date=datetime.now(),
            spieleinsatz=500000,
            jackpot=1000000,
            rolling_cv=0.6,
            state_label="COOLDOWN",
        )
        rec = get_bet_recommendation(state)
        assert rec["action"] == "AVOID"
        assert rec["confidence"] == 0.7
        assert "Axiom A7" in rec["reason"]

    def test_hot_recommendation(self):
        """Test recommendation for HOT state."""
        state = EconomicState(
            date=datetime.now(),
            spieleinsatz=1500000,
            jackpot=15000000,
            rolling_cv=0.3,
            state_label="HOT",
        )
        rec = get_bet_recommendation(state)
        assert rec["action"] == "CONSIDER"

    def test_normal_recommendation(self):
        """Test recommendation for NORMAL state."""
        state = EconomicState(
            date=datetime.now(),
            spieleinsatz=1000000,
            jackpot=5000000,
            rolling_cv=0.3,
            state_label="NORMAL",
        )
        rec = get_bet_recommendation(state)
        assert rec["action"] == "NEUTRAL"


class TestComputeStateDistribution:
    """Tests for compute_state_distribution function."""

    def test_distribution(self):
        """Test computing state distribution."""
        states = [
            EconomicState(datetime.now(), 1000, 1000, 0.3, "NORMAL"),
            EconomicState(datetime.now(), 1000, 1000, 0.3, "NORMAL"),
            EconomicState(datetime.now(), 500, 500, 0.6, "COOLDOWN"),
        ]
        dist = compute_state_distribution(states)

        assert dist["total"] == 3
        assert dist["counts"]["NORMAL"] == 2
        assert dist["counts"]["COOLDOWN"] == 1
        assert abs(dist["percentages"]["NORMAL"] - 66.67) < 1

    def test_empty_distribution(self):
        """Test distribution of empty states list."""
        dist = compute_state_distribution([])
        assert dist["total"] == 0
        assert dist["counts"] == {}
        assert dist["percentages"] == {}


class TestEconomicStateDataclass:
    """Tests for EconomicState dataclass."""

    def test_default_state_label(self):
        """Test default state label."""
        state = EconomicState(
            date=datetime.now(),
            spieleinsatz=1000000,
            jackpot=5000000,
            rolling_cv=0.3,
        )
        assert state.state_label == "NORMAL"

    def test_custom_state_label(self):
        """Test custom state label."""
        state = EconomicState(
            date=datetime.now(),
            spieleinsatz=1000000,
            jackpot=5000000,
            rolling_cv=0.3,
            state_label="COOLDOWN",
        )
        assert state.state_label == "COOLDOWN"
