#!/usr/bin/env python
"""HYP-006: Wiederkehrende Gewinnzahlen (WGZ) Analyse.

Dieses Script analysiert wiederkehrende Muster in KENO-Ziehungen:
- Wiederholungsrate zwischen aufeinanderfolgenden Ziehungen
- GK1-Korrelation (Gewinnklasse 1)
- Paar-Stabilitaet ueber Zeit

Usage:
    python scripts/analyze_hyp006.py --config config/keno.yaml
    python scripts/analyze_hyp006.py --data-dir Keno_GPTs --output results/hyp006

Repro Command:
    python scripts/analyze_hyp006.py --config config/keno.yaml \
        --output results/hyp006/wgz_analysis.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.recurrence import (
    analyze_pair_stability,
    analyze_recurrence,
    calculate_gk1_correlation,
    generate_recurrence_report,
)
from kenobase.core.data_loader import DataLoader, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_gk1_dates(gk1_path: Path) -> list[datetime]:
    """Laedt GK1-Ereignisdaten aus CSV.

    Expected format: Datum,Keno-Typ,Anzahl der Gewinner,...
    """
    gk1_dates = []

    if not gk1_path.exists():
        logger.warning(f"GK1 file not found: {gk1_path}")
        return gk1_dates

    import csv

    with open(gk1_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date_str = row.get("Datum", "").strip()
                if date_str:
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                    gk1_dates.append(date)
            except (ValueError, KeyError) as e:
                logger.debug(f"Could not parse GK1 date: {e}")
                continue

    logger.info(f"Loaded {len(gk1_dates)} GK1 events from {gk1_path.name}")
    return gk1_dates


def main() -> int:
    """Hauptfunktion fuer HYP-006 Analyse."""
    parser = argparse.ArgumentParser(
        description="HYP-006: Wiederkehrende Gewinnzahlen (WGZ) Analyse",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config" / "default.yaml",
        help="Pfad zur Konfigurationsdatei",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "Keno_GPTs",
        help="Verzeichnis mit Daten-CSVs",
    )
    parser.add_argument(
        "--keno-file",
        type=str,
        default="10-9_KGDaten_gefiltert.csv",
        help="KENO-Ziehungsdaten CSV",
    )
    parser.add_argument(
        "--gk1-file",
        type=str,
        default="10-9_Liste_GK1_Treffer.csv",
        help="GK1-Ereignisse CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results" / "hyp006" / "wgz_analysis.json",
        help="Ausgabe-Pfad fuer Report",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=1,
        help="Lookback-Fenster fuer Wiederholungs-Check",
    )
    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=3,
        help="Mindest-Haeufigkeit fuer stabile Paare",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("HYP-006: Wiederkehrende Gewinnzahlen (WGZ) Analyse")
    logger.info("=" * 60)

    # Load KENO data
    keno_path = args.data_dir / args.keno_file
    if not keno_path.exists():
        # Try alternative data source
        alt_path = PROJECT_ROOT / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
        if alt_path.exists():
            keno_path = alt_path
            logger.info(f"Using alternative data source: {keno_path}")
        else:
            logger.error(f"KENO data file not found: {keno_path}")
            return 1

    logger.info(f"Loading KENO data from: {keno_path}")

    try:
        loader = DataLoader()
        draws = loader.load(keno_path, game_type=GameType.KENO)
        logger.info(f"Loaded {len(draws)} KENO draws")
    except Exception as e:
        logger.error(f"Failed to load KENO data: {e}")
        return 1

    if len(draws) < 10:
        logger.error("Insufficient data: need at least 10 draws")
        return 1

    # Load GK1 events - try data_dir first, then fallback to Keno_GPTs
    gk1_path = args.data_dir / args.gk1_file
    if not gk1_path.exists():
        gk1_path = PROJECT_ROOT / "Keno_GPTs" / args.gk1_file
    gk1_dates = load_gk1_dates(gk1_path)

    # Configure analysis
    config = {
        "window": args.window,
        "min_occurrences": args.min_occurrences,
        "min_streak": 3,
        "top_n": 50,
    }

    logger.info(f"Analysis config: {config}")

    # Run individual analyses for logging
    logger.info("-" * 40)
    logger.info("1. Recurrence Analysis")
    recurrence = analyze_recurrence(draws, window=config["window"])
    logger.info(f"   Total draws analyzed: {recurrence.total_draws}")
    logger.info(f"   Draws with recurrence: {recurrence.draws_with_recurrence}")
    logger.info(f"   Recurrence rate: {recurrence.recurrence_percentage:.1f}%")
    logger.info(f"   Avg recurrence count: {recurrence.avg_recurrence_count:.2f}")
    logger.info(f"   Max recurrence count: {recurrence.max_recurrence_count}")

    logger.info("-" * 40)
    logger.info("2. Pair Stability Analysis")
    pair_stability = analyze_pair_stability(
        draws,
        min_occurrences=config["min_occurrences"],
        top_n=config["top_n"],
    )
    logger.info(f"   Total pairs analyzed: {pair_stability.total_pairs_analyzed}")
    logger.info(f"   Stable pairs (>={config['min_occurrences']}): {len(pair_stability.stable_pairs)}")
    logger.info(f"   Stability score: {pair_stability.stability_score:.4f}")
    if pair_stability.top_pairs:
        logger.info("   Top 5 pairs:")
        for pair, count in pair_stability.top_pairs[:5]:
            logger.info(f"      {pair}: {count}x")

    if gk1_dates:
        logger.info("-" * 40)
        logger.info("3. GK1 Correlation Analysis")
        gk1_corr = calculate_gk1_correlation(draws, gk1_dates, window=config["window"])
        logger.info(f"   GK1 events found: {gk1_corr.total_gk1_events}")
        logger.info(f"   GK1 with prior recurrence: {gk1_corr.gk1_with_prior_recurrence}")
        logger.info(f"   Correlation rate: {gk1_corr.correlation_rate:.2%}")
        logger.info(f"   Baseline rate: {gk1_corr.baseline_recurrence_rate:.2%}")
        diff = gk1_corr.correlation_rate - gk1_corr.baseline_recurrence_rate
        logger.info(f"   Difference: {diff:+.2%}")

    # Generate full report
    logger.info("-" * 40)
    logger.info("Generating full report...")
    report = generate_recurrence_report(draws, gk1_dates, config)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Save report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Report saved to: {args.output}")

    # Summary
    logger.info("=" * 60)
    logger.info("SUMMARY - HYP-006 Acceptance Criteria")
    logger.info("=" * 60)
    for key, value in report["acceptance_criteria"].items():
        status = "PASS" if value else "FAIL"
        logger.info(f"  {key}: {status}")

    all_passed = all(report["acceptance_criteria"].values())
    if all_passed:
        logger.info("-" * 40)
        logger.info("ALL ACCEPTANCE CRITERIA PASSED")
    else:
        logger.warning("Some acceptance criteria failed - check report for details")

    return 0


if __name__ == "__main__":
    sys.exit(main())
