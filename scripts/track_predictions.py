#!/usr/bin/env python3
"""Kenobase Prediction Tracking CLI - Speichert und vergleicht Vorhersagen.

Usage:
    # Neue Vorhersage speichern (aus predict.py Output)
    python scripts/track_predictions.py save --numbers 1,5,17,23,45,67

    # Mit Tier-Klassifikation
    python scripts/track_predictions.py save --numbers 1,5,17,23,45,67 \\
        --tier-a 17,23 --tier-b 1,45 --tier-c 5,67

    # Vorhersage mit Ist-Ergebnis vergleichen
    python scripts/track_predictions.py compare --draw-id KENO-2025-12-28 \\
        --actuals 3,5,17,22,28,35,41,45,48,52,55,58,61,64,67,68,69,70,11,19

    # Alle Vorhersagen listen
    python scripts/track_predictions.py list

    # Aggregierte Statistiken anzeigen
    python scripts/track_predictions.py stats

    # Einzelne Vorhersage anzeigen
    python scripts/track_predictions.py show --draw-id KENO-2025-12-28
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

from kenobase.prediction.storage import (
    Prediction,
    PredictionStorage,
    generate_draw_id,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_numbers(numbers_str: str) -> list[int]:
    """Parst komma-separierte Zahlen.

    Args:
        numbers_str: String wie "1,5,17,23"

    Returns:
        Liste von Integers
    """
    if not numbers_str:
        return []
    return [int(n.strip()) for n in numbers_str.split(",") if n.strip()]


def cmd_save(args: argparse.Namespace, storage: PredictionStorage) -> int:
    """Speichert eine neue Vorhersage."""
    numbers = parse_numbers(args.numbers)
    if not numbers:
        print("Fehler: Keine Zahlen angegeben (--numbers)")
        return 1

    draw_id = args.draw_id or generate_draw_id(args.game_type)

    tier_predictions = {}
    if args.tier_a:
        tier_predictions["A"] = parse_numbers(args.tier_a)
    if args.tier_b:
        tier_predictions["B"] = parse_numbers(args.tier_b)
    if args.tier_c:
        tier_predictions["C"] = parse_numbers(args.tier_c)

    prediction = Prediction(
        draw_id=draw_id,
        numbers=numbers,
        tier_predictions=tier_predictions,
        mode=args.mode,
        config={
            "game_type": args.game_type,
            "source": "track_predictions.py",
        },
    )

    path = storage.save_prediction(prediction)

    print("=" * 60)
    print("VORHERSAGE GESPEICHERT")
    print("=" * 60)
    print(f"Draw ID:     {draw_id}")
    print(f"Zeitpunkt:   {prediction.prediction_time.isoformat()}")
    print(f"Zahlen:      {', '.join(map(str, numbers))}")
    if tier_predictions:
        print(f"Tier A:      {', '.join(map(str, tier_predictions.get('A', [])))}")
        print(f"Tier B:      {', '.join(map(str, tier_predictions.get('B', [])))}")
        print(f"Tier C:      {', '.join(map(str, tier_predictions.get('C', [])))}")
    print(f"Modus:       {args.mode}")
    print(f"Datei:       {path}")
    print("=" * 60)

    return 0


def cmd_compare(args: argparse.Namespace, storage: PredictionStorage) -> int:
    """Vergleicht Vorhersage mit Ist-Ergebnis."""
    if not args.draw_id:
        print("Fehler: --draw-id erforderlich")
        return 1

    actuals = parse_numbers(args.actuals)
    if not actuals:
        print("Fehler: --actuals erforderlich (20 Zahlen fuer KENO)")
        return 1

    metrics = storage.compare_and_update(args.draw_id, actuals)

    if not metrics:
        print(f"Fehler: Vorhersage nicht gefunden: {args.draw_id}")
        return 1

    prediction = storage.load_prediction(args.draw_id)

    print("=" * 60)
    print("VERGLEICH ABGESCHLOSSEN")
    print("=" * 60)
    print(f"Draw ID:     {args.draw_id}")
    print(f"Vorhersage:  {', '.join(map(str, prediction.numbers))}")
    print(f"Ist-Zahlen:  {', '.join(map(str, actuals[:10]))}...")
    print("-" * 60)
    print(f"TREFFER:     {metrics.hits} von {len(prediction.numbers)}")
    print(f"Hit Rate:    {metrics.hit_rate:.1%}")
    print(f"Precision:   {metrics.precision:.1%}")

    if metrics.tier_accuracy:
        print("-" * 60)
        print("Tier-Genauigkeit:")
        for tier, accuracy in sorted(metrics.tier_accuracy.items()):
            tier_nums = prediction.tier_predictions.get(tier, [])
            tier_hits = int(accuracy * len(tier_nums))
            print(f"  Tier {tier}: {tier_hits}/{len(tier_nums)} ({accuracy:.1%})")

    print("=" * 60)

    return 0


def cmd_list(args: argparse.Namespace, storage: PredictionStorage) -> int:
    """Listet alle gespeicherten Vorhersagen."""
    draw_ids = storage.list_predictions()

    if not draw_ids:
        print("Keine Vorhersagen gefunden.")
        return 0

    print("=" * 60)
    print("GESPEICHERTE VORHERSAGEN")
    print("=" * 60)
    print(f"{'Draw ID':<25} {'Zahlen':<20} {'Treffer':<10} {'Status'}")
    print("-" * 60)

    for draw_id in draw_ids:
        pred = storage.load_prediction(draw_id)
        if pred:
            nums_str = ", ".join(map(str, pred.numbers[:4])) + "..."
            if pred.metrics:
                hits_str = f"{pred.metrics.hits}/{len(pred.numbers)}"
                status = "AUSGEWERTET"
            else:
                hits_str = "-"
                status = "OFFEN"
            print(f"{draw_id:<25} {nums_str:<20} {hits_str:<10} {status}")

    print("-" * 60)
    print(f"Gesamt: {len(draw_ids)} Vorhersagen")
    print("=" * 60)

    return 0


def cmd_show(args: argparse.Namespace, storage: PredictionStorage) -> int:
    """Zeigt eine einzelne Vorhersage im Detail."""
    if not args.draw_id:
        print("Fehler: --draw-id erforderlich")
        return 1

    prediction = storage.load_prediction(args.draw_id)

    if not prediction:
        print(f"Fehler: Vorhersage nicht gefunden: {args.draw_id}")
        return 1

    print("=" * 60)
    print("VORHERSAGE DETAILS")
    print("=" * 60)
    print(f"Draw ID:     {prediction.draw_id}")
    print(f"Zeitpunkt:   {prediction.prediction_time.isoformat()}")
    print(f"Modus:       {prediction.mode}")
    print(f"Zahlen:      {', '.join(map(str, prediction.numbers))}")

    if prediction.tier_predictions:
        print("-" * 60)
        print("Tier-Klassifikation:")
        for tier in ["A", "B", "C"]:
            nums = prediction.tier_predictions.get(tier, [])
            if nums:
                print(f"  Tier {tier}: {', '.join(map(str, nums))}")

    if prediction.actuals:
        print("-" * 60)
        print(f"Ist-Zahlen:  {', '.join(map(str, prediction.actuals))}")

    if prediction.metrics:
        print("-" * 60)
        print("Metriken:")
        print(f"  Treffer:   {prediction.metrics.hits}")
        print(f"  Hit Rate:  {prediction.metrics.hit_rate:.1%}")
        print(f"  Precision: {prediction.metrics.precision:.1%}")
        if prediction.metrics.tier_accuracy:
            print("  Tier-Genauigkeit:")
            for tier, accuracy in sorted(prediction.metrics.tier_accuracy.items()):
                print(f"    Tier {tier}: {accuracy:.1%}")

    if args.json:
        print("-" * 60)
        print("JSON:")
        print(json.dumps(prediction.to_dict(), indent=2, ensure_ascii=False))

    print("=" * 60)

    return 0


def cmd_stats(args: argparse.Namespace, storage: PredictionStorage) -> int:
    """Zeigt aggregierte Statistiken."""
    stats = storage.get_aggregate_metrics(only_evaluated=not args.all)

    print("=" * 60)
    print("AGGREGIERTE STATISTIKEN")
    print("=" * 60)

    if stats.get("count", 0) == 0:
        print("Keine Vorhersagen gefunden.")
        return 0

    print(f"Vorhersagen gesamt:    {stats['count']}")
    print(f"Ausgewertet:           {stats['evaluated']}")
    print("-" * 60)
    print(f"Treffer gesamt:        {stats['total_hits']}")
    print(f"Durchschn. Treffer:    {stats['avg_hits']:.2f}")
    print(f"Durchschn. Precision:  {stats['avg_precision']:.1%}")
    print(f"Durchschn. Hit Rate:   {stats['avg_hit_rate']:.1%}")

    if stats.get("tier_precision"):
        print("-" * 60)
        print("Precision pro Tier:")
        for tier, precision in sorted(stats["tier_precision"].items()):
            print(f"  Tier {tier}: {precision:.1%}")

    print("=" * 60)

    if args.json:
        print("\nJSON:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    return 0


def main() -> int:
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="Kenobase Prediction Tracking - Speichert und vergleicht Vorhersagen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--storage-dir",
        type=str,
        default="results/predictions",
        help="Pfad zum Speicherverzeichnis (default: results/predictions)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfuegbare Befehle")

    # save command
    save_parser = subparsers.add_parser("save", help="Speichert neue Vorhersage")
    save_parser.add_argument(
        "--numbers",
        type=str,
        required=True,
        help="Vorhergesagte Zahlen (komma-separiert)",
    )
    save_parser.add_argument(
        "--draw-id",
        type=str,
        help="Draw ID (default: KENO-YYYY-MM-DD)",
    )
    save_parser.add_argument(
        "--game-type",
        type=str,
        default="KENO",
        help="Spieltyp (default: KENO)",
    )
    save_parser.add_argument(
        "--mode",
        type=str,
        default="rule_based",
        choices=["rule_based", "ensemble"],
        help="Vorhersage-Modus (default: rule_based)",
    )
    save_parser.add_argument("--tier-a", type=str, help="Tier A Zahlen")
    save_parser.add_argument("--tier-b", type=str, help="Tier B Zahlen")
    save_parser.add_argument("--tier-c", type=str, help="Tier C Zahlen")

    # compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Vergleicht Vorhersage mit Ist-Ergebnis"
    )
    compare_parser.add_argument(
        "--draw-id",
        type=str,
        required=True,
        help="Draw ID der Vorhersage",
    )
    compare_parser.add_argument(
        "--actuals",
        type=str,
        required=True,
        help="Tatsaechliche Zahlen (komma-separiert)",
    )

    # list command
    list_parser = subparsers.add_parser("list", help="Listet alle Vorhersagen")

    # show command
    show_parser = subparsers.add_parser("show", help="Zeigt Vorhersage im Detail")
    show_parser.add_argument(
        "--draw-id",
        type=str,
        required=True,
        help="Draw ID der Vorhersage",
    )
    show_parser.add_argument(
        "--json",
        action="store_true",
        help="Zeigt auch JSON-Ausgabe",
    )

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Zeigt aggregierte Statistiken")
    stats_parser.add_argument(
        "--all",
        action="store_true",
        help="Inkludiert auch nicht-ausgewertete Vorhersagen",
    )
    stats_parser.add_argument(
        "--json",
        action="store_true",
        help="Zeigt auch JSON-Ausgabe",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    storage = PredictionStorage(storage_dir=args.storage_dir)

    commands = {
        "save": cmd_save,
        "compare": cmd_compare,
        "list": cmd_list,
        "show": cmd_show,
        "stats": cmd_stats,
    }

    return commands[args.command](args, storage)


if __name__ == "__main__":
    sys.exit(main())
