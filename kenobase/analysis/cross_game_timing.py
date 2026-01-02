"""Cross-Game Timing Analysis - Multi-Lottery Timing Signals.

This module extends strategy_from_ecosystem.py for cross-game timing.

Key Findings (from TRANS-005 / Ecosystem Graph):
- Only 1 robust edge: KENO->AUSWAHLWETTE lag=7, lift=2.41
- Pattern-to-Pattern coupling is too weak for strategies
- Timing-based signals (WHEN to play) are the valid approach

Architecture:
- Uses draw schedules of multiple lotteries as timing signals
- Computes hit-rate improvement when playing on favorable timing days
- Validates via schedule-preserving permutation null model

Draw Schedules (German Lotteries):
- KENO: Daily
- LOTTO 6aus49: Wed + Sat
- Auswahlwette: Saturday only
- Eurowette: Saturday only
- Gluecksspirale: Saturday only
- EuroJackpot: Tue + Fri (NOT part of German ecosystem - control only)
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np
from scipy import stats


@dataclass
class DrawSchedule:
    """Draw schedule for a lottery game."""

    game: str
    weekdays: list[int]  # 0=Monday, 6=Sunday
    description: str

    def has_draw_on(self, d: date) -> bool:
        """Check if this game has a draw on given date."""
        return d.weekday() in self.weekdays

    def days_until_next_draw(self, d: date) -> int:
        """Days until next draw from given date (0 if draw today)."""
        for offset in range(8):
            check = d + timedelta(days=offset)
            if self.has_draw_on(check):
                return offset
        return 7  # fallback

    def days_since_last_draw(self, d: date) -> int:
        """Days since last draw from given date (0 if draw today)."""
        for offset in range(8):
            check = d - timedelta(days=offset)
            if self.has_draw_on(check):
                return offset
        return 7  # fallback


# German lottery draw schedules
SCHEDULES = {
    "KENO": DrawSchedule("KENO", list(range(7)), "Daily"),
    "LOTTO": DrawSchedule("LOTTO", [2, 5], "Wed + Sat"),  # Wed=2, Sat=5
    "AUSWAHLWETTE": DrawSchedule("AUSWAHLWETTE", [5], "Saturday"),
    "EUROWETTE": DrawSchedule("EUROWETTE", [5], "Saturday"),
    "GLUECKSSPIRALE": DrawSchedule("GLUECKSSPIRALE", [5], "Saturday"),
    "EUROJACKPOT": DrawSchedule("EUROJACKPOT", [1, 4], "Tue + Fri"),  # Control
}


@dataclass
class TimingSignal:
    """Timing signal for a specific date."""

    date: date
    signal_name: str  # e.g., "pre_lotto_1d", "post_aw_lag7"
    signal_value: int  # typically 0/1 or days
    source_game: str
    target_game: str


@dataclass
class CrossGameTimingResult:
    """Result of cross-game timing analysis."""

    source_game: str
    target_game: str
    lag_days: int
    signal_name: str
    n_draws_total: int
    n_draws_favorable: int
    n_draws_unfavorable: int
    hit_rate_baseline: float
    hit_rate_favorable: float
    hit_rate_unfavorable: float
    hit_rate_improvement_pct: float
    p_value: Optional[float]
    is_significant: bool
    null_model: str


@dataclass
class PermutationTestResult:
    """Result of schedule-preserving permutation test."""

    observed_stat: float
    null_mean: float
    null_std: float
    p_value: float
    n_permutations: int
    is_significant: bool


def compute_timing_signals(
    dates: list[date],
    target_game: str = "KENO",
) -> list[dict]:
    """Compute timing signals for each date relative to other games.

    Args:
        dates: List of dates to analyze (typically KENO draw dates)
        target_game: The game we're analyzing timing for

    Returns:
        List of dicts with timing signal info per date
    """
    signals = []
    target_schedule = SCHEDULES.get(target_game)

    for d in dates:
        signal_dict = {"date": d}

        for game, schedule in SCHEDULES.items():
            if game == target_game:
                continue

            # Pre/post draw signals
            days_since = schedule.days_since_last_draw(d)
            days_until = schedule.days_until_next_draw(d)

            signal_dict[f"days_since_{game.lower()}"] = days_since
            signal_dict[f"days_until_{game.lower()}"] = days_until
            signal_dict[f"is_{game.lower()}_draw_day"] = 1 if days_since == 0 else 0

            # Specific lag signals (from ecosystem graph: lag=7 for KENO->AW)
            signal_dict[f"post_{game.lower()}_lag7"] = 1 if days_since == 7 else 0

        signals.append(signal_dict)

    return signals


def analyze_timing_effect(
    dates: list[date],
    hits: list[int],  # 1 if "hit" on that date, 0 otherwise
    signal_name: str,
    signal_values: list[int],  # Binary: 1=favorable, 0=unfavorable
    alpha: float = 0.05,
) -> CrossGameTimingResult:
    """Analyze the effect of a timing signal on hit rate.

    Args:
        dates: List of dates
        hits: Binary hit indicator per date (e.g., matches >= threshold)
        signal_name: Name of the timing signal being analyzed
        signal_values: Binary signal (1=favorable timing, 0=not)
        alpha: Significance level

    Returns:
        CrossGameTimingResult with hit rate comparison
    """
    if len(dates) != len(hits) or len(dates) != len(signal_values):
        raise ValueError("dates, hits, and signal_values must have same length")

    hits_arr = np.array(hits)
    signals_arr = np.array(signal_values)

    favorable_mask = signals_arr == 1
    unfavorable_mask = signals_arr == 0

    n_total = len(dates)
    n_favorable = favorable_mask.sum()
    n_unfavorable = unfavorable_mask.sum()

    hit_rate_baseline = hits_arr.mean() if n_total > 0 else 0.0
    hit_rate_favorable = hits_arr[favorable_mask].mean() if n_favorable > 0 else 0.0
    hit_rate_unfavorable = hits_arr[unfavorable_mask].mean() if n_unfavorable > 0 else 0.0

    # Improvement percentage
    if hit_rate_baseline > 0:
        improvement = ((hit_rate_favorable / hit_rate_baseline) - 1) * 100
    else:
        improvement = 0.0

    # Fisher exact test for significance
    p_value = None
    if n_favorable > 0 and n_unfavorable > 0:
        a = hits_arr[favorable_mask].sum()
        b = n_favorable - a
        c = hits_arr[unfavorable_mask].sum()
        d = n_unfavorable - c
        _, p_value = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")

    is_significant = p_value is not None and p_value < alpha

    # Parse signal name to extract source/target
    parts = signal_name.split("_")
    source_game = parts[1].upper() if len(parts) > 1 else "UNKNOWN"
    lag_days = 7 if "lag7" in signal_name else 0

    return CrossGameTimingResult(
        source_game=source_game,
        target_game="KENO",  # Default target
        lag_days=lag_days,
        signal_name=signal_name,
        n_draws_total=n_total,
        n_draws_favorable=int(n_favorable),
        n_draws_unfavorable=int(n_unfavorable),
        hit_rate_baseline=float(hit_rate_baseline),
        hit_rate_favorable=float(hit_rate_favorable),
        hit_rate_unfavorable=float(hit_rate_unfavorable),
        hit_rate_improvement_pct=float(improvement),
        p_value=float(p_value) if p_value is not None else None,
        is_significant=bool(is_significant),
        null_model="fisher_exact",
    )


def schedule_preserving_permutation_test(
    dates: list[date],
    hits: list[int],
    signal_values: list[int],
    n_permutations: int = 1000,
    alpha: float = 0.05,
    seed: Optional[int] = None,
) -> PermutationTestResult:
    """Schedule-preserving permutation test for timing effects.

    The null model preserves the weekly structure of signals by permuting
    only within same-weekday blocks. This accounts for weekly seasonality.

    Args:
        dates: List of dates
        hits: Binary hit indicator per date
        signal_values: Binary timing signal
        n_permutations: Number of permutations
        alpha: Significance level
        seed: Random seed for reproducibility

    Returns:
        PermutationTestResult with p-value from permutation null
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    hits_arr = np.array(hits)
    signals_arr = np.array(signal_values)

    # Observed statistic: hit rate difference (favorable - unfavorable)
    favorable_mask = signals_arr == 1
    unfavorable_mask = signals_arr == 0

    if favorable_mask.sum() == 0 or unfavorable_mask.sum() == 0:
        return PermutationTestResult(
            observed_stat=0.0,
            null_mean=0.0,
            null_std=0.0,
            p_value=1.0,
            n_permutations=0,
            is_significant=False,
        )

    observed_diff = hits_arr[favorable_mask].mean() - hits_arr[unfavorable_mask].mean()

    # Group by weekday for schedule-preserving permutation
    weekday_groups: dict[int, list[int]] = {}
    for i, d in enumerate(dates):
        wd = d.weekday()
        if wd not in weekday_groups:
            weekday_groups[wd] = []
        weekday_groups[wd].append(i)

    null_diffs = []
    for _ in range(n_permutations):
        # Permute hits within each weekday group
        perm_hits = np.copy(hits_arr)
        for indices in weekday_groups.values():
            if len(indices) > 1:
                subset = perm_hits[indices]
                np.random.shuffle(subset)
                perm_hits[indices] = subset

        # Compute statistic on permuted data
        perm_fav = perm_hits[favorable_mask].mean()
        perm_unfav = perm_hits[unfavorable_mask].mean()
        null_diffs.append(perm_fav - perm_unfav)

    null_diffs_arr = np.array(null_diffs)
    null_mean = null_diffs_arr.mean()
    null_std = null_diffs_arr.std()

    # Two-sided p-value: proportion of null diffs >= |observed|
    p_value = (np.abs(null_diffs_arr) >= np.abs(observed_diff)).mean()

    return PermutationTestResult(
        observed_stat=float(observed_diff),
        null_mean=float(null_mean),
        null_std=float(null_std),
        p_value=float(p_value),
        n_permutations=n_permutations,
        is_significant=bool(p_value < alpha),
    )


def run_cross_game_timing_analysis(
    keno_dates: list[date],
    keno_hits: list[int],
    signal_names: Optional[list[str]] = None,
    use_permutation_test: bool = True,
    n_permutations: int = 1000,
    alpha: float = 0.05,
    seed: Optional[int] = 42,
) -> dict:
    """Run full cross-game timing analysis.

    Based on ecosystem graph finding:
    - KENO->AUSWAHLWETTE lag=7, lift=2.41 (only robust edge)

    Args:
        keno_dates: List of KENO draw dates
        keno_hits: Binary hit indicator per KENO draw
        signal_names: Optional list of signals to test (default: key signals)
        use_permutation_test: Whether to run permutation validation
        n_permutations: Number of permutations for null model
        alpha: Significance level
        seed: Random seed

    Returns:
        Dict with analysis results
    """
    # Compute timing signals for all dates
    signals = compute_timing_signals(keno_dates, target_game="KENO")

    # Default signals to test (based on ecosystem graph)
    if signal_names is None:
        signal_names = [
            "post_lotto_lag7",
            "post_auswahlwette_lag7",  # Key finding from ecosystem graph
            "post_eurowette_lag7",
            "is_lotto_draw_day",
            "is_auswahlwette_draw_day",
        ]

    results = []
    for sig_name in signal_names:
        # Extract signal values
        try:
            sig_values = [s.get(sig_name, 0) for s in signals]
        except KeyError:
            continue

        if sum(sig_values) == 0:
            continue  # No favorable days for this signal

        # Analyze timing effect
        timing_result = analyze_timing_effect(
            dates=keno_dates,
            hits=keno_hits,
            signal_name=sig_name,
            signal_values=sig_values,
            alpha=alpha,
        )

        result_dict = asdict(timing_result)

        # Optional permutation test
        if use_permutation_test and sum(sig_values) > 0:
            perm_result = schedule_preserving_permutation_test(
                dates=keno_dates,
                hits=keno_hits,
                signal_values=sig_values,
                n_permutations=n_permutations,
                alpha=alpha,
                seed=seed,
            )
            result_dict["permutation_test"] = asdict(perm_result)
            # Override significance with permutation test result
            result_dict["is_significant_permutation"] = perm_result.is_significant

        results.append(result_dict)

    # Summary
    significant_signals = [
        r for r in results
        if r.get("is_significant") or r.get("is_significant_permutation", False)
    ]

    return {
        "analysis": "cross_game_timing",
        "target_game": "KENO",
        "n_dates": len(keno_dates),
        "signals_tested": len(results),
        "significant_signals": len(significant_signals),
        "alpha": alpha,
        "permutation_test_used": use_permutation_test,
        "results": results,
        "axiom_basis": {
            "source": "TRANS-005 / Ecosystem Graph",
            "key_finding": "KENO->AUSWAHLWETTE lag=7, lift=2.41 (only robust edge)",
            "paradigm": "Pattern->Timing shift - WHEN to play, not WHAT numbers",
            "null_model": "Schedule-preserving permutation (weekday blocks)",
        },
    }


__all__ = [
    "DrawSchedule",
    "SCHEDULES",
    "TimingSignal",
    "CrossGameTimingResult",
    "PermutationTestResult",
    "compute_timing_signals",
    "analyze_timing_effect",
    "schedule_preserving_permutation_test",
    "run_cross_game_timing_analysis",
]
