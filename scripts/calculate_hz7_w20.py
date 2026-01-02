#!/usr/bin/env python3
"""
Calculate HZ7 W20 and HZ6 W20 Hot-Zone numbers.

This script calculates the 7 (or 6) most frequent numbers from the last 20 KENO draws.
Based on validated strategy from VALIDIERTE_FAKTEN.md:
- HZ7 W20 had 69 jackpots in 32 months (2022-2024)
- ROI: +413%
- Success rate: 75%

Usage:
    python scripts/calculate_hz7_w20.py
    python scripts/calculate_hz7_w20.py --window 20 --top 7
    python scripts/calculate_hz7_w20.py --data-file path/to/keno.csv

Source: AI_COLLABORATION/KNOWLEDGE_BASE/VALIDIERTE_FAKTEN.md
"""

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
import sys


def load_keno_data(file_path: Path) -> list[tuple[datetime, list[int]]]:
    """
    Load KENO draw data from CSV file.

    Args:
        file_path: Path to the CSV file with KENO data

    Returns:
        List of (date, numbers) tuples, sorted by date descending (newest first)
    """
    draws = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split(';')
        if len(parts) < 21:
            continue

        try:
            # Parse date (DD.MM.YYYY format)
            date_str = parts[0]
            date = datetime.strptime(date_str, '%d.%m.%Y')

            # Parse numbers (columns 1-20)
            numbers = []
            for i in range(1, 21):
                numbers.append(int(parts[i]))

            draws.append((date, numbers))
        except (ValueError, IndexError):
            continue

    # Sort by date descending (newest first)
    draws.sort(key=lambda x: x[0], reverse=True)

    return draws


def calculate_hot_zone(
    draws: list[tuple[datetime, list[int]]],
    window: int = 20,
    top_n: int = 7
) -> tuple[list[int], dict[int, int], datetime, datetime]:
    """
    Calculate Hot-Zone numbers from the last N draws.

    Args:
        draws: List of (date, numbers) tuples
        window: Number of recent draws to analyze (default: 20)
        top_n: Number of top numbers to return (default: 7)

    Returns:
        Tuple of (hot_zone_numbers, frequency_dict, oldest_date, newest_date)
    """
    if len(draws) < window:
        print(f"WARNUNG: Nur {len(draws)} Ziehungen verfuegbar, {window} angefordert.")
        window = len(draws)

    # Take the most recent 'window' draws
    recent_draws = draws[:window]

    # Count frequency of each number
    counter: Counter[int] = Counter()
    for _, numbers in recent_draws:
        counter.update(numbers)

    # Get top N numbers
    top_numbers = [num for num, _ in counter.most_common(top_n)]
    top_numbers.sort()

    # Date range
    oldest_date = recent_draws[-1][0]
    newest_date = recent_draws[0][0]

    return top_numbers, dict(counter), oldest_date, newest_date


def find_data_file() -> Path:
    """Find the most recent KENO data file."""
    base_path = Path(__file__).parent.parent

    # Priority order for data files
    candidates = [
        base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2022.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv",
        base_path / "Keno_GPTs" / "Daten" / "KENO_Stats_ab-2004.csv",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Keine KENO-Datendatei gefunden. "
        "Bitte --data-file Parameter verwenden."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Berechne HZ7/HZ6 W20 Hot-Zone Zahlen"
    )
    parser.add_argument(
        "--window", "-w",
        type=int,
        default=20,
        help="Anzahl der letzten Ziehungen (Standard: 20)"
    )
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=7,
        help="Anzahl der Top-Zahlen (Standard: 7 fuer HZ7)"
    )
    parser.add_argument(
        "--data-file", "-d",
        type=Path,
        default=None,
        help="Pfad zur KENO-Datendatei (CSV)"
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Zeige alle Zahlenfrequenzen"
    )

    args = parser.parse_args()

    # Find or use specified data file
    if args.data_file:
        data_file = args.data_file
    else:
        try:
            data_file = find_data_file()
        except FileNotFoundError as e:
            print(f"FEHLER: {e}")
            sys.exit(1)

    if not data_file.exists():
        print(f"FEHLER: Datei nicht gefunden: {data_file}")
        sys.exit(1)

    print(f"Lade Daten aus: {data_file}")
    draws = load_keno_data(data_file)
    print(f"Geladene Ziehungen: {len(draws)}")

    # Calculate Hot-Zone
    hz_numbers, frequencies, oldest, newest = calculate_hot_zone(
        draws,
        window=args.window,
        top_n=args.top
    )

    # Output
    print()
    print("=" * 60)
    print(f"HOT-ZONE {args.top} / FENSTER {args.window} (HZ{args.top} W{args.window})")
    print("=" * 60)
    print()
    print(f"Zeitraum: {oldest.strftime('%d.%m.%Y')} - {newest.strftime('%d.%m.%Y')}")
    print(f"Analysierte Ziehungen: {args.window}")
    print()
    print("-" * 60)
    print(f"DEINE HZ{args.top} W{args.window} ZAHLEN:")
    print("-" * 60)
    print()
    print(f"  {hz_numbers}")
    print()
    print("Zum Spielen: " + ", ".join(str(n) for n in hz_numbers))
    print()

    # Show top frequencies
    print("-" * 60)
    print("Top 10 Zahlen nach Haeufigkeit:")
    print("-" * 60)
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    for i, (num, freq) in enumerate(sorted_freq[:10], 1):
        marker = " <-- HZ" if num in hz_numbers else ""
        print(f"  {i:2}. Zahl {num:2}: {freq} mal gezogen{marker}")

    if args.show_all:
        print()
        print("-" * 60)
        print("Alle Zahlenfrequenzen (1-70):")
        print("-" * 60)
        for num in range(1, 71):
            freq = frequencies.get(num, 0)
            marker = " <-- HZ" if num in hz_numbers else ""
            print(f"  Zahl {num:2}: {freq:2} mal{marker}")

    print()
    print("=" * 60)
    print("HINWEIS:")
    print("  - Monatlich neu berechnen (am 1. des Monats)")
    print("  - Nur Tag 1-14 spielen (FRUEH-Phase)")
    print("  - 30 Tage Pause nach 10/10 Jackpot")
    print("  - Quelle: VALIDIERTE_FAKTEN.md")
    print("=" * 60)

    # Also calculate HZ6 if HZ7 was requested
    if args.top == 7:
        print()
        print("-" * 60)
        print("BONUS: HZ6 W20 (fuer Loop-Erweitert Alternative)")
        print("-" * 60)
        hz6 = hz_numbers[:6]
        print(f"  {hz6}")
        print()

    return hz_numbers


if __name__ == "__main__":
    main()
