#!/usr/bin/env python3
"""Train->Validate->Test backtest with frozen position rules (no leakage).

Goal
----
Use *yesterday's ordered positions* as triggers, mine next-day inclusion/exclusion
rules on a TRAIN slice, validate them on a VALIDATION slice, then apply the
resulting rule set (frozen) on a TEST slice.

This implements the Axiom-First requirement: rules are NOT mined on the test
period and are not adapted during test.

Model
-----
Baseline ranking: weighted frequency P(number in next draw)
Rule layer: apply frozen position rules (exclude/include) to adjust scores

Metrics
-------
- ROI (fixed quotes per 1 EUR)
- mean hits
- near-miss / jackpot counts
- big-win counts (payout >= threshold)

Usage:
  python scripts/backtest_frozen_position_rules.py --output results/frozen_posrules_2025.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
from scipy import stats

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.core.keno_quotes import get_fixed_quote
from kenobase.prediction.position_rule_layer import (
    BASE_ABSENCE,
    BASE_PRESENCE,
    RuleFiring,
    RollingPositionRuleMiner,
    apply_rule_layer_to_scores,
    extract_ordered_keno_numbers,
    wilson_lower_bound,
)


@dataclass(frozen=True)
class FrozenRule:
    trigger_number: int
    trigger_position: int
    kind: str  # "exclude" / "include"
    predicted_number: int
    # Calibrated on validation (more conservative)
    support: int
    probability: float
    lower_bound: float


@dataclass(frozen=True)
class DayOutcome:
    date: str
    ticket: list[int]
    hits: int
    payout: float


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Frozen position rules backtest (train->val->test)")
    p.add_argument("--draws", default="data/raw/keno/KENO_ab_2022_bereinigt.csv")
    p.add_argument("--train-end", default="2023-12-31")
    p.add_argument("--val-end", default="2024-12-31")
    p.add_argument("--test-start", default="2025-01-01")
    p.add_argument("--types", type=int, nargs="*", default=[6, 7, 8, 9, 10])

    p.add_argument("--recent-draws", type=int, default=365)
    p.add_argument("--recent-weight", type=float, default=0.6)

    p.add_argument("--train-min-support", type=int, default=10)
    p.add_argument("--val-min-support", type=int, default=10)
    p.add_argument("--exclude-lb-train", type=float, default=0.80)
    p.add_argument("--include-lb-train", type=float, default=0.33)
    p.add_argument("--exclude-lb-val", type=float, default=0.78)
    p.add_argument("--include-lb-val", type=float, default=0.31)
    p.add_argument("--exclude-max", type=int, default=3)
    p.add_argument("--include-max", type=int, default=5)
    p.add_argument("--z", type=float, default=1.959963984540054)  # ~95%

    p.add_argument("--hard-exclude-lb", type=float, default=0.95)
    p.add_argument("--exclude-weight", type=float, default=2.0)
    p.add_argument("--include-weight", type=float, default=1.0)

    p.add_argument("--big-win-threshold", type=float, default=400.0)
    p.add_argument(
        "--selection",
        choices=["topk", "ev", "bigwin"],
        default="topk",
        help=(
            "Ticket-Selektion: topk=Top-k nach P(n) (default), "
            "ev=greedy Maximierung Expected Value (Paytable-aware), "
            "bigwin=greedy Maximierung P(payout>=threshold)"
        ),
    )
    p.add_argument("--output", default="results/frozen_position_rules_backtest.json")
    return p.parse_args()


def _date(x: str) -> datetime:
    return datetime.fromisoformat(x)


def _is_train(target_date: datetime, train_end: datetime) -> bool:
    return target_date <= train_end


def _is_val(target_date: datetime, train_end: datetime, val_end: datetime) -> bool:
    return train_end < target_date <= val_end


def _is_test(target_date: datetime, test_start: datetime) -> bool:
    return target_date >= test_start


def _add_draw_to_counts(
    draw_numbers: Iterable[int],
    *,
    all_counts: dict[int, int],
    recent_q: deque[set[int]],
    recent_counts: dict[int, int],
    total_draws_seen: int,
    recent_draws: int,
) -> int:
    nums = set(int(x) for x in draw_numbers)
    total_draws_seen += 1
    for n in nums:
        all_counts[n] += 1

    if recent_draws > 0:
        recent_q.append(nums)
        for n in nums:
            recent_counts[n] += 1
        while len(recent_q) > recent_draws:
            old = recent_q.popleft()
            for n in old:
                recent_counts[n] -= 1

    return total_draws_seen


def _weighted_frequency_scores(
    *,
    all_counts: dict[int, int],
    total_draws_seen: int,
    recent_counts: dict[int, int],
    recent_seen: int,
    recent_weight: float,
) -> np.ndarray:
    scores = np.zeros(71, dtype=float)
    if total_draws_seen <= 0:
        return scores

    if recent_seen > 0:
        for n in range(1, 71):
            freq_all = all_counts[n] / total_draws_seen
            freq_recent = recent_counts[n] / recent_seen
            scores[n] = recent_weight * freq_recent + (1.0 - recent_weight) * freq_all
    else:
        for n in range(1, 71):
            scores[n] = all_counts[n] / total_draws_seen
    return scores


def _rank(score: np.ndarray) -> list[int]:
    numbers = list(range(1, 71))
    numbers.sort(key=lambda n: (-float(score[n]), n))
    return numbers


def _poisson_binomial_pmf(probabilities: list[float]) -> list[float]:
    """Exact Poisson-binomial PMF via DP (k<=10)."""
    k = len(probabilities)
    pmf = [1.0] + [0.0] * k
    for p in probabilities:
        p = float(min(1.0, max(0.0, p)))
        for h in range(k, 0, -1):
            pmf[h] = pmf[h] * (1.0 - p) + pmf[h - 1] * p
        pmf[0] *= 1.0 - p
    # Numerical stability
    s = sum(pmf)
    if s > 0:
        pmf = [x / s for x in pmf]
    return pmf


def _ticket_score(
    *,
    ticket: list[int],
    p_presence: np.ndarray,
    keno_type: int,
    objective: str,
    threshold: float,
) -> float:
    ps = [float(p_presence[int(n)]) for n in ticket]
    pmf = _poisson_binomial_pmf(ps)

    if objective == "ev":
        return float(sum(pmf[h] * get_fixed_quote(keno_type, h) for h in range(len(pmf))))
    if objective == "bigwin":
        return float(
            sum(pmf[h] for h in range(len(pmf)) if get_fixed_quote(keno_type, h) >= float(threshold))
        )
    # topk is not scored (handled elsewhere)
    raise ValueError(f"Unsupported objective: {objective}")


def _select_ticket_greedy(
    *,
    p_presence: np.ndarray,
    keno_type: int,
    k: int,
    objective: str,
    threshold: float,
) -> list[int]:
    chosen: list[int] = []
    available = list(range(1, 71))
    for _ in range(int(k)):
        best_n: Optional[int] = None
        best_score = -1.0
        for n in available:
            if n in chosen:
                continue
            cand = chosen + [int(n)]
            score = _ticket_score(
                ticket=cand,
                p_presence=p_presence,
                keno_type=keno_type,
                objective=objective,
                threshold=threshold,
            )
            if score > best_score or (score == best_score and (best_n is None or n < best_n)):
                best_score = score
                best_n = int(n)
        if best_n is None:
            break
        chosen.append(best_n)

    return sorted(chosen)


def _mine_train_rules(
    draws: list[DrawResult],
    *,
    train_end: datetime,
    min_support: int,
    exclude_lb: float,
    include_lb: float,
    exclude_max: int,
    include_max: int,
    z: float,
) -> list[RuleFiring]:
    # Mine from (prev -> curr) transitions where curr.date is within TRAIN.
    transitions = [(draws[i - 1], draws[i]) for i in range(1, len(draws)) if _is_train(draws[i].date, train_end)]
    miner = RollingPositionRuleMiner(window_size=max(1, len(transitions)))

    for prev, curr in transitions:
        miner.add_transition(today_ordered=extract_ordered_keno_numbers(prev), tomorrow_numbers=curr.numbers)

    # Enumerate all triggers by iterating observed triggers in train transitions (reduces work).
    seen_triggers: set[tuple[int, int]] = set()
    for prev, _ in transitions:
        ordered = extract_ordered_keno_numbers(prev)
        for pos, num in enumerate(ordered, start=1):
            seen_triggers.add((int(num), int(pos)))

    rules: list[RuleFiring] = []
    for trig_num, trig_pos in sorted(seen_triggers):
        if miner.trigger_support(trig_num, trig_pos) < min_support:
            continue

        for cand in miner.exclusion_candidates(
            trigger_number=trig_num,
            trigger_position=trig_pos,
            max_candidates=exclude_max,
            min_support=min_support,
            min_lower_bound=exclude_lb,
            z=z,
        ):
            rules.append(
                RuleFiring(
                    trigger_number=trig_num,
                    trigger_position=trig_pos,
                    kind="exclude",
                    predicted_number=int(cand.number),
                    probability=float(cand.probability),
                    lower_bound=float(cand.lower_bound),
                    support=int(cand.support),
                )
            )

        for cand in miner.inclusion_candidates(
            trigger_number=trig_num,
            trigger_position=trig_pos,
            max_candidates=include_max,
            min_support=min_support,
            min_lower_bound=include_lb,
            z=z,
        ):
            rules.append(
                RuleFiring(
                    trigger_number=trig_num,
                    trigger_position=trig_pos,
                    kind="include",
                    predicted_number=int(cand.number),
                    probability=float(cand.probability),
                    lower_bound=float(cand.lower_bound),
                    support=int(cand.support),
                )
            )

    return rules


def _validate_rules(
    draws: list[DrawResult],
    *,
    train_end: datetime,
    val_end: datetime,
    candidates: list[RuleFiring],
    min_support: int,
    exclude_lb: float,
    include_lb: float,
    z: float,
) -> list[FrozenRule]:
    # Index candidates by trigger (num,pos) for fast firing.
    by_trigger: dict[tuple[int, int], list[RuleFiring]] = defaultdict(list)
    for r in candidates:
        by_trigger[(int(r.trigger_number), int(r.trigger_position))].append(r)

    # Count per-rule performance on validation transitions (prev -> curr) where curr.date is within VAL.
    stats_by_rule: dict[tuple[int, str, int, int], dict[str, int]] = defaultdict(lambda: {"t": 0, "c": 0})
    for i in range(1, len(draws)):
        curr = draws[i]
        if not _is_val(curr.date, train_end, val_end):
            continue
        prev = draws[i - 1]
        ordered = extract_ordered_keno_numbers(prev)
        curr_set = set(int(x) for x in curr.numbers)

        for pos, trig_num in enumerate(ordered, start=1):
            trig = (int(trig_num), int(pos))
            for r in by_trigger.get(trig, []):
                key = (int(r.trigger_number), str(r.kind), int(r.trigger_position), int(r.predicted_number))
                stats_by_rule[key]["t"] += 1
                if r.kind == "exclude":
                    stats_by_rule[key]["c"] += int(int(r.predicted_number) not in curr_set)
                else:
                    stats_by_rule[key]["c"] += int(int(r.predicted_number) in curr_set)

    frozen: list[FrozenRule] = []
    for (trig_num, kind, trig_pos, pred), v in stats_by_rule.items():
        t = int(v["t"])
        c = int(v["c"])
        if t < min_support:
            continue

        p = c / t
        lb = wilson_lower_bound(c, t, z=z)
        if kind == "exclude" and lb < exclude_lb:
            continue
        if kind == "include" and lb < include_lb:
            continue

        frozen.append(
            FrozenRule(
                trigger_number=int(trig_num),
                trigger_position=int(trig_pos),
                kind=str(kind),
                predicted_number=int(pred),
                support=int(t),
                probability=float(p),
                lower_bound=float(lb),
            )
        )

    return frozen


def _null_probability_big_win(*, keno_type: int, threshold: float) -> float:
    probs = KENO_PROBABILITIES.get(int(keno_type), {})
    p = 0.0
    for hits, ph in probs.items():
        if get_fixed_quote(keno_type, int(hits)) >= float(threshold):
            p += float(ph)
    return float(p)


def _summarize_outcomes(*, keno_type: int, outcomes: list[DayOutcome], threshold: float) -> dict[str, Any]:
    n = len(outcomes)
    invested = int(n)
    won = float(sum(o.payout for o in outcomes))
    roi = float(((won - invested) / invested) * 100.0) if invested > 0 else 0.0

    hits = [o.hits for o in outcomes]
    payouts = [o.payout for o in outcomes]

    near_hits = int(keno_type - 1)
    jack_hits = int(keno_type)
    near_count = int(sum(1 for h in hits if h == near_hits))
    jack_count = int(sum(1 for h in hits if h == jack_hits))
    big_count = int(sum(1 for p in payouts if p >= threshold))

    p_near = float(KENO_PROBABILITIES.get(int(keno_type), {}).get(near_hits, 0.0))
    p_jack = float(KENO_PROBABILITIES.get(int(keno_type), {}).get(jack_hits, 0.0))
    p_big = _null_probability_big_win(keno_type=keno_type, threshold=threshold)

    def _pval(k: int, p0: float) -> Optional[float]:
        if n <= 0:
            return None
        if not 0.0 <= p0 <= 1.0:
            return None
        return float(stats.binomtest(k, n=n, p=p0).pvalue)

    return {
        "n_days": n,
        "invested_eur": invested,
        "won_eur": round(won, 2),
        "profit_eur": round(won - invested, 2),
        "roi_percent": round(roi, 2),
        "mean_payout_per_eur": round((won / invested) if invested > 0 else 0.0, 4),
        "mean_hits": round(float(np.mean(hits)) if hits else 0.0, 4),
        "near_miss": {
            "hits": near_hits,
            "count": near_count,
            "expected": round(p_near * n, 3),
            "p_value": _pval(near_count, p_near),
        },
        "jackpot": {
            "hits": jack_hits,
            "count": jack_count,
            "expected": round(p_jack * n, 3),
            "p_value": _pval(jack_count, p_jack),
        },
        "big_win": {
            "threshold_eur": float(threshold),
            "count": big_count,
            "expected": round(p_big * n, 3),
            "p_value": _pval(big_count, p_big),
            "max_payout_eur": round(float(max(payouts)) if payouts else 0.0, 2),
        },
    }


def _tail(xs: list[DayOutcome], window: int) -> list[DayOutcome]:
    return xs[-window:] if window > 0 and len(xs) > window else xs


def main() -> int:
    args = _parse_args()

    train_end = _date(args.train_end)
    val_end = _date(args.val_end)
    test_start = _date(args.test_start)

    if not (train_end < val_end < test_start):
        raise ValueError("Need train_end < val_end < test_start")

    loader = DataLoader()
    draws = [d for d in loader.load(args.draws) if d.game_type == GameType.KENO]
    draws = sorted(draws, key=lambda d: d.date)
    if len(draws) < 2:
        raise ValueError("Need at least 2 draws")

    # --- Mine rules on TRAIN ---
    train_candidates = _mine_train_rules(
        draws,
        train_end=train_end,
        min_support=int(args.train_min_support),
        exclude_lb=float(args.exclude_lb_train),
        include_lb=float(args.include_lb_train),
        exclude_max=int(args.exclude_max),
        include_max=int(args.include_max),
        z=float(args.z),
    )

    # --- Validate rules on VAL and freeze ---
    frozen_rules = _validate_rules(
        draws,
        train_end=train_end,
        val_end=val_end,
        candidates=train_candidates,
        min_support=int(args.val_min_support),
        exclude_lb=float(args.exclude_lb_val),
        include_lb=float(args.include_lb_val),
        z=float(args.z),
    )

    # Index frozen rules for firing.
    frozen_by_trigger: dict[tuple[int, int], list[FrozenRule]] = defaultdict(list)
    for r in frozen_rules:
        frozen_by_trigger[(int(r.trigger_number), int(r.trigger_position))].append(r)

    # --- Walk-forward backtest on TEST ---
    all_counts = {n: 0 for n in range(1, 71)}
    recent_counts = {n: 0 for n in range(1, 71)}
    recent_q: deque[set[int]] = deque()
    total_draws_seen = 0

    # Seed history with first draw
    total_draws_seen = _add_draw_to_counts(
        draws[0].numbers,
        all_counts=all_counts,
        recent_q=recent_q,
        recent_counts=recent_counts,
        total_draws_seen=total_draws_seen,
        recent_draws=int(args.recent_draws),
    )

    by_type_outcomes_baseline: dict[int, list[DayOutcome]] = {int(k): [] for k in args.types}
    by_type_outcomes_rules: dict[int, list[DayOutcome]] = {int(k): [] for k in args.types}

    for i in range(1, len(draws)):
        prev = draws[i - 1]
        curr = draws[i]

        # Build scores from history up to prev (exclude curr draw).
        base_scores = _weighted_frequency_scores(
            all_counts=all_counts,
            total_draws_seen=total_draws_seen,
            recent_counts=recent_counts,
            recent_seen=len(recent_q),
            recent_weight=float(args.recent_weight),
        )

        ordered_prev = extract_ordered_keno_numbers(prev)
        fired_ex: list[RuleFiring] = []
        fired_in: list[RuleFiring] = []
        for pos, trig_num in enumerate(ordered_prev, start=1):
            for r in frozen_by_trigger.get((int(trig_num), int(pos)), []):
                firing = RuleFiring(
                    trigger_number=int(r.trigger_number),
                    trigger_position=int(r.trigger_position),
                    kind=str(r.kind),
                    predicted_number=int(r.predicted_number),
                    probability=float(r.probability),
                    lower_bound=float(r.lower_bound),
                    support=int(r.support),
                )
                if r.kind == "exclude":
                    fired_ex.append(firing)
                else:
                    fired_in.append(firing)

        adjusted_scores, _, _ = apply_rule_layer_to_scores(
            base_scores,
            exclusions=fired_ex,
            inclusions=fired_in,
            hard_exclude=True,
            hard_exclude_lb=float(args.hard_exclude_lb),
            exclude_weight=float(args.exclude_weight),
            include_weight=float(args.include_weight),
        )

        # Evaluate if this is a TEST day (target date in test period).
        if _is_test(curr.date, test_start):
            curr_set = set(int(x) for x in curr.numbers)

            selection = str(args.selection)
            if selection == "topk":
                ranked_base = _rank(base_scores)
                ranked_adj = _rank(adjusted_scores)
            else:
                ranked_base = []
                ranked_adj = []

            # For paytable-aware objectives we need probabilities in [0,1].
            p_base_arr = np.clip(base_scores, 0.0, 1.0)
            p_adj_arr = np.clip(np.exp(adjusted_scores), 0.0, 1.0)

            for keno_type in sorted(set(int(x) for x in args.types)):
                if selection == "topk":
                    t_base = ranked_base[:keno_type]
                    t_adj = ranked_adj[:keno_type]
                else:
                    t_base = _select_ticket_greedy(
                        p_presence=p_base_arr,
                        keno_type=keno_type,
                        k=keno_type,
                        objective=selection,
                        threshold=float(args.big_win_threshold),
                    )
                    t_adj = _select_ticket_greedy(
                        p_presence=p_adj_arr,
                        keno_type=keno_type,
                        k=keno_type,
                        objective=selection,
                        threshold=float(args.big_win_threshold),
                    )

                h_base = int(len(set(t_base) & curr_set))
                payout_base = float(get_fixed_quote(keno_type, h_base))
                by_type_outcomes_baseline[keno_type].append(
                    DayOutcome(date=str(curr.date.date()), ticket=t_base, hits=h_base, payout=payout_base)
                )

                h_adj = int(len(set(t_adj) & curr_set))
                payout_adj = float(get_fixed_quote(keno_type, h_adj))
                by_type_outcomes_rules[keno_type].append(
                    DayOutcome(date=str(curr.date.date()), ticket=t_adj, hits=h_adj, payout=payout_adj)
                )

        # Update history with curr draw for next step.
        total_draws_seen = _add_draw_to_counts(
            curr.numbers,
            all_counts=all_counts,
            recent_q=recent_q,
            recent_counts=recent_counts,
            total_draws_seen=total_draws_seen,
            recent_draws=int(args.recent_draws),
        )

    by_type: dict[str, Any] = {}
    for keno_type in sorted(set(int(x) for x in args.types)):
        base = by_type_outcomes_baseline[keno_type]
        rules = by_type_outcomes_rules[keno_type]

        overall = {
            "baseline_weighted_frequency": _summarize_outcomes(
                keno_type=keno_type, outcomes=base, threshold=float(args.big_win_threshold)
            ),
            "frozen_rules": _summarize_outcomes(
                keno_type=keno_type, outcomes=rules, threshold=float(args.big_win_threshold)
            ),
        }
        overall["delta"] = {
            "roi_percent": round(overall["frozen_rules"]["roi_percent"] - overall["baseline_weighted_frequency"]["roi_percent"], 2),
            "big_win_count": int(overall["frozen_rules"]["big_win"]["count"] - overall["baseline_weighted_frequency"]["big_win"]["count"]),
        }

        windows = {}
        for w in [30, 90, 180, 365]:
            windows[str(w)] = {
                "baseline_weighted_frequency": _summarize_outcomes(
                    keno_type=keno_type,
                    outcomes=_tail(base, w),
                    threshold=float(args.big_win_threshold),
                ),
                "frozen_rules": _summarize_outcomes(
                    keno_type=keno_type,
                    outcomes=_tail(rules, w),
                    threshold=float(args.big_win_threshold),
                ),
            }

        by_type[f"typ_{keno_type}"] = {
            "overall": overall,
            "windows": windows,
            "last_ticket_baseline": base[-1].ticket if base else [],
            "last_ticket_frozen": rules[-1].ticket if rules else [],
        }

    payload = {
        "analysis": "frozen_position_rules_backtest",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "draws_path": args.draws,
            "train_end": args.train_end,
            "val_end": args.val_end,
            "test_start": args.test_start,
            "types": [int(x) for x in args.types],
            "recent_draws": int(args.recent_draws),
            "recent_weight": float(args.recent_weight),
            "train_min_support": int(args.train_min_support),
            "val_min_support": int(args.val_min_support),
            "exclude_lb_train": float(args.exclude_lb_train),
            "include_lb_train": float(args.include_lb_train),
            "exclude_lb_val": float(args.exclude_lb_val),
            "include_lb_val": float(args.include_lb_val),
            "exclude_max": int(args.exclude_max),
            "include_max": int(args.include_max),
            "hard_exclude_lb": float(args.hard_exclude_lb),
            "exclude_weight": float(args.exclude_weight),
            "include_weight": float(args.include_weight),
            "big_win_threshold": float(args.big_win_threshold),
            "selection": str(args.selection),
        },
        "rules": {
            "candidates_train": len(train_candidates),
            "frozen_after_val": len(frozen_rules),
            "baseline_presence": BASE_PRESENCE,
            "baseline_absence": BASE_ABSENCE,
        },
        "by_type": by_type,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {args.output}")

    print("\n" + "=" * 90)
    print(f"Frozen position rules (train<= {args.train_end}, val<= {args.val_end}, test>= {args.test_start})")
    print(f"Rules: candidates={len(train_candidates)} -> frozen={len(frozen_rules)}")
    print("=" * 90)
    for k in sorted(by_type.keys()):
        o = by_type[k]["overall"]
        b = o["baseline_weighted_frequency"]["roi_percent"]
        r = o["frozen_rules"]["roi_percent"]
        print(f"{k}: ROI baseline={b:+.2f}% vs frozen={r:+.2f}% (delta {o['delta']['roi_percent']:+.2f}pp)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
