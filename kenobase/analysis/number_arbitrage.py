"""Number Arbitrage - Cross-Lottery Number Exploitation.

Goal
----
Exploit lag-based correlations between lottery games for number selection.
Based on ecosystem_graph findings: KENO->AUSWAHLWETTE lag=7, lift=2.41, q=0.027.

Strategy concept: If number X appeared in Game A, number Y in Game B after N days
is more likely (conditional lift > 1).

This module implements:
- Train/test split for rule discovery and evaluation
- Schedule-preserving permutation null models
- Frozen-rules evaluation (no parameter changes in test set)
- EuroJackpot as negative control (should show NO correlation)

Important
---------
Per Axiom A1 (House-Edge), ROI > 0% is physically implausible. Any apparent
positive ROI should trigger a warning (likely overfitting or data issue).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Optional

import numpy as np

from kenobase.analysis.cross_lottery_coupling import (
    ConditionalLift,
    GameDraws,
    _align_source_to_target,
    _presence_matrix,
    bh_fdr,
    conditional_lifts_number_triggers,
)


@dataclass(frozen=True)
class ArbitrageRule:
    """A frozen arbitrage rule discovered in train set."""

    source_game: str
    target_game: str
    trigger_number: int
    target_number: int
    lag_days: int
    train_lift: float
    train_q_value: float
    train_support: int
    train_base_rate: float
    train_conditional_rate: float


@dataclass
class ArbitrageEvaluation:
    """Out-of-sample evaluation of an arbitrage rule."""

    rule: ArbitrageRule
    test_support: int
    test_base_rate: float
    test_conditional_rate: float
    test_lift: float
    test_p_value: float
    is_significant: bool  # test_lift > 1.1 and test_p_value < 0.05


@dataclass
class BacktestResult:
    """Result of backtesting arbitrage rules."""

    train_start: date
    train_end: date
    test_start: date
    test_end: date
    n_rules_discovered: int
    n_rules_significant_test: int
    evaluations: list[ArbitrageEvaluation]
    null_model_lifts: list[float]  # permutation null model results
    negative_control: Optional[dict]  # EuroJackpot results


def split_game_draws_by_date(
    draws: GameDraws,
    split_date: date,
) -> tuple[GameDraws, GameDraws]:
    """Split GameDraws into train (< split_date) and test (>= split_date)."""
    train_mask = [d < split_date for d in draws.dates]
    test_mask = [d >= split_date for d in draws.dates]

    train_idx = [i for i, m in enumerate(train_mask) if m]
    test_idx = [i for i, m in enumerate(test_mask) if m]

    train_dates = [draws.dates[i] for i in train_idx]
    test_dates = [draws.dates[i] for i in test_idx]

    train_presence = draws.presence[train_idx] if train_idx else np.zeros((0, draws.presence.shape[1]), dtype=np.int8)
    test_presence = draws.presence[test_idx] if test_idx else np.zeros((0, draws.presence.shape[1]), dtype=np.int8)

    train_ordered = None
    test_ordered = None
    if draws.ordered_numbers is not None:
        train_ordered = [draws.ordered_numbers[i] for i in train_idx]
        test_ordered = [draws.ordered_numbers[i] for i in test_idx]

    train_jackpot = None
    test_jackpot = None
    if draws.jackpot_winners is not None:
        train_jackpot = {d: v for d, v in draws.jackpot_winners.items() if d < split_date}
        test_jackpot = {d: v for d, v in draws.jackpot_winners.items() if d >= split_date}

    train_draws = GameDraws(
        name=draws.name,
        pool_max=draws.pool_max,
        draw_size=draws.draw_size,
        dates=train_dates,
        presence=train_presence,
        ordered_numbers=train_ordered,
        jackpot_winners=train_jackpot,
    )
    test_draws = GameDraws(
        name=draws.name,
        pool_max=draws.pool_max,
        draw_size=draws.draw_size,
        dates=test_dates,
        presence=test_presence,
        ordered_numbers=test_ordered,
        jackpot_winners=test_jackpot,
    )
    return train_draws, test_draws


def discover_arbitrage_rules(
    source: GameDraws,
    target: GameDraws,
    lag_days: int,
    min_support: int = 30,
    lift_threshold: float = 1.1,
    alpha_fdr: float = 0.05,
    max_rules: int = 50,
) -> list[ArbitrageRule]:
    """Discover arbitrage rules from training data.

    Args:
        source: Source game draws (e.g., KENO)
        target: Target game draws (e.g., AUSWAHLWETTE)
        lag_days: Days between source and target draws
        min_support: Minimum trigger occurrences
        lift_threshold: Minimum lift to consider a rule
        alpha_fdr: FDR threshold for significance
        max_rules: Maximum number of rules to return

    Returns:
        List of ArbitrageRule objects, sorted by q_value then lift
    """
    lifts = conditional_lifts_number_triggers(
        source=source,
        target=target,
        lag_days=lag_days,
        min_support=min_support,
        alpha_fdr=alpha_fdr,
        max_results=max_rules * 2,  # get more candidates for filtering
        filter_by_alpha=True,  # only significant rules
    )

    rules = []
    for lift in lifts:
        if lift.lift >= lift_threshold:
            rules.append(
                ArbitrageRule(
                    source_game=lift.source,
                    target_game=lift.target,
                    trigger_number=int(lift.trigger),
                    target_number=lift.target_number,
                    lag_days=lift.lag_days,
                    train_lift=lift.lift,
                    train_q_value=lift.q_value,
                    train_support=lift.support,
                    train_base_rate=lift.base_rate,
                    train_conditional_rate=lift.conditional_rate,
                )
            )

    # Sort by q_value (lower is better), then by lift (higher is better)
    rules.sort(key=lambda r: (r.train_q_value, -r.train_lift))
    return rules[:max_rules]


def evaluate_rule_on_test(
    rule: ArbitrageRule,
    source_test: GameDraws,
    target_test: GameDraws,
    alpha: float = 0.05,
    lift_threshold: float = 1.1,
) -> ArbitrageEvaluation:
    """Evaluate a frozen arbitrage rule on test data.

    IMPORTANT: No parameters are changed - this is a frozen evaluation.
    """
    from scipy import stats

    pairs = _align_source_to_target(
        source_dates=source_test.dates,
        target_dates=target_test.dates,
        lag_days=rule.lag_days,
    )

    if not pairs:
        return ArbitrageEvaluation(
            rule=rule,
            test_support=0,
            test_base_rate=0.0,
            test_conditional_rate=0.0,
            test_lift=0.0,
            test_p_value=1.0,
            is_significant=False,
        )

    s_idx, t_idx = zip(*pairs, strict=False)
    X = _presence_matrix(source_test, s_idx)
    Y = _presence_matrix(target_test, t_idx)

    n_pairs = len(pairs)
    trigger_col = rule.trigger_number  # 1-indexed
    target_col = rule.target_number  # 1-indexed

    # Count occurrences
    trigger_present = X[:, trigger_col].astype(bool)
    target_present = Y[:, target_col].astype(bool)

    support = int(trigger_present.sum())
    target_total = int(target_present.sum())

    if support == 0:
        return ArbitrageEvaluation(
            rule=rule,
            test_support=0,
            test_base_rate=target_total / max(1, n_pairs),
            test_conditional_rate=0.0,
            test_lift=0.0,
            test_p_value=1.0,
            is_significant=False,
        )

    # 2x2 contingency table
    both = int((trigger_present & target_present).sum())
    a = both
    b = support - both
    c = target_total - both
    d = (n_pairs - support) - c

    if d < 0:
        d = 0  # numeric guard

    base_rate = target_total / max(1, n_pairs)
    conditional_rate = both / support if support > 0 else 0.0
    lift = (conditional_rate / base_rate) if base_rate > 0 else 0.0

    _, p_value = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")

    is_significant = bool(lift >= lift_threshold and p_value < alpha)

    return ArbitrageEvaluation(
        rule=rule,
        test_support=support,
        test_base_rate=base_rate,
        test_conditional_rate=conditional_rate,
        test_lift=lift,
        test_p_value=p_value,
        is_significant=is_significant,
    )


def schedule_preserving_permutation(draws: GameDraws, seed: int = 42) -> GameDraws:
    """Create a schedule-preserving permutation of draws.

    This preserves the draw schedule (dates) but randomly shuffles
    which numbers appear on which date. This is the null model.
    """
    rng = random.Random(seed)
    n_draws = len(draws.dates)

    # Shuffle row indices
    shuffled_idx = list(range(n_draws))
    rng.shuffle(shuffled_idx)

    # Create permuted presence matrix
    permuted_presence = draws.presence[shuffled_idx].copy()

    permuted_ordered = None
    if draws.ordered_numbers is not None:
        permuted_ordered = [draws.ordered_numbers[i] for i in shuffled_idx]

    return GameDraws(
        name=draws.name + "_permuted",
        pool_max=draws.pool_max,
        draw_size=draws.draw_size,
        dates=draws.dates,  # keep original dates
        presence=permuted_presence,
        ordered_numbers=permuted_ordered,
        jackpot_winners=draws.jackpot_winners,  # keep original jackpots
    )


def run_null_model(
    source: GameDraws,
    target: GameDraws,
    lag_days: int,
    n_permutations: int = 100,
    min_support: int = 30,
    seed: int = 42,
) -> list[float]:
    """Run schedule-preserving permutation null model.

    Returns the maximum lift observed in each permutation.
    This establishes the null distribution for comparison.
    """
    max_lifts = []
    for i in range(n_permutations):
        perm_source = schedule_preserving_permutation(source, seed=seed + i)

        lifts = conditional_lifts_number_triggers(
            source=perm_source,
            target=target,
            lag_days=lag_days,
            min_support=min_support,
            alpha_fdr=1.0,  # don't filter
            max_results=1,  # only need max
            filter_by_alpha=False,
        )

        if lifts:
            max_lifts.append(max(r.lift for r in lifts))
        else:
            max_lifts.append(1.0)

    return max_lifts


def backtest_number_arbitrage(
    source: GameDraws,
    target: GameDraws,
    lag_days: int,
    split_date: date,
    negative_control_source: Optional[GameDraws] = None,
    min_support: int = 30,
    lift_threshold: float = 1.1,
    alpha_fdr: float = 0.05,
    max_rules: int = 50,
    n_permutations: int = 100,
    seed: int = 42,
) -> BacktestResult:
    """Complete backtest of number arbitrage strategy.

    Args:
        source: Source game (e.g., KENO)
        target: Target game (e.g., AUSWAHLWETTE)
        lag_days: Days between source and target
        split_date: Date to split train/test (test >= split_date)
        negative_control_source: Optional negative control (e.g., EuroJackpot)
        min_support: Minimum trigger support
        lift_threshold: Minimum lift for rules
        alpha_fdr: FDR threshold
        max_rules: Maximum rules to discover
        n_permutations: Number of null model permutations
        seed: Random seed

    Returns:
        BacktestResult with all evaluations and null model results
    """
    # Split data
    source_train, source_test = split_game_draws_by_date(source, split_date)
    target_train, target_test = split_game_draws_by_date(target, split_date)

    # Discover rules in train set
    rules = discover_arbitrage_rules(
        source=source_train,
        target=target_train,
        lag_days=lag_days,
        min_support=min_support,
        lift_threshold=lift_threshold,
        alpha_fdr=alpha_fdr,
        max_rules=max_rules,
    )

    # Evaluate rules in test set (FROZEN - no parameter changes)
    evaluations = []
    for rule in rules:
        eval_result = evaluate_rule_on_test(
            rule=rule,
            source_test=source_test,
            target_test=target_test,
            alpha=alpha_fdr,
            lift_threshold=lift_threshold,
        )
        evaluations.append(eval_result)

    # Run null model
    null_lifts = run_null_model(
        source=source_train,
        target=target_train,
        lag_days=lag_days,
        n_permutations=n_permutations,
        min_support=min_support,
        seed=seed,
    )

    # Negative control (EuroJackpot - should show NO correlation)
    negative_control = None
    if negative_control_source is not None:
        nc_train, nc_test = split_game_draws_by_date(negative_control_source, split_date)
        nc_rules = discover_arbitrage_rules(
            source=nc_train,
            target=target_train,
            lag_days=lag_days,
            min_support=min_support,
            lift_threshold=lift_threshold,
            alpha_fdr=alpha_fdr,
            max_rules=max_rules,
        )
        nc_evaluations = []
        for rule in nc_rules:
            eval_result = evaluate_rule_on_test(
                rule=rule,
                source_test=nc_test,
                target_test=target_test,
                alpha=alpha_fdr,
                lift_threshold=lift_threshold,
            )
            nc_evaluations.append(eval_result)

        negative_control = {
            "source_game": negative_control_source.name,
            "n_rules_discovered": len(nc_rules),
            "n_rules_significant_test": sum(1 for e in nc_evaluations if e.is_significant),
            "message": "EuroJackpot should show NO significant rules (negative control)",
        }

    # Count significant rules in test
    n_significant = sum(1 for e in evaluations if e.is_significant)

    return BacktestResult(
        train_start=source_train.dates[0] if source_train.dates else split_date,
        train_end=source_train.dates[-1] if source_train.dates else split_date,
        test_start=source_test.dates[0] if source_test.dates else split_date,
        test_end=source_test.dates[-1] if source_test.dates else split_date,
        n_rules_discovered=len(rules),
        n_rules_significant_test=n_significant,
        evaluations=evaluations,
        null_model_lifts=null_lifts,
        negative_control=negative_control,
    )


def roi_sanity_check(lift: float, base_rate: float, house_edge: float = 0.5) -> dict:
    """Check if implied ROI is plausible given Axiom A1 (House-Edge).

    Per CLAUDE.md Section 1.1: House-Edge is 50% redistribution, guaranteed.
    Any ROI > 0% is physically implausible and indicates overfitting.

    Args:
        lift: Observed lift
        base_rate: Base probability of target number appearing
        house_edge: Expected redistribution rate (default 0.5)

    Returns:
        Dict with ROI calculation and warning if implausible
    """
    # Simplified ROI: If we bet on numbers with lift > 1, expected gain is:
    # conditional_rate * payout - 1
    # But payout is bounded by house edge
    conditional_rate = lift * base_rate

    # Theoretical max ROI assuming fair odds (no house edge)
    theoretical_roi_fair = (conditional_rate / base_rate - 1) if base_rate > 0 else 0.0

    # Adjusted for house edge: actual payout = fair_payout * (1 - house_edge)
    # This means actual ROI = theoretical_roi * (1 - house_edge) - house_edge
    adjusted_roi = theoretical_roi_fair * (1 - house_edge) - house_edge

    warning = None
    if adjusted_roi > 0:
        warning = (
            f"WARNING: Implied ROI {adjusted_roi:.1%} > 0% is IMPLAUSIBLE per Axiom A1. "
            "Likely overfitting or data issue. Check null model."
        )

    return {
        "lift": lift,
        "base_rate": base_rate,
        "conditional_rate": conditional_rate,
        "theoretical_roi_fair": theoretical_roi_fair,
        "adjusted_roi": adjusted_roi,
        "house_edge": house_edge,
        "warning": warning,
    }


__all__ = [
    "ArbitrageEvaluation",
    "ArbitrageRule",
    "BacktestResult",
    "backtest_number_arbitrage",
    "discover_arbitrage_rules",
    "evaluate_rule_on_test",
    "roi_sanity_check",
    "run_null_model",
    "schedule_preserving_permutation",
    "split_game_draws_by_date",
]
