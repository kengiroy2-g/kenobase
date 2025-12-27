"""Unit tests for kenobase.pipeline.validation_metrics module.

Tests Precision, Recall, F1-Score calculation for validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.pipeline.validation_metrics import (
    ValidationMetrics,
    calculate_f1,
    calculate_hits,
    calculate_metrics,
    calculate_metrics_dict,
    calculate_precision,
    calculate_recall,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_draws() -> list[DrawResult]:
    """Sample draws for testing."""
    return [
        DrawResult(date=datetime(2024, 1, 1), numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 2), numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11], game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 3), numbers=[5, 6, 7, 8, 9, 10, 11, 12, 13, 14], game_type=GameType.KENO),
    ]


@pytest.fixture
def keno_draws() -> list[DrawResult]:
    """KENO-style draws (20 numbers per draw)."""
    return [
        DrawResult(date=datetime(2024, 1, 1), numbers=list(range(1, 21)), game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 2), numbers=list(range(5, 25)), game_type=GameType.KENO),
        DrawResult(date=datetime(2024, 1, 3), numbers=list(range(10, 30)), game_type=GameType.KENO),
    ]


# =============================================================================
# Test calculate_hits
# =============================================================================


class TestCalculateHits:
    """Tests for calculate_hits function."""

    def test_all_hits(self, sample_draws: list[DrawResult]) -> None:
        """Test when all predicted numbers appear in all draws."""
        predicted = [5, 6, 7]  # Diese Zahlen sind in allen draws
        hits = calculate_hits(predicted, sample_draws)
        assert hits == 9  # 3 Zahlen * 3 Draws

    def test_partial_hits(self, sample_draws: list[DrawResult]) -> None:
        """Test when some predicted numbers appear."""
        predicted = [1, 2, 15]  # 1,2 nur in draw 1; 2 in draw 2; 15 nirgends
        hits = calculate_hits(predicted, sample_draws)
        assert hits == 3  # draw1: 1,2 (2), draw2: 2 (1), draw3: 0

    def test_no_hits(self, sample_draws: list[DrawResult]) -> None:
        """Test when no predicted numbers appear."""
        predicted = [99, 100]
        hits = calculate_hits(predicted, sample_draws)
        assert hits == 0

    def test_empty_predicted(self, sample_draws: list[DrawResult]) -> None:
        """Test with empty prediction list."""
        hits = calculate_hits([], sample_draws)
        assert hits == 0

    def test_empty_draws(self) -> None:
        """Test with empty draws list."""
        hits = calculate_hits([1, 2, 3], [])
        assert hits == 0


# =============================================================================
# Test calculate_precision
# =============================================================================


class TestCalculatePrecision:
    """Tests for calculate_precision function."""

    def test_perfect_precision(self) -> None:
        """Test 100% precision."""
        precision = calculate_precision(hits=10, total_predictions=10)
        assert precision == 1.0

    def test_half_precision(self) -> None:
        """Test 50% precision."""
        precision = calculate_precision(hits=5, total_predictions=10)
        assert precision == 0.5

    def test_zero_precision(self) -> None:
        """Test 0% precision."""
        precision = calculate_precision(hits=0, total_predictions=10)
        assert precision == 0.0

    def test_division_by_zero(self) -> None:
        """Test handling of zero total_predictions."""
        precision = calculate_precision(hits=0, total_predictions=0)
        assert precision == 0.0


# =============================================================================
# Test calculate_recall
# =============================================================================


class TestCalculateRecall:
    """Tests for calculate_recall function."""

    def test_perfect_recall(self) -> None:
        """Test 100% recall."""
        recall = calculate_recall(hits=20, total_actual=20)
        assert recall == 1.0

    def test_partial_recall(self) -> None:
        """Test partial recall."""
        recall = calculate_recall(hits=10, total_actual=20)
        assert recall == 0.5

    def test_zero_recall(self) -> None:
        """Test 0% recall."""
        recall = calculate_recall(hits=0, total_actual=20)
        assert recall == 0.0

    def test_division_by_zero(self) -> None:
        """Test handling of zero total_actual."""
        recall = calculate_recall(hits=0, total_actual=0)
        assert recall == 0.0


# =============================================================================
# Test calculate_f1
# =============================================================================


class TestCalculateF1:
    """Tests for calculate_f1 function."""

    def test_perfect_f1(self) -> None:
        """Test perfect F1 score."""
        f1 = calculate_f1(precision=1.0, recall=1.0)
        assert f1 == 1.0

    def test_balanced_f1(self) -> None:
        """Test balanced F1 with equal P and R."""
        f1 = calculate_f1(precision=0.5, recall=0.5)
        assert f1 == 0.5

    def test_unbalanced_f1(self) -> None:
        """Test F1 with different P and R."""
        f1 = calculate_f1(precision=0.8, recall=0.4)
        expected = 2 * 0.8 * 0.4 / (0.8 + 0.4)
        assert abs(f1 - expected) < 1e-10

    def test_zero_precision(self) -> None:
        """Test F1 when precision is zero."""
        f1 = calculate_f1(precision=0.0, recall=0.5)
        assert f1 == 0.0

    def test_zero_recall(self) -> None:
        """Test F1 when recall is zero."""
        f1 = calculate_f1(precision=0.5, recall=0.0)
        assert f1 == 0.0

    def test_both_zero(self) -> None:
        """Test F1 when both are zero."""
        f1 = calculate_f1(precision=0.0, recall=0.0)
        assert f1 == 0.0


# =============================================================================
# Test calculate_metrics
# =============================================================================


class TestCalculateMetrics:
    """Tests for calculate_metrics function."""

    def test_returns_validation_metrics(self, sample_draws: list[DrawResult]) -> None:
        """Test that calculate_metrics returns ValidationMetrics."""
        result = calculate_metrics([5, 6, 7], sample_draws, numbers_per_draw=10)
        assert isinstance(result, ValidationMetrics)

    def test_correct_hits(self, sample_draws: list[DrawResult]) -> None:
        """Test correct hits calculation."""
        result = calculate_metrics([5, 6, 7], sample_draws, numbers_per_draw=10)
        assert result.hits == 9

    def test_correct_total_predictions(self, sample_draws: list[DrawResult]) -> None:
        """Test correct total_predictions calculation."""
        predicted = [5, 6, 7]  # 3 Zahlen
        result = calculate_metrics(predicted, sample_draws, numbers_per_draw=10)
        assert result.total_predictions == 9  # 3 * 3

    def test_correct_total_actual(self, sample_draws: list[DrawResult]) -> None:
        """Test correct total_actual calculation."""
        result = calculate_metrics([5, 6, 7], sample_draws, numbers_per_draw=10)
        assert result.total_actual == 30  # 10 * 3

    def test_correct_precision(self, sample_draws: list[DrawResult]) -> None:
        """Test correct precision calculation."""
        result = calculate_metrics([5, 6, 7], sample_draws, numbers_per_draw=10)
        expected_precision = 9 / 9  # 100% - alle Vorhersagen treffen
        assert result.precision == expected_precision

    def test_correct_recall(self, sample_draws: list[DrawResult]) -> None:
        """Test correct recall calculation."""
        result = calculate_metrics([5, 6, 7], sample_draws, numbers_per_draw=10)
        expected_recall = 9 / 30  # 30% der tatsaechlichen Zahlen
        assert result.recall == expected_recall

    def test_keno_style(self, keno_draws: list[DrawResult]) -> None:
        """Test with KENO-style 20 numbers per draw."""
        predicted = list(range(1, 11))  # 10 Zahlen
        result = calculate_metrics(predicted, keno_draws, numbers_per_draw=20)
        # hits: draw1 hat 1-20, also 10 hits
        # draw2 hat 5-24, also 6 hits (5-10)
        # draw3 hat 10-29, also 1 hit (10)
        expected_hits = 10 + 6 + 1
        assert result.hits == expected_hits
        assert result.total_predictions == 30  # 10 * 3
        assert result.total_actual == 60  # 20 * 3

    def test_empty_predicted(self, sample_draws: list[DrawResult]) -> None:
        """Test with empty predictions."""
        result = calculate_metrics([], sample_draws, numbers_per_draw=10)
        assert result.hits == 0
        assert result.precision == 0.0
        assert result.recall == 0.0
        assert result.f1_score == 0.0

    def test_empty_draws(self) -> None:
        """Test with empty draws."""
        result = calculate_metrics([1, 2, 3], [], numbers_per_draw=10)
        assert result.hits == 0
        assert result.total_predictions == 0
        assert result.total_actual == 0


# =============================================================================
# Test calculate_metrics_dict
# =============================================================================


class TestCalculateMetricsDict:
    """Tests for calculate_metrics_dict function (compatibility wrapper)."""

    def test_returns_dict(self, sample_draws: list[DrawResult]) -> None:
        """Test that calculate_metrics_dict returns dict."""
        result = calculate_metrics_dict([5, 6, 7], sample_draws)
        assert isinstance(result, dict)

    def test_dict_keys(self, sample_draws: list[DrawResult]) -> None:
        """Test that dict has expected keys."""
        result = calculate_metrics_dict([5, 6, 7], sample_draws)
        expected_keys = {"hits", "total_predictions", "precision", "recall", "f1_score"}
        assert set(result.keys()) == expected_keys

    def test_same_values_as_metrics(self, sample_draws: list[DrawResult]) -> None:
        """Test that dict values match ValidationMetrics."""
        predicted = [5, 6, 7]
        metrics = calculate_metrics(predicted, sample_draws, numbers_per_draw=20)
        result = calculate_metrics_dict(predicted, sample_draws, numbers_per_draw=20)
        assert result["hits"] == metrics.hits
        assert result["precision"] == metrics.precision
        assert result["recall"] == metrics.recall
        assert result["f1_score"] == metrics.f1_score


# =============================================================================
# Test ValidationMetrics
# =============================================================================


class TestValidationMetrics:
    """Tests for ValidationMetrics dataclass."""

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        metrics = ValidationMetrics(
            hits=10,
            total_predictions=20,
            total_actual=100,
            precision=0.5,
            recall=0.1,
            f1_score=0.167,
        )
        result = metrics.to_dict()
        assert result["hits"] == 10
        assert result["total_predictions"] == 20
        assert result["total_actual"] == 100
        assert result["precision"] == 0.5
        assert result["recall"] == 0.1
        assert result["f1_score"] == 0.167

    def test_dataclass_fields(self) -> None:
        """Test that all expected fields exist."""
        metrics = ValidationMetrics(
            hits=1,
            total_predictions=2,
            total_actual=3,
            precision=0.5,
            recall=0.33,
            f1_score=0.4,
        )
        assert hasattr(metrics, "hits")
        assert hasattr(metrics, "total_predictions")
        assert hasattr(metrics, "total_actual")
        assert hasattr(metrics, "precision")
        assert hasattr(metrics, "recall")
        assert hasattr(metrics, "f1_score")
