#!/usr/bin/env python3
"""HYP_014: Overlap-Autokorrelation.

Tests if overlap_count time series shows temporal dependencies (autocorrelation).
- overlap_count = |numbers_t ∩ numbers_{t-1}| (range 0-20)
- Expected mean: 20*20/70 = 5.714

Methodology:
- Compute Pearson autocorrelation at lag=1..7
- Null model: block-permutation preserving weekly structure (7-day blocks)
- Acceptance criterion: |r| < 0.1 if random

Output:
- results/hyp014_overlap_autocorrelation.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


EXPECTED_OVERLAP = 20 * 20 / 70  # 5.714285...
MAX_LAG = 7
N_PERMUTATIONS = 1000
ALPHA = 0.05


def load_draws(draw_path: Path) -> pd.DataFrame:
    """Load draw data and attach numbers_set."""
    df = pd.read_csv(draw_path, sep=";", encoding="utf-8", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Datum"]).sort_values("Datum").reset_index(drop=True)

    number_cols = [col for col in df.columns if col.startswith("Keno_Z")]
    df["numbers_set"] = df[number_cols].apply(
        lambda row: set(int(x) for x in row.dropna().astype(int).tolist()),
        axis=1,
    )
    return df


def compute_overlap_series(draws: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Compute overlap_count time series.

    Returns:
        overlap_counts: array of overlap counts (length N-1)
        dates: list of date strings (length N-1)
    """
    overlap_counts = []
    dates = []
    previous_set: Optional[set[int]] = None

    for _, row in draws.iterrows():
        current_set = row["numbers_set"]
        if previous_set is not None:
            overlap_count = len(previous_set & current_set)
            overlap_counts.append(overlap_count)
            dates.append(str(row["Datum"].date()))
        previous_set = current_set

    return np.array(overlap_counts), dates


def pearson_autocorrelation(series: np.ndarray, lag: int) -> float:
    """Compute Pearson autocorrelation at given lag."""
    if lag >= len(series):
        return np.nan
    x = series[:-lag] if lag > 0 else series
    y = series[lag:] if lag > 0 else series

    if len(x) < 2:
        return np.nan

    # Pearson correlation
    r, _ = stats.pearsonr(x, y)
    return float(r)


def compute_autocorrelations(series: np.ndarray, max_lag: int) -> dict[int, float]:
    """Compute autocorrelations for lag=1..max_lag."""
    return {lag: pearson_autocorrelation(series, lag) for lag in range(1, max_lag + 1)}


def block_permutation(series: np.ndarray, block_size: int = 7) -> np.ndarray:
    """Permute series by shuffling blocks (preserves weekly structure).

    Blocks of `block_size` consecutive values are kept intact,
    but the order of blocks is randomized.
    """
    n = len(series)
    n_blocks = (n + block_size - 1) // block_size

    # Create blocks (last block may be smaller)
    blocks = []
    for i in range(n_blocks):
        start = i * block_size
        end = min(start + block_size, n)
        blocks.append(series[start:end])

    # Shuffle block order
    np.random.shuffle(blocks)

    # Concatenate
    return np.concatenate(blocks)


def permutation_test(
    series: np.ndarray,
    lag: int,
    n_perms: int,
    block_size: int = 7,
) -> dict:
    """Permutation test for autocorrelation significance.

    Returns:
        dict with observed r, null distribution stats, p-value
    """
    observed_r = pearson_autocorrelation(series, lag)

    null_rs = []
    for _ in range(n_perms):
        perm_series = block_permutation(series, block_size)
        null_rs.append(pearson_autocorrelation(perm_series, lag))

    null_rs = np.array(null_rs)

    # Two-tailed p-value: proportion of |null_r| >= |observed_r|
    p_value = float(np.mean(np.abs(null_rs) >= np.abs(observed_r)))

    return {
        "observed_r": observed_r,
        "null_mean": float(np.mean(null_rs)),
        "null_std": float(np.std(null_rs)),
        "null_min": float(np.min(null_rs)),
        "null_max": float(np.max(null_rs)),
        "p_value": p_value,
        "significant": p_value < ALPHA,
    }


def ljung_box_test(series: np.ndarray, max_lag: int) -> dict:
    """Ljung-Box test for autocorrelation (tests if any lag is significant)."""
    from scipy import stats as sp_stats

    n = len(series)
    autocorrs = []

    for lag in range(1, max_lag + 1):
        r = pearson_autocorrelation(series, lag)
        autocorrs.append(r)

    # Ljung-Box Q statistic
    q_stat = 0.0
    for k, r in enumerate(autocorrs, start=1):
        if not np.isnan(r):
            q_stat += (r ** 2) / (n - k)
    q_stat = n * (n + 2) * q_stat

    # Chi-squared p-value with max_lag degrees of freedom
    p_value = float(1 - sp_stats.chi2.cdf(q_stat, df=max_lag))

    return {
        "q_statistic": float(q_stat),
        "df": max_lag,
        "p_value": p_value,
        "significant": p_value < ALPHA,
    }


def hypothesis_decision(
    autocorrs: dict[int, float],
    perm_tests: dict[int, dict],
    ljung_box: dict,
    threshold: float = 0.1,
) -> dict:
    """Decide on hypothesis based on results.

    HYP_014: Overlap-Autokorrelation
    - Accept (SUPPORT): |r| >= threshold OR significant permutation test
    - Reject: |r| < threshold AND no significant autocorrelation
    """
    # Check if any lag has |r| >= threshold
    large_r = any(abs(r) >= threshold for r in autocorrs.values() if not np.isnan(r))

    # Check if any permutation test is significant
    perm_significant = any(
        pt.get("significant", False) for pt in perm_tests.values()
    )

    # Ljung-Box overall test
    lb_significant = ljung_box.get("significant", False)

    support = large_r or perm_significant or lb_significant

    max_r_lag = max(autocorrs.keys(), key=lambda k: abs(autocorrs[k]) if not np.isnan(autocorrs[k]) else 0)
    max_r = autocorrs[max_r_lag]

    if support:
        reason = f"Temporal dependency detected: max |r|={abs(max_r):.4f} at lag={max_r_lag}"
        if perm_significant:
            reason += "; permutation test significant"
        if lb_significant:
            reason += "; Ljung-Box test significant"
    else:
        reason = f"No temporal dependency: max |r|={abs(max_r):.4f} < {threshold} (random-like)"

    return {
        "hypothesis": "HYP_014",
        "support": support,
        "max_abs_r": float(abs(max_r)),
        "max_r_lag": max_r_lag,
        "threshold": threshold,
        "reason": reason,
    }


def save_json(output_path: Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Test HYP_014: Overlap-Autokorrelation")
    parser.add_argument(
        "--draws",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2022_bereinigt.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/hyp014_overlap_autocorrelation.json"),
    )
    parser.add_argument("--max-lag", type=int, default=MAX_LAG)
    parser.add_argument("--n-perms", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)

    # Load data
    draws = load_draws(args.draws)
    overlap_series, dates = compute_overlap_series(draws)
    n = len(overlap_series)

    # Basic statistics
    basic_stats = {
        "n": n,
        "mean": float(np.mean(overlap_series)),
        "std": float(np.std(overlap_series, ddof=1)),
        "min": int(np.min(overlap_series)),
        "max": int(np.max(overlap_series)),
        "expected_mean": EXPECTED_OVERLAP,
    }

    # Compute autocorrelations
    autocorrs = compute_autocorrelations(overlap_series, args.max_lag)

    # Permutation tests for each lag
    perm_tests = {}
    for lag in range(1, args.max_lag + 1):
        perm_tests[lag] = permutation_test(
            overlap_series, lag, args.n_perms, block_size=7
        )

    # Ljung-Box test
    ljung_box = ljung_box_test(overlap_series, args.max_lag)

    # Hypothesis decision
    decision = hypothesis_decision(autocorrs, perm_tests, ljung_box)

    # Build output
    payload = {
        "metadata": {
            "draws_file": str(args.draws),
            "date_range": {
                "start": dates[0] if dates else None,
                "end": dates[-1] if dates else None,
            },
            "max_lag": args.max_lag,
            "n_permutations": args.n_perms,
            "seed": args.seed,
            "alpha": ALPHA,
        },
        "basic_stats": basic_stats,
        "autocorrelations": {str(k): v for k, v in autocorrs.items()},
        "permutation_tests": {str(k): v for k, v in perm_tests.items()},
        "ljung_box_test": ljung_box,
        "decision": decision,
        "interpretation": {
            "if_random": "Overlap-count should show |r| < 0.1 for all lags if draws are independent",
            "if_dependent": "Significant autocorrelation would suggest temporal structure in overlap patterns",
        },
    }

    save_json(args.output, payload)

    # Console output
    print(f"HYP_014: Overlap-Autokorrelation Analysis")
    print(f"=========================================")
    print(f"Data: {args.draws}")
    print(f"N observations: {n}")
    print(f"Mean overlap: {basic_stats['mean']:.3f} (expected: {EXPECTED_OVERLAP:.3f})")
    print()
    print("Autocorrelations:")
    for lag, r in autocorrs.items():
        pt = perm_tests[lag]
        sig = "*" if pt["significant"] else ""
        print(f"  lag={lag}: r={r:.4f} (p={pt['p_value']:.4f}){sig}")
    print()
    print(f"Ljung-Box Q={ljung_box['q_statistic']:.2f}, df={ljung_box['df']}, p={ljung_box['p_value']:.4f}")
    print()
    print(f"Decision: {'SUPPORT' if decision['support'] else 'REJECT'}")
    print(f"Reason: {decision['reason']}")
    print()
    print(f"JSON written to {args.output}")


if __name__ == "__main__":
    main()
