#!/usr/bin/env python
"""Build ecosystem graph from cross-lottery coupling results.

Usage:
    python scripts/build_ecosystem_graph.py
    python scripts/build_ecosystem_graph.py --coupling results/cross_lottery_coupling.json
    python scripts/build_ecosystem_graph.py --q-threshold 0.01 --lift-threshold 1.2
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.ecosystem_graph import (
    build_ecosystem_graph_from_coupling_results,
    save_ecosystem_graph,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build ecosystem graph from cross-lottery coupling results"
    )
    parser.add_argument(
        "--coupling",
        type=Path,
        default=Path("results/cross_lottery_coupling.json"),
        help="Path to cross_lottery_coupling.json (default: results/cross_lottery_coupling.json)",
    )
    parser.add_argument(
        "--alternative",
        type=Path,
        default=None,
        help="Path to alternative coupling results JSON (optional)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/ecosystem_graph.json"),
        help="Output path (default: results/ecosystem_graph.json)",
    )
    parser.add_argument(
        "--q-threshold",
        type=float,
        default=0.05,
        help="FDR q-value threshold (default: 0.05)",
    )
    parser.add_argument(
        "--lift-threshold",
        type=float,
        default=1.1,
        help="Minimum lift for conditional lift edges (default: 1.1)",
    )
    args = parser.parse_args()

    if not args.coupling.exists():
        logger.error(f"Coupling results not found: {args.coupling}")
        return 1

    logger.info(f"Building ecosystem graph from {args.coupling}")
    logger.info(f"Thresholds: q < {args.q_threshold}, lift > {args.lift_threshold}")

    try:
        graph = build_ecosystem_graph_from_coupling_results(
            coupling_json_path=args.coupling,
            q_threshold=args.q_threshold,
            lift_threshold=args.lift_threshold,
            alternative_results_path=args.alternative,
        )
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        return 1

    summary = graph.summary()
    logger.info(f"Graph summary: {summary['n_nodes']} nodes, {summary['n_edges']} edges")
    logger.info(f"Games: {summary['games']}")
    logger.info(f"Methods: {summary['methods_used']}")
    logger.info(f"Edges by method: {summary['edges_by_method']}")

    save_ecosystem_graph(graph, args.output)
    logger.info(f"Saved ecosystem graph to {args.output}")

    # Print summary for quick inspection
    print("\n=== Ecosystem Graph Summary ===")
    print(f"Nodes: {summary['n_nodes']}")
    print(f"Edges: {summary['n_edges']}")
    print(f"Games: {', '.join(summary['games'])}")
    print(f"Control nodes: {', '.join(summary['control_nodes']) or 'none'}")
    print(f"Methods: {', '.join(summary['methods_used']) or 'none'}")

    if summary["n_edges"] > 0:
        print("\nEdge details:")
        for method, count in summary["edges_by_method"].items():
            print(f"  {method}: {count}")

        print("\nTop edges by weight:")
        sorted_edges = sorted(graph.edges, key=lambda e: -e.weight)[:10]
        for edge in sorted_edges:
            print(
                f"  {edge.source} -> {edge.target} "
                f"(lag={edge.lag_days}d, {edge.method}, "
                f"weight={edge.weight:.3f}, q={edge.q_value:.4f})"
            )
    else:
        print("\nNo significant edges found with current thresholds.")
        print("Consider lowering --q-threshold or --lift-threshold")

    return 0


if __name__ == "__main__":
    sys.exit(main())
