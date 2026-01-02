"""Unit tests for strategy_from_ecosystem.py module.

Tests the Axiom-First timing/EV strategy derived from ecosystem analysis.
"""

from datetime import datetime, timedelta
from typing import Optional

import pytest

# Import the strategy module functions
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from strategy_from_ecosystem import (
    COOLDOWN_DAYS,
    StrategyDecision,
    compute_ev_multiplier,
    compute_ev_summary,
    compute_jackpot_cooldown_dates,
    generate_strategy_decisions,
    is_in_cooldown,
)
from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.economic_state import EconomicState


class TestComputeEvMultiplier:
    """Tests for EV multiplier computation."""

    def test_cooldown_ev(self):
        """COOLDOWN state should have -66% EV (0.34 multiplier)."""
        ev = compute_ev_multiplier("COOLDOWN")
        assert ev == pytest.approx(0.34, rel=0.01)

    def test_hot_ev(self):
        """HOT state should have +20% EV (1.20 multiplier)."""
        ev = compute_ev_multiplier("HOT")
        assert ev == pytest.approx(1.20, rel=0.01)

    def test_normal_ev(self):
        """NORMAL state should have baseline EV (1.0 multiplier)."""
        ev = compute_ev_multiplier("NORMAL")
        assert ev == pytest.approx(1.0, rel=0.01)

    def test_recovery_ev(self):
        """RECOVERY state should have 0.85 EV multiplier."""
        ev = compute_ev_multiplier("RECOVERY")
        assert ev == pytest.approx(0.85, rel=0.01)

    def test_unknown_ev(self):
        """Unknown state should default to 1.0."""
        ev = compute_ev_multiplier("UNKNOWN_STATE")
        assert ev == pytest.approx(1.0, rel=0.01)


class TestIsInCooldown:
    """Tests for cooldown period checking."""

    def test_in_cooldown_period(self):
        """Date within cooldown period should return True."""
        hit_date = datetime(2024, 1, 1)
        cooldown_end = hit_date + timedelta(days=COOLDOWN_DAYS)
        periods = [(hit_date, cooldown_end)]

        # Day 15 is within 30-day cooldown
        check_date = datetime(2024, 1, 15)
        assert is_in_cooldown(check_date, periods) is True

    def test_outside_cooldown_period(self):
        """Date outside cooldown period should return False."""
        hit_date = datetime(2024, 1, 1)
        cooldown_end = hit_date + timedelta(days=COOLDOWN_DAYS)
        periods = [(hit_date, cooldown_end)]

        # Day 31 is after 30-day cooldown
        check_date = datetime(2024, 2, 5)
        assert is_in_cooldown(check_date, periods) is False

    def test_on_hit_date(self):
        """Hit date itself should be in cooldown."""
        hit_date = datetime(2024, 1, 1)
        cooldown_end = hit_date + timedelta(days=COOLDOWN_DAYS)
        periods = [(hit_date, cooldown_end)]

        assert is_in_cooldown(hit_date, periods) is True

    def test_on_cooldown_end(self):
        """Last day of cooldown should still be in cooldown."""
        hit_date = datetime(2024, 1, 1)
        cooldown_end = hit_date + timedelta(days=COOLDOWN_DAYS)
        periods = [(hit_date, cooldown_end)]

        assert is_in_cooldown(cooldown_end, periods) is True

    def test_empty_periods(self):
        """Empty periods list should return False."""
        check_date = datetime(2024, 1, 15)
        assert is_in_cooldown(check_date, []) is False

    def test_multiple_periods(self):
        """Should handle multiple cooldown periods."""
        period1 = (datetime(2024, 1, 1), datetime(2024, 1, 31))
        period2 = (datetime(2024, 6, 1), datetime(2024, 6, 30))
        periods = [period1, period2]

        # Check dates in different periods
        assert is_in_cooldown(datetime(2024, 1, 15), periods) is True
        assert is_in_cooldown(datetime(2024, 6, 15), periods) is True
        assert is_in_cooldown(datetime(2024, 3, 15), periods) is False


class TestComputeJackpotCooldownDates:
    """Tests for jackpot cooldown detection."""

    def test_detect_jackpot_hit(self):
        """Should detect jackpot hit when >70% drop occurs."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "15000000"},  # High jackpot
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "1000000"},  # Dropped to 1M (>70% drop)
            ),
        ]

        periods = compute_jackpot_cooldown_dates(draws, jackpot_threshold=10_000_000.0)
        assert len(periods) == 1
        assert periods[0][0] == datetime(2024, 1, 2)  # Hit date

    def test_no_hit_small_drop(self):
        """Should not detect hit if drop is <70%."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "15000000"},
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "10000000"},  # Only 33% drop
            ),
        ]

        periods = compute_jackpot_cooldown_dates(draws, jackpot_threshold=10_000_000.0)
        assert len(periods) == 0

    def test_no_hit_below_threshold(self):
        """Should not detect hit if previous jackpot was below threshold."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "5000000"},  # Below threshold
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
                metadata={"jackpot": "1000000"},
            ),
        ]

        periods = compute_jackpot_cooldown_dates(draws, jackpot_threshold=10_000_000.0)
        assert len(periods) == 0


class TestGenerateStrategyDecisions:
    """Tests for strategy decision generation."""

    def test_cooldown_state_avoid(self):
        """COOLDOWN state should generate AVOID action."""
        states = [
            EconomicState(
                date=datetime(2024, 1, 1),
                spieleinsatz=1000000.0,
                jackpot=5000000.0,
                rolling_cv=0.6,
                state_label="COOLDOWN",
            )
        ]

        decisions = generate_strategy_decisions(states, cooldown_periods=[])
        assert len(decisions) == 1
        assert decisions[0].action == "AVOID"
        assert decisions[0].state == "COOLDOWN"

    def test_normal_state_play(self):
        """NORMAL state should generate PLAY action."""
        states = [
            EconomicState(
                date=datetime(2024, 1, 1),
                spieleinsatz=1000000.0,
                jackpot=5000000.0,
                rolling_cv=0.3,
                state_label="NORMAL",
            )
        ]

        decisions = generate_strategy_decisions(states, cooldown_periods=[])
        assert len(decisions) == 1
        assert decisions[0].action == "PLAY"
        assert decisions[0].state == "NORMAL"

    def test_hot_state_cautious(self):
        """HOT state should generate CAUTIOUS action."""
        states = [
            EconomicState(
                date=datetime(2024, 1, 1),
                spieleinsatz=2000000.0,
                jackpot=15000000.0,
                rolling_cv=0.3,
                state_label="HOT",
            )
        ]

        decisions = generate_strategy_decisions(states, cooldown_periods=[])
        assert len(decisions) == 1
        assert decisions[0].action == "CAUTIOUS"
        assert decisions[0].state == "HOT"

    def test_jackpot_cooldown_overrides(self):
        """Jackpot cooldown should override other states."""
        states = [
            EconomicState(
                date=datetime(2024, 1, 15),
                spieleinsatz=2000000.0,
                jackpot=15000000.0,
                rolling_cv=0.3,
                state_label="HOT",  # Would normally be CAUTIOUS
            )
        ]

        # But date is in cooldown period
        cooldown_periods = [(datetime(2024, 1, 1), datetime(2024, 1, 31))]

        decisions = generate_strategy_decisions(states, cooldown_periods)
        assert len(decisions) == 1
        assert decisions[0].action == "AVOID"
        assert decisions[0].state == "COOLDOWN_JACKPOT"


class TestComputeEvSummary:
    """Tests for EV summary computation."""

    def test_empty_decisions(self):
        """Empty decisions should return minimal summary."""
        summary = compute_ev_summary([])
        assert summary["n_decisions"] == 0

    def test_mixed_decisions(self):
        """Should correctly summarize mixed decisions."""
        decisions = [
            StrategyDecision(
                date=datetime(2024, 1, 1),
                state="NORMAL",
                action="PLAY",
                ev_multiplier=1.0,
                confidence=0.5,
                reason="Test",
            ),
            StrategyDecision(
                date=datetime(2024, 1, 2),
                state="COOLDOWN",
                action="AVOID",
                ev_multiplier=0.34,
                confidence=0.7,
                reason="Test",
            ),
            StrategyDecision(
                date=datetime(2024, 1, 3),
                state="HOT",
                action="CAUTIOUS",
                ev_multiplier=1.2,
                confidence=0.6,
                reason="Test",
            ),
        ]

        summary = compute_ev_summary(decisions)
        assert summary["n_decisions"] == 3
        assert summary["play_days"] == 2  # PLAY + CAUTIOUS
        assert summary["avoid_days"] == 1
        assert summary["action_counts"]["PLAY"] == 1
        assert summary["action_counts"]["AVOID"] == 1
        assert summary["action_counts"]["CAUTIOUS"] == 1

    def test_relative_improvement(self):
        """Should compute positive improvement when avoiding bad days."""
        decisions = [
            StrategyDecision(
                date=datetime(2024, 1, i),
                state="NORMAL",
                action="PLAY",
                ev_multiplier=1.0,
                confidence=0.5,
                reason="Test",
            )
            for i in range(1, 8)  # 7 normal days
        ] + [
            StrategyDecision(
                date=datetime(2024, 1, i),
                state="COOLDOWN",
                action="AVOID",
                ev_multiplier=0.34,
                confidence=0.7,
                reason="Test",
            )
            for i in range(8, 11)  # 3 cooldown days
        ]

        summary = compute_ev_summary(decisions)
        assert summary["play_days"] == 7
        assert summary["avoid_days"] == 3
        # Play days have EV=1.0, which is above average (dragged down by 0.34)
        assert summary["relative_improvement_pct"] > 0


class TestIntegration:
    """Integration tests for the strategy module."""

    def test_full_workflow_synthetic(self):
        """Test full workflow with synthetic data."""
        # Create synthetic draws
        draws = []
        for i in range(100):
            date = datetime(2024, 1, 1) + timedelta(days=i)
            # Jackpot hit around day 30
            if i < 30:
                jackpot = 15000000 - i * 100000
            elif i == 30:
                jackpot = 1000000  # Hit!
            else:
                jackpot = 1000000 + (i - 30) * 500000

            draws.append(
                DrawResult(
                    date=date,
                    numbers=list(range(1, 21)),
                    game_type=GameType.KENO,
                    metadata={"jackpot": str(int(jackpot))},
                )
            )

        # Detect cooldown
        periods = compute_jackpot_cooldown_dates(draws)
        assert len(periods) >= 1

        # Create states and decisions
        from kenobase.core.economic_state import extract_economic_states

        states = extract_economic_states(draws)
        decisions = generate_strategy_decisions(states, periods)

        # Should have decisions for all states
        assert len(decisions) == len(states)

        # Some decisions should be AVOID (during cooldown)
        avoid_count = sum(1 for d in decisions if d.action == "AVOID")
        assert avoid_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
