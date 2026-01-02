#!/usr/bin/env python3
"""Prev-day backtest (Vortag -> Heute) with rolling windows.

This script evaluates whether using yesterday's ordered draw (positions) to
adjust tickets improves outcomes versus a static baseline ticket.

It reports:
- ROI (fixed quotes per 1 EUR)
- hit counts (near-miss / jackpot)
- "big win" frequency (payout >= threshold, default 400 EUR)
- summaries over last 30 / 90 / 180 / 365 draws

Usage examples:
  python scripts/backtest_prevday_windows.py --start-date 2025-01-01 --output results/prevday_windows_2025.json
  python scripts/backtest_prevday_windows.py --start-date 2024-01-01 --end-date 2024-12-31
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DataLoader, GameType
from kenobase.core.keno_quotes import get_fixed_quote

import dynamic_recommendation as dyn


@dataclass(frozen=True)
class DayResult:
    date: str
    ticket: list[int]
    hits: int
    payout: float


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prev-day backtest with rolling windows")
    parser.add_argument(
        "--draws",
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="Pfad zur KENO-Ziehungsdatei (default: data/raw/keno/KENO_ab_2022_bereinigt.csv)",
    )
    parser.add_argument(
        "--types",
        type=int,
        nargs="*",
        default=[6, 7, 8, 9, 10],
        help="Keno-Typen (Anzahl Zahlen), z.B. --types 6 7 8 9 10",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2025-01-01",
        help="Startdatum inkl. (YYYY-MM-DD) fuer die Auswertung (default: 2025-01-01)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="Optionales Enddatum inkl. (YYYY-MM-DD). Default: letztes Datum im Datensatz.",
    )
    parser.add_argument(
        "--windows",
        type=int,
        nargs="*",
        default=[30, 90, 180, 365],
        help="Rolling Windows in Tagen/Draws (default: 30 90 180 365)",
    )
    parser.add_argument(
        "--big-win-threshold",
        type=float,
        default=400.0,
        help="Schwelle fuer 'Big Win' (EUR, default: 400)",
    )
    parser.add_argument(
        "--jackpot-file",
        type=str,
        default=None,
        help="Optional: GK1/GK10_10 CSV fuer Jackpot-Cooldown (z.B. Keno_GPTs/10-9_KGDaten_gefiltert.csv)",
    )
    parser.add_argument(
        "--cooldown-days",
        type=int,
        default=30,
        help="Cooldown-Tage nach Jackpot wenn --jackpot-file gesetzt ist (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/prevday_backtest_windows.json",
        help="Output JSON Pfad (default: results/prevday_backtest_windows.json)",
    )
    return parser.parse_args()


def _find_start_end_indices(dates: list[datetime], start_date: datetime, end_date: datetime) -> tuple[int, int]:
    start_idx = next((i for i, d in enumerate(dates) if d >= start_date), None)
    if start_idx is None:
        raise ValueError(f"start_date={start_date.date()} not found in dataset range")
    if start_idx < 1:
        raise ValueError("start_date must not be the first draw (needs previous day for context)")

    end_idx = max(i for i, d in enumerate(dates) if d <= end_date)
    if end_idx < start_idx:
        raise ValueError("end_date is before start_date in dataset")
    return int(start_idx), int(end_idx)


def _simulate_ticket(ticket: list[int], keno_type: int, draw_set: set[int]) -> tuple[int, float]:
    hits = int(len(set(ticket) & draw_set))
    payout = float(get_fixed_quote(keno_type, hits))
    return hits, payout


def _null_probability_big_win(*, keno_type: int, threshold: float) -> float:
    probs = KENO_PROBABILITIES.get(int(keno_type), {})
    p = 0.0
    for hits, ph in probs.items():
        if get_fixed_quote(keno_type, int(hits)) >= float(threshold):
            p += float(ph)
    return float(p)


def _summarize(
    *,
    keno_type: int,
    results: list[DayResult],
    threshold: float,
) -> dict[str, Any]:
    n = len(results)
    invested = int(n)
    won = float(sum(r.payout for r in results))
    roi = float(((won - invested) / invested) * 100.0) if invested > 0 else 0.0

    hits = [r.hits for r in results]
    payouts = [r.payout for r in results]

    big_win_count = int(sum(1 for p in payouts if p >= threshold))
    big_win_total = float(sum(p for p in payouts if p >= threshold))
    max_payout = float(max(payouts)) if payouts else 0.0

    near_miss_hits = int(keno_type - 1)
    jackpot_hits = int(keno_type)
    near_miss_count = int(sum(1 for h in hits if h == near_miss_hits))
    jackpot_count = int(sum(1 for h in hits if h == jackpot_hits))

    p_big = _null_probability_big_win(keno_type=keno_type, threshold=threshold)
    p_jack = float(KENO_PROBABILITIES.get(int(keno_type), {}).get(jackpot_hits, 0.0))
    p_near = float(KENO_PROBABILITIES.get(int(keno_type), {}).get(near_miss_hits, 0.0))

    def _binom_pval(k: int, p0: float) -> Optional[float]:
        if n <= 0:
            return None
        if not 0.0 <= p0 <= 1.0:
            return None
        return float(stats.binomtest(k, n=n, p=p0).pvalue)

    return {
        "n_days": int(n),
        "invested_eur": invested,
        "won_eur": round(won, 2),
        "profit_eur": round(won - invested, 2),
        "roi_percent": round(roi, 2),
        "mean_payout_per_eur": round((won / invested) if invested > 0 else 0.0, 4),
        "mean_hits": round(float(np.mean(hits)) if hits else 0.0, 4),
        "near_miss": {
            "hits": near_miss_hits,
            "count": near_miss_count,
            "expected": round(p_near * n, 3),
            "p_value": _binom_pval(near_miss_count, p_near),
        },
        "jackpot": {
            "hits": jackpot_hits,
            "count": jackpot_count,
            "expected": round(p_jack * n, 3),
            "p_value": _binom_pval(jackpot_count, p_jack),
        },
        "big_win": {
            "threshold_eur": float(threshold),
            "count": big_win_count,
            "expected": round(p_big * n, 3),
            "p_value": _binom_pval(big_win_count, p_big),
            "total_payout_eur": round(big_win_total, 2),
            "max_payout_eur": round(max_payout, 2),
        },
    }


def _tail(results: list[DayResult], window: int) -> list[DayResult]:
    if window <= 0:
        return results
    return results[-window:] if len(results) > window else results


def main() -> int:
    args = _parse_args()

    start_date = datetime.fromisoformat(args.start_date)
    end_date = datetime.fromisoformat(args.end_date) if args.end_date else None

    loader = DataLoader()
    draws = [d for d in loader.load(args.draws) if d.game_type == GameType.KENO]
    draws = sorted(draws, key=lambda d: d.date)
    if len(draws) < 2:
        raise ValueError("Need at least 2 draws for prev-day backtest")

    dates = [d.date for d in draws]
    if end_date is None:
        end_date = dates[-1]

    start_idx, end_idx = _find_start_end_indices(dates, start_date, end_date)

    jackpot_dates = None
    if args.jackpot_file:
        jackpot_dates = dyn.load_jackpot_dates(args.jackpot_file)

    by_type: dict[str, Any] = {}

    for keno_type in sorted(set(int(t) for t in args.types)):
        baseline_results: list[DayResult] = []
        dynamic_results: list[DayResult] = []

        base_ticket = dyn.OPTIMAL_TICKETS.get(int(keno_type))
        if not base_ticket:
            base_ticket = dyn.OPTIMAL_TICKETS[9][: int(keno_type)]

        for i in range(start_idx, end_idx + 1):
            prev = draws[i - 1]
            curr = draws[i]

            if jackpot_dates is not None:
                warning = dyn.check_jackpot_warning(curr.date, jackpot_dates, cooldown_days=int(args.cooldown_days))
                if warning.get("in_cooldown"):
                    continue

            prev_positions = prev.metadata.get("numbers_ordered") or list(prev.numbers)
            if not isinstance(prev_positions, list) or len(prev_positions) != 20:
                continue
            prev_set = set(int(x) for x in prev_positions)
            prev_absent = set(range(1, 71)) - prev_set

            draw_set = set(int(x) for x in curr.numbers)

            # Baseline: static ticket
            hits_b, payout_b = _simulate_ticket(list(base_ticket), int(keno_type), draw_set)
            baseline_results.append(
                DayResult(date=str(curr.date.date()), ticket=list(base_ticket), hits=hits_b, payout=payout_b)
            )

            # Dynamic: prev-day rule layer from scripts/dynamic_recommendation.py
            exclude = dyn.apply_exclusion_rules(prev_positions, verbose=False)
            boost = dyn.apply_inclusion_boost(prev_positions, verbose=False)
            likely_absent = dyn.apply_absence_correlations(prev_absent)
            ticket_dyn = dyn.generate_dynamic_ticket(int(keno_type), exclude, boost, likely_absent)

            hits_d, payout_d = _simulate_ticket(ticket_dyn, int(keno_type), draw_set)
            dynamic_results.append(
                DayResult(date=str(curr.date.date()), ticket=ticket_dyn, hits=hits_d, payout=payout_d)
            )

        overall = {
            "baseline": _summarize(keno_type=keno_type, results=baseline_results, threshold=args.big_win_threshold),
            "dynamic_prevday": _summarize(keno_type=keno_type, results=dynamic_results, threshold=args.big_win_threshold),
        }
        overall["delta"] = {
            "roi_percent": round(
                overall["dynamic_prevday"]["roi_percent"] - overall["baseline"]["roi_percent"], 2
            ),
            "big_win_count": int(
                overall["dynamic_prevday"]["big_win"]["count"] - overall["baseline"]["big_win"]["count"]
            ),
            "jackpot_count": int(
                overall["dynamic_prevday"]["jackpot"]["count"] - overall["baseline"]["jackpot"]["count"]
            ),
        }

        windows_summary: dict[str, Any] = {}
        for w in sorted(set(int(x) for x in args.windows)):
            windows_summary[str(w)] = {
                "baseline": _summarize(
                    keno_type=keno_type, results=_tail(baseline_results, w), threshold=args.big_win_threshold
                ),
                "dynamic_prevday": _summarize(
                    keno_type=keno_type, results=_tail(dynamic_results, w), threshold=args.big_win_threshold
                ),
            }

        by_type[f"typ_{keno_type}"] = {
            "ticket_baseline": list(base_ticket),
            "overall": overall,
            "windows": windows_summary,
        }

    payload = {
        "analysis": "prevday_backtest_windows",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "draws_path": args.draws,
            "start_date": args.start_date,
            "end_date": end_date.date().isoformat(),
            "types": [int(x) for x in args.types],
            "windows": [int(x) for x in args.windows],
            "big_win_threshold": float(args.big_win_threshold),
            "jackpot_file": args.jackpot_file,
            "cooldown_days": int(args.cooldown_days),
        },
        "by_type": by_type,
        "notes": {
            "quotes": "Fixed quotes per 1 EUR from kenobase/core/keno_quotes.py",
            "baseline": "Static OPTIMAL_TICKETS from scripts/dynamic_recommendation.py",
            "dynamic_prevday": "Same base ticket + prev-day exclusion/inclusion/absence rules",
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {args.output}")

    # Minimal console summary for quick scan
    print("\n" + "=" * 80)
    print(f"Prev-day backtest from {args.start_date} to {end_date.date().isoformat()}  (big_win>={args.big_win_threshold} EUR)")
    print("=" * 80)
    for key in sorted(by_type.keys()):
        o = by_type[key]["overall"]
        b = o["baseline"]
        d = o["dynamic_prevday"]
        print(
            f"{key}: ROI baseline={b['roi_percent']:+.2f}% vs dynamic={d['roi_percent']:+.2f}%  "
            f"bigwins {b['big_win']['count']}->{d['big_win']['count']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
