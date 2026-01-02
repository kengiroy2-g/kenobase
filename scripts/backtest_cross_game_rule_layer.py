#!/usr/bin/env python3
"""Walk-forward backtest: cross-game trigger rules -> KENO.

This script takes the *significant* rules from a previously generated
`results/cross_lottery_coupling.json` and evaluates them as a filter/boost layer
on top of a baseline KENO ranking model (weighted frequency).

Example:
  python scripts/backtest_cross_game_rule_layer.py
  python scripts/backtest_cross_game_rule_layer.py --alpha 0.05 --start-index 365
  python scripts/backtest_cross_game_rule_layer.py --output results/cross_game_rule_layer_backtest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.prediction.cross_game_rule_backtester import CrossGameRule, backtest_cross_game_rule_layer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest cross-game rule layer for KENO")
    parser.add_argument(
        "--rules-json",
        type=str,
        default="results/cross_lottery_coupling.json",
        help="Cross-lottery coupling JSON (default: results/cross_lottery_coupling.json)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR threshold used to select significant rules (default: 0.05)",
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
        "--start-index",
        type=int,
        default=365,
        help="Ab welcher Ziehung mit Vorhersagen starten (default: 365)",
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
        default="results/cross_game_rule_layer_backtest.json",
        help="Output JSON (default: results/cross_game_rule_layer_backtest.json)",
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


def _load_significant_rules(path: str, *, alpha: float) -> list[CrossGameRule]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    sig = raw.get("conditional_lifts", {}).get("significant", {})

    rules: list[CrossGameRule] = []
    for bucket in ("number_triggers", "ordered_value_triggers"):
        for r in sig.get(bucket, []):
            if str(r.get("target")) != "KENO":
                continue
            if float(r.get("q_value", 1.0)) > float(alpha):
                continue
            rules.append(
                CrossGameRule(
                    source=str(r["source"]),
                    target=str(r["target"]),
                    lag_days=int(r["lag_days"]),
                    trigger_kind=str(r["trigger_kind"]),
                    trigger=str(r["trigger"]),
                    target_number=int(r["target_number"]),
                    support=int(r.get("support", 0)),
                    base_rate=float(r.get("base_rate", 0.0)),
                    conditional_rate=float(r.get("conditional_rate", 0.0)),
                    lift=float(r.get("lift", 0.0)),
                    p_value=float(r.get("p_value", 1.0)),
                    q_value=float(r.get("q_value", 1.0)),
                )
            )

    # Stable order for reporting.
    rules.sort(key=lambda x: (x.q_value, abs(x.lift - 1.0), x.source, x.lag_days, x.trigger, x.target_number))
    return rules


def _fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def main() -> int:
    args = parse_args()

    rules = _load_significant_rules(args.rules_json, alpha=float(args.alpha))

    keno = _load_keno(args.keno)
    sources = {
        "LOTTO": _load_lotto(args.lotto),
        "AUSWAHLWETTE": _load_auswahlwette(args.auswahlwette),
        "GLUECKSSPIRALE": _load_gluecksspirale(args.gluecksspirale),
        "EUROWETTE": _load_eurowette(args.eurowette),
        "EUROJACKPOT": _load_eurojackpot(args.eurojackpot),
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

    payload = backtest_cross_game_rule_layer(
        keno,
        sources=sources,
        rules=rules,
        keno_types=args.types,
        start_index=args.start_index,
        recent_draws=args.recent_draws,
        recent_weight=args.recent_weight,
        hard_exclude=not args.no_hard_exclude,
        include_multiplier=args.include_multiplier,
        max_exclusions_per_draw=args.max_exclusions_per_draw,
        max_inclusions_per_draw=args.max_inclusions_per_draw,
        ordered_value_position_maps=ordered_maps,
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(payload), indent=2, ensure_ascii=False), encoding="utf-8")

    ex = payload.rule_accuracy["exclusion"]
    inc = payload.rule_accuracy["inclusion"]

    print("=" * 100)
    print("Cross-Game Rule Layer Backtest (target: KENO)")
    print(f"Rules (q<={args.alpha}): {payload.rules['count']}  Output: {args.output}")
    print(
        f"KENO draws={payload.draws['keno_count']} ({payload.draws['keno_start']}..{payload.draws['keno_end']})"
    )
    print(f"start_index={payload.config['start_index']} recent={payload.config['recent_draws']} w={payload.config['recent_weight']}")
    print(
        f"Rule accuracy: exclusion={_fmt_pct(ex['accuracy'])} (trials={ex['trials']}, baseline={_fmt_pct(ex['baseline'])}, lift={_fmt_pct(ex['lift'])})"
    )
    print(
        f"              inclusion={_fmt_pct(inc['accuracy'])} (trials={inc['trials']}, baseline={_fmt_pct(inc['baseline'])}, lift={_fmt_pct(inc['lift'])})"
    )
    print("=" * 100)
    print()

    for k in payload.config["keno_types"]:
        s = payload.by_type[f"typ_{k}"]
        print(
            f"Type {k}: mean_hits baseline={s['mean_hits_baseline']:.4f} with_rules={s['mean_hits_with_rules']:.4f} delta={s['delta_mean_hits']:+.4f}"
        )
    print()

    # Show the most-fired rules.
    by_rule = payload.rules.get("by_rule", {})
    if by_rule:
        top = sorted(by_rule.items(), key=lambda kv: (-int(kv[1]["trials"]), -float(kv[1]["accuracy"])))[:10]
        print("Top fired rules (by trials):")
        for rule_id, stats in top:
            print(f"  {rule_id}  trials={stats['trials']}  acc={_fmt_pct(stats['accuracy'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
