"""Unit tests for DIST-003 sum null model helpers."""

from __future__ import annotations

import itertools
import math

import pytest

from kenobase.analysis.dist003_sum_null_model import exact_sum_counts, fit_sum_null_model


@pytest.mark.unit
def test_exact_sum_counts_total_combinations() -> None:
    counts = exact_sum_counts(numbers_min=1, numbers_max=10, numbers_drawn=3)
    assert sum(counts.values()) == math.comb(10, 3)


@pytest.mark.unit
def test_fit_sum_null_model_is_perfect_on_full_enumeration() -> None:
    # Enumerate all combinations for n=10, k=3; observed distribution equals the exact null.
    sums = [sum(c) for c in itertools.combinations(range(1, 11), 3)]
    fit = fit_sum_null_model(sums, numbers_min=1, numbers_max=10, numbers_drawn=3, bin_width=1)
    assert fit.total_draws == math.comb(10, 3)
    assert fit.expected_mean == pytest.approx(3 * (1 + 10) / 2)
    assert fit.chi2_statistic == pytest.approx(0.0, abs=1e-12)
    assert fit.chi2_p_value == pytest.approx(1.0, abs=1e-12)

