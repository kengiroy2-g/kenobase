#!/usr/bin/env python3
"""Walk-forward backtest for frequency-based ticket suggestions (types 6-9).

Examples:
  python scripts/backtest_tickets.py
  python scripts/backtest_tickets.py --types 6 7 8 9 --start-index 365
  python scripts/backtest_tickets.py --recent-draws 200 --recent-weight 0.7
  python scripts/backtest_tickets.py --output results/ticket_backtest.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.data_loader import DataLoader
from kenobase.prediction.ticket_backtester import save_backtest_json, walk_forward_backtest_weighted_frequency


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest ticket suggestions (walk-forward)")
    parser.add_argument(
        "--draws",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Pfad zur Ziehungs-CSV (default: data/raw/keno/KENO_ab_2018.csv)",
    )
    parser.add_argument(
        "--types",
        type=int,
        nargs="*",
        default=[6, 7, 8, 9],
        help="Keno-Typen (Anzahl Zahlen), z.B. --types 6 7 8 9 (default: 6 7 8 9)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=365,
        help="Ab welcher Ziehung mit Vorhersagen starten (History bis dahin) (default: 365)",
    )
    parser.add_argument(
        "--recent-draws",
        type=int,
        default=365,
        help="Fenster fuer Recent-Frequenz (default: 365, 0 = aus)",
    )
    parser.add_argument(
        "--recent-weight",
        type=float,
        default=0.6,
        help="Gewicht fuer Recent-Frequenz (default: 0.6)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: JSON Output-Pfad, z.B. results/ticket_backtest.json",
    )
    return parser.parse_args()


def _fmt_pct(x: float) -> str:
    return f"{x*100:.4f}%"


def main() -> int:
    args = parse_args()

    loader = DataLoader()
    draws = loader.load(args.draws)
    draws = sorted(draws, key=lambda d: d.date)

    results = walk_forward_backtest_weighted_frequency(
        draws,
        keno_types=args.types,
        start_index=args.start_index,
        recent_draws=args.recent_draws,
        recent_weight=args.recent_weight,
    )

    print("=" * 90)
    print("KENO Ticket Backtest (walk-forward, weighted frequency)")
    print(f"Draws: {len(draws)} from {draws[0].date.date()} to {draws[-1].date.date()}")
    print(f"Start index: {args.start_index} -> predictions: {len(draws) - args.start_index}")
    print(f"Model: weighted_frequency(recent_draws={args.recent_draws}, recent_weight={args.recent_weight})")
    print("=" * 90)
    print()

    for r in results:
        print(f"Type {r.keno_type} (k={r.keno_type}):")
        print(
            f"  mean hits: {r.mean_hits:.4f}  (expected {r.expected_mean_hits:.4f})"
            + (
                f"  z={r.mean_hits_z:.2f} p={r.mean_hits_p_value:.4f}"
                if r.mean_hits_z is not None and r.mean_hits_p_value is not None
                else ""
            )
        )
        print(
            f"  near-miss (hits={r.near_miss_hits}): {r.near_miss_count}/{r.n_predictions} "
            f"(expected {r.expected_near_miss_count:.2f}, p≈{r.near_miss_p_value:.4f})"
            if r.near_miss_p_value is not None
            else f"  near-miss (hits={r.near_miss_hits}): {r.near_miss_count}/{r.n_predictions}"
        )
        print(
            f"  jackpot  (hits={r.jackpot_hits}): {r.jackpot_count}/{r.n_predictions} "
            f"(expected {r.expected_jackpot_count:.2f}, p≈{r.jackpot_p_value:.4f})"
            if r.jackpot_p_value is not None
            else f"  jackpot  (hits={r.jackpot_hits}): {r.jackpot_count}/{r.n_predictions}"
        )
        print(
            f"  Uniform P(near|jack): {_fmt_pct(r.hit_distribution.expected_counts[r.near_miss_hits] / r.n_predictions + r.hit_distribution.expected_counts[r.jackpot_hits] / r.n_predictions)}"
        )
        print(f"  last ticket: {', '.join(map(str, r.last_ticket))}")
        print(
            f"  hit-dist chi2 p≈{r.hit_distribution.chi2_p_value:.4f} "
            f"(bins_used={r.hit_distribution.bins_used})"
            if r.hit_distribution.chi2_p_value is not None
            else f"  hit-dist: {r.hit_distribution.note}"
        )
        print()

    if args.output:
        save_backtest_json(results, output_path=args.output, draws_path=args.draws)
        print(f"JSON geschrieben: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

