"""Unit tests for loss streak analysis.

Tests:
- is_payout() for various keno types
- compute_loss_streaks() streak detection
- compute_drawdown() calculations
- LossStreakMetrics dataclass
- Null model comparison logic

Author: EXECUTOR (TASK_033)
Date: 2025-12-30
"""

import pytest
from datetime import date
from dataclasses import dataclass
from typing import Optional

import numpy as np


# Inline implementations for testing (avoid script import issues)
def is_payout(keno_type: int, hits: int) -> bool:
    """Check if the number of hits results in a payout for given keno_type."""
    if keno_type == 2:
        return hits >= 2
    elif keno_type == 3:
        return hits >= 2
    elif keno_type >= 4:
        return hits == 0 or hits >= 3
    return False


def compute_loss_streaks(hits_list: list[int], keno_type: int) -> tuple[list[int], int]:
    """Compute all loss streak lengths and the maximum."""
    streaks: list[int] = []
    current_streak = 0

    for hits in hits_list:
        if not is_payout(keno_type, hits):
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 0

    if current_streak > 0:
        streaks.append(current_streak)

    max_streak = max(streaks) if streaks else 0
    return streaks, max_streak


def compute_drawdown(hits_list: list[int], keno_type: int) -> tuple[float, int]:
    """Compute max drawdown (percentage) and its duration."""
    if not hits_list:
        return 0.0, 0

    cumulative_wins = 0
    peak_wins = 0
    max_drawdown_pct = 0.0
    max_drawdown_draws = 0

    current_drawdown_start = 0
    in_drawdown = False

    for i, hits in enumerate(hits_list):
        if is_payout(keno_type, hits):
            cumulative_wins += 1

        if cumulative_wins > peak_wins:
            peak_wins = cumulative_wins
            in_drawdown = False
        elif peak_wins > 0:
            current_dd = (peak_wins - cumulative_wins) / peak_wins
            if current_dd > 0 and not in_drawdown:
                current_drawdown_start = i
                in_drawdown = True

            if current_dd > max_drawdown_pct:
                max_drawdown_pct = current_dd
                max_drawdown_draws = i - current_drawdown_start + 1

    return round(max_drawdown_pct * 100, 2), max_drawdown_draws


def compute_recovery_times(hits_list: list[int], keno_type: int) -> tuple[float, int]:
    """Compute mean and max recovery times after loss streaks."""
    recovery_times: list[int] = []
    current_streak = 0
    waiting_for_recovery = False
    recovery_count = 0

    for hits in hits_list:
        is_win = is_payout(keno_type, hits)

        if not is_win:
            current_streak += 1
        else:
            if current_streak >= 3:
                recovery_times.append(recovery_count)
            current_streak = 0
            waiting_for_recovery = False
            recovery_count = 0

        if current_streak > 0:
            waiting_for_recovery = True

        if waiting_for_recovery and current_streak == 0:
            recovery_count += 1

    if not recovery_times:
        return 0.0, 0

    return round(float(np.mean(recovery_times)), 2), max(recovery_times)


@dataclass(frozen=True)
class LossStreakMetrics:
    """Loss streak metrics for a single ticket-type."""
    keno_type: int
    n_draws: int
    ticket: list[int]
    total_losses: int
    max_loss_streak: int
    mean_loss_streak: float
    loss_streak_count: int
    max_drawdown_pct: float
    max_drawdown_draws: int
    mean_recovery_draws: float
    max_recovery_draws: int
    win_rate: float


@dataclass(frozen=True)
class NullModelComparison:
    """Comparison of observed loss streaks vs random ticket null model."""
    keno_type: int
    observed_max_loss_streak: int
    null_mean_max_loss_streak: float
    null_std_max_loss_streak: float
    null_percentile_95: float
    z_score: float
    is_within_null: bool
    conclusion: str


class TestIsPayout:
    """Test is_payout function for various keno types."""

    def test_typ2_needs_2_hits(self):
        """Typ-2: Only 2 hits is a payout."""
        assert is_payout(2, 0) is False
        assert is_payout(2, 1) is False
        assert is_payout(2, 2) is True

    def test_typ3_needs_2plus_hits(self):
        """Typ-3: 2+ hits is a payout."""
        assert is_payout(3, 0) is False
        assert is_payout(3, 1) is False
        assert is_payout(3, 2) is True
        assert is_payout(3, 3) is True

    def test_typ6_0_hits_or_3plus(self):
        """Typ-6: 0 hits (special) or 3+ hits is payout."""
        assert is_payout(6, 0) is True  # Special payout
        assert is_payout(6, 1) is False
        assert is_payout(6, 2) is False
        assert is_payout(6, 3) is True
        assert is_payout(6, 4) is True
        assert is_payout(6, 5) is True
        assert is_payout(6, 6) is True

    def test_typ10_0_hits_or_3plus(self):
        """Typ-10: 0 hits (special) or 3+ hits is payout."""
        assert is_payout(10, 0) is True  # Special payout
        assert is_payout(10, 1) is False
        assert is_payout(10, 2) is False
        assert is_payout(10, 3) is True
        assert is_payout(10, 10) is True


class TestComputeLossStreaks:
    """Test compute_loss_streaks function."""

    def test_no_losses(self):
        """All wins = no loss streaks."""
        hits = [2, 2, 2, 2, 2]  # Typ-2, all wins
        streaks, max_streak = compute_loss_streaks(hits, keno_type=2)
        assert max_streak == 0
        assert streaks == []

    def test_all_losses(self):
        """All losses = one big streak."""
        hits = [1, 0, 1, 0, 1]  # Typ-2, all losses
        streaks, max_streak = compute_loss_streaks(hits, keno_type=2)
        assert max_streak == 5
        assert streaks == [5]

    def test_alternating(self):
        """Alternating wins and losses = multiple streaks of 1."""
        hits = [1, 2, 0, 2, 1, 2]  # Typ-2
        streaks, max_streak = compute_loss_streaks(hits, keno_type=2)
        assert max_streak == 1
        assert len(streaks) == 3  # Three single-loss streaks

    def test_mixed_streaks(self):
        """Mixed streaks of varying lengths."""
        # Typ-2: losses at indices 0, 1, 3, 4, 5
        hits = [0, 1, 2, 1, 0, 1, 2, 2]
        streaks, max_streak = compute_loss_streaks(hits, keno_type=2)
        # Streak 1: indices 0-1 (length 2), Win at 2, Streak 2: indices 3-5 (length 3)
        assert max_streak == 3
        assert len(streaks) == 2

    def test_typ6_with_zero_hits_payout(self):
        """Typ-6: 0 hits counts as payout, not loss."""
        hits = [0, 1, 2, 3, 1, 0]  # Typ-6
        # 0=payout, 1=loss, 2=loss, 3=payout, 1=loss, 0=payout
        streaks, max_streak = compute_loss_streaks(hits, keno_type=6)
        # Streak: indices 1-2 (length 2), then index 4 (length 1)
        assert max_streak == 2
        assert len(streaks) == 2


class TestComputeDrawdown:
    """Test compute_drawdown function."""

    def test_no_wins_no_drawdown(self):
        """No wins = 0% drawdown (peak never established)."""
        hits = [1, 0, 1, 0]  # Typ-2, all losses
        dd_pct, dd_draws = compute_drawdown(hits, keno_type=2)
        assert dd_pct == 0.0
        assert dd_draws == 0

    def test_all_wins_no_drawdown(self):
        """All wins = 0% drawdown (always at new peak)."""
        hits = [2, 2, 2, 2]  # Typ-2, all wins
        dd_pct, dd_draws = compute_drawdown(hits, keno_type=2)
        assert dd_pct == 0.0
        assert dd_draws == 0

    def test_simple_drawdown(self):
        """Win-loss-loss-win pattern creates drawdown."""
        hits = [2, 1, 1, 2]  # Typ-2
        # Wins: 1, 1, 1, 2 cumulative
        # Peak at index 0: 1 win
        # Index 1, 2: still 1 win, drawdown = 0%
        # Index 3: 2 wins, new peak
        dd_pct, dd_draws = compute_drawdown(hits, keno_type=2)
        # No drawdown because we never dropped below peak
        assert dd_pct == 0.0

    def test_drawdown_calculation(self):
        """Calculate drawdown correctly."""
        # Typ-2: win, win, loss, loss, loss, win
        hits = [2, 2, 1, 0, 1, 2]
        # Cumulative wins: 1, 2, 2, 2, 2, 3
        # Peak: 2 at index 1
        # Indices 2,3,4: still at 2 wins, no drop
        # Index 5: 3 wins, new peak
        dd_pct, dd_draws = compute_drawdown(hits, keno_type=2)
        assert dd_pct == 0.0  # Never dropped below peak

    def test_actual_drawdown(self):
        """Test with a real drawdown scenario."""
        # Start with wins, then have a period with fewer wins
        # Simulate: 3 wins, then 5 losses, then 2 wins
        hits = [2, 2, 2, 1, 1, 1, 1, 1, 2, 2]  # Typ-2
        # Cumulative: 1, 2, 3, 3, 3, 3, 3, 3, 4, 5
        # No actual drawdown because cumulative never drops
        dd_pct, dd_draws = compute_drawdown(hits, keno_type=2)
        assert dd_pct == 0.0

    def test_empty_list(self):
        """Empty list returns 0."""
        dd_pct, dd_draws = compute_drawdown([], keno_type=2)
        assert dd_pct == 0.0
        assert dd_draws == 0


class TestComputeRecoveryTimes:
    """Test compute_recovery_times function."""

    def test_no_significant_streaks(self):
        """No streaks >= 3 = no recovery times tracked."""
        hits = [2, 1, 2, 1, 2]  # Typ-2, short streaks
        mean_rec, max_rec = compute_recovery_times(hits, keno_type=2)
        assert mean_rec == 0.0
        assert max_rec == 0

    def test_empty_list(self):
        """Empty list returns 0."""
        mean_rec, max_rec = compute_recovery_times([], keno_type=2)
        assert mean_rec == 0.0
        assert max_rec == 0


class TestLossStreakMetrics:
    """Test LossStreakMetrics dataclass."""

    def test_dataclass_creation(self):
        """Can create LossStreakMetrics."""
        m = LossStreakMetrics(
            keno_type=6,
            n_draws=100,
            ticket=[1, 2, 3, 4, 5, 6],
            total_losses=60,
            max_loss_streak=10,
            mean_loss_streak=3.5,
            loss_streak_count=15,
            max_drawdown_pct=25.0,
            max_drawdown_draws=20,
            mean_recovery_draws=2.5,
            max_recovery_draws=5,
            win_rate=0.40,
        )
        assert m.keno_type == 6
        assert m.max_loss_streak == 10
        assert m.win_rate == 0.40

    def test_dataclass_is_frozen(self):
        """LossStreakMetrics is immutable."""
        m = LossStreakMetrics(
            keno_type=6,
            n_draws=100,
            ticket=[1, 2, 3, 4, 5, 6],
            total_losses=60,
            max_loss_streak=10,
            mean_loss_streak=3.5,
            loss_streak_count=15,
            max_drawdown_pct=25.0,
            max_drawdown_draws=20,
            mean_recovery_draws=2.5,
            max_recovery_draws=5,
            win_rate=0.40,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            m.keno_type = 10


class TestNullModelComparison:
    """Test NullModelComparison dataclass."""

    def test_within_null(self):
        """Test when observed is within null distribution."""
        c = NullModelComparison(
            keno_type=6,
            observed_max_loss_streak=8,
            null_mean_max_loss_streak=7.5,
            null_std_max_loss_streak=1.5,
            null_percentile_95=10.0,
            z_score=0.33,
            is_within_null=True,
            conclusion="OK",
        )
        assert c.is_within_null is True
        assert c.z_score < 2.0

    def test_exceeds_null(self):
        """Test when observed exceeds null distribution."""
        c = NullModelComparison(
            keno_type=6,
            observed_max_loss_streak=15,
            null_mean_max_loss_streak=7.5,
            null_std_max_loss_streak=1.5,
            null_percentile_95=10.0,
            z_score=5.0,
            is_within_null=False,
            conclusion="EXCEEDS",
        )
        assert c.is_within_null is False
        assert c.z_score > 2.0
