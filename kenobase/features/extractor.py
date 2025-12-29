"""Feature Extractor - Extrahiert Features aus Rohdaten.

Dieses Modul stellt den FeatureExtractor bereit, der alle 18+ Features
aus den Ziehungsdaten extrahiert und als FeatureVector pro Zahl zurueckgibt.

Integriert die folgenden Analysis-Module:
- frequency: freq_raw, freq_rolling, freq_hot, freq_cold
- pattern: duo_score, trio_score, quatro_score
- temporal_cycles: weekday_bias, month_bias, holiday_proximity
- popularity_correlation: is_birthday, is_schoene, is_safe
- stake_correlation: einsatz_score, auszahlung_score
- recurrence: streak_length, stability_score
- stable_numbers: law_a_score
- cluster_reset: reset_probability, cluster_signal
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np
import pandas as pd

from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


class FeatureCategory(str, Enum):
    """Feature-Kategorien."""

    FREQUENCY = "frequency"
    PATTERN = "pattern"
    TEMPORAL = "temporal"
    POPULARITY = "popularity"
    STAKE = "stake"
    RECURRENCE = "recurrence"
    STABILITY = "stability"
    CLUSTER = "cluster"


@dataclass
class FeatureVector:
    """Feature-Vektor fuer eine einzelne Zahl.

    Attributes:
        number: Die Zahl (1-70 fuer KENO)
        features: Dict mit Feature-Name -> Wert (0.0-1.0 normalisiert)
        combined_score: Gewichteter Gesamt-Score
        tier: Klassifikation (A/B/C)
        metadata: Zusaetzliche Informationen
    """

    number: int
    features: dict[str, float] = field(default_factory=dict)
    combined_score: float = 0.5
    tier: str = "C"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "number": self.number,
            "features": self.features.copy(),
            "combined_score": round(self.combined_score, 4),
            "tier": self.tier,
            "metadata": self.metadata.copy(),
        }


class FeatureExtractor:
    """Extrahiert Features aus Ziehungsdaten.

    Integriert alle Analysis-Module und berechnet 18+ Features pro Zahl.

    Verwendung:
        extractor = FeatureExtractor(numbers_range=(1, 70))
        features = extractor.extract(draws)
        # features: Dict[int, FeatureVector]
    """

    # Birthday numbers (1-31)
    BIRTHDAY_NUMBERS = set(range(1, 32))

    # "Schoene" Zahlen (optisch ansprechend)
    SCHOENE_ZAHLEN = {7, 11, 13, 17, 21, 33, 37, 44, 55, 66, 69, 70}

    def __init__(
        self,
        numbers_range: tuple[int, int] = (1, 70),
        numbers_to_draw: int = 20,
        hot_threshold: float = 0.37,
        cold_threshold: float = 0.20,
        rolling_window: int = 50,
        stability_threshold: float = 0.90,
    ):
        """Initialisiert den Extractor.

        Args:
            numbers_range: Zahlenbereich (min, max)
            numbers_to_draw: Anzahl gezogener Zahlen pro Ziehung
            hot_threshold: Schwelle fuer "hot" Klassifikation
            cold_threshold: Schwelle fuer "cold" Klassifikation
            rolling_window: Fenstergroesse fuer Rolling-Features
            stability_threshold: Schwelle fuer Model Law A
        """
        self.numbers_range = numbers_range
        self.numbers_to_draw = numbers_to_draw
        self.hot_threshold = hot_threshold
        self.cold_threshold = cold_threshold
        self.rolling_window = rolling_window
        self.stability_threshold = stability_threshold

        self._all_numbers = list(range(numbers_range[0], numbers_range[1] + 1))

    def extract(
        self,
        draws: list[DrawResult],
        hyp_results: Optional[dict[str, dict]] = None,
    ) -> dict[int, FeatureVector]:
        """Extrahiert alle Features fuer alle Zahlen.

        Args:
            draws: Liste von DrawResult-Objekten
            hyp_results: Optional vorberechnete Hypothesen-Ergebnisse

        Returns:
            Dict mit Zahl als Key und FeatureVector als Value
        """
        if not draws:
            logger.warning("No draws provided, returning empty features")
            return {n: FeatureVector(number=n) for n in self._all_numbers}

        logger.info(f"Extracting features from {len(draws)} draws")

        # Initialize feature vectors
        vectors: dict[int, FeatureVector] = {
            n: FeatureVector(number=n) for n in self._all_numbers
        }

        # Extract all feature categories
        self._extract_frequency_features(draws, vectors)
        self._extract_pattern_features(draws, vectors)
        self._extract_temporal_features(draws, vectors)
        self._extract_popularity_features(vectors, hyp_results)
        self._extract_stake_features(vectors, hyp_results)
        self._extract_recurrence_features(draws, vectors)
        self._extract_stability_features(draws, vectors)
        self._extract_cluster_features(draws, vectors)

        # Calculate combined scores and tiers
        self._calculate_combined_scores(vectors)

        logger.info(f"Extracted {len(vectors[1].features)} features per number")
        return vectors

    def _extract_frequency_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Frequency-Features."""
        # Count occurrences
        counts: dict[int, int] = {n: 0 for n in self._all_numbers}
        for draw in draws:
            for num in draw.numbers:
                if num in counts:
                    counts[num] += 1

        total_draws = len(draws)
        if total_draws == 0:
            return

        # Raw frequency
        for num in self._all_numbers:
            freq_raw = counts[num] / total_draws
            vectors[num].features["freq_raw"] = freq_raw

            # Hot/Cold classification
            if freq_raw >= self.hot_threshold:
                vectors[num].features["freq_hot"] = 1.0
                vectors[num].features["freq_cold"] = 0.0
            elif freq_raw <= self.cold_threshold:
                vectors[num].features["freq_hot"] = 0.0
                vectors[num].features["freq_cold"] = 1.0
            else:
                # Proportional score
                range_size = self.hot_threshold - self.cold_threshold
                if range_size > 0:
                    hot_score = (freq_raw - self.cold_threshold) / range_size
                else:
                    hot_score = 0.5
                vectors[num].features["freq_hot"] = hot_score
                vectors[num].features["freq_cold"] = 1.0 - hot_score

        # Rolling frequency (last N draws)
        recent_draws = draws[-self.rolling_window :]
        recent_counts: dict[int, int] = {n: 0 for n in self._all_numbers}
        for draw in recent_draws:
            for num in draw.numbers:
                if num in recent_counts:
                    recent_counts[num] += 1

        for num in self._all_numbers:
            freq_rolling = recent_counts[num] / max(len(recent_draws), 1)
            vectors[num].features["freq_rolling"] = freq_rolling

    def _extract_pattern_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Pattern-Features (Duo/Trio/Quatro)."""
        from collections import Counter
        from itertools import combinations

        # Count pair occurrences
        pair_counts: Counter = Counter()
        trio_counts: Counter = Counter()
        quatro_counts: Counter = Counter()

        for draw in draws:
            nums = sorted(draw.numbers)
            # Pairs (duos)
            for pair in combinations(nums, 2):
                pair_counts[pair] += 1
            # Trios
            for trio in combinations(nums, 3):
                trio_counts[trio] += 1
            # Quatros (sample to avoid explosion)
            if len(nums) >= 4:
                for quatro in combinations(nums[:10], 4):  # Limit to first 10
                    quatro_counts[quatro] += 1

        # Calculate per-number scores
        duo_scores: dict[int, float] = {n: 0.0 for n in self._all_numbers}
        trio_scores: dict[int, float] = {n: 0.0 for n in self._all_numbers}
        quatro_scores: dict[int, float] = {n: 0.0 for n in self._all_numbers}

        # Sum pattern involvement
        for pair, count in pair_counts.items():
            for num in pair:
                if num in duo_scores:
                    duo_scores[num] += count

        for trio, count in trio_counts.items():
            for num in trio:
                if num in trio_scores:
                    trio_scores[num] += count

        for quatro, count in quatro_counts.items():
            for num in quatro:
                if num in quatro_scores:
                    quatro_scores[num] += count

        # Normalize to 0-1
        max_duo = max(duo_scores.values()) or 1
        max_trio = max(trio_scores.values()) or 1
        max_quatro = max(quatro_scores.values()) or 1

        for num in self._all_numbers:
            vectors[num].features["duo_score"] = duo_scores[num] / max_duo
            vectors[num].features["trio_score"] = trio_scores[num] / max_trio
            vectors[num].features["quatro_score"] = quatro_scores[num] / max_quatro

    def _extract_temporal_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Temporal-Features."""
        from datetime import date

        # German holidays (simplified)
        holidays = {
            (1, 1),   # Neujahr
            (5, 1),   # Tag der Arbeit
            (10, 3),  # Tag der Deutschen Einheit
            (12, 25), # 1. Weihnachtstag
            (12, 26), # 2. Weihnachtstag
        }

        # Count by weekday and month
        weekday_counts: dict[int, dict[int, int]] = {
            n: {i: 0 for i in range(7)} for n in self._all_numbers
        }
        month_counts: dict[int, dict[int, int]] = {
            n: {i: 0 for i in range(1, 13)} for n in self._all_numbers
        }
        holiday_counts: dict[int, int] = {n: 0 for n in self._all_numbers}

        total_weekday: dict[int, int] = {i: 0 for i in range(7)}
        total_month: dict[int, int] = {i: 0 for i in range(1, 13)}
        total_holiday = 0

        for draw in draws:
            weekday = draw.date.weekday()
            month = draw.date.month
            is_holiday = (draw.date.month, draw.date.day) in holidays

            total_weekday[weekday] += 1
            total_month[month] += 1
            if is_holiday:
                total_holiday += 1

            for num in draw.numbers:
                if num in self._all_numbers:
                    weekday_counts[num][weekday] += 1
                    month_counts[num][month] += 1
                    if is_holiday:
                        holiday_counts[num] += 1

        # Calculate bias (chi-square-like deviation from expected)
        expected_per_draw = self.numbers_to_draw / len(self._all_numbers)

        for num in self._all_numbers:
            # Weekday bias: variance from uniform distribution
            weekday_devs = []
            for wd in range(7):
                expected = total_weekday[wd] * expected_per_draw
                actual = weekday_counts[num][wd]
                if expected > 0:
                    weekday_devs.append(abs(actual - expected) / expected)
            vectors[num].features["weekday_bias"] = (
                np.mean(weekday_devs) if weekday_devs else 0.0
            )

            # Month bias
            month_devs = []
            for m in range(1, 13):
                expected = total_month[m] * expected_per_draw
                actual = month_counts[num][m]
                if expected > 0:
                    month_devs.append(abs(actual - expected) / expected)
            vectors[num].features["month_bias"] = (
                np.mean(month_devs) if month_devs else 0.0
            )

            # Holiday proximity
            if total_holiday > 0:
                expected_holiday = total_holiday * expected_per_draw
                actual_holiday = holiday_counts[num]
                vectors[num].features["holiday_proximity"] = (
                    actual_holiday / max(expected_holiday, 1)
                )
            else:
                vectors[num].features["holiday_proximity"] = 0.5

    def _extract_popularity_features(
        self,
        vectors: dict[int, FeatureVector],
        hyp_results: Optional[dict[str, dict]] = None,
    ) -> None:
        """Extrahiert Popularity-Features."""
        # Birthday numbers (1-31)
        for num in self._all_numbers:
            vectors[num].features["is_birthday"] = 1.0 if num in self.BIRTHDAY_NUMBERS else 0.0

        # "Schoene" Zahlen
        for num in self._all_numbers:
            vectors[num].features["is_schoene"] = 1.0 if num in self.SCHOENE_ZAHLEN else 0.0

        # Safe numbers from HYP-010 results
        safe_numbers: set[int] = set()
        if hyp_results and "HYP-010" in hyp_results:
            classification = hyp_results["HYP-010"].get("classification", {})
            safe_numbers = set(classification.get("safe_numbers", []))

        for num in self._all_numbers:
            vectors[num].features["is_safe"] = 1.0 if num in safe_numbers else 0.0

    def _extract_stake_features(
        self,
        vectors: dict[int, FeatureVector],
        hyp_results: Optional[dict[str, dict]] = None,
    ) -> None:
        """Extrahiert Stake-Features."""
        low_stake: set[int] = set()
        high_stake: set[int] = set()

        if hyp_results and "HYP-012" in hyp_results:
            classification = hyp_results["HYP-012"].get("classification", {})
            low_stake = set(classification.get("low_stake_numbers", []))
            high_stake = set(classification.get("high_stake_numbers", []))

        for num in self._all_numbers:
            # Inverted einsatz score (low stake = high score)
            if num in low_stake:
                vectors[num].features["einsatz_score"] = 0.8
            elif num in high_stake:
                vectors[num].features["einsatz_score"] = 0.2
            else:
                vectors[num].features["einsatz_score"] = 0.5

            # Auszahlung score (same as einsatz for now)
            if num in low_stake:
                vectors[num].features["auszahlung_score"] = 0.75
            elif num in high_stake:
                vectors[num].features["auszahlung_score"] = 0.25
            else:
                vectors[num].features["auszahlung_score"] = 0.5

    def _extract_recurrence_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Recurrence-Features."""
        # Calculate streaks and gaps
        last_seen: dict[int, int] = {n: -1 for n in self._all_numbers}
        current_streak: dict[int, int] = {n: 0 for n in self._all_numbers}
        max_streak: dict[int, int] = {n: 0 for n in self._all_numbers}
        gaps: dict[int, list[int]] = {n: [] for n in self._all_numbers}

        for idx, draw in enumerate(draws):
            drawn_set = set(draw.numbers)
            for num in self._all_numbers:
                if num in drawn_set:
                    if last_seen[num] >= 0:
                        gaps[num].append(idx - last_seen[num])
                    current_streak[num] += 1
                    max_streak[num] = max(max_streak[num], current_streak[num])
                    last_seen[num] = idx
                else:
                    current_streak[num] = 0

        # Normalize streaks
        max_any_streak = max(max_streak.values()) or 1
        for num in self._all_numbers:
            vectors[num].features["streak_length"] = current_streak[num] / max_any_streak

            # Stability: inverse coefficient of variation of gaps
            if len(gaps[num]) >= 2:
                gap_std = np.std(gaps[num])
                gap_mean = np.mean(gaps[num])
                if gap_mean > 0:
                    cv = gap_std / gap_mean
                    # Lower CV = more stable
                    vectors[num].features["stability_score"] = 1.0 / (1.0 + cv)
                else:
                    vectors[num].features["stability_score"] = 0.5
            else:
                vectors[num].features["stability_score"] = 0.5

    def _extract_stability_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Model Law A Stability-Features."""
        # Calculate rolling frequencies over multiple windows
        windows = [10, 20, 50, 100]
        window_freqs: dict[int, list[float]] = {n: [] for n in self._all_numbers}

        for window in windows:
            if len(draws) < window:
                continue

            # Multiple samples
            for start in range(0, len(draws) - window, window // 2):
                window_draws = draws[start : start + window]
                counts: dict[int, int] = {n: 0 for n in self._all_numbers}
                for draw in window_draws:
                    for num in draw.numbers:
                        if num in counts:
                            counts[num] += 1

                for num in self._all_numbers:
                    freq = counts[num] / window
                    window_freqs[num].append(freq)

        # Model Law A: stability = 1 - std/mean
        for num in self._all_numbers:
            if len(window_freqs[num]) >= 3:
                mean_freq = np.mean(window_freqs[num])
                std_freq = np.std(window_freqs[num])
                if mean_freq > 0:
                    stability = 1.0 - (std_freq / mean_freq)
                    vectors[num].features["law_a_score"] = max(0.0, min(1.0, stability))
                else:
                    vectors[num].features["law_a_score"] = 0.5
            else:
                vectors[num].features["law_a_score"] = 0.5

    def _extract_cluster_features(
        self, draws: list[DrawResult], vectors: dict[int, FeatureVector]
    ) -> None:
        """Extrahiert Cluster-Features."""
        # Simplified cluster reset detection
        # Look for numbers that appear in clusters then disappear

        window = 10
        if len(draws) < window * 2:
            for num in self._all_numbers:
                vectors[num].features["reset_probability"] = 0.5
                vectors[num].features["cluster_signal"] = 0.0
            return

        # Recent vs previous window
        recent = draws[-window:]
        previous = draws[-window * 2 : -window]

        recent_counts: dict[int, int] = {n: 0 for n in self._all_numbers}
        previous_counts: dict[int, int] = {n: 0 for n in self._all_numbers}

        for draw in recent:
            for num in draw.numbers:
                if num in recent_counts:
                    recent_counts[num] += 1

        for draw in previous:
            for num in draw.numbers:
                if num in previous_counts:
                    previous_counts[num] += 1

        for num in self._all_numbers:
            prev = previous_counts[num]
            curr = recent_counts[num]

            # Reset probability: high if number was frequent then dropped
            if prev > 0:
                change = (curr - prev) / prev
                if change < -0.5:  # Dropped by more than 50%
                    vectors[num].features["reset_probability"] = min(1.0, abs(change))
                else:
                    vectors[num].features["reset_probability"] = 0.0
            else:
                vectors[num].features["reset_probability"] = 0.0

            # Cluster signal: 1=rising, -1=falling, 0=stable
            if prev == 0 and curr > 0:
                vectors[num].features["cluster_signal"] = 1.0  # BUY
            elif prev > 0 and curr == 0:
                vectors[num].features["cluster_signal"] = -1.0  # SELL
            elif prev > 0 and curr > prev:
                vectors[num].features["cluster_signal"] = 0.5  # Mild BUY
            elif prev > 0 and curr < prev:
                vectors[num].features["cluster_signal"] = -0.5  # Mild SELL
            else:
                vectors[num].features["cluster_signal"] = 0.0  # HOLD

    def _calculate_combined_scores(
        self, vectors: dict[int, FeatureVector]
    ) -> None:
        """Berechnet Combined Scores und Tiers."""
        from kenobase.features.registry import FeatureRegistry

        registry = FeatureRegistry()

        for num in self._all_numbers:
            vec = vectors[num]
            total_weighted = 0.0
            total_weight = 0.0

            for feature_name, value in vec.features.items():
                definition = registry.get(feature_name)
                weight = definition.weight if definition else 1.0

                # Normalize non-normalized features
                if definition and not definition.normalize:
                    # Binary features - use as-is
                    pass

                total_weighted += value * weight
                total_weight += weight

            if total_weight > 0:
                vec.combined_score = total_weighted / total_weight
            else:
                vec.combined_score = 0.5

            # Tier classification
            if vec.combined_score >= 0.7:
                vec.tier = "A"
            elif vec.combined_score >= 0.5:
                vec.tier = "B"
            else:
                vec.tier = "C"


__all__ = [
    "FeatureCategory",
    "FeatureExtractor",
    "FeatureVector",
]
