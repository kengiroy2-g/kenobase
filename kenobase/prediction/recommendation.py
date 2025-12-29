"""Recommendation Engine - Generiert Spielempfehlungen basierend auf Synthese-Scores.

Dieses Modul wandelt die kombinierten Zahlen-Scores in konkrete
Spielempfehlungen um, unter Beruecksichtigung von:
- Zehnergruppen-Filter (max 2 pro Gruppe)
- Avalanche-Theorie (max 4 Zahlen empfohlen)
- Tier-basierte Klassifikation (A/B/C)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from kenobase.prediction.synthesizer import NumberScore

logger = logging.getLogger(__name__)


class RecommendationTier(Enum):
    """Empfehlungs-Tiers basierend auf Combined Score."""

    A = "A"  # combined_score >= 0.7, starke Empfehlung
    B = "B"  # 0.5 <= combined_score < 0.7, moderate Empfehlung
    C = "C"  # combined_score < 0.5, keine Empfehlung


@dataclass
class Recommendation:
    """Eine einzelne Zahlen-Empfehlung."""

    number: int
    combined_score: float
    tier: RecommendationTier
    reasons: list[str]
    decade: int  # Zehnergruppe (1-10 -> 1, 11-20 -> 2, etc.)


def get_decade(number: int) -> int:
    """Bestimmt die Zehnergruppe einer Zahl.

    Args:
        number: Zahl (1-70).

    Returns:
        Zehnergruppe (1-7 fuer KENO).
    """
    return ((number - 1) // 10) + 1


def apply_decade_filter(
    numbers: list[NumberScore],
    max_per_decade: int = 2,
) -> list[NumberScore]:
    """Wendet Zehnergruppen-Filter an.

    Behaelt maximal max_per_decade Zahlen pro Zehnergruppe,
    priorisiert nach combined_score.

    Args:
        numbers: Liste von NumberScore, sortiert nach Score.
        max_per_decade: Maximum Zahlen pro Zehnergruppe.

    Returns:
        Gefilterte Liste von NumberScore.
    """
    decade_counts: dict[int, int] = {}
    filtered: list[NumberScore] = []

    for ns in numbers:
        decade = get_decade(ns.number)
        count = decade_counts.get(decade, 0)

        if count < max_per_decade:
            filtered.append(ns)
            decade_counts[decade] = count + 1

    return filtered


def generate_recommendations(
    scores: dict[int, NumberScore],
    top_n: int = 6,
    max_per_decade: int = 2,
    anti_avalanche_limit: Optional[int] = 4,
) -> list[Recommendation]:
    """Generiert Spielempfehlungen basierend auf Synthese-Scores.

    Args:
        scores: Dict mit Zahl -> NumberScore aus Synthesizer.
        top_n: Anzahl der Empfehlungen (default 6 fuer KENO-Typ).
        max_per_decade: Maximum Zahlen pro Zehnergruppe.
        anti_avalanche_limit: Max Zahlen wegen Avalanche-Theorie (None = kein Limit).

    Returns:
        Liste von Recommendation, sortiert nach Score.
    """
    # Sortiere nach combined_score absteigend
    sorted_scores = sorted(
        scores.values(),
        key=lambda x: x.combined_score,
        reverse=True,
    )

    # Wende Zehnergruppen-Filter an
    filtered = apply_decade_filter(sorted_scores, max_per_decade)

    # Limitiere auf top_n
    top_scores = filtered[:top_n]

    # Warne bei Avalanche-Risiko
    if anti_avalanche_limit and len(top_scores) > anti_avalanche_limit:
        logger.warning(
            f"Anti-Avalanche: {len(top_scores)} Zahlen empfohlen, "
            f"aber Limit ist {anti_avalanche_limit}. "
            "Theta steigt exponentiell mit mehr Zahlen."
        )

    # Konvertiere zu Recommendations
    recommendations: list[Recommendation] = []

    for ns in top_scores:
        tier = RecommendationTier(ns.tier)
        reasons = []

        for hyp_id, hs in ns.hypothesis_scores.items():
            if hs.score >= 0.6:  # Nur positive Gruende auflisten
                reasons.append(f"{hyp_id}: {hs.reason}")

        recommendations.append(
            Recommendation(
                number=ns.number,
                combined_score=ns.combined_score,
                tier=tier,
                reasons=reasons,
                decade=get_decade(ns.number),
            )
        )

    return recommendations


def recommendations_to_dict(recommendations: list[Recommendation]) -> dict:
    """Konvertiert Recommendations zu einem serialisierbaren Dict.

    Args:
        recommendations: Liste von Recommendation.

    Returns:
        Dict fuer JSON-Export.
    """
    return {
        "count": len(recommendations),
        "recommendations": [
            {
                "number": r.number,
                "combined_score": round(r.combined_score, 4),
                "tier": r.tier.value,
                "decade": r.decade,
                "reasons": r.reasons,
            }
            for r in recommendations
        ],
        "numbers": [r.number for r in recommendations],
        "tier_summary": {
            "A": len([r for r in recommendations if r.tier == RecommendationTier.A]),
            "B": len([r for r in recommendations if r.tier == RecommendationTier.B]),
            "C": len([r for r in recommendations if r.tier == RecommendationTier.C]),
        },
    }


def format_recommendations(recommendations: list[Recommendation]) -> str:
    """Formatiert Recommendations fuer Konsolen-Ausgabe.

    Args:
        recommendations: Liste von Recommendation.

    Returns:
        Formatierter String.
    """
    lines = [
        "=" * 60,
        "KENOBASE PREDICTION - Zahlen-Empfehlungen",
        "=" * 60,
        "",
    ]

    for i, r in enumerate(recommendations, 1):
        lines.append(f"{i}. Zahl {r.number:2d}  [Tier {r.tier.value}]  Score: {r.combined_score:.3f}")
        lines.append(f"   Zehnergruppe: {r.decade}")
        if r.reasons:
            for reason in r.reasons[:2]:  # Max 2 Gruende
                lines.append(f"   - {reason}")
        lines.append("")

    tier_a = len([r for r in recommendations if r.tier == RecommendationTier.A])
    tier_b = len([r for r in recommendations if r.tier == RecommendationTier.B])
    tier_c = len([r for r in recommendations if r.tier == RecommendationTier.C])

    lines.extend([
        "-" * 60,
        f"Zusammenfassung: {len(recommendations)} Zahlen empfohlen",
        f"  Tier A (stark): {tier_a}",
        f"  Tier B (moderat): {tier_b}",
        f"  Tier C (neutral): {tier_c}",
        "",
        f"Empfohlene Zahlen: {', '.join(str(r.number) for r in recommendations)}",
        "=" * 60,
    ])

    return "\n".join(lines)


__all__ = [
    "Recommendation",
    "RecommendationTier",
    "generate_recommendations",
    "recommendations_to_dict",
    "format_recommendations",
    "get_decade",
    "apply_decade_filter",
]
