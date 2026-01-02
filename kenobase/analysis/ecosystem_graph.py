"""Ecosystem-Graph for German Lottery cross-game couplings.

This module builds a graph representation of the German lottery ecosystem where:
- Nodes = Games (KENO, LOTTO, AUSWAHLWETTE, GLUECKSSPIRALE, EUROWETTE, EUROJACKPOT)
- Edges = Robust statistical couplings between games

Edge criterion:
- q_value < 0.05 AND lift > 1.1 (FDR-corrected conditional lift)
- OR significant alternative method (Granger, MI, TE, DTW)

Output format is NetworkX-compatible dict with nodes/edges/weights.

Important:
- EuroJackpot is included as a separate node (international, control game)
- The graph is directed (source -> target with lag)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EcosystemNode:
    """A node representing a lottery game in the ecosystem.

    Attributes:
        name: Game identifier (e.g., 'KENO', 'LOTTO')
        draws: Number of draws in the dataset
        start_date: First draw date (ISO format)
        end_date: Last draw date (ISO format)
        pool_max: Maximum number in the pool
        draw_size: Numbers drawn per game
        is_control: True if this is a control game (e.g., EuroJackpot)
    """

    name: str
    draws: int = 0
    start_date: str = ""
    end_date: str = ""
    pool_max: int = 0
    draw_size: int = 0
    is_control: bool = False


@dataclass(frozen=True)
class EcosystemEdge:
    """A directed edge representing a coupling between two games.

    Attributes:
        source: Source game name
        target: Target game name
        lag_days: Lag in days from source to target
        method: Detection method (conditional_lift, granger, mi, te, dtw)
        statistic: Primary statistic value (lift or test statistic)
        q_value: FDR-corrected q-value
        weight: Edge weight for graph algorithms (derived from statistic)
        details: Additional method-specific details
    """

    source: str
    target: str
    lag_days: int
    method: str
    statistic: float
    q_value: float
    weight: float
    details: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.lag_days, self.method))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EcosystemEdge):
            return NotImplemented
        return (
            self.source == other.source
            and self.target == other.target
            and self.lag_days == other.lag_days
            and self.method == other.method
        )


@dataclass
class EcosystemGraph:
    """NetworkX-compatible graph representation of lottery ecosystem.

    Attributes:
        nodes: Dict of game name -> EcosystemNode
        edges: List of EcosystemEdge (directed edges)
        metadata: Analysis metadata (timestamps, config, etc.)
    """

    nodes: dict[str, EcosystemNode] = field(default_factory=dict)
    edges: list[EcosystemEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: EcosystemNode) -> None:
        """Add or update a node."""
        self.nodes[node.name] = node

    def add_edge(self, edge: EcosystemEdge) -> None:
        """Add an edge if not duplicate."""
        if edge not in self.edges:
            self.edges.append(edge)

    def get_edges_from(self, source: str) -> list[EcosystemEdge]:
        """Get all edges originating from a source game."""
        return [e for e in self.edges if e.source == source]

    def get_edges_to(self, target: str) -> list[EcosystemEdge]:
        """Get all edges pointing to a target game."""
        return [e for e in self.edges if e.target == target]

    def to_networkx_dict(self) -> dict[str, Any]:
        """Export to NetworkX-compatible adjacency dict format.

        Returns:
            Dict with 'nodes', 'edges', 'metadata' suitable for
            nx.node_link_graph() or direct JSON serialization.
        """
        return {
            "directed": True,
            "multigraph": True,
            "graph": self.metadata,
            "nodes": [
                {"id": name, **asdict(node)} for name, node in self.nodes.items()
            ],
            "links": [
                {
                    "source": e.source,
                    "target": e.target,
                    "lag_days": e.lag_days,
                    "method": e.method,
                    "statistic": e.statistic,
                    "q_value": e.q_value,
                    "weight": e.weight,
                    **e.details,
                }
                for e in self.edges
            ],
        }

    def summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        return {
            "n_nodes": len(self.nodes),
            "n_edges": len(self.edges),
            "games": list(self.nodes.keys()),
            "methods_used": list(set(e.method for e in self.edges)),
            "edges_by_method": {
                method: len([e for e in self.edges if e.method == method])
                for method in set(e.method for e in self.edges)
            },
            "control_nodes": [n for n, node in self.nodes.items() if node.is_control],
        }


def build_ecosystem_graph_from_coupling_results(
    coupling_json_path: Path | str,
    q_threshold: float = 0.05,
    lift_threshold: float = 1.1,
    alternative_results_path: Optional[Path | str] = None,
) -> EcosystemGraph:
    """Build ecosystem graph from cross_lottery_coupling.json.

    Args:
        coupling_json_path: Path to cross_lottery_coupling.json
        q_threshold: FDR q-value threshold for significance
        lift_threshold: Minimum lift for conditional lift edges
        alternative_results_path: Optional path to alternative_coupling results

    Returns:
        EcosystemGraph with nodes and edges
    """
    coupling_path = Path(coupling_json_path)
    if not coupling_path.exists():
        raise FileNotFoundError(f"Coupling results not found: {coupling_path}")

    with open(coupling_path, encoding="utf-8") as f:
        data = json.load(f)

    graph = EcosystemGraph()
    graph.metadata = {
        "generated_at": datetime.now().isoformat(),
        "source_file": str(coupling_path),
        "q_threshold": q_threshold,
        "lift_threshold": lift_threshold,
        "config": data.get("config", {}),
    }

    # Add nodes from games section
    games = data.get("games", {})
    control_games = {"EUROJACKPOT"}  # EuroJackpot is external control

    # Game pool/draw size mapping (from domain knowledge)
    game_specs = {
        "KENO": {"pool_max": 70, "draw_size": 20},
        "LOTTO": {"pool_max": 49, "draw_size": 6},
        "AUSWAHLWETTE": {"pool_max": 49, "draw_size": 6},
        "GLUECKSSPIRALE": {"pool_max": 9, "draw_size": 7},  # Special format
        "EUROWETTE": {"pool_max": 2, "draw_size": 13},  # Outcome-based
        "EUROJACKPOT": {"pool_max": 50, "draw_size": 5},  # 5+2 format
    }

    for game_name, game_info in games.items():
        specs = game_specs.get(game_name, {"pool_max": 0, "draw_size": 0})
        node = EcosystemNode(
            name=game_name,
            draws=game_info.get("draws", 0),
            start_date=game_info.get("start", ""),
            end_date=game_info.get("end", ""),
            pool_max=specs["pool_max"],
            draw_size=specs["draw_size"],
            is_control=game_name in control_games,
        )
        graph.add_node(node)

    # Extract edges from conditional_lifts.significant
    conditional_lifts = data.get("conditional_lifts", {})
    significant = conditional_lifts.get("significant", {})

    # Process number triggers
    for item in significant.get("number_triggers", []):
        q_val = item.get("q_value", 1.0)
        lift = item.get("lift", 0.0)

        if q_val <= q_threshold and lift >= lift_threshold:
            edge = EcosystemEdge(
                source=item["source"],
                target=item["target"],
                lag_days=item.get("lag_days", 0),
                method="conditional_lift_number",
                statistic=lift,
                q_value=q_val,
                weight=lift,  # Use lift as weight
                details={
                    "trigger": item.get("trigger"),
                    "trigger_kind": "number",
                    "target_number": item.get("target_number"),
                    "support": item.get("support"),
                    "base_rate": item.get("base_rate"),
                    "conditional_rate": item.get("conditional_rate"),
                },
            )
            graph.add_edge(edge)

    # Process KENO position triggers
    for item in significant.get("keno_position_triggers", []):
        q_val = item.get("q_value", 1.0)
        lift = item.get("lift", 0.0)

        if q_val <= q_threshold and lift >= lift_threshold:
            edge = EcosystemEdge(
                source=item["source"],
                target=item["target"],
                lag_days=item.get("lag_days", 0),
                method="conditional_lift_position",
                statistic=lift,
                q_value=q_val,
                weight=lift,
                details={
                    "trigger": item.get("trigger"),
                    "trigger_kind": "keno_position",
                    "target_number": item.get("target_number"),
                    "support": item.get("support"),
                },
            )
            graph.add_edge(edge)

    # Process ordered value triggers
    for item in significant.get("ordered_value_triggers", []):
        q_val = item.get("q_value", 1.0)
        lift = item.get("lift", 0.0)

        if q_val <= q_threshold and lift >= lift_threshold:
            edge = EcosystemEdge(
                source=item["source"],
                target=item["target"],
                lag_days=item.get("lag_days", 0),
                method="conditional_lift_ordered",
                statistic=lift,
                q_value=q_val,
                weight=lift,
                details={
                    "trigger": item.get("trigger"),
                    "trigger_kind": "ordered_value",
                    "target_number": item.get("target_number"),
                    "support": item.get("support"),
                },
            )
            graph.add_edge(edge)

    # Process alternative coupling results if provided
    if alternative_results_path:
        alt_path = Path(alternative_results_path)
        if alt_path.exists():
            _add_alternative_edges(graph, alt_path, q_threshold)
        else:
            logger.warning(f"Alternative results not found: {alt_path}")

    return graph


def _add_alternative_edges(
    graph: EcosystemGraph,
    alt_path: Path,
    q_threshold: float,
) -> None:
    """Add edges from alternative coupling methods (Granger, MI, TE, DTW).

    Args:
        graph: EcosystemGraph to add edges to
        alt_path: Path to alternative coupling JSON
        q_threshold: FDR q-value threshold
    """
    try:
        with open(alt_path, encoding="utf-8") as f:
            alt_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not load alternative results: {e}")
        return

    results = alt_data.get("results", [])
    for item in results:
        q_val = item.get("q_value", 1.0)
        if q_val > q_threshold:
            continue

        # Skip control pairs unless they show unexpected significance
        is_control = item.get("is_control", False)
        if is_control:
            logger.info(
                f"Control pair significant: {item.get('source')}->{item.get('target')}"
            )

        method = item.get("method", "unknown")
        statistic = item.get("statistic", 0.0)

        # Weight: for MI/TE use statistic directly, for DTW invert (less distance = more coupling)
        if method.startswith("dtw"):
            weight = -statistic  # DTW returns negative distance already
        else:
            weight = abs(statistic)

        edge = EcosystemEdge(
            source=item.get("source", "unknown"),
            target=item.get("target", "unknown"),
            lag_days=item.get("lag", 0),
            method=method,
            statistic=statistic,
            q_value=q_val,
            weight=weight,
            details={
                "n_samples": item.get("n_samples"),
                "null_mean": item.get("null_mean"),
                "null_std": item.get("null_std"),
                "segment": item.get("segment"),
                "is_control": is_control,
            },
        )
        graph.add_edge(edge)


def save_ecosystem_graph(
    graph: EcosystemGraph,
    output_path: Path | str,
) -> None:
    """Save ecosystem graph to JSON file.

    Args:
        graph: EcosystemGraph to save
        output_path: Output file path
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "analysis": "ecosystem_graph",
        "generated_at": datetime.now().isoformat(),
        "summary": graph.summary(),
        "graph": graph.to_networkx_dict(),
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved ecosystem graph to {output}")


def load_ecosystem_graph(input_path: Path | str) -> EcosystemGraph:
    """Load ecosystem graph from JSON file.

    Args:
        input_path: Path to ecosystem_graph.json

    Returns:
        EcosystemGraph instance
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    graph_data = data.get("graph", {})
    graph = EcosystemGraph()
    graph.metadata = graph_data.get("graph", {})

    # Load nodes
    for node_data in graph_data.get("nodes", []):
        node = EcosystemNode(
            name=node_data.get("id", node_data.get("name", "unknown")),
            draws=node_data.get("draws", 0),
            start_date=node_data.get("start_date", ""),
            end_date=node_data.get("end_date", ""),
            pool_max=node_data.get("pool_max", 0),
            draw_size=node_data.get("draw_size", 0),
            is_control=node_data.get("is_control", False),
        )
        graph.add_node(node)

    # Load edges
    for link in graph_data.get("links", []):
        # Extract details (everything except core fields)
        core_fields = {
            "source",
            "target",
            "lag_days",
            "method",
            "statistic",
            "q_value",
            "weight",
        }
        details = {k: v for k, v in link.items() if k not in core_fields}

        edge = EcosystemEdge(
            source=link["source"],
            target=link["target"],
            lag_days=link.get("lag_days", 0),
            method=link.get("method", "unknown"),
            statistic=link.get("statistic", 0.0),
            q_value=link.get("q_value", 1.0),
            weight=link.get("weight", 0.0),
            details=details,
        )
        graph.add_edge(edge)

    return graph


__all__ = [
    "EcosystemNode",
    "EcosystemEdge",
    "EcosystemGraph",
    "build_ecosystem_graph_from_coupling_results",
    "save_ecosystem_graph",
    "load_ecosystem_graph",
]
