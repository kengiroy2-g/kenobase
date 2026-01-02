"""Unit tests for draw_features module (FEAT-001).

Tests cover:
- DrawFeatures dataclass creation and validation
- DrawFeatureExtractor: single and batch extraction
- Feature calculations: sum, decade_counts, entropy, uniqueness
- Statistics computation
- Null model comparison readiness

Author: EXECUTOR (TASK FEAT-001)
Date: 2025-12-30
"""

from datetime import datetime
from unittest.mock import MagicMock

import numpy as np
import pytest

from kenobase.analysis.draw_features import (
    DrawFeatureExtractor,
    DrawFeatures,
    FeatureStatistics,
    compute_feature_matrix,
    extract_draw_features,
)


class TestDrawFeatures:
    """Test DrawFeatures dataclass."""

    def test_create_valid_features(self) -> None:
        """Test creating DrawFeatures with valid data."""
        features = DrawFeatures(
            draw_sum=710,
            decade_counts=(3, 3, 3, 3, 3, 3, 2),
            entropy=2.8,
            uniqueness=0.5,
            date=datetime(2025, 1, 1),
        )
        assert features.draw_sum == 710
        assert len(features.decade_counts) == 7
        assert features.entropy == 2.8
        assert features.uniqueness == 0.5
        assert features.date == datetime(2025, 1, 1)

    def test_invalid_decade_counts_length(self) -> None:
        """Test that invalid decade_counts length raises error."""
        with pytest.raises(ValueError, match="must have 7 elements"):
            DrawFeatures(
                draw_sum=710,
                decade_counts=(3, 3, 3),  # Only 3 elements
                entropy=2.8,
                uniqueness=0.5,
            )

    def test_to_dict(self) -> None:
        """Test to_dict serialization."""
        features = DrawFeatures(
            draw_sum=710,
            decade_counts=(3, 3, 3, 3, 3, 3, 2),
            entropy=2.807,
            uniqueness=0.55,
            date=datetime(2025, 1, 15),
        )
        d = features.to_dict()
        assert d["draw_sum"] == 710
        assert d["decade_counts"] == [3, 3, 3, 3, 3, 3, 2]
        assert d["entropy"] == 2.807
        assert d["uniqueness"] == 0.55
        assert "2025-01-15" in d["date"]

    def test_to_dict_without_date(self) -> None:
        """Test to_dict when date is None."""
        features = DrawFeatures(
            draw_sum=710,
            decade_counts=(3, 3, 3, 3, 3, 3, 2),
            entropy=2.8,
            uniqueness=0.5,
        )
        d = features.to_dict()
        assert d["date"] is None

    def test_to_vector(self) -> None:
        """Test to_vector creates correct numpy array."""
        features = DrawFeatures(
            draw_sum=700,
            decade_counts=(2, 3, 3, 3, 3, 3, 3),
            entropy=2.7,
            uniqueness=0.6,
        )
        vec = features.to_vector()
        assert vec.shape == (10,)
        assert vec[0] == 700  # sum
        assert list(vec[1:8]) == [2, 3, 3, 3, 3, 3, 3]  # decade counts
        assert vec[8] == pytest.approx(2.7)  # entropy
        assert vec[9] == pytest.approx(0.6)  # uniqueness


class TestDrawFeatureExtractor:
    """Test DrawFeatureExtractor class."""

    @pytest.fixture
    def mock_draw(self) -> MagicMock:
        """Create a mock DrawResult for testing."""
        draw = MagicMock()
        # 20 numbers distributed across decades
        # Decades: 0 (1-10), 1 (11-20), 2 (21-30), 3 (31-40), 4 (41-50), 5 (51-60), 6 (61-70)
        draw.numbers = [
            3, 7, 9,           # Decade 0: 3 numbers
            12, 15, 18,        # Decade 1: 3 numbers
            22, 25, 28,        # Decade 2: 3 numbers
            33, 36, 39,        # Decade 3: 3 numbers
            42, 45, 48,        # Decade 4: 3 numbers
            53, 56,            # Decade 5: 2 numbers
            62, 65, 68,        # Decade 6: 3 numbers
        ]  # Total: 20 numbers
        draw.date = datetime(2025, 1, 15)
        return draw

    @pytest.fixture
    def mock_draw_uniform(self) -> MagicMock:
        """Create a mock draw with nearly uniform decade distribution."""
        draw = MagicMock()
        # Roughly even distribution: ~2-3 per decade
        draw.numbers = [
            1, 5, 10,          # Decade 0: 3
            11, 15, 20,        # Decade 1: 3
            21, 25,            # Decade 2: 2
            31, 35, 40,        # Decade 3: 3
            41, 45, 50,        # Decade 4: 3
            51, 55, 60,        # Decade 5: 3
            61, 65, 70,        # Decade 6: 3
        ]  # Total: 20 numbers
        draw.date = datetime(2025, 1, 16)
        return draw

    @pytest.fixture
    def mock_draw_skewed(self) -> MagicMock:
        """Create a mock draw skewed toward lower numbers."""
        draw = MagicMock()
        # Heavy in decades 0-2 (birthday range)
        draw.numbers = [
            1, 2, 3, 4, 5, 6, 7, 8,     # Decade 0: 8
            11, 12, 13, 14, 15, 16,     # Decade 1: 6
            21, 22, 23, 24,             # Decade 2: 4
            31, 32,                      # Decade 3: 2
        ]  # Total: 20 numbers
        draw.date = datetime(2025, 1, 17)
        return draw

    def test_extract_single_draw(self, mock_draw: MagicMock) -> None:
        """Test extracting features from a single draw."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw)

        assert isinstance(features, DrawFeatures)
        assert features.draw_sum == sum(mock_draw.numbers)
        assert len(features.decade_counts) == 7
        assert sum(features.decade_counts) == 20  # All 20 numbers accounted for
        assert 0 <= features.entropy <= np.log2(7) + 0.1  # Within valid range
        assert 0 <= features.uniqueness <= 1
        assert features.date == datetime(2025, 1, 15)

    def test_extract_decade_counts(self, mock_draw: MagicMock) -> None:
        """Test decade count calculation."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw)

        # Verify counts match expected distribution
        assert features.decade_counts[0] == 3  # Decade 0: 3, 7, 9
        assert features.decade_counts[1] == 3  # Decade 1: 12, 15, 18
        assert features.decade_counts[2] == 3  # Decade 2: 22, 25, 28
        assert features.decade_counts[3] == 3  # Decade 3: 33, 36, 39
        assert features.decade_counts[4] == 3  # Decade 4: 42, 45, 48
        assert features.decade_counts[5] == 2  # Decade 5: 53, 56
        assert features.decade_counts[6] == 3  # Decade 6: 62, 65, 68

    def test_entropy_uniform_distribution(self, mock_draw_uniform: MagicMock) -> None:
        """Test entropy is high for uniform distribution."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw_uniform)

        # Uniform distribution should have high entropy (close to max ~2.807)
        assert features.entropy > 2.5

    def test_entropy_skewed_distribution(self, mock_draw_skewed: MagicMock) -> None:
        """Test entropy is lower for skewed distribution."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw_skewed)

        # Skewed distribution should have lower entropy
        # With decades 4, 5, 6 empty, entropy should be < max
        assert features.entropy < 2.5

    def test_uniqueness_heuristic(self, mock_draw_skewed: MagicMock) -> None:
        """Test uniqueness heuristic (no frequency data)."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw_skewed)

        # With all numbers <= 32, uniqueness should be low
        # (heuristic: numbers > 31 are "unique")
        assert features.uniqueness < 0.2

    def test_uniqueness_with_high_numbers(self, mock_draw: MagicMock) -> None:
        """Test uniqueness with numbers > 31."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract(mock_draw)

        # Count numbers > 31 in mock_draw
        high_count = sum(1 for n in mock_draw.numbers if n > 31)
        expected_uniqueness = high_count / len(mock_draw.numbers)
        assert features.uniqueness == pytest.approx(expected_uniqueness)

    def test_uniqueness_with_frequency_data(self, mock_draw: MagicMock) -> None:
        """Test uniqueness calculation with actual frequency data."""
        # Create frequency data where numbers 50+ are rare
        frequencies = {i: 100 - i for i in range(1, 71)}  # Higher number = lower freq

        extractor = DrawFeatureExtractor(
            number_frequencies=frequencies, uniqueness_percentile=25.0
        )
        features = extractor.extract(mock_draw)

        # With this frequency distribution, high numbers should be "rare"
        assert 0 <= features.uniqueness <= 1

    def test_extract_batch(
        self, mock_draw: MagicMock, mock_draw_uniform: MagicMock
    ) -> None:
        """Test batch extraction of multiple draws."""
        extractor = DrawFeatureExtractor()
        features_list = extractor.extract_batch([mock_draw, mock_draw_uniform])

        assert len(features_list) == 2
        assert all(isinstance(f, DrawFeatures) for f in features_list)
        assert features_list[0].date == datetime(2025, 1, 15)
        assert features_list[1].date == datetime(2025, 1, 16)

    def test_extract_batch_empty(self) -> None:
        """Test batch extraction with empty list."""
        extractor = DrawFeatureExtractor()
        features_list = extractor.extract_batch([])
        assert features_list == []


class TestFeatureStatistics:
    """Test FeatureStatistics computation."""

    @pytest.fixture
    def sample_features(self) -> list[DrawFeatures]:
        """Create sample features for statistics testing."""
        return [
            DrawFeatures(
                draw_sum=700,
                decade_counts=(3, 3, 3, 3, 3, 3, 2),
                entropy=2.7,
                uniqueness=0.5,
            ),
            DrawFeatures(
                draw_sum=720,
                decade_counts=(2, 3, 3, 3, 3, 3, 3),
                entropy=2.8,
                uniqueness=0.6,
            ),
            DrawFeatures(
                draw_sum=710,
                decade_counts=(3, 2, 3, 3, 3, 3, 3),
                entropy=2.75,
                uniqueness=0.55,
            ),
        ]

    def test_compute_statistics(self, sample_features: list[DrawFeatures]) -> None:
        """Test statistics computation."""
        extractor = DrawFeatureExtractor()
        stats = extractor.compute_statistics(sample_features)

        assert isinstance(stats, FeatureStatistics)
        assert stats.n_draws == 3
        assert stats.sum_mean == pytest.approx(710.0)
        assert stats.sum_std > 0
        assert stats.entropy_mean == pytest.approx(2.75)
        assert stats.uniqueness_mean == pytest.approx(0.55)
        assert len(stats.decade_means) == 7
        assert len(stats.decade_stds) == 7

    def test_compute_statistics_empty(self) -> None:
        """Test statistics with empty feature list."""
        extractor = DrawFeatureExtractor()
        stats = extractor.compute_statistics([])

        assert stats.n_draws == 0
        assert stats.sum_mean == 0.0
        assert stats.entropy_mean == 0.0
        assert stats.uniqueness_mean == 0.0

    def test_statistics_to_dict(self, sample_features: list[DrawFeatures]) -> None:
        """Test FeatureStatistics to_dict."""
        extractor = DrawFeatureExtractor()
        stats = extractor.compute_statistics(sample_features)
        d = stats.to_dict()

        assert "n_draws" in d
        assert "sum_mean" in d
        assert "sum_std" in d
        assert "entropy_mean" in d
        assert "decade_means" in d
        assert len(d["decade_means"]) == 7


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.fixture
    def mock_draw(self) -> MagicMock:
        """Create a mock DrawResult."""
        draw = MagicMock()
        draw.numbers = list(range(1, 21))  # Numbers 1-20
        draw.date = datetime(2025, 1, 1)
        return draw

    def test_extract_draw_features(self, mock_draw: MagicMock) -> None:
        """Test extract_draw_features convenience function."""
        features = extract_draw_features(mock_draw)

        assert isinstance(features, DrawFeatures)
        assert features.draw_sum == sum(range(1, 21))  # 1+2+...+20 = 210

    def test_extract_draw_features_with_frequencies(
        self, mock_draw: MagicMock
    ) -> None:
        """Test extract_draw_features with frequency data."""
        frequencies = {i: 50 for i in range(1, 71)}
        features = extract_draw_features(mock_draw, number_frequencies=frequencies)

        assert isinstance(features, DrawFeatures)

    def test_compute_feature_matrix(self, mock_draw: MagicMock) -> None:
        """Test compute_feature_matrix function."""
        draws = [mock_draw, mock_draw]
        matrix = compute_feature_matrix(draws)

        assert matrix.shape == (2, 10)
        # Both rows should be identical since same draw
        assert np.allclose(matrix[0], matrix[1])


class TestNullModelReadiness:
    """Test that features are suitable for null model comparison."""

    @pytest.fixture
    def sample_draws(self) -> list[MagicMock]:
        """Create sample draws for null model testing."""
        draws = []
        for i in range(100):
            draw = MagicMock()
            # Random-ish distribution of 20 numbers from 1-70
            np.random.seed(i)
            draw.numbers = sorted(np.random.choice(range(1, 71), 20, replace=False).tolist())
            draw.date = datetime(2025, 1, 1)
            draws.append(draw)
        return draws

    def test_feature_vectors_numeric(self, sample_draws: list[MagicMock]) -> None:
        """Test that feature vectors are numeric (for null model tests)."""
        matrix = compute_feature_matrix(sample_draws)

        # All values should be finite numbers
        assert np.all(np.isfinite(matrix))
        # No NaN values
        assert not np.any(np.isnan(matrix))

    def test_feature_variance_nonzero(self, sample_draws: list[MagicMock]) -> None:
        """Test that features have variance (can be permuted meaningfully)."""
        matrix = compute_feature_matrix(sample_draws)

        # Each column should have some variance
        variances = np.var(matrix, axis=0)
        assert np.all(variances > 0), "All features should have nonzero variance"

    def test_entropy_bounded(self, sample_draws: list[MagicMock]) -> None:
        """Test that entropy is within theoretical bounds."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract_batch(sample_draws)

        max_entropy = np.log2(7)  # ~2.807 for 7 decades
        for f in features:
            assert 0 <= f.entropy <= max_entropy + 0.01

    def test_uniqueness_bounded(self, sample_draws: list[MagicMock]) -> None:
        """Test that uniqueness is in [0, 1]."""
        extractor = DrawFeatureExtractor()
        features = extractor.extract_batch(sample_draws)

        for f in features:
            assert 0 <= f.uniqueness <= 1


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_numbers(self) -> None:
        """Test draw with empty numbers list."""
        draw = MagicMock()
        draw.numbers = []
        draw.date = None

        extractor = DrawFeatureExtractor()
        features = extractor.extract(draw)

        assert features.draw_sum == 0
        assert features.decade_counts == (0, 0, 0, 0, 0, 0, 0)
        assert features.entropy == 0.0
        assert features.uniqueness == 0.0

    def test_all_same_decade(self) -> None:
        """Test draw with all numbers in same decade."""
        draw = MagicMock()
        draw.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # All in decade 0
        draw.date = None

        extractor = DrawFeatureExtractor()
        features = extractor.extract(draw)

        assert features.decade_counts[0] == 10
        assert sum(features.decade_counts) == 10
        # Single-decade should have zero entropy
        assert features.entropy == 0.0

    def test_numbers_at_boundaries(self) -> None:
        """Test numbers at decade boundaries."""
        draw = MagicMock()
        draw.numbers = [1, 10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 60, 61, 70]
        draw.date = None

        extractor = DrawFeatureExtractor()
        features = extractor.extract(draw)

        # Each decade should have exactly 2 numbers
        assert features.decade_counts == (2, 2, 2, 2, 2, 2, 2)

    def test_draw_without_date(self) -> None:
        """Test draw without date attribute."""
        draw = MagicMock(spec=[])  # Empty spec - no attributes
        draw.numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        extractor = DrawFeatureExtractor()
        features = extractor.extract(draw)

        assert features.date is None
