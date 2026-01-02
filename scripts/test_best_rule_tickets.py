#!/usr/bin/env python3
"""
TEST: Beste Regel (Extreme Index Quartile) mit Tickets.

Regel:
- UNTER = Index im oberen Quartil (hoechste 25%)
- UEBER = Index im unteren Quartil (niedrigste 25%)

Ticket-Strategie:
- Vermeide vorhergesagte UNTER-Zahlen
- Bevorzuge vorhergesagte UEBER-Zahlen
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
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
    """Holt Momentum-Zahlen."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()
    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def calculate_index(draws: List[Dict], target_idx: int, zahl: int) -> int:
    """Berechnet Index (letzte 20 Tage)."""
    lookback_20 = draws[max(0, target_idx-20):target_idx]
    return sum(1 if zahl in d["zahlen"] else -1 for d in lookback_20)


def apply_extreme_index_rule(pool: Set[int], indices: Dict[int, int]) -> Tuple[Set[int], Set[int]]:
    """Extreme Index Quartile Regel."""
    sorted_indices = sorted(indices.items(), key=lambda x: x[1])
    n = len(sorted_indices)
    q25_idx = n // 4
    q75_idx = 3 * n // 4

    # UEBER = niedrigstes Quartil (Index am niedrigsten)
    pred_over = {z for z, _ in sorted_indices[:q25_idx]}

    # UNTER = hoechstes Quartil (Index am hoechsten)
    pred_under = {z for z, _ in sorted_indices[q75_idx:]}

    return pred_under, pred_over


def test_tickets_detailed(
    tickets: List[Tuple[str, List[int]]],
    draws: List[Dict],
    start_date: datetime,
    end_date: datetime
) -> Dict:
    """Testet Tickets mit detaillierten Statistiken."""
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    results = {}
    for name, ticket in tickets:
        ticket_set = set(ticket)
        typ = len(ticket)

        hits_per_draw = []
        jackpot_dates = []

        for draw in test_draws:
            hits = len(ticket_set & draw["zahlen"])
            hits_per_draw.append(hits)
            if hits == typ:
                jackpot_dates.append(draw["datum_str"])

        # Berechne Near-Miss (typ-1 Treffer)
        near_misses = sum(1 for h in hits_per_draw if h == typ - 1)

        results[name] = {
            "ticket": ticket,
            "typ": typ,
            "test_days": len(test_draws),
            "jackpots": len(jackpot_dates),
            "jackpot_dates": jackpot_dates,
            "near_misses": near_misses,
            "avg_hits": sum(hits_per_draw) / len(hits_per_draw) if hits_per_draw else 0,
            "max_hits": max(hits_per_draw) if hits_per_draw else 0,
            "hit_distribution": {i: hits_per_draw.count(i) for i in range(typ + 1)},
        }

    return results


def run_stichtag_test(draws: List[Dict], stichtag: datetime, test_end: datetime):
    """Fuehrt Test fuer einen Stichtag durch."""
    print(f"\n{'='*100}")
    print(f"STICHTAG: {stichtag.date()}")
    print(f"Testperiode: {stichtag.date()} bis {test_end.date()}")
    print(f"{'='*100}")

    # Index finden
    stichtag_idx = next(i for i, d in enumerate(draws) if d["datum"] >= stichtag)

    # Pool generieren
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum

    # Indices berechnen
    indices = {z: calculate_index(draws, stichtag_idx, z) for z in pool}

    # Regel anwenden
    pred_under, pred_over = apply_extreme_index_rule(pool, indices)

    print(f"\n  Pool ({len(pool)} Zahlen): {sorted(pool)}")
    print(f"\n  Indices am Stichtag:")
    sorted_by_idx = sorted(indices.items(), key=lambda x: x[1])
    for z, idx in sorted_by_idx:
        marker = ""
        if z in pred_under:
            marker = " ← UNTER (vermeiden)"
        elif z in pred_over:
            marker = " ← UEBER (bevorzugen)"
        print(f"    {z:>3}: {idx:>+3}{marker}")

    print(f"\n  Vorhergesagt UNTER (vermeiden): {sorted(pred_under)}")
    print(f"  Vorhergesagt UEBER (bevorzugen): {sorted(pred_over)}")

    # Tickets erstellen
    # Pool ohne UNTER, sortiert nach Index (niedrigster zuerst = UEBER Tendenz)
    safe_pool = pool - pred_under
    sorted_safe = sorted(safe_pool, key=lambda z: indices[z])

    # Typ 6 Tickets
    ticket_6_ueber = sorted(list(pred_over)[:6])
    if len(ticket_6_ueber) < 6:
        filler = [z for z in sorted_safe if z not in ticket_6_ueber]
        ticket_6_ueber = sorted(ticket_6_ueber + filler[:6-len(ticket_6_ueber)])

    ticket_6_safe = sorted(sorted_safe[:6])

    # Typ 7 Tickets
    ticket_7_ueber = sorted(list(pred_over)[:7])
    if len(ticket_7_ueber) < 7:
        filler = [z for z in sorted_safe if z not in ticket_7_ueber]
        ticket_7_ueber = sorted(ticket_7_ueber + filler[:7-len(ticket_7_ueber)])

    ticket_7_safe = sorted(sorted_safe[:7])

    tickets = [
        ("Typ6-UEBER", ticket_6_ueber),
        ("Typ6-SAFE", ticket_6_safe),
        ("Typ7-UEBER", ticket_7_ueber),
        ("Typ7-SAFE", ticket_7_safe),
    ]

    print(f"\n  TICKETS:")
    for name, ticket in tickets:
        print(f"    {name}: {ticket}")

    # Testen
    results = test_tickets_detailed(tickets, draws, stichtag, test_end)

    print(f"\n  ERGEBNISSE:")
    print(f"  {'Ticket':<15} {'Jackpots':<10} {'NearMiss':<10} {'AvgHits':<10} {'vs.Erw.':<10}")
    print("  " + "-" * 60)

    for name, res in results.items():
        typ = res['typ']
        expected = typ * 20 / 70
        diff_pct = ((res['avg_hits'] - expected) / expected) * 100
        print(f"  {name:<15} {res['jackpots']:<10} {res['near_misses']:<10} "
              f"{res['avg_hits']:<10.2f} {diff_pct:>+8.1f}%")

    return results


def main():
    print("=" * 100)
    print("TEST: Beste Regel (Extreme Index Quartile) mit Tickets")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Teste mehrere Stichtage
    stichtage = [
        datetime(2025, 2, 1),
        datetime(2025, 3, 1),
        datetime(2025, 4, 1),
        datetime(2025, 5, 1),
    ]
    test_end = datetime(2025, 7, 31)

    all_results = []

    for stichtag in stichtage:
        results = run_stichtag_test(draws, stichtag, test_end)
        all_results.append((stichtag, results))

    # === AGGREGIERTE STATISTIK ===
    print(f"\n\n{'='*100}")
    print("AGGREGIERTE STATISTIK UEBER ALLE STICHTAGE")
    print(f"{'='*100}")

    ticket_types = ["Typ6-UEBER", "Typ6-SAFE", "Typ7-UEBER", "Typ7-SAFE"]

    for ticket_type in ticket_types:
        total_jackpots = sum(res[ticket_type]['jackpots'] for _, res in all_results)
        total_near_misses = sum(res[ticket_type]['near_misses'] for _, res in all_results)
        avg_hits_list = [res[ticket_type]['avg_hits'] for _, res in all_results]
        overall_avg = sum(avg_hits_list) / len(avg_hits_list)

        typ = 6 if "6" in ticket_type else 7
        expected = typ * 20 / 70
        diff_pct = ((overall_avg - expected) / expected) * 100

        print(f"\n  {ticket_type}:")
        print(f"    Gesamt Jackpots: {total_jackpots}")
        print(f"    Gesamt Near-Misses: {total_near_misses}")
        print(f"    Durchschnitt Treffer: {overall_avg:.2f} (vs. Erw. {expected:.2f} = {diff_pct:+.1f}%)")

    # === VERGLEICH: UEBER vs SAFE ===
    print(f"\n\n{'='*100}")
    print("VERGLEICH: UEBER-Tickets vs SAFE-Tickets")
    print(f"{'='*100}")

    for typ in [6, 7]:
        ueber_key = f"Typ{typ}-UEBER"
        safe_key = f"Typ{typ}-SAFE"

        ueber_avg = sum(res[ueber_key]['avg_hits'] for _, res in all_results) / len(all_results)
        safe_avg = sum(res[safe_key]['avg_hits'] for _, res in all_results) / len(all_results)

        ueber_jp = sum(res[ueber_key]['jackpots'] for _, res in all_results)
        safe_jp = sum(res[safe_key]['jackpots'] for _, res in all_results)

        print(f"\n  Typ {typ}:")
        print(f"    UEBER: {ueber_avg:.2f} Treffer/Tag, {ueber_jp} Jackpots")
        print(f"    SAFE:  {safe_avg:.2f} Treffer/Tag, {safe_jp} Jackpots")
        print(f"    Differenz: {ueber_avg - safe_avg:+.3f} Treffer/Tag")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
