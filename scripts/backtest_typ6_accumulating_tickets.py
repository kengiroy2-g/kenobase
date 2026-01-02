#!/usr/bin/env python3
"""
BACKTEST: Typ-6 (6/6) mit "akkumulierenden Tickets" ueber X Tage.

Strategie (wie beschrieben):
  - Jeden Tag wird ein neues Typ-6 Ticket aus einem NEUEN Pool generiert (ohne Lookahead).
  - Alle bisher generierten Tickets bleiben bis zum Ende des X-Tage-Zeitraums aktiv
    (d.h. am Tag 30 werden bis zu 30 Tickets parallel gespielt).
  - Nach X Tagen werden alle Tickets gestoppt.

Auswertung:
  - Wir starten eine X-Tage-"Kampagne" an jedem moeglichen Starttag im Jahr (rolling starts),
    und messen: Gibt es mindestens 1 echten 6/6 Treffer innerhalb des Fensters?

Hinweis:
  - Ein "pool_hits >= 6" ist KEIN 6/6-Gewinn, wenn du nicht exakt die gezogenen 6 Zahlen gespielt hast.
  - Dieses Script prueft echte 6/6 Treffer: ticket ⊆ drawn(20).
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_optimized_tickets import (  # noqa: E402
    build_reduced_pool,
    filter_combinations,
    get_hot_numbers,
    load_keno_data,
    score_combination,
)


@dataclass(frozen=True)
class CampaignResult:
    start_idx: int
    success: bool
    day_to_first_win: Optional[int]
    tickets_generated: int


def _parse_pool_sizes(value: str) -> list[int]:
    parts = [p.strip() for p in value.split(",") if p.strip()]
    sizes = [int(p) for p in parts]
    if not sizes:
        raise ValueError("pool-sizes darf nicht leer sein")
    if any(s <= 0 or s > 70 for s in sizes):
        raise ValueError("pool-sizes muessen zwischen 1 und 70 liegen")
    return sizes


def _to_mask(numbers: tuple[int, ...]) -> int:
    mask = 0
    for n in numbers:
        mask |= 1 << n
    return mask


def _choose_ticket(
    *,
    train_draws: list[dict],
    pool_size: int,
    strict: bool,
    selection: str,
    rng: random.Random,
    top_random_n: int,
) -> tuple[Optional[tuple[int, ...]], int]:
    pool, _details = build_reduced_pool(train_draws, target_size=pool_size)
    hot = get_hot_numbers(train_draws, lookback=3)

    if strict:
        params = dict(
            min_decades=5,
            nbd_ratio_range=(0.45, 0.55),
            no_consecutive=True,
            hot_count=2,
            sum_range=(150, 250),
        )
    else:
        params = dict(
            min_decades=4,
            nbd_ratio_range=(0.33, 0.67),
            no_consecutive=True,
            hot_count=2,
            sum_range=(100, 300),
        )

    combos = filter_combinations(pool, hot, ticket_size=6, **params)
    if not combos:
        combos = filter_combinations(
            pool,
            hot,
            ticket_size=6,
            min_decades=3,
            nbd_ratio_range=(0.2, 0.8),
            no_consecutive=True,
            hot_count=None,
            sum_range=(50, 350),
        )

    if not combos:
        return None, 0

    if selection == "random":
        return tuple(rng.choice(combos)), len(combos)

    ranked = sorted(combos, key=lambda c: score_combination(c, hot), reverse=True)
    if selection == "top1":
        return tuple(ranked[0]), len(combos)
    if selection == "top_random":
        k = min(max(1, top_random_n), len(ranked))
        return tuple(rng.choice(ranked[:k])), len(combos)

    raise ValueError(f"Unknown selection: {selection}")


def _compute_campaign_results(
    *,
    draws: list[dict],
    year: int,
    window: int,
    pool_size: int,
    strict: bool,
    selection: str,
    top_random_n: int,
    seed: int,
    min_history: int,
) -> tuple[list[CampaignResult], dict]:
    rng = random.Random(seed)

    indices = [i for i, d in enumerate(draws) if d["datum"].year == year]
    if not indices:
        raise ValueError(f"Keine Ziehungen fuer Jahr {year} gefunden")

    draw_masks = {i: _to_mask(tuple(sorted(draws[i]["zahlen"]))) for i in indices}

    # Precompute daily ticket (lookahead-free) for the whole year for this pool_size.
    ticket_masks: dict[int, Optional[int]] = {}
    combo_counts: dict[int, int] = {}
    tickets_generated = 0

    for idx in indices:
        if idx < min_history:
            ticket_masks[idx] = None
            combo_counts[idx] = 0
            continue

        train = draws[:idx]
        ticket, n_combos = _choose_ticket(
            train_draws=train,
            pool_size=pool_size,
            strict=strict,
            selection=selection,
            rng=rng,
            top_random_n=top_random_n,
        )
        combo_counts[idx] = n_combos
        if ticket is None:
            ticket_masks[idx] = None
            continue
        ticket_masks[idx] = _to_mask(ticket)
        tickets_generated += 1

    # Campaign starts: every possible day where the full window stays inside the year.
    starts: list[int] = []
    for s in indices:
        if s < min_history:
            continue
        end_idx = s + window - 1
        if end_idx >= len(draws):
            continue
        if draws[end_idx]["datum"].year != year:
            continue
        starts.append(s)

    results: list[CampaignResult] = []
    for s in starts:
        active: list[int] = []
        success = False
        day_to_first_win: Optional[int] = None
        generated_in_campaign = 0

        for offset in range(window):
            idx = s + offset
            tm = ticket_masks.get(idx)
            if tm is not None:
                active.append(tm)
                generated_in_campaign += 1

            dmask = draw_masks[idx]
            for t in active:
                if (t & dmask) == t:
                    success = True
                    day_to_first_win = offset + 1
                    break
            if success:
                break

        results.append(
            CampaignResult(
                start_idx=s,
                success=success,
                day_to_first_win=day_to_first_win,
                tickets_generated=generated_in_campaign,
            )
        )

    meta = {
        "starts_tested": len(starts),
        "tickets_generated_in_year": tickets_generated,
        "avg_filtered_combos_per_day": statistics.mean(
            [combo_counts[i] for i in indices if i >= min_history]
        )
        if any(i >= min_history for i in indices)
        else 0.0,
    }
    return results, meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest: Typ-6 mit akkumulierenden Tickets")
    parser.add_argument("--year", type=int, default=2025, help="Jahr (Default: 2025)")
    parser.add_argument("--window", type=int, default=30, help="Kampagnenlaenge in Tagen (Default: 30)")
    parser.add_argument("--pool-sizes", type=str, default="10,11,12,13,14,15,16,17")
    parser.add_argument("--strict", action="store_true", help="Strenge Filter (wie generator --strict)")
    parser.add_argument(
        "--selection",
        choices=["top1", "top_random", "random"],
        default="top1",
        help="Wie das Tages-Ticket aus dem Pool gewaehlt wird (Default: top1)",
    )
    parser.add_argument(
        "--top-random-n",
        type=int,
        default=50,
        help="Nur fuer selection=top_random: Auswahl zufaellig aus Top-N (Default: 50)",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed fuer random/top_random (Default: 0)")
    parser.add_argument("--min-history", type=int, default=60, help="Min Historie fuer Prognose (Default: 60)")
    parser.add_argument("--output", type=str, default="", help="Optional: JSON output (Pfad relativ zum Repo-Root)")
    args = parser.parse_args()

    if args.window <= 0:
        raise SystemExit("--window muss > 0 sein")

    pool_sizes = _parse_pool_sizes(args.pool_sizes)

    base_path = SCRIPTS_DIR.parent
    draws = load_keno_data(base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv")

    print("=" * 90)
    print(
        f"BACKTEST Typ-6 Akkumulierende Tickets: year={args.year}, window={args.window}, "
        f"strict={args.strict}, selection={args.selection}"
    )
    if args.selection == "top_random":
        print(f"top_random_n={args.top_random_n}, seed={args.seed}")
    if args.selection == "random":
        print(f"seed={args.seed}")
    print("=" * 90)
    print()

    rows = []
    payload_rows = []

    for pool_size in pool_sizes:
        campaign_results, meta = _compute_campaign_results(
            draws=draws,
            year=args.year,
            window=args.window,
            pool_size=pool_size,
            strict=args.strict,
            selection=args.selection,
            top_random_n=args.top_random_n,
            seed=args.seed,
            min_history=args.min_history,
        )

        starts = meta["starts_tested"]
        wins = [r for r in campaign_results if r.success]
        win_days = [r.day_to_first_win for r in wins if r.day_to_first_win is not None]

        rate = (len(wins) / starts) if starts else 0.0
        avg_day = statistics.mean(win_days) if win_days else None
        med_day = statistics.median(win_days) if win_days else None

        rows.append(
            {
                "pool_size": pool_size,
                "starts": starts,
                "wins": len(wins),
                "success_rate": rate,
                "avg_day_to_win": avg_day,
                "median_day_to_win": med_day,
                "avg_filtered_combos_per_day": meta["avg_filtered_combos_per_day"],
            }
        )

        payload_rows.append(
            {
                "pool_size": pool_size,
                "starts_tested": starts,
                "wins": len(wins),
                "success_rate": rate,
                "avg_day_to_first_win": avg_day,
                "median_day_to_first_win": med_day,
                "avg_filtered_combos_per_day": meta["avg_filtered_combos_per_day"],
            }
        )

    print(f"{'Pool':>4} {'Starts':>7} {'Wins':>6} {'Rate':>8} {'Ø Tag':>8} {'Median':>8}")
    print("-" * 60)
    for r in rows:
        avg_day = f"{r['avg_day_to_win']:.1f}" if r["avg_day_to_win"] is not None else "-"
        med_day = f"{r['median_day_to_win']:.1f}" if r["median_day_to_win"] is not None else "-"
        print(
            f"{r['pool_size']:>4} {r['starts']:>7} {r['wins']:>6} "
            f"{r['success_rate']*100:>7.1f}% {avg_day:>8} {med_day:>8}"
        )

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = base_path / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_payload = {
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "params": {
                "year": args.year,
                "window": args.window,
                "pool_sizes": pool_sizes,
                "strict": args.strict,
                "selection": args.selection,
                "top_random_n": args.top_random_n if args.selection == "top_random" else None,
                "seed": args.seed if args.selection in {"random", "top_random"} else None,
                "min_history": args.min_history,
            },
            "rows": payload_rows,
        }
        out_path.write_text(json.dumps(out_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"JSON gespeichert: {out_path}")


if __name__ == "__main__":
    main()

