#!/usr/bin/env python3
"""
ANALYSE 2025: Monatliche Pool-Validierung

1. Fuer jeden Monat: Pool 5 Tage vor dem 8. bilden
2. Ergebnisse ueber das ganze Jahr beobachten
3. Wenn 8/9/10 Zahlen im Pool -> pruefen ob GK-Gewinne moeglich
4. Analyse rund um 10/10 Jackpot-Events

Nutzung:
    python scripts/analyze_2025_monthly_pools.py
    python scripts/analyze_2025_monthly_pools.py --save
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

# KENO Quoten fuer Typ 8, 9, 10
QUOTES = {
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 12, 6: 100, 7: 1000, 8: 10000},
    9: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 6, 6: 50, 7: 500, 8: 5000, 9: 50000},
    10: {0: 0, 1: 0, 2: 2, 3: 0, 4: 0, 5: 2, 6: 15, 7: 100, 8: 1000, 9: 10000, 10: 100000},
}


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
    """Wann wurde die Zahl zuletzt gezogen (0 = heute)."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    """Wie oft wurde die Zahl in den letzten X Tagen gezogen."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def build_reduced_pool(draws: List[Dict], target_size: int = 17) -> Tuple[Set[int], Dict]:
    """
    DANCE-006: Baut reduzierten Pool von ~17 Zahlen.

    Methode:
    - HOT: Top 5 (ohne Korrektur-Kandidaten)
    - COLD-Birthday: Top 6 (seltenste)
    - COLD-Non-Birthday: Top 6 (seltenste)
    """
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # HOT: Ohne Korrektur-Kandidaten, sortiert nach Index
    hot_filtered = hot - TOP_20_CORRECTION
    hot_sorted = sorted(hot_filtered, key=lambda z: get_index(draws, z))
    hot_keep = set(hot_sorted[:5]) if len(hot_sorted) >= 5 else set(hot_sorted)

    # COLD-Birthday: Seltenste zuerst
    cold_bd_sorted = sorted(cold_birthday, key=lambda z: get_count(draws, z))
    cold_bd_keep = set(cold_bd_sorted[:6])

    # COLD-Non-Birthday: Seltenste zuerst
    cold_nbd_sorted = sorted(cold_nonbd, key=lambda z: get_count(draws, z))
    cold_nbd_keep = set(cold_nbd_sorted[:6])

    reduced_pool = hot_keep | cold_bd_keep | cold_nbd_keep

    details = {
        "hot_all": sorted(hot),
        "hot_keep": sorted(hot_keep),
        "cold_birthday_keep": sorted(cold_bd_keep),
        "cold_nonbd_keep": sorted(cold_nbd_keep),
        "pool_size": len(reduced_pool),
    }

    return reduced_pool, details


def get_decades(numbers) -> int:
    """Anzahl verschiedener Dekaden."""
    return len(set((n - 1) // 10 for n in numbers))


def get_non_birthday_ratio(numbers) -> float:
    """Anteil Non-Birthday Zahlen."""
    nbd = len([n for n in numbers if n > 31])
    return nbd / len(numbers) if numbers else 0


def has_consecutive(numbers) -> bool:
    """Prueft ob konsekutive Zahlen vorhanden sind."""
    nums = sorted(numbers)
    for i in range(len(nums) - 1):
        if nums[i + 1] - nums[i] == 1:
            return True
    return False


def get_hot_count(numbers, hot_set: Set[int]) -> int:
    """Anzahl HOT-Zahlen im Ticket."""
    return len([n for n in numbers if n in hot_set])


def filter_combinations(
    pool: Set[int],
    hot: Set[int],
    ticket_size: int = 6,
    min_decades: int = 5,
    nbd_ratio_range: Tuple[float, float] = (0.45, 0.55),
    hot_count: int = 2,
    sum_range: Tuple[int, int] = (150, 250),
) -> List[tuple]:
    """Filtert Kombinationen basierend auf allen Strategien."""
    all_combos = list(combinations(sorted(pool), ticket_size))

    filtered = all_combos

    # Filter 1: Dekaden
    filtered = [c for c in filtered if get_decades(c) >= min_decades]

    # Filter 2: Non-Birthday Ratio
    filtered = [c for c in filtered
                if nbd_ratio_range[0] <= get_non_birthday_ratio(c) <= nbd_ratio_range[1]]

    # Filter 3: Keine Konsekutiven
    filtered = [c for c in filtered if not has_consecutive(c)]

    # Filter 4: HOT Count
    if hot_count is not None:
        filtered = [c for c in filtered if get_hot_count(c, hot) == hot_count]

    # Filter 5: Summe
    filtered = [c for c in filtered if sum_range[0] <= sum(c) <= sum_range[1]]

    return filtered


def find_draws_by_date(draws: List[Dict], target_date: datetime) -> Optional[int]:
    """Findet Index einer Ziehung nach Datum."""
    for i, draw in enumerate(draws):
        if draw["datum"].date() == target_date.date():
            return i
    return None


def get_pool_date(year: int, month: int) -> datetime:
    """Berechnet das Datum 5 Tage vor dem 8. eines Monats."""
    eighth = datetime(year, month, 8)
    return eighth - timedelta(days=5)  # 3. des Monats


def analyze_month(
    draws: List[Dict],
    pool_date: datetime,
    month_end: datetime
) -> Dict:
    """Analysiert einen Monat mit gegebenem Pool."""

    # Finde Ziehung am Pool-Datum
    pool_idx = None
    for i, draw in enumerate(draws):
        if draw["datum"].date() <= pool_date.date():
            pool_idx = i

    if pool_idx is None or pool_idx < 30:
        return {"error": "Nicht genuegend historische Daten"}

    # Pool bilden mit Daten bis pool_date
    train_data = draws[:pool_idx + 1]
    pool, pool_details = build_reduced_pool(train_data)
    hot = get_hot_numbers(train_data, lookback=3)

    # Gefilterte Kombinationen
    filtered_combos = filter_combinations(pool, hot, ticket_size=6)

    # Finde alle Ziehungen im Zeitraum
    test_draws = []
    for draw in draws:
        if pool_date.date() < draw["datum"].date() <= month_end.date():
            test_draws.append(draw)

    # Analyse jeder Ziehung
    results = []
    jackpots_6 = []
    big_hits = []  # 8, 9, 10 Treffer aus Pool

    for draw in test_draws:
        drawn = draw["zahlen"]
        pool_hits = len(pool & drawn)

        # Check fuer 6/6 Jackpots in gefilterten Kombis
        jackpots_today = 0
        for combo in filtered_combos:
            if len(set(combo) & drawn) == 6:
                jackpots_today += 1

        if jackpots_today > 0:
            jackpots_6.append({
                "datum": draw["datum"].strftime("%d.%m.%Y"),
                "count": jackpots_today
            })

        # Big Hits (8+ aus Pool in Ziehung)
        if pool_hits >= 8:
            big_hits.append({
                "datum": draw["datum"].strftime("%d.%m.%Y"),
                "pool_hits": pool_hits,
                "pool_numbers_drawn": sorted(pool & drawn),
                "gk_potential": f"GK{pool_hits} moeglich" if pool_hits <= 10 else "10+",
            })

        results.append({
            "datum": draw["datum"].strftime("%d.%m.%Y"),
            "pool_hits": pool_hits,
            "jackpots_6": jackpots_today,
        })

    return {
        "pool_date": pool_date.strftime("%d.%m.%Y"),
        "pool": sorted(pool),
        "pool_size": len(pool),
        "pool_details": pool_details,
        "filtered_combos_count": len(filtered_combos),
        "test_period": {
            "start": test_draws[0]["datum"].strftime("%d.%m.%Y") if test_draws else None,
            "end": test_draws[-1]["datum"].strftime("%d.%m.%Y") if test_draws else None,
            "days": len(test_draws),
        },
        "total_jackpots_6": sum(j["count"] for j in jackpots_6),
        "jackpot_days": jackpots_6,
        "big_hits_8plus": big_hits,
        "avg_pool_hits": sum(r["pool_hits"] for r in results) / len(results) if results else 0,
        "daily_results": results,
    }


def find_jackpot_10_events(draws: List[Dict]) -> List[Dict]:
    """
    Findet alle potenziellen 10/10 Jackpot-Tage.
    Ein 10/10 ist moeglich wenn alle 10 gespielten Zahlen gezogen wurden.
    Da wir keine Spielerdaten haben, markieren wir Tage wo unser Pool 10+ Treffer hatte.
    """
    jackpot_events = []

    # Wir haben keine echten GK1 (10/10) Daten
    # Stattdessen: Finde Tage wo Pool-basierte Typ-10-Tickets haetten gewinnen koennen

    for i in range(30, len(draws)):
        train_data = draws[:i]
        pool, _ = build_reduced_pool(train_data)

        # Wenn Pool >= 10 Zahlen hat
        if len(pool) >= 10:
            drawn = draws[i]["zahlen"]
            pool_hits = len(pool & drawn)

            # 10+ Treffer aus Pool = potenzieller Jackpot
            if pool_hits >= 10:
                jackpot_events.append({
                    "datum": draws[i]["datum"].strftime("%d.%m.%Y"),
                    "pool_hits": pool_hits,
                    "pool": sorted(pool),
                    "pool_numbers_drawn": sorted(pool & drawn),
                })

    return jackpot_events


def analyze_around_jackpot(
    draws: List[Dict],
    jackpot_date: datetime,
    days_before: int = 5,
    days_after: int = 5
) -> Dict:
    """Analysiert Pool-Performance rund um ein Jackpot-Event."""

    # Finde Jackpot-Index
    jp_idx = None
    for i, draw in enumerate(draws):
        if draw["datum"].date() == jackpot_date.date():
            jp_idx = i
            break

    if jp_idx is None:
        return {"error": f"Jackpot-Datum {jackpot_date} nicht gefunden"}

    results = {
        "jackpot_date": jackpot_date.strftime("%d.%m.%Y"),
        "before": [],
        "after": [],
    }

    # Analyse Tage VOR dem Jackpot
    for offset in range(1, days_before + 1):
        idx = jp_idx - offset
        if idx >= 30:
            train_data = draws[:idx]
            pool, _ = build_reduced_pool(train_data)
            drawn = draws[idx]["zahlen"]
            pool_hits = len(pool & drawn)

            results["before"].append({
                "datum": draws[idx]["datum"].strftime("%d.%m.%Y"),
                "days_before_jp": offset,
                "pool_hits": pool_hits,
                "pool_size": len(pool),
            })

    # Analyse Tage NACH dem Jackpot
    for offset in range(1, days_after + 1):
        idx = jp_idx + offset
        if idx < len(draws):
            # Pool am JP-Tag gebildet
            train_data = draws[:jp_idx + 1]
            pool, _ = build_reduced_pool(train_data)
            drawn = draws[idx]["zahlen"]
            pool_hits = len(pool & drawn)

            results["after"].append({
                "datum": draws[idx]["datum"].strftime("%d.%m.%Y"),
                "days_after_jp": offset,
                "pool_hits": pool_hits,
                "pool_size": len(pool),
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="2025 Monatliche Pool-Analyse")
    parser.add_argument("--save", action="store_true", help="Ergebnisse als JSON speichern")
    args = parser.parse_args()

    # Daten laden
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    # Filter auf 2025
    draws_2025 = [d for d in draws if d["datum"].year == 2025]

    print("=" * 80)
    print("2025 MONATLICHE POOL-ANALYSE")
    print("Pool-Bildung: 5 Tage vor dem 8. jedes Monats")
    print("=" * 80)
    print()
    print(f"Gesamt Ziehungen 2025: {len(draws_2025)}")
    if draws_2025:
        print(f"Zeitraum: {draws_2025[0]['datum'].strftime('%d.%m.%Y')} - {draws_2025[-1]['datum'].strftime('%d.%m.%Y')}")
    print()

    # Monatliche Analyse
    monthly_results = {}
    all_jackpots = []
    all_big_hits = []

    for month in range(1, 13):
        # Pool-Datum: 3. des Monats (5 Tage vor dem 8.)
        try:
            pool_date = get_pool_date(2025, month)
        except ValueError:
            continue

        # Monatsende
        if month == 12:
            month_end = datetime(2025, 12, 31)
        else:
            month_end = datetime(2025, month + 1, 1) - timedelta(days=1)

        # Pruefe ob wir Daten fuer diesen Monat haben
        has_data = any(d["datum"].month == month and d["datum"].year == 2025 for d in draws)
        if not has_data:
            continue

        print(f"\n{'=' * 60}")
        print(f"MONAT {month}/2025")
        print(f"Pool-Datum: {pool_date.strftime('%d.%m.%Y')}")
        print(f"{'=' * 60}")

        result = analyze_month(draws, pool_date, month_end)
        monthly_results[month] = result

        if "error" in result:
            print(f"  FEHLER: {result['error']}")
            continue

        print(f"  Pool: {result['pool']} ({result['pool_size']} Zahlen)")
        print(f"  Gefilterte Kombis: {result['filtered_combos_count']}")
        print(f"  Testzeitraum: {result['test_period']['start']} - {result['test_period']['end']} ({result['test_period']['days']} Tage)")
        print(f"  Durchschnittl. Pool-Treffer: {result['avg_pool_hits']:.2f}")
        print(f"  6/6 Jackpots: {result['total_jackpots_6']}")

        if result["jackpot_days"]:
            all_jackpots.extend(result["jackpot_days"])
            print(f"\n  JACKPOTS 6/6:")
            for jp in result["jackpot_days"]:
                print(f"    {jp['datum']}: {jp['count']}x")

        if result["big_hits_8plus"]:
            all_big_hits.extend(result["big_hits_8plus"])
            print(f"\n  BIG HITS (8+ aus Pool):")
            for bh in result["big_hits_8plus"]:
                print(f"    {bh['datum']}: {bh['pool_hits']}/Pool - {bh['gk_potential']}")
                print(f"      Gezogene Pool-Zahlen: {bh['pool_numbers_drawn']}")

    # Zusammenfassung
    print()
    print("=" * 80)
    print("JAHRES-ZUSAMMENFASSUNG 2025")
    print("=" * 80)
    print()

    total_months = len([m for m in monthly_results.values() if "error" not in m])
    total_jackpots = sum(m.get("total_jackpots_6", 0) for m in monthly_results.values())
    total_days = sum(m.get("test_period", {}).get("days", 0) for m in monthly_results.values())

    print(f"Analysierte Monate:       {total_months}")
    print(f"Analysierte Tage:         {total_days}")
    print(f"Gesamt 6/6 Jackpots:      {total_jackpots}")
    print(f"Big Hits (8+ aus Pool):   {len(all_big_hits)}")
    print()

    if all_jackpots:
        print("ALLE 6/6 JACKPOTS:")
        for jp in all_jackpots:
            print(f"  {jp['datum']}: {jp['count']}x Jackpot")

    if all_big_hits:
        print()
        print("ALLE BIG HITS (8+ TREFFER AUS POOL):")
        print("-" * 60)
        print("Diese Tage haetten GK8/9/10 Gewinne ermoeglichen koennen:")
        print()
        for bh in all_big_hits:
            print(f"  {bh['datum']}: {bh['pool_hits']} von 17 Pool-Zahlen gezogen")
            print(f"    → {bh['gk_potential']}")
            print(f"    Gezogen: {bh['pool_numbers_drawn']}")
            print()

    # Jackpot-Event-Analyse
    print()
    print("=" * 80)
    print("ANALYSE RUND UM 10/10 JACKPOT-EVENTS")
    print("=" * 80)
    print()

    # Bekannte Jackpots (aus GK1 Liste oder manuell)
    known_jackpots = [
        # Format: (Datum, Typ, Info)
        # Hier koennten bekannte Jackpots eingetragen werden
    ]

    # Finde potenzielle 10+ Treffer-Events
    potential_jackpots = find_jackpot_10_events(draws)
    potential_2025 = [p for p in potential_jackpots
                      if datetime.strptime(p["datum"], "%d.%m.%Y").year == 2025]

    if potential_2025:
        print(f"Potenzielle Jackpot-Tage (10+ Pool-Treffer): {len(potential_2025)}")
        print()
        for pj in potential_2025:
            print(f"  {pj['datum']}: {pj['pool_hits']} Pool-Zahlen gezogen")
            print(f"    Pool: {pj['pool']}")
            print(f"    Getroffen: {pj['pool_numbers_drawn']}")

            # Analyse rund um diesen Tag
            jp_date = datetime.strptime(pj["datum"], "%d.%m.%Y")
            around = analyze_around_jackpot(draws, jp_date, days_before=5, days_after=5)

            if "error" not in around:
                print(f"\n    Pool-Performance VORHER:")
                for b in around["before"]:
                    print(f"      -{b['days_before_jp']}d: {b['pool_hits']}/{b['pool_size']} Treffer")

                print(f"\n    Pool-Performance NACHHER:")
                for a in around["after"]:
                    print(f"      +{a['days_after_jp']}d: {a['pool_hits']}/{a['pool_size']} Treffer")
            print()
    else:
        print("Keine 10+ Pool-Treffer-Tage in 2025 gefunden.")

    # Speichern
    if args.save:
        output = {
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "monthly_pools_2025",
            "summary": {
                "total_months": total_months,
                "total_days": total_days,
                "total_jackpots_6": total_jackpots,
                "big_hits_8plus": len(all_big_hits),
            },
            "monthly_results": {str(k): v for k, v in monthly_results.items()},
            "all_jackpots": all_jackpots,
            "all_big_hits": all_big_hits,
            "potential_10_jackpots": potential_2025,
        }

        output_path = base_path / "results/2025_monthly_pool_analysis.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
