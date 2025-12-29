#!/usr/bin/env python
"""
Bereinigt CSV-Dateien fuer alle deutschen Lotterien.

Unterstuetzte Lotterien:
- KENO
- Lotto 6aus49
- EuroJackpot
- Gluecksspirale
- Auswahlwette (Toto)
- Eurowette (Toto 13er)

Verwendung:
    python scripts/clean_lottery_csv.py <input.csv> <output.csv> --type <lottery_type>

Beispiele:
    python scripts/clean_lottery_csv.py data/raw/LOTTO_ab_2022.csv data/raw/lotto/LOTTO_bereinigt.csv --type lotto
    python scripts/clean_lottery_csv.py data/raw/EJ_ab_2022.csv data/raw/eurojackpot/EJ_bereinigt.csv --type eurojackpot
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def clean_lotto(input_path: str, output_path: str) -> int:
    """
    Bereinigt Lotto 6aus49 CSV.

    Rohformat:
        Datum; ;Gewinnzahlen;ZZ;S;Spiel77;Super6;Spieleinsatz;...
        05.01.2022; ;32; 7; 6; 4;41; 2;--;--;0;9897574;339740;...

    Zielformat:
        Datum;L1;L2;L3;L4;L5;L6;Zusatzzahl;Superzahl;Spiel77;Super6;Spieleinsatz
        05.01.2022;32;7;6;4;41;2;0;9;9897574;339740;35825518.80
    """
    header = "Datum;L1;L2;L3;L4;L5;L6;Zusatzzahl;Superzahl;Spiel77;Super6;Spieleinsatz;Jackpot_Kl1"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or i == 0:  # Skip header
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = [p.strip() for p in line.split(';')]

            # Datum validieren
            if not re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0]):
                continue

            try:
                # Format: Datum; ;Z1;Z2;Z3;Z4;Z5;Z6;ZZ;--;SZ;Spiel77;Super6;Spieleinsatz;...
                datum = parts[0]
                # Skip empty field at index 1
                zahlen = [parts[j].strip() for j in range(2, 8)]  # 6 Zahlen
                zusatzzahl = parts[8].replace('--', '0').strip()
                # Index 9 is often "--"
                superzahl = parts[10].strip() if len(parts) > 10 else '0'
                spiel77 = parts[11].strip() if len(parts) > 11 else ''
                super6 = parts[12].strip() if len(parts) > 12 else ''
                spieleinsatz = parts[13].strip().replace('.', '').replace(',', '.') if len(parts) > 13 else ''

                # Jackpot Klasse 1 (Position 14)
                jackpot = parts[14].strip() if len(parts) > 14 else ''
                if 'Jackpot' in jackpot:
                    jackpot = '0'  # Kein Gewinner
                else:
                    jackpot = jackpot.replace('.', '').replace(',', '.')

                cleaned = f"{datum};{';'.join(zahlen)};{zusatzzahl};{superzahl};{spiel77};{super6};{spieleinsatz};{jackpot}"
                cleaned_lines.append(cleaned)
                processed += 1
            except (IndexError, ValueError) as e:
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


def clean_eurojackpot(input_path: str, output_path: str) -> int:
    """
    Bereinigt EuroJackpot CSV.

    Rohformat:
        Datum;5 aus 50;EZ;Spieleinsatz;Anz. Kl. 1;...
        07.01.2022;47;23;21;17; 8; 6; 2; 45.918.930,00;...

    Zielformat:
        Datum;E1;E2;E3;E4;E5;Euro1;Euro2;Spieleinsatz;Jackpot
    """
    header = "Datum;E1;E2;E3;E4;E5;Euro1;Euro2;Spieleinsatz;Jackpot"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or i == 0:
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = [p.strip() for p in line.split(';')]

            if not re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0]):
                continue

            try:
                datum = parts[0]
                # 5 Hauptzahlen + 2 Eurozahlen
                zahlen = [parts[j].strip() for j in range(1, 6)]  # E1-E5
                euro1 = parts[6].strip()
                euro2 = parts[7].strip()
                spieleinsatz = parts[8].strip().replace('.', '').replace(',', '.')

                # Jackpot Status (Kl. 1)
                jackpot_anz = parts[9].strip() if len(parts) > 9 else ''
                if 'Jackpot' in jackpot_anz:
                    jackpot = '0'
                else:
                    jackpot = jackpot_anz

                cleaned = f"{datum};{';'.join(zahlen)};{euro1};{euro2};{spieleinsatz};{jackpot}"
                cleaned_lines.append(cleaned)
                processed += 1
            except (IndexError, ValueError):
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


def clean_gluecksspirale(input_path: str, output_path: str) -> int:
    """
    Bereinigt Gluecksspirale CSV.

    Rohformat:
        Datum;Zahlen Kl. 1-5;Zahlen Kl. 6;Zahlen Kl. 7;...
        08.01.2022;1;92;499;4856;79871;869836, 495909;6587702;...

    Zielformat:
        Datum;Kl1;Kl2;Kl3;Kl4;Kl5;Kl6_1;Kl6_2;Kl7;Spiel77;Super6;Spieleinsatz
    """
    header = "Datum;Kl1;Kl2;Kl3;Kl4;Kl5;Kl6_1;Kl6_2;Kl7;Spiel77;Super6;Spieleinsatz"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or i == 0:
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = [p.strip() for p in line.split(';')]

            if not re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0]):
                continue

            try:
                datum = parts[0]
                # Klassen 1-5 (einzelne Ziffern/Zahlen)
                kl1 = parts[1].strip()
                kl2 = parts[2].strip()
                kl3 = parts[3].strip()
                kl4 = parts[4].strip()
                kl5 = parts[5].strip()

                # Klasse 6 (2 Gewinnzahlen, kommasepariert)
                kl6_raw = parts[6].strip()
                kl6_parts = [x.strip() for x in kl6_raw.split(',')]
                kl6_1 = kl6_parts[0] if len(kl6_parts) > 0 else ''
                kl6_2 = kl6_parts[1] if len(kl6_parts) > 1 else ''

                # Klasse 7
                kl7 = parts[7].strip()

                # Spiel77, Super6, Spieleinsatz (suchen in restlichen Teilen)
                spiel77 = parts[-3].strip() if len(parts) >= 3 else ''
                super6 = parts[-2].strip() if len(parts) >= 2 else ''
                spieleinsatz = parts[-1].strip().replace('.', '').replace(',', '.') if parts[-1].strip() else ''

                cleaned = f"{datum};{kl1};{kl2};{kl3};{kl4};{kl5};{kl6_1};{kl6_2};{kl7};{spiel77};{super6};{spieleinsatz}"
                cleaned_lines.append(cleaned)
                processed += 1
            except (IndexError, ValueError):
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


def clean_auswahlwette(input_path: str, output_path: str) -> int:
    """
    Bereinigt Auswahlwette (Toto) CSV.

    Rohformat:
        Datum;Gewinnzahlen;ZZ;Spiel77;Super6;Spieleinsatz;...
        08.01.2022; 1; 3;39; 9;21;36;45;1252044;558562;375.592,75;...

    Zielformat:
        Datum;A1;A2;A3;A4;A5;A6;Zusatzzahl;Spiel77;Super6;Spieleinsatz
    """
    header = "Datum;A1;A2;A3;A4;A5;A6;Zusatzzahl;Spiel77;Super6;Spieleinsatz"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or i == 0:
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = [p.strip() for p in line.split(';')]

            if not re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0]):
                continue

            try:
                datum = parts[0]
                # 6 Gewinnzahlen + Zusatzzahl
                zahlen = [parts[j].strip() for j in range(1, 7)]
                zusatzzahl = parts[7].strip()
                spiel77 = parts[8].strip()
                super6 = parts[9].strip()
                spieleinsatz = parts[10].strip().replace('.', '').replace(',', '.')

                cleaned = f"{datum};{';'.join(zahlen)};{zusatzzahl};{spiel77};{super6};{spieleinsatz}"
                cleaned_lines.append(cleaned)
                processed += 1
            except (IndexError, ValueError):
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


def clean_eurowette(input_path: str, output_path: str) -> int:
    """
    Bereinigt Eurowette (Toto 13er) CSV.

    Rohformat:
        Datum;Gewinnzahlen;Spiel77;Super6;Spieleinsatz;...
        08.01.2022; 0; 1; 0; 1; 0; 2; 2; 1; 0; 0; 2; 2; 2;1252044;558562;497.007,50;...

    Zielformat:
        Datum;T1;T2;T3;T4;T5;T6;T7;T8;T9;T10;T11;T12;T13;Spiel77;Super6;Spieleinsatz
        (T = Tipp: 0=Heimsieg, 1=Unentschieden, 2=Auswaertssieg)
    """
    header = "Datum;T1;T2;T3;T4;T5;T6;T7;T8;T9;T10;T11;T12;T13;Spiel77;Super6;Spieleinsatz"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or i == 0:
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = [p.strip() for p in line.split(';')]

            if not re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0]):
                continue

            try:
                datum = parts[0]
                # 13 Tipps (0, 1, 2)
                tipps = [parts[j].strip() for j in range(1, 14)]
                spiel77 = parts[14].strip()
                super6 = parts[15].strip()
                spieleinsatz = parts[16].strip().replace('.', '').replace(',', '.')

                cleaned = f"{datum};{';'.join(tipps)};{spiel77};{super6};{spieleinsatz}"
                cleaned_lines.append(cleaned)
                processed += 1
            except (IndexError, ValueError):
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


def clean_keno(input_path: str, output_path: str) -> int:
    """
    Bereinigt KENO CSV (aus clean_keno_csv.py).
    """
    header = "Datum;Keno_Z1;Keno_Z2;Keno_Z3;Keno_Z4;Keno_Z5;Keno_Z6;Keno_Z7;Keno_Z8;Keno_Z9;Keno_Z10;Keno_Z11;Keno_Z12;Keno_Z13;Keno_Z14;Keno_Z15;Keno_Z16;Keno_Z17;Keno_Z18;Keno_Z19;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz"
    cleaned_lines = [header]
    processed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if 'Gewinnzahlen' in line or 'Datum' in line and i == 0:
                continue
            if 'Spieleins' in line or 'Angaben' in line or 'Gew' in line:
                continue

            parts = line.split(';')
            if len(parts) < 22:
                continue

            date_match = re.match(r'\d{2}\.\d{2}\.\d{4}', parts[0].strip())
            if not date_match:
                continue

            cleaned_parts = [p.strip() for p in parts]
            while len(cleaned_parts) < 23:
                cleaned_parts.append('')
            cleaned_parts = cleaned_parts[:23]

            cleaned_line = ';'.join(cleaned_parts)
            cleaned_lines.append(cleaned_line)
            processed += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))

    return processed


CLEANERS = {
    'keno': clean_keno,
    'lotto': clean_lotto,
    'eurojackpot': clean_eurojackpot,
    'gluecksspirale': clean_gluecksspirale,
    'auswahlwette': clean_auswahlwette,
    'eurowette': clean_eurowette,
}


def main():
    parser = argparse.ArgumentParser(
        description='Bereinigt Lotterie-CSV-Dateien',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python clean_lottery_csv.py LOTTO.csv LOTTO_clean.csv --type lotto
  python clean_lottery_csv.py EJ.csv EJ_clean.csv --type eurojackpot

Typen:
  keno          - KENO (20 Zahlen aus 70)
  lotto         - Lotto 6aus49
  eurojackpot   - EuroJackpot (5+2)
  gluecksspirale - Gluecksspirale
  auswahlwette  - Auswahlwette/Toto
  eurowette     - Eurowette/13er Toto
        """
    )

    parser.add_argument('input', help='Input CSV-Datei')
    parser.add_argument('output', help='Output CSV-Datei')
    parser.add_argument('--type', '-t', required=True, choices=CLEANERS.keys(),
                        help='Lotterie-Typ')

    args = parser.parse_args()

    cleaner = CLEANERS[args.type]
    count = cleaner(args.input, args.output)

    print(f"Bereinigung abgeschlossen:")
    print(f"  Typ:     {args.type}")
    print(f"  Input:   {args.input}")
    print(f"  Output:  {args.output}")
    print(f"  Zeilen:  {count}")


if __name__ == "__main__":
    main()
