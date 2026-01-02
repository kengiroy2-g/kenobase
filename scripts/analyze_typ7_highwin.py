#!/usr/bin/env python3
"""Typ-7 High-Win Forensik: Detailanalyse aller Typ-7 7/7 Treffer (1.000 EUR).

Dedicated analysis for Keno Typ-7 high-win events (7/7 hits = 1.000 EUR payout).
Filters and enriches events from existing forensik data.

Features:
- Weekday distribution for Typ-7 events only
- Birthday-ratio analysis (numbers 1-31 vs 32-70)
- Preceding draw pattern analysis
- Comparison with Typ-6 (500 EUR) as baseline

Examples:
  python scripts/analyze_typ7_highwin.py
  python scripts/analyze_typ7_highwin.py --forensik results/high_win_forensik.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Typ7ForensikResult:
    """Typ-7 specific forensik analysis result."""

    typ7_events_total: int
    typ7_unique_dates: int
    weekday_distribution: dict[str, int]
    birthday_ratio_mean: float
    birthday_ratio_events: list[float]
    strategy_distribution: dict[str, int]
    preceding_draw_birthday_ratio_mean: float
    typ6_comparison: dict[str, Any]
    events: list[dict[str, Any]]


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def _filter_typ7_events(forensik_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter only Typ-7 events from forensik data."""
    events = forensik_data.get("events", [])
    return [e for e in events if e.get("keno_type") == 7]


def _filter_typ6_events(forensik_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter only Typ-6 events for baseline comparison."""
    events = forensik_data.get("events", [])
    return [e for e in events if e.get("keno_type") == 6]


def _compute_statistics(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute descriptive statistics for a list of events."""
    if not events:
        return {
            "count": 0,
            "unique_dates": 0,
            "birthday_ratio_mean": None,
            "birthday_ratio_std": None,
            "weekday_distribution": {},
            "strategy_distribution": {},
            "preceding_birthday_ratio_mean": None,
        }

    dates = list(set(e["date"] for e in events))
    br_values = [e["birthday_ratio"] for e in events if "birthday_ratio" in e]
    weekdays = [e["weekday"] for e in events if "weekday" in e]
    strategies = [e["strategy"] for e in events if "strategy" in e]

    # Preceding draw birthday ratios
    prec_br_values = []
    for e in events:
        if "preceding_draw" in e and e["preceding_draw"]:
            prec_br = e["preceding_draw"].get("birthday_ratio")
            if prec_br is not None:
                prec_br_values.append(prec_br)

    br_mean = sum(br_values) / len(br_values) if br_values else None
    br_std = None
    if br_values and len(br_values) > 1 and br_mean is not None:
        br_std = (sum((v - br_mean) ** 2 for v in br_values) / len(br_values)) ** 0.5

    prec_br_mean = sum(prec_br_values) / len(prec_br_values) if prec_br_values else None

    return {
        "count": len(events),
        "unique_dates": len(dates),
        "birthday_ratio_mean": br_mean,
        "birthday_ratio_std": br_std,
        "birthday_ratio_values": br_values,
        "weekday_distribution": dict(Counter(weekdays)),
        "strategy_distribution": dict(Counter(strategies)),
        "preceding_birthday_ratio_mean": prec_br_mean,
    }


def run_typ7_forensik(forensik_path: Path) -> Typ7ForensikResult:
    """Run Typ-7 specific forensik analysis."""
    forensik_data = _load_json(forensik_path)

    typ7_events = _filter_typ7_events(forensik_data)
    typ6_events = _filter_typ6_events(forensik_data)

    typ7_stats = _compute_statistics(typ7_events)
    typ6_stats = _compute_statistics(typ6_events)

    # Compute deltas for comparison
    delta_birthday_ratio = None
    if typ7_stats["birthday_ratio_mean"] is not None and typ6_stats["birthday_ratio_mean"] is not None:
        delta_birthday_ratio = typ7_stats["birthday_ratio_mean"] - typ6_stats["birthday_ratio_mean"]

    delta_preceding_birthday_ratio = None
    if (
        typ7_stats["preceding_birthday_ratio_mean"] is not None
        and typ6_stats["preceding_birthday_ratio_mean"] is not None
    ):
        delta_preceding_birthday_ratio = (
            typ7_stats["preceding_birthday_ratio_mean"] - typ6_stats["preceding_birthday_ratio_mean"]
        )

    typ6_comparison = {
        "typ6_count": typ6_stats["count"],
        "typ6_birthday_ratio_mean": typ6_stats["birthday_ratio_mean"],
        "typ6_preceding_birthday_ratio_mean": typ6_stats["preceding_birthday_ratio_mean"],
        "typ6_weekday_distribution": typ6_stats["weekday_distribution"],
        "delta_birthday_ratio": delta_birthday_ratio,
        "delta_preceding_birthday_ratio": delta_preceding_birthday_ratio,
    }

    return Typ7ForensikResult(
        typ7_events_total=typ7_stats["count"],
        typ7_unique_dates=typ7_stats["unique_dates"],
        weekday_distribution=typ7_stats["weekday_distribution"],
        birthday_ratio_mean=typ7_stats["birthday_ratio_mean"] or 0.0,
        birthday_ratio_events=typ7_stats.get("birthday_ratio_values", []),
        strategy_distribution=typ7_stats["strategy_distribution"],
        preceding_draw_birthday_ratio_mean=typ7_stats["preceding_birthday_ratio_mean"] or 0.0,
        typ6_comparison=typ6_comparison,
        events=typ7_events,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Typ-7 High-Win Forensik Analysis (1.000 EUR)")
    parser.add_argument(
        "--forensik",
        type=str,
        default="results/high_win_forensik.json",
        help="Input forensik JSON (default: results/high_win_forensik.json)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/typ7_highwin_forensik.json",
        help="Output JSON (default: results/typ7_highwin_forensik.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    forensik_path = Path(args.forensik)
    if not forensik_path.exists():
        print(f"ERROR: Forensik file not found: {forensik_path}")
        return 1

    print("=" * 80)
    print("TYP-7 HIGH-WIN FORENSIK ANALYSIS (1.000 EUR)")
    print("=" * 80)
    print(f"Input: {args.forensik}")
    print()

    result = run_typ7_forensik(forensik_path)

    # Summary
    print(f"Typ-7 High-Win Events: {result.typ7_events_total}")
    print(f"Unique Dates: {result.typ7_unique_dates}")
    print()

    print("CAVEAT: N={} is very small for statistical conclusions!".format(result.typ7_events_total))
    print()

    print("Weekday Distribution (Typ-7):")
    if result.weekday_distribution:
        for day, count in sorted(result.weekday_distribution.items(), key=lambda x: -x[1]):
            print(f"  {day}: {count}")
    else:
        print("  (no data)")
    print()

    print(f"Birthday Ratio (mean): {result.birthday_ratio_mean:.3f}")
    print(f"  (0.443 = expected for uniform 20/70)")
    if result.birthday_ratio_events:
        print(f"  Individual values: {result.birthday_ratio_events}")
    print()

    print(f"Preceding Draw Birthday Ratio (mean): {result.preceding_draw_birthday_ratio_mean:.3f}")
    print()

    print("Strategy Distribution (Typ-7):")
    if result.strategy_distribution:
        for strat, count in sorted(result.strategy_distribution.items(), key=lambda x: -x[1]):
            print(f"  {strat}: {count}")
    else:
        print("  (no data)")
    print()

    print("=" * 80)
    print("COMPARISON WITH TYP-6 (500 EUR) AS BASELINE")
    print("=" * 80)
    c = result.typ6_comparison
    print(f"  Typ-6 Events: {c['typ6_count']}")
    print(f"  Typ-6 Birthday Ratio (mean): {c['typ6_birthday_ratio_mean']:.3f}" if c["typ6_birthday_ratio_mean"] else "  Typ-6 Birthday Ratio: n/a")
    print(f"  Typ-6 Preceding Birthday Ratio (mean): {c['typ6_preceding_birthday_ratio_mean']:.3f}" if c["typ6_preceding_birthday_ratio_mean"] else "  Typ-6 Preceding Birthday Ratio: n/a")
    print()

    if c["delta_birthday_ratio"] is not None:
        print(f"  Delta Birthday Ratio (Typ7 - Typ6): {c['delta_birthday_ratio']:+.3f}")
    if c["delta_preceding_birthday_ratio"] is not None:
        print(f"  Delta Preceding Birthday Ratio (Typ7 - Typ6): {c['delta_preceding_birthday_ratio']:+.3f}")
    print()

    print("  Typ-6 Weekday Distribution:")
    if c["typ6_weekday_distribution"]:
        for day, count in sorted(c["typ6_weekday_distribution"].items(), key=lambda x: -x[1]):
            print(f"    {day}: {count}")
    print()

    # Event details
    print("=" * 80)
    print("TYP-7 EVENT DETAILS")
    print("=" * 80)
    for i, e in enumerate(result.events, 1):
        print(f"\n[Event {i}] Date: {e['date']}, Weekday: {e['weekday']}")
        print(f"  Ticket: {e['ticket_numbers']}")
        print(f"  Hits: {e['hits']}, Payout: {e['payout']} EUR")
        print(f"  Strategy: {e['strategy']}")
        print(f"  Draw Birthday Ratio: {e['birthday_ratio']:.2f}")
        if e.get("preceding_draw"):
            prec = e["preceding_draw"]
            print(f"  Preceding Draw ({prec['date']}): Birthday Ratio = {prec['birthday_ratio']:.2f}")

    print()

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "analysis": "typ7_highwin_forensik",
        "generated_at": datetime.now().isoformat(),
        "forensik_source": str(args.forensik),
        "typ7_events_total": result.typ7_events_total,
        "typ7_unique_dates": result.typ7_unique_dates,
        "caveat": f"N={result.typ7_events_total} is very small for statistical conclusions",
        "weekday_distribution": result.weekday_distribution,
        "birthday_ratio_mean": result.birthday_ratio_mean,
        "birthday_ratio_events": result.birthday_ratio_events,
        "strategy_distribution": result.strategy_distribution,
        "preceding_draw_birthday_ratio_mean": result.preceding_draw_birthday_ratio_mean,
        "typ6_comparison": result.typ6_comparison,
        "events": result.events,
    }

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON written: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
