"""Unit tests for ticket suggester helpers."""

from __future__ import annotations

from datetime import datetime

import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.prediction.ticket_suggester import (
    poisson_binomial_pmf,
    rank_numbers_weighted_frequency,
)


@pytest.mark.unit
def test_poisson_binomial_pmf_sums_to_one() -> None:
    pmf = poisson_binomial_pmf([0.2, 0.5, 0.8])
    assert sum(pmf) == pytest.approx(1.0, abs=1e-12)
    assert len(pmf) == 4


@pytest.mark.unit
def test_rank_numbers_weighted_frequency_prefers_more_frequent_number() -> None:
    # Construct 3 draws where number 1 appears always, number 2 appears once.
    draws = [
        DrawResult(date=datetime(2024, 1, 1), numbers=[1, 3], game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 2), numbers=[1, 4], game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 3), numbers=[1, 2], game_type=GameType.KENO),
    ]

    ranked = rank_numbers_weighted_frequency(
        draws,
        numbers_range=(1, 4),
        recent_draws=0,
        recent_weight=0.6,
    )

    assert ranked[0].number == 1
    assert ranked[-1].number == 3 or ranked[-1].number == 4

