#!/usr/bin/env python
"""HYP-002 GK1 Wartezeit-Analyse Script.

Analysiert die Verteilung der Wartezeiten zwischen GK1 Treffern.
Testet ob Jackpot-Bildungs-Zyklen existieren.

Usage:
    python scripts/analyze_hyp002.py
    python scripts/analyze_hyp002.py --data-path data/10-9_KGDaten_gefiltert.csv
    python scripts/analyze_hyp002.py --output results/hyp002_gk1_waiting.json
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.gk1_waiting import (
    run_hyp002_waiting_analysis,
    GK1WaitingResult,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_summary(result: GK1WaitingResult) -> None:
    """Druckt Zusammenfassung der Analyse."""
    print("\n" + "=" * 70)
    print("HYP-002: GK1 WARTEZEIT-ANALYSE")
    print("=" * 70)
    print(f"Analyse-Datum: {result.analysis_date}")
    print(f"Datenquelle: {result.data_source}")
    print()

    # Keno-9 Ergebnisse
    if result.stats_keno9:
        print("-" * 35)
        print("KENO-TYP 9")
        print("-" * 35)
        s = result.stats_keno9
        print(f"  Anzahl GK1-Ereignisse: {s.n_events}")
        print(f"  Mittlere Wartezeit:    {s.mean_days:.1f} Tage")
        print(f"  Standardabweichung:    {s.std_days:.1f} Tage")
        print(f"  Median:                {s.median_days:.1f} Tage")
        print(f"  Min/Max:               {s.min_days} / {s.max_days} Tage")
        print(f"  Variationskoeffizient: {s.cv:.4f}")

        if result.chi2_keno9:
            c = result.chi2_keno9
            status = "UNIFORM" if c.is_uniform else "NICHT UNIFORM"
            print(f"\n  Chi-Quadrat Test:")
            print(f"    Teststatistik: {c.chi2_statistic:.4f}")
            print(f"    p-Wert:        {c.p_value:.6f}")
            print(f"    Ergebnis:      {status}")

        if result.outliers_keno9:
            o = result.outliers_keno9
            print(f"\n  Outlier-Analyse:")
            print(f"    Anzahl Outlier:    {o.n_outliers}")
            print(f"    Schwellwert:       {o.outlier_threshold:.1f} Tage")
            if o.outlier_values:
                print(f"    Outlier-Werte:     {o.outlier_values[:5]}...")
    print()

    # Keno-10 Ergebnisse
    if result.stats_keno10:
        print("-" * 35)
        print("KENO-TYP 10")
        print("-" * 35)
        s = result.stats_keno10
        print(f"  Anzahl GK1-Ereignisse: {s.n_events}")
        print(f"  Mittlere Wartezeit:    {s.mean_days:.1f} Tage")
        print(f"  Standardabweichung:    {s.std_days:.1f} Tage")
        print(f"  Median:                {s.median_days:.1f} Tage")
        print(f"  Min/Max:               {s.min_days} / {s.max_days} Tage")
        print(f"  Variationskoeffizient: {s.cv:.4f}")

        if result.chi2_keno10:
            c = result.chi2_keno10
            status = "UNIFORM" if c.is_uniform else "NICHT UNIFORM"
            print(f"\n  Chi-Quadrat Test:")
            print(f"    Teststatistik: {c.chi2_statistic:.4f}")
            print(f"    p-Wert:        {c.p_value:.6f}")
            print(f"    Ergebnis:      {status}")

        if result.outliers_keno10:
            o = result.outliers_keno10
            print(f"\n  Outlier-Analyse:")
            print(f"    Anzahl Outlier:    {o.n_outliers}")
            print(f"    Schwellwert:       {o.outlier_threshold:.1f} Tage")
            if o.outlier_values:
                print(f"    Outlier-Werte:     {o.outlier_values[:5]}...")
    print()

    # Gesamtergebnis
    print("=" * 70)
    print("HYPOTHESEN-ERGEBNIS")
    print("=" * 70)
    print(f"\n{result.hypothesis_result}")
    print()
    status = "ERFUELLT" if result.acceptance_criteria_met else "NICHT ERFUELLT"
    print(f"Acceptance Criteria (p > 0.05): {status}")
    print("=" * 70)


def main():
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="HYP-002: GK1 Wartezeit-Analyse",
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
        default="results/hyp002_gk1_waiting.json",
        help="Pfad zur Ausgabe-JSON-Datei",
    )
    parser.add_argument(
        "--n-bins",
        type=int,
        default=10,
        help="Anzahl Bins fuer Histogramm und Chi-Quadrat Test",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Signifikanzniveau fuer Chi-Quadrat Test",
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

    # Fuehre Analyse durch
    logger.info(f"Starte HYP-002 Analyse mit Daten aus {data_path}")

    try:
        from kenobase.analysis.gk1_waiting import analyze_gk1_waiting, export_result_to_json

        result = analyze_gk1_waiting(
            data_path=data_path,
            n_bins=args.n_bins,
            alpha=args.alpha,
        )

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
