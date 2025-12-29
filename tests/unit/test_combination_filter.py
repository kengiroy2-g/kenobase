"""Unit tests for kenobase.core.combination_filter module (TASK-P05)."""

import pytest

from kenobase.analysis.sum_distribution import SumCluster
from kenobase.core.combination_filter import (
    SumBounds,
    derive_sum_bounds_from_clusters,
    derive_sum_bounds_from_config,
)
from kenobase.core.config import KenobaseConfig, SumWindowsConfig


class TestSumBounds:
    """Tests for SumBounds dataclass."""

    def test_inactive_when_no_bounds(self):
        """SumBounds is inactive when both min and max are None."""
        bounds = SumBounds(min_sum=None, max_sum=None)
        assert not bounds.is_active()

    def test_active_when_min_set(self):
        """SumBounds is active when min_sum is set."""
        bounds = SumBounds(min_sum=100, max_sum=None)
        assert bounds.is_active()

    def test_active_when_max_set(self):
        """SumBounds is active when max_sum is set."""
        bounds = SumBounds(min_sum=None, max_sum=200)
        assert bounds.is_active()

    def test_active_when_both_set(self):
        """SumBounds is active when both are set."""
        bounds = SumBounds(min_sum=100, max_sum=200)
        assert bounds.is_active()

    def test_repr_inactive(self):
        """Inactive SumBounds has clear repr."""
        bounds = SumBounds(min_sum=None, max_sum=None)
        assert "inactive" in repr(bounds)

    def test_repr_active(self):
        """Active SumBounds shows range."""
        bounds = SumBounds(min_sum=100, max_sum=200, source="test")
        assert "100" in repr(bounds)
        assert "200" in repr(bounds)
        assert "test" in repr(bounds)


class TestDeriveSumBoundsFromClusters:
    """Tests for derive_sum_bounds_from_clusters function."""

    def test_empty_clusters(self):
        """Returns inactive bounds for empty cluster list."""
        bounds = derive_sum_bounds_from_clusters([])
        assert not bounds.is_active()
        assert bounds.source == "cluster"

    def test_single_cluster(self):
        """Extracts bounds from single cluster."""
        cluster = SumCluster(
            center=150.0,
            range_min=140,
            range_max=160,
            density=0.20,
            z_score=0.5,
        )
        bounds = derive_sum_bounds_from_clusters([cluster])
        assert bounds.min_sum == 140
        assert bounds.max_sum == 160
        assert bounds.source == "cluster"
        assert bounds.cluster_density == pytest.approx(0.20)

    def test_multiple_clusters_union(self):
        """Union of multiple clusters gives outer bounds."""
        clusters = [
            SumCluster(center=150.0, range_min=140, range_max=160, density=0.15, z_score=0.0),
            SumCluster(center=200.0, range_min=190, range_max=210, density=0.20, z_score=1.0),
        ]
        bounds = derive_sum_bounds_from_clusters(clusters, use_union=True)
        assert bounds.min_sum == 140  # min of all range_min
        assert bounds.max_sum == 210  # max of all range_max
        assert bounds.cluster_density == pytest.approx(0.35)

    def test_multiple_clusters_largest_only(self):
        """With use_union=False, only largest cluster is used."""
        clusters = [
            SumCluster(center=150.0, range_min=140, range_max=160, density=0.10, z_score=0.0),
            SumCluster(center=200.0, range_min=190, range_max=210, density=0.25, z_score=1.0),
        ]
        bounds = derive_sum_bounds_from_clusters(clusters, use_union=False)
        assert bounds.min_sum == 190  # from largest cluster
        assert bounds.max_sum == 210
        assert bounds.cluster_density == pytest.approx(0.25)


class TestDeriveSumBoundsFromConfig:
    """Tests for derive_sum_bounds_from_config function."""

    def test_manual_overrides_priority(self):
        """Manual overrides have highest priority."""
        config = KenobaseConfig()
        config.analysis.sum_windows = SumWindowsConfig(
            manual_min_sum=100,
            manual_max_sum=200,
        )
        # Even with clusters, manual should win
        clusters = [
            SumCluster(center=150.0, range_min=140, range_max=160, density=0.20, z_score=0.0),
        ]
        bounds = derive_sum_bounds_from_config(config, clusters=clusters)
        assert bounds.min_sum == 100
        assert bounds.max_sum == 200
        assert bounds.source == "config"

    def test_clusters_used_when_no_manual(self):
        """Clusters are used when no manual overrides."""
        config = KenobaseConfig()
        config.analysis.sum_windows = SumWindowsConfig(
            manual_min_sum=None,
            manual_max_sum=None,
        )
        clusters = [
            SumCluster(center=150.0, range_min=140, range_max=160, density=0.20, z_score=0.0),
        ]
        bounds = derive_sum_bounds_from_config(config, clusters=clusters)
        assert bounds.min_sum == 140
        assert bounds.max_sum == 160
        assert bounds.source == "cluster"

    def test_no_bounds_when_nothing_configured(self):
        """Returns inactive bounds when nothing configured."""
        config = KenobaseConfig()
        config.analysis.sum_windows = SumWindowsConfig(
            manual_min_sum=None,
            manual_max_sum=None,
        )
        bounds = derive_sum_bounds_from_config(config, clusters=None)
        assert not bounds.is_active()
        assert bounds.source == "none"
