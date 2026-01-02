"""Cross-lottery coupling analysis (KENO / LOTTO / EuroJackpot).

Goal
----
Explore whether there are statistically robust, *time-shifted* dependencies between
draws of different lottery games (e.g., KENO today -> LOTTO next draw), and whether
pair/group structures overlap more than expected.

This is an exploratory analysis layer. It provides:
- date alignment (event-based, lag in days),
- conditional lift tables with Fisher exact tests + BH/FDR correction,
- within-game pair lift tables and cross-game overlap tests,
- jackpot-conditioned overlap checks (requires jackpot indicator columns).

Important
---------
Many tests are run in parallel (multiple comparisons). Always rely on out-of-sample
checks and FDR-adjusted p-values (`q_value`) to avoid false discoveries.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from itertools import combinations
from typing import Iterable, Optional

import numpy as np
from scipy import stats

from kenobase.prediction.position_rule_layer import KENO_MAX_NUMBER, KENO_POSITIONS, trigger_index


def bh_fdr(p_values: np.ndarray) -> np.ndarray:
    """Benjamini–Hochberg FDR correction (returns q-values).

    Args:
        p_values: array-like of p-values in [0, 1]
    """
    p = np.asarray(p_values, dtype=float)
    if p.ndim != 1:
        raise ValueError("p_values must be 1D")
    if p.size == 0:
        return p
    if np.any((p < 0.0) | (p > 1.0) | ~np.isfinite(p)):
        raise ValueError("p_values must be finite and within [0, 1]")

    m = int(p.size)
    order = np.argsort(p)
    ranks = np.empty(m, dtype=float)
    ranks[order] = np.arange(1, m + 1, dtype=float)

    q = p * (m / ranks)
    q_sorted = q[order]
    q_sorted = np.minimum.accumulate(q_sorted[::-1])[::-1]
    q_sorted = np.clip(q_sorted, 0.0, 1.0)

    out = np.empty_like(q_sorted)
    out[order] = q_sorted
    return out


@dataclass(frozen=True)
class GameDraws:
    """In-memory representation of one game's draws."""

    name: str
    pool_max: int
    draw_size: int
    dates: list[date]
    presence: np.ndarray  # shape (n_draws, pool_max+1), bool/int, index 1..pool_max
    ordered_numbers: Optional[list[list[int]]] = None  # KENO only
    jackpot_winners: Optional[dict[date, int]] = None  # optional

    def __post_init__(self) -> None:
        if self.presence.shape[0] != len(self.dates):
            raise ValueError("presence rows must match number of dates")
        if self.presence.shape[1] != self.pool_max + 1:
            raise ValueError("presence columns must be pool_max+1 (including index 0)")
        if self.ordered_numbers is not None and len(self.ordered_numbers) != len(self.dates):
            raise ValueError("ordered_numbers length must match dates")


@dataclass(frozen=True)
class ConditionalLift:
    source: str
    target: str
    lag_days: int
    trigger_kind: str  # "number" or "keno_position"
    trigger: str  # e.g. "49" or "49@1"
    target_number: int
    support: int
    base_rate: float
    conditional_rate: float
    lift: float
    p_value: float
    q_value: float


@dataclass(frozen=True)
class PairLift:
    game: str
    pool_max: int
    draw_size: int
    pair: tuple[int, int]
    observed: int
    expected: float
    lift: float


@dataclass(frozen=True)
class PairOverlapResult:
    range_max: int
    top_k: int
    universe_pairs: int
    overlap: int
    expected_overlap: float
    p_value: float
    games: list[str]


@dataclass(frozen=True)
class JackpotOverlapResult:
    source: str
    target: str
    n_total: int
    n_jackpot: int
    mean_overlap_jackpot: float
    mean_overlap_non_jackpot: float
    delta: float
    p_value: Optional[float]


def _align_source_to_target(
    *,
    source_dates: list[date],
    target_dates: list[date],
    lag_days: int,
) -> list[tuple[int, int]]:
    """Align each target draw to the latest source draw <= (target_date - lag_days)."""
    if not source_dates or not target_dates:
        return []
    if lag_days < 0:
        raise ValueError("lag_days must be >= 0")

    pairs: list[tuple[int, int]] = []
    for t_i, t_date in enumerate(target_dates):
        desired = t_date - timedelta(days=int(lag_days))
        s_i = bisect_right(source_dates, desired) - 1
        if s_i >= 0:
            pairs.append((s_i, t_i))
    return pairs


def _presence_matrix(draws: GameDraws, indices: Iterable[int]) -> np.ndarray:
    idx = np.fromiter((int(i) for i in indices), dtype=np.int64)
    return draws.presence[idx]


def conditional_lifts_number_triggers(
    *,
    source: GameDraws,
    target: GameDraws,
    lag_days: int,
    min_support: int = 30,
    max_results: int = 50,
    alpha_fdr: float = 0.05,
    filter_by_alpha: bool = True,
) -> list[ConditionalLift]:
    """Compute conditional lifts P(target_n | source_m) vs base P(target_n).

    Uses Fisher exact test per (m,n) and BH/FDR correction across all pairs.
    """
    pairs = _align_source_to_target(source_dates=source.dates, target_dates=target.dates, lag_days=lag_days)
    if not pairs:
        return []

    s_idx, t_idx = zip(*pairs, strict=False)
    X = _presence_matrix(source, s_idx)[:, 1 : source.pool_max + 1].astype(np.int16, copy=False)
    Y = _presence_matrix(target, t_idx)[:, 1 : target.pool_max + 1].astype(np.int16, copy=False)

    n_pairs = int(X.shape[0])
    support = X.sum(axis=0)  # (source_pool,)
    target_totals = Y.sum(axis=0)  # (target_pool,)
    base_rate = target_totals / max(1, n_pairs)

    present = X.T @ Y  # (source_pool, target_pool)

    # Fisher exact p-values for triggers with enough support.
    p_values: list[float] = []
    meta: list[tuple[int, int, int, float, float, float]] = []
    # store: (m_idx, n_idx, support_m, base_rate_n, cond_rate, lift)
    for m0 in range(source.pool_max):
        sup = int(support[m0])
        if sup < int(min_support):
            continue
        a_row = present[m0]
        for n0 in range(target.pool_max):
            a = int(a_row[n0])
            if sup == 0:
                continue
            b = sup - a
            c = int(target_totals[n0]) - a
            d = (n_pairs - sup) - c
            if d < 0:
                # Should not happen, but guard against numeric inconsistencies.
                continue

            _, p = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")
            p_values.append(float(p))

            cond_rate = a / sup if sup > 0 else 0.0
            lift = (cond_rate / base_rate[n0]) if base_rate[n0] > 0 else 0.0
            meta.append((m0 + 1, n0 + 1, sup, float(base_rate[n0]), float(cond_rate), float(lift)))

    if not p_values:
        return []

    q = bh_fdr(np.asarray(p_values, dtype=float))

    lifts: list[ConditionalLift] = [
        ConditionalLift(
            source=source.name,
            target=target.name,
            lag_days=int(lag_days),
            trigger_kind="number",
            trigger=str(m),
            target_number=int(n),
            support=int(sup),
            base_rate=float(p0),
            conditional_rate=float(p1),
            lift=float(lift),
            p_value=float(pv),
            q_value=float(qv),
        )
        for (m, n, sup, p0, p1, lift), pv, qv in zip(meta, p_values, q, strict=False)
    ]

    if filter_by_alpha:
        lifts = [r for r in lifts if float(r.q_value) <= float(alpha_fdr)]

    lifts.sort(key=lambda r: (r.q_value, -abs(math.log(max(1e-12, r.lift))), -r.support, r.trigger, r.target_number))
    return lifts[: int(max_results)]


def conditional_lifts_keno_position_triggers(
    *,
    keno: GameDraws,
    target: GameDraws,
    lag_days: int,
    min_support: int = 20,
    max_results: int = 50,
    alpha_fdr: float = 0.05,
    filter_by_alpha: bool = True,
) -> list[ConditionalLift]:
    """Conditional lifts with KENO (number@position) triggers.

    Only meaningful if `keno.ordered_numbers` is present.
    """
    if keno.ordered_numbers is None:
        return []

    pairs = _align_source_to_target(source_dates=keno.dates, target_dates=target.dates, lag_days=lag_days)
    if not pairs:
        return []

    s_idx, t_idx = zip(*pairs, strict=False)
    ordered = [keno.ordered_numbers[i] for i in s_idx]

    n_pairs = len(ordered)
    n_triggers = KENO_POSITIONS * KENO_MAX_NUMBER  # 1400
    X = np.zeros((n_pairs, n_triggers), dtype=np.int8)
    for i, nums in enumerate(ordered):
        if len(nums) != KENO_POSITIONS:
            raise ValueError("KENO ordered_numbers must have 20 values per draw")
        for pos, num in enumerate(nums, start=1):
            X[i, trigger_index(int(num), int(pos))] = 1

    Y = _presence_matrix(target, t_idx)[:, 1 : target.pool_max + 1].astype(np.int16, copy=False)
    support = X.sum(axis=0)
    target_totals = Y.sum(axis=0)
    base_rate = target_totals / max(1, n_pairs)

    present = X.T.astype(np.int16) @ Y  # (1400, target_pool)

    p_values: list[float] = []
    meta: list[tuple[int, int, int, float, float, float]] = []
    for trig_idx in range(n_triggers):
        sup = int(support[trig_idx])
        if sup < int(min_support):
            continue
        a_row = present[trig_idx]
        trig_num = (trig_idx % KENO_MAX_NUMBER) + 1
        trig_pos = (trig_idx // KENO_MAX_NUMBER) + 1
        trig_label = f"{trig_num}@{trig_pos}"
        for n0 in range(target.pool_max):
            a = int(a_row[n0])
            b = sup - a
            c = int(target_totals[n0]) - a
            d = (n_pairs - sup) - c
            if d < 0:
                continue
            _, p = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")
            p_values.append(float(p))
            cond_rate = a / sup if sup > 0 else 0.0
            lift = (cond_rate / base_rate[n0]) if base_rate[n0] > 0 else 0.0
            meta.append((trig_label, n0 + 1, sup, float(base_rate[n0]), float(cond_rate), float(lift)))

    if not p_values:
        return []

    q = bh_fdr(np.asarray(p_values, dtype=float))
    lifts: list[ConditionalLift] = [
        ConditionalLift(
            source=keno.name,
            target=target.name,
            lag_days=int(lag_days),
            trigger_kind="keno_position",
            trigger=str(trig_label),
            target_number=int(n),
            support=int(sup),
            base_rate=float(p0),
            conditional_rate=float(p1),
            lift=float(lift),
            p_value=float(pv),
            q_value=float(qv),
        )
        for (trig_label, n, sup, p0, p1, lift), pv, qv in zip(meta, p_values, q, strict=False)
    ]

    if filter_by_alpha:
        lifts = [r for r in lifts if float(r.q_value) <= float(alpha_fdr)]

    lifts.sort(key=lambda r: (r.q_value, -abs(math.log(max(1e-12, r.lift))), -r.support, r.trigger, r.target_number))
    return lifts[: int(max_results)]


def conditional_lifts_ordered_value_triggers(
    *,
    source: GameDraws,
    target: GameDraws,
    lag_days: int,
    position_labels: Optional[list[str]] = None,
    min_support: int = 20,
    max_results: int = 50,
    alpha_fdr: float = 0.05,
    filter_by_alpha: bool = True,
) -> list[ConditionalLift]:
    """Compute conditional lifts using ordered (position,value) triggers.

    This supports games where a draw is an ordered vector of small-domain integer values
    (e.g., Eurowette outcomes `T1..T13` with values 0/1/2, or Glücksspirale fields).

    Trigger format is `<pos_label>=<value>` (e.g., `T5=2`).
    """
    if source.ordered_numbers is None:
        return []

    pairs = _align_source_to_target(source_dates=source.dates, target_dates=target.dates, lag_days=lag_days)
    if not pairs:
        return []

    s_idx, t_idx = zip(*pairs, strict=False)
    ordered = [source.ordered_numbers[i] for i in s_idx]
    if not ordered:
        return []

    positions = len(ordered[0])
    for row in ordered:
        if len(row) != positions:
            raise ValueError("source ordered_numbers must have consistent row length")

    if position_labels is not None:
        if len(position_labels) != positions:
            raise ValueError("position_labels must match number of positions in ordered_numbers")
        labels = list(position_labels)
    else:
        labels = [str(i) for i in range(1, positions + 1)]

    Y = _presence_matrix(target, t_idx)[:, 1 : target.pool_max + 1].astype(np.int16, copy=False)
    n_pairs = int(Y.shape[0])
    target_totals = Y.sum(axis=0)  # (target_pool,)
    base_rate = target_totals / max(1, n_pairs)

    # Count support and co-occurrences (a) for each trigger.
    support: dict[str, int] = {}
    co_counts: dict[str, np.ndarray] = {}

    for i, row in enumerate(ordered):
        present_targets = np.nonzero(Y[i])[0]
        if present_targets.size == 0:
            continue
        for pos, raw_value in enumerate(row):
            if raw_value is None:
                continue
            try:
                value = int(raw_value)
            except Exception:
                continue
            trigger = f"{labels[pos]}={value}"
            support[trigger] = support.get(trigger, 0) + 1
            counts = co_counts.get(trigger)
            if counts is None:
                counts = np.zeros((target.pool_max,), dtype=np.int32)
                co_counts[trigger] = counts
            counts[present_targets] += 1

    # Fisher exact p-values
    p_values: list[float] = []
    meta: list[tuple[str, int, int, float, float, float]] = []
    for trigger, sup in support.items():
        if int(sup) < int(min_support):
            continue
        a_row = co_counts.get(trigger)
        if a_row is None:
            continue
        for n0 in range(target.pool_max):
            a = int(a_row[n0])
            b = int(sup) - a
            c = int(target_totals[n0]) - a
            d = (n_pairs - int(sup)) - c
            if d < 0:
                continue
            _, p = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")
            p_values.append(float(p))
            cond_rate = a / int(sup) if sup > 0 else 0.0
            lift = (cond_rate / base_rate[n0]) if base_rate[n0] > 0 else 0.0
            meta.append((trigger, n0 + 1, int(sup), float(base_rate[n0]), float(cond_rate), float(lift)))

    if not p_values:
        return []

    q = bh_fdr(np.asarray(p_values, dtype=float))
    lifts: list[ConditionalLift] = [
        ConditionalLift(
            source=source.name,
            target=target.name,
            lag_days=int(lag_days),
            trigger_kind="ordered_value",
            trigger=str(trig),
            target_number=int(n),
            support=int(sup),
            base_rate=float(p0),
            conditional_rate=float(p1),
            lift=float(lift),
            p_value=float(pv),
            q_value=float(qv),
        )
        for (trig, n, sup, p0, p1, lift), pv, qv in zip(meta, p_values, q, strict=False)
    ]

    if filter_by_alpha:
        lifts = [r for r in lifts if float(r.q_value) <= float(alpha_fdr)]

    lifts.sort(key=lambda r: (r.q_value, -abs(math.log(max(1e-12, r.lift))), -r.support, r.trigger, r.target_number))
    return lifts[: int(max_results)]


def top_pairs_by_lift(
    *,
    game: GameDraws,
    restrict_max: Optional[int] = None,
    top_k: int = 50,
) -> list[PairLift]:
    """Compute top co-occurring pairs by lift (observed/expected)."""
    max_n = int(restrict_max) if restrict_max is not None else int(game.pool_max)
    if max_n < 2:
        return []

    counts: dict[tuple[int, int], int] = {}
    for row in game.presence[:, 1 : max_n + 1]:
        nums = [i + 1 for i, v in enumerate(row, start=0) if int(v) == 1]
        for a, b in combinations(nums, 2):
            key = (int(a), int(b)) if a < b else (int(b), int(a))
            counts[key] = counts.get(key, 0) + 1

    n_draws = int(game.presence.shape[0])
    N = int(game.pool_max)
    d = int(game.draw_size)
    p_pair = (d * (d - 1)) / (N * (N - 1)) if N > 1 else 0.0
    expected = n_draws * p_pair

    lifts: list[PairLift] = []
    for pair, obs in counts.items():
        if pair[1] > max_n:
            continue
        lift = (obs / expected) if expected > 0 else 0.0
        lifts.append(
            PairLift(
                game=game.name,
                pool_max=int(game.pool_max),
                draw_size=int(game.draw_size),
                pair=(int(pair[0]), int(pair[1])),
                observed=int(obs),
                expected=float(expected),
                lift=float(lift),
            )
        )

    lifts.sort(key=lambda p: (-p.lift, -p.observed, p.pair))
    return lifts[: int(top_k)]


def pair_overlap_significance(
    *,
    pair_lists: list[list[PairLift]],
    range_max: int,
    top_k: int,
) -> PairOverlapResult:
    """Overlap significance for top-k pair lists using a hypergeometric null."""
    if len(pair_lists) < 2:
        raise ValueError("Need at least 2 pair lists")
    if range_max < 2:
        raise ValueError("range_max must be >= 2")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    universe = (range_max * (range_max - 1)) // 2
    sets: list[set[tuple[int, int]]] = []
    games: list[str] = []
    for lst in pair_lists:
        games.append(lst[0].game if lst else "unknown")
        s = {(p.pair[0], p.pair[1]) for p in lst[:top_k] if p.pair[1] <= range_max}
        sets.append(s)

    overlap_set = set.intersection(*sets)
    overlap = int(len(overlap_set))

    # For 2 lists, use exact hypergeom. For >2, approximate by sequential intersections.
    expected_overlap = float(top_k)
    p_value: float
    if len(sets) == 2:
        k1 = int(len(sets[0]))
        k2 = int(len(sets[1]))
        expected_overlap = (k1 * k2) / universe if universe > 0 else 0.0
        # P(X >= overlap)
        p_value = float(stats.hypergeom.sf(overlap - 1, universe, k1, k2))
    else:
        # Approximate: intersect sequentially and compute expected overlap via product.
        expected_overlap = float(top_k)
        for s in sets[1:]:
            expected_overlap *= (len(s) / universe) if universe > 0 else 0.0
        p_value = float("nan")

    return PairOverlapResult(
        range_max=int(range_max),
        top_k=int(top_k),
        universe_pairs=int(universe),
        overlap=overlap,
        expected_overlap=float(expected_overlap),
        p_value=float(p_value),
        games=games,
    )


def jackpot_overlap_analysis(
    *,
    source_with_jackpot: GameDraws,
    target: GameDraws,
    lag_days: int = 0,
) -> JackpotOverlapResult:
    """Compare overlap counts in target draws on jackpot vs non-jackpot source days.

    Example: source=LOTTO (jackpot days), target=KENO, lag_days=0 uses the same date.
    If lag_days=1, it uses the next day in the target game.
    """
    if not source_with_jackpot.jackpot_winners:
        raise ValueError("source_with_jackpot must have jackpot_winners mapping")

    if lag_days < 0:
        raise ValueError("lag_days must be >= 0")

    target_index = {d: i for i, d in enumerate(target.dates)}

    overlaps_j: list[int] = []
    overlaps_n: list[int] = []
    n_total = 0
    for s_i, s_date in enumerate(source_with_jackpot.dates):
        t_date = s_date + timedelta(days=int(lag_days))
        t_i = target_index.get(t_date)
        if t_i is None:
            continue

        n_total += 1
        jackpot_winners = int(source_with_jackpot.jackpot_winners.get(s_date, 0))
        src_nums = set(np.nonzero(source_with_jackpot.presence[s_i])[0].tolist())
        trg_nums = set(np.nonzero(target.presence[t_i])[0].tolist())
        overlap = int(len(src_nums.intersection(trg_nums)))
        if jackpot_winners > 0:
            overlaps_j.append(overlap)
        else:
            overlaps_n.append(overlap)

    mean_j = float(np.mean(overlaps_j)) if overlaps_j else 0.0
    mean_n = float(np.mean(overlaps_n)) if overlaps_n else 0.0
    p_value = None
    if overlaps_j and overlaps_n:
        # Non-parametric test; overlap counts are discrete.
        _, p = stats.mannwhitneyu(overlaps_j, overlaps_n, alternative="two-sided")
        p_value = float(p)

    return JackpotOverlapResult(
        source=source_with_jackpot.name,
        target=target.name,
        n_total=int(n_total),
        n_jackpot=int(len(overlaps_j)),
        mean_overlap_jackpot=mean_j,
        mean_overlap_non_jackpot=mean_n,
        delta=float(mean_j - mean_n),
        p_value=p_value,
    )


def to_jsonable(obj) -> dict:
    """Convert dataclasses / nested structures to JSON-serializable dict."""
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


__all__ = [
    "ConditionalLift",
    "GameDraws",
    "JackpotOverlapResult",
    "PairLift",
    "PairOverlapResult",
    "bh_fdr",
    "conditional_lifts_keno_position_triggers",
    "conditional_lifts_ordered_value_triggers",
    "conditional_lifts_number_triggers",
    "jackpot_overlap_analysis",
    "pair_overlap_significance",
    "top_pairs_by_lift",
    "to_jsonable",
]
