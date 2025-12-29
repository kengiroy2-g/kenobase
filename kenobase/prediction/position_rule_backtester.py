"""Walk-forward next-day backtest for the position rule layer.

Scenario
--------
At day i, we have observed today's draw (including *ordered* positions).
We want to predict day i+1.

Models compared:
1) Baseline: weighted frequency ranking (recent + all-time)
2) Baseline + Position-Rule-Layer: exclusion/inclusion rules derived from a rolling
   window of past transitions (i-1 -> i, i-2 -> i-1, ...).
"""

from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

import numpy as np
from scipy import stats

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DrawResult, GameType
from kenobase.prediction.position_rule_layer import (
    BASE_ABSENCE,
    BASE_PRESENCE,
    RollingPositionRuleMiner,
    apply_rule_layer_to_scores,
    extract_ordered_keno_numbers,
    index_to_trigger,
    trigger_index,
)


@dataclass(frozen=True)
class HitDistribution:
    keno_type: int
    observed_counts: dict[int, int]
    expected_counts: dict[int, float]
    chi2_statistic: Optional[float]
    chi2_p_value: Optional[float]
    bins_used: int
    note: str = ""


@dataclass(frozen=True)
class ModelMetrics:
    model: str
    keno_type: int
    n_predictions: int
    start_index: int
    recent_draws: int
    recent_weight: float
    mean_hits: float
    expected_mean_hits: float
    mean_hits_z: Optional[float]
    mean_hits_p_value: Optional[float]
    near_miss_hits: int
    near_miss_count: int
    expected_near_miss_count: float
    near_miss_p_value: Optional[float]
    jackpot_hits: int
    jackpot_count: int
    expected_jackpot_count: float
    jackpot_p_value: Optional[float]
    last_ticket: list[int]
    hit_distribution: HitDistribution


@dataclass(frozen=True)
class RuleAccuracy:
    trials: int
    correct: int
    accuracy: float
    baseline: float
    lift: float


@dataclass(frozen=True)
class TriggerRuleSummary:
    trigger_number: int
    trigger_position: int
    kind: str  # "exclude" / "include"
    predicted_numbers: list[int]
    trials: int
    correct: int
    accuracy: float


@dataclass(frozen=True)
class PositionRuleLayerBacktestPayload:
    analysis: str
    generated_at: str
    draws: dict
    config: dict
    rule_accuracy: dict
    by_type: dict
    top_rules: dict


def _hypergeom_mean_var(
    *,
    keno_type: int,
    numbers_range: int = 70,
    numbers_drawn: int = 20,
) -> tuple[float, float]:
    n = numbers_drawn
    N = numbers_range
    K = keno_type
    mean = n * (K / N)
    var = n * (K / N) * (1.0 - K / N) * ((N - n) / (N - 1))
    return float(mean), float(var)


def _chi_square_from_counts(
    observed: dict[int, int],
    expected: dict[int, float],
    *,
    min_expected: float = 5.0,
) -> tuple[Optional[float], Optional[float], int, str]:
    keys = sorted(expected.keys())
    obs_list = [int(observed.get(k, 0)) for k in keys]
    exp_list = [float(expected.get(k, 0.0)) for k in keys]

    merged_obs: list[int] = []
    merged_exp: list[float] = []
    acc_obs = 0
    acc_exp = 0.0
    for o, e in zip(obs_list, exp_list, strict=False):
        acc_obs += int(o)
        acc_exp += float(e)
        if acc_exp >= min_expected:
            merged_obs.append(acc_obs)
            merged_exp.append(acc_exp)
            acc_obs = 0
            acc_exp = 0.0

    if acc_exp > 0 or acc_obs > 0:
        if merged_obs:
            merged_obs[-1] += acc_obs
            merged_exp[-1] += acc_exp
        else:
            merged_obs.append(acc_obs)
            merged_exp.append(acc_exp)

    if len(merged_obs) < 2 or sum(merged_exp) <= 0:
        return None, None, len(merged_obs), "insufficient bins for chi-square after merging"

    obs_arr = np.asarray(merged_obs, dtype=int)
    exp_arr = np.asarray(merged_exp, dtype=float)

    if exp_arr.sum() > 0:
        exp_arr *= float(obs_arr.sum() / exp_arr.sum())

    chi2, p = stats.chisquare(obs_arr, f_exp=exp_arr)
    return float(chi2), float(p), int(len(merged_obs)), "chi-square vs exact hypergeometric null (merged bins)"


def _rank_from_scores(score: np.ndarray) -> list[int]:
    # score shape (71,) index 1..70, ties -> smaller number first.
    numbers = list(range(1, 71))
    numbers.sort(key=lambda n: (-float(score[n]), n))
    return numbers


def _compute_weighted_frequency_scores(
    *,
    all_counts: dict[int, int],
    total_seen: int,
    recent_counts: dict[int, int],
    recent_seen: int,
    recent_weight: float,
) -> np.ndarray:
    # Return array (71,) of marginal presence probabilities.
    scores = np.zeros(71, dtype=float)
    if total_seen <= 0:
        return scores

    if recent_seen > 0:
        for n in range(1, 71):
            freq_all = all_counts[n] / total_seen
            freq_recent = recent_counts[n] / recent_seen
            scores[n] = recent_weight * freq_recent + (1.0 - recent_weight) * freq_all
    else:
        for n in range(1, 71):
            scores[n] = all_counts[n] / total_seen

    return scores


def _finalize_metrics(
    *,
    model: str,
    keno_type: int,
    hits_list: list[int],
    start_index: int,
    recent_draws: int,
    recent_weight: float,
    last_ticket: list[int],
) -> ModelMetrics:
    n_predictions = len(hits_list)
    mean_hits = float(np.mean(hits_list)) if hits_list else 0.0
    expected_mean, var = _hypergeom_mean_var(keno_type=keno_type)

    mean_z = None
    mean_p = None
    if hits_list and var > 0:
        se = math.sqrt(var / len(hits_list))
        if se > 0:
            mean_z = float((mean_hits - expected_mean) / se)
            mean_p = float(2.0 * stats.norm.sf(abs(mean_z)))

    near_hits = keno_type - 1
    jack_hits = keno_type
    near_count = int(sum(1 for h in hits_list if h == near_hits))
    jack_count = int(sum(1 for h in hits_list if h == jack_hits))

    probs = KENO_PROBABILITIES.get(int(keno_type))
    if not probs:
        raise ValueError(f"Unsupported keno_type for null model: {keno_type}")
    p_near = float(probs.get(near_hits, 0.0))
    p_jack = float(probs.get(jack_hits, 0.0))
    exp_near = p_near * n_predictions
    exp_jack = p_jack * n_predictions

    near_p = float(stats.binomtest(near_count, n=n_predictions, p=p_near).pvalue) if hits_list else None
    jack_p = float(stats.binomtest(jack_count, n=n_predictions, p=p_jack).pvalue) if hits_list else None

    obs_counts = {m: 0 for m in range(0, keno_type + 1)}
    for h in hits_list:
        if 0 <= h <= keno_type:
            obs_counts[int(h)] += 1

    exp_counts = {m: float(probs.get(m, 0.0)) * n_predictions for m in range(0, keno_type + 1)}
    chi2, chi2_p, bins_used, note = _chi_square_from_counts(obs_counts, exp_counts)

    distribution = HitDistribution(
        keno_type=int(keno_type),
        observed_counts=obs_counts,
        expected_counts=exp_counts,
        chi2_statistic=chi2,
        chi2_p_value=chi2_p,
        bins_used=bins_used,
        note=note,
    )

    return ModelMetrics(
        model=model,
        keno_type=int(keno_type),
        n_predictions=n_predictions,
        start_index=int(start_index),
        recent_draws=int(recent_draws),
        recent_weight=float(recent_weight),
        mean_hits=float(mean_hits),
        expected_mean_hits=float(expected_mean),
        mean_hits_z=mean_z,
        mean_hits_p_value=mean_p,
        near_miss_hits=int(near_hits),
        near_miss_count=near_count,
        expected_near_miss_count=float(exp_near),
        near_miss_p_value=near_p,
        jackpot_hits=int(jack_hits),
        jackpot_count=jack_count,
        expected_jackpot_count=float(exp_jack),
        jackpot_p_value=jack_p,
        last_ticket=list(last_ticket),
        hit_distribution=distribution,
    )


def backtest_position_rule_layer(
    draws: list[DrawResult],
    *,
    keno_types: list[int],
    start_index: int = 365,
    recent_draws: int = 365,
    recent_weight: float = 0.6,
    rule_window: int = 365,
    rule_min_support: int = 10,
    exclude_max: int = 3,
    include_max: int = 5,
    exclude_lb: float = 0.90,
    include_lb: float = 0.40,
    hard_exclude: bool = True,
    hard_exclude_lb: float = 0.95,
    exclude_weight: float = 2.0,
    include_weight: float = 1.0,
    z: float = 1.959963984540054,
) -> PositionRuleLayerBacktestPayload:
    if not draws:
        raise ValueError("draws must not be empty")
    if any(d.game_type != GameType.KENO for d in draws):
        raise ValueError("backtest_position_rule_layer currently supports KENO draws only")
    if start_index < 1:
        raise ValueError("start_index must be >= 1 (need at least one prior transition for rules)")
    if start_index >= len(draws) - 1:
        raise ValueError(f"start_index={start_index} must be < len(draws)-1 ({len(draws)-1})")
    if not 0.0 <= recent_weight <= 1.0:
        raise ValueError("recent_weight must be in [0, 1]")

    sorted_draws = sorted(draws, key=lambda d: d.date)
    ordered_by_i = [extract_ordered_keno_numbers(d) for d in sorted_draws]

    # Sanity: ordered data should not be purely sorted most of the time.
    # (If it's sorted, positions are not draw order and rule layer becomes meaningless.)
    n_sorted_like = sum(1 for nums in ordered_by_i if nums == sorted(nums))
    if n_sorted_like > len(ordered_by_i) * 0.5:
        raise ValueError(
            "Ordered numbers look sorted for most draws; positions likely not available. "
            "Ensure DataLoader stores metadata['numbers_ordered']."
        )

    # Frequency history (marginal presence)
    total_seen = 0
    all_counts = {n: 0 for n in range(1, 71)}
    recent_counts = {n: 0 for n in range(1, 71)}
    recent_q: deque[list[int]] = deque()

    def add_history(numbers: list[int]) -> None:
        nonlocal total_seen
        total_seen += 1
        for x in numbers:
            all_counts[int(x)] += 1
            recent_counts[int(x)] += 1
        recent_q.append(list(numbers))
        if recent_draws > 0 and len(recent_q) > recent_draws:
            old = recent_q.popleft()
            for x in old:
                recent_counts[int(x)] -= 1

    # Initialize with day 0
    add_history(sorted_draws[0].numbers)

    # Rule miner (rolling transitions)
    miner = RollingPositionRuleMiner(window_size=rule_window)

    # Storage per model/k
    hits_base: dict[int, list[int]] = defaultdict(list)
    hits_rules: dict[int, list[int]] = defaultdict(list)
    last_ticket_base: dict[int, list[int]] = defaultdict(list)
    last_ticket_rules: dict[int, list[int]] = defaultdict(list)

    # Accuracy tracking for fired rules (out-of-sample per-day evaluation)
    ex_trials = 0
    ex_correct = 0
    in_trials = 0
    in_correct = 0

    # Per trigger summary: key (trigger_idx, kind, predicted_number) -> trials/correct
    per_rule_counts: dict[tuple[int, str, int], tuple[int, int]] = defaultdict(lambda: (0, 0))

    for i in range(0, len(sorted_draws) - 1):
        # Update miner with transition i-1 -> i (available once i>=1).
        if i >= 1:
            miner.add_transition(
                today_ordered=ordered_by_i[i - 1],
                tomorrow_numbers=sorted_draws[i].numbers,
            )

        # Predict i+1 once we have enough history.
        if i >= start_index:
            # Baseline scores (marginal presence estimate)
            scores_base = _compute_weighted_frequency_scores(
                all_counts=all_counts,
                total_seen=total_seen,
                recent_counts=recent_counts,
                recent_seen=len(recent_q),
                recent_weight=recent_weight,
            )
            ranked_base = _rank_from_scores(scores_base)

            # Rule layer: fire rules from today's ordered draw.
            exclusions, inclusions = miner.fire_rules_for_ordered_draw(
                ordered_by_i[i],
                exclude_max=exclude_max,
                include_max=include_max,
                min_support=rule_min_support,
                exclude_lb=exclude_lb,
                include_lb=include_lb,
                z=z,
            )
            scores_rules, _, _ = apply_rule_layer_to_scores(
                scores_base,
                exclusions=exclusions,
                inclusions=inclusions,
                hard_exclude=hard_exclude,
                hard_exclude_lb=hard_exclude_lb,
                exclude_weight=exclude_weight,
                include_weight=include_weight,
            )
            ranked_rules = _rank_from_scores(scores_rules)

            next_set = set(sorted_draws[i + 1].numbers)

            # Track rule accuracy (next day).
            for firing in exclusions:
                ex_trials += 1
                correct = int(firing.predicted_number) not in next_set
                ex_correct += int(correct)
                k = trigger_index(int(firing.trigger_number), int(firing.trigger_position))
                key = (k, "exclude", int(firing.predicted_number))
                t, c = per_rule_counts[key]
                per_rule_counts[key] = (t + 1, c + int(correct))

            for firing in inclusions:
                in_trials += 1
                correct = int(firing.predicted_number) in next_set
                in_correct += int(correct)
                k = trigger_index(int(firing.trigger_number), int(firing.trigger_position))
                key = (k, "include", int(firing.predicted_number))
                t, c = per_rule_counts[key]
                per_rule_counts[key] = (t + 1, c + int(correct))

            # Ticket evaluation
            for k in keno_types:
                ticket_base = ranked_base[: int(k)]
                ticket_rules = ranked_rules[: int(k)]
                last_ticket_base[int(k)] = ticket_base
                last_ticket_rules[int(k)] = ticket_rules

                hits_base[int(k)].append(len(next_set.intersection(ticket_base)))
                hits_rules[int(k)].append(len(next_set.intersection(ticket_rules)))

        # Add next draw to history for next iteration.
        add_history(sorted_draws[i + 1].numbers)

    # Finalize metrics per k
    by_type: dict[str, dict] = {}
    for k in sorted(set(keno_types)):
        m_base = _finalize_metrics(
            model="weighted_frequency_nextday",
            keno_type=k,
            hits_list=hits_base.get(k, []),
            start_index=start_index,
            recent_draws=recent_draws,
            recent_weight=recent_weight,
            last_ticket=last_ticket_base.get(k, []),
        )
        m_rules = _finalize_metrics(
            model="weighted_frequency_nextday+position_rules",
            keno_type=k,
            hits_list=hits_rules.get(k, []),
            start_index=start_index,
            recent_draws=recent_draws,
            recent_weight=recent_weight,
            last_ticket=last_ticket_rules.get(k, []),
        )
        by_type[f"typ_{k}"] = {
            "baseline": asdict(m_base),
            "with_rules": asdict(m_rules),
            "delta": {
                "mean_hits": float(m_rules.mean_hits - m_base.mean_hits),
                "near_miss_count": int(m_rules.near_miss_count - m_base.near_miss_count),
                "jackpot_count": int(m_rules.jackpot_count - m_base.jackpot_count),
            },
        }

    # Aggregate rule accuracy
    ex_acc = ex_correct / ex_trials if ex_trials else 0.0
    in_acc = in_correct / in_trials if in_trials else 0.0
    rule_accuracy = {
        "exclusion": asdict(
            RuleAccuracy(
                trials=int(ex_trials),
                correct=int(ex_correct),
                accuracy=float(ex_acc),
                baseline=float(BASE_ABSENCE),
                lift=float(ex_acc - BASE_ABSENCE),
            )
        ),
        "inclusion": asdict(
            RuleAccuracy(
                trials=int(in_trials),
                correct=int(in_correct),
                accuracy=float(in_acc),
                baseline=float(BASE_PRESENCE),
                lift=float(in_acc - BASE_PRESENCE),
            )
        ),
    }

    # Summarize top rules by accuracy with minimum trials
    min_trials_for_top = 25
    trigger_agg: dict[tuple[int, str], list[tuple[int, int, int]]] = defaultdict(list)
    for (trig_idx, kind, predicted), (t, c) in per_rule_counts.items():
        trigger_agg[(trig_idx, kind)].append((predicted, t, c))

    summaries: list[TriggerRuleSummary] = []
    for (trig_idx, kind), items in trigger_agg.items():
        total_t = sum(t for _, t, _ in items)
        total_c = sum(c for _, _, c in items)
        if total_t < min_trials_for_top:
            continue
        # Choose the most common predicted numbers for display.
        items_sorted = sorted(items, key=lambda x: (-x[1], x[0]))
        predicted_numbers = [p for p, _, _ in items_sorted[: max(exclude_max if kind == "exclude" else include_max, 1)]]
        number, position = index_to_trigger(trig_idx)
        summaries.append(
            TriggerRuleSummary(
                trigger_number=int(number),
                trigger_position=int(position),
                kind=str(kind),
                predicted_numbers=[int(x) for x in predicted_numbers],
                trials=int(total_t),
                correct=int(total_c),
                accuracy=float(total_c / total_t) if total_t > 0 else 0.0,
            )
        )

    top_ex = sorted([s for s in summaries if s.kind == "exclude"], key=lambda s: (-s.accuracy, -s.trials))
    top_in = sorted([s for s in summaries if s.kind == "include"], key=lambda s: (-s.accuracy, -s.trials))

    payload = PositionRuleLayerBacktestPayload(
        analysis="position_rule_layer_nextday_backtest",
        generated_at=datetime.now().isoformat(),
        draws={
            "count": len(sorted_draws),
            "start_date": str(sorted_draws[0].date.date()),
            "end_date": str(sorted_draws[-1].date.date()),
        },
        config={
            "keno_types": [int(k) for k in keno_types],
            "start_index": int(start_index),
            "recent_draws": int(recent_draws),
            "recent_weight": float(recent_weight),
            "rule_window": int(rule_window),
            "rule_min_support": int(rule_min_support),
            "exclude_max": int(exclude_max),
            "include_max": int(include_max),
            "exclude_lb": float(exclude_lb),
            "include_lb": float(include_lb),
            "hard_exclude": bool(hard_exclude),
            "hard_exclude_lb": float(hard_exclude_lb),
            "exclude_weight": float(exclude_weight),
            "include_weight": float(include_weight),
            "z": float(z),
        },
        rule_accuracy=rule_accuracy,
        by_type=by_type,
        top_rules={
            "min_trials": int(min_trials_for_top),
            "top_exclusion": [asdict(s) for s in top_ex[:20]],
            "top_inclusion": [asdict(s) for s in top_in[:20]],
        },
    )

    return payload


__all__ = [
    "HitDistribution",
    "ModelMetrics",
    "PositionRuleLayerBacktestPayload",
    "RuleAccuracy",
    "TriggerRuleSummary",
    "backtest_position_rule_layer",
]

