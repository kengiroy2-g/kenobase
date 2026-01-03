#!/usr/bin/env python3
"""
BACKTEST: Typ-6 (6/6) innerhalb von X Tagen fuer verschiedene Pool-Groessen.

Wichtig:
- "pool_hits>=6" bedeutet nur: In der Ziehung waren >=6 Zahlen aus deinem Pool.
  Das ist KEIN automatischer 6/6-Gewinn, ausser du spielst genau die 6 gezogenen Zahlen.

Objectives:
  - pool_hits:      Fenster-Erfolg, wenn innerhalb des Fensters ein Tag mit pool_hits>=min_hits existiert.
  - filtered_all:   Fenster-Erfolg, wenn innerhalb des Fensters ein 6/6 mit *irgendeiner*
                    gefilterten Kombination (filter_combinations) existiert (impliziert: du spielst alle).
  - topk:           Fenster-Erfolg, wenn innerhalb des Fensters ein 6/6 mit den Top-K Tickets existiert.

Pool-Modus:
  - fixed:   Pool/Tickets werden am Fenster-Start gebaut und fuer das Fenster eingefroren.
  - rolling: Pool/Tickets werden taeglich neu gebaut (realistischer, aber teurer zu spielen).

Beispiele:
  python scripts/backtest_typ6_window.py --year 2025 --window 30 --objective pool_hits --pool-sizes 10,12,14,17
  python scripts/backtest_typ6_window.py --year 2025 --window 30 --objective filtered_all --pool-sizes 14,15,16,17
  python scripts/backtest_typ6_window.py --year 2025 --window 30 --objective topk --mode rolling --pool-sizes 17 --tickets-per-day 3
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from generate_optimized_tickets import (
    build_reduced_pool,
    filter_combinations,
    get_hot_numbers,
    score_combination,
)

from generate_optimized_pool_v3 import (
    attach_stake_and_ratio,
    build_reduced_pool_v3,
    load_gq_daily_stats,
    load_keno_draws,
)

from kenobase.analysis.popularity_correlation import calculate_popularity_scores_heuristic


@dataclass
class ResultRow:
    pool_size: int
    windows_tested: int
    windows_success: int
    success_rate: float
    avg_days_to_success: Optional[float]
    avg_tickets_per_day: Optional[float]
    avg_available_combos: Optional[float]


def _parse_pool_sizes(value: str) -> list[int]:
    parts = [p.strip() for p in value.split(",") if p.strip()]
    sizes: list[int] = []
    for p in parts:
        sizes.append(int(p))
    if not sizes:
        raise ValueError("pool-sizes darf nicht leer sein")
    if any(s <= 0 or s > 70 for s in sizes):
        raise ValueError("pool-sizes muessen zwischen 1 und 70 liegen")
    return sizes


def _within_year(draws: list[dict], start_idx: int, window: int, year: int) -> bool:
    end_idx = start_idx + window
    if end_idx > len(draws):
        return False
    return draws[start_idx]["datum"].year == year and draws[end_idx - 1]["datum"].year == year


def _window_success_fixed(
    draws: list[dict],
    start_idx: int,
    window: int,
    pool_size: int,
    pool_method: str,
    daily_stats: dict,
    popularity_scores: dict[int, float],
    correction_lookback_days: int,
    objective: str,
    tickets_per_day: int,
    min_hits: int,
) -> tuple[bool, Optional[int], Optional[int]]:
    train = draws[:start_idx]
    if pool_method == "v2":
        pool, _ = build_reduced_pool(train, target_size=pool_size)
    elif pool_method == "v3":
        pool, _ = build_reduced_pool_v3(
            draws=train,
            daily_stats=daily_stats,
            popularity_scores=popularity_scores,
            target_size=pool_size,
            correction_lookback_days=correction_lookback_days,
        )
    else:
        raise ValueError(f"Unknown pool_method: {pool_method}")
    hot = get_hot_numbers(train, lookback=3)

    combo_sets: list[set[int]] = []
    if objective in {"filtered_all", "topk"}:
        combos = filter_combinations(pool, hot, ticket_size=6)
        if objective == "topk" and combos:
            ranked = sorted(combos, key=lambda c: score_combination(c, hot), reverse=True)
            combos = ranked[: min(tickets_per_day, len(ranked))]
        combo_sets = [set(c) for c in combos]

    day_to_pool6: Optional[int] = None
    day_to_win: Optional[int] = None

    for day_offset in range(window):
        drawn = draws[start_idx + day_offset]["zahlen"]
        hits = len(pool & drawn)

        if day_to_pool6 is None and hits >= min_hits:
            day_to_pool6 = day_offset + 1

        if objective == "pool_hits":
            continue

        if day_to_win is None and hits >= 6 and combo_sets:
            for cs in combo_sets:
                if cs.issubset(drawn):
                    day_to_win = day_offset + 1
                    break

        if day_to_win is not None and day_to_pool6 is not None:
            break

    if objective == "pool_hits":
        return (day_to_pool6 is not None), day_to_pool6, None
    return (day_to_win is not None), day_to_pool6, day_to_win


def _build_daily_flags_rolling(
    draws: list[dict],
    day_indices: list[int],
    pool_size: int,
    pool_method: str,
    daily_stats: dict,
    popularity_scores: dict[int, float],
    correction_lookback_days: int,
    objective: str,
    tickets_per_day: int,
    min_history: int,
    min_hits: int,
) -> tuple[list[bool], Optional[float]]:
    flags: list[bool] = []
    combo_counts: list[int] = []

    for idx in day_indices:
        if idx < min_history:
            flags.append(False)
            continue

        train = draws[:idx]
        drawn = draws[idx]["zahlen"]

        if pool_method == "v2":
            pool, _ = build_reduced_pool(train, target_size=pool_size)
        elif pool_method == "v3":
            pool, _ = build_reduced_pool_v3(
                draws=train,
                daily_stats=daily_stats,
                popularity_scores=popularity_scores,
                target_size=pool_size,
                correction_lookback_days=correction_lookback_days,
            )
        else:
            raise ValueError(f"Unknown pool_method: {pool_method}")
        hits = len(pool & drawn)

        if objective == "pool_hits":
            flags.append(hits >= min_hits)
            continue

        hot = get_hot_numbers(train, lookback=3)
        combos = filter_combinations(pool, hot, ticket_size=6)
        combo_counts.append(len(combos))
        if not combos or hits < 6:
            flags.append(False)
            continue

        if objective == "topk":
            ranked = sorted(combos, key=lambda c: score_combination(c, hot), reverse=True)
            combos = ranked[: min(tickets_per_day, len(ranked))]

        combo_sets = [set(c) for c in combos]
        flags.append(any(cs.issubset(drawn) for cs in combo_sets))

    if objective == "pool_hits":
        return flags, None
    return flags, statistics.mean(combo_counts) if combo_counts else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest: Typ-6 6/6 innerhalb eines Fensters")
    parser.add_argument("--year", type=int, default=2025, help="Jahr (Default: 2025)")
    parser.add_argument("--window", type=int, default=30, help="Fensterlaenge in Tagen (Default: 30)")
    parser.add_argument(
        "--pool-sizes",
        type=str,
        default="10,11,12,13,14,15,16,17",
        help="Komma-separierte Pool-Groessen (Default: 10..17)",
    )
    parser.add_argument(
        "--objective",
        choices=["pool_hits", "filtered_all", "topk"],
        default="filtered_all",
        help="Was zaehlt als Erfolg (Default: filtered_all)",
    )
    parser.add_argument(
        "--mode",
        choices=["fixed", "rolling"],
        default="fixed",
        help="Pool/Tickets pro Fenster (fixed) oder taeglich (rolling) (Default: fixed)",
    )
    parser.add_argument(
        "--pool-method",
        choices=["v2", "v3"],
        default="v2",
        help="Welcher Pool-Generator (Default: v2)",
    )
    parser.add_argument(
        "--correction-lookback",
        type=int,
        default=60,
        help="Nur fuer pool-method=v3: Lookback fuer Correction-State (Default: 60)",
    )
    parser.add_argument(
        "--tickets-per-day",
        type=int,
        default=3,
        help="Nur fuer objective=topk: Anzahl gespielter Tickets/Tag (Default: 3)",
    )
    parser.add_argument(
        "--min-history",
        type=int,
        default=60,
        help="Minimale Historie bevor ein Tag bewertet wird (Default: 60)",
    )
    parser.add_argument(
        "--min-hits",
        type=int,
        default=6,
        help="Nur fuer objective=pool_hits: Schwelle (Default: 6)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional: JSON output (Pfad relativ zum Repo-Root)",
    )
    args = parser.parse_args()

    if args.window <= 0:
        raise SystemExit("--window muss > 0 sein")
    if args.tickets_per_day <= 0 and args.objective == "topk":
        raise SystemExit("--tickets-per-day muss > 0 sein fuer objective=topk")

    pool_sizes = _parse_pool_sizes(args.pool_sizes)

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    draws = load_keno_draws(keno_path)

    daily_stats: dict = {}
    if args.pool_method == "v3":
        gq_paths = [
            base_path / "Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
            base_path / "Keno_GPTs/Keno_GQ_2025.csv",
        ]
        daily_stats = load_gq_daily_stats(gq_paths)
        daily_stats = attach_stake_and_ratio(draws=draws, daily_stats=daily_stats)

    popularity_scores = calculate_popularity_scores_heuristic(range(1, 71))

    day_indices = [i for i, d in enumerate(draws) if d["datum"].year == args.year]
    if not day_indices:
        raise SystemExit(f"Keine Ziehungen fuer Jahr {args.year} gefunden")

    rows: list[ResultRow] = []
    details: dict[int, dict] = {}

    if args.mode == "rolling":
        for pool_size in pool_sizes:
            flags, avg_combo_count = _build_daily_flags_rolling(
                draws=draws,
                day_indices=day_indices,
                pool_size=pool_size,
                pool_method=args.pool_method,
                daily_stats=daily_stats,
                popularity_scores=popularity_scores,
                correction_lookback_days=args.correction_lookback,
                objective=args.objective,
                tickets_per_day=args.tickets_per_day,
                min_history=args.min_history,
                min_hits=args.min_hits,
            )

            windows_tested = max(0, len(flags) - args.window + 1)
            windows_success = 0
            days_to_success: list[int] = []

            for start in range(windows_tested):
                w = flags[start : start + args.window]
                if any(w):
                    windows_success += 1
                    days_to_success.append(w.index(True) + 1)

            rows.append(
                ResultRow(
                    pool_size=pool_size,
                    windows_tested=windows_tested,
                    windows_success=windows_success,
                    success_rate=windows_success / windows_tested if windows_tested else 0.0,
                    avg_days_to_success=statistics.mean(days_to_success) if days_to_success else None,
                    avg_tickets_per_day=float(args.tickets_per_day) if args.objective == "topk" else avg_combo_count,
                    avg_available_combos=avg_combo_count,
                )
            )
            details[pool_size] = {
                "daily_successes": int(sum(1 for f in flags if f)),
            }
    else:
        for pool_size in pool_sizes:
            windows_tested = 0
            windows_success = 0
            days_to_success: list[int] = []
            combo_counts: list[int] = []

            for start_idx in day_indices:
                if start_idx < args.min_history:
                    continue
                if not _within_year(draws, start_idx, args.window, args.year):
                    continue

                windows_tested += 1

                ok, _day_to_pool6, day_to_win = _window_success_fixed(
                    draws=draws,
                    start_idx=start_idx,
                    window=args.window,
                    pool_size=pool_size,
                    pool_method=args.pool_method,
                    daily_stats=daily_stats,
                    popularity_scores=popularity_scores,
                    correction_lookback_days=args.correction_lookback,
                    objective=args.objective,
                    tickets_per_day=args.tickets_per_day,
                    min_hits=args.min_hits,
                )
                if ok:
                    windows_success += 1
                    if args.objective == "pool_hits":
                        # day_to_pool6 ist dann gesetzt
                        days_to_success.append(_day_to_pool6 or 0)
                    else:
                        days_to_success.append(day_to_win or 0)

                if args.objective in {"filtered_all", "topk"}:
                    # Kombi-Count am Fenster-Start (Kosten-Indikator)
                    train = draws[:start_idx]
                    if args.pool_method == "v2":
                        pool, _ = build_reduced_pool(train, target_size=pool_size)
                    elif args.pool_method == "v3":
                        pool, _ = build_reduced_pool_v3(
                            draws=train,
                            daily_stats=daily_stats,
                            popularity_scores=popularity_scores,
                            target_size=pool_size,
                            correction_lookback_days=args.correction_lookback,
                        )
                    else:
                        raise ValueError(f"Unknown pool_method: {args.pool_method}")
                    hot = get_hot_numbers(train, lookback=3)
                    combos = filter_combinations(pool, hot, ticket_size=6)
                    combo_counts.append(len(combos))

            rows.append(
                ResultRow(
                    pool_size=pool_size,
                    windows_tested=windows_tested,
                    windows_success=windows_success,
                    success_rate=windows_success / windows_tested if windows_tested else 0.0,
                    avg_days_to_success=statistics.mean(days_to_success) if days_to_success else None,
                    avg_tickets_per_day=(
                        float(args.tickets_per_day)
                        if args.objective == "topk"
                        else (statistics.mean(combo_counts) if combo_counts else None)
                    ),
                    avg_available_combos=statistics.mean(combo_counts) if combo_counts else None,
                )
            )

    # Console output
    print("=" * 80)
    print(
        f"BACKTEST Typ-6 Fenster: year={args.year}, window={args.window}, "
        f"objective={args.objective}, mode={args.mode}, pool_method={args.pool_method}"
    )
    if args.objective == "topk":
        print(f"tickets_per_day={args.tickets_per_day}")
    if args.objective == "pool_hits":
        print(f"min_hits={args.min_hits}")
    print("=" * 80)
    print()
    print(
        f"{'Pool':>4} {'Windows':>8} {'Erfolg':>8} {'Rate':>8} {'Ø Tage':>8} "
        f"{'Tickets/Tag':>11} {'Ø Kombis':>9}"
    )
    print("-" * 80)
    for r in rows:
        avg_days = f"{r.avg_days_to_success:.1f}" if r.avg_days_to_success is not None else "-"
        avg_tickets = f"{r.avg_tickets_per_day:.0f}" if r.avg_tickets_per_day is not None else "-"
        avg_combos = f"{r.avg_available_combos:.0f}" if r.avg_available_combos is not None else "-"
        print(
            f"{r.pool_size:>4} {r.windows_tested:>8} {r.windows_success:>8} "
            f"{r.success_rate*100:>7.1f}% {avg_days:>8} {avg_tickets:>11} {avg_combos:>9}"
        )

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = base_path / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "params": {
                "year": args.year,
                "window": args.window,
                "objective": args.objective,
                "mode": args.mode,
                "tickets_per_day": args.tickets_per_day if args.objective == "topk" else None,
                "pool_sizes": pool_sizes,
                "min_history": args.min_history,
                "min_hits": args.min_hits if args.objective == "pool_hits" else None,
            },
            "rows": [r.__dict__ for r in rows],
            "details": details,
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"JSON gespeichert: {out_path}")


if __name__ == "__main__":
    main()
