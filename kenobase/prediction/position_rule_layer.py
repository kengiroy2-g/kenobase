"""Position-based next-day rule layer for KENO.

This module mines conditional patterns of the form:

  Trigger:  (number X appears at position P today)
  Target:   (number Y appears tomorrow)  -> inclusion
            (number Y is absent tomorrow) -> exclusion

The intent is pragmatic: use the observed conditional structure as a predictive
layer (filters/boosts) on top of an existing ranking model.

Important
---------
If draws are truly uniform random (20 of 70 without replacement), then:
- P(Y in next draw | any trigger) == 20/70, and
- P(Y not in next draw | any trigger) == 50/70,
up to sampling noise.
In that case, this layer should not deliver consistent out-of-sample lift.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np

from kenobase.core.data_loader import DrawResult, GameType

KENO_MIN_NUMBER = 1
KENO_MAX_NUMBER = 70
KENO_DRAW_SIZE = 20
KENO_POSITIONS = 20

# Baseline marginal probabilities under a uniform null model (one draw):
BASE_PRESENCE = KENO_DRAW_SIZE / KENO_MAX_NUMBER  # 20/70
BASE_ABSENCE = 1.0 - BASE_PRESENCE  # 50/70


def trigger_index(number: int, position: int) -> int:
    """Map (number, position) to a compact index in [0, 1400)."""
    if not (KENO_MIN_NUMBER <= number <= KENO_MAX_NUMBER):
        raise ValueError(f"number must be in [{KENO_MIN_NUMBER}, {KENO_MAX_NUMBER}], got {number}")
    if not (1 <= position <= KENO_POSITIONS):
        raise ValueError(f"position must be in [1, {KENO_POSITIONS}], got {position}")
    return (position - 1) * KENO_MAX_NUMBER + (number - 1)


def index_to_trigger(idx: int) -> tuple[int, int]:
    """Inverse of trigger_index()."""
    if idx < 0 or idx >= KENO_POSITIONS * KENO_MAX_NUMBER:
        raise ValueError(f"idx out of range: {idx}")
    position = idx // KENO_MAX_NUMBER + 1
    number = idx % KENO_MAX_NUMBER + 1
    return number, position


def extract_ordered_keno_numbers(draw: DrawResult) -> list[int]:
    """Extract ordered KENO numbers (positions 1..20) from a DrawResult.

    The DataLoader stores the original order in `metadata["numbers_ordered"]`.
    If it's missing (older artifacts), this falls back to `draw.numbers`, which
    are sorted and therefore not usable for position analyses.
    """
    if draw.game_type != GameType.KENO:
        raise ValueError(f"Expected KENO draw, got {draw.game_type}")

    ordered = draw.metadata.get("numbers_ordered")
    if isinstance(ordered, list) and len(ordered) == KENO_DRAW_SIZE and all(
        isinstance(x, int) for x in ordered
    ):
        return ordered

    # Fallback (sorted): keep it explicit so callers can decide what to do.
    return list(draw.numbers)


def wilson_lower_bound(successes: int, n: int, *, z: float = 1.959963984540054) -> float:
    """Wilson score lower bound for a binomial proportion.

    Args:
        successes: number of successes
        n: number of trials
        z: z-value (default: 1.96 for ~95% CI)
    """
    if n <= 0:
        return 0.0
    if successes < 0 or successes > n:
        raise ValueError(f"successes must be in [0, n], got {successes} (n={n})")

    phat = successes / n
    denom = 1.0 + (z * z) / n
    center = (phat + (z * z) / (2.0 * n)) / denom
    margin = (z * math.sqrt((phat * (1.0 - phat) + (z * z) / (4.0 * n)) / n)) / denom
    return float(max(0.0, center - margin))


@dataclass(frozen=True)
class RuleCandidate:
    """One candidate target number for a trigger."""

    number: int
    probability: float
    lower_bound: float
    support: int


@dataclass(frozen=True)
class RuleFiring:
    """A fired rule for a specific day."""

    trigger_number: int
    trigger_position: int
    kind: str  # "exclude" or "include"
    predicted_number: int
    probability: float
    lower_bound: float
    support: int


@dataclass(frozen=True)
class Transition:
    """One next-day transition used for rolling statistics."""

    trigger_indices: np.ndarray  # shape (20,)
    next_numbers: np.ndarray  # shape (20,)


class RollingPositionRuleMiner:
    """Mine trigger->target conditional stats in a rolling window of transitions."""

    def __init__(
        self,
        *,
        window_size: int = 365,
    ) -> None:
        if window_size < 1:
            raise ValueError("window_size must be >= 1")
        self.window_size = int(window_size)

        self._n_triggers = KENO_POSITIONS * KENO_MAX_NUMBER  # 1400
        self._support = np.zeros(self._n_triggers, dtype=np.int32)
        self._present = np.zeros((self._n_triggers, KENO_MAX_NUMBER + 1), dtype=np.int32)  # [0..70]
        self._transitions: deque[Transition] = deque()

    @property
    def n_transitions(self) -> int:
        return int(len(self._transitions))

    def _add_counts(self, trigger_indices: np.ndarray, next_numbers: np.ndarray) -> None:
        self._support[trigger_indices] += 1
        for num in next_numbers:
            self._present[trigger_indices, int(num)] += 1

    def _remove_counts(self, trigger_indices: np.ndarray, next_numbers: np.ndarray) -> None:
        self._support[trigger_indices] -= 1
        for num in next_numbers:
            self._present[trigger_indices, int(num)] -= 1

    def add_transition(self, *, today_ordered: Iterable[int], tomorrow_numbers: Iterable[int]) -> None:
        """Add one (today -> tomorrow) transition to the rolling window."""
        today = list(today_ordered)
        tomorrow = list(tomorrow_numbers)
        if len(today) != KENO_DRAW_SIZE:
            raise ValueError(f"today_ordered must have {KENO_DRAW_SIZE} numbers, got {len(today)}")
        if len(tomorrow) != KENO_DRAW_SIZE:
            raise ValueError(f"tomorrow_numbers must have {KENO_DRAW_SIZE} numbers, got {len(tomorrow)}")

        trigger_indices = np.asarray(
            [trigger_index(int(num), pos) for pos, num in enumerate(today, start=1)],
            dtype=np.int32,
        )
        next_numbers = np.asarray([int(x) for x in tomorrow], dtype=np.int32)

        transition = Transition(trigger_indices=trigger_indices, next_numbers=next_numbers)
        self._transitions.append(transition)
        self._add_counts(trigger_indices, next_numbers)

        while len(self._transitions) > self.window_size:
            old = self._transitions.popleft()
            self._remove_counts(old.trigger_indices, old.next_numbers)

    def trigger_support(self, number: int, position: int) -> int:
        """Return support count for a given trigger within the rolling window."""
        idx = trigger_index(number, position)
        return int(self._support[idx])

    def _get_counts_for_trigger(self, number: int, position: int) -> tuple[int, np.ndarray]:
        idx = trigger_index(number, position)
        n = int(self._support[idx])
        counts = self._present[idx]  # view
        return n, counts

    def exclusion_candidates(
        self,
        *,
        trigger_number: int,
        trigger_position: int,
        max_candidates: int = 3,
        min_support: int = 10,
        min_lower_bound: float = 0.90,
        z: float = 1.959963984540054,
    ) -> list[RuleCandidate]:
        """Numbers that are likely absent tomorrow given the trigger."""
        n, present_counts = self._get_counts_for_trigger(trigger_number, trigger_position)
        if n < int(min_support):
            return []

        candidates: list[RuleCandidate] = []
        for num in range(KENO_MIN_NUMBER, KENO_MAX_NUMBER + 1):
            present = int(present_counts[num])
            absent = n - present
            p_abs = absent / n
            lb = wilson_lower_bound(absent, n, z=z)
            if lb >= float(min_lower_bound):
                candidates.append(
                    RuleCandidate(number=num, probability=float(p_abs), lower_bound=float(lb), support=n)
                )

        candidates.sort(key=lambda c: (-c.lower_bound, -c.probability, c.number))
        return candidates[: int(max_candidates)]

    def inclusion_candidates(
        self,
        *,
        trigger_number: int,
        trigger_position: int,
        max_candidates: int = 5,
        min_support: int = 10,
        min_lower_bound: float = 0.40,
        z: float = 1.959963984540054,
    ) -> list[RuleCandidate]:
        """Numbers that are likely present tomorrow given the trigger."""
        n, present_counts = self._get_counts_for_trigger(trigger_number, trigger_position)
        if n < int(min_support):
            return []

        candidates: list[RuleCandidate] = []
        for num in range(KENO_MIN_NUMBER, KENO_MAX_NUMBER + 1):
            present = int(present_counts[num])
            p_inc = present / n
            lb = wilson_lower_bound(present, n, z=z)
            if lb >= float(min_lower_bound):
                candidates.append(
                    RuleCandidate(number=num, probability=float(p_inc), lower_bound=float(lb), support=n)
                )

        candidates.sort(key=lambda c: (-c.lower_bound, -c.probability, c.number))
        return candidates[: int(max_candidates)]

    def fire_rules_for_ordered_draw(
        self,
        ordered_numbers: list[int],
        *,
        exclude_max: int = 3,
        include_max: int = 5,
        min_support: int = 10,
        exclude_lb: float = 0.90,
        include_lb: float = 0.40,
        z: float = 1.959963984540054,
    ) -> tuple[list[RuleFiring], list[RuleFiring]]:
        """Fire exclusion/inclusion rules for a given ordered draw (today)."""
        if len(ordered_numbers) != KENO_DRAW_SIZE:
            raise ValueError(f"ordered_numbers must have {KENO_DRAW_SIZE} numbers, got {len(ordered_numbers)}")

        exclusion_firings: list[RuleFiring] = []
        inclusion_firings: list[RuleFiring] = []

        for position, trig_num in enumerate(ordered_numbers, start=1):
            trig_num = int(trig_num)

            for cand in self.exclusion_candidates(
                trigger_number=trig_num,
                trigger_position=position,
                max_candidates=exclude_max,
                min_support=min_support,
                min_lower_bound=exclude_lb,
                z=z,
            ):
                exclusion_firings.append(
                    RuleFiring(
                        trigger_number=trig_num,
                        trigger_position=position,
                        kind="exclude",
                        predicted_number=cand.number,
                        probability=cand.probability,
                        lower_bound=cand.lower_bound,
                        support=cand.support,
                    )
                )

            for cand in self.inclusion_candidates(
                trigger_number=trig_num,
                trigger_position=position,
                max_candidates=include_max,
                min_support=min_support,
                min_lower_bound=include_lb,
                z=z,
            ):
                inclusion_firings.append(
                    RuleFiring(
                        trigger_number=trig_num,
                        trigger_position=position,
                        kind="include",
                        predicted_number=cand.number,
                        probability=cand.probability,
                        lower_bound=cand.lower_bound,
                        support=cand.support,
                    )
                )

        return exclusion_firings, inclusion_firings


def apply_rule_layer_to_scores(
    base_presence_scores: np.ndarray,
    *,
    exclusions: Iterable[RuleFiring],
    inclusions: Iterable[RuleFiring],
    hard_exclude: bool = True,
    hard_exclude_lb: float = 0.95,
    exclude_weight: float = 2.0,
    include_weight: float = 1.0,
    eps: float = 1e-9,
) -> tuple[np.ndarray, set[int], set[int]]:
    """Apply fired rules as a filter/boost layer on top of per-number presence scores.

    Args:
        base_presence_scores: array shape (71,), index 1..70 holds estimated marginal P(number in next draw).
        exclusions: fired exclusion rules (kind="exclude") with lower_bound meaning P(absent) lower CI bound.
        inclusions: fired inclusion rules (kind="include") with lower_bound meaning P(present) lower CI bound.
        hard_exclude: if True, numbers with very high exclusion confidence are removed from ranking.
        hard_exclude_lb: minimum exclusion lower bound to hard-exclude.
        exclude_weight: strength for exclusion evidence (log space, negative contribution).
        include_weight: strength for inclusion evidence (log space, positive contribution).
        eps: numerical stability.

    Returns:
        (adjusted_scores, excluded_numbers, included_numbers)
    """
    if base_presence_scores.shape != (KENO_MAX_NUMBER + 1,):
        raise ValueError(f"base_presence_scores must have shape (71,), got {base_presence_scores.shape}")

    p0 = float(BASE_PRESENCE)
    log_p0 = math.log(max(eps, p0))

    adjusted = np.log(np.clip(base_presence_scores, eps, 1.0))

    excluded: set[int] = set()
    included: set[int] = set()

    # Inclusion: use conservative lower bound on P(present | trigger).
    for firing in inclusions:
        num = int(firing.predicted_number)
        included.add(num)
        p_present_lb = float(min(1.0 - eps, max(eps, firing.lower_bound)))
        adjusted[num] += float(include_weight) * (math.log(p_present_lb) - log_p0)

    # Exclusion: lower_bound is for P(absent | trigger). This implies an upper bound on presence.
    for firing in exclusions:
        num = int(firing.predicted_number)
        excluded.add(num)
        p_abs_lb = float(min(1.0 - eps, max(eps, firing.lower_bound)))
        p_present_ub = float(min(1.0 - eps, max(eps, 1.0 - p_abs_lb)))
        adjusted[num] += float(exclude_weight) * (math.log(p_present_ub) - log_p0)

    if hard_exclude:
        for firing in exclusions:
            if float(firing.lower_bound) >= float(hard_exclude_lb):
                adjusted[int(firing.predicted_number)] = -1e9

    return adjusted, excluded, included


__all__ = [
    "BASE_ABSENCE",
    "BASE_PRESENCE",
    "KENO_DRAW_SIZE",
    "KENO_MAX_NUMBER",
    "KENO_MIN_NUMBER",
    "KENO_POSITIONS",
    "RollingPositionRuleMiner",
    "RuleCandidate",
    "RuleFiring",
    "apply_rule_layer_to_scores",
    "extract_ordered_keno_numbers",
    "index_to_trigger",
    "trigger_index",
    "wilson_lower_bound",
]

