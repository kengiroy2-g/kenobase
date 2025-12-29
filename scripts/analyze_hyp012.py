#!/usr/bin/env python3
"""HYP-012 Analysis Script: Stake-Number Correlation.

Tests hypothesis that stake amounts (Spieleinsatz) correlate with drawn numbers,
identifying "low-stake" vs "high-stake" number patterns.

Usage:
    python scripts/analyze_hyp012.py
    python scripts/analyze_hyp012.py --stake-file path/to/stake.csv
    python scripts/analyze_hyp012.py --output results/hyp012_custom.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.stake_correlation import (
    StakeAnalysisSummary,
    run_hyp012_analysis,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_result(summary: StakeAnalysisSummary) -> dict:
    """Format analysis result for JSON output.

    Args:
        summary: Analysis summary

    Returns:
        JSON-serializable dict
    """
    corr = summary.correlation

    result = {
        "hypothesis": "HYP-012",
        "description": "Stake-Number Correlation Analysis (Spieleinsatz)",
        "timestamp": datetime.now().isoformat(),
        "correlation": {
            "spieleinsatz": {
                "pearson_r": round(corr.pearson_r, 4),
                "pearson_p": round(corr.pearson_p, 4),
                "spearman_r": round(corr.spearman_r, 4),
                "spearman_p": round(corr.spearman_p, 4),
                "is_significant": bool(corr.is_significant),
            },
        },
        "data_summary": {
            "n_numbers": int(corr.n_samples),
            "n_draws": int(corr.n_draws),
        },
        "classification": {
            "low_stake_numbers": [int(n) for n in summary.low_stake_numbers],
            "high_stake_numbers": [int(n) for n in summary.high_stake_numbers],
            "stats": {
                k: float(v) if isinstance(v, (int, float)) else v
                for k, v in summary.classification_stats.items()
            },
        },
        "interpretation": interpret_result(summary),
    }

    # Add optional correlations
    if summary.auszahlung_correlation:
        az = summary.auszahlung_correlation
        result["correlation"]["total_auszahlung"] = {
            "pearson_r": round(az.pearson_r, 4),
            "pearson_p": round(az.pearson_p, 4),
            "spearman_r": round(az.spearman_r, 4),
            "spearman_p": round(az.spearman_p, 4),
            "is_significant": bool(az.is_significant),
        }

    if summary.restbetrag_correlation:
        rb = summary.restbetrag_correlation
        result["correlation"]["restbetrag"] = {
            "pearson_r": round(rb.pearson_r, 4),
            "pearson_p": round(rb.pearson_p, 4),
            "spearman_r": round(rb.spearman_r, 4),
            "spearman_p": round(rb.spearman_p, 4),
            "is_significant": bool(rb.is_significant),
        }

    return result


def interpret_result(summary: StakeAnalysisSummary) -> dict:
    """Generate interpretation of results.

    Args:
        summary: Analysis summary

    Returns:
        Dict with interpretation text
    """
    corr = summary.correlation

    # Determine significance and direction
    if not corr.is_significant:
        significance = "NOT_SIGNIFICANT"
        verdict = (
            "No significant correlation found between draw frequency and stake amounts. "
            "Numbers appear independent of Spieleinsatz."
        )
    else:
        if corr.spearman_r > 0.2:
            significance = "POSITIVE_CORRELATION"
            verdict = (
                "Positive correlation: Numbers drawn more often appear in high-stake draws. "
                "This could suggest stake-influenced number selection or player behavior patterns."
            )
        elif corr.spearman_r < -0.2:
            significance = "NEGATIVE_CORRELATION"
            verdict = (
                "Negative correlation: Numbers drawn more often appear in LOW-stake draws. "
                "This could indicate the RNG behavior differs based on stake levels."
            )
        else:
            significance = "WEAK_CORRELATION"
            verdict = (
                "Weak but statistically significant correlation. "
                "Effect size is small, likely no practical significance."
            )

    return {
        "significance": significance,
        "verdict": verdict,
        "low_stake_count": len(summary.low_stake_numbers),
        "high_stake_count": len(summary.high_stake_numbers),
        "recommendation": (
            f"Low-stake numbers: {summary.low_stake_numbers[:10]}..."
            if len(summary.low_stake_numbers) > 10
            else f"Low-stake numbers: {summary.low_stake_numbers}"
        ),
    }


def main() -> int:
    """Run HYP-012 analysis.

    Returns:
        Exit code (0 = success)
    """
    parser = argparse.ArgumentParser(
        description="HYP-012: Analyze stake-number correlation (Spieleinsatz)"
    )
    parser.add_argument(
        "--stake-file",
        type=str,
        default="Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV",
        help="Path to stake data CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/hyp012_stake_correlation.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="Standard deviation threshold for classification (default: 1.0)",
    )

    args = parser.parse_args()

    # Resolve paths
    stake_path = project_root / args.stake_file
    output_path = project_root / args.output

    # Check file exists
    if not stake_path.exists():
        logger.error(f"Stake file not found: {stake_path}")
        return 1

    # Run analysis
    logger.info(f"Running HYP-012 analysis with stake data from {stake_path}")
    summary = run_hyp012_analysis(
        stake_path=stake_path,
        classification_threshold=args.threshold,
    )

    # Format and display results
    result = format_result(summary)

    print("\n" + "=" * 60)
    print("HYP-012: STAKE-NUMBER CORRELATION ANALYSIS")
    print("=" * 60)
    print(f"\nData: {result['data_summary']['n_draws']} draws analyzed")
    print(f"\nSpielgeld Correlation Results:")
    spieleinsatz = result["correlation"]["spieleinsatz"]
    print(f"  Pearson:  r={spieleinsatz['pearson_r']:.4f}, "
          f"p={spieleinsatz['pearson_p']:.4f}")
    print(f"  Spearman: r={spieleinsatz['spearman_r']:.4f}, "
          f"p={spieleinsatz['spearman_p']:.4f}")
    print(f"  Significant: {spieleinsatz['is_significant']}")

    if "total_auszahlung" in result["correlation"]:
        ausz = result["correlation"]["total_auszahlung"]
        print(f"\nTotal Auszahlung Correlation:")
        print(f"  Pearson:  r={ausz['pearson_r']:.4f}, p={ausz['pearson_p']:.4f}")
        print(f"  Significant: {ausz['is_significant']}")

    if "restbetrag" in result["correlation"]:
        rest = result["correlation"]["restbetrag"]
        print(f"\nRestbetrag Correlation:")
        print(f"  Pearson:  r={rest['pearson_r']:.4f}, p={rest['pearson_p']:.4f}")
        print(f"  Significant: {rest['is_significant']}")

    print(f"\nClassification:")
    print(f"  Low-stake numbers ({len(summary.low_stake_numbers)}): "
          f"{summary.low_stake_numbers}")
    print(f"  High-stake numbers ({len(summary.high_stake_numbers)}): "
          f"{summary.high_stake_numbers}")
    print(f"\nInterpretation: {result['interpretation']['significance']}")
    print(f"  {result['interpretation']['verdict']}")
    print("=" * 60)

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
