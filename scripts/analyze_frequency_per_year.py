#!/usr/bin/env python3
"""Analyse der Zahlenfrequenz pro Jahr.

Dieses Script berechnet die Haeufigkeit jeder KENO-Zahl (1-70)
fuer jedes Jahr im Datensatz. Ermoeglicht Year-over-Year
Stabilitaetsanalyse (Axiom A5).

Usage:
    python scripts/analyze_frequency_per_year.py
    python scripts/analyze_frequency_per_year.py --input data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_frequency_per_year.py --output results/custom_output.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.frequency import (
    YearlyFrequencyResult,
    calculate_frequency_per_year,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Berechnet Zahlenfrequenz pro Jahr fuer KENO-Daten."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2022_bereinigt.csv"),
        help="Pfad zur KENO CSV-Datei",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/frequency_per_year.json"),
        help="Pfad fuer JSON-Output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausfuehrliche Ausgabe",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load data
    if not args.input.exists():
        logger.error(f"Input-Datei nicht gefunden: {args.input}")
        return 1

    logger.info(f"Lade Daten aus: {args.input}")
    loader = DataLoader()
    draws = loader.load(args.input)
    logger.info(f"Geladen: {len(draws)} Ziehungen")

    if not draws:
        logger.error("Keine Ziehungen geladen!")
        return 1

    # Calculate per-year frequency
    logger.info("Berechne Frequenzen pro Jahr...")
    results = calculate_frequency_per_year(draws, number_range=(1, 70))

    # Prepare output structure
    output = {
        "metadata": {
            "source": str(args.input),
            "total_draws": len(draws),
            "years": sorted(results.keys()),
            "number_range": [1, 70],
        },
        "yearly_frequencies": {},
    }

    # Convert to serializable format
    for year, year_results in results.items():
        year_data = {
            "total_draws": year_results[0].total_draws if year_results else 0,
            "numbers": {},
        }
        for r in year_results:
            year_data["numbers"][r.number] = {
                "absolute": r.absolute_frequency,
                "relative": round(r.relative_frequency, 4),
            }
        output["yearly_frequencies"][year] = year_data

    # Add summary statistics
    output["summary"] = {}
    for year, year_results in results.items():
        if year_results:
            freqs = [r.absolute_frequency for r in year_results]
            total_counts = sum(freqs)
            expected_per_number = year_results[0].total_draws * 20 / 70
            output["summary"][year] = {
                "total_counts": total_counts,
                "expected_total": year_results[0].total_draws * 20,
                "counts_match": total_counts == year_results[0].total_draws * 20,
                "avg_frequency": round(sum(freqs) / len(freqs), 2),
                "expected_per_number": round(expected_per_number, 2),
                "min_frequency": min(freqs),
                "max_frequency": max(freqs),
            }

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Ergebnisse gespeichert: {args.output}")

    # Print summary
    print("\n=== Frequenz pro Jahr - Zusammenfassung ===\n")
    for year in sorted(results.keys()):
        year_results = results[year]
        if year_results:
            total_draws = year_results[0].total_draws
            freqs = [r.absolute_frequency for r in year_results]
            print(
                f"Jahr {year}: {total_draws:4d} Ziehungen, "
                f"avg freq: {sum(freqs)/len(freqs):5.1f}, "
                f"range: [{min(freqs):3d} - {max(freqs):3d}]"
            )

    print(f"\nOutput: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
