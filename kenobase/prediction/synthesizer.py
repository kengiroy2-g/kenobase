"""Hypothesen-Synthesizer - Kombiniert Ergebnisse aus verschiedenen Analysen.

Dieses Modul liest die Ergebnisse aller HYP-Analysen (JSON-Dateien in results/)
und berechnet einen kombinierten Score pro Zahl (1-70 fuer KENO).

Verfuegbare Hypothesen (per Proxy-Review verifiziert):
- HYP-007: Duo/Trio/Quatro Pattern Validation (NOT SIGNIFICANT)
- HYP-010: Odds Correlation (safe_numbers, popular_numbers)
- HYP-011: Temporal Cycles (holiday_analysis SIGNIFICANT)
- HYP-012: Stake Correlation (low_stake, high_stake numbers)

Scoring-Ansatz:
- Jede Hypothese liefert 0-1 normalisierte Scores
- Gewichtung basiert auf statistischer Signifikanz
- Combined Score = gewichtete Summe / Summe der Gewichte
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class HypothesisScore:
    """Score einer Zahl fuer eine einzelne Hypothese."""

    hypothesis_id: str
    score: float  # 0.0 - 1.0
    is_significant: bool
    weight: float  # Gewichtung basierend auf Signifikanz
    reason: str


@dataclass
class NumberScore:
    """Kombinierter Score fuer eine einzelne Zahl."""

    number: int
    combined_score: float
    hypothesis_scores: dict[str, HypothesisScore] = field(default_factory=dict)
    tier: str = "C"  # A/B/C basierend auf combined_score


class HypothesisSynthesizer:
    """Kombiniert Ergebnisse aus verschiedenen Hypothesen-Analysen."""

    # Gewichtung basierend auf Signifikanz und Relevanz
    DEFAULT_WEIGHTS = {
        "HYP-007": 0.1,   # Nicht signifikant, aber Pattern-Info nuetzlich
        "HYP-010": 0.3,   # Odds-Korrelation, teilweise signifikant
        "HYP-011": 0.3,   # Temporal, Feiertags-Effekt signifikant
        "HYP-012": 0.3,   # Stake-Korrelation, Auszahlung signifikant
    }

    def __init__(
        self,
        results_dir: str = "results",
        numbers_range: tuple[int, int] = (1, 70),
        weights: Optional[dict[str, float]] = None,
    ):
        """Initialisiert den Synthesizer.

        Args:
            results_dir: Pfad zum Ergebnis-Verzeichnis.
            numbers_range: Zahlenbereich (min, max), default KENO (1-70).
            weights: Optionale benutzerdefinierte Gewichtung pro Hypothese.
        """
        self.results_dir = Path(results_dir)
        self.numbers_range = numbers_range
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._hyp_results: dict[str, dict] = {}

    def load_results(self) -> dict[str, dict]:
        """Laedt alle HYP-Ergebnisse aus dem results-Verzeichnis.

        Returns:
            Dict mit Hypothesen-ID als Key und JSON-Daten als Value.
        """
        if not self.results_dir.exists():
            logger.warning(f"Results directory not found: {self.results_dir}")
            return {}

        results = {}
        for json_file in self.results_dir.glob("hyp*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    hyp_id = data.get("hypothesis", data.get("hypothesis_id", ""))
                    if hyp_id:
                        results[hyp_id] = data
                        logger.info(f"Loaded {hyp_id} from {json_file.name}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load {json_file}: {e}")

        self._hyp_results = results
        return results

    def _extract_hyp007_scores(self, data: dict) -> dict[int, HypothesisScore]:
        """Extrahiert Scores aus HYP-007 (Pattern Validation).

        Zahlen die in Top-Patterns vorkommen bekommen hoeheren Score.
        """
        scores = {}
        pattern_numbers: dict[int, int] = {}  # Zahl -> Haeufigkeit in Top-Patterns

        # Sammle alle Zahlen aus Top-10 Patterns (Duos, Trios, Quatros)
        for pattern_type in ["duo", "trio", "quatro"]:
            patterns = data.get("results", {}).get(pattern_type, {})
            for pattern_info in patterns.get("top_10_patterns", []):
                for num in pattern_info.get("pattern", []):
                    pattern_numbers[num] = pattern_numbers.get(num, 0) + 1

        # Normalisiere auf 0-1
        max_count = max(pattern_numbers.values()) if pattern_numbers else 1

        for number in range(self.numbers_range[0], self.numbers_range[1] + 1):
            count = pattern_numbers.get(number, 0)
            score = count / max_count if max_count > 0 else 0.0
            scores[number] = HypothesisScore(
                hypothesis_id="HYP-007",
                score=score,
                is_significant=False,  # Keine Patterns signifikant
                weight=self.weights.get("HYP-007", 0.1),
                reason=f"In {count} Top-Patterns" if count > 0 else "Nicht in Top-Patterns",
            )

        return scores

    def _extract_hyp010_scores(self, data: dict) -> dict[int, HypothesisScore]:
        """Extrahiert Scores aus HYP-010 (Odds Correlation).

        Safe numbers (wenige Mitspieler) bekommen hoeheren Score.
        Popular numbers (viele Mitspieler) bekommen niedrigeren Score.
        """
        scores = {}
        classification = data.get("classification", {})
        safe_numbers = set(classification.get("safe_numbers", []))
        popular_numbers = set(classification.get("popular_numbers", []))

        for number in range(self.numbers_range[0], self.numbers_range[1] + 1):
            if number in safe_numbers:
                score = 0.8  # Hoeher: weniger Mitspieler = bessere Quote
                reason = "Safe (wenige Mitspieler)"
            elif number in popular_numbers:
                score = 0.2  # Niedriger: viele Mitspieler = schlechtere Quote
                reason = "Popular (viele Mitspieler)"
            else:
                score = 0.5  # Neutral
                reason = "Neutral"

            scores[number] = HypothesisScore(
                hypothesis_id="HYP-010",
                score=score,
                is_significant=False,  # Korrelation nicht signifikant
                weight=self.weights.get("HYP-010", 0.3),
                reason=reason,
            )

        return scores

    def _extract_hyp011_scores(self, data: dict) -> dict[int, HypothesisScore]:
        """Extrahiert Scores aus HYP-011 (Temporal Cycles).

        Diese Hypothese hat keine per-number Scores, aber der Feiertags-Effekt
        ist signifikant. Wir geben allen Zahlen einen Basis-Score.
        """
        scores = {}
        holiday = data.get("holiday_analysis", {})
        is_sig = holiday.get("is_significant", False)
        confidence = data.get("confidence", 0.5)

        # Da keine per-number Daten: alle Zahlen bekommen Basis-Score
        base_score = confidence if is_sig else 0.5

        for number in range(self.numbers_range[0], self.numbers_range[1] + 1):
            scores[number] = HypothesisScore(
                hypothesis_id="HYP-011",
                score=base_score,
                is_significant=is_sig,
                weight=self.weights.get("HYP-011", 0.3) * (1.5 if is_sig else 1.0),
                reason=f"Feiertags-Effekt {'signifikant' if is_sig else 'nicht signifikant'}",
            )

        return scores

    def _extract_hyp012_scores(self, data: dict) -> dict[int, HypothesisScore]:
        """Extrahiert Scores aus HYP-012 (Stake Correlation).

        Low-stake numbers (wenig Einsatz) bekommen hoeheren Score.
        High-stake numbers (viel Einsatz) bekommen niedrigeren Score.
        """
        scores = {}
        classification = data.get("classification", {})
        low_stake = set(classification.get("low_stake_numbers", []))
        high_stake = set(classification.get("high_stake_numbers", []))

        # Auszahlung-Korrelation ist signifikant!
        payout_sig = data.get("correlation", {}).get("total_auszahlung", {}).get("is_significant", False)

        for number in range(self.numbers_range[0], self.numbers_range[1] + 1):
            if number in low_stake:
                score = 0.75  # Hoeher: weniger Einsatz = potenziell bessere Quote
                reason = "Low-Stake (weniger Einsatz)"
            elif number in high_stake:
                score = 0.25  # Niedriger: mehr Einsatz = mehr Konkurrenz
                reason = "High-Stake (mehr Einsatz)"
            else:
                score = 0.5  # Neutral
                reason = "Neutral"

            scores[number] = HypothesisScore(
                hypothesis_id="HYP-012",
                score=score,
                is_significant=payout_sig,
                weight=self.weights.get("HYP-012", 0.3) * (1.5 if payout_sig else 1.0),
                reason=reason,
            )

        return scores

    def synthesize(self) -> dict[int, NumberScore]:
        """Berechnet kombinierte Scores fuer alle Zahlen.

        Returns:
            Dict mit Zahl als Key und NumberScore als Value.
        """
        if not self._hyp_results:
            self.load_results()

        # Sammle Scores pro Hypothese
        all_scores: dict[str, dict[int, HypothesisScore]] = {}

        extractors = {
            "HYP-007": self._extract_hyp007_scores,
            "HYP-010": self._extract_hyp010_scores,
            "HYP-011": self._extract_hyp011_scores,
            "HYP-012": self._extract_hyp012_scores,
        }

        for hyp_id, extractor in extractors.items():
            if hyp_id in self._hyp_results:
                all_scores[hyp_id] = extractor(self._hyp_results[hyp_id])
                logger.info(f"Extracted scores from {hyp_id}")

        # Kombiniere Scores
        number_scores: dict[int, NumberScore] = {}

        for number in range(self.numbers_range[0], self.numbers_range[1] + 1):
            hyp_scores: dict[str, HypothesisScore] = {}
            total_weighted_score = 0.0
            total_weight = 0.0

            for hyp_id, scores in all_scores.items():
                if number in scores:
                    hs = scores[number]
                    hyp_scores[hyp_id] = hs
                    total_weighted_score += hs.score * hs.weight
                    total_weight += hs.weight

            combined = total_weighted_score / total_weight if total_weight > 0 else 0.5

            # Tier basierend auf combined_score
            if combined >= 0.7:
                tier = "A"
            elif combined >= 0.5:
                tier = "B"
            else:
                tier = "C"

            number_scores[number] = NumberScore(
                number=number,
                combined_score=combined,
                hypothesis_scores=hyp_scores,
                tier=tier,
            )

        return number_scores

    def get_top_numbers(self, n: int = 10) -> list[NumberScore]:
        """Gibt die Top-N Zahlen nach combined_score zurueck.

        Args:
            n: Anzahl der zurueckzugebenden Zahlen.

        Returns:
            Liste von NumberScore, absteigend sortiert nach combined_score.
        """
        scores = self.synthesize()
        sorted_scores = sorted(
            scores.values(),
            key=lambda x: x.combined_score,
            reverse=True,
        )
        return sorted_scores[:n]

    def to_dict(self) -> dict:
        """Exportiert Synthesizer-Ergebnisse als Dict.

        Returns:
            Dict mit allen Scores und Metadaten.
        """
        scores = self.synthesize()
        return {
            "synthesis_type": "hypothesis_combination",
            "numbers_range": list(self.numbers_range),
            "hypotheses_used": list(self._hyp_results.keys()),
            "weights": self.weights,
            "scores": {
                num: {
                    "number": ns.number,
                    "combined_score": round(ns.combined_score, 4),
                    "tier": ns.tier,
                    "hypothesis_scores": {
                        hyp_id: {
                            "score": round(hs.score, 4),
                            "weight": round(hs.weight, 4),
                            "is_significant": hs.is_significant,
                            "reason": hs.reason,
                        }
                        for hyp_id, hs in ns.hypothesis_scores.items()
                    },
                }
                for num, ns in scores.items()
            },
        }


__all__ = ["HypothesisSynthesizer", "NumberScore", "HypothesisScore"]
