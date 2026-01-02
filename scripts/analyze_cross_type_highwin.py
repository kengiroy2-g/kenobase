#!/usr/bin/env python3
"""Cross-Type High-Win Comparison: Unified analysis across Keno Typ-6 through Typ-10.

Aggregates existing forensik data from multiple sources into a single
comparison report. This is a descriptive analysis - no ROI optimization.

Data Sources:
- results/high_win_forensik.json (Typ-6, Typ-7 events)
- results/typ7_highwin_forensik.json (Typ-7 detailed)
- results/typ8_forensik.json (Typ-8 events)
- results/typ9_highwin_forensik.json (Typ-9 null result)
- results/typ10_highwin_forensik.json (Typ-10 null result)

Examples:
  python scripts/analyze_cross_type_highwin.py
  python scripts/analyze_cross_type_highwin.py --output results/custom_output.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TypeSummary:
    """Summary statistics for a single Keno type."""

    keno_type: int
    events_count: int
    unique_dates: int
    payout_per_hit: float
    birthday_ratio_mean: float | None
    weekday_distribution: dict[str, int]
    strategy_distribution: dict[str, int]
    null_hypothesis: str | None = None
    caveat: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CrossTypeComparison:
    """Cross-type comparison result."""

    types: dict[int, TypeSummary]
    total_events: int
    draws_analyzed: int
    date_range: tuple[str, str]
    interpretation: str


def _load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None if not found."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_typ6_from_forensik(data: dict[str, Any]) -> TypeSummary:
    """Extract Typ-6 summary from high_win_forensik.json."""
    events = [e for e in data.get("events", []) if e.get("keno_type") == 6]

    if not events:
        return TypeSummary(
            keno_type=6,
            events_count=0,
            unique_dates=0,
            payout_per_hit=500.0,
            birthday_ratio_mean=None,
            weekday_distribution={},
            strategy_distribution={},
            null_hypothesis="no_events",
            caveat="No Typ-6 6/6 events in data",
        )

    dates = list(set(e["date"] for e in events))
    br_values = [e["birthday_ratio"] for e in events if "birthday_ratio" in e]
    br_mean = sum(br_values) / len(br_values) if br_values else None

    weekday_dist: dict[str, int] = {}
    strategy_dist: dict[str, int] = {}

    for e in events:
        wd = e.get("weekday")
        if wd:
            weekday_dist[wd] = weekday_dist.get(wd, 0) + 1
        strat = e.get("strategy")
        if strat:
            strategy_dist[strat] = strategy_dist.get(strat, 0) + 1

    return TypeSummary(
        keno_type=6,
        events_count=len(events),
        unique_dates=len(dates),
        payout_per_hit=500.0,
        birthday_ratio_mean=br_mean,
        weekday_distribution=weekday_dist,
        strategy_distribution=strategy_dist,
        caveat=f"N={len(events)} events",
        events=events,
    )


def _extract_typ7_from_forensik(data: dict[str, Any]) -> TypeSummary:
    """Extract Typ-7 summary from typ7_highwin_forensik.json or main forensik."""
    events = data.get("events", [])

    if not events:
        return TypeSummary(
            keno_type=7,
            events_count=0,
            unique_dates=0,
            payout_per_hit=1000.0,
            birthday_ratio_mean=None,
            weekday_distribution={},
            strategy_distribution={},
            null_hypothesis="no_events",
            caveat="No Typ-7 7/7 events in data",
        )

    dates = list(set(e["date"] for e in events))
    br_mean = data.get("birthday_ratio_mean")
    weekday_dist = data.get("weekday_distribution", {})
    strategy_dist = data.get("strategy_distribution", {})

    return TypeSummary(
        keno_type=7,
        events_count=len(events),
        unique_dates=len(dates),
        payout_per_hit=1000.0,
        birthday_ratio_mean=br_mean,
        weekday_distribution=weekday_dist,
        strategy_distribution=strategy_dist,
        caveat=data.get("caveat", f"N={len(events)} events"),
        events=events,
    )


def _extract_typ8_from_forensik(data: dict[str, Any]) -> TypeSummary:
    """Extract Typ-8 summary from typ8_forensik.json."""
    events = data.get("events", [])
    events_8of8 = [e for e in events if e.get("hits") == 8]
    events_7of8 = [e for e in events if e.get("hits") == 7]

    total_events = len(events)
    dates = list(set(e["date"] for e in events))
    br_mean = data.get("birthday_ratio_mean")
    weekday_dist = data.get("weekday_distribution", {})

    # Strategy not tracked in typ8_forensik, derive from events if present
    strategy_dist: dict[str, int] = {}

    # Focus on 8/8 hits for high-win comparison (10.000 EUR)
    n_8of8 = len(events_8of8)
    n_7of8 = len(events_7of8)

    caveat = f"N={total_events} (8/8: {n_8of8}, 7/8: {n_7of8})"

    return TypeSummary(
        keno_type=8,
        events_count=n_8of8,  # Only count 8/8 for consistency with other types
        unique_dates=len(set(e["date"] for e in events_8of8)) if events_8of8 else 0,
        payout_per_hit=10000.0,
        birthday_ratio_mean=br_mean,
        weekday_distribution=weekday_dist,
        strategy_distribution=strategy_dist,
        caveat=caveat,
        events=events_8of8,
    )


def _extract_typ9_null(data: dict[str, Any]) -> TypeSummary:
    """Extract Typ-9 summary from null result file."""
    null_test = data.get("null_hypothesis_test", {})

    return TypeSummary(
        keno_type=9,
        events_count=0,
        unique_dates=0,
        payout_per_hit=50000.0,
        birthday_ratio_mean=None,
        weekday_distribution={},
        strategy_distribution={},
        null_hypothesis=null_test.get("result", "absence_consistent_with_expectation"),
        caveat=data.get("caveat", "Typ-9 high-wins are extremely rare events"),
    )


def _extract_typ10_null(data: dict[str, Any]) -> TypeSummary:
    """Extract Typ-10 summary from null result file."""
    null_test = data.get("null_hypothesis_test", {})

    return TypeSummary(
        keno_type=10,
        events_count=0,
        unique_dates=0,
        payout_per_hit=100000.0,
        birthday_ratio_mean=None,
        weekday_distribution={},
        strategy_distribution={},
        null_hypothesis=null_test.get("result", "absence_consistent_with_expectation"),
        caveat=data.get("caveat", "Typ-10 10/10 hits are extremely rare events"),
    )


def run_cross_type_comparison(
    forensik_path: Path,
    typ7_path: Path,
    typ8_path: Path,
    typ9_path: Path,
    typ10_path: Path,
) -> CrossTypeComparison:
    """Run cross-type high-win comparison."""
    types: dict[int, TypeSummary] = {}
    total_events = 0
    all_dates: list[str] = []

    # Load main forensik for Typ-6
    forensik_data = _load_json(forensik_path)
    if forensik_data:
        types[6] = _extract_typ6_from_forensik(forensik_data)
        total_events += types[6].events_count
        all_dates.extend(e["date"] for e in types[6].events)

    # Load Typ-7 specific
    typ7_data = _load_json(typ7_path)
    if typ7_data:
        types[7] = _extract_typ7_from_forensik(typ7_data)
        total_events += types[7].events_count
        all_dates.extend(e["date"] for e in types[7].events)
    elif forensik_data:
        # Fallback: extract from main forensik
        events_typ7 = [e for e in forensik_data.get("events", []) if e.get("keno_type") == 7]
        if events_typ7:
            types[7] = TypeSummary(
                keno_type=7,
                events_count=len(events_typ7),
                unique_dates=len(set(e["date"] for e in events_typ7)),
                payout_per_hit=1000.0,
                birthday_ratio_mean=sum(e.get("birthday_ratio", 0) for e in events_typ7) / len(events_typ7),
                weekday_distribution=dict(
                    (wd, sum(1 for e in events_typ7 if e.get("weekday") == wd))
                    for wd in set(e.get("weekday") for e in events_typ7 if e.get("weekday"))
                ),
                strategy_distribution={},
                caveat=f"N={len(events_typ7)} events (from main forensik)",
                events=events_typ7,
            )
            total_events += types[7].events_count
            all_dates.extend(e["date"] for e in events_typ7)

    # Load Typ-8
    typ8_data = _load_json(typ8_path)
    if typ8_data:
        types[8] = _extract_typ8_from_forensik(typ8_data)
        total_events += types[8].events_count
        all_dates.extend(e["date"] for e in types[8].events)

    # Load Typ-9 null result
    typ9_data = _load_json(typ9_path)
    if typ9_data:
        types[9] = _extract_typ9_null(typ9_data)
        # events_count is 0 for null result

    # Load Typ-10 null result
    typ10_data = _load_json(typ10_path)
    if typ10_data:
        types[10] = _extract_typ10_null(typ10_data)
        # events_count is 0 for null result

    # Determine draws analyzed (from typ9/typ10 which have this info)
    draws_analyzed = 0
    if typ9_data:
        draws_analyzed = typ9_data.get("draws_analyzed", 0)
    elif typ10_data:
        draws_analyzed = typ10_data.get("draws_analyzed", 0)

    # Date range
    date_range = ("", "")
    if all_dates:
        all_dates_sorted = sorted(all_dates)
        date_range = (all_dates_sorted[0], all_dates_sorted[-1])

    # Interpretation
    interpretation_parts = [
        f"Cross-type comparison of {total_events} high-win events across Typ-6 to Typ-10.",
    ]

    if 6 in types:
        interpretation_parts.append(f"Typ-6 (6/6=500 EUR): {types[6].events_count} events observed.")
    if 7 in types:
        interpretation_parts.append(f"Typ-7 (7/7=1000 EUR): {types[7].events_count} events observed.")
    if 8 in types:
        interpretation_parts.append(f"Typ-8 (8/8=10000 EUR): {types[8].events_count} events observed.")
    if 9 in types:
        interpretation_parts.append(
            f"Typ-9 (9/9=50000 EUR): 0 events (statistically expected, P(0)>80%)."
        )
    if 10 in types:
        interpretation_parts.append(
            f"Typ-10 (10/10=100000 EUR): 0 events (statistically expected, P(0)>95%)."
        )

    # Birthday ratio comparison
    br_values = [(t, types[t].birthday_ratio_mean) for t in [6, 7, 8] if t in types and types[t].birthday_ratio_mean is not None]
    if br_values:
        br_summary = ", ".join(f"Typ-{t}: {br:.3f}" for t, br in br_values)
        interpretation_parts.append(f"Birthday ratios (expected ~0.443): {br_summary}.")

    interpretation = " ".join(interpretation_parts)

    return CrossTypeComparison(
        types=types,
        total_events=total_events,
        draws_analyzed=draws_analyzed,
        date_range=date_range,
        interpretation=interpretation,
    )


def _type_summary_to_dict(summary: TypeSummary) -> dict[str, Any]:
    """Convert TypeSummary to dict for JSON serialization."""
    return {
        "keno_type": summary.keno_type,
        "events_count": summary.events_count,
        "unique_dates": summary.unique_dates,
        "payout_per_hit_eur": summary.payout_per_hit,
        "birthday_ratio_mean": summary.birthday_ratio_mean,
        "weekday_distribution": summary.weekday_distribution,
        "strategy_distribution": summary.strategy_distribution,
        "null_hypothesis": summary.null_hypothesis,
        "caveat": summary.caveat,
        "events_count_in_detail": len(summary.events),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-Type High-Win Comparison (Typ-6 to Typ-10)")
    parser.add_argument(
        "--forensik",
        type=str,
        default="results/high_win_forensik.json",
        help="Main forensik JSON (default: results/high_win_forensik.json)",
    )
    parser.add_argument(
        "--typ7",
        type=str,
        default="results/typ7_highwin_forensik.json",
        help="Typ-7 forensik JSON (default: results/typ7_highwin_forensik.json)",
    )
    parser.add_argument(
        "--typ8",
        type=str,
        default="results/typ8_forensik.json",
        help="Typ-8 forensik JSON (default: results/typ8_forensik.json)",
    )
    parser.add_argument(
        "--typ9",
        type=str,
        default="results/typ9_highwin_forensik.json",
        help="Typ-9 forensik JSON (default: results/typ9_highwin_forensik.json)",
    )
    parser.add_argument(
        "--typ10",
        type=str,
        default="results/typ10_highwin_forensik.json",
        help="Typ-10 forensik JSON (default: results/typ10_highwin_forensik.json)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/cross_type_highwin_comparison.json",
        help="Output JSON (default: results/cross_type_highwin_comparison.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=" * 80)
    print("CROSS-TYPE HIGH-WIN COMPARISON (Typ-6 to Typ-10)")
    print("=" * 80)
    print()

    result = run_cross_type_comparison(
        forensik_path=Path(args.forensik),
        typ7_path=Path(args.typ7),
        typ8_path=Path(args.typ8),
        typ9_path=Path(args.typ9),
        typ10_path=Path(args.typ10),
    )

    # Print summary
    print(f"Total High-Win Events: {result.total_events}")
    print(f"Draws Analyzed: {result.draws_analyzed}")
    if result.date_range[0]:
        print(f"Date Range: {result.date_range[0]} to {result.date_range[1]}")
    print()

    print("-" * 80)
    print("PER-TYPE SUMMARY")
    print("-" * 80)
    print()

    for keno_type in [6, 7, 8, 9, 10]:
        if keno_type not in result.types:
            print(f"Typ-{keno_type}: NO DATA AVAILABLE")
            print()
            continue

        summary = result.types[keno_type]
        print(f"Typ-{keno_type} ({int(summary.payout_per_hit):,} EUR per full hit):")
        print(f"  Events: {summary.events_count}")
        print(f"  Unique Dates: {summary.unique_dates}")

        if summary.birthday_ratio_mean is not None:
            print(f"  Birthday Ratio Mean: {summary.birthday_ratio_mean:.3f} (expected: 0.443)")
        else:
            print("  Birthday Ratio Mean: n/a")

        if summary.weekday_distribution:
            wd_str = ", ".join(f"{k}: {v}" for k, v in sorted(summary.weekday_distribution.items(), key=lambda x: -x[1])[:3])
            print(f"  Top Weekdays: {wd_str}")

        if summary.strategy_distribution:
            strat_str = ", ".join(f"{k}: {v}" for k, v in sorted(summary.strategy_distribution.items(), key=lambda x: -x[1])[:3])
            print(f"  Top Strategies: {strat_str}")

        if summary.null_hypothesis:
            print(f"  Null Hypothesis: {summary.null_hypothesis}")

        if summary.caveat:
            print(f"  Caveat: {summary.caveat}")

        print()

    print("-" * 80)
    print("INTERPRETATION")
    print("-" * 80)
    print(result.interpretation)
    print()

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "analysis": "cross_type_highwin_comparison",
        "generated_at": datetime.now().isoformat(),
        "sources": {
            "forensik": args.forensik,
            "typ7": args.typ7,
            "typ8": args.typ8,
            "typ9": args.typ9,
            "typ10": args.typ10,
        },
        "total_events": result.total_events,
        "draws_analyzed": result.draws_analyzed,
        "date_range": {"start": result.date_range[0], "end": result.date_range[1]},
        "types": {str(k): _type_summary_to_dict(v) for k, v in result.types.items()},
        "interpretation": result.interpretation,
    }

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON written: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
