#!/usr/bin/env python3
"""DIST-003 CLI: Sum distribution vs exact null model.

This checks the observed sum(20 drawn numbers) distribution against the correct
expected distribution (20 without replacement from 1..70).

Examples:
  python scripts/analyze_dist003_sum.py
  python scripts/analyze_dist003_sum.py --data data/raw/keno/KENO_ab_2018.csv --bin-width 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.dist003_sum_null_model import fit_sum_null_model
from kenobase.core.data_loader import DataLoader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DIST-003: Sum distribution null-model check")
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Pfad zur Ziehungs-CSV (default: data/raw/keno/KENO_ab_2018.csv)",
    )
    parser.add_argument(
        "--bin-width",
        type=int,
        default=20,
        help="Histogram bin width (default: 20)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"ERROR: data not found: {data_path}")
        return 1

    loader = DataLoader()
    draws = loader.load(str(data_path))
    sums = [sum(d.numbers) for d in draws]

    fit = fit_sum_null_model(sums, bin_width=args.bin_width)

    print("=" * 80)
    print("DIST-003: Sum distribution vs exact null model")
    print(f"Data: {data_path}")
    print("=" * 80)
    print(f"draws: {fit.total_draws}")
    print(f"observed min/max: {fit.observed_sum_min} / {fit.observed_sum_max}")
    print(f"expected mean/std: {fit.expected_mean:.2f} / {fit.expected_std:.2f}")
    print(f"chi2: {fit.chi2_statistic:.2f}, dof={fit.degrees_of_freedom}, p={fit.chi2_p_value:.6f}")
    print(f"bins_used: {fit.bins_used} (bin_width={fit.bin_width})")
    if fit.note:
        print(f"note: {fit.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

