#!/usr/bin/env python3
"""Suggest KENO tickets for types 6-9 based on a simple frequency model.

Examples:
  python scripts/suggest_tickets.py
  python scripts/suggest_tickets.py --types 6 7 8 9 --recent-draws 365 --recent-weight 0.6
  python scripts/suggest_tickets.py --output results/ticket_suggestions.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.data_loader import DataLoader
from kenobase.prediction.ticket_suggester import save_suggestions_json, suggest_tickets_from_draws


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Suggest KENO tickets (types 6-9)")
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
        default=[6, 7, 8, 9],
        help="Keno-Typen (Anzahl Zahlen), z.B. --types 6 7 8 9 (default: 6 7 8 9)",
    )
    parser.add_argument(
        "--recent-draws",
        type=int,
        default=365,
        help="Anzahl letzter Ziehungen fuer Recent-Frequenz (default: 365, 0 = aus)",
    )
    parser.add_argument(
        "--recent-weight",
        type=float,
        default=0.6,
        help="Gewicht fuer Recent-Frequenz (default: 0.6)",
    )
    parser.add_argument(
        "--with-heuristic-probabilities",
        action="store_true",
        help="Zeigt zusaetzlich heuristische Modell-Wahrscheinlichkeiten (Independence/Poisson-binomial).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: JSON Output-Pfad, z.B. results/ticket_suggestions.json",
    )
    return parser.parse_args()


def _fmt_pct(x: float) -> str:
    return f"{x*100:.6f}%"


def main() -> int:
    args = parse_args()

    loader = DataLoader()
    draws = loader.load(args.draws)
    draws = sorted(draws, key=lambda d: d.date)

    suggestions = suggest_tickets_from_draws(
        draws,
        keno_types=args.types,
        recent_draws=args.recent_draws,
        recent_weight=args.recent_weight,
        with_model_probabilities=args.with_heuristic_probabilities,
    )

    print("=" * 80)
    print("KENO Ticket Suggestions (frequency model)")
    print(f"Draws: {len(draws)} from {draws[0].date.date()} to {draws[-1].date.date()}")
    print(f"Model: weighted_frequency(recent_draws={args.recent_draws}, recent_weight={args.recent_weight})")
    print("=" * 80)
    print()

    for s in suggestions:
        print(f"Type {s.keno_type}: {', '.join(map(str, s.numbers))}")
        u = s.probabilities_uniform
        print(
            f"  Uniform: near-miss={_fmt_pct(u.near_miss)}  jackpot={_fmt_pct(u.jackpot)}  "
            f"(near|jack)={_fmt_pct(u.near_or_jackpot)}"
        )
        if s.probabilities_model is not None:
            m = s.probabilities_model
            print(
                f"  Heuristic*: near-miss={_fmt_pct(m.near_miss)}  jackpot={_fmt_pct(m.jackpot)}  "
                f"(near|jack)={_fmt_pct(m.near_or_jackpot)}"
            )
        print()

    if args.output:
        save_suggestions_json(suggestions, output_path=args.output, draws_path=args.draws)
        print(f"JSON geschrieben: {args.output}")

    if args.with_heuristic_probabilities:
        print("*Heuristic-Werte sind Approximationen (Independence/Poisson-binomial).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
