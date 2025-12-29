#!/usr/bin/env python
"""Bereinigt KENO CSV-Dateien auf das Standard-Format."""

import re
import sys
from pathlib import Path


def clean_keno_csv(input_path: str, output_path: str = None) -> int:
    """
    Bereinigt KENO CSV-Datei.

    Konvertiert von:
        Datum;                    Gewinnzahlen;Plus 5;  Spieleinsatz
        03.01.2022;19;32;18;45; 5;27;...

    Zu:
        Datum;Keno_Z1;Keno_Z2;...;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz
        03.01.2022;19;32;18;45;5;27;...
    """
    input_file = Path(input_path)
    if output_path is None:
        output_path = input_file.parent / f"{input_file.stem}_bereinigt.csv"

    # Standard-Header
    header = "Datum;Keno_Z1;Keno_Z2;Keno_Z3;Keno_Z4;Keno_Z5;Keno_Z6;Keno_Z7;Keno_Z8;Keno_Z9;Keno_Z10;Keno_Z11;Keno_Z12;Keno_Z13;Keno_Z14;Keno_Z15;Keno_Z16;Keno_Z17;Keno_Z18;Keno_Z19;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz"

    cleaned_lines = [header]
    skipped = 0
    processed = 0

    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip header line (contains "Datum" and "Gewinnzahlen")
            if 'Gewinnzahlen' in line or 'Datum' in line and i == 0:
                skipped += 1
                continue

            # Skip footer garbage
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                skipped += 1
                continue

            # Parse the data line
            # Format: DD.MM.YYYY;Z1;Z2;...;Z20;Plus5;Spieleinsatz
            parts = line.split(';')

            # Need at least date + 20 numbers + plus5
            if len(parts) < 22:
                skipped += 1
                continue

            # Check if first part is a date
            date_match = re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0].strip())
            if not date_match:
                skipped += 1
                continue

            # Clean each part (remove extra spaces)
            cleaned_parts = []
            for j, part in enumerate(parts):
                part = part.strip()
                # Remove leading zeros from Plus5 only if it's a 5-digit number
                if j == 21 and len(part) == 5:  # Plus5 position
                    part = part.lstrip('0') or '0'
                cleaned_parts.append(part)

            # Ensure we have exactly 23 columns (date + 20 numbers + plus5 + spieleinsatz)
            if len(cleaned_parts) >= 22:
                # Take first 23 columns or pad with empty
                while len(cleaned_parts) < 23:
                    cleaned_parts.append('')
                cleaned_parts = cleaned_parts[:23]

                cleaned_line = ';'.join(cleaned_parts)
                cleaned_lines.append(cleaned_line)
                processed += 1

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    print(f"Bereinigung abgeschlossen:")
    print(f"  Input:     {input_path}")
    print(f"  Output:    {output_path}")
    print(f"  Zeilen:    {processed} verarbeitet, {skipped} uebersprungen")

    return processed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_keno_csv.py <input.csv> [output.csv]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    count = clean_keno_csv(input_path, output_path)
    print(f"\n{count} Ziehungen bereinigt.")
