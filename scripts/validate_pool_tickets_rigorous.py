#!/usr/bin/env python3
"""
RIGOROSE VALIDIERUNG: Pool-Tickets gegen echte GK-Gewinner

Fuer jeden Monat:
1. Pool bilden (17 Zahlen)
2. Alle moeglichen Typ 8, 9, 10 Tickets aus dem Pool generieren
3. Fuer jeden Tag pruefen: Haetten unsere Tickets gewonnen?
4. Mit echten GK-Daten vergleichen

Das ist die KORREKTE Pruefung!
"""

import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}


def load_keno_data(filepath: Path) -> List[Dict]:
    """Laedt KENO-Ziehungsdaten."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                datum_str = row.get("Datum", "").strip()
                if not datum_str:
                    continue
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                numbers = []
                for i in range(1, 21):
                    col = f"Keno_Z{i}"
                    if col in row and row[col]:
                        numbers.append(int(row[col]))
                if len(numbers) == 20:
                    data.append({"datum": datum, "zahlen": set(numbers)})
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def load_gq_data(filepath: Path) -> dict:
    """Laedt Keno_GQ Gewinnklassen-Daten."""
    data = defaultdict(lambda: defaultdict(dict))
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                datum = row.get("Datum", "").strip()
                keno_typ = int(row.get("Keno-Typ", 0))
                richtige = int(row.get("Anzahl richtiger Zahlen", 0))
                gewinner_str = row.get("Anzahl der Gewinner", "0").replace(".", "")
                gewinner = int(gewinner_str) if gewinner_str else 0
                data[datum][keno_typ][richtige] = gewinner
            except Exception:
                continue
    return dict(data)


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    """HOT Zahlen (>=2x in den letzten X Tagen)."""
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_index(draws: List[Dict], number: int) -> int:
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def build_reduced_pool(draws: List[Dict]) -> Tuple[Set[int], Set[int]]:
    """Baut reduzierten Pool und gibt auch HOT-Set zurueck."""
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_sorted = sorted(hot_filtered, key=lambda z: get_index(draws, z))
    hot_keep = set(hot_sorted[:5]) if len(hot_sorted) >= 5 else set(hot_sorted)

    cold_bd_sorted = sorted(cold_birthday, key=lambda z: get_count(draws, z))
    cold_bd_keep = set(cold_bd_sorted[:6])

    cold_nbd_sorted = sorted(cold_nonbd, key=lambda z: get_count(draws, z))
    cold_nbd_keep = set(cold_nbd_sorted[:6])

    reduced_pool = hot_keep | cold_bd_keep | cold_nbd_keep
    return reduced_pool, hot


def main():
    base_path = Path(__file__).parent.parent

    # Daten laden
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    gq_path = base_path / "Keno_GPTs/Keno_GQ_2025.csv"

    draws = load_keno_data(keno_path)
    gq_data = load_gq_data(gq_path)

    print("=" * 80)
    print("RIGOROSE VALIDIERUNG: Pool-Tickets vs. Echte GK-Gewinner")
    print("=" * 80)
    print()
    print("Methode:")
    print("1. Pool bilden (17 Zahlen) am 3. jedes Monats")
    print("2. ALLE moeglichen Typ 8/9/10 Tickets aus Pool generieren")
    print("3. Fuer jeden Tag: Wie viele unserer Tickets haetten gewonnen?")
    print("4. Vergleich mit echten GK-Gewinnern")
    print()

    # Analysiere jeden Monat
    results_by_month = {}

    for month in range(1, 13):
        # Pool-Datum: 3. des Monats
        try:
            pool_date = datetime(2025, month, 3)
        except ValueError:
            continue

        # Finde Ziehung am Pool-Datum
        pool_idx = None
        for i, draw in enumerate(draws):
            if draw["datum"].date() <= pool_date.date():
                pool_idx = i

        if pool_idx is None or pool_idx < 30:
            continue

        # Pool bilden
        train_data = draws[:pool_idx + 1]
        pool, hot = build_reduced_pool(train_data)

        if len(pool) < 10:
            print(f"Monat {month}: Pool zu klein ({len(pool)} Zahlen)")
            continue

        # Generiere ALLE moeglichen Tickets aus dem Pool
        pool_list = sorted(pool)
        tickets_typ8 = list(combinations(pool_list, 8))
        tickets_typ9 = list(combinations(pool_list, 9))
        tickets_typ10 = list(combinations(pool_list, 10))

        print(f"\n{'=' * 60}")
        print(f"MONAT {month}/2025 - Pool gebildet am {pool_date.strftime('%d.%m.%Y')}")
        print(f"{'=' * 60}")
        print(f"Pool ({len(pool)} Zahlen): {pool_list}")
        print(f"Moegliche Typ 8 Tickets:  {len(tickets_typ8)}")
        print(f"Moegliche Typ 9 Tickets:  {len(tickets_typ9)}")
        print(f"Moegliche Typ 10 Tickets: {len(tickets_typ10)}")
        print()

        # Monatsende
        if month == 12:
            month_end = datetime(2025, 12, 31)
        else:
            month_end = datetime(2025, month + 1, 1) - timedelta(days=1)

        # Analysiere jeden Tag
        month_results = {
            "pool": pool_list,
            "tickets_typ8": len(tickets_typ8),
            "tickets_typ9": len(tickets_typ9),
            "tickets_typ10": len(tickets_typ10),
            "days": [],
            "wins_typ8": 0,
            "wins_typ9": 0,
            "wins_typ10": 0,
            "gk_typ8_days": 0,
            "gk_typ9_days": 0,
            "gk_typ10_days": 0,
        }

        print(f"{'Datum':<12} {'T8 Wins':<10} {'T9 Wins':<10} {'T10 Wins':<10} {'GK8':<6} {'GK9':<6} {'GK10':<6}")
        print("-" * 70)

        for draw in draws:
            if not (pool_date.date() < draw["datum"].date() <= month_end.date()):
                continue
            if draw["datum"].year != 2025:
                continue

            drawn = draw["zahlen"]
            datum_str = draw["datum"].strftime("%d.%m.%Y")

            # Zaehle wie viele unserer Tickets gewonnen haetten
            wins_t8 = sum(1 for t in tickets_typ8 if set(t).issubset(drawn))
            wins_t9 = sum(1 for t in tickets_typ9 if set(t).issubset(drawn))
            wins_t10 = sum(1 for t in tickets_typ10 if set(t).issubset(drawn))

            # Hole echte GK-Daten
            gk8_winners = gq_data.get(datum_str, {}).get(8, {}).get(8, 0)
            gk9_winners = gq_data.get(datum_str, {}).get(9, {}).get(9, 0)
            gk10_winners = gq_data.get(datum_str, {}).get(10, {}).get(10, 0)

            # Nur Tage mit Gewinnen anzeigen
            if wins_t8 > 0 or wins_t9 > 0 or wins_t10 > 0 or gk8_winners > 0 or gk9_winners > 0 or gk10_winners > 0:
                print(f"{datum_str:<12} {wins_t8:<10} {wins_t9:<10} {wins_t10:<10} {gk8_winners:<6} {gk9_winners:<6} {gk10_winners:<6}")

            month_results["days"].append({
                "datum": datum_str,
                "our_wins_typ8": wins_t8,
                "our_wins_typ9": wins_t9,
                "our_wins_typ10": wins_t10,
                "gk8_winners": gk8_winners,
                "gk9_winners": gk9_winners,
                "gk10_winners": gk10_winners,
            })

            month_results["wins_typ8"] += wins_t8
            month_results["wins_typ9"] += wins_t9
            month_results["wins_typ10"] += wins_t10
            if gk8_winners > 0:
                month_results["gk_typ8_days"] += 1
            if gk9_winners > 0:
                month_results["gk_typ9_days"] += 1
            if gk10_winners > 0:
                month_results["gk_typ10_days"] += 1

        print()
        print(f"MONATS-ZUSAMMENFASSUNG:")
        print(f"  Unsere Typ 8 Jackpots:  {month_results['wins_typ8']}")
        print(f"  Unsere Typ 9 Jackpots:  {month_results['wins_typ9']}")
        print(f"  Unsere Typ 10 Jackpots: {month_results['wins_typ10']}")
        print(f"  Echte GK8-Tage:         {month_results['gk_typ8_days']}")
        print(f"  Echte GK9-Tage:         {month_results['gk_typ9_days']}")
        print(f"  Echte GK10-Tage:        {month_results['gk_typ10_days']}")

        results_by_month[month] = month_results

    # Gesamtzusammenfassung
    print()
    print("=" * 80)
    print("JAHRES-ZUSAMMENFASSUNG 2025")
    print("=" * 80)
    print()

    total_wins_t8 = sum(m["wins_typ8"] for m in results_by_month.values())
    total_wins_t9 = sum(m["wins_typ9"] for m in results_by_month.values())
    total_wins_t10 = sum(m["wins_typ10"] for m in results_by_month.values())
    total_gk8_days = sum(m["gk_typ8_days"] for m in results_by_month.values())
    total_gk9_days = sum(m["gk_typ9_days"] for m in results_by_month.values())
    total_gk10_days = sum(m["gk_typ10_days"] for m in results_by_month.values())

    print(f"UNSERE POOL-TICKETS (haetten gewonnen):")
    print(f"  Typ 8 Jackpots (8/8):   {total_wins_t8}")
    print(f"  Typ 9 Jackpots (9/9):   {total_wins_t9}")
    print(f"  Typ 10 Jackpots (10/10): {total_wins_t10}")
    print()
    print(f"ECHTE GK-GEWINNER-TAGE (laut Keno_GQ):")
    print(f"  GK8 Tage mit Gewinnern:  {total_gk8_days}")
    print(f"  GK9 Tage mit Gewinnern:  {total_gk9_days}")
    print(f"  GK10 Tage mit Gewinnern: {total_gk10_days}")
    print()

    # Validierung: An wie vielen GK-Tagen haetten WIR auch gewonnen?
    print("=" * 80)
    print("KREUZ-VALIDIERUNG: Unsere Gewinne vs. Echte GK-Tage")
    print("=" * 80)
    print()

    matching_t8 = 0
    matching_t9 = 0
    matching_t10 = 0
    our_exclusive_t8 = 0
    our_exclusive_t9 = 0
    our_exclusive_t10 = 0

    for month_data in results_by_month.values():
        for day in month_data["days"]:
            # Tage wo WIR UND echte Spieler gewonnen haben
            if day["our_wins_typ8"] > 0 and day["gk8_winners"] > 0:
                matching_t8 += 1
            if day["our_wins_typ9"] > 0 and day["gk9_winners"] > 0:
                matching_t9 += 1
            if day["our_wins_typ10"] > 0 and day["gk10_winners"] > 0:
                matching_t10 += 1

            # Tage wo NUR WIR gewonnen haetten (aber niemand sonst)
            if day["our_wins_typ8"] > 0 and day["gk8_winners"] == 0:
                our_exclusive_t8 += 1
            if day["our_wins_typ9"] > 0 and day["gk9_winners"] == 0:
                our_exclusive_t9 += 1
            if day["our_wins_typ10"] > 0 and day["gk10_winners"] == 0:
                our_exclusive_t10 += 1

    print(f"Typ 8:")
    print(f"  Tage wo WIR + andere gewonnen:     {matching_t8}")
    print(f"  Tage wo NUR WIR gewonnen haetten:  {our_exclusive_t8}")
    print()
    print(f"Typ 9:")
    print(f"  Tage wo WIR + andere gewonnen:     {matching_t9}")
    print(f"  Tage wo NUR WIR gewonnen haetten:  {our_exclusive_t9}")
    print()
    print(f"Typ 10:")
    print(f"  Tage wo WIR + andere gewonnen:     {matching_t10}")
    print(f"  Tage wo NUR WIR gewonnen haetten:  {our_exclusive_t10}")

    # ROI Berechnung
    print()
    print("=" * 80)
    print("ROI-BERECHNUNG (wenn alle Pool-Tickets gespielt)")
    print("=" * 80)
    print()

    # Quoten
    QUOTE_T8 = 10000  # 8/8 bei Typ 8
    QUOTE_T9 = 50000  # 9/9 bei Typ 9
    QUOTE_T10 = 100000  # 10/10 bei Typ 10

    for month, data in results_by_month.items():
        days_played = len(data["days"])
        if days_played == 0:
            continue

        # Kosten: Alle Tickets jeden Tag
        cost_t8 = data["tickets_typ8"] * days_played * 1  # 1 EUR pro Ticket
        cost_t9 = data["tickets_typ9"] * days_played * 1
        cost_t10 = data["tickets_typ10"] * days_played * 1

        # Gewinne
        win_t8 = data["wins_typ8"] * QUOTE_T8
        win_t9 = data["wins_typ9"] * QUOTE_T9
        win_t10 = data["wins_typ10"] * QUOTE_T10

        # ROI
        roi_t8 = ((win_t8 - cost_t8) / cost_t8 * 100) if cost_t8 > 0 else 0
        roi_t9 = ((win_t9 - cost_t9) / cost_t9 * 100) if cost_t9 > 0 else 0
        roi_t10 = ((win_t10 - cost_t10) / cost_t10 * 100) if cost_t10 > 0 else 0

        print(f"Monat {month}:")
        print(f"  Typ 8:  Einsatz {cost_t8:>8} EUR, Gewinn {win_t8:>10} EUR, ROI: {roi_t8:>+8.1f}%")
        print(f"  Typ 9:  Einsatz {cost_t9:>8} EUR, Gewinn {win_t9:>10} EUR, ROI: {roi_t9:>+8.1f}%")
        print(f"  Typ 10: Einsatz {cost_t10:>8} EUR, Gewinn {win_t10:>10} EUR, ROI: {roi_t10:>+8.1f}%")
        print()

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "method": "rigorous_validation",
        "results_by_month": {str(k): {key: val for key, val in v.items() if key != "days"}
                            for k, v in results_by_month.items()},
        "totals": {
            "our_wins_typ8": total_wins_t8,
            "our_wins_typ9": total_wins_t9,
            "our_wins_typ10": total_wins_t10,
            "gk8_days": total_gk8_days,
            "gk9_days": total_gk9_days,
            "gk10_days": total_gk10_days,
            "matching_t8": matching_t8,
            "matching_t9": matching_t9,
            "matching_t10": matching_t10,
            "our_exclusive_t8": our_exclusive_t8,
            "our_exclusive_t9": our_exclusive_t9,
            "our_exclusive_t10": our_exclusive_t10,
        }
    }

    output_path = base_path / "results/pool_tickets_rigorous_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
