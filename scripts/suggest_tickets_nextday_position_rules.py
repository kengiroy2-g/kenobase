#!/usr/bin/env python3
"""Suggest next-day KENO tickets using a position-based exclusion/inclusion rule layer.

This is the practical "daily use" companion to `backtest_position_rule_layer.py`:
it trains rules on the past (rolling window) and applies them to the latest draw
to produce suggestions for tomorrow.

Examples:
  python scripts/suggest_tickets_nextday_position_rules.py
  python scripts/suggest_tickets_nextday_position_rules.py --types 6 7 8 9 10
  python scripts/suggest_tickets_nextday_position_rules.py --today-ordered "29,51,...,11"
  python scripts/suggest_tickets_nextday_position_rules.py --output results/nextday_suggestions.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DataLoader
from kenobase.prediction.position_rule_layer import (
    RollingPositionRuleMiner,
    apply_rule_layer_to_scores,
    extract_ordered_keno_numbers,
)
from kenobase.prediction.ticket_suggester import rank_numbers_weighted_frequency


@dataclass(frozen=True)
class NextDaySuggestion:
    keno_type: int
    ticket: list[int]


@dataclass(frozen=True)
class NextDaySuggestionPayload:
    analysis: str
    generated_at: str
    trained_until_date: str
    for_date: str
    config: dict
    today_ordered: list[int]
    exclusions: list[int]
    inclusions: list[int]
    top_ranked: list[int]
    suggestions: list[NextDaySuggestion]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest next-day tickets with a position-rule exclusion/inclusion layer"
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
        "--today-ordered",
        type=str,
        default=None,
        help=(
            "Optional: 20 Zahlen als Komma-Liste in Ziehungsreihenfolge (pos 1..20), "
            'z.B. --today-ordered "29,51,28,...,11"'
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: JSON Output-Pfad, z.B. results/nextday_suggestions.json",
    )
    return parser.parse_args()


def _parse_today_ordered(arg: Optional[str]) -> Optional[list[int]]:
    if not arg:
        return None
    parts = [p.strip() for p in arg.split(",") if p.strip()]
    nums = [int(p) for p in parts]
    if len(nums) != 20:
        raise ValueError(f"--today-ordered must contain exactly 20 numbers, got {len(nums)}")
    if len(set(nums)) != 20:
        raise ValueError("--today-ordered must contain 20 unique numbers")
    if any(n < 1 or n > 70 for n in nums):
        raise ValueError("--today-ordered numbers must be in 1..70")
    return nums


def _fmt_pct(x: float) -> str:
    return f"{x*100:.4f}%"


def _uniform_near_or_jackpot(k: int) -> float:
    probs = KENO_PROBABILITIES.get(int(k))
    if not probs:
        return 0.0
    return float(probs.get(k - 1, 0.0) + probs.get(k, 0.0))


def main() -> int:
    args = parse_args()

    loader = DataLoader()
    draws = loader.load(args.draws)
    draws = sorted(draws, key=lambda d: d.date)
    if len(draws) < 2:
        raise SystemExit("Need at least 2 draws in CSV for training")

    ordered = [extract_ordered_keno_numbers(d) for d in draws]
    today_ordered = _parse_today_ordered(args.today_ordered) or ordered[-1]

    # Baseline ranking scores (marginal presence estimate)
    ranked = rank_numbers_weighted_frequency(
        draws,
        recent_draws=args.recent_draws,
        recent_weight=args.recent_weight,
    )
    base_scores = np.zeros(71, dtype=float)
    for r in ranked:
        base_scores[int(r.number)] = float(r.score)

    # Train rolling transition rules up to (yesterday -> today).
    miner = RollingPositionRuleMiner(window_size=args.rule_window)
    start = max(0, (len(draws) - 1) - int(args.rule_window))
    for i in range(start, len(draws) - 1):
        miner.add_transition(today_ordered=ordered[i], tomorrow_numbers=draws[i + 1].numbers)

    exclusions, inclusions = miner.fire_rules_for_ordered_draw(
        today_ordered,
        exclude_max=args.exclude_max,
        include_max=args.include_max,
        min_support=args.rule_min_support,
        exclude_lb=args.exclude_lb,
        include_lb=args.include_lb,
    )
    adjusted_scores, excluded_set, included_set = apply_rule_layer_to_scores(
        base_scores,
        exclusions=exclusions,
        inclusions=inclusions,
        hard_exclude=not args.no_hard_exclude,
        hard_exclude_lb=args.hard_exclude_lb,
        exclude_weight=args.exclude_weight,
        include_weight=args.include_weight,
    )

    ranked_numbers = sorted(range(1, 71), key=lambda n: (-float(adjusted_scores[n]), int(n)))
    suggestions = [
        NextDaySuggestion(keno_type=int(k), ticket=sorted(ranked_numbers[: int(k)]))
        for k in sorted(set(args.types))
    ]

    today_date = draws[-1].date.date()
    for_date = today_date + timedelta(days=1)

    print("=" * 90)
    print("KENO Next-Day Suggestions: weighted_frequency + position_rules")
    print(f"Trained until: {today_date}  ->  For: {for_date}")
    print(
        f"Config: recent_draws={args.recent_draws} recent_weight={args.recent_weight} "
        f"rule_window={args.rule_window} min_support={args.rule_min_support} "
        f"exclude_lb={args.exclude_lb} include_lb={args.include_lb}"
    )
    print("=" * 90)
    print(f"Today ordered: {today_ordered}")
    print()

    print(
        f"Rules fired: exclusions={len(exclusions)} (unique={len(excluded_set)})  "
        f"inclusions={len(inclusions)} (unique={len(included_set)})"
    )
    print(f"Triggered exclusions (unique): {sorted(excluded_set) if excluded_set else 'none'}")
    print(f"Triggered inclusions (unique): {sorted(included_set) if included_set else 'none'}")
    print()

    for s in suggestions:
        p = _uniform_near_or_jackpot(s.keno_type)
        print(
            f"Type {s.keno_type}: {', '.join(map(str, s.ticket))}  "
            f"(uniform P(near|jack)={_fmt_pct(p)})"
        )

    payload = NextDaySuggestionPayload(
        analysis="nextday_suggestions_position_rule_layer",
        generated_at=datetime.now().isoformat(),
        trained_until_date=str(today_date),
        for_date=str(for_date),
        config={
            "types": [int(k) for k in sorted(set(args.types))],
            "recent_draws": int(args.recent_draws),
            "recent_weight": float(args.recent_weight),
            "rule_window": int(args.rule_window),
            "rule_min_support": int(args.rule_min_support),
            "exclude_max": int(args.exclude_max),
            "include_max": int(args.include_max),
            "exclude_lb": float(args.exclude_lb),
            "include_lb": float(args.include_lb),
            "hard_exclude": bool(not args.no_hard_exclude),
            "hard_exclude_lb": float(args.hard_exclude_lb),
            "exclude_weight": float(args.exclude_weight),
            "include_weight": float(args.include_weight),
        },
        today_ordered=[int(x) for x in today_ordered],
        exclusions=[int(x) for x in sorted(excluded_set)],
        inclusions=[int(x) for x in sorted(included_set)],
        top_ranked=[int(x) for x in ranked_numbers[:20]],
        suggestions=suggestions,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(payload), indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"JSON geschrieben: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
