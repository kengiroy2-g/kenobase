#!/usr/bin/env python3
"""
BACKTEST: Pool V2 vs V3 (Correction-aware)

Vergleicht die taegliche Pool-Trefferzahl (pool_hits = |Pool ∩ Ziehung|)
zwischen:
  - V2: DANCE-006 + DANCE-009 (Pattern-Filter, Score)
  - V3: V2 + A8 (Auszahlungs-Reaktion) + dynamischer Pool-Mix

Wichtig:
  - pool_hits>=6 ist KEIN automatischer 6/6-Gewinn (ohne exaktes Ticket).
  - Dieses Script bewertet nur "Coverage"/Konzentration des Pools.

Beispiele:
  python scripts/backtest_pool_v2_vs_v3.py --year 2025 --pool-size 17
  python scripts/backtest_pool_v2_vs_v3.py --year 2025 --pool-size 17 --permutations 20000
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from generate_optimized_tickets import build_reduced_pool
from generate_optimized_pool_v3 import (
    attach_stake_and_ratio,
    build_reduced_pool_v3,
    load_gq_daily_stats,
    load_keno_draws,
)
from kenobase.analysis.popularity_correlation import calculate_popularity_scores_heuristic


@dataclass(frozen=True)
class DayRow:
    idx: int
    date: str
    hits_v2: int
    hits_v3: int


def sign_test_two_sided_p_value(wins: int, losses: int) -> float:
    """Exakter 2-seitiger Sign-Test p-Wert (Binomial, p=0.5)."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    numerator = sum(math.comb(n, i) for i in range(k + 1))
    return float(min(1.0, 2 * numerator / (2**n)))


def permutation_sign_flip_p_value(
    abs_diffs: list[int],
    observed_total: int,
    n_permutations: int,
    seed: int,
) -> float | None:
    """Permutationstest (Sign-Flip) fuer Summe der Diffs (2-seitig)."""
    if n_permutations <= 0:
        return None
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_permutations):
        total = 0
        for d in abs_diffs:
            total += d if rng.random() < 0.5 else -d
        if abs(total) >= abs(observed_total):
            extreme += 1
    return (extreme + 1) / (n_permutations + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest: Pool V2 vs V3 (pool_hits)")
    parser.add_argument("--year", type=int, default=2025, help="Jahr (Default: 2025)")
    parser.add_argument("--pool-size", type=int, default=17, help="Pool-Groesse (Default: 17)")
    parser.add_argument("--min-history", type=int, default=60, help="Min Historie (Default: 60)")
    parser.add_argument(
        "--correction-lookback",
        type=int,
        default=60,
        help="V3: Lookback fuer Correction-State (Default: 60)",
    )
    parser.add_argument("--permutations", type=int, default=0, help="Optional: Permutationstest N (Default: 0)")
    parser.add_argument("--seed", type=int, default=0, help="Seed fuer Permutationstest (Default: 0)")
    args = parser.parse_args()

    if args.pool_size <= 0 or args.pool_size > 70:
        raise SystemExit("--pool-size muss zwischen 1 und 70 liegen")
    if args.min_history < 1:
        raise SystemExit("--min-history muss >= 1 sein")

    base_path = Path(__file__).parent.parent
    draws = load_keno_draws(base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv")

    gq_paths = [
        base_path / "Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
        base_path / "Keno_GPTs/Keno_GQ_2025.csv",
    ]
    daily_stats = load_gq_daily_stats(gq_paths)
    daily_stats = attach_stake_and_ratio(draws=draws, daily_stats=daily_stats)

    popularity_scores = calculate_popularity_scores_heuristic(range(1, 71))

    year_indices = [i for i, d in enumerate(draws) if d["datum"].year == args.year]
    if not year_indices:
        raise SystemExit(f"Keine Ziehungen fuer Jahr {args.year} gefunden")

    rows: list[DayRow] = []
    wins = 0
    losses = 0
    ties = 0
    diffs: list[int] = []

    for idx in year_indices:
        if idx < args.min_history:
            continue

        train = draws[:idx]
        drawn = draws[idx]["zahlen"]

        pool_v2, _ = build_reduced_pool(train, target_size=args.pool_size)
        pool_v3, _ = build_reduced_pool_v3(
            draws=train,
            daily_stats=daily_stats,
            popularity_scores=popularity_scores,
            target_size=args.pool_size,
            correction_lookback_days=args.correction_lookback,
        )

        hits_v2 = len(pool_v2 & drawn)
        hits_v3 = len(pool_v3 & drawn)
        diff = hits_v3 - hits_v2

        rows.append(
            DayRow(
                idx=idx,
                date=draws[idx]["datum"].date().isoformat(),
                hits_v2=hits_v2,
                hits_v3=hits_v3,
            )
        )

        if diff > 0:
            wins += 1
            diffs.append(diff)
        elif diff < 0:
            losses += 1
            diffs.append(diff)
        else:
            ties += 1

    if not rows:
        raise SystemExit("Keine auswertbaren Tage (min-history zu hoch?)")

    diffs_np = np.array([r.hits_v3 - r.hits_v2 for r in rows], dtype=float)
    v2_np = np.array([r.hits_v2 for r in rows], dtype=float)
    v3_np = np.array([r.hits_v3 for r in rows], dtype=float)

    # Success rates by threshold
    thresholds = [6, 7, 8, 9, 10]
    rates = []
    for t in thresholds:
        r2 = float(np.mean(v2_np >= t))
        r3 = float(np.mean(v3_np >= t))
        rates.append((t, r2, r3))

    p_sign = sign_test_two_sided_p_value(wins=wins, losses=losses)
    abs_diffs = [abs(int(d)) for d in diffs]
    observed_total = int(round(float(np.sum(diffs_np))))
    p_perm = permutation_sign_flip_p_value(
        abs_diffs=abs_diffs,
        observed_total=observed_total,
        n_permutations=args.permutations,
        seed=args.seed,
    )

    print("=" * 100)
    print(f"BACKTEST Pool V2 vs V3: year={args.year}, pool_size={args.pool_size}")
    print(f"min_history={args.min_history}, correction_lookback={args.correction_lookback}")
    print("=" * 100)
    print(f"Days evaluated: {len(rows)}")
    print(f"V3 better days: {wins} | V2 better days: {losses} | ties: {ties}")
    print(f"Mean hits: V2={float(np.mean(v2_np)):.3f}  V3={float(np.mean(v3_np)):.3f}  Δ={float(np.mean(diffs_np)):.3f}")
    print(f"Median Δhits (V3-V2): {float(np.median(diffs_np)):.3f}")
    print(f"Sign-test p-value: {p_sign:.4g}")
    if p_perm is not None:
        print(f"Permutation p-value (n={args.permutations}): {p_perm:.4g}")
    print()
    print("Threshold success (pool_hits >= t):")
    for t, r2, r3 in rates:
        print(f"  t={t}: V2={r2*100:5.1f}%  V3={r3*100:5.1f}%  Δ={(r3-r2)*100:+5.1f}%")


if __name__ == "__main__":
    main()

