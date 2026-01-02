#!/usr/bin/env python3
"""Train->Test backtest: mine cross-game rules on Train, evaluate frozen rules on Test (target: KENO).

This avoids a common pitfall:
Selecting "significant" rules on the full dataset and then backtesting them on the same
period inflates results (in-sample selection bias).

Default split:
  - Train: 2022-01-01 .. 2023-12-31
  - Test:  2024-01-01 .. end
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.cross_lottery_coupling import (
    GameDraws,
    conditional_lifts_number_triggers,
    conditional_lifts_ordered_value_triggers,
)
from kenobase.prediction.cross_game_rule_backtester import CrossGameRule, backtest_cross_game_rule_layer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train/Test backtest for cross-game rule layer (target: KENO)")
    parser.add_argument(
        "--train-end",
        type=str,
        default="2023-12-31",
        help="Train end date (YYYY-MM-DD), test starts after this date (default: 2023-12-31)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold for selecting rules on Train (default: 0.05)",
    )
    parser.add_argument(
        "--selection",
        type=str,
        default="significant",
        choices=["significant", "top_n"],
        help="Rule selection on Train: significant (q<=alpha) or top_n by q (default: significant)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=50,
        help="If --selection top_n: number of rules to keep (default: 50)",
    )
    parser.add_argument(
        "--only-exclusion",
        action="store_true",
        help="If set: keep only rules with lift<1 (exclusion candidates) when selecting rules",
    )
    parser.add_argument(
        "--lags",
        type=int,
        nargs="*",
        default=[0, 1, 2, 7],
        help="Lag days for mining (default: 0 1 2 7)",
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
        help="Min support for ordered_value triggers (default: 20)",
    )
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
        help="EuroJackpot CSV (default: data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--types",
        type=int,
        nargs="*",
        default=[6, 7, 8, 9, 10],
        help="Keno-Typen (Anzahl Zahlen), z.B. --types 6 7 8 9 10 (default: 6 7 8 9 10)",
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
        "--no-hard-exclude",
        action="store_true",
        help="Deaktiviert Hard-Exclude (sonst werden Exclusions als Filter angewendet)",
    )
    parser.add_argument(
        "--include-multiplier",
        type=float,
        default=1.25,
        help="Multiplikator fuer include-Regeln (default: 1.25)",
    )
    parser.add_argument(
        "--max-exclusions-per-draw",
        type=int,
        default=None,
        help="Optional: Max. Exclusion-Regeln pro Ziehung anwenden (default: None = alle)",
    )
    parser.add_argument(
        "--max-inclusions-per-draw",
        type=int,
        default=None,
        help="Optional: Max. Inclusion-Regeln pro Ziehung anwenden (default: None = alle)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/cross_game_rule_layer_train_test_backtest.json",
        help="Output JSON (default: results/cross_game_rule_layer_train_test_backtest.json)",
    )
    return parser.parse_args()


def _slice_end(draws: GameDraws, *, end_date: date) -> GameDraws:
    idx = [i for i, d in enumerate(draws.dates) if d <= end_date]
    presence = draws.presence[idx]
    ordered_numbers = [draws.ordered_numbers[i] for i in idx] if draws.ordered_numbers is not None else None
    jackpot_winners = (
        {d: int(v) for d, v in (draws.jackpot_winners or {}).items() if d <= end_date}
        if draws.jackpot_winners is not None
        else None
    )
    return GameDraws(
        name=draws.name,
        pool_max=int(draws.pool_max),
        draw_size=int(draws.draw_size),
        dates=[draws.dates[i] for i in idx],
        presence=presence,
        ordered_numbers=ordered_numbers,
        jackpot_winners=jackpot_winners,
    )


def _first_index_after(dates: list[date], cutoff: date) -> Optional[int]:
    for i, d in enumerate(dates):
        if d > cutoff:
            return int(i)
    return None


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

    return GameDraws(
        name="LOTTO",
        pool_max=49,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
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

    return GameDraws(
        name="EUROJACKPOT",
        pool_max=50,
        draw_size=5,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


def _mine_rules_train(
    *,
    keno_train: GameDraws,
    lotto_train: GameDraws,
    aw_train: GameDraws,
    ej_train: GameDraws,
    ew_train: GameDraws,
    gs_train: GameDraws,
    lags: list[int],
    alpha: float,
    min_support: int,
    min_support_pos: int,
    selection: str,
    top_n: int,
    only_exclusion: bool,
) -> list[CrossGameRule]:
    candidates = []
    filter_by_alpha = bool(selection == "significant")
    max_results = int(100000) if filter_by_alpha else int(max(1000, int(top_n) * 20))
    for lag in lags:
        candidates.extend(
            conditional_lifts_number_triggers(
                source=lotto_train,
                target=keno_train,
                lag_days=int(lag),
                min_support=int(min_support),
                max_results=max_results,
                alpha_fdr=float(alpha),
                filter_by_alpha=filter_by_alpha,
            )
        )
        candidates.extend(
            conditional_lifts_number_triggers(
                source=aw_train,
                target=keno_train,
                lag_days=int(lag),
                min_support=int(min_support),
                max_results=max_results,
                alpha_fdr=float(alpha),
                filter_by_alpha=filter_by_alpha,
            )
        )
        candidates.extend(
            conditional_lifts_number_triggers(
                source=ej_train,
                target=keno_train,
                lag_days=int(lag),
                min_support=int(min_support),
                max_results=max_results,
                alpha_fdr=float(alpha),
                filter_by_alpha=filter_by_alpha,
            )
        )
        candidates.extend(
            conditional_lifts_ordered_value_triggers(
                source=ew_train,
                target=keno_train,
                lag_days=int(lag),
                position_labels=[f"T{i}" for i in range(1, 14)],
                min_support=int(min_support_pos),
                max_results=max_results,
                alpha_fdr=float(alpha),
                filter_by_alpha=filter_by_alpha,
            )
        )
        candidates.extend(
            conditional_lifts_ordered_value_triggers(
                source=gs_train,
                target=keno_train,
                lag_days=int(lag),
                position_labels=["Kl1", "Kl2", "Kl3", "Kl4", "Kl5", "Kl6_1", "Kl6_2", "Kl7"],
                min_support=int(min_support_pos),
                max_results=max_results,
                alpha_fdr=float(alpha),
                filter_by_alpha=filter_by_alpha,
            )
        )

    rules = [
        CrossGameRule(
            source=str(r.source),
            target=str(r.target),
            lag_days=int(r.lag_days),
            trigger_kind=str(r.trigger_kind),
            trigger=str(r.trigger),
            target_number=int(r.target_number),
            support=int(r.support),
            base_rate=float(r.base_rate),
            conditional_rate=float(r.conditional_rate),
            lift=float(r.lift),
            p_value=float(r.p_value),
            q_value=float(r.q_value),
        )
        for r in candidates
        if str(r.target) == "KENO"
    ]
    if only_exclusion:
        rules = [r for r in rules if float(r.lift) < 1.0]
    rules.sort(key=lambda x: (x.q_value, abs(x.lift - 1.0), x.source, x.lag_days, x.trigger, x.target_number))
    if selection == "top_n":
        rules = rules[: int(top_n)]
    return rules


def _fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def main() -> int:
    args = parse_args()

    train_end = date.fromisoformat(str(args.train_end))
    lags = sorted(set(int(x) for x in args.lags if int(x) >= 0))

    keno = _load_keno(args.keno)
    lotto = _load_lotto(args.lotto)
    aw = _load_auswahlwette(args.auswahlwette)
    ej = _load_eurojackpot(args.eurojackpot)
    ew = _load_eurowette(args.eurowette)
    gs = _load_gluecksspirale(args.gluecksspirale)

    keno_train = _slice_end(keno, end_date=train_end)
    lotto_train = _slice_end(lotto, end_date=train_end)
    aw_train = _slice_end(aw, end_date=train_end)
    ej_train = _slice_end(ej, end_date=train_end)
    ew_train = _slice_end(ew, end_date=train_end)
    gs_train = _slice_end(gs, end_date=train_end)

    rules_train = _mine_rules_train(
        keno_train=keno_train,
        lotto_train=lotto_train,
        aw_train=aw_train,
        ej_train=ej_train,
        ew_train=ew_train,
        gs_train=gs_train,
        lags=lags,
        alpha=float(args.alpha),
        min_support=int(args.min_support),
        min_support_pos=int(args.min_support_pos),
        selection=str(args.selection),
        top_n=int(args.top_n),
        only_exclusion=bool(args.only_exclusion),
    )

    test_start_idx = _first_index_after(keno.dates, train_end)
    if test_start_idx is None:
        raise ValueError("No test period: train_end is after last KENO date")

    sources_full = {
        "LOTTO": lotto,
        "AUSWAHLWETTE": aw,
        "EUROJACKPOT": ej,
        "EUROWETTE": ew,
        "GLUECKSSPIRALE": gs,
    }
    ordered_maps = {
        "EUROWETTE": {f"T{i}": i - 1 for i in range(1, 14)},
        "GLUECKSSPIRALE": {
            "Kl1": 0,
            "Kl2": 1,
            "Kl3": 2,
            "Kl4": 3,
            "Kl5": 4,
            "Kl6_1": 5,
            "Kl6_2": 6,
            "Kl7": 7,
        },
    }

    backtest = backtest_cross_game_rule_layer(
        keno,
        sources=sources_full,
        rules=rules_train,
        keno_types=args.types,
        start_index=int(test_start_idx),
        recent_draws=int(args.recent_draws),
        recent_weight=float(args.recent_weight),
        hard_exclude=not args.no_hard_exclude,
        include_multiplier=float(args.include_multiplier),
        max_exclusions_per_draw=args.max_exclusions_per_draw,
        max_inclusions_per_draw=args.max_inclusions_per_draw,
        ordered_value_position_maps=ordered_maps,
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "analysis": "cross_game_rule_layer_train_test_backtest",
        "generated_at": datetime.now().isoformat(),
        "split": {
            "train_end": str(train_end),
            "test_start": str(keno.dates[test_start_idx]),
            "test_end": str(keno.dates[-1]),
            "train_counts": {
                "KENO": len(keno_train.dates),
                "LOTTO": len(lotto_train.dates),
                "AUSWAHLWETTE": len(aw_train.dates),
                "EUROJACKPOT": len(ej_train.dates),
                "EUROWETTE": len(ew_train.dates),
                "GLUECKSSPIRALE": len(gs_train.dates),
            },
            "test_counts": {
                "KENO_predictions": int(backtest.by_type[f"typ_{int(args.types[0])}"]["n_predictions"])
                if args.types
                else 0
            },
        },
        "mining": {
            "selection": str(args.selection),
            "alpha_fdr": float(args.alpha),
            "lags": lags,
            "min_support": int(args.min_support),
            "min_support_pos": int(args.min_support_pos),
            "top_n": int(args.top_n),
            "only_exclusion": bool(args.only_exclusion),
            "rules_mined": len(rules_train),
            "rules": [asdict(r) for r in rules_train],
        },
        "backtest": asdict(backtest),
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    ex = backtest.rule_accuracy["exclusion"]
    inc = backtest.rule_accuracy["inclusion"]

    print("=" * 100)
    print("Train/Test Backtest: Cross-Game Rule Layer (target: KENO)")
    print(f"Train end: {train_end}  Test: {keno.dates[test_start_idx]}..{keno.dates[-1]}")
    if str(args.selection) == "significant":
        sel = f"q<={args.alpha}"
    else:
        sel = f"top_n={int(args.top_n)} by q (alpha used only for q-values)"
    print(f"Mined rules (Train, selection={args.selection} {sel}): {len(rules_train)}  Output: {args.output}")
    print("=" * 100)
    print(
        f"Rule accuracy (Test): exclusion={_fmt_pct(ex['accuracy'])} (trials={ex['trials']}, baseline={_fmt_pct(ex['baseline'])}, lift={_fmt_pct(ex['lift'])})"
    )
    print(
        f"                    inclusion={_fmt_pct(inc['accuracy'])} (trials={inc['trials']}, baseline={_fmt_pct(inc['baseline'])}, lift={_fmt_pct(inc['lift'])})"
    )
    print()
    for k in backtest.config["keno_types"]:
        s = backtest.by_type[f"typ_{k}"]
        print(
            f"Type {k}: mean_hits baseline={s['mean_hits_baseline']:.4f} with_rules={s['mean_hits_with_rules']:.4f} delta={s['delta_mean_hits']:+.4f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
