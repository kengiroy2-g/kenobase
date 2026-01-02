#!/usr/bin/env python3
"""Cross-lottery coupling analysis (KENO/Lotto/Auswahlwette/Gluecksspirale/Eurowette/EuroJackpot).

This script is an exploratory tool to test whether number behavior shows
cross-game dependencies (possibly time-shifted and jackpot-conditioned).

Examples:
  python scripts/analyze_cross_lottery_coupling.py
  python scripts/analyze_cross_lottery_coupling.py --lags 0 1 2 7 --min-support 30
  python scripts/analyze_cross_lottery_coupling.py --output results/cross_lottery_coupling.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.cross_lottery_coupling import (
    bh_fdr,
    conditional_lifts_keno_position_triggers,
    conditional_lifts_number_triggers,
    conditional_lifts_ordered_value_triggers,
    jackpot_overlap_analysis,
    pair_overlap_significance,
    top_pairs_by_lift,
    to_jsonable,
    GameDraws,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-lottery coupling analysis")
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
        help="LOTTO CSV with jackpot column (default: data/raw/lotto/LOTTO_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--auswahlwette",
        type=str,
        default="data/raw/auswahlwette/AW_ab_2022_bereinigt.csv",
        help="Auswahlwette CSV (default: data/raw/auswahlwette/AW_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--gluecksspirale",
        type=str,
        default="data/raw/gluecksspirale/GS_ab_2022_bereinigt.csv",
        help="Gluecksspirale CSV (default: data/raw/gluecksspirale/GS_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--eurowette",
        type=str,
        default="data/raw/eurowette/EW_ab_2022_bereinigt.csv",
        help="Eurowette CSV (default: data/raw/eurowette/EW_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--eurojackpot",
        type=str,
        default="data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv",
        help="EuroJackpot CSV with jackpot column (default: data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv)",
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
        default=30,
        help="Min support for number triggers (default: 30)",
    )
    parser.add_argument(
        "--min-support-pos",
        type=int,
        default=20,
        help="Min support for KENO position triggers (default: 20)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold (default: 0.05)",
    )
    parser.add_argument(
        "--top-k-pairs",
        type=int,
        default=200,
        help="Top-k pairs per game for overlap tests (default: 200)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/cross_lottery_coupling.json",
        help="Output JSON (default: results/cross_lottery_coupling.json)",
    )
    return parser.parse_args()


def _load_keno(path: str) -> GameDraws:
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
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    num_cols = [f"L{i}" for i in range(1, 7)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 50), dtype=np.int8)  # 1..49
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols]
        for n in nums:
            if 1 <= n <= 49:
                presence[i, n] = 1

    jackpot_map: dict = {}
    if "Jackpot_Kl1" in df.columns:
        for d, v in zip(dates, df["Jackpot_Kl1"].tolist(), strict=False):
            try:
                jackpot_map[d] = int(v)
            except Exception:
                jackpot_map[d] = 0

    return GameDraws(
        name="LOTTO",
        pool_max=49,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=jackpot_map,
    )


def _load_auswahlwette(path: str) -> GameDraws:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    num_cols = [f"A{i}" for i in range(1, 7)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 50), dtype=np.int8)  # 1..49
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols]
        for n in nums:
            if 1 <= n <= 49:
                presence[i, n] = 1

    return GameDraws(
        name="AUSWAHLWETTE",
        pool_max=49,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


def _load_gluecksspirale(path: str) -> GameDraws:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    cols = ["Kl1", "Kl2", "Kl3", "Kl4", "Kl5", "Kl6_1", "Kl6_2", "Kl7"]
    dates = [d.date() for d in df["Datum"].tolist()]

    ordered_numbers: list[list[int]] = []
    for _, row in df.iterrows():
        ordered_numbers.append([int(row[c]) for c in cols])

    # Not a number pool game; keep a minimal presence matrix to satisfy GameDraws.
    presence = np.zeros((len(df), 2), dtype=np.int8)
    return GameDraws(
        name="GLUECKSSPIRALE",
        pool_max=1,
        draw_size=0,
        dates=dates,
        presence=presence,
        ordered_numbers=ordered_numbers,
        jackpot_winners=None,
    )


def _load_eurowette(path: str) -> GameDraws:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    cols = [f"T{i}" for i in range(1, 14)]
    dates = [d.date() for d in df["Datum"].tolist()]

    ordered_numbers: list[list[int]] = []
    for _, row in df.iterrows():
        ordered_numbers.append([int(row[c]) for c in cols])

    presence = np.zeros((len(df), 2), dtype=np.int8)
    return GameDraws(
        name="EUROWETTE",
        pool_max=1,
        draw_size=0,
        dates=dates,
        presence=presence,
        ordered_numbers=ordered_numbers,
        jackpot_winners=None,
    )


def _load_eurojackpot(path: str) -> GameDraws:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    num_cols = [f"E{i}" for i in range(1, 6)]
    dates = [d.date() for d in df["Datum"].tolist()]

    presence = np.zeros((len(df), 51), dtype=np.int8)  # 1..50
    for i, row in df.iterrows():
        nums = [int(row[c]) for c in num_cols]
        for n in nums:
            if 1 <= n <= 50:
                presence[i, n] = 1

    jackpot_map: dict = {}
    if "Jackpot" in df.columns:
        for d, v in zip(dates, df["Jackpot"].tolist(), strict=False):
            try:
                jackpot_map[d] = int(v)
            except Exception:
                jackpot_map[d] = 0

    return GameDraws(
        name="EUROJACKPOT",
        pool_max=50,
        draw_size=5,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=jackpot_map,
    )


def main() -> int:
    args = parse_args()

    keno = _load_keno(args.keno)
    lotto = _load_lotto(args.lotto)
    aw = _load_auswahlwette(args.auswahlwette)
    gs = _load_gluecksspirale(args.gluecksspirale)
    ew = _load_eurowette(args.eurowette)
    ej = _load_eurojackpot(args.eurojackpot)

    lags = [int(x) for x in args.lags]
    lags = sorted(set([x for x in lags if x >= 0]))

    # Pair overlap: restrict to 1..49 for comparability.
    pairs_keno_49 = top_pairs_by_lift(game=keno, restrict_max=49, top_k=args.top_k_pairs)
    pairs_lotto_49 = top_pairs_by_lift(game=lotto, restrict_max=49, top_k=args.top_k_pairs)
    pairs_aw_49 = top_pairs_by_lift(game=aw, restrict_max=49, top_k=args.top_k_pairs)
    pairs_ej_49 = top_pairs_by_lift(game=ej, restrict_max=49, top_k=args.top_k_pairs)

    overlap_keno_lotto = pair_overlap_significance(
        pair_lists=[pairs_keno_49, pairs_lotto_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )
    overlap_keno_ej = pair_overlap_significance(
        pair_lists=[pairs_keno_49, pairs_ej_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )
    overlap_lotto_ej = pair_overlap_significance(
        pair_lists=[pairs_lotto_49, pairs_ej_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )
    overlap_keno_aw = pair_overlap_significance(
        pair_lists=[pairs_keno_49, pairs_aw_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )
    overlap_lotto_aw = pair_overlap_significance(
        pair_lists=[pairs_lotto_49, pairs_aw_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )
    overlap_ej_aw = pair_overlap_significance(
        pair_lists=[pairs_ej_49, pairs_aw_49],
        range_max=49,
        top_k=min(args.top_k_pairs, 200),
    )

    # Jackpot-conditioned overlap (same-day by default).
    jack_lotto_keno = jackpot_overlap_analysis(source_with_jackpot=lotto, target=keno, lag_days=0)
    jack_ej_keno = jackpot_overlap_analysis(source_with_jackpot=ej, target=keno, lag_days=0)

    # Conditional lifts
    candidates: dict = {"number_triggers": [], "keno_position_triggers": [], "ordered_value_triggers": []}
    for lag in lags:
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=keno,
                target=lotto,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=keno,
                target=ej,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=keno,
                target=aw,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        # Reverse direction (other games -> KENO) for practical cross-game filters.
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=lotto,
                target=keno,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=ej,
                target=keno,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["number_triggers"].extend(
            conditional_lifts_number_triggers(
                source=aw,
                target=keno,
                lag_days=lag,
                min_support=args.min_support,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["keno_position_triggers"].extend(
            conditional_lifts_keno_position_triggers(
                keno=keno,
                target=lotto,
                lag_days=lag,
                min_support=args.min_support_pos,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["keno_position_triggers"].extend(
            conditional_lifts_keno_position_triggers(
                keno=keno,
                target=ej,
                lag_days=lag,
                min_support=args.min_support_pos,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["keno_position_triggers"].extend(
            conditional_lifts_keno_position_triggers(
                keno=keno,
                target=aw,
                lag_days=lag,
                min_support=args.min_support_pos,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["ordered_value_triggers"].extend(
            conditional_lifts_ordered_value_triggers(
                source=gs,
                target=keno,
                lag_days=lag,
                position_labels=["Kl1", "Kl2", "Kl3", "Kl4", "Kl5", "Kl6_1", "Kl6_2", "Kl7"],
                min_support=args.min_support_pos,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )
        candidates["ordered_value_triggers"].extend(
            conditional_lifts_ordered_value_triggers(
                source=ew,
                target=keno,
                lag_days=lag,
                position_labels=[f"T{i}" for i in range(1, 14)],
                min_support=args.min_support_pos,
                alpha_fdr=args.alpha,
                max_results=200,
                filter_by_alpha=False,
            )
        )

    significant = {
        "number_triggers": [r for r in candidates["number_triggers"] if float(r.q_value) <= float(args.alpha)],
        "keno_position_triggers": [
            r for r in candidates["keno_position_triggers"] if float(r.q_value) <= float(args.alpha)
        ],
        "ordered_value_triggers": [
            r for r in candidates["ordered_value_triggers"] if float(r.q_value) <= float(args.alpha)
        ],
    }

    payload = {
        "analysis": "cross_lottery_coupling",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "keno": args.keno,
            "lotto": args.lotto,
            "auswahlwette": args.auswahlwette,
            "gluecksspirale": args.gluecksspirale,
            "eurowette": args.eurowette,
            "eurojackpot": args.eurojackpot,
            "lags": lags,
            "min_support": int(args.min_support),
            "min_support_pos": int(args.min_support_pos),
            "alpha_fdr": float(args.alpha),
            "top_k_pairs": int(args.top_k_pairs),
        },
        "games": {
            "KENO": {"draws": len(keno.dates), "start": str(keno.dates[0]), "end": str(keno.dates[-1])},
            "LOTTO": {"draws": len(lotto.dates), "start": str(lotto.dates[0]), "end": str(lotto.dates[-1])},
            "AUSWAHLWETTE": {"draws": len(aw.dates), "start": str(aw.dates[0]), "end": str(aw.dates[-1])},
            "GLUECKSSPIRALE": {"draws": len(gs.dates), "start": str(gs.dates[0]), "end": str(gs.dates[-1])},
            "EUROWETTE": {"draws": len(ew.dates), "start": str(ew.dates[0]), "end": str(ew.dates[-1])},
            "EUROJACKPOT": {"draws": len(ej.dates), "start": str(ej.dates[0]), "end": str(ej.dates[-1])},
        },
        "pair_lifts_top": {
            "keno_1_49": [asdict(p) for p in pairs_keno_49[:50]],
            "lotto_1_49": [asdict(p) for p in pairs_lotto_49[:50]],
            "auswahlwette_1_49": [asdict(p) for p in pairs_aw_49[:50]],
            "eurojackpot_1_49": [asdict(p) for p in pairs_ej_49[:50]],
        },
        "pair_overlap": {
            "keno_lotto": asdict(overlap_keno_lotto),
            "keno_eurojackpot": asdict(overlap_keno_ej),
            "lotto_eurojackpot": asdict(overlap_lotto_ej),
            "keno_auswahlwette": asdict(overlap_keno_aw),
            "lotto_auswahlwette": asdict(overlap_lotto_aw),
            "eurojackpot_auswahlwette": asdict(overlap_ej_aw),
        },
        "jackpot_overlap": {
            "lotto_vs_keno": asdict(jack_lotto_keno),
            "eurojackpot_vs_keno": asdict(jack_ej_keno),
        },
        "conditional_lifts": {
            "alpha_fdr": float(args.alpha),
            "top_candidates": to_jsonable(candidates),
            "significant": to_jsonable(significant),
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 100)
    print("Cross-Lottery Coupling Analysis")
    print(f"Output: {args.output}")
    print("=" * 100)
    print(
        f"KENO draws={len(keno.dates)}  LOTTO draws={len(lotto.dates)}  "
        f"AUSWAHLWETTE draws={len(aw.dates)}  GLUECKSSPIRALE draws={len(gs.dates)}  "
        f"EUROWETTE draws={len(ew.dates)}  EUROJACKPOT draws={len(ej.dates)}"
    )
    print()
    print("Pair overlap (top-k, range 1..49):")
    print(
        f"  KENO vs LOTTO: overlap={overlap_keno_lotto.overlap} exp={overlap_keno_lotto.expected_overlap:.2f} "
        f"p={overlap_keno_lotto.p_value:.4g}"
    )
    print(
        f"  KENO vs EJ:    overlap={overlap_keno_ej.overlap} exp={overlap_keno_ej.expected_overlap:.2f} "
        f"p={overlap_keno_ej.p_value:.4g}"
    )
    print(
        f"  LOTTO vs EJ:   overlap={overlap_lotto_ej.overlap} exp={overlap_lotto_ej.expected_overlap:.2f} "
        f"p={overlap_lotto_ej.p_value:.4g}"
    )
    print(
        f"  KENO vs AW:    overlap={overlap_keno_aw.overlap} exp={overlap_keno_aw.expected_overlap:.2f} "
        f"p={overlap_keno_aw.p_value:.4g}"
    )
    print(
        f"  LOTTO vs AW:   overlap={overlap_lotto_aw.overlap} exp={overlap_lotto_aw.expected_overlap:.2f} "
        f"p={overlap_lotto_aw.p_value:.4g}"
    )
    print(
        f"  EJ vs AW:      overlap={overlap_ej_aw.overlap} exp={overlap_ej_aw.expected_overlap:.2f} "
        f"p={overlap_ej_aw.p_value:.4g}"
    )
    print()
    print("Jackpot-conditioned overlap (same-day):")
    if jack_lotto_keno.p_value is not None:
        print(
            f"  LOTTO jackpot -> KENO overlap delta={jack_lotto_keno.delta:+.3f} "
            f"(n_jackpot={jack_lotto_keno.n_jackpot}/{jack_lotto_keno.n_total}, p={jack_lotto_keno.p_value:.4g})"
        )
    if jack_ej_keno.p_value is not None:
        print(
            f"  EJ jackpot -> KENO overlap delta={jack_ej_keno.delta:+.3f} "
            f"(n_jackpot={jack_ej_keno.n_jackpot}/{jack_ej_keno.n_total}, p={jack_ej_keno.p_value:.4g})"
        )
    print()
    print(
        "Conditional lifts stored under payload['conditional_lifts'] "
        f"(significant: number={len(significant['number_triggers'])}, "
        f"keno_position={len(significant['keno_position_triggers'])}, "
        f"ordered_value={len(significant['ordered_value_triggers'])})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
