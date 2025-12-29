#!/usr/bin/env python3
"""Kenobase Sum Windows Analysis Script.

Analysiert die Summen-Verteilung von KENO-Ziehungen.

Hypothese: Summenwerte clustern in bestimmten Fenstern
(z.B. [140-170] und [190-220]).

KENO-Kontext:
- 20 Zahlen werden aus [1,70] gezogen
- Erwartungswert: E[sum] = 20 * (1+70)/2 = 710
- Theoretische Std: ~58

Usage:
    python scripts/analyze_sum_windows.py --data data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_sum_windows.py --data data/raw/keno/KENO_ab_2018.csv --plot
    python scripts/analyze_sum_windows.py --help
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Projekt-Root zum Pfad hinzufuegen
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.sum_distribution import (
    SumDistributionResult,
    export_result_to_json,
    plot_sum_distribution,
    run_sum_window_analysis,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_result(result: SumDistributionResult) -> str:
    """Formatiert Ergebnis fuer Konsolen-Output.

    Args:
        result: SumDistributionResult

    Returns:
        Formatierter String
    """
    lines = [
        "=" * 60,
        "KENO Sum Distribution Analysis",
        "=" * 60,
        "",
        f"Data Source: {result.data_source}",
        f"Total Draws: {result.total_draws:,}",
        f"Analysis Date: {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "-" * 40,
        "Summary Statistics",
        "-" * 40,
        f"  Observed Mean:   {result.sum_mean:.2f}",
        f"  Expected Mean:   {result.expected_mean:.2f}",
        f"  Deviation:       {result.sum_mean - result.expected_mean:+.2f}",
        f"  Std Deviation:   {result.sum_std:.2f}",
        f"  Min Sum:         {result.sum_min}",
        f"  Max Sum:         {result.sum_max}",
        f"  Range:           {result.sum_max - result.sum_min}",
        "",
        "-" * 40,
        "Chi-Square Test (vs Uniform)",
        "-" * 40,
        f"  Statistic:       {result.chi_square.statistic:.4f}",
        f"  p-value:         {result.chi_square.p_value:.6f}",
        f"  DoF:             {result.chi_square.degrees_of_freedom}",
        f"  Significant:     {'YES' if result.chi_square.is_significant else 'NO'}",
        "",
    ]

    if result.clusters:
        lines.extend(
            [
                "-" * 40,
                f"Detected Clusters ({len(result.clusters)})",
                "-" * 40,
            ]
        )
        for i, c in enumerate(result.clusters, 1):
            lines.extend(
                [
                    f"  Cluster {i}:",
                    f"    Range:     [{c.range_min} - {c.range_max}]",
                    f"    Center:    {c.center:.1f}",
                    f"    Density:   {c.density:.2%}",
                    f"    Z-Score:   {c.z_score:+.2f}",
                ]
            )
    else:
        lines.extend(
            [
                "-" * 40,
                "No significant clusters detected",
                "-" * 40,
            ]
        )

    lines.extend(
        [
            "",
            "-" * 40,
            "Histogram (Top 10 Bins)",
            "-" * 40,
        ]
    )

    # Top 10 Bins nach Count
    sorted_bins = sorted(result.histogram, key=lambda h: h.count, reverse=True)[:10]
    for h in sorted_bins:
        bar = "#" * int(h.frequency * 100)
        lines.append(f"  [{h.bin_start:4d}-{h.bin_end:4d}]: {h.count:5d} ({h.frequency:5.2%}) {bar}")

    lines.extend(
        [
            "",
            "=" * 60,
        ]
    )

    return "\n".join(lines)


def main() -> int:
    """Hauptfunktion des Scripts.

    Returns:
        Exit-Code (0 = Erfolg)
    """
    parser = argparse.ArgumentParser(
        description="Analyze KENO sum distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO CSV file (default: data/raw/keno/KENO_ab_2018.csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="results/sum_windows_analysis.json",
        help="Output JSON path (default: results/sum_windows_analysis.json)",
    )
    parser.add_argument(
        "--bin-width",
        type=int,
        default=20,
        help="Histogram bin width (default: 20)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate histogram plot",
    )
    parser.add_argument(
        "--plot-path",
        type=str,
        default="results/sum_windows_histogram.png",
        help="Plot output path (default: results/sum_windows_histogram.png)",
    )
    parser.add_argument(
        "--show-plot",
        action="store_true",
        help="Show plot interactively",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress console output",
    )

    args = parser.parse_args()

    # Pfade relativ zum Projekt-Root
    data_path = PROJECT_ROOT / args.data
    output_path = PROJECT_ROOT / args.output

    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    logger.info(f"Starting sum window analysis on {data_path}")

    # Analyse durchfuehren
    result = run_sum_window_analysis(
        data_path=data_path,
        bin_width=args.bin_width,
        output_path=output_path,
    )

    if result.total_draws == 0:
        logger.error("No draws loaded - check data file")
        return 1

    # Konsolen-Output
    if not args.quiet:
        print(format_result(result))

    # Plot generieren
    if args.plot or args.show_plot:
        plot_path = PROJECT_ROOT / args.plot_path if args.plot else None
        plot_sum_distribution(result, output_path=plot_path, show=args.show_plot)

    logger.info(f"Analysis complete. Results saved to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
