#!/usr/bin/env python
"""CLI Script fuer Langzeit-Zahlen-Balance Analyse (TASK-R05).

Analysiert die Balance aller KENO-Zahlen und erkennt Trigger-Ereignisse
fuer potenzielle Mean-Reversion.

Usage:
    python scripts/analyze_longterm_balance.py --data data/KENO_Stats_ab-2018.csv
    python scripts/analyze_longterm_balance.py --data data/KENO_Stats_ab-2018.csv --window 1000
    python scripts/analyze_longterm_balance.py --data data/KENO_Stats_ab-2018.csv --output results/balance.json

Example Output:
    Langzeit-Balance Analyse (TASK-R05)
    ====================================
    Zeitfenster: 500 Ziehungen
    Unterrepraesentiert: 12 Zahlen
    Ueberrepraesentiert: 8 Zahlen

    Aktive Trigger (2.0 std):
    - Zahl 42: REVERSION_UP (-2.34 std, Konfidenz: 68%)
    - Zahl 17: REVERSION_DOWN (+2.15 std, Konfidenz: 63%)
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

from kenobase.core.data_loader import DataLoader, GameType
from kenobase.analysis.longterm_balance import (
    analyze_longterm_balance,
    generate_longterm_balance_report,
)


def setup_logging(verbose: bool = False) -> None:
    """Konfiguriert Logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="Langzeit-Zahlen-Balance Analyse (TASK-R05)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --data data/KENO_Stats_ab-2018.csv
  %(prog)s --data data/KENO_Stats_ab-2018.csv --window 1000
  %(prog)s --data data/KENO_Stats_ab-2018.csv --output results/longterm_balance.json
        """,
    )

    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Pfad zur KENO-Daten CSV-Datei",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=500,
        help="Analyse-Fenster (Anzahl Ziehungen, default: 500)",
    )
    parser.add_argument(
        "--balance-threshold",
        type=float,
        default=0.1,
        help="Schwellwert fuer Balance-Klassifikation (default: 0.1 = 10%%)",
    )
    parser.add_argument(
        "--trigger-threshold",
        type=float,
        default=2.0,
        help="Schwellwert fuer Trigger in Standardabweichungen (default: 2.0)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Ausgabe-Pfad fuer JSON-Report (optional)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausfuehrliche Ausgabe",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validiere Input
    if not args.data.exists():
        logger.error(f"Datei nicht gefunden: {args.data}")
        return 1

    # Lade Daten
    logger.info(f"Lade Daten aus {args.data}...")
    loader = DataLoader()
    try:
        draws = loader.load(args.data, game_type=GameType.KENO)
    except Exception as e:
        logger.error(f"Fehler beim Laden: {e}")
        return 1

    if len(draws) < args.window:
        logger.error(
            f"Nicht genuegend Daten: {len(draws)} Ziehungen (minimum: {args.window})"
        )
        return 1

    logger.info(f"Geladen: {len(draws)} Ziehungen")

    # Analysiere Balance
    logger.info(f"Analysiere Balance (Fenster: {args.window} Ziehungen)...")
    result = analyze_longterm_balance(
        draws,
        window=args.window,
        balance_threshold=args.balance_threshold,
        trigger_threshold_std=args.trigger_threshold,
    )

    # Ausgabe
    print()
    print("Langzeit-Balance Analyse (TASK-R05)")
    print("=" * 40)
    print(f"Zeitfenster: {result.window} Ziehungen")
    print(f"Erwartete Frequenz: {result.expected_frequency:.4f} ({result.expected_frequency * result.window:.1f} pro Zahl)")
    print()
    print(f"Unterrepraesentiert: {result.underrepresented_count} Zahlen")
    print(f"Ueberrepraesentiert: {result.overrepresented_count} Zahlen")
    print(f"Normal: {70 - result.underrepresented_count - result.overrepresented_count} Zahlen")
    print(f"Durchschnittliche Abweichung: {result.mean_absolute_deviation:.1%}")
    print()

    # Top unterrepraesentiert
    under = [s for s in result.number_stats if s.classification == "underrepresented"]
    if under:
        print("Top 5 unterrepraesentierte Zahlen:")
        for s in under[:5]:
            print(
                f"  Zahl {s.number:2d}: {s.balance_score:+.1%} "
                f"({s.observed_count}/{s.expected_count:.0f} erwartet, "
                f"{s.deviation_std:+.2f} std)"
            )
        print()

    # Top ueberrepraesentiert
    over = [s for s in reversed(result.number_stats) if s.classification == "overrepresented"]
    if over:
        print("Top 5 ueberrepraesentierte Zahlen:")
        for s in list(over)[:5]:
            print(
                f"  Zahl {s.number:2d}: {s.balance_score:+.1%} "
                f"({s.observed_count}/{s.expected_count:.0f} erwartet, "
                f"{s.deviation_std:+.2f} std)"
            )
        print()

    # Trigger
    if result.triggers:
        print(f"Aktive Trigger ({args.trigger_threshold} std):")
        for t in result.triggers[:10]:
            print(
                f"  Zahl {t.number:2d}: {t.trigger_type:15s} "
                f"({t.deviation_std:+.2f} std, Konfidenz: {t.confidence:.0%})"
            )
        if len(result.triggers) > 10:
            print(f"  ... und {len(result.triggers) - 10} weitere")
    else:
        print(f"Keine aktiven Trigger (Schwellwert: {args.trigger_threshold} std)")
    print()

    # Report speichern
    if args.output:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "window": args.window,
            "balance_threshold": args.balance_threshold,
            "trigger_threshold_std": args.trigger_threshold,
        }
        report = generate_longterm_balance_report(draws, args.window, config)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Report gespeichert: {output_path}")
        print(f"Report gespeichert: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
