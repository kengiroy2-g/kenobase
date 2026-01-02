#!/usr/bin/env python3
"""Walk-Forward Lookback Period Grid Search with BH/FDR Correction.

Dedicated analysis to find optimal lookback period (recent_draws) for
position rule layer backtesting. Tests range: [30, 60, 90, 180, 365, 540, 730] days.

Implements Benjamini-Hochberg (BH) FDR correction for multiple testing
per CLAUDE.md Section 3.0 Axiom-First requirements.

Usage:
  python scripts/walk_forward_lookback_grid.py --output results/walk_forward_lookback_grid.json
  python scripts/walk_forward_lookback_grid.py --quick  # Reduced grid for testing
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
from scipy import stats

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.core.keno_quotes import get_fixed_quote
from kenobase.prediction.position_rule_layer import (
    RuleFiring,
    RollingPositionRuleMiner,
    apply_rule_layer_to_scores,
    extract_ordered_keno_numbers,
    wilson_lower_bound,
)


# Lookback periods to test (in days/draws)
LOOKBACK_GRID = [30, 60, 90, 180, 365, 540, 730]
LOOKBACK_GRID_QUICK = [90, 365, 730]


@dataclass(frozen=True)
class LookbackParams:
    """Parameter combination for lookback grid search."""

    recent_draws: int
    recent_weight: float = 0.6
    train_min_support: int = 10
    val_min_support: int = 10
    exclude_lb_train: float = 0.80
    include_lb_train: float = 0.33
    exclude_lb_val: float = 0.78
    include_lb_val: float = 0.31
    exclude_max: int = 3
    include_max: int = 5
    hard_exclude_lb: float = 0.95
    exclude_weight: float = 2.0
    include_weight: float = 1.0


@dataclass(frozen=True)
class FrozenRule:
    trigger_number: int
    trigger_position: int
    kind: str
    predicted_number: int
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
    p = argparse.ArgumentParser(description="Walk-Forward Lookback Grid Search with BH/FDR")
    p.add_argument("--draws", default="data/raw/keno/KENO_ab_2022_bereinigt.csv")
    p.add_argument("--train-end", default="2023-12-31")
    p.add_argument("--val-end", default="2024-12-31")
    p.add_argument("--test-start", default="2025-01-01")
    p.add_argument("--types", type=int, nargs="*", default=[6, 7, 8, 9, 10])
    p.add_argument("--quick", action="store_true", help="Reduced grid for testing")
    p.add_argument("--big-win-threshold", type=float, default=400.0)
    p.add_argument("--z", type=float, default=1.959963984540054)
    p.add_argument("--fdr-alpha", type=float, default=0.10, help="FDR threshold for BH correction")
    p.add_argument("--output", default="results/walk_forward_lookback_grid.json")
    return p.parse_args()


def _build_lookback_grid(quick: bool = False) -> list[LookbackParams]:
    """Build parameter grid focused on lookback periods.

    Full grid: 7 lookback periods
    Quick grid: 3 lookback periods for testing
    """
    lookbacks = LOOKBACK_GRID_QUICK if quick else LOOKBACK_GRID
    return [LookbackParams(recent_draws=lb) for lb in lookbacks]


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


def _mine_train_rules(
    draws: list[DrawResult],
    *,
    train_end: datetime,
    params: LookbackParams,
    z: float,
) -> list[RuleFiring]:
    transitions = [
        (draws[i - 1], draws[i]) for i in range(1, len(draws)) if _is_train(draws[i].date, train_end)
    ]
    miner = RollingPositionRuleMiner(window_size=max(1, len(transitions)))

    for prev, curr in transitions:
        miner.add_transition(today_ordered=extract_ordered_keno_numbers(prev), tomorrow_numbers=curr.numbers)

    seen_triggers: set[tuple[int, int]] = set()
    for prev, _ in transitions:
        ordered = extract_ordered_keno_numbers(prev)
        for pos, num in enumerate(ordered, start=1):
            seen_triggers.add((int(num), int(pos)))

    rules: list[RuleFiring] = []
    for trig_num, trig_pos in sorted(seen_triggers):
        if miner.trigger_support(trig_num, trig_pos) < params.train_min_support:
            continue

        for cand in miner.exclusion_candidates(
            trigger_number=trig_num,
            trigger_position=trig_pos,
            max_candidates=params.exclude_max,
            min_support=params.train_min_support,
            min_lower_bound=params.exclude_lb_train,
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
            max_candidates=params.include_max,
            min_support=params.train_min_support,
            min_lower_bound=params.include_lb_train,
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
    params: LookbackParams,
    z: float,
) -> list[FrozenRule]:
    by_trigger: dict[tuple[int, int], list[RuleFiring]] = defaultdict(list)
    for r in candidates:
        by_trigger[(int(r.trigger_number), int(r.trigger_position))].append(r)

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
        if t < params.val_min_support:
            continue

        p = c / t
        lb = wilson_lower_bound(c, t, z=z)
        if kind == "exclude" and lb < params.exclude_lb_val:
            continue
        if kind == "include" and lb < params.include_lb_val:
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

    big_count = int(sum(1 for p in payouts if p >= threshold))
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
        "mean_hits": round(float(np.mean(hits)) if hits else 0.0, 4),
        "big_win_count": big_count,
        "big_win_expected": round(p_big * n, 3),
        "big_win_pvalue": _pval(big_count, p_big),
    }


def _tail(xs: list[DayOutcome], window: int) -> list[DayOutcome]:
    return xs[-window:] if window > 0 and len(xs) > window else xs


def _run_single_lookback(
    draws: list[DrawResult],
    *,
    train_end: datetime,
    val_end: datetime,
    test_start: datetime,
    params: LookbackParams,
    keno_types: list[int],
    big_win_threshold: float,
    z: float,
) -> dict[str, Any]:
    """Run backtest for a single lookback period."""

    # Mine and validate rules
    train_candidates = _mine_train_rules(draws, train_end=train_end, params=params, z=z)
    frozen_rules = _validate_rules(
        draws, train_end=train_end, val_end=val_end, candidates=train_candidates, params=params, z=z
    )

    frozen_by_trigger: dict[tuple[int, int], list[FrozenRule]] = defaultdict(list)
    for r in frozen_rules:
        frozen_by_trigger[(int(r.trigger_number), int(r.trigger_position))].append(r)

    # Walk-forward on test
    all_counts = {n: 0 for n in range(1, 71)}
    recent_counts = {n: 0 for n in range(1, 71)}
    recent_q: deque[set[int]] = deque()
    total_draws_seen = 0

    total_draws_seen = _add_draw_to_counts(
        draws[0].numbers,
        all_counts=all_counts,
        recent_q=recent_q,
        recent_counts=recent_counts,
        total_draws_seen=total_draws_seen,
        recent_draws=params.recent_draws,
    )

    by_type_outcomes_baseline: dict[int, list[DayOutcome]] = {int(k): [] for k in keno_types}
    by_type_outcomes_rules: dict[int, list[DayOutcome]] = {int(k): [] for k in keno_types}

    for i in range(1, len(draws)):
        prev = draws[i - 1]
        curr = draws[i]

        base_scores = _weighted_frequency_scores(
            all_counts=all_counts,
            total_draws_seen=total_draws_seen,
            recent_counts=recent_counts,
            recent_seen=len(recent_q),
            recent_weight=params.recent_weight,
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
            hard_exclude_lb=params.hard_exclude_lb,
            exclude_weight=params.exclude_weight,
            include_weight=params.include_weight,
        )

        if _is_test(curr.date, test_start):
            curr_set = set(int(x) for x in curr.numbers)
            ranked_base = _rank(base_scores)
            ranked_adj = _rank(adjusted_scores)

            for keno_type in keno_types:
                t_base = ranked_base[:keno_type]
                t_adj = ranked_adj[:keno_type]

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

        total_draws_seen = _add_draw_to_counts(
            curr.numbers,
            all_counts=all_counts,
            recent_q=recent_q,
            recent_counts=recent_counts,
            total_draws_seen=total_draws_seen,
            recent_draws=params.recent_draws,
        )

    # Summarize results per keno_type
    by_type: dict[str, Any] = {}
    for keno_type in keno_types:
        base = by_type_outcomes_baseline[keno_type]
        rules = by_type_outcomes_rules[keno_type]

        overall_base = _summarize_outcomes(keno_type=keno_type, outcomes=base, threshold=big_win_threshold)
        overall_rules = _summarize_outcomes(keno_type=keno_type, outcomes=rules, threshold=big_win_threshold)

        delta_roi = overall_rules["roi_percent"] - overall_base["roi_percent"]
        delta_bigwin = overall_rules["big_win_count"] - overall_base["big_win_count"]

        windows: dict[str, Any] = {}
        for w in [30, 90, 180, 365]:
            w_base = _summarize_outcomes(keno_type=keno_type, outcomes=_tail(base, w), threshold=big_win_threshold)
            w_rules = _summarize_outcomes(keno_type=keno_type, outcomes=_tail(rules, w), threshold=big_win_threshold)
            windows[str(w)] = {
                "baseline_roi": w_base["roi_percent"],
                "rules_roi": w_rules["roi_percent"],
                "delta_roi": round(w_rules["roi_percent"] - w_base["roi_percent"], 2),
                "baseline_bigwin": w_base["big_win_count"],
                "rules_bigwin": w_rules["big_win_count"],
            }

        by_type[f"typ_{keno_type}"] = {
            "baseline_roi": overall_base["roi_percent"],
            "rules_roi": overall_rules["roi_percent"],
            "delta_roi": round(delta_roi, 2),
            "baseline_bigwin": overall_base["big_win_count"],
            "rules_bigwin": overall_rules["big_win_count"],
            "delta_bigwin": delta_bigwin,
            "big_win_pvalue": overall_rules["big_win_pvalue"],
            "windows": windows,
        }

    return {
        "lookback_days": params.recent_draws,
        "params": asdict(params),
        "rules_count": {"candidates": len(train_candidates), "frozen": len(frozen_rules)},
        "by_type": by_type,
    }


def _benjamini_hochberg(pvalues: list[Optional[float]], alpha: float = 0.10) -> list[bool]:
    """Apply Benjamini-Hochberg FDR correction.

    Returns list of booleans indicating which hypotheses are significant after correction.
    """
    n = len(pvalues)
    if n == 0:
        return []

    # Handle None values (mark as non-significant)
    valid_indices = [i for i, p in enumerate(pvalues) if p is not None]
    valid_pvalues = [pvalues[i] for i in valid_indices]

    if not valid_pvalues:
        return [False] * n

    # Sort by p-value
    sorted_indices = sorted(range(len(valid_pvalues)), key=lambda i: valid_pvalues[i])
    sorted_pvalues = [valid_pvalues[i] for i in sorted_indices]

    # BH procedure
    m = len(sorted_pvalues)
    thresholds = [(i + 1) * alpha / m for i in range(m)]

    # Find largest k where p[k] <= threshold[k]
    significant_count = 0
    for k in range(m - 1, -1, -1):
        if sorted_pvalues[k] <= thresholds[k]:
            significant_count = k + 1
            break

    # Mark significant
    significant_sorted = [i < significant_count for i in range(m)]

    # Map back to original order
    result = [False] * n
    for sorted_idx, orig_idx in enumerate(sorted_indices):
        result[valid_indices[orig_idx]] = significant_sorted[sorted_idx]

    return result


def main() -> int:
    args = _parse_args()
    start_time = time.time()

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

    lookback_grid = _build_lookback_grid(quick=args.quick)
    keno_types = [int(t) for t in args.types]

    print("Walk-Forward Lookback Period Grid Search")
    print(f"Lookback periods: {[p.recent_draws for p in lookback_grid]}")
    print(f"Keno types: {keno_types}")
    print(f"FDR alpha: {args.fdr_alpha}")
    print("=" * 80)

    # Run grid search
    results: list[dict[str, Any]] = []
    for idx, params in enumerate(lookback_grid):
        print(f"[{idx + 1}/{len(lookback_grid)}] Testing lookback={params.recent_draws} days")

        result = _run_single_lookback(
            draws,
            train_end=train_end,
            val_end=val_end,
            test_start=test_start,
            params=params,
            keno_types=keno_types,
            big_win_threshold=args.big_win_threshold,
            z=args.z,
        )
        results.append(result)

    # Collect all p-values for BH correction
    pvalue_list: list[tuple[int, int, str, Optional[float]]] = []
    for lb_idx, res in enumerate(results):
        for typ_key, typ_data in res["by_type"].items():
            keno_type = int(typ_key.split("_")[1])
            pvalue_list.append((lb_idx, keno_type, "overall", typ_data.get("big_win_pvalue")))

    # Apply BH correction
    pvalues_only = [x[3] for x in pvalue_list]
    significant_flags = _benjamini_hochberg(pvalues_only, alpha=args.fdr_alpha)

    # Build significance map
    significance_map: dict[tuple[int, int, str], bool] = {}
    for i, (lb_idx, keno_type, window, _) in enumerate(pvalue_list):
        significance_map[(lb_idx, keno_type, window)] = significant_flags[i]

    # Augment results with FDR-corrected significance
    n_significant = 0
    for lb_idx, res in enumerate(results):
        for typ_key, typ_data in res["by_type"].items():
            keno_type = int(typ_key.split("_")[1])
            is_sig = significance_map.get((lb_idx, keno_type, "overall"), False)
            typ_data["fdr_significant"] = is_sig
            if is_sig:
                n_significant += 1

    # Find best lookback per type (based on delta_roi)
    best_lookback_by_type: dict[int, dict[str, Any]] = {}
    for keno_type in keno_types:
        best_delta = float("-inf")
        best_result = None
        for lb_idx, res in enumerate(results):
            typ_key = f"typ_{keno_type}"
            if typ_key in res["by_type"]:
                delta = res["by_type"][typ_key]["delta_roi"]
                if delta > best_delta:
                    best_delta = delta
                    best_result = {
                        "lookback_days": res["lookback_days"],
                        "delta_roi": delta,
                        "rules_roi": res["by_type"][typ_key]["rules_roi"],
                        "baseline_roi": res["by_type"][typ_key]["baseline_roi"],
                        "fdr_significant": res["by_type"][typ_key].get("fdr_significant", False),
                    }
        if best_result:
            best_lookback_by_type[keno_type] = best_result

    # Create lookback comparison matrix (lookback x keno_type)
    lookback_matrix: dict[int, dict[str, float]] = {}
    for res in results:
        lb = res["lookback_days"]
        lookback_matrix[lb] = {}
        for typ_key, typ_data in res["by_type"].items():
            keno_type = int(typ_key.split("_")[1])
            lookback_matrix[lb][f"typ_{keno_type}_delta_roi"] = typ_data["delta_roi"]
            lookback_matrix[lb][f"typ_{keno_type}_rules_roi"] = typ_data["rules_roi"]
            lookback_matrix[lb][f"typ_{keno_type}_baseline_roi"] = typ_data["baseline_roi"]

    elapsed = time.time() - start_time
    total_comparisons = len(pvalue_list)

    payload = {
        "analysis": "walk_forward_lookback_grid",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "draws_path": args.draws,
            "train_end": args.train_end,
            "val_end": args.val_end,
            "test_start": args.test_start,
            "types": keno_types,
            "quick_mode": args.quick,
            "big_win_threshold": args.big_win_threshold,
            "fdr_alpha": args.fdr_alpha,
            "lookback_periods_tested": [p.recent_draws for p in lookback_grid],
        },
        "summary": {
            "lookback_count": len(lookback_grid),
            "total_comparisons": total_comparisons,
            "fdr_significant_count": n_significant,
            "runtime_seconds": round(elapsed, 2),
        },
        "best_lookback_by_type": {f"typ_{k}": v for k, v in best_lookback_by_type.items()},
        "lookback_matrix": lookback_matrix,
        "grid_results": results,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {args.output}")

    print("\n" + "=" * 80)
    print(f"Lookback Grid Search Complete: {len(lookback_grid)} periods, {elapsed:.1f}s")
    print(f"FDR Correction: {n_significant}/{total_comparisons} significant at alpha={args.fdr_alpha}")
    print("=" * 80)

    print("\nBest lookback per keno type (by delta_roi):")
    for keno_type in sorted(best_lookback_by_type.keys()):
        b = best_lookback_by_type[keno_type]
        sig_marker = "*" if b["fdr_significant"] else ""
        print(
            f"  Typ-{keno_type}: lookback={b['lookback_days']} days, "
            f"delta_roi={b['delta_roi']:+.2f}pp{sig_marker} "
            f"(rules={b['rules_roi']:.2f}%, baseline={b['baseline_roi']:.2f}%)"
        )

    print("\nLookback comparison matrix (delta_roi by type):")
    header = "Lookback | " + " | ".join([f"Typ-{t}" for t in keno_types])
    print(header)
    print("-" * len(header))
    for lb in sorted(lookback_matrix.keys()):
        row = f"{lb:>7}d | "
        row += " | ".join([f"{lookback_matrix[lb].get(f'typ_{t}_delta_roi', 0.0):+6.2f}" for t in keno_types])
        print(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
