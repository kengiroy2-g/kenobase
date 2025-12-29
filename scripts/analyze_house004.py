#!/usr/bin/env python3
"""HOUSE-004 CLI: Near-Miss Analyse (Jackpot-Kontext vs. Normal).

Beispiele:
  python scripts/analyze_house004.py --context self
  python scripts/analyze_house004.py --context gk1 --types 4 5 6 7
  python scripts/analyze_house004.py --gq-file Keno_GPTs/Keno_GQ_2022_2023-2024.csv --output results/house004.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.house004_near_miss import run_house004_from_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HOUSE-004: Near-Miss Analyse")
    parser.add_argument(
        "--gq-file",
        type=str,
        default="Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
        help="Pfad zur GQ-CSV (default: Keno_GPTs/Keno_GQ_2022_2023-2024.csv)",
    )
    parser.add_argument(
        "--context",
        choices=["self", "gk1"],
        default="self",
        help="Kontext-Definition fuer 'Jackpot-Tage' (default: self)",
    )
    parser.add_argument(
        "--types",
        type=int,
        nargs="*",
        default=None,
        help="Optional: Keno-Typen (z.B. --types 4 9 10). Default: alle in Datei.",
    )
    parser.add_argument(
        "--n-sim",
        type=int,
        default=20000,
        help="Monte-Carlo Simulationen fuer Erklaermodel (nur context=self). Default 20000.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: JSON Output-Pfad, z.B. results/house004.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    results = run_house004_from_file(
        args.gq_file,
        context=args.context,
        keno_types=args.types,
        n_sim=args.n_sim,
        seed=args.seed,
        output_json=args.output,
    )

    print("=" * 80)
    print("HOUSE-004: Near-Miss Ratio")
    print(f"Context: {args.context}")
    print(f"GQ file: {args.gq_file}")
    print("=" * 80)
    print()

    header = [
        "Type",
        "Overall",
        "InContext",
        "OutContext",
        "Diff(in-out)",
        "Model_p",
        "r(shape)",
        "muJ/day",
        "muN/day",
    ]
    print("{:>4s} {:>10s} {:>10s} {:>10s} {:>11s} {:>8s} {:>8s} {:>8s} {:>8s}".format(*header))

    def fmt(x):
        return "-" if x is None else f"{x:.2f}"

    for r in results:
        model_p = r.model.simulated_p_value_two_sided if r.model else None
        r_shape = r.model.gamma_shape_r if r.model else None
        mu_j = r.model.mu_jackpot_per_day if r.model else None
        mu_n = r.model.mu_near_per_day if r.model else None

        print(
            f"{r.keno_type:4d} {fmt(r.overall.ratio):>10s} {fmt(r.in_context.ratio):>10s} "
            f"{fmt(r.out_context.ratio):>10s} {fmt(r.diff_in_minus_out):>11s} "
            f"{fmt(model_p):>8s} {fmt(r_shape):>8s} {fmt(mu_j):>8s} {fmt(mu_n):>8s}"
        )

    if args.output:
        print(f"\nJSON geschrieben: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
