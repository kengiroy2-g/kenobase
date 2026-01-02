#!/usr/bin/env python3
"""
SMART TICKET GENERATOR V2

Verbesserte Version mit:
1. Strikt Non-Birthday (32-70) als Primaer-Pool
2. Dezentralisierte Auswahl (ueber alle Dekaden verteilt)
3. Exclusion von HOT + Korrektur-Kandidaten
4. Backtesting zur Validierung
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from random import sample, seed, shuffle
from typing import Dict, List, Set, Tuple

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31
NON_BIRTHDAY_NUMBERS = set(range(32, 71))  # 32-70
ALL_NUMBERS = set(range(1, 71))  # 1-70

# Dekaden
DECADES = {
    1: set(range(1, 11)),    # 1-10
    2: set(range(11, 21)),   # 11-20
    3: set(range(21, 31)),   # 21-30
    4: set(range(31, 41)),   # 31-40
    5: set(range(41, 51)),   # 41-50
    6: set(range(51, 61)),   # 51-60
    7: set(range(61, 71)),   # 61-70
}

# Top-20 Korrektur-Zahlen (aus Training 2024)
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
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_status(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Tuple[Set[int], Set[int]]:
    """
    Bestimmt HOT (Momentum) und COLD (Anti-Momentum) Zahlen.
    """
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set(), ALL_NUMBERS

    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1

    hot = {z for z, c in counts.items() if c >= 2}
    cold = ALL_NUMBERS - hot

    return hot, cold


def get_index_values(draws: List[Dict], target_date: datetime, pool: Set[int], lookback: int = 20) -> Dict[int, int]:
    """Berechnet Index-Werte fuer alle Pool-Zahlen."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return {z: 0 for z in pool}

    recent = relevant[-lookback:]
    indices = {}
    for z in pool:
        idx = sum(1 if z in d["zahlen"] else -1 for d in recent)
        indices[z] = idx

    return indices


def build_smart_pool(
    hot: Set[int],
    cold: Set[int],
    indices: Dict[int, int],
    strict_non_birthday: bool = True
) -> Tuple[Set[int], Dict]:
    """
    Baut einen intelligenten Pool.

    Strategie:
    1. Primaer: Non-Birthday (32-70) + COLD
    2. Sekundaer: COLD Birthday nur wenn Pool zu klein
    3. Exclusion: HOT + Top-20 Korrektur
    4. Bevorzuge: Zahlen mit niedrigem Index (unter-repraesentiert)
    """
    stats = {
        "non_birthday_cold": 0,
        "birthday_cold": 0,
        "excluded_hot": 0,
        "excluded_correction": 0,
    }

    # Schritt 1: Non-Birthday + COLD
    primary_pool = NON_BIRTHDAY_NUMBERS & cold
    stats["non_birthday_cold"] = len(primary_pool)

    # Schritt 2: Birthday + COLD (nur wenn noetig)
    secondary_pool = BIRTHDAY_NUMBERS & cold
    stats["birthday_cold"] = len(secondary_pool)

    # Schritt 3: Exclusion - HOT Korrektur-Kandidaten
    hot_correction = hot & TOP_20_CORRECTION
    stats["excluded_correction"] = len(hot_correction)

    # Schritt 4: Exclusion - alle HOT Zahlen
    stats["excluded_hot"] = len(hot)

    # Kombiniere Pools
    if strict_non_birthday:
        pool = primary_pool - hot_correction
    else:
        pool = (primary_pool | secondary_pool) - hot_correction

    # Filtere zusaetzlich alle HOT Zahlen
    pool = pool - hot

    return pool, stats


def select_spread_numbers(pool: Set[int], n: int, indices: Dict[int, int]) -> List[int]:
    """
    Waehlt Zahlen mit guter Streuung ueber Dekaden.

    Strategie:
    1. Versuche aus jeder Dekade mindestens 1 Zahl zu nehmen
    2. Bevorzuge Zahlen mit niedrigem Index (unter-repraesentiert)
    """
    if len(pool) < n:
        return sorted(pool)

    selected = []
    remaining_pool = set(pool)

    # Schritt 1: Eine Zahl aus jeder Dekade (wenn verfuegbar)
    for decade_num, decade_set in sorted(DECADES.items()):
        available = remaining_pool & decade_set
        if available and len(selected) < n:
            # Waehle Zahl mit niedrigstem Index
            best = min(available, key=lambda z: indices.get(z, 0))
            selected.append(best)
            remaining_pool.remove(best)

    # Schritt 2: Auffuellen mit niedrigsten Index-Zahlen
    if len(selected) < n:
        remaining_sorted = sorted(remaining_pool, key=lambda z: indices.get(z, 0))
        selected.extend(remaining_sorted[:n - len(selected)])

    return sorted(selected[:n])


def select_diverse_numbers(pool: Set[int], n: int, indices: Dict[int, int], random_seed: int) -> List[int]:
    """Waehlt diverse Zahlen mit Zufallskomponente."""
    if len(pool) < n:
        return sorted(pool)

    seed(random_seed)

    # Sortiere nach Index (niedrigster zuerst)
    sorted_pool = sorted(pool, key=lambda z: indices.get(z, 0))

    # Nimm Top 50% (unter-repraesentiert) und waehle zufaellig daraus
    top_half = sorted_pool[:len(sorted_pool) // 2 + 1]

    if len(top_half) >= n:
        selected = sample(top_half, n)
    else:
        selected = list(top_half) + sample(list(set(sorted_pool) - set(top_half)), n - len(top_half))

    return sorted(selected)


def generate_tickets(
    pool: Set[int],
    indices: Dict[int, int],
    ticket_types: List[int] = [6, 7]
) -> List[Tuple[str, List[int]]]:
    """Generiert verschiedene Ticket-Strategien."""
    tickets = []

    for typ in ticket_types:
        if len(pool) < typ:
            continue

        # Strategie 1: Spread (ueber Dekaden verteilt)
        spread_ticket = select_spread_numbers(pool, typ, indices)
        tickets.append((f"Typ{typ}-Spread", spread_ticket))

        # Strategie 2: LowIdx (niedrigster Index = am meisten unter-repraesentiert)
        sorted_by_idx = sorted(pool, key=lambda z: indices.get(z, 0))
        low_idx_ticket = sorted(sorted_by_idx[:typ])
        tickets.append((f"Typ{typ}-LowIdx", low_idx_ticket))

        # Strategie 3-5: Diverse (zufaellig aus unter-repraesentierten)
        for i in range(3):
            diverse_ticket = select_diverse_numbers(pool, typ, indices, random_seed=42 + i)
            tickets.append((f"Typ{typ}-Div{i+1}", diverse_ticket))

    return tickets


def test_tickets(
    tickets: List[Tuple[str, List[int]]],
    draws: List[Dict],
    start_date: datetime,
    end_date: datetime
) -> Dict:
    """Testet Tickets gegen Ziehungen."""
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    results = {}
    for name, ticket in tickets:
        ticket_set = set(ticket)
        typ = len(ticket)

        hits = [len(ticket_set & d["zahlen"]) for d in test_draws]
        jackpots = sum(1 for h in hits if h == typ)
        near_miss = sum(1 for h in hits if h == typ - 1)
        avg_hits = sum(hits) / len(hits) if hits else 0
        expected = typ * 20 / 70

        results[name] = {
            "ticket": ticket,
            "typ": typ,
            "n_days": len(test_draws),
            "jackpots": jackpots,
            "near_miss": near_miss,
            "avg_hits": avg_hits,
            "expected": expected,
            "improvement_pct": (avg_hits / expected - 1) * 100 if expected > 0 else 0,
        }

    return results


def main():
    print("=" * 100)
    print("SMART TICKET GENERATOR V2")
    print("Non-Birthday + Anti-Momentum + Index-Optimierung")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    latest_draw = draws[-1]["datum"]
    target_date = latest_draw + timedelta(days=1)

    print(f"\nLetzte Ziehung: {latest_draw.date()}")
    print(f"Tickets fuer: {target_date.date()}")

    # === MOMENTUM-STATUS ===
    print(f"\n{'='*100}")
    print("MOMENTUM-ANALYSE")
    print(f"{'='*100}")

    hot, cold = get_momentum_status(draws, target_date, lookback=3)
    print(f"\nHOT (vermeiden): {sorted(hot)}")
    print(f"HOT Korrektur-Kandidaten: {sorted(hot & TOP_20_CORRECTION)}")

    # === INDEX-WERTE ===
    indices = get_index_values(draws, target_date, ALL_NUMBERS, lookback=20)

    # === SMART POOL ===
    print(f"\n{'='*100}")
    print("SMART POOL GENERIEREN")
    print(f"{'='*100}")

    pool, stats = build_smart_pool(hot, cold, indices, strict_non_birthday=False)

    print(f"\nPool-Statistik:")
    print(f"  Non-Birthday COLD: {stats['non_birthday_cold']}")
    print(f"  Birthday COLD:     {stats['birthday_cold']}")
    print(f"  Ausgeschlossen HOT: {stats['excluded_hot']}")
    print(f"  Ausgeschlossen Korrektur: {stats['excluded_correction']}")

    print(f"\nFinaler Pool ({len(pool)} Zahlen):")
    # Zeige mit Index-Werten
    pool_with_idx = [(z, indices.get(z, 0)) for z in sorted(pool)]
    for z, idx in pool_with_idx:
        marker = "  " if z in NON_BIRTHDAY_NUMBERS else "BD"
        print(f"  {z:>2} (Idx: {idx:>+3}) {marker}")

    # === TICKETS GENERIEREN ===
    print(f"\n{'='*100}")
    print("TICKETS GENERIEREN")
    print(f"{'='*100}")

    tickets = generate_tickets(pool, indices, ticket_types=[6, 7])

    print("\nGenerierte Tickets:")
    for name, ticket in tickets:
        ticket_indices = [indices.get(z, 0) for z in ticket]
        avg_idx = sum(ticket_indices) / len(ticket_indices)
        print(f"  {name:<12}: {ticket} (Avg Idx: {avg_idx:+.1f})")

    # === BACKTEST ===
    print(f"\n{'='*100}")
    print("BACKTEST (letzte 90 Tage)")
    print(f"{'='*100}")

    test_start = latest_draw - timedelta(days=90)
    test_end = latest_draw

    results = test_tickets(tickets, draws, test_start, test_end)

    print(f"\n{'Ticket':<15} {'Zahlen':<30} {'Avg':<8} {'vs.Erw.':<10} {'JP':<5} {'NM'}")
    print("-" * 90)

    for name in sorted(results.keys()):
        res = results[name]
        ticket_str = str(res['ticket'])
        print(f"{name:<15} {ticket_str:<30} {res['avg_hits']:.2f}    {res['improvement_pct']:>+6.1f}%   "
              f"{res['jackpots']:<5} {res['near_miss']}")

    # === VERGLEICH MIT BASELINE ===
    print(f"\n{'='*100}")
    print("VERGLEICH MIT BASELINE (Random aus 1-70)")
    print(f"{'='*100}")

    # Generiere Baseline-Tickets (zufaellig aus allen Zahlen)
    baseline_tickets = []
    seed(42)
    for typ in [6, 7]:
        for i in range(3):
            ticket = sorted(sample(list(ALL_NUMBERS), typ))
            baseline_tickets.append((f"Baseline{typ}_{i+1}", ticket))

    baseline_results = test_tickets(baseline_tickets, draws, test_start, test_end)

    print("\nBaseline-Tickets:")
    for name in sorted(baseline_results.keys()):
        res = baseline_results[name]
        print(f"  {name}: {res['ticket']} → {res['improvement_pct']:+.1f}%")

    # Durchschnitt
    smart_avg_6 = sum(r['improvement_pct'] for n, r in results.items() if "Typ6" in n) / 5
    smart_avg_7 = sum(r['improvement_pct'] for n, r in results.items() if "Typ7" in n) / 5
    base_avg_6 = sum(r['improvement_pct'] for n, r in baseline_results.items() if "Baseline6" in n) / 3
    base_avg_7 = sum(r['improvement_pct'] for n, r in baseline_results.items() if "Baseline7" in n) / 3

    print(f"\nDurchschnittliche Verbesserung:")
    print(f"  Typ 6 - Smart: {smart_avg_6:+.1f}%, Baseline: {base_avg_6:+.1f}%, Differenz: {smart_avg_6 - base_avg_6:+.1f}%")
    print(f"  Typ 7 - Smart: {smart_avg_7:+.1f}%, Baseline: {base_avg_7:+.1f}%, Differenz: {smart_avg_7 - base_avg_7:+.1f}%")

    # === EMPFEHLUNG ===
    print(f"\n{'='*100}")
    print(f"EMPFEHLUNG FUER {target_date.date()}")
    print(f"{'='*100}")

    best_typ6 = max([r for n, r in results.items() if "Typ6" in n], key=lambda x: x['improvement_pct'])
    best_typ7 = max([r for n, r in results.items() if "Typ7" in n], key=lambda x: x['improvement_pct'])

    print(f"\n  *** BESTE TYP 6 ***")
    print(f"  Ticket: {best_typ6['ticket']}")
    print(f"  Backtest: {best_typ6['improvement_pct']:+.1f}% vs. Erwartung")

    print(f"\n  *** BESTE TYP 7 ***")
    print(f"  Ticket: {best_typ7['ticket']}")
    print(f"  Backtest: {best_typ7['improvement_pct']:+.1f}% vs. Erwartung")

    print(f"\n[Generator abgeschlossen]")


if __name__ == "__main__":
    main()
