"""Walk-forward backtest for ticket suggestion models."""

from __future__ import annotations

import json
import math
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class HitDistribution:
    """Observed vs expected hit distribution for one keno_type."""

    keno_type: int
    observed_counts: dict[int, int]  # hits -> count
    expected_counts: dict[int, float]  # hits -> expected count (null)
    chi2_statistic: Optional[float]
    chi2_p_value: Optional[float]
    bins_used: int
    note: str = ""


@dataclass(frozen=True)
class TicketBacktestResult:
    keno_type: int
    n_predictions: int
    start_index: int
    recent_draws: int
    recent_weight: float
    mean_hits: float
    expected_mean_hits: float
    mean_hits_z: Optional[float]
    mean_hits_p_value: Optional[float]
    near_miss_hits: int  # k-1
    near_miss_count: int
    expected_near_miss_count: float
    near_miss_p_value: Optional[float]
    jackpot_hits: int  # k
    jackpot_count: int
    expected_jackpot_count: float
    jackpot_p_value: Optional[float]
    last_ticket: list[int]
    hit_distribution: HitDistribution


def _hypergeom_mean_var(*, keno_type: int, numbers_range: int = 70, numbers_drawn: int = 20) -> tuple[float, float]:
    """Mean/variance for hits when ticket size=keno_type, draw size=numbers_drawn, population=numbers_range."""
    # X ~ Hypergeom(N, K=keno_type, n=numbers_drawn) where K are "success states" (ticket numbers).
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
    """Chi-square with automatic bin merging for low expected counts."""
    # Work on sorted hit counts
    keys = sorted(expected.keys())
    obs_list = [int(observed.get(k, 0)) for k in keys]
    exp_list = [float(expected.get(k, 0.0)) for k in keys]

    # Merge adjacent bins until expected >= min_expected.
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

    # Enforce exact total match (SciPy requirement).
    if exp_arr.sum() > 0:
        exp_arr *= float(obs_arr.sum() / exp_arr.sum())

    chi2, p = stats.chisquare(obs_arr, f_exp=exp_arr)
    return float(chi2), float(p), int(len(merged_obs)), "chi-square vs exact hypergeometric null (merged bins)"


def walk_forward_backtest_weighted_frequency(
    draws: list[DrawResult],
    *,
    keno_types: list[int],
    start_index: int = 365,
    recent_draws: int = 365,
    recent_weight: float = 0.6,
    numbers_range: tuple[int, int] = (1, 70),
    numbers_drawn: int = 20,
) -> list[TicketBacktestResult]:
    """Walk-forward backtest for the weighted-frequency ticket suggester.

    For each draw i >= start_index:
      - build number scores from draws[:i]
      - pick top-k numbers per requested keno_type
      - evaluate hits against draw i
    """
    if not draws:
        raise ValueError("draws must not be empty")
    if start_index < 1:
        raise ValueError("start_index must be >= 1")
    if not 0.0 <= recent_weight <= 1.0:
        raise ValueError("recent_weight must be in [0, 1]")

    min_n, max_n = numbers_range
    if min_n != 1 or max_n != 70:
        raise ValueError("Only numbers_range (1, 70) is supported for KENO backtest")

    sorted_draws = sorted(draws, key=lambda d: d.date)
    if start_index >= len(sorted_draws):
        raise ValueError(f"start_index={start_index} must be < number of draws ({len(sorted_draws)})")

    numbers = list(range(min_n, max_n + 1))

    total_seen = 0
    all_counts = {n: 0 for n in numbers}

    recent_q: deque[list[int]] = deque()
    recent_counts = {n: 0 for n in numbers}

    # Per keno_type tracking
    hits_by_k: dict[int, list[int]] = defaultdict(list)
    last_ticket_by_k: dict[int, list[int]] = {}

    def add_history(draw_numbers: list[int]) -> None:
        nonlocal total_seen
        total_seen += 1
        for n in draw_numbers:
            all_counts[n] += 1

        if recent_draws > 0:
            if len(recent_q) >= recent_draws:
                old = recent_q.popleft()
                for n in old:
                    recent_counts[n] -= 1
            recent_q.append(draw_numbers)
            for n in draw_numbers:
                recent_counts[n] += 1

    # Prime history up to start_index
    for i in range(start_index):
        add_history(sorted_draws[i].numbers)

    for i in range(start_index, len(sorted_draws)):
        # Build scores from history (exclude current draw)
        freq_all = {n: (all_counts[n] / total_seen) for n in numbers} if total_seen > 0 else {n: 0.0 for n in numbers}

        if recent_draws > 0 and len(recent_q) > 0:
            w = len(recent_q)
            freq_recent = {n: (recent_counts[n] / w) for n in numbers}
            score = {n: recent_weight * freq_recent[n] + (1.0 - recent_weight) * freq_all[n] for n in numbers}
        else:
            score = freq_all

        # Match `rank_numbers_weighted_frequency` tie-breaking:
        # sort by score desc; ties -> smaller number first.
        ranked = sorted(numbers, key=lambda n: (-score[n], n))

        draw_set = set(sorted_draws[i].numbers)
        for k in keno_types:
            ticket = ranked[:k]
            last_ticket_by_k[k] = ticket
            hits = len(draw_set.intersection(ticket))
            hits_by_k[k].append(int(hits))

        # Update history with current draw for next step
        add_history(sorted_draws[i].numbers)

    results: list[TicketBacktestResult] = []
    n_predictions = len(sorted_draws) - start_index

    for k in sorted(set(keno_types)):
        hits_list = hits_by_k.get(k, [])
        if len(hits_list) != n_predictions:
            raise RuntimeError(f"Internal error: hits length mismatch for k={k}")

        mean_hits = float(np.mean(hits_list)) if hits_list else 0.0
        expected_mean, var = _hypergeom_mean_var(keno_type=k, numbers_range=max_n, numbers_drawn=numbers_drawn)

        mean_z = None
        mean_p = None
        if hits_list and var > 0:
            se = math.sqrt(var / len(hits_list))
            if se > 0:
                mean_z = float((mean_hits - expected_mean) / se)
                mean_p = float(2.0 * stats.norm.sf(abs(mean_z)))

        # Near-miss / jackpot counts
        near_hits = k - 1
        jack_hits = k
        near_count = int(sum(1 for h in hits_list if h == near_hits))
        jack_count = int(sum(1 for h in hits_list if h == jack_hits))

        probs = KENO_PROBABILITIES.get(k)
        if not probs:
            raise ValueError(f"Unsupported keno_type for null model: {k}")

        p_near = float(probs.get(near_hits, 0.0))
        p_jack = float(probs.get(jack_hits, 0.0))

        exp_near = p_near * len(hits_list)
        exp_jack = p_jack * len(hits_list)

        near_p = float(stats.binomtest(near_count, n=len(hits_list), p=p_near).pvalue) if hits_list else None
        jack_p = float(stats.binomtest(jack_count, n=len(hits_list), p=p_jack).pvalue) if hits_list else None

        # Hit distribution
        obs_counts = {m: 0 for m in range(0, k + 1)}
        for h in hits_list:
            if 0 <= h <= k:
                obs_counts[int(h)] += 1

        exp_counts = {m: float(probs.get(m, 0.0)) * len(hits_list) for m in range(0, k + 1)}
        chi2, chi2_p, bins_used, note = _chi_square_from_counts(obs_counts, exp_counts)

        distribution = HitDistribution(
            keno_type=k,
            observed_counts=obs_counts,
            expected_counts=exp_counts,
            chi2_statistic=chi2,
            chi2_p_value=chi2_p,
            bins_used=bins_used,
            note=note,
        )

        results.append(
            TicketBacktestResult(
                keno_type=int(k),
                n_predictions=len(hits_list),
                start_index=int(start_index),
                recent_draws=int(recent_draws),
                recent_weight=float(recent_weight),
                mean_hits=mean_hits,
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
                last_ticket=last_ticket_by_k.get(k, []),
                hit_distribution=distribution,
            )
        )

    return results


def save_backtest_json(
    results: list[TicketBacktestResult],
    *,
    output_path: str | Path,
    draws_path: Optional[str] = None,
) -> None:
    payload = {
        "analysis": "ticket_backtest",
        "generated_at": datetime.now().isoformat(),
        "draws_path": draws_path,
        "results": [asdict(r) for r in results],
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


__all__ = [
    "HitDistribution",
    "TicketBacktestResult",
    "walk_forward_backtest_weighted_frequency",
    "save_backtest_json",
]
