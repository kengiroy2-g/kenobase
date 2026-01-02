"""Walk-forward backtest for cross-game trigger rules targeting KENO.

This evaluates whether *fixed* cross-lottery rules of the form

  (source trigger at date <= target_date - lag) -> (KENO number more/less likely)

provide measurable out-of-sample signal when used as a filter/boost layer on top of a
baseline KENO ranking model (weighted frequency).

Important
---------
This is an exploratory statistical backtest. Results can be sensitive to:
- how date-alignment is defined (latest source <= target-lag),
- the chosen lags and rule selection procedure (multiple testing),
- and the baseline model / thresholds used to convert rules into actions.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.prediction.position_rule_layer import BASE_ABSENCE, BASE_PRESENCE, KENO_MAX_NUMBER


@dataclass(frozen=True)
class CrossGameRule:
    source: str
    target: str
    lag_days: int
    trigger_kind: str  # "number" | "ordered_value"
    trigger: str  # e.g. "8" or "T6=1"
    target_number: int
    support: int
    base_rate: float
    conditional_rate: float
    lift: float
    p_value: float
    q_value: float

    @property
    def kind(self) -> str:
        # Convenience for the backtest layer.
        return "include" if float(self.lift) > 1.0 else "exclude"


@dataclass(frozen=True)
class RuleAccuracy:
    trials: int
    correct: int
    accuracy: float
    baseline: float
    lift: float


@dataclass(frozen=True)
class TypeSummary:
    keno_type: int
    n_predictions: int
    mean_hits_baseline: float
    mean_hits_with_rules: float
    delta_mean_hits: float


@dataclass(frozen=True)
class CrossGameRuleBacktestPayload:
    analysis: str
    generated_at: str
    draws: dict
    config: dict
    rules: dict
    rule_accuracy: dict
    by_type: dict


def _align_latest_source_index(source_dates: list[date], target_date: date, lag_days: int) -> Optional[int]:
    if lag_days < 0:
        raise ValueError("lag_days must be >= 0")
    desired = target_date - timedelta(days=int(lag_days))
    idx = bisect_right(source_dates, desired) - 1
    return int(idx) if idx >= 0 else None


def _rank_from_scores(scores: np.ndarray) -> list[int]:
    numbers = list(range(1, KENO_MAX_NUMBER + 1))
    numbers.sort(key=lambda n: (-float(scores[n]), n))
    return numbers


def _compute_weighted_frequency_scores(
    *,
    all_counts: np.ndarray,
    total_seen: int,
    recent_counts: np.ndarray,
    recent_seen: int,
    recent_weight: float,
) -> np.ndarray:
    scores = np.zeros(KENO_MAX_NUMBER + 1, dtype=float)
    if total_seen <= 0:
        return scores
    if recent_seen > 0:
        scores[1:] = float(recent_weight) * (recent_counts[1:] / recent_seen) + (1.0 - float(recent_weight)) * (
            all_counts[1:] / total_seen
        )
    else:
        scores[1:] = all_counts[1:] / total_seen
    return scores


def _parse_ordered_value_trigger(trigger: str) -> tuple[str, int]:
    if "=" not in trigger:
        raise ValueError(f"Invalid ordered_value trigger: {trigger!r}")
    label, value_str = trigger.split("=", 1)
    label = label.strip()
    value = int(value_str.strip())
    return label, int(value)


def backtest_cross_game_rule_layer(
    keno: GameDraws,
    *,
    sources: dict[str, GameDraws],
    rules: list[CrossGameRule],
    keno_types: list[int],
    start_index: int = 365,
    recent_draws: int = 365,
    recent_weight: float = 0.6,
    hard_exclude: bool = True,
    include_multiplier: float = 1.25,
    max_exclusions_per_draw: Optional[int] = None,
    max_inclusions_per_draw: Optional[int] = None,
    ordered_value_position_maps: Optional[dict[str, dict[str, int]]] = None,
) -> CrossGameRuleBacktestPayload:
    """Walk-forward backtest for KENO using cross-game rules as filter/boost layer.

    Prediction target is KENO draw at index i using information from:
    - past KENO draws [0..i-1] for baseline frequency,
    - source game draws aligned by date <= (keno_date[i] - lag_days).
    """
    if not keno.dates:
        raise ValueError("keno must not be empty")
    if start_index < 1:
        raise ValueError("start_index must be >= 1 (need at least 1 prior draw for baseline)")
    if start_index >= len(keno.dates):
        raise ValueError(f"start_index={start_index} must be < len(keno.dates) ({len(keno.dates)})")
    if not 0.0 <= float(recent_weight) <= 1.0:
        raise ValueError("recent_weight must be in [0, 1]")

    ordered_maps = ordered_value_position_maps or {}

    # Precompute KENO numbers per draw.
    keno_numbers: list[list[int]] = []
    for row in keno.presence:
        nums = np.nonzero(row)[0].tolist()
        nums = [int(x) for x in nums if x >= 1]
        keno_numbers.append(nums)

    # Baseline history (marginal presence).
    all_counts = np.zeros(KENO_MAX_NUMBER + 1, dtype=np.int32)
    recent_counts = np.zeros(KENO_MAX_NUMBER + 1, dtype=np.int32)
    recent_q: deque[list[int]] = deque()
    total_seen = 0

    def add_history(nums: list[int]) -> None:
        nonlocal total_seen
        total_seen += 1
        for n in nums:
            all_counts[int(n)] += 1
            recent_counts[int(n)] += 1
        recent_q.append(list(nums))
        if recent_draws > 0 and len(recent_q) > int(recent_draws):
            old = recent_q.popleft()
            for n in old:
                recent_counts[int(n)] -= 1

    # Initialize with first draw.
    add_history(keno_numbers[0])

    hits_baseline: dict[int, list[int]] = defaultdict(list)
    hits_rules: dict[int, list[int]] = defaultdict(list)

    # Rule accuracy tracking
    per_rule_counts: dict[str, tuple[int, int]] = defaultdict(lambda: (0, 0))
    ex_trials = 0
    ex_correct = 0
    in_trials = 0
    in_correct = 0

    for i in range(1, len(keno.dates)):
        if i >= start_index:
            scores = _compute_weighted_frequency_scores(
                all_counts=all_counts,
                total_seen=total_seen,
                recent_counts=recent_counts,
                recent_seen=len(recent_q),
                recent_weight=recent_weight,
            )
            ranked_base = _rank_from_scores(scores)

            target_date = keno.dates[i]
            actual = set(keno_numbers[i])

            excluded: set[int] = set()
            included: set[int] = set()

            fired_exclusions: list[CrossGameRule] = []
            fired_inclusions: list[CrossGameRule] = []

            for rule in rules:
                if rule.target != "KENO":
                    continue
                src = sources.get(rule.source)
                if src is None:
                    continue

                src_i = _align_latest_source_index(src.dates, target_date, int(rule.lag_days))
                if src_i is None:
                    continue

                fired = False
                if rule.trigger_kind == "number":
                    trig_num = int(rule.trigger)
                    if 1 <= trig_num <= src.pool_max and int(src.presence[src_i, trig_num]) == 1:
                        fired = True
                elif rule.trigger_kind == "ordered_value":
                    if src.ordered_numbers is None:
                        continue
                    label, value = _parse_ordered_value_trigger(rule.trigger)
                    pos_map = ordered_maps.get(rule.source)
                    if not pos_map:
                        continue
                    pos_idx = pos_map.get(label)
                    if pos_idx is None:
                        continue
                    if int(src.ordered_numbers[src_i][int(pos_idx)]) == int(value):
                        fired = True
                else:
                    # ignore unsupported trigger kinds (e.g., "keno_position")
                    continue

                if not fired:
                    continue

                if rule.kind == "exclude":
                    fired_exclusions.append(rule)
                else:
                    fired_inclusions.append(rule)

            def priority_key(r: CrossGameRule) -> tuple:
                effect = abs(math.log(max(1e-12, float(r.lift))))
                return (float(r.q_value), -effect, -int(r.support), str(r.source), int(r.lag_days), str(r.trigger))

            if max_exclusions_per_draw is not None:
                fired_exclusions.sort(key=priority_key)
                fired_exclusions = fired_exclusions[: int(max_exclusions_per_draw)]
            if max_inclusions_per_draw is not None:
                fired_inclusions.sort(key=priority_key)
                fired_inclusions = fired_inclusions[: int(max_inclusions_per_draw)]

            for rule in fired_exclusions:
                rule_id = f"{rule.source}|lag={rule.lag_days}|{rule.trigger_kind}|{rule.trigger}->{rule.target_number}"
                trials, correct = per_rule_counts[rule_id]
                ex_trials += 1
                is_correct = int(rule.target_number) not in actual
                ex_correct += int(is_correct)
                excluded.add(int(rule.target_number))
                per_rule_counts[rule_id] = (trials + 1, correct + int(is_correct))

            for rule in fired_inclusions:
                rule_id = f"{rule.source}|lag={rule.lag_days}|{rule.trigger_kind}|{rule.trigger}->{rule.target_number}"
                trials, correct = per_rule_counts[rule_id]
                in_trials += 1
                is_correct = int(rule.target_number) in actual
                in_correct += int(is_correct)
                included.add(int(rule.target_number))
                per_rule_counts[rule_id] = (trials + 1, correct + int(is_correct))

            scores_rules = scores.copy()
            if excluded and hard_exclude:
                for n in excluded:
                    scores_rules[int(n)] = -1e9
            if included and include_multiplier != 1.0:
                for n in included:
                    scores_rules[int(n)] *= float(include_multiplier)

            ranked_rules = _rank_from_scores(scores_rules)

            for k in keno_types:
                ticket_base = set(ranked_base[: int(k)])
                ticket_rules = set(ranked_rules[: int(k)])
                hits_baseline[int(k)].append(len(actual.intersection(ticket_base)))
                hits_rules[int(k)].append(len(actual.intersection(ticket_rules)))

        # Add current draw to history for next prediction.
        add_history(keno_numbers[i])

    # Summaries
    by_type: dict[str, dict] = {}
    for k in sorted(set(int(x) for x in keno_types)):
        hb = hits_baseline.get(k, [])
        hr = hits_rules.get(k, [])
        mb = float(np.mean(hb)) if hb else 0.0
        mr = float(np.mean(hr)) if hr else 0.0
        summary = TypeSummary(
            keno_type=int(k),
            n_predictions=int(len(hb)),
            mean_hits_baseline=float(mb),
            mean_hits_with_rules=float(mr),
            delta_mean_hits=float(mr - mb),
        )
        by_type[f"typ_{k}"] = asdict(summary)

    # Aggregate accuracy
    ex_acc = float(ex_correct / ex_trials) if ex_trials else 0.0
    in_acc = float(in_correct / in_trials) if in_trials else 0.0
    rule_accuracy = {
        "exclusion": asdict(
            RuleAccuracy(
                trials=int(ex_trials),
                correct=int(ex_correct),
                accuracy=float(ex_acc),
                baseline=float(BASE_ABSENCE),
                lift=float(ex_acc - float(BASE_ABSENCE)),
            )
        ),
        "inclusion": asdict(
            RuleAccuracy(
                trials=int(in_trials),
                correct=int(in_correct),
                accuracy=float(in_acc),
                baseline=float(BASE_PRESENCE),
                lift=float(in_acc - float(BASE_PRESENCE)),
            )
        ),
    }

    by_rule_out: dict[str, dict] = {}
    for rule_id, (t, c) in per_rule_counts.items():
        acc = float(c / t) if t else 0.0
        by_rule_out[str(rule_id)] = {"trials": int(t), "correct": int(c), "accuracy": float(acc)}

    payload = CrossGameRuleBacktestPayload(
        analysis="cross_game_rule_layer_backtest",
        generated_at=datetime.now().isoformat(),
        draws={
            "keno_count": int(len(keno.dates)),
            "keno_start": str(keno.dates[0]),
            "keno_end": str(keno.dates[-1]),
        },
        config={
            "keno_types": [int(x) for x in keno_types],
            "start_index": int(start_index),
            "recent_draws": int(recent_draws),
            "recent_weight": float(recent_weight),
            "hard_exclude": bool(hard_exclude),
            "include_multiplier": float(include_multiplier),
            "max_exclusions_per_draw": int(max_exclusions_per_draw)
            if max_exclusions_per_draw is not None
            else None,
            "max_inclusions_per_draw": int(max_inclusions_per_draw)
            if max_inclusions_per_draw is not None
            else None,
        },
        rules={
            "count": int(len(rules)),
            "by_rule": by_rule_out,
        },
        rule_accuracy=rule_accuracy,
        by_type=by_type,
    )
    return payload


__all__ = [
    "CrossGameRule",
    "CrossGameRuleBacktestPayload",
    "backtest_cross_game_rule_layer",
]
