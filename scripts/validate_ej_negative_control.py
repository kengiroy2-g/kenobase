#!/usr/bin/env python3
"""EuroJackpot Negative Control Validation (EJ-001).

This script validates that EuroJackpot, as an EXTERNAL (international) lottery,
does NOT show significant cross-correlations with the German ecosystem (KENO/LOTTO/AW).

Falsification Logic:
- DE ecosystem hypothesis: KENO/LOTTO/Auswahlwette show inter-correlations
- Negative control: EJ (external, international) should NOT correlate with DE games
- If EJ->KENO shows q<=0.05, the ecosystem hypothesis is weakened

Acceptance Criteria:
- Train/Test split (80/20)
- Rules mined in Train, frozen for Test
- EJ triggers must show q>0.05 (no significant correlation to DE games)
- DE-internal triggers may show q<=0.05 (confirms ecosystem hypothesis)

Examples:
  python scripts/validate_ej_negative_control.py
  python scripts/validate_ej_negative_control.py --train-ratio 0.7 --output results/ej_negative_control.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.cross_lottery_coupling import (
    ConditionalLift,
    GameDraws,
    bh_fdr,
    conditional_lifts_number_triggers,
    pair_overlap_significance,
    to_jsonable,
    top_pairs_by_lift,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EuroJackpot Negative Control Validation")
    parser.add_argument(
        "--keno",
        type=str,
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="KENO CSV",
    )
    parser.add_argument(
        "--lotto",
        type=str,
        default="data/raw/lotto/LOTTO_ab_2022_bereinigt.csv",
        help="LOTTO CSV",
    )
    parser.add_argument(
        "--auswahlwette",
        type=str,
        default="data/raw/auswahlwette/AW_ab_2022_bereinigt.csv",
        help="Auswahlwette CSV",
    )
    parser.add_argument(
        "--eurojackpot",
        type=str,
        default="data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv",
        help="EuroJackpot CSV",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Train/Test split ratio (default: 0.8)",
    )
    parser.add_argument(
        "--lags",
        type=int,
        nargs="*",
        default=[0, 1, 2, 7],
        help="Lag days for conditional tests (default: 0 1 2 7)",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=20,
        help="Min support for number triggers (default: 20)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold (default: 0.05)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/ej_negative_control.json",
        help="Output JSON",
    )
    return parser.parse_args()


def _load_game(
    path: str,
    name: str,
    pool_max: int,
    draw_size: int,
    num_cols: list[str],
    date_format: str = "%d.%m.%Y",
) -> GameDraws:
    """Generic game loader."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format=date_format)
    df = df.sort_values("Datum").reset_index(drop=True)

    dates = [d.date() for d in df["Datum"].tolist()]
    presence = np.zeros((len(df), pool_max + 1), dtype=np.int8)

    for i, row in df.iterrows():
        for c in num_cols:
            try:
                n = int(row[c])
                if 1 <= n <= pool_max:
                    presence[i, n] = 1
            except (ValueError, KeyError):
                continue

    return GameDraws(
        name=name,
        pool_max=pool_max,
        draw_size=draw_size,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


def split_game_data(game: GameDraws, train_ratio: float) -> tuple[GameDraws, GameDraws]:
    """Split GameDraws into train and test sets by date."""
    n = len(game.dates)
    split_idx = int(n * train_ratio)

    train = GameDraws(
        name=game.name,
        pool_max=game.pool_max,
        draw_size=game.draw_size,
        dates=game.dates[:split_idx],
        presence=game.presence[:split_idx],
        ordered_numbers=game.ordered_numbers[:split_idx] if game.ordered_numbers else None,
        jackpot_winners={d: v for d, v in (game.jackpot_winners or {}).items() if d in game.dates[:split_idx]},
    )

    test = GameDraws(
        name=game.name,
        pool_max=game.pool_max,
        draw_size=game.draw_size,
        dates=game.dates[split_idx:],
        presence=game.presence[split_idx:],
        ordered_numbers=game.ordered_numbers[split_idx:] if game.ordered_numbers else None,
        jackpot_winners={d: v for d, v in (game.jackpot_winners or {}).items() if d in game.dates[split_idx:]},
    )

    return train, test


def compute_lifts_for_pair(
    source: GameDraws,
    target: GameDraws,
    lags: list[int],
    min_support: int,
    alpha: float,
) -> list[ConditionalLift]:
    """Compute conditional lifts for a source->target pair across lags."""
    results: list[ConditionalLift] = []
    for lag in lags:
        lifts = conditional_lifts_number_triggers(
            source=source,
            target=target,
            lag_days=lag,
            min_support=min_support,
            alpha_fdr=alpha,
            max_results=500,
            filter_by_alpha=False,
        )
        results.extend(lifts)
    return results


def validate_on_test(
    rules: list[ConditionalLift],
    source_test: GameDraws,
    target_test: GameDraws,
    lags: list[int],
    min_support: int,
    alpha: float,
) -> dict[str, Any]:
    """Validate train-mined rules on test data."""
    # Re-compute lifts on test set
    test_lifts = compute_lifts_for_pair(source_test, target_test, lags, min_support, alpha)

    # Create lookup for train rules
    train_keys = {(r.source, r.target, r.lag_days, r.trigger, r.target_number) for r in rules if r.q_value <= alpha}

    # Find matching rules in test
    validated = []
    for tl in test_lifts:
        key = (tl.source, tl.target, tl.lag_days, tl.trigger, tl.target_number)
        if key in train_keys:
            validated.append(tl)

    # Check how many train rules survived in test with q<=alpha
    survived = [v for v in validated if v.q_value <= alpha]

    return {
        "train_significant_count": len(train_keys),
        "test_evaluated_count": len(validated),
        "test_survived_count": len(survived),
        "survival_rate": len(survived) / max(1, len(train_keys)),
        "survived_rules": [asdict(r) for r in survived[:20]],
    }


def main() -> int:
    args = parse_args()
    lags = sorted(set([x for x in args.lags if x >= 0]))

    print("=" * 80)
    print("EuroJackpot Negative Control Validation (EJ-001)")
    print("=" * 80)
    print(f"Train ratio: {args.train_ratio}")
    print(f"Lags: {lags}")
    print(f"Alpha (FDR): {args.alpha}")
    print()

    # Load games
    keno = _load_game(args.keno, "KENO", 70, 20, [f"Keno_Z{i}" for i in range(1, 21)])
    lotto = _load_game(args.lotto, "LOTTO", 49, 6, [f"L{i}" for i in range(1, 7)])
    aw = _load_game(args.auswahlwette, "AUSWAHLWETTE", 49, 6, [f"A{i}" for i in range(1, 7)])
    ej = _load_game(args.eurojackpot, "EUROJACKPOT", 50, 5, [f"E{i}" for i in range(1, 6)])

    print(f"KENO: {len(keno.dates)} draws")
    print(f"LOTTO: {len(lotto.dates)} draws")
    print(f"AUSWAHLWETTE: {len(aw.dates)} draws")
    print(f"EUROJACKPOT: {len(ej.dates)} draws")
    print()

    # Split into train/test
    keno_train, keno_test = split_game_data(keno, args.train_ratio)
    lotto_train, lotto_test = split_game_data(lotto, args.train_ratio)
    aw_train, aw_test = split_game_data(aw, args.train_ratio)
    ej_train, ej_test = split_game_data(ej, args.train_ratio)

    print(f"Train/Test splits:")
    print(f"  KENO: {len(keno_train.dates)} / {len(keno_test.dates)}")
    print(f"  LOTTO: {len(lotto_train.dates)} / {len(lotto_test.dates)}")
    print(f"  AW: {len(aw_train.dates)} / {len(aw_test.dates)}")
    print(f"  EJ: {len(ej_train.dates)} / {len(ej_test.dates)}")
    print()

    results: dict[str, Any] = {
        "analysis": "ej_negative_control",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "train_ratio": args.train_ratio,
            "lags": lags,
            "min_support": args.min_support,
            "alpha_fdr": args.alpha,
        },
        "data": {
            "keno_total": len(keno.dates),
            "lotto_total": len(lotto.dates),
            "aw_total": len(aw.dates),
            "ej_total": len(ej.dates),
        },
    }

    # =========================================================================
    # SECTION 1: DE Internal Correlations (should show some significance)
    # =========================================================================
    print("-" * 80)
    print("SECTION 1: DE Internal Cross-Correlations (KENO <-> LOTTO <-> AW)")
    print("-" * 80)

    # KENO -> LOTTO
    keno_lotto_train = compute_lifts_for_pair(keno_train, lotto_train, lags, args.min_support, args.alpha)
    keno_lotto_sig = [r for r in keno_lotto_train if r.q_value <= args.alpha]
    print(f"KENO->LOTTO (train): {len(keno_lotto_sig)} significant triggers (q<={args.alpha})")

    # LOTTO -> KENO
    lotto_keno_train = compute_lifts_for_pair(lotto_train, keno_train, lags, args.min_support, args.alpha)
    lotto_keno_sig = [r for r in lotto_keno_train if r.q_value <= args.alpha]
    print(f"LOTTO->KENO (train): {len(lotto_keno_sig)} significant triggers (q<={args.alpha})")

    # KENO -> AW
    keno_aw_train = compute_lifts_for_pair(keno_train, aw_train, lags, args.min_support, args.alpha)
    keno_aw_sig = [r for r in keno_aw_train if r.q_value <= args.alpha]
    print(f"KENO->AW (train): {len(keno_aw_sig)} significant triggers (q<={args.alpha})")

    # AW -> KENO
    aw_keno_train = compute_lifts_for_pair(aw_train, keno_train, lags, args.min_support, args.alpha)
    aw_keno_sig = [r for r in aw_keno_train if r.q_value <= args.alpha]
    print(f"AW->KENO (train): {len(aw_keno_sig)} significant triggers (q<={args.alpha})")

    # LOTTO -> AW
    lotto_aw_train = compute_lifts_for_pair(lotto_train, aw_train, lags, args.min_support, args.alpha)
    lotto_aw_sig = [r for r in lotto_aw_train if r.q_value <= args.alpha]
    print(f"LOTTO->AW (train): {len(lotto_aw_sig)} significant triggers (q<={args.alpha})")

    de_internal_total_sig = len(keno_lotto_sig) + len(lotto_keno_sig) + len(keno_aw_sig) + len(aw_keno_sig) + len(lotto_aw_sig)
    print(f"\nDE Internal Total Significant: {de_internal_total_sig}")

    results["de_internal"] = {
        "keno_lotto": {"train_significant": len(keno_lotto_sig), "top_rules": [asdict(r) for r in keno_lotto_sig[:10]]},
        "lotto_keno": {"train_significant": len(lotto_keno_sig), "top_rules": [asdict(r) for r in lotto_keno_sig[:10]]},
        "keno_aw": {"train_significant": len(keno_aw_sig), "top_rules": [asdict(r) for r in keno_aw_sig[:10]]},
        "aw_keno": {"train_significant": len(aw_keno_sig), "top_rules": [asdict(r) for r in aw_keno_sig[:10]]},
        "lotto_aw": {"train_significant": len(lotto_aw_sig), "top_rules": [asdict(r) for r in lotto_aw_sig[:10]]},
        "total_significant": de_internal_total_sig,
    }

    # =========================================================================
    # SECTION 2: EJ External Correlations (should NOT show significance)
    # =========================================================================
    print()
    print("-" * 80)
    print("SECTION 2: EJ External Cross-Correlations (NEGATIVE CONTROL)")
    print("-" * 80)
    print("Expectation: EJ is EXTERNAL (international), should NOT correlate with DE games")
    print()

    # EJ -> KENO
    ej_keno_train = compute_lifts_for_pair(ej_train, keno_train, lags, args.min_support, args.alpha)
    ej_keno_sig = [r for r in ej_keno_train if r.q_value <= args.alpha]
    print(f"EJ->KENO (train): {len(ej_keno_sig)} significant triggers (q<={args.alpha})")

    # KENO -> EJ
    keno_ej_train = compute_lifts_for_pair(keno_train, ej_train, lags, args.min_support, args.alpha)
    keno_ej_sig = [r for r in keno_ej_train if r.q_value <= args.alpha]
    print(f"KENO->EJ (train): {len(keno_ej_sig)} significant triggers (q<={args.alpha})")

    # EJ -> LOTTO
    ej_lotto_train = compute_lifts_for_pair(ej_train, lotto_train, lags, args.min_support, args.alpha)
    ej_lotto_sig = [r for r in ej_lotto_train if r.q_value <= args.alpha]
    print(f"EJ->LOTTO (train): {len(ej_lotto_sig)} significant triggers (q<={args.alpha})")

    # LOTTO -> EJ
    lotto_ej_train = compute_lifts_for_pair(lotto_train, ej_train, lags, args.min_support, args.alpha)
    lotto_ej_sig = [r for r in lotto_ej_train if r.q_value <= args.alpha]
    print(f"LOTTO->EJ (train): {len(lotto_ej_sig)} significant triggers (q<={args.alpha})")

    # EJ -> AW
    ej_aw_train = compute_lifts_for_pair(ej_train, aw_train, lags, args.min_support, args.alpha)
    ej_aw_sig = [r for r in ej_aw_train if r.q_value <= args.alpha]
    print(f"EJ->AW (train): {len(ej_aw_sig)} significant triggers (q<={args.alpha})")

    # AW -> EJ
    aw_ej_train = compute_lifts_for_pair(aw_train, ej_train, lags, args.min_support, args.alpha)
    aw_ej_sig = [r for r in aw_ej_train if r.q_value <= args.alpha]
    print(f"AW->EJ (train): {len(aw_ej_sig)} significant triggers (q<={args.alpha})")

    ej_external_total_sig = len(ej_keno_sig) + len(keno_ej_sig) + len(ej_lotto_sig) + len(lotto_ej_sig) + len(ej_aw_sig) + len(aw_ej_sig)
    print(f"\nEJ External Total Significant: {ej_external_total_sig}")

    results["ej_external"] = {
        "ej_keno": {"train_significant": len(ej_keno_sig), "top_rules": [asdict(r) for r in ej_keno_sig[:10]]},
        "keno_ej": {"train_significant": len(keno_ej_sig), "top_rules": [asdict(r) for r in keno_ej_sig[:10]]},
        "ej_lotto": {"train_significant": len(ej_lotto_sig), "top_rules": [asdict(r) for r in ej_lotto_sig[:10]]},
        "lotto_ej": {"train_significant": len(lotto_ej_sig), "top_rules": [asdict(r) for r in lotto_ej_sig[:10]]},
        "ej_aw": {"train_significant": len(ej_aw_sig), "top_rules": [asdict(r) for r in ej_aw_sig[:10]]},
        "aw_ej": {"train_significant": len(aw_ej_sig), "top_rules": [asdict(r) for r in aw_ej_sig[:10]]},
        "total_significant": ej_external_total_sig,
    }

    # =========================================================================
    # SECTION 3: Validation on Test Set
    # =========================================================================
    print()
    print("-" * 80)
    print("SECTION 3: Out-of-Sample Validation (Test Set)")
    print("-" * 80)

    # Validate DE-internal rules on test
    keno_lotto_test_val = validate_on_test(keno_lotto_train, keno_test, lotto_test, lags, args.min_support, args.alpha)
    print(f"KENO->LOTTO test survival: {keno_lotto_test_val['test_survived_count']}/{keno_lotto_test_val['train_significant_count']} ({keno_lotto_test_val['survival_rate']:.1%})")

    lotto_keno_test_val = validate_on_test(lotto_keno_train, lotto_test, keno_test, lags, args.min_support, args.alpha)
    print(f"LOTTO->KENO test survival: {lotto_keno_test_val['test_survived_count']}/{lotto_keno_test_val['train_significant_count']} ({lotto_keno_test_val['survival_rate']:.1%})")

    # Validate EJ-external rules on test
    ej_keno_test_val = validate_on_test(ej_keno_train, ej_test, keno_test, lags, args.min_support, args.alpha)
    print(f"EJ->KENO test survival: {ej_keno_test_val['test_survived_count']}/{ej_keno_test_val['train_significant_count']} ({ej_keno_test_val['survival_rate']:.1%})")

    keno_ej_test_val = validate_on_test(keno_ej_train, keno_test, ej_test, lags, args.min_support, args.alpha)
    print(f"KENO->EJ test survival: {keno_ej_test_val['test_survived_count']}/{keno_ej_test_val['train_significant_count']} ({keno_ej_test_val['survival_rate']:.1%})")

    results["test_validation"] = {
        "de_internal": {
            "keno_lotto": keno_lotto_test_val,
            "lotto_keno": lotto_keno_test_val,
        },
        "ej_external": {
            "ej_keno": ej_keno_test_val,
            "keno_ej": keno_ej_test_val,
        },
    }

    # =========================================================================
    # SECTION 4: Pair Overlap Analysis
    # =========================================================================
    print()
    print("-" * 80)
    print("SECTION 4: Pair Overlap Analysis (1..49 range)")
    print("-" * 80)

    pairs_keno = top_pairs_by_lift(game=keno, restrict_max=49, top_k=200)
    pairs_lotto = top_pairs_by_lift(game=lotto, restrict_max=49, top_k=200)
    pairs_aw = top_pairs_by_lift(game=aw, restrict_max=49, top_k=200)
    pairs_ej = top_pairs_by_lift(game=ej, restrict_max=49, top_k=200)

    # DE internal overlaps
    overlap_keno_lotto = pair_overlap_significance(pair_lists=[pairs_keno, pairs_lotto], range_max=49, top_k=100)
    overlap_keno_aw = pair_overlap_significance(pair_lists=[pairs_keno, pairs_aw], range_max=49, top_k=100)
    overlap_lotto_aw = pair_overlap_significance(pair_lists=[pairs_lotto, pairs_aw], range_max=49, top_k=100)

    # EJ external overlaps
    overlap_keno_ej = pair_overlap_significance(pair_lists=[pairs_keno, pairs_ej], range_max=49, top_k=100)
    overlap_lotto_ej = pair_overlap_significance(pair_lists=[pairs_lotto, pairs_ej], range_max=49, top_k=100)
    overlap_aw_ej = pair_overlap_significance(pair_lists=[pairs_aw, pairs_ej], range_max=49, top_k=100)

    print("DE Internal Pair Overlaps:")
    print(f"  KENO vs LOTTO: overlap={overlap_keno_lotto.overlap} expected={overlap_keno_lotto.expected_overlap:.2f} p={overlap_keno_lotto.p_value:.4g}")
    print(f"  KENO vs AW:    overlap={overlap_keno_aw.overlap} expected={overlap_keno_aw.expected_overlap:.2f} p={overlap_keno_aw.p_value:.4g}")
    print(f"  LOTTO vs AW:   overlap={overlap_lotto_aw.overlap} expected={overlap_lotto_aw.expected_overlap:.2f} p={overlap_lotto_aw.p_value:.4g}")

    print("\nEJ External Pair Overlaps (NEGATIVE CONTROL):")
    print(f"  KENO vs EJ:    overlap={overlap_keno_ej.overlap} expected={overlap_keno_ej.expected_overlap:.2f} p={overlap_keno_ej.p_value:.4g}")
    print(f"  LOTTO vs EJ:   overlap={overlap_lotto_ej.overlap} expected={overlap_lotto_ej.expected_overlap:.2f} p={overlap_lotto_ej.p_value:.4g}")
    print(f"  AW vs EJ:      overlap={overlap_aw_ej.overlap} expected={overlap_aw_ej.expected_overlap:.2f} p={overlap_aw_ej.p_value:.4g}")

    results["pair_overlap"] = {
        "de_internal": {
            "keno_lotto": asdict(overlap_keno_lotto),
            "keno_aw": asdict(overlap_keno_aw),
            "lotto_aw": asdict(overlap_lotto_aw),
        },
        "ej_external": {
            "keno_ej": asdict(overlap_keno_ej),
            "lotto_ej": asdict(overlap_lotto_ej),
            "aw_ej": asdict(overlap_aw_ej),
        },
    }

    # =========================================================================
    # SECTION 5: Falsification Verdict
    # =========================================================================
    print()
    print("=" * 80)
    print("FALSIFICATION VERDICT")
    print("=" * 80)

    # Hypothesis: DE games correlate, EJ does not
    de_has_correlations = de_internal_total_sig > 0
    ej_has_correlations = ej_external_total_sig > 0

    # Check pair overlaps
    de_pair_sig = any(p < args.alpha for p in [overlap_keno_lotto.p_value, overlap_keno_aw.p_value, overlap_lotto_aw.p_value])
    ej_pair_sig = any(p < args.alpha for p in [overlap_keno_ej.p_value, overlap_lotto_ej.p_value, overlap_aw_ej.p_value])

    print(f"DE Internal Shows Correlations: {de_has_correlations} (total sig: {de_internal_total_sig})")
    print(f"EJ External Shows Correlations: {ej_has_correlations} (total sig: {ej_external_total_sig})")
    print(f"DE Pair Overlaps Significant: {de_pair_sig}")
    print(f"EJ Pair Overlaps Significant: {ej_pair_sig}")
    print()

    if ej_has_correlations or ej_pair_sig:
        verdict = "WEAKENED"
        explanation = "EJ (external) shows unexpected correlations with DE games - ecosystem hypothesis is weakened"
    elif de_has_correlations or de_pair_sig:
        verdict = "SUPPORTED"
        explanation = "DE games show correlations, EJ does not - ecosystem hypothesis is supported"
    else:
        verdict = "INCONCLUSIVE"
        explanation = "Neither DE nor EJ show significant correlations - no conclusion possible"

    print(f"Verdict: {verdict}")
    print(f"Explanation: {explanation}")

    results["verdict"] = {
        "status": verdict,
        "explanation": explanation,
        "de_internal_significant": de_internal_total_sig,
        "ej_external_significant": ej_external_total_sig,
        "de_pair_overlap_significant": de_pair_sig,
        "ej_pair_overlap_significant": ej_pair_sig,
        "acceptance_criteria": {
            "ej_triggers_q_gt_alpha": ej_external_total_sig == 0,
            "train_test_split_applied": True,
            "nullmodel_comparison": "FDR/BH correction applied",
        },
    }

    # Save results
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nResults saved to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
