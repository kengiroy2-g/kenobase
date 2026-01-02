"""Regime/State Detection using change-point analysis and HMM.

This module implements a two-stage pipeline:
1) Change-point detection (ruptures) on economic proxies
2) HMM (hmmlearn) to decode regimes and map them to economic_state labels
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Optional, Sequence

import numpy as np

try:
    import ruptures as rpt
except ImportError:  # pragma: no cover - handled via fallback
    rpt = None

try:
    from hmmlearn.hmm import GaussianHMM
except ImportError:  # pragma: no cover - handled via fallback
    GaussianHMM = None

try:
    from sklearn.cluster import KMeans
except ImportError:  # pragma: no cover - handled via fallback
    KMeans = None

from kenobase.core.data_loader import DrawResult
from kenobase.core.economic_state import (
    classify_economic_state,
    compute_rolling_cv,
    parse_jackpot,
    parse_spieleinsatz,
)


@dataclass
class RegimeDetectionConfig:
    """Configuration for regime detection."""

    train_split_date: datetime = datetime(2024, 1, 1)
    cv_window: int = 30
    numbers_range: tuple[int, int] = (1, 70)
    change_point_model: str = "rbf"
    change_point_penalty: float = 5.0
    change_point_min_size: int = 10
    boundary_tolerance: int = 1
    n_states: int = 4
    covariance_type: str = "full"
    n_iter: int = 200
    random_state: Optional[int] = 42
    jackpot_high_threshold: float = 10_000_000.0
    cv_high_threshold: float = 0.5


@dataclass
class RegimeDetectionResult:
    """Result container for regime detection."""

    dates: list[datetime]
    latent_states: list[int]
    state_labels: list[str]
    baseline_labels: list[str]
    boundaries: list[int]
    accuracy: float
    boundary_f1: float
    log_likelihood: float
    train_size: int
    mapping: dict[int, str] = field(default_factory=dict)
    feature_stats: dict = field(default_factory=dict)


class _SimpleChangePoint:
    """Fallback change-point detector when ruptures is unavailable."""

    def __init__(self, min_size: int) -> None:
        self.min_size = min_size
        self._features: Optional[np.ndarray] = None

    def fit(self, features: np.ndarray) -> "_SimpleChangePoint":
        self._features = features
        return self

    def predict(self, penalty: float) -> list[int]:
        if self._features is None or len(self._features) == 0:
            return [0]

        diffs = np.linalg.norm(np.diff(self._features, axis=0), axis=1)
        threshold = np.mean(diffs) + penalty
        boundaries: list[int] = []
        for idx, diff in enumerate(diffs, start=1):
            if diff >= threshold and idx >= self.min_size and len(self._features) - idx >= self.min_size:
                boundaries.append(idx)

        if not boundaries:
            boundaries = [len(self._features)]
        else:
            boundaries.append(len(self._features))

        return boundaries


class _SimpleGaussianHMM:
    """Fallback HMM that clusters with KMeans when hmmlearn is unavailable."""

    def __init__(
        self,
        n_components: int,
        covariance_type: str = "full",
        n_iter: int = 200,
        random_state: Optional[int] = None,
    ) -> None:
        self.n_components = n_components
        self.random_state = random_state
        self.model: Optional[KMeans] = None

    def fit(self, features: np.ndarray, lengths: Optional[list[int]] = None) -> "_SimpleGaussianHMM":
        if KMeans is None:
            raise ImportError("sklearn is required for fallback HMM")
        self.model = KMeans(
            n_clusters=self.n_components,
            n_init="auto",
            random_state=self.random_state,
        )
        self.model.fit(features)
        return self

    def predict(self, features: np.ndarray) -> list[int]:
        if self.model is None:
            raise RuntimeError("Model is not fitted")
        return self.model.predict(features).tolist()

    def score(self, features: np.ndarray) -> float:
        if self.model is None:
            raise RuntimeError("Model is not fitted")
        labels = self.model.predict(features)
        centers = self.model.cluster_centers_
        distances = np.linalg.norm(features - centers[labels], axis=1)
        return -float(np.mean(distances))


def _compute_baseline_labels(
    spieleinsatz: Sequence[Optional[float]],
    jackpot: Sequence[Optional[float]],
    rolling_cv: Sequence[Optional[float]],
    train_mask: np.ndarray,
    config: RegimeDetectionConfig,
) -> tuple[list[str], Optional[float]]:
    """Compute baseline economic_state labels for mapping."""
    train_spieleinsatz = [
        v for v, is_train in zip(spieleinsatz, train_mask) if is_train and v is not None
    ]
    spieleinsatz_baseline = (
        float(np.median(train_spieleinsatz)) if train_spieleinsatz else None
    )

    labels: list[str] = []
    for se, jp, cv in zip(spieleinsatz, jackpot, rolling_cv):
        labels.append(
            classify_economic_state(
                spieleinsatz=se,
                jackpot=jp,
                rolling_cv=cv,
                spieleinsatz_baseline=spieleinsatz_baseline,
                jackpot_high_threshold=config.jackpot_high_threshold,
                cv_high_threshold=config.cv_high_threshold,
            )
        )
    return labels, spieleinsatz_baseline


def _impute_and_scale_features(
    feature_matrix: np.ndarray, train_mask: np.ndarray
) -> tuple[np.ndarray, dict]:
    """Impute missing values with train medians and standardize."""
    if feature_matrix.size == 0:
        return feature_matrix, {}

    if np.sum(train_mask) == 0:
        train_mask = np.ones(len(feature_matrix), dtype=bool)

    medians = np.nanmedian(feature_matrix[train_mask], axis=0)
    medians = np.where(np.isnan(medians), 0.0, medians)
    imputed = np.where(np.isnan(feature_matrix), medians, feature_matrix)

    train_imputed = imputed[train_mask]
    means = np.mean(train_imputed, axis=0)
    stds = np.std(train_imputed, axis=0)
    stds = np.where(stds == 0, 1.0, stds)

    scaled = (imputed - means) / stds

    stats = {
        "medians": medians.tolist(),
        "means": means.tolist(),
        "stds": stds.tolist(),
    }
    return scaled, stats


def _detect_change_points(
    train_features: np.ndarray, config: RegimeDetectionConfig
) -> tuple[list[int], list[int]]:
    """Detect change points on training data and return boundaries and segment lengths."""
    if len(train_features) < max(config.change_point_min_size * 2, 5):
        return [], []

    if rpt is not None:
        algo = rpt.Pelt(
            model=config.change_point_model,
            min_size=config.change_point_min_size,
            jump=1,
        )
    else:
        algo = _SimpleChangePoint(min_size=config.change_point_min_size)

    algo.fit(train_features)
    breakpoints = sorted(set(algo.predict(config.change_point_penalty)))
    if not breakpoints or breakpoints[-1] != len(train_features):
        breakpoints.append(len(train_features))

    boundaries = [bp for bp in breakpoints if bp < len(train_features)]
    segment_lengths = [breakpoints[0]] + [
        b - a for a, b in zip(breakpoints[:-1], breakpoints[1:])
    ]
    return boundaries, segment_lengths


def _map_states_to_labels(
    latent_states: Sequence[int],
    baseline_labels: Sequence[str],
    train_mask: np.ndarray,
    n_states: int,
) -> tuple[list[str], dict[int, str]]:
    """Map HMM latent states to economic_state labels via majority vote on train."""
    mapping: dict[int, str] = {}
    default_label = "NORMAL"
    train_labels = [lbl for lbl, is_train in zip(baseline_labels, train_mask) if is_train]
    if train_labels:
        default_label = Counter(train_labels).most_common(1)[0][0]

    for state in range(n_states):
        state_labels = [
            lbl
            for lbl, st, is_train in zip(baseline_labels, latent_states, train_mask)
            if st == state and is_train
        ]
        if state_labels:
            mapping[state] = Counter(state_labels).most_common(1)[0][0]

    mapped = [mapping.get(st, default_label) for st in latent_states]
    return mapped, mapping


def _boundary_f1(
    predicted_boundaries: Iterable[int],
    baseline_labels: Sequence[str],
    tolerance: int,
) -> float:
    """Compute boundary F1 vs. baseline label transitions."""
    true_boundaries = {
        idx for idx in range(1, len(baseline_labels)) if baseline_labels[idx] != baseline_labels[idx - 1]
    }
    predicted = {b for b in predicted_boundaries if b < len(baseline_labels)}

    if not predicted or not true_boundaries:
        return 0.0

    matched_true = set()
    matches = 0
    for pred in sorted(predicted):
        for true in sorted(true_boundaries):
            if true in matched_true:
                continue
            if abs(true - pred) <= tolerance:
                matched_true.add(true)
                matches += 1
                break

    precision = matches / len(predicted) if predicted else 0.0
    recall = matches / len(true_boundaries) if true_boundaries else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def detect_regimes(
    draws: list[DrawResult], config: Optional[RegimeDetectionConfig] = None
) -> RegimeDetectionResult:
    """Detect regimes for a sequence of draws.

    Args:
        draws: Draw results (will be sorted by date)
        config: Optional configuration

    Returns:
        RegimeDetectionResult with latent and mapped states, metrics, and boundaries
    """
    cfg = config or RegimeDetectionConfig()
    if not draws:
        return RegimeDetectionResult(
            dates=[],
            latent_states=[],
            state_labels=[],
            baseline_labels=[],
            boundaries=[],
            accuracy=0.0,
            boundary_f1=0.0,
            log_likelihood=0.0,
            train_size=0,
        )

    sorted_draws = sorted(draws, key=lambda d: d.date)
    dates = [d.date for d in sorted_draws]
    train_mask = np.array([d.date < cfg.train_split_date for d in sorted_draws])

    spieleinsatz = [parse_spieleinsatz(d.metadata) for d in sorted_draws]
    jackpot = [parse_jackpot(d.metadata) for d in sorted_draws]
    rolling_cv = compute_rolling_cv(
        sorted_draws, window=cfg.cv_window, numbers_range=cfg.numbers_range
    )

    feature_matrix = np.array(
        [
            [
                se if se is not None else np.nan,
                jp if jp is not None else np.nan,
                cv if cv is not None else np.nan,
            ]
            for se, jp, cv in zip(spieleinsatz, jackpot, rolling_cv)
        ]
    )

    scaled_features, feature_stats = _impute_and_scale_features(feature_matrix, train_mask)

    train_features = scaled_features[train_mask]
    boundaries, segment_lengths = _detect_change_points(train_features, cfg)

    if GaussianHMM is not None:
        model = GaussianHMM(
            n_components=cfg.n_states,
            covariance_type=cfg.covariance_type,
            n_iter=cfg.n_iter,
            random_state=cfg.random_state,
        )
    else:
        model = _SimpleGaussianHMM(
            n_components=cfg.n_states,
            covariance_type=cfg.covariance_type,
            n_iter=cfg.n_iter,
            random_state=cfg.random_state,
        )
    if len(train_features) == 0:
        train_features = scaled_features
        segment_lengths = [len(train_features)]
        train_mask = np.ones(len(train_features), dtype=bool)

    if not segment_lengths:
        segment_lengths = [len(train_features)]
    model.fit(train_features, lengths=segment_lengths)

    latent_states = np.asarray(model.predict(scaled_features)).tolist()

    baseline_labels, spieleinsatz_baseline = _compute_baseline_labels(
        spieleinsatz, jackpot, rolling_cv, train_mask, cfg
    )
    mapped_labels, mapping = _map_states_to_labels(
        latent_states, baseline_labels, train_mask, cfg.n_states
    )

    test_mask = ~train_mask
    test_labels = [lbl for lbl, is_test in zip(baseline_labels, test_mask) if is_test]
    test_pred_labels = [lbl for lbl, is_test in zip(mapped_labels, test_mask) if is_test]
    accuracy = 0.0
    if test_labels:
        accuracy = float(
            sum(1 for t, p in zip(test_labels, test_pred_labels) if t == p)
            / len(test_labels)
        )

    boundary_f1 = _boundary_f1(
        predicted_boundaries=boundaries,
        baseline_labels=[lbl for lbl, is_train in zip(baseline_labels, train_mask) if is_train],
        tolerance=cfg.boundary_tolerance,
    )

    test_features = scaled_features[test_mask]
    if len(test_features) > 0:
        log_likelihood = float(model.score(test_features))
    else:
        log_likelihood = float(model.score(train_features))

    feature_stats["spieleinsatz_baseline"] = spieleinsatz_baseline
    feature_stats["change_point_penalty"] = cfg.change_point_penalty
    feature_stats["segment_count"] = len(boundaries) + 1 if boundaries else 1

    return RegimeDetectionResult(
        dates=dates,
        latent_states=latent_states,
        state_labels=mapped_labels,
        baseline_labels=baseline_labels,
        boundaries=boundaries,
        accuracy=accuracy,
        boundary_f1=boundary_f1,
        log_likelihood=log_likelihood,
        train_size=int(np.sum(train_mask)),
        mapping=mapping,
        feature_stats=feature_stats,
    )


__all__ = [
    "RegimeDetectionConfig",
    "RegimeDetectionResult",
    "detect_regimes",
]
