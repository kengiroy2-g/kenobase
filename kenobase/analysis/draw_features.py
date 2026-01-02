"""Draw Feature Extraction for Kenobase V2.0 (FEAT-001).

This module provides a unified interface for extracting abstract features
from lottery draws. Instead of analyzing individual numbers (pattern-first),
we extract features like sum, decade distribution, entropy, and uniqueness
which can then be analyzed at a higher level (axiom-first).

Features:
- sum: Sum of all drawn numbers (int)
- decade_counts: Distribution across 7 decades [1-10, 11-20, ..., 61-70]
- entropy: Shannon entropy of decade distribution (float, in bits)
- uniqueness: Ratio of "rare" numbers in draw (float, 0-1)

Usage:
    from kenobase.analysis.draw_features import (
        DrawFeatures,
        DrawFeatureExtractor,
        extract_draw_features,
    )

    extractor = DrawFeatureExtractor()
    features = extractor.extract(draw)  # Single draw
    features_list = extractor.extract_batch(draws)  # Multiple draws

Author: EXECUTOR (TASK FEAT-001)
Date: 2025-12-30
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Sequence

import numpy as np

from kenobase.analysis.decade_affinity import NUM_DECADES, get_decade

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class DrawFeatures:
    """Feature vector for a single draw.

    All features are numeric and can be compared against null models
    for statistical significance testing.

    Attributes:
        draw_sum: Sum of all drawn numbers (e.g., ~710 for KENO with 20 from 1-70)
        decade_counts: List of 7 counts, one per decade [1-10, 11-20, ..., 61-70]
        entropy: Shannon entropy of decade distribution (in bits, range 0 to log2(7))
        uniqueness: Ratio of numbers below median frequency (0-1)
        date: Optional date of the draw
    """

    draw_sum: int
    decade_counts: tuple[int, ...]
    entropy: float
    uniqueness: float
    date: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate feature values."""
        if len(self.decade_counts) != NUM_DECADES:
            raise ValueError(
                f"decade_counts must have {NUM_DECADES} elements, "
                f"got {len(self.decade_counts)}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "draw_sum": self.draw_sum,
            "decade_counts": list(self.decade_counts),
            "entropy": self.entropy,
            "uniqueness": self.uniqueness,
            "date": self.date.isoformat() if self.date else None,
        }

    def to_vector(self) -> np.ndarray:
        """Convert to numpy vector for numerical analysis.

        Returns:
            Array of shape (10,): [sum, d0, d1, d2, d3, d4, d5, d6, entropy, uniqueness]
        """
        return np.array(
            [self.draw_sum]
            + list(self.decade_counts)
            + [self.entropy, self.uniqueness]
        )


@dataclass
class FeatureStatistics:
    """Aggregate statistics for a collection of DrawFeatures.

    Attributes:
        n_draws: Number of draws analyzed
        sum_mean: Mean of draw sums
        sum_std: Standard deviation of draw sums
        entropy_mean: Mean entropy
        entropy_std: Std of entropy
        uniqueness_mean: Mean uniqueness
        uniqueness_std: Std of uniqueness
        decade_means: Mean counts per decade
        decade_stds: Std of counts per decade
    """

    n_draws: int
    sum_mean: float
    sum_std: float
    entropy_mean: float
    entropy_std: float
    uniqueness_mean: float
    uniqueness_std: float
    decade_means: tuple[float, ...]
    decade_stds: tuple[float, ...]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "n_draws": self.n_draws,
            "sum_mean": self.sum_mean,
            "sum_std": self.sum_std,
            "entropy_mean": self.entropy_mean,
            "entropy_std": self.entropy_std,
            "uniqueness_mean": self.uniqueness_mean,
            "uniqueness_std": self.uniqueness_std,
            "decade_means": list(self.decade_means),
            "decade_stds": list(self.decade_stds),
        }


class DrawFeatureExtractor:
    """Unified feature extractor for lottery draws.

    Extracts abstract features (sum, decade distribution, entropy, uniqueness)
    from DrawResult objects for axiom-first analysis.

    The uniqueness score requires historical frequency data. If not provided,
    a heuristic based on number value is used (higher numbers = less popular).

    Example:
        extractor = DrawFeatureExtractor()
        features = extractor.extract(draw)
        features_list = extractor.extract_batch(draws)
        stats = extractor.compute_statistics(features_list)
    """

    def __init__(
        self,
        number_frequencies: Optional[dict[int, float]] = None,
        uniqueness_percentile: float = 25.0,
    ) -> None:
        """Initialize the feature extractor.

        Args:
            number_frequencies: Optional dict mapping number -> historical frequency.
                If provided, uniqueness is calculated based on this.
            uniqueness_percentile: Percentile threshold for "rare" numbers.
                Numbers with frequency below this percentile are considered unique.
                Default: 25.0 (bottom quartile)
        """
        self._number_frequencies = number_frequencies
        self._uniqueness_percentile = uniqueness_percentile
        self._frequency_threshold: Optional[float] = None

        if number_frequencies:
            freqs = list(number_frequencies.values())
            self._frequency_threshold = float(
                np.percentile(freqs, uniqueness_percentile)
            )

    def extract(self, draw: DrawResult) -> DrawFeatures:
        """Extract features from a single draw.

        Args:
            draw: DrawResult object with numbers and optional date

        Returns:
            DrawFeatures containing all extracted features
        """
        numbers = draw.numbers
        draw_date = draw.date if hasattr(draw, "date") else None

        # Feature 1: Sum
        draw_sum = sum(numbers)

        # Feature 2: Decade counts
        decade_counts = self._calculate_decade_counts(numbers)

        # Feature 3: Entropy (Shannon, in bits)
        entropy = self._calculate_entropy(decade_counts)

        # Feature 4: Uniqueness
        uniqueness = self._calculate_uniqueness(numbers)

        return DrawFeatures(
            draw_sum=draw_sum,
            decade_counts=tuple(decade_counts),
            entropy=entropy,
            uniqueness=uniqueness,
            date=draw_date,
        )

    def extract_batch(self, draws: Sequence[DrawResult]) -> list[DrawFeatures]:
        """Extract features from multiple draws.

        Args:
            draws: Sequence of DrawResult objects

        Returns:
            List of DrawFeatures, one per draw
        """
        return [self.extract(draw) for draw in draws]

    def compute_statistics(
        self, features: Sequence[DrawFeatures]
    ) -> FeatureStatistics:
        """Compute aggregate statistics over a collection of features.

        Args:
            features: Sequence of DrawFeatures

        Returns:
            FeatureStatistics with means and standard deviations
        """
        if not features:
            return FeatureStatistics(
                n_draws=0,
                sum_mean=0.0,
                sum_std=0.0,
                entropy_mean=0.0,
                entropy_std=0.0,
                uniqueness_mean=0.0,
                uniqueness_std=0.0,
                decade_means=tuple([0.0] * NUM_DECADES),
                decade_stds=tuple([0.0] * NUM_DECADES),
            )

        sums = np.array([f.draw_sum for f in features])
        entropies = np.array([f.entropy for f in features])
        uniquenesses = np.array([f.uniqueness for f in features])
        decades = np.array([list(f.decade_counts) for f in features])

        return FeatureStatistics(
            n_draws=len(features),
            sum_mean=float(np.mean(sums)),
            sum_std=float(np.std(sums)),
            entropy_mean=float(np.mean(entropies)),
            entropy_std=float(np.std(entropies)),
            uniqueness_mean=float(np.mean(uniquenesses)),
            uniqueness_std=float(np.std(uniquenesses)),
            decade_means=tuple(float(m) for m in np.mean(decades, axis=0)),
            decade_stds=tuple(float(s) for s in np.std(decades, axis=0)),
        )

    def _calculate_decade_counts(self, numbers: Sequence[int]) -> list[int]:
        """Count numbers in each decade.

        Args:
            numbers: List of drawn numbers (1-70 for KENO)

        Returns:
            List of 7 counts, one per decade
        """
        counts = [0] * NUM_DECADES
        for num in numbers:
            if 1 <= num <= 70:
                decade = get_decade(num)
                counts[decade] += 1
        return counts

    def _calculate_entropy(self, decade_counts: Sequence[int]) -> float:
        """Calculate Shannon entropy of decade distribution.

        Uses log2 for entropy in bits. Maximum entropy for 7 decades is log2(7) ~= 2.807.

        Args:
            decade_counts: List of counts per decade

        Returns:
            Entropy in bits (0 to log2(7))
        """
        total = sum(decade_counts)
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in decade_counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return entropy

    def _calculate_uniqueness(self, numbers: Sequence[int]) -> float:
        """Calculate uniqueness score based on number rarity.

        If historical frequencies are provided, uniqueness is the ratio of
        numbers below the frequency threshold (e.g., bottom 25%).

        If no frequencies are provided, a heuristic is used:
        - Higher numbers (41-70) are considered "less popular" due to
          birthday bias avoiding them.
        - Numbers 1-31 are considered "popular" (birthdays).

        Args:
            numbers: List of drawn numbers

        Returns:
            Uniqueness score (0-1), higher = more unique numbers
        """
        if not numbers:
            return 0.0

        if self._number_frequencies and self._frequency_threshold is not None:
            # Use actual frequency data
            rare_count = sum(
                1
                for num in numbers
                if self._number_frequencies.get(num, 0) < self._frequency_threshold
            )
            return rare_count / len(numbers)
        else:
            # Heuristic: numbers > 31 are "unique" (not birthdays)
            # This is a simplified model based on known birthday bias
            unique_count = sum(1 for num in numbers if num > 31)
            return unique_count / len(numbers)


def extract_draw_features(
    draw: DrawResult,
    number_frequencies: Optional[dict[int, float]] = None,
) -> DrawFeatures:
    """Convenience function to extract features from a single draw.

    Args:
        draw: DrawResult object
        number_frequencies: Optional historical frequency data

    Returns:
        DrawFeatures for the draw
    """
    extractor = DrawFeatureExtractor(number_frequencies=number_frequencies)
    return extractor.extract(draw)


def compute_feature_matrix(
    draws: Sequence[DrawResult],
    number_frequencies: Optional[dict[int, float]] = None,
) -> np.ndarray:
    """Extract features from draws and return as matrix.

    Args:
        draws: Sequence of DrawResult objects
        number_frequencies: Optional historical frequency data

    Returns:
        Matrix of shape (n_draws, 10) where columns are:
        [sum, d0, d1, d2, d3, d4, d5, d6, entropy, uniqueness]
    """
    extractor = DrawFeatureExtractor(number_frequencies=number_frequencies)
    features = extractor.extract_batch(draws)
    return np.array([f.to_vector() for f in features])


__all__ = [
    "DrawFeatures",
    "FeatureStatistics",
    "DrawFeatureExtractor",
    "extract_draw_features",
    "compute_feature_matrix",
]
