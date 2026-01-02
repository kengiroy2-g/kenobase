"""Popularity-Risk Module - Spieler-Popularitaet als Risiko-Proxy (POP-001).

Kombiniert Birthday-Score und Pattern-Risk zu einem PopularityRiskScore,
der als Risiko-Proxy fuer Spielentscheidungen dient.

Basiert auf:
- anti_birthday.py: Birthday-Score (1-31 bevorzugt von Spielern)
- popularity_correlation.py: calculate_birthday_score(), SCHOENE_ZAHLEN

Axiom-First Grundlage:
- A2 (Dauerscheine): Spieler nutzen feste Kombinationen
- A3 (Attraktivitaet): System bevorzugt "populaere" Gewinne fuer PR
- Hypothese: Hohe Popularitaet = mehr Konkurrenz = niedrigerer EV
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

import numpy as np

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


# Birthday numbers (1-31) - empirisch populaerer
BIRTHDAY_NUMBERS = set(range(1, 32))

# "Schoene Zahlen" - aesthetisch bevorzugt
SCHOENE_ZAHLEN = {7, 11, 13, 17, 21, 33, 37, 42, 49, 55, 66, 69, 70}

# Pattern-Typen die Spieler bevorzugen
ROUND_NUMBERS = {10, 20, 30, 40, 50, 60, 70}
LUCKY_NUMBERS = {7, 13, 21, 77}  # 77 not in KENO but pattern


class PopularityRiskLevel(Enum):
    """Risiko-Level basierend auf Popularitaets-Score."""

    LOW = "LOW"  # score < 0.3 - wenig Konkurrenz
    MEDIUM = "MEDIUM"  # 0.3 <= score < 0.6
    HIGH = "HIGH"  # 0.6 <= score < 0.8
    VERY_HIGH = "VERY_HIGH"  # score >= 0.8 - viel Konkurrenz


@dataclass(frozen=True)
class PopularityRiskScore:
    """Kombinierter Popularitaets-Risiko-Score fuer eine Zahlenmenge.

    Attributes:
        score: Gesamt-Risiko-Score (0.0 - 1.0)
        birthday_score: Anteil Birthday-Zahlen (0.0 - 1.0)
        pattern_score: Anteil Pattern-Zahlen (0.0 - 1.0)
        competition_factor: Geschaetzter Konkurrenz-Faktor (1.0 = Baseline)
        risk_level: Kategorisiertes Risiko-Level
        numbers: Die bewerteten Zahlen
    """

    score: float
    birthday_score: float
    pattern_score: float
    competition_factor: float
    risk_level: PopularityRiskLevel
    numbers: tuple[int, ...]

    def to_dict(self) -> dict:
        """Serialisiere zu Dictionary."""
        return {
            "score": round(self.score, 4),
            "birthday_score": round(self.birthday_score, 4),
            "pattern_score": round(self.pattern_score, 4),
            "competition_factor": round(self.competition_factor, 4),
            "risk_level": self.risk_level.value,
            "numbers": list(self.numbers),
        }


def calculate_birthday_score(numbers: list[int]) -> float:
    """Berechne Birthday-Score (Anteil 1-31).

    Wiederverwendet aus popularity_correlation.py.

    Args:
        numbers: Liste von KENO-Zahlen

    Returns:
        Score 0.0-1.0 (1.0 = alle Birthday-Zahlen)
    """
    if not numbers:
        return 0.0
    birthday_count = sum(1 for n in numbers if n in BIRTHDAY_NUMBERS)
    return birthday_count / len(numbers)


def calculate_pattern_score(numbers: list[int]) -> float:
    """Berechne Pattern-Score (Anteil populaerer Muster).

    Pattern-Typen:
    - Schoene Zahlen (7, 11, 13, etc.)
    - Runde Zahlen (10, 20, 30, etc.)
    - Konsekutive Paare (z.B. 5-6, 11-12)
    - Symmetrische Zahlen (11, 22, 33, etc.)

    Args:
        numbers: Liste von KENO-Zahlen

    Returns:
        Score 0.0-1.0 (1.0 = alle Pattern-Zahlen)
    """
    if not numbers:
        return 0.0

    pattern_count = 0
    sorted_nums = sorted(numbers)

    for n in sorted_nums:
        # Schoene Zahlen
        if n in SCHOENE_ZAHLEN:
            pattern_count += 1
            continue

        # Runde Zahlen
        if n in ROUND_NUMBERS:
            pattern_count += 1
            continue

        # Symmetrische Zahlen (11, 22, 33, 44, 55, 66)
        if n in {11, 22, 33, 44, 55, 66}:
            pattern_count += 1
            continue

    # Konsekutive Paare zaehlen
    consecutive_pairs = 0
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            consecutive_pairs += 1

    # Konsekutive Paare erhoehen Pattern-Score leicht
    if len(numbers) > 1:
        consecutive_ratio = consecutive_pairs / (len(numbers) - 1)
        # Max 0.2 extra fuer viele konsekutive
        pattern_count += consecutive_ratio * 0.2 * len(numbers)

    return min(pattern_count / len(numbers), 1.0)


def estimate_competition_factor(
    birthday_score: float,
    pattern_score: float,
    *,
    birthday_weight: float = 0.6,
    pattern_weight: float = 0.4,
    base_multiplier: float = 1.3,
) -> float:
    """Schaetze Konkurrenz-Faktor basierend auf Popularitaet.

    Basiert auf empirischen Daten aus HYP-004/HYP-010:
    - 30% mehr Gewinner bei Birthday-lastigen Ziehungen (1.3x)
    - Winner-Ratio korreliert mit Birthday-Score (r=0.3921)

    Der Konkurrenz-Faktor gibt an, wie viele Mitspieler
    wahrscheinlich die gleichen Zahlen gewaehlt haben.

    Args:
        birthday_score: Birthday-Score (0.0 - 1.0)
        pattern_score: Pattern-Score (0.0 - 1.0)
        birthday_weight: Gewichtung Birthday-Score (default 0.6)
        pattern_weight: Gewichtung Pattern-Score (default 0.4)
        base_multiplier: Maximaler Konkurrenz-Faktor (default 1.3)

    Returns:
        Konkurrenz-Faktor (1.0 = Baseline, >1.0 = mehr Konkurrenz)
    """
    # Kombinierter Score
    combined = (birthday_score * birthday_weight +
                pattern_score * pattern_weight)

    # Konkurrenz-Faktor: 1.0 bei combined=0, base_multiplier bei combined=1.0
    return 1.0 + combined * (base_multiplier - 1.0)


def calculate_popularity_risk_score(
    numbers: list[int],
    *,
    birthday_weight: float = 0.6,
    pattern_weight: float = 0.4,
) -> PopularityRiskScore:
    """Berechne kombinierten Popularitaets-Risiko-Score.

    Kombiniert Birthday-Score und Pattern-Score zu einem
    Gesamt-Risiko-Score fuer Konkurrenz-Schaetzung.

    Args:
        numbers: Liste von KENO-Zahlen (1-70)
        birthday_weight: Gewichtung Birthday-Score
        pattern_weight: Gewichtung Pattern-Score

    Returns:
        PopularityRiskScore mit allen Metriken

    Raises:
        ValueError: Bei leerer Zahlenliste oder invaliden Zahlen
    """
    if not numbers:
        raise ValueError("Zahlenliste darf nicht leer sein")

    # Validiere Zahlen
    for n in numbers:
        if not isinstance(n, (int, np.integer)) or n < 1 or n > 70:
            raise ValueError(f"Ungueltige KENO-Zahl: {n}")

    # Berechne Teil-Scores
    birthday_score = calculate_birthday_score(numbers)
    pattern_score = calculate_pattern_score(numbers)

    # Kombinierter Score
    combined_score = (birthday_score * birthday_weight +
                      pattern_score * pattern_weight)

    # Konkurrenz-Faktor
    competition_factor = estimate_competition_factor(
        birthday_score,
        pattern_score,
        birthday_weight=birthday_weight,
        pattern_weight=pattern_weight,
    )

    # Risiko-Level
    if combined_score < 0.3:
        risk_level = PopularityRiskLevel.LOW
    elif combined_score < 0.6:
        risk_level = PopularityRiskLevel.MEDIUM
    elif combined_score < 0.8:
        risk_level = PopularityRiskLevel.HIGH
    else:
        risk_level = PopularityRiskLevel.VERY_HIGH

    return PopularityRiskScore(
        score=combined_score,
        birthday_score=birthday_score,
        pattern_score=pattern_score,
        competition_factor=competition_factor,
        risk_level=risk_level,
        numbers=tuple(sorted(numbers)),
    )


def should_play(
    numbers: list[int],
    *,
    max_risk_score: float = 0.7,
    max_competition_factor: float = 1.2,
) -> tuple[bool, str]:
    """Entscheide ob eine Kombination gespielt werden sollte.

    Basiert auf Popularitaets-Risiko: Hohe Popularitaet
    bedeutet mehr Konkurrenz und damit niedrigeren EV.

    Args:
        numbers: Liste von KENO-Zahlen
        max_risk_score: Maximaler akzeptabler Risiko-Score
        max_competition_factor: Maximaler akzeptabler Konkurrenz-Faktor

    Returns:
        Tuple (should_play, reason)
    """
    try:
        risk = calculate_popularity_risk_score(numbers)
    except ValueError as e:
        return False, f"Ungueltige Zahlen: {e}"

    # Pruefe Risiko-Score
    if risk.score > max_risk_score:
        return False, (
            f"Risiko-Score zu hoch: {risk.score:.2f} > {max_risk_score:.2f}. "
            f"Zu viel Konkurrenz erwartet."
        )

    # Pruefe Konkurrenz-Faktor
    if risk.competition_factor > max_competition_factor:
        return False, (
            f"Konkurrenz-Faktor zu hoch: {risk.competition_factor:.2f}x. "
            f"Erwarteter EV sinkt."
        )

    # Alles OK
    if risk.risk_level == PopularityRiskLevel.LOW:
        reason = "Niedrige Popularitaet = wenig Konkurrenz. Guter EV."
    elif risk.risk_level == PopularityRiskLevel.MEDIUM:
        reason = "Moderate Popularitaet. Akzeptabler EV."
    else:
        reason = f"Hohe Popularitaet ({risk.risk_level.value}), aber unter Grenzwerten."

    return True, reason


def adjust_recommendation_by_popularity(
    numbers: list[int],
    base_score: float,
    *,
    popularity_penalty_weight: float = 0.2,
) -> float:
    """Passe einen Empfehlungs-Score basierend auf Popularitaet an.

    Hohe Popularitaet reduziert den Score, da mehr Konkurrenz
    erwartet wird und damit der EV sinkt.

    Args:
        numbers: Liste von KENO-Zahlen
        base_score: Basis-Score aus anderen Analysen (0.0 - 1.0)
        popularity_penalty_weight: Gewichtung der Penalty

    Returns:
        Angepasster Score (0.0 - 1.0)
    """
    try:
        risk = calculate_popularity_risk_score(numbers)
    except ValueError:
        return base_score  # Bei Fehler keine Anpassung

    # Penalty basierend auf Risiko-Score
    penalty = risk.score * popularity_penalty_weight

    # Angepasster Score
    adjusted = base_score * (1.0 - penalty)

    return max(0.0, min(1.0, adjusted))


def analyze_draw_popularity(
    drawn_numbers: list[int],
) -> dict:
    """Analysiere Popularitaet einer Ziehung.

    Nuetzlich fuer Rueckblick-Analyse: Waren die gezogenen
    Zahlen populaer (viele Gewinner) oder unpopulaer?

    Args:
        drawn_numbers: Liste von 20 gezogenen KENO-Zahlen

    Returns:
        Dict mit Analyse-Ergebnissen
    """
    if len(drawn_numbers) != 20:
        logger.warning(
            f"Erwarte 20 Zahlen, erhalten: {len(drawn_numbers)}"
        )

    risk = calculate_popularity_risk_score(drawn_numbers)

    # Erwartete Gewinner-Multiplikator
    # Bei hoher Popularitaet: mehr Gewinner erwartet
    expected_winner_multiplier = risk.competition_factor

    # Strategie-Empfehlung
    if risk.risk_level in (PopularityRiskLevel.HIGH, PopularityRiskLevel.VERY_HIGH):
        strategy_hint = "Ziehung war populaer - viele Gewinner erwartet"
    else:
        strategy_hint = "Ziehung war unpopulaer - weniger Gewinner erwartet"

    return {
        "popularity_risk": risk.to_dict(),
        "expected_winner_multiplier": round(expected_winner_multiplier, 4),
        "strategy_hint": strategy_hint,
        "drawn_birthday_count": sum(1 for n in drawn_numbers if n in BIRTHDAY_NUMBERS),
        "drawn_pattern_count": len([n for n in drawn_numbers if n in SCHOENE_ZAHLEN]),
    }


__all__ = [
    "PopularityRiskScore",
    "PopularityRiskLevel",
    "BIRTHDAY_NUMBERS",
    "SCHOENE_ZAHLEN",
    "calculate_birthday_score",
    "calculate_pattern_score",
    "estimate_competition_factor",
    "calculate_popularity_risk_score",
    "should_play",
    "adjust_recommendation_by_popularity",
    "analyze_draw_popularity",
]
