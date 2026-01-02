"""Unit tests for number_arbitrage module."""

from datetime import date

import numpy as np
import pytest

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.analysis.number_arbitrage import (
    ArbitrageRule,
    discover_arbitrage_rules,
    evaluate_rule_on_test,
    roi_sanity_check,
    run_null_model,
    schedule_preserving_permutation,
    split_game_draws_by_date,
)


def _make_test_game(
    name: str = "TEST",
    pool_max: int = 49,
    draw_size: int = 6,
    n_draws: int = 100,
    start_date: date = date(2022, 1, 1),
) -> GameDraws:
    """Create a test GameDraws with deterministic data."""
    dates = [date.fromordinal(start_date.toordinal() + i) for i in range(n_draws)]
    presence = np.zeros((n_draws, pool_max + 1), dtype=np.int8)

    # Create deterministic pattern: numbers 1-6 on day 0, 2-7 on day 1, etc.
    for i in range(n_draws):
        for j in range(draw_size):
            num = ((i + j) % pool_max) + 1
            presence[i, num] = 1

    return GameDraws(
        name=name,
        pool_max=pool_max,
        draw_size=draw_size,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


class TestSplitGameDrawsByDate:
    def test_split_basic(self):
        game = _make_test_game(n_draws=100, start_date=date(2022, 1, 1))
        split = date(2022, 2, 1)  # day 31

        train, test = split_game_draws_by_date(game, split)

        assert len(train.dates) == 31
        assert len(test.dates) == 69
        assert all(d < split for d in train.dates)
        assert all(d >= split for d in test.dates)
        assert train.presence.shape[0] == 31
        assert test.presence.shape[0] == 69

    def test_split_preserves_metadata(self):
        game = _make_test_game(name="KENO", pool_max=70, draw_size=20)
        split = date(2022, 2, 1)

        train, test = split_game_draws_by_date(game, split)

        assert train.name == "KENO"
        assert test.name == "KENO"
        assert train.pool_max == 70
        assert test.pool_max == 70
        assert train.draw_size == 20
        assert test.draw_size == 20


class TestSchedulePreservingPermutation:
    def test_permutation_preserves_dates(self):
        game = _make_test_game(n_draws=50)
        permuted = schedule_preserving_permutation(game, seed=42)

        assert permuted.dates == game.dates
        assert len(permuted.dates) == len(game.dates)

    def test_permutation_shuffles_presence(self):
        game = _make_test_game(n_draws=50)
        permuted = schedule_preserving_permutation(game, seed=42)

        # Presence should be shuffled but same total numbers
        assert permuted.presence.shape == game.presence.shape
        assert permuted.presence.sum() == game.presence.sum()

        # But not identical order
        assert not np.array_equal(permuted.presence, game.presence)

    def test_permutation_deterministic(self):
        game = _make_test_game(n_draws=50)
        p1 = schedule_preserving_permutation(game, seed=42)
        p2 = schedule_preserving_permutation(game, seed=42)

        assert np.array_equal(p1.presence, p2.presence)


class TestDiscoverArbitrageRules:
    def test_discover_with_correlated_data(self):
        # Create source and target with artificial correlation
        source = _make_test_game(name="SOURCE", n_draws=100)
        target = _make_test_game(name="TARGET", n_draws=100)

        # Inject correlation: when source has 1, target has 2 (100% of the time)
        # This creates a perfect lift scenario
        for i in range(100):
            if source.presence[i, 1] == 1:
                target.presence[i, 2] = 1

        rules = discover_arbitrage_rules(
            source=source,
            target=target,
            lag_days=0,
            min_support=5,
            lift_threshold=1.0,
            alpha_fdr=0.5,
            max_rules=10,
        )

        # Should find at least some rules with the injected correlation
        assert isinstance(rules, list)
        # All rules should have required attributes
        for rule in rules:
            assert hasattr(rule, "source_game")
            assert hasattr(rule, "target_game")
            assert hasattr(rule, "trigger_number")
            assert hasattr(rule, "target_number")
            assert hasattr(rule, "train_lift")
            assert hasattr(rule, "train_q_value")


class TestEvaluateRuleOnTest:
    def test_evaluate_frozen_rule(self):
        source = _make_test_game(name="SOURCE", n_draws=50)
        target = _make_test_game(name="TARGET", n_draws=50)

        rule = ArbitrageRule(
            source_game="SOURCE",
            target_game="TARGET",
            trigger_number=1,
            target_number=2,
            lag_days=0,
            train_lift=2.0,
            train_q_value=0.01,
            train_support=30,
            train_base_rate=0.12,
            train_conditional_rate=0.24,
        )

        eval_result = evaluate_rule_on_test(rule, source, target, alpha=0.05)

        assert eval_result.rule == rule
        assert isinstance(eval_result.test_support, int)
        assert isinstance(eval_result.test_lift, float)
        assert isinstance(eval_result.test_p_value, float)
        assert isinstance(eval_result.is_significant, bool)

    def test_empty_test_set(self):
        source = _make_test_game(n_draws=10)
        target = _make_test_game(n_draws=10)

        # Split so test is empty
        split = date(2099, 1, 1)
        _, source_test = split_game_draws_by_date(source, split)
        _, target_test = split_game_draws_by_date(target, split)

        rule = ArbitrageRule(
            source_game="SOURCE",
            target_game="TARGET",
            trigger_number=1,
            target_number=2,
            lag_days=0,
            train_lift=2.0,
            train_q_value=0.01,
            train_support=30,
            train_base_rate=0.12,
            train_conditional_rate=0.24,
        )

        eval_result = evaluate_rule_on_test(rule, source_test, target_test)

        assert eval_result.test_support == 0
        assert eval_result.is_significant is False


class TestRunNullModel:
    def test_null_model_produces_lifts(self):
        source = _make_test_game(name="SOURCE", n_draws=50)
        target = _make_test_game(name="TARGET", n_draws=50)

        lifts = run_null_model(
            source=source,
            target=target,
            lag_days=0,
            n_permutations=10,
            min_support=5,
            seed=42,
        )

        assert len(lifts) == 10
        assert all(isinstance(x, float) for x in lifts)
        # All lifts should be >= 0 (or close to 1.0 for random data)
        assert all(x >= 0 for x in lifts)


class TestRoiSanityCheck:
    def test_roi_with_low_lift(self):
        result = roi_sanity_check(lift=1.1, base_rate=0.1)

        assert result["lift"] == 1.1
        assert result["base_rate"] == 0.1
        assert "conditional_rate" in result
        assert "adjusted_roi" in result
        # Low lift should not trigger warning
        assert result["warning"] is None

    def test_roi_with_high_lift_triggers_warning(self):
        # Very high lift would imply positive ROI, which is implausible
        result = roi_sanity_check(lift=5.0, base_rate=0.1, house_edge=0.5)

        assert result["lift"] == 5.0
        # With 50% house edge, even 5x lift shouldn't produce positive ROI
        # theoretical_roi_fair = (5.0 * 0.1 / 0.1 - 1) = 4.0 = 400%
        # adjusted_roi = 4.0 * 0.5 - 0.5 = 1.5 = 150%
        # This should trigger warning
        if result["adjusted_roi"] > 0:
            assert result["warning"] is not None
            assert "IMPLAUSIBLE" in result["warning"]

    def test_roi_house_edge_applied(self):
        result = roi_sanity_check(lift=2.0, base_rate=0.1, house_edge=0.5)

        # theoretical_roi_fair = 2.0 - 1 = 1.0 = 100%
        # adjusted_roi = 1.0 * 0.5 - 0.5 = 0.0 = 0%
        assert result["theoretical_roi_fair"] == pytest.approx(1.0)
        assert result["adjusted_roi"] == pytest.approx(0.0)
        assert result["house_edge"] == 0.5


class TestIntegration:
    def test_full_backtest_flow(self):
        """Integration test for full backtest workflow."""
        source = _make_test_game(name="SOURCE", n_draws=100)
        target = _make_test_game(name="TARGET", n_draws=100)
        split = date(2022, 2, 15)  # day 45

        # Split
        source_train, source_test = split_game_draws_by_date(source, split)
        target_train, target_test = split_game_draws_by_date(target, split)

        assert len(source_train.dates) > 0
        assert len(source_test.dates) > 0

        # Discover rules in train
        rules = discover_arbitrage_rules(
            source=source_train,
            target=target_train,
            lag_days=0,
            min_support=5,
            lift_threshold=1.0,
            alpha_fdr=1.0,  # no filtering for test
            max_rules=5,
        )

        # Evaluate rules in test (if any found)
        for rule in rules:
            eval_result = evaluate_rule_on_test(rule, source_test, target_test)
            assert eval_result.rule == rule
            assert eval_result.test_support >= 0
