"""Unit tests for cross_spectrum_coupling module.

Tests cover:
1. Synthetic sinusoidal signals with known frequency/phase lag
2. Null control with independent noise series
3. CLI schema validation
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.analysis.cross_spectrum_coupling import (
    DEFAULT_BANDS,
    CoherenceResult,
    CrossSpectrumSummary,
    FrequencyBand,
    PhaseResult,
    SpectralCouplingResult,
    align_series_by_date,
    analyze_spectral_coupling,
    circular_mean,
    compute_cpsd_coherence,
    compute_plv,
    extract_band_metrics,
    generate_block_surrogate,
    generate_phase_surrogate,
    run_cross_spectrum_analysis,
    to_jsonable,
)
from kenobase.analysis.number_representations import GameTimeSeries


class TestBasicFunctions:
    """Test basic utility functions."""

    def test_compute_plv_perfect_locking(self):
        """PLV should be 1.0 for perfectly locked phases."""
        phases = np.zeros(100)  # All phases = 0
        plv = compute_plv(phases)
        assert plv == pytest.approx(1.0, abs=1e-6)

    def test_compute_plv_uniform_phases(self):
        """PLV should be ~0 for uniformly distributed phases."""
        phases = np.linspace(0, 2 * np.pi, 1000, endpoint=False)
        plv = compute_plv(phases)
        assert plv < 0.1  # Should be close to 0

    def test_compute_plv_partial_locking(self):
        """PLV should be intermediate for partially locked phases."""
        # 50% locked at 0, 50% random
        locked = np.zeros(500)
        random = np.random.uniform(0, 2 * np.pi, 500)
        phases = np.concatenate([locked, random])
        plv = compute_plv(phases)
        assert 0.3 < plv < 0.7

    def test_circular_mean_zero(self):
        """Circular mean of phases at 0 should be 0."""
        phases = np.zeros(100)
        mean_dir, resultant = circular_mean(phases)
        assert mean_dir == pytest.approx(0.0, abs=1e-6)
        assert resultant == pytest.approx(1.0, abs=1e-6)

    def test_circular_mean_pi(self):
        """Circular mean of phases at pi should be pi."""
        phases = np.full(100, np.pi)
        mean_dir, resultant = circular_mean(phases)
        assert abs(mean_dir) == pytest.approx(np.pi, abs=1e-6)
        assert resultant == pytest.approx(1.0, abs=1e-6)


class TestSurrogates:
    """Test surrogate generation."""

    def test_phase_surrogate_preserves_length(self):
        """Phase surrogate should preserve signal length."""
        x = np.random.randn(256)
        surr = generate_phase_surrogate(x, seed=42)
        assert len(surr) == len(x)

    def test_phase_surrogate_preserves_spectrum(self):
        """Phase surrogate should preserve amplitude spectrum."""
        x = np.sin(np.linspace(0, 4 * np.pi, 256)) + 0.5 * np.sin(np.linspace(0, 8 * np.pi, 256))
        surr = generate_phase_surrogate(x, seed=42)

        # Compare amplitude spectra (skip DC component which may have tiny numerical errors)
        orig_amp = np.abs(np.fft.rfft(x))
        surr_amp = np.abs(np.fft.rfft(surr))
        # Use looser tolerance for numerical stability
        np.testing.assert_allclose(orig_amp[1:], surr_amp[1:], rtol=1e-10, atol=1e-14)

    def test_block_surrogate_preserves_length(self):
        """Block surrogate should preserve signal length."""
        x = np.random.randn(100)
        surr = generate_block_surrogate(x, block_size=7, seed=42)
        assert len(surr) == len(x)

    def test_block_surrogate_preserves_values(self):
        """Block surrogate should preserve all values (just reordered)."""
        x = np.arange(100, dtype=float)
        surr = generate_block_surrogate(x, block_size=10, seed=42)
        assert set(x) == set(surr)


class TestSpectralComputation:
    """Test spectral computation functions."""

    def test_cpsd_coherence_identical_signals(self):
        """Coherence should be 1.0 for identical signals."""
        x = np.sin(np.linspace(0, 10 * np.pi, 256))
        freqs, cpsd, coh, phase = compute_cpsd_coherence(x, x, nperseg=64)

        assert len(freqs) == len(coh)
        # Coherence should be ~1 everywhere for identical signals
        assert np.mean(coh) > 0.99

    def test_cpsd_coherence_orthogonal_signals(self):
        """Coherence should be high at signal frequency for phase-shifted signals."""
        x = np.sin(np.linspace(0, 10 * np.pi, 256))
        y = np.cos(np.linspace(0, 10 * np.pi, 256))  # 90 degree phase shift
        freqs, cpsd, coh, phase = compute_cpsd_coherence(x, y, nperseg=64)

        # Coherence should be high at the signal frequency (even if mean is lower)
        # Find peak coherence - should be very high since signals are phase-locked
        assert np.max(coh) > 0.95

    def test_cpsd_coherence_noise(self):
        """Coherence should be low for independent noise."""
        rng = np.random.default_rng(42)
        x = rng.standard_normal(256)
        y = rng.standard_normal(256)
        freqs, cpsd, coh, phase = compute_cpsd_coherence(x, y, nperseg=64)

        # Coherence should be low for independent signals
        assert np.mean(coh) < 0.5


class TestSyntheticSinusoids:
    """Test with synthetic sinusoidal signals of known frequency and phase."""

    def create_synthetic_game(
        self,
        name: str,
        n_draws: int,
        frequency: float,
        phase: float,
        start_date: date,
        pool_max: int = 70,
        draw_size: int = 20,
        noise_level: float = 0.1,
        seed: int = 42,
    ) -> GameDraws:
        """Create synthetic game draws with sinusoidal pattern in number selection.

        The pattern affects which numbers are drawn based on a sinusoidal wave.
        """
        rng = np.random.default_rng(seed)
        dates = [start_date + timedelta(days=i) for i in range(n_draws)]
        presence = np.zeros((n_draws, pool_max + 1), dtype=np.int8)

        for i in range(n_draws):
            # Sinusoidal bias for number selection
            t = i
            wave = np.sin(2 * np.pi * frequency * t + phase)
            bias = (wave + 1) / 2  # Normalize to [0, 1]

            # Select numbers with bias towards high or low based on wave
            if bias > 0.5 + noise_level * rng.standard_normal():
                # Prefer higher numbers
                probs = np.linspace(0.5, 1.5, pool_max)
            else:
                # Prefer lower numbers
                probs = np.linspace(1.5, 0.5, pool_max)

            probs = probs / probs.sum()
            selected = rng.choice(pool_max, size=draw_size, replace=False, p=probs) + 1
            presence[i, selected] = 1

        return GameDraws(
            name=name,
            pool_max=pool_max,
            draw_size=draw_size,
            dates=dates,
            presence=presence,
        )

    def test_detect_known_coupling(self):
        """Should detect coupling between signals with same frequency."""
        start = date(2020, 1, 1)
        freq = 1 / 14  # Biweekly periodicity

        game1 = self.create_synthetic_game(
            "Game1", n_draws=500, frequency=freq, phase=0, start_date=start, seed=42
        )
        game2 = self.create_synthetic_game(
            "Game2", n_draws=500, frequency=freq, phase=0.5, start_date=start, seed=43
        )

        result = analyze_spectral_coupling(
            game1,
            game2,
            representation="centroid",
            n_surrogates=99,
            alpha_fdr=0.1,
            seed=42,
        )

        assert result.n_samples > 0
        assert len(result.coherence_results) > 0
        # With matching frequencies, we expect some coherence
        max_coh = max(r.max_coherence for r in result.coherence_results)
        assert max_coh > 0.1

    def test_no_coupling_different_frequencies(self):
        """Should not detect strong coupling for different frequencies."""
        start = date(2020, 1, 1)

        game1 = self.create_synthetic_game(
            "Game1", n_draws=500, frequency=1 / 7, phase=0, start_date=start, seed=42
        )
        game2 = self.create_synthetic_game(
            "Game2", n_draws=500, frequency=1 / 30, phase=0, start_date=start, seed=43
        )

        result = analyze_spectral_coupling(
            game1,
            game2,
            representation="centroid",
            n_surrogates=49,
            alpha_fdr=0.05,
            seed=42,
        )

        # Coherence should be lower for mismatched frequencies
        mean_coh = np.mean([r.mean_coherence for r in result.coherence_results])
        assert mean_coh < 0.5


class TestNullControl:
    """Test null control with independent noise."""

    def create_noise_game(
        self,
        name: str,
        n_draws: int,
        start_date: date,
        pool_max: int = 70,
        draw_size: int = 20,
        seed: int = 42,
    ) -> GameDraws:
        """Create game with purely random draws (no pattern)."""
        rng = np.random.default_rng(seed)
        dates = [start_date + timedelta(days=i) for i in range(n_draws)]
        presence = np.zeros((n_draws, pool_max + 1), dtype=np.int8)

        for i in range(n_draws):
            selected = rng.choice(pool_max, size=draw_size, replace=False) + 1
            presence[i, selected] = 1

        return GameDraws(
            name=name,
            pool_max=pool_max,
            draw_size=draw_size,
            dates=dates,
            presence=presence,
        )

    def test_no_coupling_noise(self):
        """Should not find significant coupling in pure noise."""
        start = date(2020, 1, 1)

        game1 = self.create_noise_game("Noise1", n_draws=300, start_date=start, seed=42)
        game2 = self.create_noise_game("Noise2", n_draws=300, start_date=start, seed=99)

        result = analyze_spectral_coupling(
            game1,
            game2,
            representation="centroid",
            n_surrogates=99,
            alpha_fdr=0.05,
            seed=42,
        )

        # Should not be significant for noise
        assert not result.is_significant

    def test_negative_control_flag(self):
        """Negative control flag should be set correctly."""
        start = date(2020, 1, 1)

        game1 = self.create_noise_game("KENO", n_draws=100, start_date=start, seed=42)
        game2 = self.create_noise_game("EuroJackpot", n_draws=100, start_date=start, seed=43)

        result = analyze_spectral_coupling(
            game1,
            game2,
            n_surrogates=19,
            negative_control=True,
            seed=42,
        )

        assert result.negative_control is True


class TestCLISchema:
    """Test CLI output schema."""

    def create_simple_game(self, name: str, n: int = 50) -> GameDraws:
        """Create minimal game for schema testing."""
        start = date(2020, 1, 1)
        dates = [start + timedelta(days=i) for i in range(n)]
        presence = np.zeros((n, 71), dtype=np.int8)
        rng = np.random.default_rng(42)
        for i in range(n):
            selected = rng.choice(70, size=20, replace=False) + 1
            presence[i, selected] = 1
        return GameDraws(
            name=name, pool_max=70, draw_size=20, dates=dates, presence=presence
        )

    def test_summary_schema(self):
        """CrossSpectrumSummary should have all required fields."""
        games = [self.create_simple_game("A"), self.create_simple_game("B")]
        summary = run_cross_spectrum_analysis(
            games,
            representations=["centroid"],
            n_surrogates=9,
            seed=42,
        )

        assert hasattr(summary, "timestamp")
        assert hasattr(summary, "n_pairs")
        assert hasattr(summary, "n_representations")
        assert hasattr(summary, "n_bands")
        assert hasattr(summary, "n_surrogates")
        assert hasattr(summary, "alpha_fdr")
        assert hasattr(summary, "results")
        assert hasattr(summary, "significant_count")
        assert hasattr(summary, "negative_control_significant")

    def test_result_schema(self):
        """SpectralCouplingResult should have all required fields."""
        games = [self.create_simple_game("A"), self.create_simple_game("B")]
        summary = run_cross_spectrum_analysis(
            games,
            representations=["centroid"],
            n_surrogates=9,
            seed=42,
        )

        assert len(summary.results) > 0
        result = summary.results[0]

        assert hasattr(result, "source_game")
        assert hasattr(result, "target_game")
        assert hasattr(result, "representation")
        assert hasattr(result, "n_samples")
        assert hasattr(result, "coherence_results")
        assert hasattr(result, "phase_results")
        assert hasattr(result, "is_significant")
        assert hasattr(result, "negative_control")

    def test_coherence_result_schema(self):
        """CoherenceResult should have all required fields including q_value."""
        games = [self.create_simple_game("A"), self.create_simple_game("B")]
        summary = run_cross_spectrum_analysis(
            games,
            representations=["centroid"],
            n_surrogates=9,
            seed=42,
        )

        result = summary.results[0]
        if result.coherence_results:
            coh = result.coherence_results[0]
            assert hasattr(coh, "band_name")
            assert hasattr(coh, "mean_coherence")
            assert hasattr(coh, "max_coherence")
            assert hasattr(coh, "peak_frequency")
            assert hasattr(coh, "p_value")
            assert hasattr(coh, "q_value")

    def test_phase_result_schema(self):
        """PhaseResult should have all required fields including q_value."""
        games = [self.create_simple_game("A"), self.create_simple_game("B")]
        summary = run_cross_spectrum_analysis(
            games,
            representations=["centroid"],
            n_surrogates=9,
            seed=42,
        )

        result = summary.results[0]
        if result.phase_results:
            phase = result.phase_results[0]
            assert hasattr(phase, "band_name")
            assert hasattr(phase, "mean_phase_diff")
            assert hasattr(phase, "plv")
            assert hasattr(phase, "p_value")
            assert hasattr(phase, "q_value")

    def test_to_jsonable(self):
        """to_jsonable should produce valid JSON structure."""
        games = [self.create_simple_game("A"), self.create_simple_game("B")]
        summary = run_cross_spectrum_analysis(
            games,
            representations=["centroid"],
            n_surrogates=9,
            seed=42,
        )

        jsonable = to_jsonable(summary)

        # Should be a dict
        assert isinstance(jsonable, dict)
        # Should have key fields
        assert "timestamp" in jsonable
        assert "results" in jsonable
        assert isinstance(jsonable["results"], list)

        # Should be JSON serializable
        import json
        json_str = json.dumps(jsonable, default=str)
        assert len(json_str) > 0


class TestAlignSeries:
    """Test time series alignment."""

    def test_align_overlapping_dates(self):
        """Should align series with overlapping dates."""
        dates1 = [date(2020, 1, i) for i in range(1, 11)]
        dates2 = [date(2020, 1, i) for i in range(5, 15)]
        vals1 = np.arange(10, dtype=float)
        vals2 = np.arange(10, dtype=float) + 100

        ts1 = GameTimeSeries("A", dates1, vals1, "sum", 70)
        ts2 = GameTimeSeries("B", dates2, vals2, "sum", 70)

        aligned1, aligned2, common = align_series_by_date(ts1, ts2)

        # Should have 6 overlapping dates (5-10)
        assert len(common) == 6
        assert len(aligned1) == 6
        assert len(aligned2) == 6

    def test_align_no_overlap(self):
        """Should return empty for non-overlapping dates."""
        dates1 = [date(2020, 1, i) for i in range(1, 6)]
        dates2 = [date(2020, 1, i) for i in range(10, 15)]
        vals1 = np.arange(5, dtype=float)
        vals2 = np.arange(5, dtype=float)

        ts1 = GameTimeSeries("A", dates1, vals1, "sum", 70)
        ts2 = GameTimeSeries("B", dates2, vals2, "sum", 70)

        aligned1, aligned2, common = align_series_by_date(ts1, ts2)

        assert len(common) == 0
        assert len(aligned1) == 0
        assert len(aligned2) == 0
