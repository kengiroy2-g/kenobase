#!/usr/bin/env python
"""HYP-014 Mehrwochenschein Jackpot-Timing Analyse Script.

Analysiert ob Jackpot-Treffer systematisch zu bestimmten Zeitpunkten
innerhalb von Abo-Perioden (Mehrwochenscheine) auftreten.

Usage:
    python scripts/analyze_hyp014.py
    python scripts/analyze_hyp014.py --data-path data/10-9_KGDaten_gefiltert.csv
    python scripts/analyze_hyp014.py --output results/hyp014_multiweek_timing.json
    python scripts/analyze_hyp014.py --n-simulations 50000 --seed 123
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.multiweek_timing import (
    MultiweekTimingResult,
    SimulationConfig,
    analyze_multiweek_timing,
    export_result_to_json,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_jackpot_dates(data_path: Path) -> list[datetime]:
    """Laedt Jackpot-Daten aus CSV.

    Args:
        data_path: Pfad zur GK1Summary CSV-Datei

    Returns:
        Liste der Jackpot-Daten (datetime)
    """
    loader = DataLoader()
    data = loader.load(data_path)

    # Extrahiere Daten
    dates = [record.datum for record in data if hasattr(record, "datum")]
    logger.info(f"Loaded {len(dates)} jackpot dates from {data_path.name}")

    return dates


def print_summary(result: MultiweekTimingResult) -> None:
    """Druckt Zusammenfassung der Analyse."""
    print("\n" + "=" * 70)
    print("HYP-014: MEHRWOCHENSCHEIN JACKPOT-TIMING ANALYSE")
    print("=" * 70)
    print(f"Analyse-Datum: {result.analysis_date}")
    print(f"Datenquelle: {result.data_source}")
    print(f"Anzahl Jackpots: {result.n_jackpots}")
    print(f"Zeitraum: {result.date_range_start} - {result.date_range_end}")
    print()

    # Monte-Carlo Konfiguration
    print("-" * 35)
    print("MONTE-CARLO KONFIGURATION")
    print("-" * 35)
    print(f"  Simulationen: {result.simulation_config.n_simulations}")
    print(f"  Random Seed:  {result.simulation_config.random_seed}")
    print(f"  Abo-Laengen:  {result.simulation_config.abo_lengths}")
    print()

    # Ergebnisse pro Abo-Laenge
    for i, abo_length in enumerate(result.simulation_config.abo_lengths):
        print("-" * 35)
        print(f"ABO-LAENGE: {abo_length} TAGE")
        print("-" * 35)

        # Distribution
        if i < len(result.distributions):
            dist = result.distributions[i]
            print(f"  Anzahl Jackpots:      {dist.n_jackpots}")
            print(f"  Mittlere Position:    {dist.mean_position_ratio:.4f}")
            print(f"  Std Position:         {dist.std_position_ratio:.4f}")
            print(f"  Position-Verteilung:")
            for label, count in zip(dist.position_labels, dist.position_counts):
                print(f"    {label}: {count}")

        # Chi-Quadrat Test
        if i < len(result.chi2_results):
            chi2 = result.chi2_results[i]
            status = "UNIFORM" if chi2.is_uniform else "NICHT UNIFORM"
            print(f"\n  Chi-Quadrat Test:")
            print(f"    Teststatistik: {chi2.chi2_statistic:.4f}")
            print(f"    p-Wert:        {chi2.p_value:.6f}")
            print(f"    Ergebnis:      {status}")

        # Monte-Carlo Vergleich
        if i < len(result.mc_comparisons):
            mc = result.mc_comparisons[i]
            status = "SIGNIFIKANT" if mc.is_significant else "NICHT SIGNIFIKANT"
            print(f"\n  Monte-Carlo Vergleich:")
            print(f"    Beobachtet:    {mc.observed_mean_ratio:.4f}")
            print(f"    Simuliert:     {mc.simulated_mean_ratio:.4f} +/- {mc.simulated_std_ratio:.4f}")
            print(f"    Z-Score:       {mc.z_score:.4f}")
            print(f"    p-Wert (MC):   {mc.p_value_mc:.6f}")
            print(f"    Ergebnis:      {status}")

        print()

    # Gesamtergebnis
    print("=" * 70)
    print("HYPOTHESEN-ERGEBNIS")
    print("=" * 70)
    print(f"\nVerdict: {result.verdict}")
    print(f"Konfidenz: {result.confidence:.0%}")

    if result.verdict == "NICHT_BESTAETIGT":
        print("\nInterpretation: Jackpot-Positionen innerhalb von Abo-Perioden")
        print("erscheinen zufaellig verteilt. Keine Hinweise auf systematische")
        print("Timing-Manipulation bei Mehrwochenscheinen.")
    elif result.verdict == "BESTAETIGT":
        print("\nInterpretation: Signifikante Abweichung von Zufallsverteilung!")
        print("Jackpot-Treffer koennten systematisch zu bestimmten Zeitpunkten")
        print("innerhalb von Abo-Perioden auftreten.")
    else:
        print("\nInterpretation: Ergebnis unklar. Weitere Untersuchung erforderlich.")

    status = "ERFUELLT" if result.acceptance_criteria_met else "NICHT ERFUELLT"
    print(f"\nAcceptance Criteria (p > 0.05): {status}")
    print("=" * 70)


def main() -> int:
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="HYP-014: Mehrwochenschein Jackpot-Timing Analyse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/10-9_KGDaten_gefiltert.csv",
        help="Pfad zur GK1Summary CSV-Datei",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="results/hyp014_multiweek_timing.json",
        help="Pfad zur Ausgabe-JSON-Datei",
    )
    parser.add_argument(
        "--n-simulations",
        type=int,
        default=10000,
        help="Anzahl Monte-Carlo Simulationen (default: 10000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random Seed fuer Reproduzierbarkeit (default: 42)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Signifikanzniveau (default: 0.05)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Nur JSON-Output, keine Konsolenausgabe",
    )

    args = parser.parse_args()

    # Pruefe ob Daten existieren
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Datei nicht gefunden: {data_path}")
        logger.info("Verfuegbare Dateien in data/:")
        data_dir = Path("data")
        if data_dir.exists():
            for f in sorted(data_dir.glob("*.csv")):
                logger.info(f"  - {f.name}")
        sys.exit(1)

    # Lade Daten
    logger.info(f"Starte HYP-014 Analyse mit Daten aus {data_path}")
    jackpot_dates = load_jackpot_dates(data_path)

    if not jackpot_dates:
        logger.error("Keine Jackpot-Daten gefunden!")
        sys.exit(1)

    # Konfiguriere Simulation
    config = SimulationConfig(
        n_simulations=args.n_simulations,
        random_seed=args.seed,
    )

    # Fuehre Analyse durch
    try:
        result = analyze_multiweek_timing(
            jackpot_dates,
            simulation_config=config,
            alpha=args.alpha,
        )
        result.data_source = str(data_path)

        # Speichere JSON
        output_path = Path(args.output)
        export_result_to_json(result, output_path)
        logger.info(f"Ergebnis gespeichert: {output_path}")

        # Drucke Zusammenfassung
        if not args.quiet:
            print_summary(result)

        # Return-Code basierend auf Acceptance Criteria
        return 0 if result.acceptance_criteria_met else 1

    except Exception as e:
        logger.error(f"Analyse fehlgeschlagen: {e}")
        raise


if __name__ == "__main__":
    sys.exit(main())
