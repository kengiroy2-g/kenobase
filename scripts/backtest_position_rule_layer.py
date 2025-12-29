#!/usr/bin/env python3
"""Walk-forward next-day backtest for the position rule layer (exclusion/inclusion).

Examples:
  python scripts/backtest_position_rule_layer.py
  python scripts/backtest_position_rule_layer.py --types 6 7 8 9 10 --start-index 365
  python scripts/backtest_position_rule_layer.py --rule-window 365 --rule-min-support 15
  python scripts/backtest_position_rule_layer.py --output results/position_rule_layer_backtest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.data_loader import DataLoader
from kenobase.prediction.position_rule_backtester import backtest_position_rule_layer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest next-day ticket ranking with a position-based rule layer"
    )
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
        "--rule-window",
        type=int,
        default=365,
        help="Rolling-Fenster (Transitions) fuer Regeln (default: 365)",
    )
    parser.add_argument(
        "--rule-min-support",
        type=int,
        default=10,
        help="Minimum Support pro Trigger (default: 10)",
    )
    parser.add_argument(
        "--exclude-max",
        type=int,
        default=3,
        help="Max. Exclusion-Kandidaten pro Trigger (default: 3)",
    )
    parser.add_argument(
        "--include-max",
        type=int,
        default=5,
        help="Max. Inclusion-Kandidaten pro Trigger (default: 5)",
    )
    parser.add_argument(
        "--exclude-lb",
        type=float,
        default=0.90,
        help="Wilson-LB Threshold fuer P(absent|trigger) (default: 0.90)",
    )
    parser.add_argument(
        "--include-lb",
        type=float,
        default=0.40,
        help="Wilson-LB Threshold fuer P(present|trigger) (default: 0.40)",
    )
    parser.add_argument(
        "--no-hard-exclude",
        action="store_true",
        help="Deaktiviert Hard-Exclude (sonst sehr hohe Exclusions werden komplett entfernt)",
    )
    parser.add_argument(
        "--hard-exclude-lb",
        type=float,
        default=0.95,
        help="Threshold fuer Hard-Exclude (default: 0.95)",
    )
    parser.add_argument(
        "--exclude-weight",
        type=float,
        default=2.0,
        help="Staerke der Exclusion-Anpassung (log-space) (default: 2.0)",
    )
    parser.add_argument(
        "--include-weight",
        type=float,
        default=1.0,
        help="Staerke der Inclusion-Anpassung (log-space) (default: 1.0)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: JSON Output-Pfad, z.B. results/position_rule_layer_backtest.json",
    )
    return parser.parse_args()


def _fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def main() -> int:
    args = parse_args()

    loader = DataLoader()
    draws = loader.load(args.draws)
    draws = sorted(draws, key=lambda d: d.date)

    payload = backtest_position_rule_layer(
        draws,
        keno_types=args.types,
        start_index=args.start_index,
        recent_draws=args.recent_draws,
        recent_weight=args.recent_weight,
        rule_window=args.rule_window,
        rule_min_support=args.rule_min_support,
        exclude_max=args.exclude_max,
        include_max=args.include_max,
        exclude_lb=args.exclude_lb,
        include_lb=args.include_lb,
        hard_exclude=not args.no_hard_exclude,
        hard_exclude_lb=args.hard_exclude_lb,
        exclude_weight=args.exclude_weight,
        include_weight=args.include_weight,
    )

    ex = payload.rule_accuracy["exclusion"]
    inc = payload.rule_accuracy["inclusion"]

    print("=" * 100)
    print("KENO Next-Day Backtest: weighted_frequency + position_rules")
    print(
        f"Draws: {payload.draws['count']} from {payload.draws['start_date']} to {payload.draws['end_date']}"
    )
    first_k = int(payload.config["keno_types"][0]) if payload.config.get("keno_types") else None
    n_predictions = (
        int(payload.by_type[f"typ_{first_k}"]["baseline"]["n_predictions"]) if first_k is not None else 0
    )
    print(
        f"Predictions start_index={payload.config['start_index']} -> n={n_predictions}"
    )
    if int(ex.get("trials", 0)) == 0:
        excl_str = "exclusion=no rules fired"
    else:
        excl_str = (
            f"exclusion={_fmt_pct(ex['accuracy'])} "
            f"(trials={ex['trials']}, baseline={_fmt_pct(ex['baseline'])}, lift={_fmt_pct(ex['lift'])})"
        )

    if int(inc.get("trials", 0)) == 0:
        incl_str = "inclusion=no rules fired"
    else:
        incl_str = (
            f"inclusion={_fmt_pct(inc['accuracy'])} "
            f"(trials={inc['trials']}, baseline={_fmt_pct(inc['baseline'])}, lift={_fmt_pct(inc['lift'])})"
        )

    print(f"Rule accuracy (next day): {excl_str}; {incl_str}")
    print("=" * 100)
    print()

    for k in payload.config["keno_types"]:
        key = f"typ_{k}"
        base = payload.by_type[key]["baseline"]
        rules = payload.by_type[key]["with_rules"]
        delta = payload.by_type[key]["delta"]

        print(f"Type {k}:")
        print(
            f"  mean_hits: baseline={base['mean_hits']:.4f}  with_rules={rules['mean_hits']:.4f}  "
            f"delta={delta['mean_hits']:+.4f}"
        )
        print(
            f"  near_miss_count: baseline={base['near_miss_count']}  with_rules={rules['near_miss_count']}  "
            f"delta={delta['near_miss_count']:+d}"
        )
        print(
            f"  jackpot_count:   baseline={base['jackpot_count']}  with_rules={rules['jackpot_count']}  "
            f"delta={delta['jackpot_count']:+d}"
        )
        print(f"  last_ticket(with_rules): {', '.join(map(str, rules['last_ticket']))}")
        print()

    top = payload.top_rules
    top_ex = top.get("top_exclusion", [])
    top_in = top.get("top_inclusion", [])
    if top_ex:
        print(f"Top exclusion rules (min_trials={top.get('min_trials')}):")
        for r in top_ex[:10]:
            print(
                f"  Trigger {r['trigger_number']}@{r['trigger_position']} -> {r['predicted_numbers']}  "
                f"acc={_fmt_pct(r['accuracy'])}  trials={r['trials']}"
            )
        print()
    if top_in:
        print(f"Top inclusion rules (min_trials={top.get('min_trials')}):")
        for r in top_in[:10]:
            print(
                f"  Trigger {r['trigger_number']}@{r['trigger_position']} -> {r['predicted_numbers']}  "
                f"acc={_fmt_pct(r['accuracy'])}  trials={r['trials']}"
            )
        print()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(payload), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON geschrieben: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
