#!/usr/bin/env python3
"""Walk-Forward Yearly Transfer Matrix Analysis.

Creates a transfer matrix measuring how well rules trained on Year X
generalize to Year Y for all year combinations.

Per CLAUDE.md Axiom-First: frozen rules from train, tested OOS,
BH/FDR correction for multiple comparisons.

Usage:
  python scripts/walk_forward_yearly_transfer.py
  python scripts/walk_forward_yearly_transfer.py --output results/yearly_transfer_matrix.json
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


@dataclass(frozen=True)
class FrozenRule:
    """A rule frozen after training."""
    trigger_number: int
    trigger_position: int
    kind: str
    predicted_number: int
    support: int
    probability: float
    lower_bound: float


@dataclass(frozen=True)
class DayOutcome:
    """Result of a single day's backtest."""
    date: str
    ticket: list[int]
    hits: int
    payout: float


# Default parameters (from best configs in walk_forward_param_grid.py)
DEFAULT_PARAMS = {
    "recent_draws": 365,
    "recent_weight": 0.6,
    "train_min_support": 10,
    "exclude_lb_train": 0.80,
    "include_lb_train": 0.33,
    "exclude_max": 3,
    "include_max": 5,
    "hard_exclude_lb": 0.95,
    "exclude_weight": 2.0,
    "include_weight": 1.0,
}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Walk-Forward Yearly Transfer Matrix")
    p.add_argument("--draws", default="data/raw/keno/KENO_ab_2022_bereinigt.csv")
    p.add_argument("--types", type=int, nargs="*", default=[8, 9, 10])
    p.add_argument("--big-win-threshold", type=float, default=400.0)
    p.add_argument("--z", type=float, default=1.959963984540054)
    p.add_argument("--fdr-alpha", type=float, default=0.10, help="FDR threshold for BH correction")
    p.add_argument("--output", default="results/yearly_transfer_matrix.json")
    return p.parse_args()


def _get_year(d: datetime) -> int:
    """Extract year from datetime."""
    return d.year


def _filter_by_year(draws: list[DrawResult], year: int) -> list[DrawResult]:
    """Filter draws to a specific year."""
    return [d for d in draws if _get_year(d.date) == year]


def _mine_train_rules(
    draws: list[DrawResult],
    *,
    z: float,
    min_support: int,
    exclude_lb: float,
    include_lb: float,
    exclude_max: int,
    include_max: int,
) -> list[RuleFiring]:
    """Mine position rules from training draws."""
    if len(draws) < 2:
        return []

    transitions = [(draws[i - 1], draws[i]) for i in range(1, len(draws))]
    miner = RollingPositionRuleMiner(window_size=max(1, len(transitions)))

    for prev, curr in transitions:
        miner.add_transition(
            today_ordered=extract_ordered_keno_numbers(prev),
            tomorrow_numbers=curr.numbers,
        )

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


def _freeze_rules(rules: list[RuleFiring]) -> list[FrozenRule]:
    """Convert RuleFirings to FrozenRules."""
    return [
        FrozenRule(
            trigger_number=int(r.trigger_number),
            trigger_position=int(r.trigger_position),
            kind=str(r.kind),
            predicted_number=int(r.predicted_number),
            support=int(r.support),
            probability=float(r.probability),
            lower_bound=float(r.lower_bound),
        )
        for r in rules
    ]


def _add_draw_to_counts(
    draw_numbers: Iterable[int],
    *,
    all_counts: dict[int, int],
    recent_q: deque[set[int]],
    recent_counts: dict[int, int],
    total_draws_seen: int,
    recent_draws: int,
) -> int:
    """Update frequency counts with a new draw."""
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
    """Calculate weighted frequency scores for each number."""
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
    """Rank numbers by score (highest first)."""
    numbers = list(range(1, 71))
    numbers.sort(key=lambda n: (-float(score[n]), n))
    return numbers


def _null_probability_big_win(*, keno_type: int, threshold: float) -> float:
    """Calculate null probability of big win for a given keno type."""
    probs = KENO_PROBABILITIES.get(int(keno_type), {})
    p = 0.0
    for hits, ph in probs.items():
        if get_fixed_quote(keno_type, int(hits)) >= float(threshold):
            p += float(ph)
    return float(p)


def _summarize_outcomes(
    *, keno_type: int, outcomes: list[DayOutcome], threshold: float
) -> dict[str, Any]:
    """Summarize backtest outcomes."""
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


def _test_rules_on_year(
    test_draws: list[DrawResult],
    *,
    frozen_rules: list[FrozenRule],
    keno_types: list[int],
    big_win_threshold: float,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Test frozen rules on a given year's draws."""
    if len(test_draws) < 2:
        return {"error": "insufficient_data", "n_draws": len(test_draws)}

    frozen_by_trigger: dict[tuple[int, int], list[FrozenRule]] = defaultdict(list)
    for r in frozen_rules:
        frozen_by_trigger[(int(r.trigger_number), int(r.trigger_position))].append(r)

    # Initialize frequency tracking
    all_counts = {n: 0 for n in range(1, 71)}
    recent_counts = {n: 0 for n in range(1, 71)}
    recent_q: deque[set[int]] = deque()
    total_draws_seen = 0

    total_draws_seen = _add_draw_to_counts(
        test_draws[0].numbers,
        all_counts=all_counts,
        recent_q=recent_q,
        recent_counts=recent_counts,
        total_draws_seen=total_draws_seen,
        recent_draws=params["recent_draws"],
    )

    by_type_outcomes_baseline: dict[int, list[DayOutcome]] = {int(k): [] for k in keno_types}
    by_type_outcomes_rules: dict[int, list[DayOutcome]] = {int(k): [] for k in keno_types}

    for i in range(1, len(test_draws)):
        prev = test_draws[i - 1]
        curr = test_draws[i]

        base_scores = _weighted_frequency_scores(
            all_counts=all_counts,
            total_draws_seen=total_draws_seen,
            recent_counts=recent_counts,
            recent_seen=len(recent_q),
            recent_weight=params["recent_weight"],
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
            hard_exclude_lb=params["hard_exclude_lb"],
            exclude_weight=params["exclude_weight"],
            include_weight=params["include_weight"],
        )

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
            recent_draws=params["recent_draws"],
        )

    # Summarize results
    by_type: dict[str, Any] = {}
    for keno_type in keno_types:
        base = by_type_outcomes_baseline[keno_type]
        rules = by_type_outcomes_rules[keno_type]

        overall_base = _summarize_outcomes(
            keno_type=keno_type, outcomes=base, threshold=big_win_threshold
        )
        overall_rules = _summarize_outcomes(
            keno_type=keno_type, outcomes=rules, threshold=big_win_threshold
        )

        delta_roi = overall_rules["roi_percent"] - overall_base["roi_percent"]
        delta_bigwin = overall_rules["big_win_count"] - overall_base["big_win_count"]

        by_type[f"typ_{keno_type}"] = {
            "baseline_roi": overall_base["roi_percent"],
            "rules_roi": overall_rules["roi_percent"],
            "delta_roi": round(delta_roi, 2),
            "baseline_bigwin": overall_base["big_win_count"],
            "rules_bigwin": overall_rules["big_win_count"],
            "delta_bigwin": delta_bigwin,
            "big_win_pvalue": overall_rules["big_win_pvalue"],
            "n_days": overall_rules["n_days"],
        }

    return by_type


def _benjamini_hochberg(pvalues: list[Optional[float]], alpha: float = 0.10) -> list[bool]:
    """Apply Benjamini-Hochberg FDR correction.

    Returns list of booleans indicating which hypotheses are significant after correction.
    """
    n = len(pvalues)
    if n == 0:
        return []

    valid_indices = [i for i, p in enumerate(pvalues) if p is not None]
    valid_pvalues = [pvalues[i] for i in valid_indices]

    if not valid_pvalues:
        return [False] * n

    sorted_indices = sorted(range(len(valid_pvalues)), key=lambda i: valid_pvalues[i])
    sorted_pvalues = [valid_pvalues[i] for i in sorted_indices]

    m = len(sorted_pvalues)
    thresholds = [(i + 1) * alpha / m for i in range(m)]

    significant_count = 0
    for k in range(m - 1, -1, -1):
        if sorted_pvalues[k] <= thresholds[k]:
            significant_count = k + 1
            break

    significant_sorted = [i < significant_count for i in range(m)]

    result = [False] * n
    for sorted_idx, orig_idx in enumerate(sorted_indices):
        result[valid_indices[orig_idx]] = significant_sorted[sorted_idx]

    return result


def main() -> int:
    args = _parse_args()
    start_time = time.time()

    loader = DataLoader()
    draws = [d for d in loader.load(args.draws) if d.game_type == GameType.KENO]
    draws = sorted(draws, key=lambda d: d.date)

    if len(draws) < 2:
        print("ERROR: Need at least 2 draws")
        return 1

    # Identify available years
    years = sorted(set(_get_year(d.date) for d in draws))
    print(f"Yearly Transfer Matrix Analysis")
    print(f"Available years: {years}")
    print(f"Keno types: {args.types}")
    print(f"FDR alpha: {args.fdr_alpha}")
    print("=" * 80)

    keno_types = [int(t) for t in args.types]
    params = DEFAULT_PARAMS.copy()

    # Build transfer matrix
    transfer_matrix: dict[str, dict[str, Any]] = {}
    all_pvalues: list[tuple[int, int, int, Optional[float]]] = []

    for train_year in years:
        train_draws = _filter_by_year(draws, train_year)
        print(f"\n[Train Year: {train_year}] {len(train_draws)} draws")

        if len(train_draws) < 30:
            print(f"  SKIP: insufficient training data (<30 draws)")
            continue

        # Mine rules from training year
        train_rules = _mine_train_rules(
            train_draws,
            z=args.z,
            min_support=params["train_min_support"],
            exclude_lb=params["exclude_lb_train"],
            include_lb=params["include_lb_train"],
            exclude_max=params["exclude_max"],
            include_max=params["include_max"],
        )
        frozen_rules = _freeze_rules(train_rules)
        print(f"  Rules mined: {len(frozen_rules)}")

        transfer_matrix[str(train_year)] = {
            "train_draws": len(train_draws),
            "rules_mined": len(frozen_rules),
            "test_results": {},
        }

        # Test on each year
        for test_year in years:
            if test_year == train_year:
                # In-sample (for reference)
                label = "in_sample"
            else:
                label = "out_of_sample"

            test_draws = _filter_by_year(draws, test_year)
            if len(test_draws) < 10:
                print(f"  -> Test {test_year}: SKIP (insufficient data)")
                continue

            result = _test_rules_on_year(
                test_draws,
                frozen_rules=frozen_rules,
                keno_types=keno_types,
                big_win_threshold=args.big_win_threshold,
                params=params,
            )

            transfer_matrix[str(train_year)]["test_results"][str(test_year)] = {
                "type": label,
                "test_draws": len(test_draws),
                "by_type": result,
            }

            # Collect p-values for FDR correction
            if isinstance(result, dict) and "error" not in result:
                for typ_key, typ_data in result.items():
                    if isinstance(typ_data, dict):
                        keno_type = int(typ_key.split("_")[1])
                        pval = typ_data.get("big_win_pvalue")
                        all_pvalues.append((train_year, test_year, keno_type, pval))

            # Summary line
            if isinstance(result, dict) and "typ_9" in result:
                delta = result["typ_9"]["delta_roi"]
                print(f"  -> Test {test_year} ({label}): Typ-9 delta_roi={delta:+.2f}pp")

    # Apply BH FDR correction
    pvalues_only = [x[3] for x in all_pvalues]
    significant_flags = _benjamini_hochberg(pvalues_only, alpha=args.fdr_alpha)

    # Build significance map
    significance_map: dict[tuple[int, int, int], bool] = {}
    for i, (train_yr, test_yr, keno_type, _) in enumerate(all_pvalues):
        significance_map[(train_yr, test_yr, keno_type)] = significant_flags[i]

    # Augment results with FDR-corrected significance
    n_significant = 0
    for train_year_str, train_data in transfer_matrix.items():
        train_year = int(train_year_str)
        for test_year_str, test_data in train_data.get("test_results", {}).items():
            test_year = int(test_year_str)
            by_type = test_data.get("by_type", {})
            if isinstance(by_type, dict):
                for typ_key, typ_data in by_type.items():
                    if isinstance(typ_data, dict):
                        keno_type = int(typ_key.split("_")[1])
                        is_sig = significance_map.get((train_year, test_year, keno_type), False)
                        typ_data["fdr_significant"] = is_sig
                        if is_sig:
                            n_significant += 1

    # Compute summary statistics
    oos_results: list[dict[str, Any]] = []
    for train_year_str, train_data in transfer_matrix.items():
        for test_year_str, test_data in train_data.get("test_results", {}).items():
            if test_data.get("type") == "out_of_sample":
                by_type = test_data.get("by_type", {})
                if isinstance(by_type, dict):
                    for typ_key, typ_data in by_type.items():
                        if isinstance(typ_data, dict):
                            oos_results.append({
                                "train_year": int(train_year_str),
                                "test_year": int(test_year_str),
                                "keno_type": int(typ_key.split("_")[1]),
                                "delta_roi": typ_data.get("delta_roi", 0),
                                "rules_roi": typ_data.get("rules_roi", 0),
                                "baseline_roi": typ_data.get("baseline_roi", 0),
                                "fdr_significant": typ_data.get("fdr_significant", False),
                            })

    # Summary by direction (forward vs backward transfer)
    forward_transfer = [r for r in oos_results if r["test_year"] > r["train_year"]]
    backward_transfer = [r for r in oos_results if r["test_year"] < r["train_year"]]

    def _mean_delta(results: list[dict]) -> float:
        if not results:
            return 0.0
        return float(np.mean([r["delta_roi"] for r in results]))

    elapsed = time.time() - start_time

    payload = {
        "analysis": "walk_forward_yearly_transfer",
        "generated_at": datetime.now().isoformat(),
        "config": {
            "draws_path": args.draws,
            "types": keno_types,
            "big_win_threshold": args.big_win_threshold,
            "fdr_alpha": args.fdr_alpha,
            "params": params,
        },
        "available_years": years,
        "summary": {
            "total_year_pairs": len(oos_results),
            "fdr_significant_count": n_significant,
            "mean_oos_delta_roi": round(_mean_delta(oos_results), 2),
            "forward_transfer_count": len(forward_transfer),
            "forward_transfer_mean_delta": round(_mean_delta(forward_transfer), 2),
            "backward_transfer_count": len(backward_transfer),
            "backward_transfer_mean_delta": round(_mean_delta(backward_transfer), 2),
            "runtime_seconds": round(elapsed, 2),
        },
        "transfer_matrix": transfer_matrix,
        "oos_results_flat": oos_results,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {args.output}")

    print("\n" + "=" * 80)
    print(f"Transfer Matrix Complete: {len(years)} years, {elapsed:.1f}s")
    print(f"FDR Correction: {n_significant}/{len(all_pvalues)} significant at alpha={args.fdr_alpha}")
    print(f"Mean OOS Delta ROI: {_mean_delta(oos_results):+.2f}pp")
    print(f"Forward Transfer (train<test): {_mean_delta(forward_transfer):+.2f}pp over {len(forward_transfer)} pairs")
    print(f"Backward Transfer (train>test): {_mean_delta(backward_transfer):+.2f}pp over {len(backward_transfer)} pairs")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
