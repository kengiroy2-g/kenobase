#!/usr/bin/env python3
"""Typ-8 High-Win Forensik: Spezifische Analyse fuer Typ-8 Tickets mit Schwelle 100 EUR.

Typ-8 Auszahlungen (pro 1 EUR Einsatz):
- 8 Treffer: 10.000 EUR
- 7 Treffer: 100 EUR
- 6 Treffer: 15 EUR
- 5 Treffer: 2 EUR
- 4 Treffer: 1 EUR
- 0 Treffer: 1 EUR (Garantie)

Diese Analyse fokussiert auf Events >= 100 EUR (d.h. 7/8 und 8/8 Treffer).

Usage:
    python scripts/backtest_typ8_analysis.py
    python scripts/backtest_typ8_analysis.py --threshold 15
    python scripts/backtest_typ8_analysis.py --draws data/raw/keno/KENO_ab_2022_bereinigt.csv
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any

from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.core.keno_quotes import get_fixed_quote, KENO_FIXED_QUOTES_BY_TYPE


@dataclass
class Typ8Event:
    """Single Typ-8 high-win event."""

    date: str
    ticket: list[int]
    hits: int
    payout: float
    draw_numbers: list[int]
    matching_numbers: list[int]


@dataclass
class Typ8ForensikResult:
    """Complete Typ-8 forensik analysis result."""

    total_draws: int
    total_events: int
    events_by_hits: dict[int, int]
    total_payout: float
    mean_payout: float
    weekday_distribution: dict[str, int]
    birthday_ratio_mean: float
    cluster_analysis: dict[str, Any]
    permutation_test: dict[str, Any]
    events: list[dict[str, Any]]


def _parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD string to datetime."""
    return datetime.strptime(s, "%Y-%m-%d")


def _calculate_birthday_ratio(numbers: list[int]) -> float:
    """Calculate birthday (1-31) ratio."""
    birthday = sum(1 for n in numbers if 1 <= n <= 31)
    return birthday / len(numbers) if numbers else 0.0


def _count_hits(ticket: list[int], draw: list[int]) -> tuple[int, list[int]]:
    """Count hits and return matching numbers."""
    ticket_set = set(ticket)
    draw_set = set(draw)
    matching = sorted(ticket_set & draw_set)
    return len(matching), matching


def _generate_test_tickets(n_tickets: int = 50) -> list[list[int]]:
    """Generate diverse Typ-8 test tickets.

    Strategy:
    1. Popular pairs from SYSTEM_STATUS
    2. Random diversification
    3. Birthday-avoidance variants
    """
    tickets: list[list[int]] = []

    # Basis: Top-pairs from SYSTEM_STATUS (co-occurrence > 210)
    top_pairs = [
        (9, 50), (20, 36), (9, 10), (32, 64), (33, 49),
        (33, 50), (24, 40), (2, 3)
    ]

    # Build tickets around pairs
    all_nums = list(range(1, 71))

    for pair in top_pairs[:8]:
        base = list(pair)
        # Fill remaining 6 numbers randomly (avoiding duplicates)
        pool = [n for n in all_nums if n not in base]
        random.seed(42 + len(tickets))  # Reproducible
        extra = random.sample(pool, 6)
        tickets.append(sorted(base + extra))

    # Add birthday-avoidance tickets (numbers 32-70)
    non_birthday = list(range(32, 71))
    random.seed(100)
    for _ in range(10):
        tickets.append(sorted(random.sample(non_birthday, 8)))

    # Add mixed tickets
    for seed in range(200, 200 + n_tickets - len(tickets)):
        random.seed(seed)
        tickets.append(sorted(random.sample(all_nums, 8)))

    return tickets[:n_tickets]


def _analyze_clustering(events: list[Typ8Event]) -> dict[str, Any]:
    """Analyze temporal clustering of events."""
    if len(events) < 2:
        return {"clusters": [], "mean_gap_days": None, "min_gap_days": None, "max_gap_days": None}

    dates = sorted(set(_parse_date(e.date) for e in events))
    gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Find clusters: events within 30 days of each other
    clusters: list[list[str]] = []
    current_cluster: list[str] = [str(dates[0].date())]

    for i in range(1, len(dates)):
        if gaps[i - 1] <= 30:
            current_cluster.append(str(dates[i].date()))
        else:
            if len(current_cluster) >= 2:
                clusters.append(current_cluster)
            current_cluster = [str(dates[i].date())]

    if len(current_cluster) >= 2:
        clusters.append(current_cluster)

    return {
        "clusters": clusters,
        "cluster_count": len(clusters),
        "mean_gap_days": sum(gaps) / len(gaps) if gaps else None,
        "min_gap_days": min(gaps) if gaps else None,
        "max_gap_days": max(gaps) if gaps else None,
    }


def _permutation_test_clustering(
    event_dates: list[str],
    all_dates: list[str],
    n_permutations: int = 1000,
) -> dict[str, Any]:
    """Test if event clustering is significant vs random placement."""
    if len(event_dates) < 2 or len(all_dates) < len(event_dates):
        return {"p_value": None, "observed_mean_gap": None, "null_mean_gap": None}

    # Observed statistic
    sorted_event_dates = sorted(event_dates)
    event_indices = [all_dates.index(d) for d in sorted_event_dates if d in all_dates]

    if len(event_indices) < 2:
        return {"p_value": None, "observed_mean_gap": None, "null_mean_gap": None}

    observed_gaps = [event_indices[i + 1] - event_indices[i] for i in range(len(event_indices) - 1)]
    observed_mean = sum(observed_gaps) / len(observed_gaps) if observed_gaps else 0

    # Permutation distribution
    n_events = len(event_dates)
    null_means: list[float] = []

    random.seed(42)
    for _ in range(n_permutations):
        sampled_indices = sorted(random.sample(range(len(all_dates)), min(n_events, len(all_dates))))
        perm_gaps = [sampled_indices[i + 1] - sampled_indices[i] for i in range(len(sampled_indices) - 1)]
        if perm_gaps:
            null_means.append(sum(perm_gaps) / len(perm_gaps))

    if not null_means:
        return {"p_value": None, "observed_mean_gap": observed_mean, "null_mean_gap": None}

    # Two-sided p-value
    p_value = sum(1 for nm in null_means if nm <= observed_mean) / len(null_means)

    return {
        "p_value": p_value,
        "observed_mean_gap": observed_mean,
        "null_mean_gap": sum(null_means) / len(null_means),
        "n_permutations": n_permutations,
        "interpretation": "p<0.05 suggests clustering is non-random" if p_value and p_value < 0.05 else "no significant clustering",
    }


def run_typ8_forensik(
    draws_path: str,
    threshold: float = 100.0,
    n_tickets: int = 50,
    n_permutations: int = 1000,
) -> Typ8ForensikResult:
    """Run complete Typ-8 forensik analysis.

    Args:
        draws_path: Path to KENO draws CSV
        threshold: Minimum payout threshold in EUR (default 100 = 7/8 hits)
        n_tickets: Number of test tickets to simulate
        n_permutations: Number of permutations for null model test

    Returns:
        Typ8ForensikResult with all analysis metrics
    """
    # Load draws
    loader = DataLoader()
    draws = loader.load(draws_path, game_type=GameType.KENO)

    if not draws:
        return Typ8ForensikResult(
            total_draws=0,
            total_events=0,
            events_by_hits={},
            total_payout=0.0,
            mean_payout=0.0,
            weekday_distribution={},
            birthday_ratio_mean=0.0,
            cluster_analysis={},
            permutation_test={},
            events=[],
        )

    # Generate test tickets
    tickets = _generate_test_tickets(n_tickets)

    # Typ-8 quotes
    typ8_quotes = KENO_FIXED_QUOTES_BY_TYPE.get(8, {})
    print(f"Typ-8 Quotes: {typ8_quotes}")
    print(f"Threshold: {threshold} EUR")
    print(f"Test Tickets: {n_tickets}")
    print(f"Total Draws: {len(draws)}")
    print()

    # Analyze each draw against each ticket
    events: list[Typ8Event] = []
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    all_dates: list[str] = []

    for draw in draws:
        date_str = str(draw.date.date())
        all_dates.append(date_str)
        draw_nums = list(draw.numbers)

        for ticket in tickets:
            hits, matching = _count_hits(ticket, draw_nums)
            payout = get_fixed_quote(8, hits)

            if payout >= threshold:
                events.append(Typ8Event(
                    date=date_str,
                    ticket=ticket,
                    hits=hits,
                    payout=payout,
                    draw_numbers=draw_nums,
                    matching_numbers=matching,
                ))

    if not events:
        return Typ8ForensikResult(
            total_draws=len(draws),
            total_events=0,
            events_by_hits={},
            total_payout=0.0,
            mean_payout=0.0,
            weekday_distribution={},
            birthday_ratio_mean=0.0,
            cluster_analysis={},
            permutation_test={},
            events=[],
        )

    # Aggregate by hits
    events_by_hits: Counter[int] = Counter()
    for e in events:
        events_by_hits[e.hits] += 1

    # Weekday distribution
    weekday_counter: Counter[str] = Counter()
    birthday_ratios: list[float] = []

    for e in events:
        dt = _parse_date(e.date)
        weekday_counter[weekdays[dt.weekday()]] += 1
        birthday_ratios.append(_calculate_birthday_ratio(e.draw_numbers))

    # Cluster analysis
    cluster_analysis = _analyze_clustering(events)

    # Permutation test
    event_dates = list(set(e.date for e in events))
    permutation_test = _permutation_test_clustering(event_dates, all_dates, n_permutations)

    # Convert events to dicts for JSON
    enriched_events = []
    for e in events:
        dt = _parse_date(e.date)
        enriched_events.append({
            "date": e.date,
            "weekday": weekdays[dt.weekday()],
            "ticket": e.ticket,
            "hits": e.hits,
            "payout": e.payout,
            "draw_numbers": e.draw_numbers,
            "matching_numbers": e.matching_numbers,
            "birthday_ratio": _calculate_birthday_ratio(e.draw_numbers),
        })

    total_payout = sum(e.payout for e in events)

    return Typ8ForensikResult(
        total_draws=len(draws),
        total_events=len(events),
        events_by_hits=dict(events_by_hits),
        total_payout=total_payout,
        mean_payout=total_payout / len(events) if events else 0.0,
        weekday_distribution=dict(weekday_counter),
        birthday_ratio_mean=sum(birthday_ratios) / len(birthday_ratios) if birthday_ratios else 0.0,
        cluster_analysis=cluster_analysis,
        permutation_test=permutation_test,
        events=enriched_events,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Typ-8 High-Win Forensik Analysis")
    parser.add_argument(
        "--draws",
        type=str,
        default="Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv",
        help="Pfad zur Ziehungs-CSV (default: Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Minimum payout threshold in EUR (default: 100 = captures 7/8)",
    )
    parser.add_argument(
        "--tickets",
        type=int,
        default=50,
        help="Number of test tickets to simulate (default: 50)",
    )
    parser.add_argument(
        "--permutations",
        type=int,
        default=1000,
        help="Number of permutations for null model test (default: 1000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/typ8_forensik.json",
        help="Output JSON (default: results/typ8_forensik.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    draws_path = Path(args.draws)
    if not draws_path.exists():
        print(f"ERROR: Draws file not found: {draws_path}")
        return 1

    print("=" * 80)
    print("TYP-8 HIGH-WIN FORENSIK ANALYSIS")
    print("=" * 80)
    print(f"Draws: {args.draws}")
    print(f"Threshold: {args.threshold} EUR")
    print(f"Tickets: {args.tickets}")
    print(f"Permutations: {args.permutations}")
    print()

    result = run_typ8_forensik(
        draws_path=str(args.draws),
        threshold=args.threshold,
        n_tickets=args.tickets,
        n_permutations=args.permutations,
    )

    # Summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Draws: {result.total_draws}")
    print(f"Total High-Win Events (>={args.threshold} EUR): {result.total_events}")
    print(f"Total Payout: {result.total_payout:.2f} EUR")
    print(f"Mean Payout per Event: {result.mean_payout:.2f} EUR")
    print()

    print("Events by Hits:")
    for hits, count in sorted(result.events_by_hits.items(), reverse=True):
        payout = get_fixed_quote(8, hits)
        print(f"  {hits}/8 hits ({payout} EUR): {count} events")
    print()

    print("Weekday Distribution:")
    for day, count in sorted(result.weekday_distribution.items(), key=lambda x: -x[1]):
        print(f"  {day}: {count}")
    print()

    print(f"Birthday Ratio (mean): {result.birthday_ratio_mean:.3f}")
    print(f"  (0.443 = expected for uniform 20/70)")
    print()

    print("Cluster Analysis:")
    ca = result.cluster_analysis
    print(f"  Clusters (<=30 days): {ca.get('cluster_count', 0)}")
    print(f"  Mean Gap (days): {ca.get('mean_gap_days', 'n/a')}")
    print()

    print("Permutation Test (Null Model):")
    pt = result.permutation_test
    print(f"  P-Value: {pt.get('p_value', 'n/a')}")
    print(f"  Interpretation: {pt.get('interpretation', 'n/a')}")
    print()

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "analysis": "typ8_forensik",
        "generated_at": datetime.now().isoformat(),
        "draws_source": str(args.draws),
        "threshold_eur": args.threshold,
        "n_tickets": args.tickets,
        "total_draws": result.total_draws,
        "total_events": result.total_events,
        "events_by_hits": result.events_by_hits,
        "total_payout": result.total_payout,
        "mean_payout": result.mean_payout,
        "weekday_distribution": result.weekday_distribution,
        "birthday_ratio_mean": result.birthday_ratio_mean,
        "cluster_analysis": result.cluster_analysis,
        "permutation_test": result.permutation_test,
        "events": result.events[:100],  # Limit to 100 events in JSON
        "events_total_in_json": min(100, len(result.events)),
    }

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON written: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
