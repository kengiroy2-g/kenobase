#!/usr/bin/env python3
"""Backtest fixed KENO tickets, focusing on high-payout events.

This script is intentionally simple: given a set of fixed tickets (e.g. the
output of `results/all_class_groups.json`) and a draw file, it evaluates:
  - ROI over the selected period
  - count of payouts >= threshold (default: 400 EUR)

Examples:
  python scripts/backtest_high_payout_tickets.py --year 2025
  python scripts/backtest_high_payout_tickets.py --year 2025 --threshold 400 --top 20
  python scripts/backtest_high_payout_tickets.py --start-date 2023-01-01 --end-date 2024-02-15
  python scripts/backtest_high_payout_tickets.py --models results/all_class_groups.json results/group_recommendations.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.core.keno_quotes import get_fixed_quote


@dataclass(frozen=True)
class TicketSpec:
    ticket_id: str
    keno_type: int
    numbers: list[int]
    source: str
    strategy: str


@dataclass(frozen=True)
class HighWinEvent:
    date: str
    hits: int
    payout: float


@dataclass(frozen=True)
class TicketBacktest:
    ticket_id: str
    keno_type: int
    numbers: list[int]
    source: str
    strategy: str
    draws: int
    invested: float
    won: float
    roi: float
    high_payout_threshold: float
    high_payout_count: int
    high_payout_events: list[HighWinEvent]
    theoretical_p_high: Optional[float]


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_tickets_from_model_json(path: Path) -> list[TicketSpec]:
    payload = _load_json(path)
    source = str(path)
    tickets: list[TicketSpec] = []

    if isinstance(payload.get("groups_by_type"), dict):
        by_type = payload["groups_by_type"]
        for typ_key, strategies in by_type.items():
            if not isinstance(strategies, dict):
                continue
            keno_type = int(str(typ_key).replace("typ_", ""))
            for strategy_name, strategy_payload in strategies.items():
                if not isinstance(strategy_payload, dict):
                    continue
                nums = strategy_payload.get("numbers")
                if not isinstance(nums, list) or not nums:
                    continue
                ticket_id = f"{path.name}:{typ_key}:{strategy_name}"
                tickets.append(
                    TicketSpec(
                        ticket_id=ticket_id,
                        keno_type=keno_type,
                        numbers=[int(n) for n in nums],
                        source=source,
                        strategy=str(strategy_name),
                    )
                )
        return tickets

    if isinstance(payload.get("keno_types"), dict):
        by_type = payload["keno_types"]
        for typ_key, strategies in by_type.items():
            if not isinstance(strategies, dict):
                continue
            keno_type = int(str(typ_key).replace("typ_", ""))
            for strategy_name, strategy_payload in strategies.items():
                if not isinstance(strategy_payload, dict):
                    continue
                nums = strategy_payload.get("numbers")
                if not isinstance(nums, list) or not nums:
                    continue
                ticket_id = f"{path.name}:{typ_key}:{strategy_name}"
                tickets.append(
                    TicketSpec(
                        ticket_id=ticket_id,
                        keno_type=keno_type,
                        numbers=[int(n) for n in nums],
                        source=source,
                        strategy=str(strategy_name),
                    )
                )
        return tickets

    raise ValueError(
        f"Unsupported model JSON format in {path}. Expected keys: groups_by_type or keno_types."
    )


def _filter_draws(
    draws: Iterable[DrawResult],
    *,
    year: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list[DrawResult]:
    out: list[DrawResult] = []
    for d in draws:
        if d.game_type != GameType.KENO:
            continue
        dd = d.date.date()
        if year is not None and dd.year != year:
            continue
        if start_date is not None and dd < start_date:
            continue
        if end_date is not None and dd > end_date:
            continue
        out.append(d)
    out.sort(key=lambda x: x.date)
    return out


def _theoretical_p_high(*, keno_type: int, threshold: float) -> Optional[float]:
    probs = KENO_PROBABILITIES.get(int(keno_type))
    if not probs:
        return None
    p = 0.0
    for hits, ph in probs.items():
        if get_fixed_quote(keno_type, int(hits)) >= threshold:
            p += float(ph)
    return float(p)


def _backtest_one(
    draws: list[DrawResult],
    ticket: TicketSpec,
    *,
    threshold: float,
    max_events: int,
) -> TicketBacktest:
    if not draws:
        raise ValueError("No draws selected for backtest (check filters)")
    if len(ticket.numbers) != int(ticket.keno_type):
        raise ValueError(
            f"Ticket k mismatch for {ticket.ticket_id}: len(numbers)={len(ticket.numbers)} "
            f"but keno_type={ticket.keno_type}"
        )

    nums = list(ticket.numbers)
    invested = float(len(draws))
    won = 0.0
    high_events: list[HighWinEvent] = []
    high_count = 0

    for d in draws:
        draw_set = set(d.numbers)
        hits = sum(1 for n in nums if n in draw_set)
        payout = float(get_fixed_quote(ticket.keno_type, hits))
        won += payout
        if payout >= threshold:
            high_count += 1
            if len(high_events) < max_events:
                high_events.append(
                    HighWinEvent(date=str(d.date.date()), hits=int(hits), payout=float(payout))
                )

    roi = (won - invested) / invested if invested > 0 else 0.0

    return TicketBacktest(
        ticket_id=ticket.ticket_id,
        keno_type=int(ticket.keno_type),
        numbers=sorted(int(n) for n in nums),
        source=ticket.source,
        strategy=ticket.strategy,
        draws=int(len(draws)),
        invested=float(invested),
        won=float(won),
        roi=float(roi),
        high_payout_threshold=float(threshold),
        high_payout_count=int(high_count),
        high_payout_events=high_events,
        theoretical_p_high=_theoretical_p_high(keno_type=ticket.keno_type, threshold=threshold),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest fixed KENO tickets for high payouts")
    parser.add_argument(
        "--draws",
        type=str,
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="Pfad zur Ziehungs-CSV (default: data/raw/keno/KENO_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs="*",
        default=["results/all_class_groups.json", "results/group_recommendations.json"],
        help="JSON-Modelle die Tickets enthalten (default: results/all_class_groups.json results/group_recommendations.json)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="Filter auf Jahr (default: 2025, 0 = aus)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Optional: Startdatum YYYY-MM-DD",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="Optional: Enddatum YYYY-MM-DD",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=400.0,
        help="High-payout threshold in EUR (default: 400)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Wie viele Tickets pro Typ anzeigen (default: 20)",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=10,
        help="Max. High-Win Events pro Ticket im JSON (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/high_payout_backtest_2025.json",
        help="Output JSON (default: results/high_payout_backtest_2025.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    year = int(args.year) if int(args.year) != 0 else None
    start_date = _parse_date(args.start_date) if args.start_date else None
    end_date = _parse_date(args.end_date) if args.end_date else None

    loader = DataLoader()
    draws = loader.load(args.draws, game_type=GameType.KENO)
    draws = _filter_draws(draws, year=year, start_date=start_date, end_date=end_date)

    tickets: list[TicketSpec] = []
    for p in args.models:
        path = Path(p)
        if not path.exists():
            continue
        tickets.extend(_extract_tickets_from_model_json(path))

    if not tickets:
        raise ValueError("No tickets found (check --models paths)")

    # Backtest all tickets.
    results: list[TicketBacktest] = []
    for t in tickets:
        results.append(_backtest_one(draws, t, threshold=float(args.threshold), max_events=int(args.max_events)))

    # Group by type and rank.
    by_type: dict[int, list[TicketBacktest]] = {}
    for r in results:
        by_type.setdefault(int(r.keno_type), []).append(r)

    for k in sorted(by_type.keys()):
        by_type[k].sort(key=lambda x: (x.high_payout_count, x.roi), reverse=True)

    # Print summary.
    period = f"{draws[0].date.date()}..{draws[-1].date.date()}" if draws else "n/a"
    print("=" * 100)
    print("KENO High-Payout Backtest (fixed tickets)")
    print(f"Draws: {len(draws)}  Period: {period}  Threshold: {float(args.threshold):.0f} EUR")
    print("=" * 100)
    print()

    for k in sorted(by_type.keys()):
        print(f"Type {k}: top {int(args.top)}")
        for r in by_type[k][: int(args.top)]:
            p_high = r.theoretical_p_high
            p_high_s = f"{p_high*100:.4f}%" if p_high is not None else "n/a"
            print(
                f"  {r.high_payout_count:>3}x >= {int(r.high_payout_threshold):>3}  "
                f"ROI {r.roi*100:>+7.2f}%  1p={p_high_s:<9}  {r.ticket_id}"
            )
        print()

    payload = {
        "analysis": "keno_high_payout_ticket_backtest",
        "generated_at": datetime.now().isoformat(),
        "draws_path": str(args.draws),
        "filters": {
            "year": year,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        },
        "threshold": float(args.threshold),
        "tickets_tested": len(results),
        "draws": {
            "count": len(draws),
            "start_date": str(draws[0].date.date()) if draws else None,
            "end_date": str(draws[-1].date.date()) if draws else None,
        },
        "results": [asdict(r) for r in results],
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON geschrieben: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

