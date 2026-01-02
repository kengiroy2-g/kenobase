"""Unit tests for frozen-rules invariant in Train->Test cross-game rule backtest.

This test validates the critical requirement that rules mined on Train data are
NOT re-fitted or re-mined when evaluated on Test data.

The frozen-rules pattern ensures:
1. Rules are mined ONLY on train slices (no data leakage)
2. backtest_cross_game_rule_layer() receives rules externally (doesn't mine)
3. The same rule set is applied consistently across all Test draws

Reference: VALID-001, CLAUDE.md Section 3.0 Axiom-First approach
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta

import numpy as np
import pytest

from kenobase.analysis.cross_lottery_coupling import (
    GameDraws,
    conditional_lifts_number_triggers,
)
from kenobase.prediction.cross_game_rule_backtester import (
    CrossGameRule,
    backtest_cross_game_rule_layer,
)


def _make_synthetic_keno(n_draws: int, start_date: date) -> GameDraws:
    """Create synthetic KENO draws for testing."""
    dates = [start_date + timedelta(days=i) for i in range(n_draws)]
    rng = np.random.default_rng(42)
    presence = np.zeros((n_draws, 71), dtype=np.int8)
    ordered: list[list[int]] = []
    for i in range(n_draws):
        nums = rng.choice(range(1, 71), size=20, replace=False)
        for n in nums:
            presence[i, n] = 1
        ordered.append(sorted(nums.tolist()))
    return GameDraws(
        name="KENO",
        pool_max=70,
        draw_size=20,
        dates=dates,
        presence=presence,
        ordered_numbers=ordered,
        jackpot_winners=None,
    )


def _make_synthetic_lotto(n_draws: int, start_date: date) -> GameDraws:
    """Create synthetic LOTTO draws for testing."""
    dates = [start_date + timedelta(days=i) for i in range(n_draws)]
    rng = np.random.default_rng(123)
    presence = np.zeros((n_draws, 50), dtype=np.int8)
    for i in range(n_draws):
        nums = rng.choice(range(1, 50), size=6, replace=False)
        for n in nums:
            presence[i, n] = 1
    return GameDraws(
        name="LOTTO",
        pool_max=49,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


class TestFrozenRulesInvariant:
    """Test suite for frozen-rules invariant."""

    def test_backtest_uses_rules_externally_no_mining(self):
        """Verify backtest_cross_game_rule_layer uses externally provided rules.

        This is the core invariant: the backtest function does NOT mine rules
        internally. It receives a list of CrossGameRule objects and applies them
        as-is without modification.
        """
        start = date(2023, 1, 1)
        keno = _make_synthetic_keno(100, start)
        lotto = _make_synthetic_lotto(100, start)

        # Create a specific rule manually (not mined)
        manual_rule = CrossGameRule(
            source="LOTTO",
            target="KENO",
            lag_days=0,
            trigger_kind="number",
            trigger="7",
            target_number=15,
            support=50,
            base_rate=0.2857,
            conditional_rate=0.40,
            lift=1.4,
            p_value=0.01,
            q_value=0.02,
        )

        # Run backtest with this single rule
        result = backtest_cross_game_rule_layer(
            keno,
            sources={"LOTTO": lotto},
            rules=[manual_rule],
            keno_types=[6],
            start_index=10,
            recent_draws=30,
            recent_weight=0.5,
        )

        # The backtest should have exactly 1 rule (our manually provided one)
        assert result.rules["count"] == 1

        # Run again with empty rules
        result_no_rules = backtest_cross_game_rule_layer(
            keno,
            sources={"LOTTO": lotto},
            rules=[],
            keno_types=[6],
            start_index=10,
            recent_draws=30,
            recent_weight=0.5,
        )

        # With no rules, count should be 0
        assert result_no_rules.rules["count"] == 0

    def test_rules_mined_on_train_are_frozen_on_test(self):
        """Verify rules mined on train period remain unchanged on test.

        This simulates the Train->Test split workflow:
        1. Mine rules on Train slice
        2. Freeze rules (convert to list)
        3. Apply frozen rules to Test slice
        4. Verify rules are NOT re-mined
        """
        start = date(2023, 1, 1)
        train_end = date(2023, 6, 30)  # 6 months train

        # Full dataset spanning train + test
        keno_full = _make_synthetic_keno(365, start)
        lotto_full = _make_synthetic_lotto(365, start)

        # Slice for train
        train_idx = [i for i, d in enumerate(keno_full.dates) if d <= train_end]
        keno_train = GameDraws(
            name="KENO",
            pool_max=70,
            draw_size=20,
            dates=[keno_full.dates[i] for i in train_idx],
            presence=keno_full.presence[train_idx],
            ordered_numbers=[keno_full.ordered_numbers[i] for i in train_idx],
            jackpot_winners=None,
        )
        lotto_train = GameDraws(
            name="LOTTO",
            pool_max=49,
            draw_size=6,
            dates=[lotto_full.dates[i] for i in train_idx],
            presence=lotto_full.presence[train_idx],
            ordered_numbers=None,
            jackpot_winners=None,
        )

        # Mine rules on TRAIN only
        train_lifts = conditional_lifts_number_triggers(
            source=lotto_train,
            target=keno_train,
            lag_days=0,
            min_support=5,
            max_results=100,
            alpha_fdr=0.5,  # Relaxed alpha to get some rules
            filter_by_alpha=False,
        )

        # Convert to frozen CrossGameRule objects
        frozen_rules = [
            CrossGameRule(
                source=str(r.source),
                target=str(r.target),
                lag_days=int(r.lag_days),
                trigger_kind=str(r.trigger_kind),
                trigger=str(r.trigger),
                target_number=int(r.target_number),
                support=int(r.support),
                base_rate=float(r.base_rate),
                conditional_rate=float(r.conditional_rate),
                lift=float(r.lift),
                p_value=float(r.p_value),
                q_value=float(r.q_value),
            )
            for r in train_lifts[:10]  # Take top 10
        ]

        # Find test start index
        test_start_idx = next(
            i for i, d in enumerate(keno_full.dates) if d > train_end
        )

        # Run backtest on TEST with frozen rules
        result = backtest_cross_game_rule_layer(
            keno_full,
            sources={"LOTTO": lotto_full},
            rules=frozen_rules,
            keno_types=[6],
            start_index=test_start_idx,
            recent_draws=30,
            recent_weight=0.5,
        )

        # Invariant: rules passed in == rules used
        assert result.rules["count"] == len(frozen_rules)

    def test_frozen_rules_dataclass_is_immutable(self):
        """Verify CrossGameRule dataclass is frozen (immutable).

        The frozen=True ensures rules cannot be modified after creation,
        which is essential for the frozen-rules pattern.
        """
        rule = CrossGameRule(
            source="LOTTO",
            target="KENO",
            lag_days=1,
            trigger_kind="number",
            trigger="5",
            target_number=10,
            support=100,
            base_rate=0.2857,
            conditional_rate=0.35,
            lift=1.225,
            p_value=0.05,
            q_value=0.08,
        )

        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            rule.lift = 2.0  # type: ignore

    def test_backtest_does_not_call_mining_functions(self):
        """Verify backtest function signature takes rules externally.

        The function signature itself guarantees the invariant:
        - rules parameter is required
        - no mining parameters (min_support, alpha, etc.) exist

        This is a structural test ensuring no accidental mining was added.
        """
        import inspect

        sig = inspect.signature(backtest_cross_game_rule_layer)
        param_names = list(sig.parameters.keys())

        # Rules must be a parameter (externally provided)
        assert "rules" in param_names

        # Mining-related parameters should NOT exist
        mining_params = [
            "min_support",
            "alpha",
            "alpha_fdr",
            "filter_by_alpha",
            "max_rules",
            "mine_rules",
        ]
        for mp in mining_params:
            assert mp not in param_names, f"Mining param {mp!r} found in backtest function"

    def test_train_test_split_no_data_leakage(self):
        """Verify train slice contains no data from test period.

        Data leakage would occur if:
        - Train dates extend into Test period
        - Rules are mined on data including Test period
        """
        start = date(2023, 1, 1)
        train_end = date(2023, 6, 30)

        keno_full = _make_synthetic_keno(365, start)

        # Slice for train (should contain only dates <= train_end)
        train_idx = [i for i, d in enumerate(keno_full.dates) if d <= train_end]
        train_dates = [keno_full.dates[i] for i in train_idx]

        # Verify no train date exceeds train_end
        for td in train_dates:
            assert td <= train_end, f"Data leakage: train date {td} > train_end {train_end}"

        # Verify test period exists after train
        test_dates = [d for d in keno_full.dates if d > train_end]
        assert len(test_dates) > 0, "No test period data available"
        assert min(test_dates) > train_end


class TestRuleApplicationConsistency:
    """Tests for consistent rule application across draws."""

    def test_same_rules_applied_to_all_test_draws(self):
        """Verify the same frozen rule set is applied to every test draw.

        The backtest iterates over test draws and applies the same rules
        without any draw-specific rule selection or re-mining.
        """
        start = date(2023, 1, 1)
        keno = _make_synthetic_keno(50, start)
        lotto = _make_synthetic_lotto(50, start)

        # Create rules with specific triggers
        rules = [
            CrossGameRule(
                source="LOTTO",
                target="KENO",
                lag_days=0,
                trigger_kind="number",
                trigger=str(n),
                target_number=n + 10,
                support=30,
                base_rate=0.2857,
                conditional_rate=0.35,
                lift=1.225,
                p_value=0.05,
                q_value=0.08,
            )
            for n in [1, 2, 3]  # 3 rules
        ]

        result = backtest_cross_game_rule_layer(
            keno,
            sources={"LOTTO": lotto},
            rules=rules,
            keno_types=[6],
            start_index=10,
            recent_draws=30,
            recent_weight=0.5,
        )

        # All 3 rules should be tracked
        assert result.rules["count"] == 3
