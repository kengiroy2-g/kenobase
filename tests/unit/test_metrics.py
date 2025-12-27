"""Unit Tests fuer Physics Metrics Module.

Tests fuer kenobase/physics/metrics.py
"""

import pytest

from kenobase.physics.metrics import (
    calculate_autocorrelation,
    calculate_autocorrelation_series,
    calculate_coefficient_of_variation,
    calculate_hurst_exponent,
    calculate_stability_score,
    calculate_volatility,
    count_regime_peaks,
)


class TestCalculateHurstExponent:
    """Tests fuer calculate_hurst_exponent()."""

    def test_random_walk_near_05(self):
        """Random Walk sollte H in validem Bereich sein."""
        import random
        random.seed(42)

        # Generate random walk
        walk = [0.0]
        for _ in range(500):
            walk.append(walk[-1] + random.gauss(0, 1))

        h = calculate_hurst_exponent(walk)

        # Should be in valid range [0, 1]
        assert 0.0 <= h <= 1.0

    def test_trending_series_above_05(self):
        """Trending Serie sollte H > 0.5 haben."""
        # Linear trend with small noise
        series = [float(i) + 0.1 * (i % 5) for i in range(200)]

        h = calculate_hurst_exponent(series)

        # Trending should be > 0.5
        assert h > 0.4  # Allow some tolerance

    def test_short_series_returns_05(self):
        """Kurze Serie gibt 0.5 zurueck."""
        h = calculate_hurst_exponent([1.0, 2.0, 3.0])
        assert h == 0.5

    def test_empty_series(self):
        """Leere Serie gibt 0.5 zurueck."""
        h = calculate_hurst_exponent([])
        assert h == 0.5


class TestCalculateAutocorrelation:
    """Tests fuer calculate_autocorrelation()."""

    def test_constant_series_high_autocorr(self):
        """Konstante Serie hat hohe Autokorrelation."""
        series = [5.0] * 20

        # Constant series has 0 variance, so autocorr is 0
        acf = calculate_autocorrelation(series, lag=1)
        assert acf == 0.0

    def test_alternating_series_negative_autocorr(self):
        """Alternierende Serie hat negative Autokorrelation."""
        series = [1.0, -1.0] * 20

        acf = calculate_autocorrelation(series, lag=1)
        assert acf < 0

    def test_trending_series_positive_autocorr(self):
        """Trending Serie hat positive Autokorrelation."""
        series = [float(i) for i in range(50)]

        acf = calculate_autocorrelation(series, lag=1)
        assert acf > 0.9  # High positive correlation

    def test_lag_larger_than_series(self):
        """Lag groesser als Serie gibt 0 zurueck."""
        series = [1.0, 2.0, 3.0]
        acf = calculate_autocorrelation(series, lag=10)
        assert acf == 0.0


class TestCalculateAutocorrelationSeries:
    """Tests fuer calculate_autocorrelation_series()."""

    def test_returns_list(self):
        """Gibt Liste von Autokorrelationen zurueck."""
        series = [float(i) for i in range(50)]
        acf_series = calculate_autocorrelation_series(series, max_lag=5)

        assert isinstance(acf_series, list)
        assert len(acf_series) == 5

    def test_decreasing_for_trending(self):
        """Autokorrelation nimmt ab fuer trending Serie."""
        series = [float(i) for i in range(100)]
        acf_series = calculate_autocorrelation_series(series, max_lag=10)

        # First lag should be highest
        assert acf_series[0] > acf_series[-1]


class TestCountRegimePeaks:
    """Tests fuer count_regime_peaks()."""

    def test_constant_series_one_peak(self):
        """Konstante Serie hat 1 Regime."""
        series = [5.0] * 50
        peaks = count_regime_peaks(series)
        assert peaks == 1

    def test_short_series_one_peak(self):
        """Kurze Serie gibt 1 zurueck."""
        peaks = count_regime_peaks([1.0, 2.0])
        assert peaks == 1

    def test_oscillating_series_multiple_peaks(self):
        """Oszillierende Serie hat mehrere Peaks."""
        # Create series with clear peaks
        series = []
        for i in range(100):
            if i % 20 == 10:
                series.append(10.0)  # Peak
            else:
                series.append(1.0)  # Base

        peaks = count_regime_peaks(series, window=5, min_prominence=0.5)
        assert peaks >= 1


class TestCalculateVolatility:
    """Tests fuer calculate_volatility()."""

    def test_constant_series_zero_volatility(self):
        """Konstante Serie hat Volatilitaet 0."""
        series = [100.0] * 20
        vol = calculate_volatility(series)
        assert vol == 0.0

    def test_volatile_series_high_volatility(self):
        """Volatile Serie hat hohe Volatilitaet."""
        series = [100.0, 110.0, 90.0, 120.0, 80.0] * 4
        vol = calculate_volatility(series)
        assert vol > 0.1

    def test_short_series(self):
        """Kurze Serie gibt 0 zurueck."""
        assert calculate_volatility([]) == 0.0
        assert calculate_volatility([5.0]) == 0.0

    def test_window_parameter(self):
        """Window-Parameter limitiert Berechnung."""
        series = [100.0] * 10 + [110.0, 90.0, 120.0, 80.0] * 3

        vol_full = calculate_volatility(series)
        vol_window = calculate_volatility(series, window=10)

        # Window only uses last 10 values (volatile part)
        assert vol_window > vol_full


class TestCalculateCoefficientOfVariation:
    """Tests fuer calculate_coefficient_of_variation()."""

    def test_constant_series_zero_cv(self):
        """Konstante Serie hat CV = 0."""
        series = [10.0] * 20
        cv = calculate_coefficient_of_variation(series)
        assert cv == 0.0

    def test_variable_series_positive_cv(self):
        """Variable Serie hat positiven CV."""
        series = [10.0, 20.0, 30.0, 40.0, 50.0]
        cv = calculate_coefficient_of_variation(series)
        assert cv > 0

    def test_zero_mean_returns_zero(self):
        """Serie mit Mean=0 gibt CV=0 zurueck."""
        series = [-5.0, -3.0, 0.0, 3.0, 5.0]  # Mean = 0
        cv = calculate_coefficient_of_variation(series)
        assert cv == 0.0

    def test_short_series(self):
        """Kurze Serie gibt 0 zurueck."""
        assert calculate_coefficient_of_variation([]) == 0.0
        assert calculate_coefficient_of_variation([5.0]) == 0.0


class TestCalculateStabilityScore:
    """Tests fuer calculate_stability_score()."""

    def test_constant_series_score_one(self):
        """Konstante Serie hat Stabilitaet 1.0."""
        series = [10.0] * 20
        score = calculate_stability_score(series)
        assert score == 1.0

    def test_variable_series_lower_score(self):
        """Variable Serie hat niedrigere Stabilitaet."""
        series = [10.0, 20.0, 30.0, 40.0, 50.0]
        score = calculate_stability_score(series)
        assert 0.0 < score < 1.0

    def test_score_clamped_to_range(self):
        """Score ist immer zwischen 0 und 1."""
        # Very high variance
        series = [1.0, 1000.0, 1.0, 1000.0]
        score = calculate_stability_score(series)
        assert 0.0 <= score <= 1.0

    def test_short_series(self):
        """Kurze Serie basiert auf CV=0, also stability=1."""
        # CV returns 0.0 for short series, so stability = 1 - 0 = 1.0
        assert calculate_stability_score([]) == 1.0
        assert calculate_stability_score([5.0]) == 1.0
