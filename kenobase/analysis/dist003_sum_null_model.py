"""DIST-003: Sum distribution null-model check (expected vs observed).

Why this exists
---------------
The sum of 20 distinct numbers drawn from 1..70 is **not** uniformly distributed.
It is close to a bell curve around ~710.

This module provides an *exact* null model for the sum distribution:
Uniform random selection of 20 numbers without replacement from 1..70.
It allows goodness-of-fit tests against the correct expected distribution (instead
of a uniform-bin test, which will be "significant" by construction).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats


@dataclass
class SumNullModelFit:
    numbers_min: int
    numbers_max: int
    numbers_drawn: int
    total_draws: int
    observed_sum_min: int
    observed_sum_max: int
    expected_mean: float
    expected_std: float
    chi2_statistic: float
    chi2_p_value: float
    degrees_of_freedom: int
    bins_used: int
    bin_width: int
    note: str = ""


def exact_sum_counts(
    *,
    numbers_min: int,
    numbers_max: int,
    numbers_drawn: int,
) -> dict[int, int]:
    """Exact distribution of sum for choosing `numbers_drawn` distinct ints from [min..max].

    Returns a mapping: sum_value -> number_of_combinations.
    """
    if numbers_min != 1:
        # Shift to 1..N then shift sums back
        shift = numbers_min - 1
        shifted = exact_sum_counts(
            numbers_min=1,
            numbers_max=numbers_max - shift,
            numbers_drawn=numbers_drawn,
        )
        return {s + shift * numbers_drawn: c for s, c in shifted.items()}

    n = numbers_max
    k = numbers_drawn

    if k <= 0 or k > n:
        return {}

    max_sum = sum(range(n - k + 1, n + 1))
    dp = [[0] * (max_sum + 1) for _ in range(k + 1)]
    dp[0][0] = 1

    for value in range(1, n + 1):
        for j in range(min(k, value), 0, -1):
            for s in range(max_sum, value - 1, -1):
                dp[j][s] += dp[j - 1][s - value]

    return {s: dp[k][s] for s in range(max_sum + 1) if dp[k][s] > 0}


def _expected_stats_from_counts(counts: dict[int, int]) -> tuple[float, float]:
    total = sum(counts.values())
    if total <= 0:
        return 0.0, 0.0
    mean = sum(s * c for s, c in counts.items()) / total
    var = sum(((s - mean) ** 2) * c for s, c in counts.items()) / total
    return float(mean), float(math.sqrt(var))


def fit_sum_null_model(
    sums: list[int],
    *,
    numbers_min: int = 1,
    numbers_max: int = 70,
    numbers_drawn: int = 20,
    bin_width: int = 20,
    range_min: Optional[int] = None,
    range_max: Optional[int] = None,
) -> SumNullModelFit:
    """Compare observed sums to the exact expected distribution via chi-square."""
    if not sums:
        return SumNullModelFit(
            numbers_min=numbers_min,
            numbers_max=numbers_max,
            numbers_drawn=numbers_drawn,
            total_draws=0,
            observed_sum_min=0,
            observed_sum_max=0,
            expected_mean=0.0,
            expected_std=0.0,
            chi2_statistic=0.0,
            chi2_p_value=1.0,
            degrees_of_freedom=0,
            bins_used=0,
            bin_width=bin_width,
            note="no sums provided",
        )

    counts = exact_sum_counts(
        numbers_min=numbers_min,
        numbers_max=numbers_max,
        numbers_drawn=numbers_drawn,
    )
    total_combos = math.comb(numbers_max - numbers_min + 1, numbers_drawn)
    expected_mean, expected_std = _expected_stats_from_counts(counts)

    sums_arr = np.asarray(sums, dtype=int)
    obs_min = int(sums_arr.min())
    obs_max = int(sums_arr.max())

    theoretical_min = sum(range(numbers_min, numbers_min + numbers_drawn))
    theoretical_max = sum(range(numbers_max - numbers_drawn + 1, numbers_max + 1))

    r_min = int(range_min) if range_min is not None else theoretical_min
    r_max = int(range_max) if range_max is not None else theoretical_max
    # `np.arange` stop is exclusive, so add +1 to guarantee the last edge is included.
    bins = np.arange(r_min, r_max + bin_width + 1, bin_width, dtype=int)
    observed, bin_edges = np.histogram(sums_arr, bins=bins)

    # Expected counts per bin from exact PMF
    expected = np.zeros_like(observed, dtype=float)
    for i in range(len(observed)):
        start = int(bin_edges[i])
        end = int(bin_edges[i + 1])
        prob = sum(c for s, c in counts.items() if start <= s < end) / total_combos
        expected[i] = prob * len(sums_arr)

    # Numerical safety: enforce identical totals for chi-square (SciPy requires this).
    if expected.sum() > 0:
        expected *= float(observed.sum() / expected.sum())

    # Chi-square requires reasonably-sized expected values; merge bins until expected >= 5.
    min_expected = 5.0
    merged_observed: list[int] = []
    merged_expected: list[float] = []
    acc_obs = 0
    acc_exp = 0.0
    for o, e in zip(observed.tolist(), expected.tolist(), strict=False):
        acc_obs += int(o)
        acc_exp += float(e)
        if acc_exp >= min_expected:
            merged_observed.append(acc_obs)
            merged_expected.append(acc_exp)
            acc_obs = 0
            acc_exp = 0.0

    if acc_exp > 0 or acc_obs > 0:
        if merged_observed:
            merged_observed[-1] += acc_obs
            merged_expected[-1] += acc_exp
        else:
            merged_observed.append(acc_obs)
            merged_expected.append(acc_exp)

    if len(merged_observed) < 2:
        return SumNullModelFit(
            numbers_min=numbers_min,
            numbers_max=numbers_max,
            numbers_drawn=numbers_drawn,
            total_draws=len(sums_arr),
            observed_sum_min=obs_min,
            observed_sum_max=obs_max,
            expected_mean=expected_mean,
            expected_std=expected_std,
            chi2_statistic=0.0,
            chi2_p_value=1.0,
            degrees_of_freedom=0,
            bins_used=len(merged_observed),
            bin_width=bin_width,
            note="insufficient bins for chi-square after merging low expected counts",
        )

    merged_obs_arr = np.asarray(merged_observed, dtype=int)
    merged_exp_arr = np.asarray(merged_expected, dtype=float)

    # One more safety pass after merging.
    if merged_exp_arr.sum() > 0:
        merged_exp_arr *= float(merged_obs_arr.sum() / merged_exp_arr.sum())

    chi2, p = stats.chisquare(merged_obs_arr, f_exp=merged_exp_arr)
    dof = int(len(merged_observed) - 1)

    return SumNullModelFit(
        numbers_min=numbers_min,
        numbers_max=numbers_max,
        numbers_drawn=numbers_drawn,
        total_draws=len(sums_arr),
        observed_sum_min=obs_min,
        observed_sum_max=obs_max,
        expected_mean=expected_mean,
        expected_std=expected_std,
        chi2_statistic=float(chi2),
        chi2_p_value=float(p),
        degrees_of_freedom=dof,
        bins_used=len(merged_observed),
        bin_width=bin_width,
        note="chi-square vs exact null distribution (merged bins for expected>=5)",
    )


__all__ = [
    "SumNullModelFit",
    "exact_sum_counts",
    "fit_sum_null_model",
]
