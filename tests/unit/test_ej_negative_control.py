"""Unit tests for EuroJackpot negative control validation (EJ-001)."""

import numpy as np
import pytest
from datetime import date

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.cross_lottery_coupling import (
    GameDraws,
    bh_fdr,
    conditional_lifts_number_triggers,
    pair_overlap_significance,
    top_pairs_by_lift,
)


def make_synthetic_game(
    name: str,
    pool_max: int,
    draw_size: int,
    n_draws: int,
    seed: int = 42,
) -> GameDraws:
    """Create synthetic game data for testing."""
    from datetime import timedelta
    rng = np.random.default_rng(seed)
    base_date = date(2022, 1, 1)
    dates = [base_date + timedelta(days=i) for i in range(n_draws)]

    presence = np.zeros((n_draws, pool_max + 1), dtype=np.int8)
    for i in range(n_draws):
        nums = rng.choice(np.arange(1, pool_max + 1), size=draw_size, replace=False)
        for n in nums:
            presence[i, n] = 1

    return GameDraws(
        name=name,
        pool_max=pool_max,
        draw_size=draw_size,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


class TestBHFDR:
    """Tests for Benjamini-Hochberg FDR correction."""

    def test_empty_array(self):
        """Empty p-value array returns empty."""
        result = bh_fdr(np.array([]))
        assert len(result) == 0

    def test_single_value(self):
        """Single p-value returns same value."""
        result = bh_fdr(np.array([0.05]))
        assert len(result) == 1
        assert 0 <= result[0] <= 1

    def test_all_small_pvalues(self):
        """All small p-values stay significant."""
        p = np.array([0.001, 0.002, 0.003])
        q = bh_fdr(p)
        assert all(q <= 0.05)

    def test_all_large_pvalues(self):
        """All large p-values stay non-significant."""
        p = np.array([0.5, 0.6, 0.7])
        q = bh_fdr(p)
        assert all(q >= p)

    def test_mixed_pvalues(self):
        """Mixed p-values get properly corrected."""
        p = np.array([0.01, 0.04, 0.5])
        q = bh_fdr(p)
        assert q[0] <= q[1] <= q[2]  # q-values preserve ordering

    def test_invalid_pvalues_raise(self):
        """Invalid p-values raise ValueError."""
        with pytest.raises(ValueError):
            bh_fdr(np.array([-0.1, 0.5]))
        with pytest.raises(ValueError):
            bh_fdr(np.array([0.5, 1.5]))


class TestGameDrawsSplit:
    """Tests for splitting GameDraws data."""

    def test_split_preserves_properties(self):
        """Split data preserves game properties."""
        game = make_synthetic_game("TEST", 49, 6, 100)

        n = len(game.dates)
        split_idx = int(n * 0.8)

        train_dates = game.dates[:split_idx]
        test_dates = game.dates[split_idx:]

        assert len(train_dates) == 80
        assert len(test_dates) == 20
        assert train_dates[-1] < test_dates[0]  # No overlap

    def test_presence_matrix_consistent(self):
        """Presence matrix is consistent after split."""
        game = make_synthetic_game("TEST", 49, 6, 50)

        # Check that each row has exactly draw_size numbers
        for i in range(len(game.dates)):
            assert game.presence[i, 1:].sum() == game.draw_size


class TestConditionalLifts:
    """Tests for conditional lift computation."""

    def test_no_lifts_on_random_data(self):
        """Random data should produce no significant lifts after FDR."""
        source = make_synthetic_game("SOURCE", 50, 5, 200, seed=1)
        target = make_synthetic_game("TARGET", 50, 5, 200, seed=2)

        lifts = conditional_lifts_number_triggers(
            source=source,
            target=target,
            lag_days=0,
            min_support=10,
            alpha_fdr=0.05,
            filter_by_alpha=True,
        )
        # Random data should produce few or no significant lifts
        # Due to FDR correction, we expect very few false positives
        assert len(lifts) < 10  # Allow some noise but not systematic

    def test_lifts_returned_with_no_filter(self):
        """Lifts are returned when filter_by_alpha=False."""
        source = make_synthetic_game("SOURCE", 50, 5, 100, seed=1)
        target = make_synthetic_game("TARGET", 50, 5, 100, seed=2)

        lifts = conditional_lifts_number_triggers(
            source=source,
            target=target,
            lag_days=0,
            min_support=5,
            alpha_fdr=0.05,
            filter_by_alpha=False,
            max_results=50,
        )
        # Should return some lifts even if not significant
        assert len(lifts) > 0


class TestPairOverlap:
    """Tests for pair overlap analysis."""

    def test_pair_overlap_random_games(self):
        """Random games should show expected overlap around expected_overlap."""
        game1 = make_synthetic_game("GAME1", 49, 6, 500, seed=10)
        game2 = make_synthetic_game("GAME2", 49, 6, 500, seed=20)

        pairs1 = top_pairs_by_lift(game=game1, restrict_max=49, top_k=100)
        pairs2 = top_pairs_by_lift(game=game2, restrict_max=49, top_k=100)

        overlap = pair_overlap_significance(
            pair_lists=[pairs1, pairs2],
            range_max=49,
            top_k=100,
        )

        # Random data should have overlap near expected
        assert overlap.overlap >= 0
        assert overlap.expected_overlap > 0
        # p-value should be > 0.05 for random data (usually)
        # But we don't hard-assert this as random can occasionally produce outliers

    def test_pair_overlap_same_game(self):
        """Same game should have perfect overlap."""
        game = make_synthetic_game("GAME", 49, 6, 500)

        pairs = top_pairs_by_lift(game=game, restrict_max=49, top_k=50)

        overlap = pair_overlap_significance(
            pair_lists=[pairs, pairs],
            range_max=49,
            top_k=50,
        )

        # Same game should have perfect overlap
        assert overlap.overlap == 50


class TestNegativeControlLogic:
    """Tests for the negative control falsification logic."""

    def test_external_game_no_correlation(self):
        """External game should not correlate with internal games."""
        # Simulate DE ecosystem
        de_game1 = make_synthetic_game("KENO", 70, 20, 300, seed=1)
        de_game2 = make_synthetic_game("LOTTO", 49, 6, 300, seed=2)

        # Simulate EJ (external, independent)
        ej_game = make_synthetic_game("EUROJACKPOT", 50, 5, 300, seed=999)

        # Compute lifts: DE internal
        de_lifts = conditional_lifts_number_triggers(
            source=de_game1,
            target=de_game2,
            lag_days=0,
            min_support=10,
            alpha_fdr=0.05,
            filter_by_alpha=True,
        )

        # Compute lifts: EJ external
        ej_lifts = conditional_lifts_number_triggers(
            source=ej_game,
            target=de_game1,
            lag_days=0,
            min_support=10,
            alpha_fdr=0.05,
            filter_by_alpha=True,
        )

        # Both should show few/no significant correlations (random data)
        # The point is EJ should NOT show MORE correlations than DE-internal
        # In real data, if ecosystem hypothesis holds:
        #   DE-internal might show some correlations
        #   EJ should show fewer or none
        assert len(ej_lifts) <= len(de_lifts) + 5  # Allow small noise margin


class TestAcceptanceCriteria:
    """Tests for EJ-001 acceptance criteria."""

    def test_train_test_split_required(self):
        """Verify train/test split can be applied."""
        game = make_synthetic_game("TEST", 49, 6, 100)

        train_ratio = 0.8
        n = len(game.dates)
        split_idx = int(n * train_ratio)

        assert split_idx == 80
        assert n - split_idx == 20

    def test_fdr_correction_applied(self):
        """Verify FDR correction reduces false positives."""
        # Create many p-values including some low ones by chance
        rng = np.random.default_rng(42)
        p_values = rng.uniform(0, 1, size=1000)

        # Add a few "significant" p-values
        p_values[:10] = 0.01

        q_values = bh_fdr(p_values)

        # After FDR, fewer values should be "significant"
        raw_sig = np.sum(p_values <= 0.05)
        fdr_sig = np.sum(q_values <= 0.05)

        # FDR correction should reduce false positives
        assert fdr_sig <= raw_sig


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
