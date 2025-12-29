"""Ticket suggester for KENO types (6-9) focused on hit probability.

Important note
--------------
If the draw is uniform random (20 of 70 without replacement), *every* selection of k numbers
has the same probability for jackpot (k hits) and near-miss (k-1 hits). In that case, no
"better numbers" exist.

This module provides a pragmatic, data-driven baseline model anyway:
- Estimate per-number draw probability via weighted historical frequency.
- Suggest top-k numbers for requested k.
- Optionally compute an approximate hit distribution under an independence assumption
  (Poisson-binomial) to quantify near-miss / jackpot probabilities for the suggested ticket.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class RankedNumber:
    number: int
    score: float
    freq_all: float
    freq_recent: Optional[float]


@dataclass(frozen=True)
class TicketProbabilities:
    near_miss: float
    jackpot: float
    near_or_jackpot: float


@dataclass(frozen=True)
class TicketSuggestion:
    keno_type: int
    numbers: list[int]
    model: str
    probabilities_uniform: TicketProbabilities
    probabilities_model: Optional[TicketProbabilities] = None


def rank_numbers_weighted_frequency(
    draws: list[DrawResult],
    *,
    numbers_range: tuple[int, int] = (1, 70),
    recent_draws: int = 365,
    recent_weight: float = 0.6,
) -> list[RankedNumber]:
    """Rank numbers by a weighted mix of recent + all-time frequency.

    `freq_*` is the per-draw marginal probability estimate: P(number appears in a draw).
    """
    if not draws:
        raise ValueError("draws must not be empty")
    if not 0.0 <= recent_weight <= 1.0:
        raise ValueError("recent_weight must be between 0 and 1")

    min_n, max_n = numbers_range
    numbers = list(range(min_n, max_n + 1))

    total_draws = len(draws)
    all_counts = {n: 0 for n in numbers}
    for draw in draws:
        for n in draw.numbers:
            if n in all_counts:
                all_counts[n] += 1

    freq_all = {n: all_counts[n] / total_draws for n in numbers}

    freq_recent_map: dict[int, float] | None = None
    if recent_draws and recent_draws > 0:
        window = min(recent_draws, total_draws)
        recent_counts = {n: 0 for n in numbers}
        for draw in draws[-window:]:
            for n in draw.numbers:
                if n in recent_counts:
                    recent_counts[n] += 1
        freq_recent_map = {n: recent_counts[n] / window for n in numbers}

    ranked: list[RankedNumber] = []
    for n in numbers:
        if freq_recent_map is None:
            score = freq_all[n]
            fr = None
        else:
            fr = freq_recent_map[n]
            score = recent_weight * fr + (1.0 - recent_weight) * freq_all[n]
        ranked.append(RankedNumber(number=n, score=float(score), freq_all=float(freq_all[n]), freq_recent=fr))

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked


def poisson_binomial_pmf(probs: list[float]) -> list[float]:
    """Poisson-binomial PMF for independent Bernoulli hits with probabilities `probs`."""
    if any(p < 0.0 or p > 1.0 for p in probs):
        raise ValueError("All probabilities must be in [0, 1]")

    pmf = [1.0]
    for p in probs:
        next_pmf = [0.0] * (len(pmf) + 1)
        for k, v in enumerate(pmf):
            next_pmf[k] += v * (1.0 - p)
            next_pmf[k + 1] += v * p
        pmf = next_pmf

    # Numerical stability: re-normalize
    total = sum(pmf)
    if total > 0:
        pmf = [x / total for x in pmf]
    return pmf


def _uniform_ticket_probabilities(keno_type: int) -> TicketProbabilities:
    probs = KENO_PROBABILITIES.get(keno_type)
    if not probs:
        raise ValueError(f"Unsupported keno_type: {keno_type}")
    near = float(probs.get(keno_type - 1, 0.0))
    jack = float(probs.get(keno_type, 0.0))
    return TicketProbabilities(near_miss=near, jackpot=jack, near_or_jackpot=near + jack)


def _model_ticket_probabilities(model_probs: list[float]) -> TicketProbabilities:
    pmf = poisson_binomial_pmf(model_probs)
    k = len(model_probs)
    near = float(pmf[k - 1]) if k >= 1 else 0.0
    jack = float(pmf[k]) if k >= 1 else 0.0
    return TicketProbabilities(near_miss=near, jackpot=jack, near_or_jackpot=near + jack)


def suggest_tickets_from_draws(
    draws: list[DrawResult],
    *,
    keno_types: list[int],
    recent_draws: int = 365,
    recent_weight: float = 0.6,
    numbers_range: tuple[int, int] = (1, 70),
    with_model_probabilities: bool = True,
) -> list[TicketSuggestion]:
    """Suggest one ticket per requested keno_type."""
    ranked = rank_numbers_weighted_frequency(
        draws,
        numbers_range=numbers_range,
        recent_draws=recent_draws,
        recent_weight=recent_weight,
    )
    score_by_number = {r.number: r.score for r in ranked}

    suggestions: list[TicketSuggestion] = []
    for k in keno_types:
        numbers = [r.number for r in ranked[:k]]
        uniform_probs = _uniform_ticket_probabilities(k)
        model_probs = None
        if with_model_probabilities:
            per_num_p = [score_by_number[n] for n in numbers]
            model_probs = _model_ticket_probabilities(per_num_p)

        suggestions.append(
            TicketSuggestion(
                keno_type=int(k),
                numbers=numbers,
                model=f"weighted_frequency(recent_draws={recent_draws}, recent_weight={recent_weight})",
                probabilities_uniform=uniform_probs,
                probabilities_model=model_probs,
            )
        )

    return suggestions


def save_suggestions_json(
    suggestions: list[TicketSuggestion],
    *,
    output_path: str | Path,
    draws_path: Optional[str] = None,
) -> None:
    payload = {
        "analysis": "ticket_suggestions",
        "generated_at": datetime.now().isoformat(),
        "draws_path": draws_path,
        "suggestions": [asdict(s) for s in suggestions],
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


__all__ = [
    "RankedNumber",
    "TicketProbabilities",
    "TicketSuggestion",
    "poisson_binomial_pmf",
    "rank_numbers_weighted_frequency",
    "suggest_tickets_from_draws",
    "save_suggestions_json",
]
