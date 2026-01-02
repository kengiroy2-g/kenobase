#!/usr/bin/env python3
"""High-Win Forensik: Detailanalyse aller Ziehungen mit Payout >=400 EUR.

Extracts all high-win events from backtest results and performs:
- Weekday distribution analysis
- Birthday-ratio analysis (numbers 1-31 vs 32-70)
- Preceding draw pattern analysis
- Event clustering (temporal proximity)
- Permutation-based null model test for clustering significance

Examples:
  python scripts/analyze_high_win_forensik.py
  python scripts/analyze_high_win_forensik.py --backtest results/high_payout_backtest_2018_2024.json
  python scripts/analyze_high_win_forensik.py --permutations 10000
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from kenobase.core.data_loader import DataLoader, DrawResult, GameType


@dataclass
class HighWinEvent:
    """Single high-win event extracted from backtest."""

    date: str
    ticket_id: str
    keno_type: int
    numbers: list[int]
    hits: int
    payout: float
    strategy: str


@dataclass
class DrawContext:
    """Context for a draw: preceding numbers, weekday, etc."""

    date: str
    weekday: str
    weekday_num: int
    numbers: list[int]
    birthday_count: int  # numbers 1-31
    non_birthday_count: int  # numbers 32-70
    birthday_ratio: float


@dataclass
class ForensikResult:
    """Complete forensik analysis result."""

    events_total: int
    unique_dates: int
    weekday_distribution: dict[str, int]
    birthday_ratio_mean: float
    birthday_ratio_events: list[float]
    ticket_distribution: dict[str, int]
    cluster_analysis: dict[str, Any]
    permutation_test: dict[str, Any]
    events: list[dict[str, Any]]


def _parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD string to datetime."""
    return datetime.strptime(s, "%Y-%m-%d")


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_high_win_events(backtest_path: Path) -> list[HighWinEvent]:
    """Extract all high-win events from backtest JSON."""
    payload = _load_json(backtest_path)
    events: list[HighWinEvent] = []

    results = payload.get("results", [])
    for r in results:
        high_events = r.get("high_payout_events", [])
        for ev in high_events:
            events.append(
                HighWinEvent(
                    date=ev["date"],
                    ticket_id=r["ticket_id"],
                    keno_type=r["keno_type"],
                    numbers=r["numbers"],
                    hits=ev["hits"],
                    payout=ev["payout"],
                    strategy=r.get("strategy", "unknown"),
                )
            )

    return events


def _load_draws_as_dict(draws_path: str) -> dict[str, list[int]]:
    """Load draws and return date -> numbers mapping."""
    loader = DataLoader()
    draws = loader.load(draws_path, game_type=GameType.KENO)
    return {str(d.date.date()): list(d.numbers) for d in draws}


def _calculate_birthday_ratio(numbers: list[int]) -> tuple[int, int, float]:
    """Calculate birthday (1-31) vs non-birthday (32-70) ratio."""
    birthday = sum(1 for n in numbers if 1 <= n <= 31)
    non_birthday = sum(1 for n in numbers if 32 <= n <= 70)
    ratio = birthday / 20.0 if len(numbers) == 20 else birthday / len(numbers)
    return birthday, non_birthday, ratio


def _get_draw_context(date_str: str, numbers: list[int]) -> DrawContext:
    """Get context for a single draw."""
    dt = _parse_date(date_str)
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    birthday, non_birthday, ratio = _calculate_birthday_ratio(numbers)

    return DrawContext(
        date=date_str,
        weekday=weekdays[dt.weekday()],
        weekday_num=dt.weekday(),
        numbers=numbers,
        birthday_count=birthday,
        non_birthday_count=non_birthday,
        birthday_ratio=ratio,
    )


def _analyze_clustering(events: list[HighWinEvent]) -> dict[str, Any]:
    """Analyze temporal clustering of high-win events."""
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
        "gaps_days": gaps,
    }


def _permutation_test_clustering(
    event_dates: list[str],
    all_dates: list[str],
    n_permutations: int = 1000,
) -> dict[str, Any]:
    """Test if event clustering is significant vs random placement.

    Null hypothesis: High-win events are uniformly distributed across all draws.
    Test statistic: Mean gap between consecutive events.
    """
    if len(event_dates) < 2 or len(all_dates) < len(event_dates):
        return {"p_value": None, "observed_mean_gap": None, "null_mean_gap": None}

    # Observed statistic
    sorted_event_dates = sorted(event_dates)
    event_indices = [all_dates.index(d) for d in sorted_event_dates]
    observed_gaps = [event_indices[i + 1] - event_indices[i] for i in range(len(event_indices) - 1)]
    observed_mean = sum(observed_gaps) / len(observed_gaps) if observed_gaps else 0

    # Permutation distribution
    n_events = len(event_dates)
    null_means: list[float] = []

    for _ in range(n_permutations):
        sampled_indices = sorted(random.sample(range(len(all_dates)), n_events))
        perm_gaps = [sampled_indices[i + 1] - sampled_indices[i] for i in range(len(sampled_indices) - 1)]
        if perm_gaps:
            null_means.append(sum(perm_gaps) / len(perm_gaps))

    if not null_means:
        return {"p_value": None, "observed_mean_gap": observed_mean, "null_mean_gap": None}

    # Two-sided p-value: proportion of permutations with mean gap <= observed
    # (smaller mean gap = more clustered)
    p_value = sum(1 for nm in null_means if nm <= observed_mean) / len(null_means)

    return {
        "p_value": p_value,
        "observed_mean_gap": observed_mean,
        "null_mean_gap": sum(null_means) / len(null_means),
        "null_std_gap": (sum((nm - sum(null_means) / len(null_means)) ** 2 for nm in null_means) / len(null_means))
        ** 0.5,
        "n_permutations": n_permutations,
        "interpretation": "p<0.05 suggests clustering is non-random" if p_value and p_value < 0.05 else "no significant clustering detected",
    }


def _analyze_ticket_performance(events: list[HighWinEvent]) -> dict[str, int]:
    """Count high-win events per ticket."""
    counter: Counter[str] = Counter()
    for e in events:
        counter[e.ticket_id] += 1
    return dict(counter.most_common())


# V1/V2 strategy classification
V1_STRATEGIES = {"near_miss", "jackpot", "balanced"}
V2_STRATEGIES = {"pair_focused"}


def _classify_strategy_version(strategy: str) -> str:
    """Classify strategy as V1 or V2."""
    if strategy in V1_STRATEGIES:
        return "V1"
    elif strategy in V2_STRATEGIES:
        return "V2"
    return "unknown"


def _analyze_v1_v2_comparison(
    events: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compare V1 vs V2 strategy forensik metrics.

    V1 strategies: near_miss, jackpot, balanced
    V2 strategies: pair_focused
    """
    v1_events = [e for e in events if e.get("strategy") in V1_STRATEGIES]
    v2_events = [e for e in events if e.get("strategy") in V2_STRATEGIES]

    def _compute_group_stats(group_events: list[dict[str, Any]]) -> dict[str, Any]:
        if not group_events:
            return {
                "count": 0,
                "unique_dates": 0,
                "birthday_ratio_mean": None,
                "birthday_ratio_std": None,
                "weekday_distribution": {},
                "total_payout": 0.0,
                "avg_payout": None,
                "strategies": {},
            }

        dates = list(set(e["date"] for e in group_events))
        br_values = [e["birthday_ratio"] for e in group_events if "birthday_ratio" in e]
        weekdays = [e["weekday"] for e in group_events if "weekday" in e]
        payouts = [e["payout"] for e in group_events if "payout" in e]
        strategies = [e["strategy"] for e in group_events if "strategy" in e]

        br_mean = sum(br_values) / len(br_values) if br_values else None
        br_std = None
        if br_values and len(br_values) > 1:
            br_std = (sum((v - br_mean) ** 2 for v in br_values) / len(br_values)) ** 0.5

        return {
            "count": len(group_events),
            "unique_dates": len(dates),
            "birthday_ratio_mean": br_mean,
            "birthday_ratio_std": br_std,
            "weekday_distribution": dict(Counter(weekdays)),
            "total_payout": sum(payouts),
            "avg_payout": sum(payouts) / len(payouts) if payouts else None,
            "strategies": dict(Counter(strategies)),
        }

    v1_stats = _compute_group_stats(v1_events)
    v2_stats = _compute_group_stats(v2_events)

    # Compute deltas
    delta_birthday_ratio = None
    if v1_stats["birthday_ratio_mean"] is not None and v2_stats["birthday_ratio_mean"] is not None:
        delta_birthday_ratio = v2_stats["birthday_ratio_mean"] - v1_stats["birthday_ratio_mean"]

    delta_avg_payout = None
    if v1_stats["avg_payout"] is not None and v2_stats["avg_payout"] is not None:
        delta_avg_payout = v2_stats["avg_payout"] - v1_stats["avg_payout"]

    return {
        "v1": v1_stats,
        "v2": v2_stats,
        "delta_birthday_ratio": delta_birthday_ratio,
        "delta_avg_payout": delta_avg_payout,
        "v1_strategies_included": list(V1_STRATEGIES),
        "v2_strategies_included": list(V2_STRATEGIES),
    }


def run_forensik(
    backtest_path: Path,
    draws_path: str,
    n_permutations: int = 1000,
) -> ForensikResult:
    """Run complete forensik analysis."""
    # Extract events
    events = _extract_high_win_events(backtest_path)
    if not events:
        return ForensikResult(
            events_total=0,
            unique_dates=0,
            weekday_distribution={},
            birthday_ratio_mean=0.0,
            birthday_ratio_events=[],
            ticket_distribution={},
            cluster_analysis={},
            permutation_test={},
            events=[],
        )

    # Load draws for context
    draws_dict = _load_draws_as_dict(draws_path)
    all_dates = sorted(draws_dict.keys())

    # Get unique dates
    unique_dates = sorted(set(e.date for e in events))

    # Weekday distribution
    weekday_counter: Counter[str] = Counter()
    birthday_ratios: list[float] = []
    enriched_events: list[dict[str, Any]] = []

    for e in events:
        if e.date not in draws_dict:
            continue

        draw_numbers = draws_dict[e.date]
        ctx = _get_draw_context(e.date, draw_numbers)

        weekday_counter[ctx.weekday] += 1
        birthday_ratios.append(ctx.birthday_ratio)

        # Preceding draw analysis
        date_idx = all_dates.index(e.date) if e.date in all_dates else -1
        prev_draw = None
        if date_idx > 0:
            prev_date = all_dates[date_idx - 1]
            prev_numbers = draws_dict.get(prev_date, [])
            prev_ctx = _get_draw_context(prev_date, prev_numbers)
            prev_draw = {
                "date": prev_date,
                "birthday_ratio": prev_ctx.birthday_ratio,
                "numbers": prev_numbers,
            }

        enriched_events.append(
            {
                "date": e.date,
                "ticket_id": e.ticket_id,
                "keno_type": e.keno_type,
                "ticket_numbers": e.numbers,
                "hits": e.hits,
                "payout": e.payout,
                "strategy": e.strategy,
                "weekday": ctx.weekday,
                "draw_numbers": draw_numbers,
                "birthday_count": ctx.birthday_count,
                "birthday_ratio": ctx.birthday_ratio,
                "preceding_draw": prev_draw,
            }
        )

    # Cluster analysis
    cluster_analysis = _analyze_clustering(events)

    # Permutation test
    permutation_test = _permutation_test_clustering(unique_dates, all_dates, n_permutations)

    # Ticket performance
    ticket_distribution = _analyze_ticket_performance(events)

    return ForensikResult(
        events_total=len(events),
        unique_dates=len(unique_dates),
        weekday_distribution=dict(weekday_counter),
        birthday_ratio_mean=sum(birthday_ratios) / len(birthday_ratios) if birthday_ratios else 0.0,
        birthday_ratio_events=birthday_ratios,
        ticket_distribution=ticket_distribution,
        cluster_analysis=cluster_analysis,
        permutation_test=permutation_test,
        events=enriched_events,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="High-Win Forensik Analysis")
    parser.add_argument(
        "--backtest",
        type=str,
        default="results/high_payout_backtest_2018_2024.json",
        help="Backtest JSON with high-payout events (default: results/high_payout_backtest_2018_2024.json)",
    )
    parser.add_argument(
        "--draws",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Pfad zur Ziehungs-CSV (default: data/raw/keno/KENO_ab_2018.csv)",
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
        default="results/high_win_forensik.json",
        help="Output JSON (default: results/high_win_forensik.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    backtest_path = Path(args.backtest)
    if not backtest_path.exists():
        print(f"ERROR: Backtest file not found: {backtest_path}")
        return 1

    print("=" * 80)
    print("HIGH-WIN FORENSIK ANALYSIS")
    print("=" * 80)
    print(f"Backtest: {args.backtest}")
    print(f"Draws: {args.draws}")
    print(f"Permutations: {args.permutations}")
    print()

    result = run_forensik(backtest_path, args.draws, args.permutations)

    # Summary
    print(f"Total High-Win Events: {result.events_total}")
    print(f"Unique Dates: {result.unique_dates}")
    print()

    print("Weekday Distribution:")
    for day, count in sorted(result.weekday_distribution.items(), key=lambda x: -x[1]):
        print(f"  {day}: {count}")
    print()

    print(f"Birthday Ratio (mean): {result.birthday_ratio_mean:.3f}")
    print(f"  (0.443 = expected for uniform 20/70)")
    print()

    print("Top Tickets by High-Win Count:")
    for ticket_id, count in list(result.ticket_distribution.items())[:10]:
        print(f"  {count}x: {ticket_id}")
    print()

    print("Cluster Analysis:")
    ca = result.cluster_analysis
    print(f"  Clusters (<=30 days): {ca.get('cluster_count', 0)}")
    print(f"  Mean Gap (days): {ca.get('mean_gap_days', 'n/a')}")
    print(f"  Min/Max Gap: {ca.get('min_gap_days', 'n/a')} / {ca.get('max_gap_days', 'n/a')}")
    print()

    print("Permutation Test (Null Model):")
    pt = result.permutation_test
    print(f"  Observed Mean Gap: {pt.get('observed_mean_gap', 'n/a')}")
    print(f"  Null Mean Gap: {pt.get('null_mean_gap', 'n/a')}")
    print(f"  P-Value: {pt.get('p_value', 'n/a')}")
    print(f"  Interpretation: {pt.get('interpretation', 'n/a')}")
    print()

    # V1 vs V2 comparison
    v1_v2_comparison = _analyze_v1_v2_comparison(result.events)

    print("=" * 80)
    print("V1 vs V2 STRATEGY COMPARISON")
    print("=" * 80)
    print(f"  V1 strategies: {', '.join(V1_STRATEGIES)}")
    print(f"  V2 strategies: {', '.join(V2_STRATEGIES)}")
    print()

    v1 = v1_v2_comparison["v1"]
    v2 = v1_v2_comparison["v2"]

    print(f"  V1 Events: {v1['count']} (unique dates: {v1['unique_dates']})")
    print(f"  V2 Events: {v2['count']} (unique dates: {v2['unique_dates']})")
    print()

    print("  Birthday Ratio (mean):")
    print(f"    V1: {v1['birthday_ratio_mean']:.3f}" if v1['birthday_ratio_mean'] else "    V1: n/a")
    print(f"    V2: {v2['birthday_ratio_mean']:.3f}" if v2['birthday_ratio_mean'] else "    V2: n/a")
    if v1_v2_comparison["delta_birthday_ratio"] is not None:
        delta_br = v1_v2_comparison["delta_birthday_ratio"]
        print(f"    Delta (V2-V1): {delta_br:+.3f}")
    print()

    print("  Average Payout:")
    print(f"    V1: {v1['avg_payout']:.2f} EUR" if v1['avg_payout'] else "    V1: n/a")
    print(f"    V2: {v2['avg_payout']:.2f} EUR" if v2['avg_payout'] else "    V2: n/a")
    if v1_v2_comparison["delta_avg_payout"] is not None:
        delta_pay = v1_v2_comparison["delta_avg_payout"]
        print(f"    Delta (V2-V1): {delta_pay:+.2f} EUR")
    print()

    print("  Weekday Distribution:")
    print(f"    V1: {v1['weekday_distribution']}")
    print(f"    V2: {v2['weekday_distribution']}")
    print()

    # Write output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "analysis": "high_win_forensik",
        "generated_at": datetime.now().isoformat(),
        "backtest_source": str(args.backtest),
        "draws_source": str(args.draws),
        "events_total": result.events_total,
        "unique_dates": result.unique_dates,
        "weekday_distribution": result.weekday_distribution,
        "birthday_ratio_mean": result.birthday_ratio_mean,
        "birthday_ratio_events": result.birthday_ratio_events,
        "ticket_distribution": result.ticket_distribution,
        "cluster_analysis": result.cluster_analysis,
        "permutation_test": result.permutation_test,
        "v1_v2_comparison": v1_v2_comparison,
        "events": result.events,
    }

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON written: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
