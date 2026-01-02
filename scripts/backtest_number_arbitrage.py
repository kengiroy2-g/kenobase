#!/usr/bin/env python3
"""Backtest Number Arbitrage strategy.

This script implements the STRAT-002 Zahlen-Arbitrage backtest:
- Train/Test split: Train=2022-2023, Test=2024+
- Focus on robust edge: KENO->AUSWAHLWETTE lag=7, lift=2.41, q=0.027
- EuroJackpot as negative control (should show NO correlation)
- Schedule-preserving permutation null model
- Frozen rules in test set (no parameter changes)

Usage:
    python scripts/backtest_number_arbitrage.py
    python scripts/backtest_number_arbitrage.py --output results/number_arbitrage_backtest.json
    python scripts/backtest_number_arbitrage.py --n-permutations 200 --seed 123
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.analyze_cross_lottery_coupling import (
    _load_auswahlwette,
    _load_eurojackpot,
    _load_keno,
)

from kenobase.analysis.number_arbitrage import (
    ArbitrageEvaluation,
    backtest_number_arbitrage,
    roi_sanity_check,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest number arbitrage strategy")
    parser.add_argument(
        "--keno",
        type=str,
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="KENO CSV path",
    )
    parser.add_argument(
        "--auswahlwette",
        type=str,
        default="data/raw/auswahlwette/AW_ab_2022_bereinigt.csv",
        help="Auswahlwette CSV path",
    )
    parser.add_argument(
        "--eurojackpot",
        type=str,
        default="data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv",
        help="EuroJackpot CSV path (negative control)",
    )
    parser.add_argument(
        "--split-date",
        type=str,
        default="2024-01-01",
        help="Train/test split date (format: YYYY-MM-DD, default: 2024-01-01)",
    )
    parser.add_argument(
        "--lag",
        type=int,
        default=7,
        help="Lag days for arbitrage (default: 7, per ecosystem_graph)",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=30,
        help="Minimum trigger support (default: 30)",
    )
    parser.add_argument(
        "--lift-threshold",
        type=float,
        default=1.1,
        help="Minimum lift for rules (default: 1.1)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold (default: 0.05)",
    )
    parser.add_argument(
        "--max-rules",
        type=int,
        default=50,
        help="Maximum rules to discover (default: 50)",
    )
    parser.add_argument(
        "--n-permutations",
        type=int,
        default=100,
        help="Number of null model permutations (default: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/number_arbitrage_backtest.json",
        help="Output JSON path",
    )
    return parser.parse_args()


def evaluation_to_dict(eval_result: ArbitrageEvaluation) -> dict:
    """Convert ArbitrageEvaluation to JSON-serializable dict."""
    return {
        "rule": {
            "source_game": eval_result.rule.source_game,
            "target_game": eval_result.rule.target_game,
            "trigger_number": eval_result.rule.trigger_number,
            "target_number": eval_result.rule.target_number,
            "lag_days": eval_result.rule.lag_days,
            "train_lift": eval_result.rule.train_lift,
            "train_q_value": eval_result.rule.train_q_value,
            "train_support": eval_result.rule.train_support,
            "train_base_rate": eval_result.rule.train_base_rate,
            "train_conditional_rate": eval_result.rule.train_conditional_rate,
        },
        "test_support": eval_result.test_support,
        "test_base_rate": eval_result.test_base_rate,
        "test_conditional_rate": eval_result.test_conditional_rate,
        "test_lift": eval_result.test_lift,
        "test_p_value": eval_result.test_p_value,
        "is_significant": eval_result.is_significant,
    }


def main() -> int:
    args = parse_args()

    # Parse split date
    split_date = date.fromisoformat(args.split_date)

    # Load data
    print("Loading data...")
    keno = _load_keno(args.keno)
    aw = _load_auswahlwette(args.auswahlwette)
    ej = _load_eurojackpot(args.eurojackpot)

    print(f"KENO: {len(keno.dates)} draws ({keno.dates[0]} to {keno.dates[-1]})")
    print(f"AUSWAHLWETTE: {len(aw.dates)} draws ({aw.dates[0]} to {aw.dates[-1]})")
    print(f"EUROJACKPOT: {len(ej.dates)} draws ({ej.dates[0]} to {ej.dates[-1]})")
    print(f"Split date: {split_date}")
    print()

    # Run backtest
    print("Running backtest...")
    print(f"  Source: {keno.name}")
    print(f"  Target: {aw.name}")
    print(f"  Lag: {args.lag} days")
    print(f"  Negative control: {ej.name}")
    print()

    result = backtest_number_arbitrage(
        source=keno,
        target=aw,
        lag_days=args.lag,
        split_date=split_date,
        negative_control_source=ej,
        min_support=args.min_support,
        lift_threshold=args.lift_threshold,
        alpha_fdr=args.alpha,
        max_rules=args.max_rules,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )

    # Analyze results
    print("=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    print(f"Train period: {result.train_start} to {result.train_end}")
    print(f"Test period:  {result.test_start} to {result.test_end}")
    print()
    print(f"Rules discovered in train: {result.n_rules_discovered}")
    print(f"Rules significant in test: {result.n_rules_significant_test}")
    print()

    # Null model analysis
    null_lifts = np.array(result.null_model_lifts)
    null_95th = np.percentile(null_lifts, 95)
    null_99th = np.percentile(null_lifts, 99)
    null_mean = np.mean(null_lifts)
    null_std = np.std(null_lifts)

    print("Null model (schedule-preserving permutation):")
    print(f"  Mean max lift: {null_mean:.3f}")
    print(f"  Std:           {null_std:.3f}")
    print(f"  95th pctl:     {null_95th:.3f}")
    print(f"  99th pctl:     {null_99th:.3f}")
    print()

    # Show significant rules
    significant_evals = [e for e in result.evaluations if e.is_significant]
    if significant_evals:
        print("Significant rules in test set:")
        for e in significant_evals[:10]:  # top 10
            print(
                f"  {e.rule.source_game}.{e.rule.trigger_number} -> "
                f"{e.rule.target_game}.{e.rule.target_number} @ lag={e.rule.lag_days}d: "
                f"train_lift={e.rule.train_lift:.2f} test_lift={e.test_lift:.2f} "
                f"p={e.test_p_value:.4f}"
            )
            # ROI sanity check
            roi_check = roi_sanity_check(e.test_lift, e.test_base_rate)
            if roi_check["warning"]:
                print(f"    {roi_check['warning']}")
    else:
        print("No significant rules survived out-of-sample test.")
    print()

    # Negative control
    if result.negative_control:
        print("Negative control (EuroJackpot):")
        print(f"  Rules discovered: {result.negative_control['n_rules_discovered']}")
        print(f"  Rules significant in test: {result.negative_control['n_rules_significant_test']}")
        print(f"  {result.negative_control['message']}")
        if result.negative_control["n_rules_significant_test"] > 0:
            print("  WARNING: Negative control shows significant rules - check methodology!")
    print()

    # Compare observed vs null
    if result.evaluations:
        max_train_lift = max(e.rule.train_lift for e in result.evaluations)
        pct_above_null = sum(1 for x in null_lifts if max_train_lift > x) / len(null_lifts) * 100
        print(f"Max train lift {max_train_lift:.2f} exceeds {pct_above_null:.1f}% of null model lifts")

    # Prepare output
    payload = {
        "analysis": "number_arbitrage_backtest",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "keno": args.keno,
            "auswahlwette": args.auswahlwette,
            "eurojackpot": args.eurojackpot,
            "split_date": str(split_date),
            "lag_days": args.lag,
            "min_support": args.min_support,
            "lift_threshold": args.lift_threshold,
            "alpha_fdr": args.alpha,
            "max_rules": args.max_rules,
            "n_permutations": args.n_permutations,
            "seed": args.seed,
        },
        "summary": {
            "train_start": str(result.train_start),
            "train_end": str(result.train_end),
            "test_start": str(result.test_start),
            "test_end": str(result.test_end),
            "n_rules_discovered": result.n_rules_discovered,
            "n_rules_significant_test": result.n_rules_significant_test,
            "success_rate": (
                result.n_rules_significant_test / result.n_rules_discovered
                if result.n_rules_discovered > 0
                else 0.0
            ),
        },
        "null_model": {
            "n_permutations": args.n_permutations,
            "mean_max_lift": float(null_mean),
            "std_max_lift": float(null_std),
            "percentile_95": float(null_95th),
            "percentile_99": float(null_99th),
            "all_lifts": [float(x) for x in null_lifts],
        },
        "evaluations": [evaluation_to_dict(e) for e in result.evaluations],
        "significant_evaluations": [evaluation_to_dict(e) for e in significant_evals],
        "negative_control": result.negative_control,
        "axiom_compliance": {
            "A1_house_edge_warning": any(
                roi_sanity_check(e.test_lift, e.test_base_rate)["warning"] is not None
                for e in significant_evals
            ),
            "message": "Per Axiom A1, ROI > 0% is implausible. See roi_sanity_check results.",
        },
    }

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results written to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
