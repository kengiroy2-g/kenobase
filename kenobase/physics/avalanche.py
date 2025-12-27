"""Avalanche-Theorie Implementation.

Dieses Modul implementiert die Self-Organized Criticality (SOC)
und Anti-Avalanche-Strategie fuer Kenobase V2.0 gemaess CLAUDE.md Section 6.4.

Kern-Konzept: theta = Verlustwahrscheinlichkeit = 1 - p^n
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class AvalancheState(str, Enum):
    """Avalanche-Zustaende basierend auf theta-Wert."""

    SAFE = "SAFE"          # theta < 0.50
    MODERATE = "MODERATE"  # 0.50 <= theta < 0.75
    WARNING = "WARNING"    # 0.75 <= theta < 0.85
    CRITICAL = "CRITICAL"  # theta >= 0.85


class AvalancheResult(NamedTuple):
    """Ergebnis der Avalanche-Berechnung."""

    theta: float
    state: AvalancheState
    is_safe_to_bet: bool


# Default thresholds
THETA_SAFE = 0.50
THETA_MODERATE = 0.75
THETA_WARNING = 0.85


def calculate_theta(precision: float, n_picks: int) -> float:
    """Berechnet die 'Neigung' theta einer Kombination (ADR-021).

    theta = Verlustwahrscheinlichkeit = 1 - p^n

    Args:
        precision: Einzelne Pick-Precision (z.B. 0.714).
        n_picks: Anzahl der Picks.

    Returns:
        theta (0.0 - 1.0).

    Example:
        >>> calculate_theta(0.7, 6)  # 6er-Kombi mit 70% Precision
        0.8823...  # CRITICAL!
    """
    if precision <= 0.0:
        return 1.0
    if precision >= 1.0:
        return 0.0
    if n_picks <= 0:
        return 0.0

    return 1.0 - (precision ** n_picks)


def get_avalanche_state(theta: float) -> AvalancheState:
    """Bestimmt Avalanche-State basierend auf theta.

    States:
        SAFE:     theta < 0.50 (Verlust < 50%)
        MODERATE: 0.50 <= theta < 0.75
        WARNING:  0.75 <= theta < 0.85
        CRITICAL: theta >= 0.85 (Verlust >= 85%)

    Args:
        theta: Berechneter theta-Wert.

    Returns:
        AvalancheState enum.
    """
    if theta < THETA_SAFE:
        return AvalancheState.SAFE
    elif theta < THETA_MODERATE:
        return AvalancheState.MODERATE
    elif theta < THETA_WARNING:
        return AvalancheState.WARNING
    else:
        return AvalancheState.CRITICAL


def get_avalanche_state_with_thresholds(
    theta: float,
    safe_threshold: float = 0.50,
    moderate_threshold: float = 0.75,
    warning_threshold: float = 0.85,
) -> AvalancheState:
    """Bestimmt Avalanche-State mit konfigurierbaren Schwellenwerten.

    Args:
        theta: Berechneter theta-Wert.
        safe_threshold: Schwelle fuer SAFE -> MODERATE.
        moderate_threshold: Schwelle fuer MODERATE -> WARNING.
        warning_threshold: Schwelle fuer WARNING -> CRITICAL.

    Returns:
        AvalancheState enum.
    """
    if theta < safe_threshold:
        return AvalancheState.SAFE
    elif theta < moderate_threshold:
        return AvalancheState.MODERATE
    elif theta < warning_threshold:
        return AvalancheState.WARNING
    else:
        return AvalancheState.CRITICAL


def is_profitable(precision: float, avg_odds: float) -> bool:
    """Prueft das Fundamental-Theorem: p * q > 1.

    Args:
        precision: Historische Trefferquote.
        avg_odds: Durchschnittliche Quote.

    Returns:
        True wenn p * q > 1 (profitabel).

    Example:
        >>> is_profitable(0.6, 2.0)  # 60% * 2.0 = 1.2 > 1
        True
        >>> is_profitable(0.4, 2.0)  # 40% * 2.0 = 0.8 < 1
        False
    """
    return precision * avg_odds > 1.0


def calculate_expected_value(precision: float, avg_odds: float, stake: float = 1.0) -> float:
    """Berechnet den erwarteten Wert eines Einsatzes.

    EV = stake * (precision * odds - 1)

    Args:
        precision: Historische Trefferquote.
        avg_odds: Durchschnittliche Quote.
        stake: Einsatzhoehe (default 1.0).

    Returns:
        Erwarteter Gewinn/Verlust pro Einsatz.
    """
    return stake * (precision * avg_odds - 1.0)


def analyze_combination(
    precision: float,
    n_picks: int,
    avg_odds: float = 1.0,
) -> AvalancheResult:
    """Analysiert eine Kombination auf Avalanche-Risiko.

    Args:
        precision: Einzelne Pick-Precision.
        n_picks: Anzahl der Picks in der Kombination.
        avg_odds: Durchschnittliche Quote (fuer Profitabilitaets-Check).

    Returns:
        AvalancheResult mit theta, state und is_safe_to_bet.
    """
    theta = calculate_theta(precision, n_picks)
    state = get_avalanche_state(theta)

    # Safe to bet if not CRITICAL and profitable
    is_safe = (
        state != AvalancheState.CRITICAL
        and (avg_odds <= 0 or is_profitable(precision ** n_picks, avg_odds))
    )

    return AvalancheResult(theta=theta, state=state, is_safe_to_bet=is_safe)


def max_picks_for_theta(precision: float, max_theta: float = 0.75) -> int:
    """Berechnet maximale Anzahl Picks fuer gegebenes theta-Limit.

    Anti-Avalanche-Strategie: Limitiere n so dass theta <= max_theta.

    Args:
        precision: Einzelne Pick-Precision.
        max_theta: Maximaler erlaubter theta-Wert.

    Returns:
        Maximale Anzahl Picks.

    Example:
        >>> max_picks_for_theta(0.7, 0.75)
        3  # Bei 70% Precision: max 3 Picks fuer theta <= 0.75
    """
    if precision <= 0.0 or precision >= 1.0:
        return 0
    if max_theta <= 0.0:
        return 0
    if max_theta >= 1.0:
        return 100  # Arbitrary large number

    import math

    # theta = 1 - p^n <= max_theta
    # p^n >= 1 - max_theta
    # n * log(p) >= log(1 - max_theta)
    # n <= log(1 - max_theta) / log(p)  # Note: log(p) < 0

    min_success_prob = 1.0 - max_theta
    if min_success_prob <= 0.0:
        return 100

    n = math.log(min_success_prob) / math.log(precision)
    return max(0, int(n))


__all__ = [
    "AvalancheState",
    "AvalancheResult",
    "THETA_SAFE",
    "THETA_MODERATE",
    "THETA_WARNING",
    "calculate_theta",
    "get_avalanche_state",
    "get_avalanche_state_with_thresholds",
    "is_profitable",
    "calculate_expected_value",
    "analyze_combination",
    "max_picks_for_theta",
]
