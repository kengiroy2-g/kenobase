"""HYP-001: Near-Miss Analyse.

Analysiert Faelle wo Spieler knapp am Hauptgewinn vorbei sind.
Near-Miss: Eine Gewinnklasse unter dem Maximum.

Hypothese: Ueberdurchschnittlich viele Near-Miss Faelle koennten auf
Spieler-Bindungsstrategie hindeuten ("fast gewonnen" motiviert Weiterspielen).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class NearMissResult:
    """Ergebnis der Near-Miss Analyse fuer einen Keno-Typ.

    Attributes:
        keno_type: Keno-Typ (2-10)
        max_matches: Maximale Treffer fuer vollen Gewinn
        near_miss_matches: Treffer fuer Near-Miss (max - 1)
        near_miss_ratio: Verhaeltnis near_miss_winners / max_winners
        expected_ratio: Erwartetes Verhaeltnis (theoretisch)
        chi2_stat: Chi-Quadrat Statistik
        p_value: p-Wert des Tests
        is_significant: True wenn p < 0.05
        n_draws: Anzahl analysierter Ziehungen
    """

    keno_type: int
    max_matches: int
    near_miss_matches: int
    near_miss_ratio: float
    expected_ratio: float
    chi2_stat: float
    p_value: float
    is_significant: bool
    n_draws: int


def _keno_match_probability(
    keno_type: int,
    matches: int,
    *,
    numbers_range: int = 70,
    numbers_drawn: int = 20,
) -> float:
    """Hypergeometric probability for exactly `matches` hits when selecting `keno_type` numbers.

    P(X=m) = C(k, m) * C(N-k, n-m) / C(N, n)
    """
    if matches < 0 or matches > keno_type:
        return 0.0
    misses = numbers_drawn - matches
    if misses < 0:
        return 0.0
    if misses > (numbers_range - keno_type):
        return 0.0
    denom = math.comb(numbers_range, numbers_drawn)
    return (
        math.comb(keno_type, matches)
        * math.comb(numbers_range - keno_type, misses)
        / denom
    )


def _build_keno_probabilities() -> dict[int, dict[int, float]]:
    """Build exact probabilities for Keno-Typ 2..10 (20 drawn out of 70)."""
    table: dict[int, dict[int, float]] = {}
    for keno_type in range(2, 11):
        table[keno_type] = {
            matches: _keno_match_probability(keno_type, matches)
            for matches in range(0, keno_type + 1)
        }
    return table


# Theoretische Wahrscheinlichkeiten (Hypergeometrisch):
# - 20 Zahlen werden aus 70 gezogen
# - Spieler wählt k=Keno-Typ Zahlen
KENO_PROBABILITIES = _build_keno_probabilities()


def calculate_expected_ratio(keno_type: int) -> float:
    """Berechnet das erwartete Near-Miss/Max-Treffer Verhaeltnis.

    Args:
        keno_type: Keno-Typ (2-10)

    Returns:
        Erwartetes Verhaeltnis P(max-1) / P(max)
    """
    if keno_type not in KENO_PROBABILITIES:
        return 1.0

    probs = KENO_PROBABILITIES[keno_type]
    max_matches = keno_type
    near_miss = keno_type - 1

    p_max = probs.get(max_matches, 0.001)
    p_near = probs.get(near_miss, 0.001)

    return p_near / p_max if p_max > 0 else 1.0


def analyze_near_miss(
    df: pd.DataFrame,
    keno_type: int,
) -> NearMissResult:
    """Analysiert Near-Miss Faelle fuer einen Keno-Typ.

    Args:
        df: DataFrame mit GQ-Daten
        keno_type: Keno-Typ (2-10)

    Returns:
        NearMissResult
    """
    # Filter auf Keno-Typ
    data = df[df["Keno-Typ"] == keno_type].copy()

    max_matches = keno_type
    near_miss_matches = keno_type - 1

    # Gruppiere nach Datum um Ziehungen zu zaehlen
    draws = data.groupby("Datum")
    n_draws = len(draws)

    # Summe Gewinner pro Kategorie
    max_data = data[data["Anzahl richtiger Zahlen"] == max_matches]
    near_data = data[data["Anzahl richtiger Zahlen"] == near_miss_matches]

    max_winners = max_data["Anzahl der Gewinner"].sum() if len(max_data) > 0 else 0
    near_winners = near_data["Anzahl der Gewinner"].sum() if len(near_data) > 0 else 0

    # Beobachtetes Verhaeltnis
    observed_ratio = near_winners / max_winners if max_winners > 0 else 0.0

    # Erwartetes Verhaeltnis
    expected_ratio = calculate_expected_ratio(keno_type)

    # Chi-Quadrat Test
    # H0: Beobachtete Verteilung entspricht theoretischer
    if max_winners > 0 and near_winners > 0:
        # Erwartete Werte basierend auf Gesamtsumme und theoretischen Proportionen
        total = max_winners + near_winners
        p_max = 1 / (1 + expected_ratio)
        p_near = expected_ratio / (1 + expected_ratio)

        expected = np.array([total * p_max, total * p_near])
        observed = np.array([max_winners, near_winners])

        chi2, p_value = stats.chisquare(observed, expected)
    else:
        chi2, p_value = 0.0, 1.0

    return NearMissResult(
        keno_type=keno_type,
        max_matches=max_matches,
        near_miss_matches=near_miss_matches,
        near_miss_ratio=round(observed_ratio, 4),
        expected_ratio=round(expected_ratio, 4),
        chi2_stat=round(float(chi2), 4),
        p_value=round(float(p_value), 6),
        is_significant=float(p_value) < 0.05,
        n_draws=n_draws,
    )


def analyze_all_near_miss(df: pd.DataFrame) -> list[NearMissResult]:
    """Analysiert Near-Miss fuer alle Keno-Typen.

    Args:
        df: DataFrame mit GQ-Daten

    Returns:
        Liste von NearMissResult
    """
    results = []

    for keno_type in range(2, 11):
        if keno_type in df["Keno-Typ"].values:
            result = analyze_near_miss(df, keno_type)
            results.append(result)

            status = "SIGNIFICANT" if result.is_significant else "normal"
            logger.info(
                f"Keno-Typ {keno_type}: near_miss_ratio={result.near_miss_ratio:.2f}, "
                f"expected={result.expected_ratio:.2f}, p={result.p_value:.4f} [{status}]"
            )

    return results


def count_significant_anomalies(results: list[NearMissResult]) -> int:
    """Zaehlt signifikante Anomalien.

    Args:
        results: Liste von NearMissResult

    Returns:
        Anzahl signifikanter Near-Miss Anomalien
    """
    return sum(1 for r in results if r.is_significant)


__all__ = [
    "NearMissResult",
    "KENO_PROBABILITIES",
    "calculate_expected_ratio",
    "analyze_near_miss",
    "analyze_all_near_miss",
    "count_significant_anomalies",
]
