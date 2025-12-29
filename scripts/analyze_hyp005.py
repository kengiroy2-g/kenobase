#!/usr/bin/env python
"""HYP-005 Analysis Script: Zehnergruppen-Paar-Affinitaet.

This script tests whether certain decade pairs (Zehnergruppen) appear
together more frequently than expected by chance.

Hypothesis: Certain decade pairs have significant affinity (chi-square p < 0.05).

Usage:
    python scripts/analyze_hyp005.py
    python scripts/analyze_hyp005.py --data-path data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_hyp005.py --output results/hyp005_decade_affinity.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.decade_affinity import (
    DecadeAffinityResult,
    decade_pair_to_name,
    generate_affinity_report,
    run_hyp005_analysis,
)
from kenobase.core.data_loader import DataLoader, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run HYP-005 analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-005: Zehnergruppen-Paar-Affinitaet"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO draw data",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/hyp005_decade_affinity.json",
        help="Output path for results",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve paths relative to project root
    data_path = PROJECT_ROOT / args.data_path
    output_path = PROJECT_ROOT / args.output

    # Check data file exists
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    # Load KENO data
    logger.info(f"Loading KENO data from {data_path}")
    loader = DataLoader()
    draws = loader.load(data_path, game_type=GameType.KENO)
    logger.info(f"Loaded {len(draws)} draws")

    # Sort by date
    draws = sorted(draws, key=lambda d: d.date)

    # Run analysis
    logger.info("Running HYP-005 analysis...")
    analysis = run_hyp005_analysis(draws, alpha=args.alpha)

    # Print report
    print(generate_affinity_report(analysis["results"], len(draws)))

    # Print summary
    summary = analysis["summary"]
    print("\n--- Summary ---")
    print(f"Analyzed draws: {summary['n_draws']}")
    print(f"Total decade pairs: {summary['n_pairs_total']}")
    print(f"Significant pairs (p < {args.alpha}): {summary['n_pairs_significant']}")
    print(f"Mean affinity score: {summary['mean_affinity_score']:.4f}")
    print(f"Std affinity score: {summary['std_affinity_score']:.4f}")

    # Conclusion
    print("\n--- Conclusion ---")
    if summary["n_pairs_significant"] > 0:
        print(f"EVIDENCE FOUND: {summary['n_pairs_significant']} significant decade pairs detected.")
        print("Some decade pairs appear together more/less often than expected by chance.")
    else:
        print("NO EVIDENCE: No significant decade pair affinities detected.")
        print("Decade pairs appear randomly distributed.")

    print("=" * 60 + "\n")

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def result_to_dict(r: DecadeAffinityResult) -> dict:
        """Convert DecadeAffinityResult to dict."""
        return {
            "pair": list(r.pair),
            "pair_name": decade_pair_to_name(r.pair),
            "observed": int(r.observed),
            "expected": float(r.expected),
            "affinity_score": float(r.affinity_score),
            "p_value": float(r.p_value),
            "is_significant": bool(r.is_significant),
        }

    output_data = {
        "hypothesis": "HYP-005",
        "description": "Zehnergruppen-Paar-Affinitaet",
        "acceptance_criteria": f"Chi-Quadrat-Test p < {args.alpha}",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "n_draws": summary["n_draws"],
            "n_pairs_total": summary["n_pairs_total"],
            "n_pairs_significant": summary["n_pairs_significant"],
            "alpha": summary["alpha"],
            "mean_affinity_score": summary["mean_affinity_score"],
            "std_affinity_score": summary["std_affinity_score"],
            "max_affinity_score": summary["max_affinity_score"],
            "min_affinity_score": summary["min_affinity_score"],
        },
        "top_pairs": [result_to_dict(r) for r in analysis["top_pairs"]],
        "anti_pairs": [result_to_dict(r) for r in analysis["anti_pairs"]],
        "all_pairs": [result_to_dict(r) for r in analysis["results"]],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
