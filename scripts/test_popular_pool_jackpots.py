#!/usr/bin/env python3
"""
TEST: Populaerer Pool (Birthday + Momentum) auf Volltreffer.

HYPOTHESE: Wenn viele Spieler Birthday + Momentum-Zahlen waehlen,
           wie oft treffen diese Kombinationen einen Jackpot (6/6, 7/7)?

METHODE:
1. An Tag X: Baue Pool aus Birthday + Momentum-Zahlen
2. Generiere ALLE 6er und 7er Kombinationen aus diesem Pool
3. Pruefe diese gegen die naechsten 6 Monate Ziehungen
4. Zaehle Volltreffer (6/6, 7/7)

Autor: Kenobase V2.5
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

# === KONSTANTEN ===

BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31

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
    """
    Holt Momentum-Zahlen (2+ mal in letzten X Tagen erschienen).
    """
    # Finde Ziehungen VOR target_date
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()

    recent = relevant[-lookback:]
    counts = defaultdict(int)

    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1

    # Zahlen mit 2+ Erscheinungen = Momentum
    return {z for z, c in counts.items() if c >= 2}


def build_popular_pool(
    draws: List[Dict],
    target_date: datetime,
    use_all_birthday: bool = False
) -> Tuple[Set[int], Dict]:
    """
    Baut Pool aus Birthday + Momentum Zahlen.

    Returns:
        (pool, meta_info)
    """
    momentum = get_momentum_numbers(draws, target_date, lookback=3)

    if use_all_birthday:
        birthday = BIRTHDAY_NUMBERS  # Alle 1-31
    else:
        birthday = BIRTHDAY_POPULAR  # Nur populaere

    pool = birthday | momentum

    meta = {
        "target_date": target_date.strftime("%d.%m.%Y"),
        "birthday_count": len(birthday),
        "momentum_count": len(momentum),
        "overlap": len(birthday & momentum),
        "total_pool": len(pool),
        "birthday_numbers": sorted(birthday),
        "momentum_numbers": sorted(momentum),
        "pool_numbers": sorted(pool),
    }

    return pool, meta


def generate_combinations(pool: Set[int], size: int) -> List[Tuple[int, ...]]:
    """Generiert alle Kombinationen der Groesse 'size' aus dem Pool."""
    pool_list = sorted(pool)
    return list(combinations(pool_list, size))


def test_combinations_over_period(
    combos: List[Tuple[int, ...]],
    draws: List[Dict],
    start_date: datetime,
    months: int = 6
) -> Dict:
    """
    Testet Kombinationen gegen Ziehungen ueber einen Zeitraum.

    Returns:
        Dict mit Ergebnissen
    """
    end_date = start_date + timedelta(days=months * 30)

    # Relevante Ziehungen
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    combo_size = len(combos[0]) if combos else 0

    results = {
        "combo_size": combo_size,
        "total_combos": len(combos),
        "test_draws": len(test_draws),
        "start_date": start_date.strftime("%d.%m.%Y"),
        "end_date": end_date.strftime("%d.%m.%Y"),
        "jackpots": [],  # Volltreffer (alle Zahlen getroffen)
        "near_misses": [],  # n-1 Treffer
        "hit_distribution": defaultdict(int),
    }

    print(f"\n  Teste {len(combos):,} {combo_size}er-Kombinationen gegen {len(test_draws)} Ziehungen...")

    for draw in test_draws:
        drawn = draw["zahlen"]

        for combo in combos:
            combo_set = set(combo)
            hits = len(combo_set & drawn)

            results["hit_distribution"][hits] += 1

            # Volltreffer!
            if hits == combo_size:
                results["jackpots"].append({
                    "combo": combo,
                    "draw_date": draw["datum_str"],
                    "drawn_numbers": sorted(drawn),
                })

            # Near Miss (n-1)
            elif hits == combo_size - 1:
                results["near_misses"].append({
                    "combo": combo,
                    "hits": hits,
                    "draw_date": draw["datum_str"],
                    "missing": list(combo_set - drawn),
                })

    return results


def analyze_results(results: Dict, typ: int) -> Dict:
    """Analysiert die Ergebnisse."""
    total_tests = results["total_combos"] * results["test_draws"]

    analysis = {
        "typ": typ,
        "total_combinations": results["total_combos"],
        "total_draws": results["test_draws"],
        "total_tests": total_tests,
        "jackpots_found": len(results["jackpots"]),
        "near_misses_found": len(results["near_misses"]),
        "jackpot_rate": len(results["jackpots"]) / total_tests if total_tests > 0 else 0,
    }

    # Hit-Verteilung analysieren
    hit_dist = results["hit_distribution"]
    analysis["hit_distribution"] = dict(hit_dist)

    # Erwartete Verteilung (Hypergeometrisch)
    # P(k Treffer) bei 20 von 70 gezogen, n gewählt
    # Für Vergleich

    return analysis


def print_results(pool_meta: Dict, results_6: Dict, results_7: Dict, analysis_6: Dict, analysis_7: Dict):
    """Gibt alle Ergebnisse formatiert aus."""

    print("\n" + "=" * 80)
    print("POPULAERER POOL TEST: Birthday + Momentum -> Jackpots?")
    print("=" * 80)

    print(f"\n--- POOL INFO (Stichtag: {pool_meta['target_date']}) ---")
    print(f"  Birthday-Zahlen ({pool_meta['birthday_count']}): {pool_meta['birthday_numbers']}")
    print(f"  Momentum-Zahlen ({pool_meta['momentum_count']}): {pool_meta['momentum_numbers']}")
    print(f"  Ueberlappung: {pool_meta['overlap']}")
    print(f"  GESAMT POOL ({pool_meta['total_pool']}): {pool_meta['pool_numbers']}")

    print(f"\n--- TYP 6 ERGEBNISSE ---")
    print(f"  Kombinationen getestet: {analysis_6['total_combinations']:,}")
    print(f"  Ziehungen geprueft: {analysis_6['total_draws']}")
    print(f"  Gesamt-Tests: {analysis_6['total_tests']:,}")
    print(f"\n  ★★★ VOLLTREFFER (6/6): {analysis_6['jackpots_found']} ★★★")
    print(f"  Near-Misses (5/6): {analysis_6['near_misses_found']}")

    if results_6["jackpots"]:
        print(f"\n  JACKPOT-DETAILS:")
        for jp in results_6["jackpots"]:
            print(f"    Datum: {jp['draw_date']}")
            print(f"    Kombi: {jp['combo']}")
            print(f"    Gezogen: {jp['drawn_numbers']}")
            print()

    print(f"\n  Treffer-Verteilung:")
    for hits in range(7):
        count = results_6["hit_distribution"].get(hits, 0)
        pct = count / analysis_6["total_tests"] * 100 if analysis_6["total_tests"] > 0 else 0
        bar = "█" * int(pct * 2)
        print(f"    {hits}/6: {count:>10,} ({pct:>6.3f}%) {bar}")

    print(f"\n--- TYP 7 ERGEBNISSE ---")
    print(f"  Kombinationen getestet: {analysis_7['total_combinations']:,}")
    print(f"  Ziehungen geprueft: {analysis_7['total_draws']}")
    print(f"  Gesamt-Tests: {analysis_7['total_tests']:,}")
    print(f"\n  ★★★ VOLLTREFFER (7/7): {analysis_7['jackpots_found']} ★★★")
    print(f"  Near-Misses (6/7): {analysis_7['near_misses_found']}")

    if results_7["jackpots"]:
        print(f"\n  JACKPOT-DETAILS:")
        for jp in results_7["jackpots"]:
            print(f"    Datum: {jp['draw_date']}")
            print(f"    Kombi: {jp['combo']}")
            print(f"    Gezogen: {jp['drawn_numbers']}")
            print()

    print(f"\n  Treffer-Verteilung:")
    for hits in range(8):
        count = results_7["hit_distribution"].get(hits, 0)
        pct = count / analysis_7["total_tests"] * 100 if analysis_7["total_tests"] > 0 else 0
        bar = "█" * int(pct * 2)
        print(f"    {hits}/7: {count:>10,} ({pct:>6.3f}%) {bar}")

    # Fazit
    print("\n" + "=" * 80)
    print("FAZIT")
    print("=" * 80)

    if analysis_6["jackpots_found"] == 0 and analysis_7["jackpots_found"] == 0:
        print("""
  KEIN EINZIGER VOLLTREFFER in 6 Monaten!

  Das bestaetigt die Korrektur-Theorie:
  → Birthday + Momentum Zahlen werden vom System KORRIGIERT
  → Diese "populaeren" Kombinationen treffen NICHT den Jackpot
  → Das System vermeidet systematisch populaere Kombinationen
        """)
    else:
        print(f"""
  Volltreffer gefunden!
  Typ 6: {analysis_6['jackpots_found']}
  Typ 7: {analysis_7['jackpots_found']}

  Interessant - manche populaere Kombinationen treffen doch.
        """)


def run_test(target_date_str: str, months: int = 6, use_all_birthday: bool = False):
    """Fuehrt den kompletten Test durch."""

    print("=" * 80)
    print(f"TEST: Populaerer Pool ab {target_date_str} fuer {months} Monate")
    print("=" * 80)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    print(f"  Ziehungen geladen: {len(draws)}")

    # Target Date parsen
    target_date = datetime.strptime(target_date_str, "%d.%m.%Y")
    print(f"  Stichtag: {target_date.date()}")

    # Pool bauen
    print("\nBaue populaeren Pool (Birthday + Momentum)...")
    pool, pool_meta = build_popular_pool(draws, target_date, use_all_birthday)
    print(f"  Pool-Groesse: {len(pool)} Zahlen")
    print(f"  Pool: {sorted(pool)}")

    # Kombinationen generieren
    print("\nGeneriere Kombinationen...")
    combos_6 = generate_combinations(pool, 6)
    combos_7 = generate_combinations(pool, 7)
    print(f"  6er-Kombinationen: {len(combos_6):,}")
    print(f"  7er-Kombinationen: {len(combos_7):,}")

    # Testen
    print(f"\nTeste gegen Ziehungen der naechsten {months} Monate...")
    results_6 = test_combinations_over_period(combos_6, draws, target_date, months)
    results_7 = test_combinations_over_period(combos_7, draws, target_date, months)

    # Analysieren
    analysis_6 = analyze_results(results_6, 6)
    analysis_7 = analyze_results(results_7, 7)

    # Ausgabe
    print_results(pool_meta, results_6, results_7, analysis_6, analysis_7)

    return {
        "pool_meta": pool_meta,
        "results_6": results_6,
        "results_7": results_7,
        "analysis_6": analysis_6,
        "analysis_7": analysis_7,
    }


def main():
    # Test ab 01.02.2025
    results = run_test("01.02.2025", months=6, use_all_birthday=False)

    # Optionaler zweiter Test mit anderem Datum
    print("\n\n" + "=" * 80)
    print("ZWEITER TEST: Ab 01.01.2024 (mehr Daten)")
    print("=" * 80)

    results_2024 = run_test("01.01.2024", months=6, use_all_birthday=False)


if __name__ == "__main__":
    main()
