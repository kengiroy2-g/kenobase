"""Physics Metrics Module.

Dieses Modul implementiert statistische Metriken fuer die Physics Layer
von Kenobase V2.0: Hurst-Exponent, Autokorrelation, und verwandte Masse.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def calculate_hurst_exponent(
    series: list[float],
    max_lag: Optional[int] = None,
) -> float:
    """Berechnet den Hurst-Exponenten einer Zeitreihe.

    Der Hurst-Exponent H charakterisiert die langfristige Abhaengigkeit:
    - H < 0.5: Mean-reverting (anti-persistent)
    - H = 0.5: Random walk
    - H > 0.5: Trending (persistent)

    Verwendet die R/S (Rescaled Range) Methode.

    Args:
        series: Zeitreihe als Liste von float.
        max_lag: Maximaler Lag fuer Berechnung. Default: len(series) // 2.

    Returns:
        Hurst-Exponent im Bereich [0, 1].
    """
    if len(series) < 20:
        return 0.5  # Not enough data, assume random

    data = np.array(series, dtype=float)
    n = len(data)

    if max_lag is None:
        max_lag = n // 2

    max_lag = min(max_lag, n // 2)
    if max_lag < 2:
        return 0.5

    # Calculate R/S for different lags
    lags = []
    rs_values = []

    for lag in range(10, max_lag + 1, max(1, max_lag // 20)):
        rs_list = []

        for start in range(0, n - lag + 1, lag):
            subset = data[start : start + lag]
            if len(subset) < 2:
                continue

            mean_val = np.mean(subset)
            deviations = subset - mean_val
            cumulative = np.cumsum(deviations)

            r = np.max(cumulative) - np.min(cumulative)
            s = np.std(subset, ddof=1)

            if s > 1e-10:
                rs_list.append(r / s)

        if rs_list:
            lags.append(lag)
            rs_values.append(np.mean(rs_list))

    if len(lags) < 2:
        return 0.5

    # Linear regression in log-log space
    log_lags = np.log(lags)
    log_rs = np.log(rs_values)

    # Simple linear regression
    slope = np.cov(log_lags, log_rs)[0, 1] / np.var(log_lags)

    # Clamp to valid range
    return max(0.0, min(1.0, slope))


def calculate_autocorrelation(
    series: list[float],
    lag: int = 1,
) -> float:
    """Berechnet die Autokorrelation fuer einen gegebenen Lag.

    Args:
        series: Zeitreihe als Liste von float.
        lag: Zeitverzoegerung (default 1).

    Returns:
        Autokorrelations-Koeffizient [-1, 1].
    """
    if len(series) <= lag:
        return 0.0

    data = np.array(series, dtype=float)
    n = len(data)

    mean_val = np.mean(data)
    var_val = np.var(data)

    if var_val < 1e-10:
        return 0.0

    covariance = np.mean((data[: n - lag] - mean_val) * (data[lag:] - mean_val))
    return covariance / var_val


def calculate_autocorrelation_series(
    series: list[float],
    max_lag: int = 20,
) -> list[float]:
    """Berechnet Autokorrelation fuer mehrere Lags.

    Args:
        series: Zeitreihe als Liste von float.
        max_lag: Maximaler Lag.

    Returns:
        Liste von Autokorrelationen fuer lag=1 bis lag=max_lag.
    """
    return [calculate_autocorrelation(series, lag) for lag in range(1, max_lag + 1)]


def count_regime_peaks(
    series: list[float],
    window: int = 10,
    min_prominence: float = 0.1,
) -> int:
    """Zaehlt die Anzahl der Regime-Peaks in einer Verteilung.

    Ein Peak markiert einen Regime-Wechsel oder lokales Maximum.

    Args:
        series: Zeitreihe als Liste von float.
        window: Fenstergroesse fuer lokale Maxima-Suche.
        min_prominence: Minimale Prominenz eines Peaks.

    Returns:
        Anzahl der erkannten Peaks.
    """
    if len(series) < window * 2:
        return 1

    data = np.array(series, dtype=float)

    # Simple peak detection: local maxima
    peaks = 0
    half_window = window // 2

    for i in range(half_window, len(data) - half_window):
        left_max = np.max(data[i - half_window : i])
        right_max = np.max(data[i + 1 : i + half_window + 1])
        current = data[i]

        if current > left_max and current > right_max:
            # Check prominence
            prominence = current - max(left_max, right_max)
            if prominence >= min_prominence:
                peaks += 1

    return max(1, peaks)  # At least 1 regime


def calculate_volatility(
    series: list[float],
    window: Optional[int] = None,
) -> float:
    """Berechnet die Volatilitaet (Standardabweichung der Returns).

    Args:
        series: Zeitreihe als Liste von float.
        window: Fenstergroesse. Default: gesamte Serie.

    Returns:
        Volatilitaet als Standardabweichung.
    """
    if len(series) < 2:
        return 0.0

    data = np.array(series, dtype=float)

    if window is not None and window < len(data):
        data = data[-window:]

    # Calculate returns (percentage changes)
    returns = np.diff(data) / np.where(data[:-1] != 0, data[:-1], 1e-10)

    return float(np.std(returns))


def calculate_coefficient_of_variation(series: list[float]) -> float:
    """Berechnet den Variationskoeffizienten (CV = std / mean).

    Args:
        series: Zeitreihe als Liste von float.

    Returns:
        Variationskoeffizient. 0 wenn mean ~ 0.
    """
    if len(series) < 2:
        return 0.0

    data = np.array(series, dtype=float)
    mean_val = np.mean(data)
    std_val = np.std(data)

    if abs(mean_val) < 1e-10:
        return 0.0

    return std_val / abs(mean_val)


def calculate_stability_score(series: list[float]) -> float:
    """Berechnet einen Stabilitaets-Score basierend auf CV.

    stability = 1 - CV (geclampt auf [0, 1])

    Args:
        series: Zeitreihe als Liste von float.

    Returns:
        Stabilitaets-Score [0, 1]. Hoeher = stabiler.
    """
    cv = calculate_coefficient_of_variation(series)
    return max(0.0, min(1.0, 1.0 - cv))


__all__ = [
    "calculate_hurst_exponent",
    "calculate_autocorrelation",
    "calculate_autocorrelation_series",
    "count_regime_peaks",
    "calculate_volatility",
    "calculate_coefficient_of_variation",
    "calculate_stability_score",
]
