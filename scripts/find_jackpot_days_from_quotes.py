"""
Finde alle Jackpot-Tage (10/10 Gewinner) aus den Quoten-Daten.

Durchsucht alle verfuegbaren Keno_Gewinnquote CSV-Dateien.
"""

import csv
from pathlib import Path
from datetime import datetime
import json


def parse_german_number(s: str) -> int:
    """Parst deutsche Zahlenformate (1.234 -> 1234)."""
    if not s or s.strip() == "":
        return 0
    s = s.strip().replace(".", "").replace(",", "")
    try:
        return int(s)
    except ValueError:
        return 0


def find_jackpot_days(csv_path: Path) -> list[dict]:
    """
    Findet alle Tage mit 10/10 Gewinnern in einer Quoten-CSV.

    Format erwartet:
    Datum;Keno-Typ;Anzahl richtiger Zahlen;Anzahl der Gewinner;Gewinn/1Eur
    """
    jackpots = []

    print(f"\nDurchsuche: {csv_path.name}")

    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)  # Skip header
            print(f"  Header: {header}")

            for row in reader:
                if len(row) < 5:
                    continue

                try:
                    datum = row[0].strip()
                    keno_typ = row[1].strip()
                    richtige = row[2].strip()
                    gewinner_str = row[3].strip()
                    gewinn = row[4].strip()

                    # Suche nach Typ 10 mit 10 richtigen
                    if keno_typ == "10" and richtige == "10":
                        gewinner = parse_german_number(gewinner_str)

                        if gewinner > 0:
                            jackpots.append({
                                "datum": datum,
                                "anzahl_gewinner": gewinner,
                                "gewinn_pro_eur": gewinn,
                                "source_file": csv_path.name,
                            })
                            print(f"  ✓ JACKPOT: {datum} - {gewinner} Gewinner")

                except (IndexError, ValueError) as e:
                    continue

    except Exception as e:
        print(f"  Fehler: {e}")

    return jackpots


def load_drawn_numbers(date_str: str, keno_data_path: Path) -> list[int] | None:
    """Laedt die 20 gezogenen Zahlen fuer ein Datum."""

    # Konvertiere Datum-Format (31.12.2023 -> 31.12.2023)
    try:
        with open(keno_data_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row.get("Datum", "").strip() == date_str.strip():
                    numbers = []
                    for i in range(1, 21):
                        col = f"Keno_Z{i}"
                        if col in row:
                            numbers.append(int(row[col]))
                    if len(numbers) == 20:
                        return sorted(numbers)
    except Exception as e:
        print(f"    Fehler beim Laden der Zahlen: {e}")

    return None


def main():
    """Durchsuche alle Quoten-Dateien nach Jackpot-Tagen."""

    print("=" * 70)
    print("SUCHE NACH JACKPOT-TAGEN (10/10 GEWINNER)")
    print("=" * 70)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")

    # Finde alle Quoten-Dateien
    quote_files = list(base_path.glob("**/*Gewinnquote*.csv"))
    quote_files += list(base_path.glob("**/*gewinnquote*.csv"))
    quote_files += list(base_path.glob("**/*Quote*.csv"))

    # Deduplizieren
    quote_files = list(set(quote_files))

    print(f"\nGefundene Quoten-Dateien: {len(quote_files)}")
    for f in quote_files:
        print(f"  - {f}")

    all_jackpots = []

    for qf in quote_files:
        jackpots = find_jackpot_days(qf)
        all_jackpots.extend(jackpots)

    # Deduplizieren nach Datum
    seen_dates = set()
    unique_jackpots = []
    for jp in all_jackpots:
        if jp["datum"] not in seen_dates:
            seen_dates.add(jp["datum"])
            unique_jackpots.append(jp)

    # Sortiere nach Datum
    unique_jackpots.sort(key=lambda x: datetime.strptime(x["datum"].strip(), "%d.%m.%Y"), reverse=True)

    print(f"\n{'='*70}")
    print(f"GEFUNDENE JACKPOT-TAGE: {len(unique_jackpots)}")
    print(f"{'='*70}")

    # Lade gezogene Zahlen
    keno_data_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print(f"\n{'Datum':<15} {'Gewinner':>10} {'Gezogene 20 Zahlen'}")
    print("-" * 70)

    for jp in unique_jackpots:
        drawn = load_drawn_numbers(jp["datum"], keno_data_path)
        jp["drawn_20"] = drawn

        drawn_str = str(drawn) if drawn else "NICHT GEFUNDEN"
        print(f"{jp['datum']:<15} {jp['anzahl_gewinner']:>10} {drawn_str}")

    # Zusammenfassung
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"\nGefundene Jackpot-Tage: {len(unique_jackpots)}")
    total_winners = sum(jp["anzahl_gewinner"] for jp in unique_jackpots)
    print(f"Gesamtzahl 10/10 Gewinner: {total_winners}")

    with_numbers = sum(1 for jp in unique_jackpots if jp.get("drawn_20"))
    print(f"Davon mit 20 Zahlen gefunden: {with_numbers}")

    # Speichern
    output = {
        "analyse": "Jackpot-Tage aus Quoten-Daten",
        "quellen": [str(f) for f in quote_files],
        "jackpot_tage": unique_jackpots,
        "statistik": {
            "anzahl_tage": len(unique_jackpots),
            "total_gewinner": total_winners,
            "mit_zahlen": with_numbers,
        }
    }

    output_path = base_path / "results/jackpot_days_from_quotes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {output_path}")

    # Hinweis
    if unique_jackpots:
        print(f"\n{'='*70}")
        print("NAECHSTER SCHRITT")
        print(f"{'='*70}")
        print("""
Fuer jeden gefundenen Jackpot-Tag brauchen wir noch:
- Die 10 GEWINNER-Zahlen (nicht in Quoten-Daten enthalten!)

Diese muessen aus Pressemitteilungen recherchiert werden:
- lotto-brandenburg.de (Brandenburg)
- lotto-bayern.de (Bayern)
- etc.
""")

    return unique_jackpots


if __name__ == "__main__":
    main()
