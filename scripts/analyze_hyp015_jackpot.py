#!/usr/bin/env python3
"""HYP-015: Jackpot-Hoehe vs. Zahlentyp Korrelation.

Analysiert ob die Jackpot-Hoehe (proxied durch GK1-Events) mit bestimmten
Zahlentypen korreliert - insbesondere Birthday-Zahlen (1-31) vs Hohe Zahlen (32-70).

Hypothese: Signifikante Korrelation (|r| > 0.2, p < 0.05, Chi-Quadrat p < 0.05)
zwischen Jackpot-Events und Zahlentyp-Verteilung deutet auf nicht-zufaellige Muster hin.

Usage:
    python scripts/analyze_hyp015_jackpot.py
    python scripts/analyze_hyp015_jackpot.py --keno-data data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_hyp015_jackpot.py --gk1-data Keno_GPTs/10-9_KGDaten_gefiltert.csv
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.jackpot_correlation import (
    export_result_to_json,
    run_hyp015_analysis,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run HYP-015 jackpot correlation analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-015: Jackpot-Hoehe vs. Zahlentyp Korrelation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--keno-data",
        type=Path,
        default=project_root / "data" / "raw" / "keno" / "KENO_ab_2018.csv",
        help="Path to KENO draw data CSV",
    )
    parser.add_argument(
        "--gk1-data",
        type=Path,
        default=project_root / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv",
        help="Path to GK1 events CSV (10-9_KGDaten_gefiltert.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "results" / "hyp015_jackpot_correlation.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input files
    if not args.keno_data.exists():
        logger.error(f"KENO data file not found: {args.keno_data}")
        sys.exit(1)

    if not args.gk1_data.exists():
        logger.error(f"GK1 data file not found: {args.gk1_data}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("HYP-015: Jackpot-Hoehe vs. Zahlentyp Korrelation")
    logger.info("=" * 60)
    logger.info(f"KENO data: {args.keno_data}")
    logger.info(f"GK1 data:  {args.gk1_data}")
    logger.info(f"Output:    {args.output}")

    # Load KENO draw data
    logger.info("\nLoading KENO draw data...")
    loader = DataLoader()
    draws = loader.load(args.keno_data)
    logger.info(f"Loaded {len(draws)} KENO draws")

    # Run analysis
    logger.info("\nRunning HYP-015 analysis...")
    result = run_hyp015_analysis(draws, args.gk1_data)

    # Print results
    logger.info("\n" + "=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)

    corr = result.correlation
    logger.info(f"\nSample Sizes:")
    logger.info(f"  Jackpot draws: {corr.n_jackpot_draws}")
    logger.info(f"  Normal draws:  {corr.n_normal_draws}")
    logger.info(f"  Total draws:   {corr.n_total_draws}")

    logger.info(f"\nCorrelation (Birthday ratio vs Jackpot indicator):")
    logger.info(f"  Pearson r:     {corr.pearson_r:+.4f} (p={corr.pearson_p:.4f})")
    logger.info(f"  Spearman r:    {corr.spearman_r:+.4f} (p={corr.spearman_p:.4f})")

    logger.info(f"\nChi-Square Test (Birthday vs High distribution):")
    logger.info(f"  Chi2 stat:     {corr.chi_square_stat:.4f}")
    logger.info(f"  p-value:       {corr.chi_square_p:.4f}")
    logger.info(f"  DoF:           {corr.chi_square_dof}")

    logger.info(f"\nSignificance Assessment:")
    logger.info(f"  |r| > 0.2 met: {abs(corr.pearson_r) > 0.2}")
    logger.info(f"  p < 0.05 met:  {corr.pearson_p < 0.05}")
    logger.info(f"  Chi2 p < 0.05: {corr.chi_square_p < 0.05}")
    logger.info(f"  IS SIGNIFICANT: {corr.is_significant}")

    # Number type statistics
    logger.info(f"\nNumber Type Statistics:")
    logger.info(f"{'Category':<12} {'Jackpot':<10} {'Normal':<10} {'Diff':<10} {'Z-Score':<10}")
    logger.info("-" * 52)
    for stat in result.number_type_stats:
        if stat.category in ["birthday", "high", "even", "odd"]:
            logger.info(
                f"{stat.category:<12} {stat.jackpot_ratio:>9.4f} {stat.normal_ratio:>9.4f} "
                f"{stat.difference:>+9.4f} {stat.z_score:>+9.2f}"
            )

    # Decade statistics
    logger.info(f"\nDecade Distribution:")
    logger.info(f"{'Decade':<12} {'Jackpot':<10} {'Normal':<10} {'Diff':<10}")
    logger.info("-" * 42)
    for stat in result.number_type_stats:
        if stat.category.startswith("decade_"):
            decade_idx = int(stat.category.split("_")[1])
            decade_label = f"{decade_idx}0s" if decade_idx > 0 else "1-9"
            logger.info(
                f"{decade_label:<12} {stat.jackpot_ratio:>9.4f} {stat.normal_ratio:>9.4f} "
                f"{stat.difference:>+9.4f}"
            )

    # Export results
    logger.info(f"\nExporting results to {args.output}...")
    export_result_to_json(result, args.output)

    # Conclusion
    logger.info("\n" + "=" * 60)
    logger.info("CONCLUSION")
    logger.info("=" * 60)
    if corr.is_significant:
        logger.info(
            "SIGNIFICANT correlation found between jackpot events and number types."
        )
        if corr.pearson_r > 0:
            logger.info("Birthday numbers (1-31) appear MORE often during jackpots.")
        else:
            logger.info("Birthday numbers (1-31) appear LESS often during jackpots.")
    else:
        logger.info(
            "NO significant correlation found between jackpot events and number types."
        )
        logger.info("The distribution of birthday vs high numbers appears random.")

    logger.info(f"\nResults saved to: {args.output}")
    logger.info("Done.")

    return 0 if not corr.is_significant else 0  # Always success for completed analysis


if __name__ == "__main__":
    sys.exit(main())
