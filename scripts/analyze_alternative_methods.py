#!/usr/bin/env python3
"""Alternative coupling analysis methods for cross-lottery ecosystems.

This script runs alternative coupling methods (Granger, Transfer Entropy,
Mutual Information, DTW) on cross-lottery time-series, following the
Axiom-First paradigm.

Features:
- Train/Test split (before/after 2024-01-01)
- EuroJackpot as negative control (international, not part of German ecosystem)
- FDR correction via BH procedure
- Permutation-based null models

Examples:
    python scripts/analyze_alternative_methods.py --method granger
    python scripts/analyze_alternative_methods.py --method all --lags 1 2 7
    python scripts/analyze_alternative_methods.py --output results/alternative_coupling.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, replace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.number_representations import (
    GameTimeSeries,
    align_time_series,
    game_to_time_series,
    get_train_test_split,
)
from kenobase.analysis.alternative_coupling import (
    CouplingResult,
    apply_fdr_correction,
    dtw_distance,
    granger_causality_test,
    mutual_information_lagged,
    run_all_methods,
    transfer_entropy,
)
from kenobase.analysis.cross_lottery_coupling import GameDraws


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alternative coupling analysis methods")
    parser.add_argument(
        "--keno",
        type=str,
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="KENO CSV (default: data/raw/keno/KENO_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--lotto",
        type=str,
        default="data/raw/lotto/LOTTO_ab_2022_bereinigt.csv",
        help="LOTTO CSV (default: data/raw/lotto/LOTTO_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--eurojackpot",
        type=str,
        default="data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv",
        help="EuroJackpot CSV (negative control)",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["granger", "te", "mi", "dtw", "all"],
        default="all",
        help="Analysis method (default: all)",
    )
    parser.add_argument(
        "--lags",
        type=int,
        nargs="*",
        default=[1, 2, 7],
        help="Lag days to test (default: 1 2 7)",
    )
    parser.add_argument(
        "--representation",
        type=str,
        choices=["sum", "mean", "centroid", "presence_vector", "normalized_vector"],
        default="centroid",
        help="Time-series representation (default: centroid)",
    )
    parser.add_argument(
        "--k-history-target",
        type=int,
        default=1,
        help="Target history length (k_y) for conditioning (default: 1)",
    )
    parser.add_argument(
        "--k-history-source",
        type=int,
        default=0,
        help="Source history length (k_x) for conditioning (default: 0)",
    )
    parser.add_argument(
        "--k-neighbors",
        type=int,
        default=5,
        help="k for kNN TE/CMI estimators (default: 5)",
    )
    parser.add_argument(
        "--n-permutations",
        type=int,
        default=100,
        help="Number of permutations for null (default: 100)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold (default: 0.05)",
    )
    parser.add_argument(
        "--split-date",
        type=str,
        default="2024-01-01",
        help="Train/test split date (default: 2024-01-01)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/alternative_coupling.json",
        help="Output JSON (default: results/alternative_coupling.json)",
    )
    parser.add_argument(
        "--use-synthetic",
        action="store_true",
        help="Use synthetic draws for a fast smoke test instead of CSV files",
    )
    return parser.parse_args()


def _load_keno(path: str) -> GameDraws:
    """Load KENO data."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 71), dtype=np.int8)
    ordered_numbers: list[list[int]] = []
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in pos_cols]
        ordered_numbers.append(nums)
        for n in nums:
            if 1 <= n <= 70:
                presence[i, n] = 1

    return GameDraws(
        name="KENO",
        pool_max=70,
        draw_size=20,
        dates=dates,
        presence=presence,
        ordered_numbers=ordered_numbers,
        jackpot_winners=None,
    )


def _load_lotto(path: str) -> GameDraws:
    """Load LOTTO data."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    num_cols = [f"L{i}" for i in range(1, 7)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 50), dtype=np.int8)
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols]
        for n in nums:
            if 1 <= n <= 49:
                presence[i, n] = 1

    return GameDraws(
        name="LOTTO",
        pool_max=49,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


def _load_eurojackpot(path: str) -> GameDraws:
    """Load EuroJackpot data (negative control)."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    num_cols = [f"E{i}" for i in range(1, 6)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 51), dtype=np.int8)
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols]
        for n in nums:
            if 1 <= n <= 50:
                presence[i, n] = 1

    return GameDraws(
        name="EUROJACKPOT",
        pool_max=50,
        draw_size=5,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


def _extract_pair_values(df: pd.DataFrame, source_name: str, target_name: str) -> tuple[np.ndarray, np.ndarray]:
    """Extract aligned source/target arrays (supports scalar and vector representations)."""
    source_cols = [c for c in df.columns if c == source_name or c.startswith(f"{source_name}_")]
    target_cols = [c for c in df.columns if c == target_name or c.startswith(f"{target_name}_")]

    if not source_cols or not target_cols:
        return np.array([]), np.array([])

    pair_df = df[source_cols + target_cols].dropna()
    if pair_df.empty:
        return np.array([]), np.array([])

    source_vals = pair_df[source_cols].to_numpy()
    target_vals = pair_df[target_cols].to_numpy()

    if source_vals.ndim == 1:
        source_vals = source_vals.reshape(-1, 1)
    if target_vals.ndim == 1:
        target_vals = target_vals.reshape(-1, 1)

    return source_vals, target_vals


def _build_presence_from_signal(
    signal: np.ndarray,
    pool_max: int,
    draw_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create presence matrix from a latent signal by biasing draws near its scaled value."""
    presence = np.zeros((len(signal), pool_max + 1), dtype=np.int8)
    pool = np.arange(1, pool_max + 1)
    sig_min, sig_max = float(np.min(signal)), float(np.max(signal))
    span = sig_max - sig_min + 1e-6

    for i, val in enumerate(signal):
        center = 1 + (val - sig_min) / span * (pool_max - 1)
        distances = np.abs(pool - center)
        weights = np.exp(-0.15 * distances)
        weights = weights / weights.sum()
        nums = rng.choice(pool, size=draw_size, replace=False, p=weights)
        for n in nums:
            presence[i, n] = 1

    return presence


def _load_synthetic_dataset(n_draws: int = 120) -> tuple[GameDraws, GameDraws, GameDraws]:
    """Generate synthetic coupled draws for smoke tests."""
    base_dates = [date(2023, 12, 1) + timedelta(days=i) for i in range(n_draws)]
    rng = np.random.default_rng(42)

    latent = rng.standard_normal(n_draws).cumsum()
    keno_signal = latent + rng.normal(scale=0.5, size=n_draws)
    lotto_signal = np.concatenate([[keno_signal[0]], keno_signal[:-1]]) * 0.7 + rng.normal(
        scale=0.6, size=n_draws
    )
    ej_signal = rng.standard_normal(n_draws)

    keno_presence = _build_presence_from_signal(keno_signal, pool_max=70, draw_size=20, rng=rng)
    lotto_presence = _build_presence_from_signal(lotto_signal, pool_max=49, draw_size=6, rng=rng)
    ej_presence = _build_presence_from_signal(ej_signal, pool_max=50, draw_size=5, rng=rng)

    keno = GameDraws(
        name="KENO",
        pool_max=70,
        draw_size=20,
        dates=base_dates,
        presence=keno_presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )
    lotto = GameDraws(
        name="LOTTO",
        pool_max=49,
        draw_size=6,
        dates=base_dates,
        presence=lotto_presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )
    ej = GameDraws(
        name="EUROJACKPOT",
        pool_max=50,
        draw_size=5,
        dates=base_dates,
        presence=ej_presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )

    return keno, lotto, ej


def run_method(
    method: str,
    source: np.ndarray,
    target: np.ndarray,
    source_name: str,
    target_name: str,
    lag: int,
    n_permutations: int,
    alpha: float,
    representation: str,
    segment: str,
    is_control: bool,
    k_history_target: int,
    k_history_source: int,
    k_neighbors: int,
) -> CouplingResult:
    """Run a single coupling method."""
    if method == "granger":
        result = granger_causality_test(
            source,
            target,
            max_lag=lag,
            n_permutations=n_permutations,
            alpha=alpha,
            representation=representation,
            segment=segment,
            is_control=is_control,
        )
    elif method == "te":
        result = transfer_entropy(
            source,
            target,
            lag=lag,
            k_history_target=k_history_target,
            k_history_source=k_history_source,
            k_neighbors=k_neighbors,
            n_permutations=n_permutations,
            alpha=alpha,
            representation=representation,
            segment=segment,
            is_control=is_control,
        )
    elif method == "mi":
        result = mutual_information_lagged(
            source,
            target,
            lag=lag,
            k_neighbors=k_neighbors,
            k_history_target=k_history_target,
            k_history_source=k_history_source,
            n_permutations=n_permutations,
            alpha=alpha,
            representation=representation,
            segment=segment,
            is_control=is_control,
        )
    elif method == "dtw":
        result = dtw_distance(
            source,
            target,
            n_permutations=n_permutations,
            alpha=alpha,
            representation=representation,
            segment=segment,
            is_control=is_control,
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    return replace(result, source=source_name, target=target_name)


def main() -> int:
    args = parse_args()

    if args.use_synthetic:
        print("Using synthetic draws (smoke test)...")
        keno, lotto, ej = _load_synthetic_dataset()
        ej_available = True
    else:
        # Check if data files exist
        keno_path = Path(args.keno)
        lotto_path = Path(args.lotto)
        ej_path = Path(args.eurojackpot)

        if not keno_path.exists():
            print(f"ERROR: KENO file not found: {args.keno}")
            return 1
        if not lotto_path.exists():
            print(f"ERROR: LOTTO file not found: {args.lotto}")
            return 1
        if not ej_path.exists():
            print(f"WARNING: EuroJackpot file not found: {args.eurojackpot}")
            print("Continuing without negative control.")
            ej_available = False
        else:
            ej_available = True

        # Load data
        print("Loading data...")
        keno = _load_keno(args.keno)
        lotto = _load_lotto(args.lotto)
        ej = _load_eurojackpot(args.eurojackpot) if ej_available else None

    # Convert to time-series
    print(f"Converting to {args.representation} representation...")
    keno_ts = game_to_time_series(keno, representation=args.representation)
    lotto_ts = game_to_time_series(lotto, representation=args.representation)
    ej_ts = game_to_time_series(ej, representation=args.representation) if ej else None

    # Align time-series
    series_list = [keno_ts, lotto_ts]
    if ej_ts:
        series_list.append(ej_ts)

    aligned = align_time_series(series_list)

    # Train/test split
    train_df, test_df = get_train_test_split(aligned, split_date=args.split_date)
    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")

    # Get methods to run
    if args.method == "all":
        methods = ["granger", "te", "mi", "dtw"]
    else:
        methods = [args.method]

    # Define game pairs
    # German ecosystem pairs (expected to show coupling)
    ecosystem_pairs = [
        ("KENO", "LOTTO"),
        ("LOTTO", "KENO"),
    ]

    # Negative control pairs (EuroJackpot - international, should NOT show coupling)
    control_pairs = []
    if ej_available:
        control_pairs = [
            ("KENO", "EUROJACKPOT"),
            ("EUROJACKPOT", "KENO"),
            ("LOTTO", "EUROJACKPOT"),
            ("EUROJACKPOT", "LOTTO"),
        ]

    lags = sorted(set([abs(int(x)) for x in args.lags]))

    print(f"\nRunning {len(methods)} method(s) on {len(ecosystem_pairs) + len(control_pairs)} pairs, {len(lags)} lag(s)...")

    all_results: list[dict] = []
    train_results: list[CouplingResult] = []
    test_results: list[CouplingResult] = []

    for method in methods:
        for source_name, target_name in ecosystem_pairs + control_pairs:
            is_control = source_name == "EUROJACKPOT" or target_name == "EUROJACKPOT"

            train_source, train_target = _extract_pair_values(train_df, source_name, target_name)
            test_source, test_target = _extract_pair_values(test_df, source_name, target_name)

            if train_source.size == 0 or test_source.size == 0:
                continue

            for lag in lags:
                train_result = run_method(
                    method=method,
                    source=train_source,
                    target=train_target,
                    source_name=source_name,
                    target_name=target_name,
                    lag=lag,
                    n_permutations=args.n_permutations,
                    alpha=args.alpha,
                    representation=args.representation,
                    segment="train",
                    is_control=is_control,
                    k_history_target=args.k_history_target,
                    k_history_source=args.k_history_source,
                    k_neighbors=args.k_neighbors,
                )
                train_results.append(train_result)

                test_result = run_method(
                    method=method,
                    source=test_source,
                    target=test_target,
                    source_name=source_name,
                    target_name=target_name,
                    lag=lag,
                    n_permutations=args.n_permutations,
                    alpha=args.alpha,
                    representation=args.representation,
                    segment="test",
                    is_control=is_control,
                    k_history_target=args.k_history_target,
                    k_history_source=args.k_history_source,
                    k_neighbors=args.k_neighbors,
                )
                test_results.append(test_result)

                all_results.append({
                    "method": method,
                    "source": source_name,
                    "target": target_name,
                    "lag": lag,
                    "is_control": is_control,
                    "train": asdict(train_result),
                    "test": asdict(test_result),
                })

    # Apply FDR correction by method/control to avoid mixing ecosystems with controls
    train_corrected = apply_fdr_correction(
        train_results, alpha=args.alpha, group_by=["method", "is_control"]
    )
    test_corrected = apply_fdr_correction(
        test_results, alpha=args.alpha, group_by=["method", "is_control"]
    )

    # Update results with corrected q-values
    for i, (tc, testc) in enumerate(zip(train_corrected, test_corrected)):
        all_results[i]["train"]["q_value"] = tc.q_value
        all_results[i]["train"]["is_significant"] = tc.is_significant
        all_results[i]["test"]["q_value"] = testc.q_value
        all_results[i]["test"]["is_significant"] = testc.is_significant

    # Summary statistics
    n_significant_train = sum(1 for r in train_corrected if r.is_significant)
    n_significant_test = sum(1 for r in test_corrected if r.is_significant)

    # Separate ecosystem vs control
    ecosystem_train_sig = sum(
        1 for r, res in zip(train_corrected, all_results)
        if r.is_significant and not res["is_control"]
    )
    control_train_sig = sum(
        1 for r, res in zip(train_corrected, all_results)
        if r.is_significant and res["is_control"]
    )
    ecosystem_test_sig = sum(
        1 for r, res in zip(test_corrected, all_results)
        if r.is_significant and not res["is_control"]
    )
    control_test_sig = sum(
        1 for r, res in zip(test_corrected, all_results)
        if r.is_significant and res["is_control"]
    )

    # Build output payload
    payload = {
        "analysis": "alternative_coupling_methods",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "keno": args.keno,
            "lotto": args.lotto,
            "eurojackpot": args.eurojackpot if ej_available else None,
            "methods": methods,
            "lags": lags,
            "representation": args.representation,
            "k_history_target": args.k_history_target,
            "k_history_source": args.k_history_source,
            "k_neighbors": args.k_neighbors,
            "n_permutations": args.n_permutations,
            "alpha": args.alpha,
            "split_date": args.split_date,
            "synthetic": args.use_synthetic,
        },
        "data": {
            "keno_draws": len(keno.dates),
            "lotto_draws": len(lotto.dates),
            "eurojackpot_draws": len(ej.dates) if ej else 0,
            "train_samples": len(train_df),
            "test_samples": len(test_df),
        },
        "summary": {
            "total_tests": len(all_results),
            "train_significant": n_significant_train,
            "test_significant": n_significant_test,
            "ecosystem_train_significant": ecosystem_train_sig,
            "ecosystem_test_significant": ecosystem_test_sig,
            "control_train_significant": control_train_sig,
            "control_test_significant": control_test_sig,
        },
        "results": all_results,
    }

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, cls=NumpyEncoder), encoding="utf-8")

    # Print summary
    print("=" * 80)
    print("Alternative Coupling Analysis - Summary")
    print("=" * 80)
    print(f"Output: {args.output}")
    print(f"Methods: {', '.join(methods)}")
    print(f"Lags: {lags}")
    print(f"Representation: {args.representation}")
    print()
    print(f"Total tests: {len(all_results)}")
    print()
    print("TRAIN SET (before {})".format(args.split_date))
    print(f"  Significant (FDR < {args.alpha}): {n_significant_train}")
    print(f"    Ecosystem pairs: {ecosystem_train_sig}")
    print(f"    Control pairs:   {control_train_sig}")
    print()
    print("TEST SET (after {})".format(args.split_date))
    print(f"  Significant (FDR < {args.alpha}): {n_significant_test}")
    print(f"    Ecosystem pairs: {ecosystem_test_sig}")
    print(f"    Control pairs:   {control_test_sig}")
    print()

    # Interpretation
    if ecosystem_train_sig > 0 and ecosystem_test_sig > 0:
        print("NOTE: Cross-lottery coupling detected in BOTH train and test sets.")
        print("      This suggests genuine ecosystem effects (if control pairs show fewer hits).")
    elif ecosystem_train_sig > 0 and ecosystem_test_sig == 0:
        print("WARNING: Coupling found in train but NOT in test set.")
        print("         This may indicate overfitting or period-specific effects.")
    else:
        print("No significant coupling detected between German lottery games.")

    if control_train_sig > 0 or control_test_sig > 0:
        print()
        print("WARNING: EuroJackpot (negative control) shows coupling signals.")
        print("         This may indicate false positives or broader effects.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
