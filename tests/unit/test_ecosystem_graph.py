"""Unit tests for kenobase.analysis.ecosystem_graph module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from kenobase.analysis.ecosystem_graph import (
    EcosystemEdge,
    EcosystemGraph,
    EcosystemNode,
    build_ecosystem_graph_from_coupling_results,
    load_ecosystem_graph,
    save_ecosystem_graph,
)


class TestEcosystemNode:
    """Tests for EcosystemNode dataclass."""

    def test_create_node(self) -> None:
        """Test basic node creation."""
        node = EcosystemNode(
            name="KENO",
            draws=1000,
            start_date="2022-01-01",
            end_date="2024-12-31",
            pool_max=70,
            draw_size=20,
            is_control=False,
        )
        assert node.name == "KENO"
        assert node.draws == 1000
        assert node.pool_max == 70
        assert not node.is_control

    def test_control_node(self) -> None:
        """Test control node (e.g., EuroJackpot)."""
        node = EcosystemNode(
            name="EUROJACKPOT",
            draws=400,
            is_control=True,
        )
        assert node.is_control is True


class TestEcosystemEdge:
    """Tests for EcosystemEdge dataclass."""

    def test_create_edge(self) -> None:
        """Test basic edge creation."""
        edge = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="conditional_lift_number",
            statistic=1.25,
            q_value=0.03,
            weight=1.25,
            details={"trigger": "11", "target_number": 7},
        )
        assert edge.source == "KENO"
        assert edge.target == "LOTTO"
        assert edge.lag_days == 1
        assert edge.weight == 1.25
        assert edge.details["trigger"] == "11"

    def test_edge_equality(self) -> None:
        """Test edge equality based on source/target/lag/method."""
        edge1 = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="granger",
            statistic=2.5,
            q_value=0.01,
            weight=2.5,
        )
        edge2 = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="granger",
            statistic=3.0,  # Different statistic
            q_value=0.02,
            weight=3.0,
        )
        edge3 = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=2,  # Different lag
            method="granger",
            statistic=2.5,
            q_value=0.01,
            weight=2.5,
        )
        assert edge1 == edge2  # Same source/target/lag/method
        assert edge1 != edge3  # Different lag

    def test_edge_hash(self) -> None:
        """Test edge hashing for use in sets."""
        edge = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="mi",
            statistic=0.5,
            q_value=0.04,
            weight=0.5,
        )
        edge_set = {edge}
        assert edge in edge_set


class TestEcosystemGraph:
    """Tests for EcosystemGraph class."""

    def test_add_node(self) -> None:
        """Test adding nodes to graph."""
        graph = EcosystemGraph()
        node = EcosystemNode(name="KENO", draws=1000)
        graph.add_node(node)
        assert "KENO" in graph.nodes
        assert graph.nodes["KENO"].draws == 1000

    def test_add_edge(self) -> None:
        """Test adding edges to graph."""
        graph = EcosystemGraph()
        edge = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="test",
            statistic=1.0,
            q_value=0.01,
            weight=1.0,
        )
        graph.add_edge(edge)
        assert len(graph.edges) == 1

    def test_no_duplicate_edges(self) -> None:
        """Test that duplicate edges are not added."""
        graph = EcosystemGraph()
        edge1 = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="test",
            statistic=1.0,
            q_value=0.01,
            weight=1.0,
        )
        edge2 = EcosystemEdge(
            source="KENO",
            target="LOTTO",
            lag_days=1,
            method="test",
            statistic=2.0,  # Different statistic
            q_value=0.02,
            weight=2.0,
        )
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        assert len(graph.edges) == 1  # Second edge is duplicate

    def test_get_edges_from(self) -> None:
        """Test getting edges from a source."""
        graph = EcosystemGraph()
        edge1 = EcosystemEdge(
            source="KENO", target="LOTTO", lag_days=1,
            method="a", statistic=1.0, q_value=0.01, weight=1.0
        )
        edge2 = EcosystemEdge(
            source="KENO", target="AUSWAHLWETTE", lag_days=2,
            method="b", statistic=1.0, q_value=0.01, weight=1.0
        )
        edge3 = EcosystemEdge(
            source="LOTTO", target="KENO", lag_days=1,
            method="c", statistic=1.0, q_value=0.01, weight=1.0
        )
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        graph.add_edge(edge3)

        keno_edges = graph.get_edges_from("KENO")
        assert len(keno_edges) == 2
        assert all(e.source == "KENO" for e in keno_edges)

    def test_get_edges_to(self) -> None:
        """Test getting edges to a target."""
        graph = EcosystemGraph()
        edge1 = EcosystemEdge(
            source="KENO", target="LOTTO", lag_days=1,
            method="a", statistic=1.0, q_value=0.01, weight=1.0
        )
        edge2 = EcosystemEdge(
            source="AUSWAHLWETTE", target="LOTTO", lag_days=2,
            method="b", statistic=1.0, q_value=0.01, weight=1.0
        )
        graph.add_edge(edge1)
        graph.add_edge(edge2)

        lotto_edges = graph.get_edges_to("LOTTO")
        assert len(lotto_edges) == 2
        assert all(e.target == "LOTTO" for e in lotto_edges)

    def test_to_networkx_dict(self) -> None:
        """Test export to NetworkX-compatible format."""
        graph = EcosystemGraph()
        graph.add_node(EcosystemNode(name="KENO", draws=1000))
        graph.add_node(EcosystemNode(name="LOTTO", draws=400))
        graph.add_edge(EcosystemEdge(
            source="KENO", target="LOTTO", lag_days=1,
            method="test", statistic=1.5, q_value=0.02, weight=1.5
        ))

        nx_dict = graph.to_networkx_dict()
        assert nx_dict["directed"] is True
        assert nx_dict["multigraph"] is True
        assert len(nx_dict["nodes"]) == 2
        assert len(nx_dict["links"]) == 1
        assert nx_dict["links"][0]["source"] == "KENO"
        assert nx_dict["links"][0]["target"] == "LOTTO"

    def test_summary(self) -> None:
        """Test graph summary generation."""
        graph = EcosystemGraph()
        graph.add_node(EcosystemNode(name="KENO", draws=1000))
        graph.add_node(EcosystemNode(name="EUROJACKPOT", draws=400, is_control=True))
        graph.add_edge(EcosystemEdge(
            source="KENO", target="EUROJACKPOT", lag_days=1,
            method="granger", statistic=2.0, q_value=0.01, weight=2.0
        ))

        summary = graph.summary()
        assert summary["n_nodes"] == 2
        assert summary["n_edges"] == 1
        assert "KENO" in summary["games"]
        assert "granger" in summary["methods_used"]
        assert "EUROJACKPOT" in summary["control_nodes"]


class TestEdgeFiltering:
    """Tests for edge filtering by q-value and lift thresholds."""

    def test_q_value_filtering(self) -> None:
        """Test that edges with q > threshold are filtered out."""
        # Create synthetic coupling JSON
        coupling_data = {
            "games": {
                "KENO": {"draws": 1000, "start": "2022-01-01", "end": "2024-12-31"},
                "LOTTO": {"draws": 400, "start": "2022-01-01", "end": "2024-12-31"},
            },
            "conditional_lifts": {
                "alpha_fdr": 0.05,
                "significant": {
                    "number_triggers": [
                        {
                            "source": "KENO",
                            "target": "LOTTO",
                            "lag_days": 1,
                            "trigger": "11",
                            "target_number": 7,
                            "lift": 1.5,
                            "q_value": 0.03,  # Below threshold
                            "support": 100,
                            "base_rate": 0.12,
                            "conditional_rate": 0.18,
                        },
                        {
                            "source": "KENO",
                            "target": "LOTTO",
                            "lag_days": 2,
                            "trigger": "15",
                            "target_number": 9,
                            "lift": 1.3,
                            "q_value": 0.08,  # Above threshold
                            "support": 80,
                            "base_rate": 0.12,
                            "conditional_rate": 0.16,
                        },
                    ],
                    "keno_position_triggers": [],
                    "ordered_value_triggers": [],
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(coupling_data, f)
            temp_path = f.name

        try:
            graph = build_ecosystem_graph_from_coupling_results(
                coupling_json_path=temp_path,
                q_threshold=0.05,
                lift_threshold=1.1,
            )
            # Only the first edge should pass (q=0.03 < 0.05)
            assert len(graph.edges) == 1
            assert graph.edges[0].q_value == 0.03
        finally:
            Path(temp_path).unlink()

    def test_lift_filtering(self) -> None:
        """Test that edges with lift < threshold are filtered out."""
        coupling_data = {
            "games": {
                "KENO": {"draws": 1000, "start": "2022-01-01", "end": "2024-12-31"},
                "LOTTO": {"draws": 400, "start": "2022-01-01", "end": "2024-12-31"},
            },
            "conditional_lifts": {
                "alpha_fdr": 0.05,
                "significant": {
                    "number_triggers": [
                        {
                            "source": "KENO",
                            "target": "LOTTO",
                            "lag_days": 1,
                            "trigger": "11",
                            "target_number": 7,
                            "lift": 1.5,  # Above lift threshold
                            "q_value": 0.01,
                            "support": 100,
                        },
                        {
                            "source": "KENO",
                            "target": "LOTTO",
                            "lag_days": 2,
                            "trigger": "15",
                            "target_number": 9,
                            "lift": 1.05,  # Below lift threshold
                            "q_value": 0.01,
                            "support": 80,
                        },
                    ],
                    "keno_position_triggers": [],
                    "ordered_value_triggers": [],
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(coupling_data, f)
            temp_path = f.name

        try:
            graph = build_ecosystem_graph_from_coupling_results(
                coupling_json_path=temp_path,
                q_threshold=0.05,
                lift_threshold=1.1,  # 1.05 < 1.1, so second edge filtered
            )
            assert len(graph.edges) == 1
            assert graph.edges[0].statistic == 1.5
        finally:
            Path(temp_path).unlink()


class TestSaveLoad:
    """Tests for save/load functionality."""

    def test_save_and_load_roundtrip(self) -> None:
        """Test that saving and loading preserves graph structure."""
        original = EcosystemGraph()
        original.metadata = {"version": "1.0", "test": True}
        original.add_node(EcosystemNode(
            name="KENO", draws=1000, start_date="2022-01-01",
            end_date="2024-12-31", pool_max=70, draw_size=20
        ))
        original.add_node(EcosystemNode(
            name="LOTTO", draws=400, is_control=False
        ))
        original.add_edge(EcosystemEdge(
            source="KENO", target="LOTTO", lag_days=1,
            method="conditional_lift_number", statistic=1.5,
            q_value=0.02, weight=1.5,
            details={"trigger": "11", "target_number": 7}
        ))

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            temp_path = f.name

        try:
            save_ecosystem_graph(original, temp_path)
            loaded = load_ecosystem_graph(temp_path)

            assert len(loaded.nodes) == 2
            assert "KENO" in loaded.nodes
            assert loaded.nodes["KENO"].draws == 1000
            assert len(loaded.edges) == 1
            assert loaded.edges[0].source == "KENO"
            assert loaded.edges[0].target == "LOTTO"
        finally:
            Path(temp_path).unlink()


class TestIntegration:
    """Integration tests with real coupling results if available."""

    @pytest.fixture
    def coupling_path(self) -> Path:
        """Get path to actual coupling results."""
        path = Path("results/cross_lottery_coupling.json")
        if not path.exists():
            pytest.skip("Coupling results not found")
        return path

    def test_build_from_real_data(self, coupling_path: Path) -> None:
        """Test building graph from actual coupling results."""
        graph = build_ecosystem_graph_from_coupling_results(
            coupling_json_path=coupling_path,
            q_threshold=0.05,
            lift_threshold=1.1,
        )

        # Should have at least 6 game nodes
        assert len(graph.nodes) >= 6
        assert "KENO" in graph.nodes
        assert "LOTTO" in graph.nodes
        assert "EUROJACKPOT" in graph.nodes

        # EUROJACKPOT should be marked as control
        assert graph.nodes["EUROJACKPOT"].is_control is True

        # Summary should work
        summary = graph.summary()
        assert summary["n_nodes"] >= 6
        assert "EUROJACKPOT" in summary["control_nodes"]
