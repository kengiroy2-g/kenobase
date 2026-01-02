#!/usr/bin/env python3
"""
Analyse: Welche Pool-Zahlen waren NICHT an 6/6 oder 7/7 Treffern beteiligt?

Das zeigt uns welche "populaeren" Zahlen das System KORRIGIERT.
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}


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
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """Holt Momentum-Zahlen (2+ mal in letzten X Tagen erschienen)."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()

    recent = relevant[-lookback:]
    counts = defaultdict(int)

    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1

    return {z for z, c in counts.items() if c >= 2}


def analyze_jackpot_numbers(
    pool: Set[int],
    draws: List[Dict],
    start_date: datetime,
    months: int = 6
) -> Dict:
    """
    Analysiert welche Pool-Zahlen an 6/6 und 7/7 Treffern beteiligt waren.
    """
    end_date = start_date + timedelta(days=months * 30)
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    # Tracking
    numbers_in_6_6 = set()
    numbers_in_7_7 = set()
    jackpots_6 = []
    jackpots_7 = []

    # Alle 6er und 7er Kombinationen
    pool_list = sorted(pool)
    combos_6 = list(combinations(pool_list, 6))
    combos_7 = list(combinations(pool_list, 7))

    print(f"\nAnalysiere {len(combos_6):,} 6er und {len(combos_7):,} 7er Kombinationen...")
    print(f"Gegen {len(test_draws)} Ziehungen ({start_date.date()} bis {end_date.date()})")

    for draw in test_draws:
        drawn = draw["zahlen"]

        # 6er pruefen
        for combo in combos_6:
            combo_set = set(combo)
            if combo_set <= drawn:  # Alle 6 getroffen
                numbers_in_6_6.update(combo_set)
                jackpots_6.append({
                    "datum": draw["datum_str"],
                    "combo": combo,
                    "gezogen": sorted(drawn)
                })

        # 7er pruefen
        for combo in combos_7:
            combo_set = set(combo)
            if combo_set <= drawn:  # Alle 7 getroffen
                numbers_in_7_7.update(combo_set)
                jackpots_7.append({
                    "datum": draw["datum_str"],
                    "combo": combo,
                    "gezogen": sorted(drawn)
                })

    # Zahlen die NICHT beteiligt waren
    not_in_6_6 = pool - numbers_in_6_6
    not_in_7_7 = pool - numbers_in_7_7
    not_in_any = pool - (numbers_in_6_6 | numbers_in_7_7)

    return {
        "pool": pool,
        "pool_size": len(pool),
        "numbers_in_6_6": numbers_in_6_6,
        "numbers_in_7_7": numbers_in_7_7,
        "not_in_6_6": not_in_6_6,
        "not_in_7_7": not_in_7_7,
        "not_in_any": not_in_any,
        "jackpots_6_count": len(jackpots_6),
        "jackpots_7_count": len(jackpots_7),
        "jackpots_6_unique_dates": len(set(j["datum"] for j in jackpots_6)),
        "jackpots_7_unique_dates": len(set(j["datum"] for j in jackpots_7)),
    }


def main():
    print("=" * 80)
    print("ANALYSE: Pool-Zahlen in Jackpots (6/6 und 7/7)")
    print("=" * 80)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    print(f"  Ziehungen: {len(draws)}")

    # === TEST 1: Ab 01.02.2025 ===
    target_date = datetime(2025, 2, 1)
    print(f"\n{'='*80}")
    print(f"TEST 1: Pool vom {target_date.date()}")
    print(f"{'='*80}")

    momentum = get_momentum_numbers(draws, target_date, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum

    print(f"\nPOOL ({len(pool)} Zahlen):")
    print(f"  Birthday (populaer): {sorted(BIRTHDAY_POPULAR)}")
    print(f"  Momentum:            {sorted(momentum)}")
    print(f"  Gesamt:              {sorted(pool)}")

    results = analyze_jackpot_numbers(pool, draws, target_date, months=6)

    print(f"\n{'='*80}")
    print("ERGEBNISSE")
    print(f"{'='*80}")

    print(f"\n--- 6/6 TREFFER ---")
    print(f"  Anzahl 6/6 Jackpots: {results['jackpots_6_count']}")
    print(f"  An {results['jackpots_6_unique_dates']} verschiedenen Tagen")
    print(f"\n  Zahlen IN 6/6 Treffern ({len(results['numbers_in_6_6'])}): {sorted(results['numbers_in_6_6'])}")
    print(f"\n  Zahlen NICHT in 6/6 ({len(results['not_in_6_6'])}): {sorted(results['not_in_6_6'])}")

    print(f"\n--- 7/7 TREFFER ---")
    print(f"  Anzahl 7/7 Jackpots: {results['jackpots_7_count']}")
    print(f"  An {results['jackpots_7_unique_dates']} verschiedenen Tagen")
    print(f"\n  Zahlen IN 7/7 Treffern ({len(results['numbers_in_7_7'])}): {sorted(results['numbers_in_7_7'])}")
    print(f"\n  Zahlen NICHT in 7/7 ({len(results['not_in_7_7'])}): {sorted(results['not_in_7_7'])}")

    print(f"\n{'='*80}")
    print("ZAHLEN DIE NIE AN EINEM JACKPOT BETEILIGT WAREN")
    print(f"{'='*80}")
    print(f"\n  Pool-Zahlen ohne Jackpot-Beteiligung ({len(results['not_in_any'])}):")
    print(f"  >>> {sorted(results['not_in_any'])} <<<")

    # Kategorisieren
    not_in_any = results['not_in_any']
    birthday_never = not_in_any & BIRTHDAY_POPULAR
    momentum_never = not_in_any & momentum
    both_never = not_in_any & (BIRTHDAY_POPULAR & momentum)

    print(f"\n  Davon Birthday-Zahlen: {sorted(birthday_never)}")
    print(f"  Davon Momentum-Zahlen: {sorted(momentum_never)}")

    if not_in_any:
        print(f"\n  >>> DIESE ZAHLEN SCHEINEN VOM SYSTEM KORRIGIERT ZU WERDEN <<<")
    else:
        print(f"\n  Alle Pool-Zahlen waren mindestens einmal an einem Jackpot beteiligt.")

    # === TEST 2: Ab 01.01.2024 (mehr Daten) ===
    target_date_2 = datetime(2024, 1, 1)
    print(f"\n\n{'='*80}")
    print(f"TEST 2: Pool vom {target_date_2.date()} (mehr historische Daten)")
    print(f"{'='*80}")

    momentum_2 = get_momentum_numbers(draws, target_date_2, lookback=3)
    pool_2 = BIRTHDAY_POPULAR | momentum_2

    print(f"\nPOOL ({len(pool_2)} Zahlen):")
    print(f"  Birthday (populaer): {sorted(BIRTHDAY_POPULAR)}")
    print(f"  Momentum:            {sorted(momentum_2)}")
    print(f"  Gesamt:              {sorted(pool_2)}")

    results_2 = analyze_jackpot_numbers(pool_2, draws, target_date_2, months=12)

    print(f"\n--- ERGEBNISSE (12 Monate) ---")
    print(f"  6/6 Jackpots: {results_2['jackpots_6_count']} an {results_2['jackpots_6_unique_dates']} Tagen")
    print(f"  7/7 Jackpots: {results_2['jackpots_7_count']} an {results_2['jackpots_7_unique_dates']} Tagen")

    print(f"\n  Zahlen NICHT in 6/6: {sorted(results_2['not_in_6_6'])}")
    print(f"  Zahlen NICHT in 7/7: {sorted(results_2['not_in_7_7'])}")
    print(f"\n  >>> NIE AN JACKPOT BETEILIGT: {sorted(results_2['not_in_any'])} <<<")

    # === ZUSAMMENFASSUNG ===
    print(f"\n\n{'='*80}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*80}")

    # Finde Zahlen die in BEIDEN Tests nie beteiligt waren
    consistent_never = results['not_in_any'] & results_2['not_in_any']

    print(f"""
    TEST 1 (Feb-Jul 2025):
      Pool: {len(pool)} Zahlen
      Nie in Jackpot: {sorted(results['not_in_any'])}

    TEST 2 (Jan 2024 - Jan 2025):
      Pool: {len(pool_2)} Zahlen
      Nie in Jackpot: {sorted(results_2['not_in_any'])}

    KONSISTENT NIE IN JACKPOT (beide Tests):
      >>> {sorted(consistent_never) if consistent_never else 'Keine'} <<<
    """)

    if consistent_never:
        print(f"    Diese {len(consistent_never)} Zahlen werden moeglicherweise systematisch korrigiert!")


if __name__ == "__main__":
    main()
