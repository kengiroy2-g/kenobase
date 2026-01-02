#!/usr/bin/env python3
"""
TEST: Vorhersage-Regel anwenden auf Stichtag 01.05.2025.

Basierend auf Beobachtungen aus Februar-Analyse:
- UNTER-repraesentierte: Hoeherer Index (naeher 0), STEIGENDER Trend
- UEBER-repraesentierte: Niedrigerer Index, STABILER/FALLENDER Trend

Strategie:
- Ticket A: Vermeide vorhergesagte UNTER-Zahlen (hoher Index + steigend)
- Ticket B: Bevorzuge vorhergesagte UEBER-Zahlen (niedriger Index + stabil/fallend)
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from statistics import stdev
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


def calculate_metrics(draws: List[Dict], target_idx: int, zahl: int) -> Dict:
    """Berechnet Metriken fuer eine Zahl."""
    lookback_20 = draws[max(0, target_idx-20):target_idx]
    index = sum(1 if zahl in d["zahlen"] else -1 for d in lookback_20)
    count_20 = sum(1 for d in lookback_20 if zahl in d["zahlen"])
    lookback_3 = draws[max(0, target_idx-3):target_idx]
    mcount = sum(1 for d in lookback_3 if zahl in d["zahlen"])
    return {"index": index, "count_20": count_20, "mcount_3": mcount}


def analyze_pool_at_date(draws: List[Dict], stichtag: datetime) -> Tuple[Set[int], Dict]:
    """Analysiert Pool am Stichtag und klassifiziert Zahlen."""
    # Finde Index
    stichtag_idx = None
    for i, d in enumerate(draws):
        if d["datum"] >= stichtag:
            stichtag_idx = i
            break

    if stichtag_idx is None:
        return set(), {}

    # Pre-Phase (2 Wochen vorher)
    pre_start = stichtag - timedelta(days=14)
    pre_start_idx = None
    for i, d in enumerate(draws):
        if d["datum"] >= pre_start:
            pre_start_idx = i
            break

    # Pool generieren
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum

    # Metriken berechnen
    results = {}
    for z in pool:
        # Pre-Indices sammeln
        pre_indices = []
        for idx in range(pre_start_idx, stichtag_idx):
            m = calculate_metrics(draws, idx, z)
            pre_indices.append(m["index"])

        # Stichtag-Metriken
        stichtag_metrics = calculate_metrics(draws, stichtag_idx, z)

        # Trend
        trend = pre_indices[-1] - pre_indices[0] if len(pre_indices) >= 2 else 0

        results[z] = {
            "stichtag_idx": stichtag_metrics["index"],
            "trend": trend,
            "mcount": stichtag_metrics["mcount_3"],
            "is_hot": stichtag_metrics["mcount_3"] >= 2,
        }

    return pool, results


def predict_under_over(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """
    Vorhersage basierend auf beobachteten Mustern:
    - UNTER: Index naeher 0 (> -5) UND steigender Trend (> +2)
    - UEBER: Index niedriger (< -8) UND stabiler/fallender Trend (<= 0)
    """
    predicted_under = set()
    predicted_over = set()

    for z in pool:
        m = metrics[z]
        idx = m["stichtag_idx"]
        trend = m["trend"]

        # UNTER-Kriterien: hoeherer Index + steigend
        if idx > -5 and trend > 2:
            predicted_under.add(z)

        # UEBER-Kriterien: niedriger Index + stabil/fallend
        if idx < -8 and trend <= 0:
            predicted_over.add(z)

    return predicted_under, predicted_over


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

        hits_per_draw = []
        jackpots = 0

        for draw in test_draws:
            hits = len(ticket_set & draw["zahlen"])
            hits_per_draw.append(hits)
            if hits == typ:
                jackpots += 1

        results[name] = {
            "ticket": ticket,
            "typ": typ,
            "test_days": len(test_draws),
            "jackpots": jackpots,
            "avg_hits": sum(hits_per_draw) / len(hits_per_draw) if hits_per_draw else 0,
            "max_hits": max(hits_per_draw) if hits_per_draw else 0,
            "hit_distribution": {i: hits_per_draw.count(i) for i in range(typ + 1)},
        }

    return results


def main():
    print("=" * 100)
    print("TEST: Vorhersage-Regel auf Stichtag 01.05.2025")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # === STICHTAG: 01.05.2025 ===
    stichtag = datetime(2025, 5, 1)
    test_end = datetime(2025, 7, 31)

    print(f"\nStichtag: {stichtag.date()}")
    print(f"Testperiode: {stichtag.date()} bis {test_end.date()}")

    # Pool und Metriken
    pool, metrics = analyze_pool_at_date(draws, stichtag)
    pool_list = sorted(pool)

    print(f"\n{'='*100}")
    print(f"POOL AM STICHTAG ({len(pool)} Zahlen)")
    print(f"{'='*100}")

    # Zeige alle Zahlen mit Metriken
    print(f"\n{'Zahl':<6} {'Index':<8} {'Trend':<8} {'Hot?':<6} {'Vorhersage'}")
    print("-" * 50)

    predicted_under, predicted_over = predict_under_over(pool, metrics)

    for z in pool_list:
        m = metrics[z]
        hot = "JA" if m["is_hot"] else ""

        if z in predicted_under:
            pred = "UNTER?"
        elif z in predicted_over:
            pred = "UEBER?"
        else:
            pred = "-"

        print(f"{z:<6} {m['stichtag_idx']:>+6}   {m['trend']:>+6.1f}   {hot:<6} {pred}")

    print(f"\n{'='*100}")
    print("VORHERSAGEN")
    print(f"{'='*100}")

    print(f"\n  Vorhergesagt UNTER-repraesentiert: {sorted(predicted_under)}")
    print(f"  Vorhergesagt UEBER-repraesentiert: {sorted(predicted_over)}")

    # === TICKETS ERSTELLEN ===
    print(f"\n{'='*100}")
    print("TICKETS ERSTELLEN")
    print(f"{'='*100}")

    # Ticket-Strategie:
    # A) "Anti-Unter": Pool ohne vorhergesagte UNTER-Zahlen → beste 6/7 aus Rest
    # B) "Pro-Ueber": Vorhergesagte UEBER-Zahlen + Auffuellen

    # Sortiere verbleibende Zahlen nach Index (niedrigster zuerst = "ueberrepraesentiert" Tendenz)
    remaining = pool - predicted_under
    sorted_remaining = sorted(remaining, key=lambda z: metrics[z]["stichtag_idx"])

    # Typ 6 Tickets
    ticket_6a = sorted_remaining[:6]  # Niedrigster Index
    # Alternatives Typ6: UEBER + Auffuellen
    ticket_6b = list(predicted_over)[:6]
    if len(ticket_6b) < 6:
        filler = [z for z in sorted_remaining if z not in ticket_6b]
        ticket_6b.extend(filler[:6-len(ticket_6b)])
    ticket_6b = sorted(ticket_6b[:6])

    # Typ 7 Tickets
    ticket_7a = sorted_remaining[:7]
    ticket_7b = list(predicted_over)[:7]
    if len(ticket_7b) < 7:
        filler = [z for z in sorted_remaining if z not in ticket_7b]
        ticket_7b.extend(filler[:7-len(ticket_7b)])
    ticket_7b = sorted(ticket_7b[:7])

    tickets = [
        ("Typ6-A (Anti-Unter)", ticket_6a),
        ("Typ6-B (Pro-Ueber)", ticket_6b),
        ("Typ7-A (Anti-Unter)", ticket_7a),
        ("Typ7-B (Pro-Ueber)", ticket_7b),
    ]

    print("\n  Generierte Tickets:")
    for name, ticket in tickets:
        print(f"    {name}: {ticket}")

    # === TICKETS TESTEN ===
    print(f"\n{'='*100}")
    print("TICKET-TEST GEGEN ZIEHUNGEN")
    print(f"{'='*100}")

    results = test_tickets(tickets, draws, stichtag, test_end)

    for name, res in results.items():
        print(f"\n  {name}:")
        print(f"    Ticket: {res['ticket']}")
        print(f"    Test-Tage: {res['test_days']}")
        print(f"    Jackpots ({res['typ']}/{res['typ']}): {res['jackpots']}")
        print(f"    Avg Treffer: {res['avg_hits']:.2f}")
        print(f"    Max Treffer: {res['max_hits']}")
        print(f"    Verteilung: ", end="")
        for hits, count in sorted(res['hit_distribution'].items()):
            print(f"{hits}:{count} ", end="")
        print()

    # === VERGLEICH MIT ERWARTUNG ===
    print(f"\n{'='*100}")
    print("VERGLEICH MIT ERWARTUNG (Hypergeometrisch)")
    print(f"{'='*100}")

    # Erwartete Treffer bei n aus 70 gewählt, 20 gezogen
    # E[X] = n * 20/70 = n * 0.2857
    for name, res in results.items():
        typ = res['typ']
        expected_hits = typ * 20 / 70
        actual_hits = res['avg_hits']
        diff_pct = ((actual_hits - expected_hits) / expected_hits) * 100

        print(f"\n  {name}:")
        print(f"    Erwartet: {expected_hits:.2f} Treffer/Tag")
        print(f"    Tatsaechlich: {actual_hits:.2f} Treffer/Tag")
        print(f"    Differenz: {diff_pct:+.1f}%")

    # === JACKPOT-ANALYSE (tatsaechlich getroffen?) ===
    print(f"\n{'='*100}")
    print("ANALYSE: Welche Zahlen waren in den Jackpots TATSAECHLICH?")
    print(f"{'='*100}")

    # Finde alle Ziehungen wo Pool >= 6 oder >= 7 Treffer hatte
    test_draws = [d for d in draws if stichtag <= d["datum"] <= test_end]

    jackpot_6_numbers = defaultdict(int)
    jackpot_7_numbers = defaultdict(int)
    jackpot_6_count = 0
    jackpot_7_count = 0

    for draw in test_draws:
        pool_hits = pool & draw["zahlen"]

        if len(pool_hits) >= 6:
            jackpot_6_count += 1
            for z in pool_hits:
                jackpot_6_numbers[z] += 1

        if len(pool_hits) >= 7:
            jackpot_7_count += 1
            for z in pool_hits:
                jackpot_7_numbers[z] += 1

    print(f"\n  Ziehungen mit >= 6 Pool-Treffern: {jackpot_6_count}")
    print(f"  Ziehungen mit >= 7 Pool-Treffern: {jackpot_7_count}")

    if jackpot_6_numbers:
        print(f"\n  Zahlen in >= 6 Treffern (Haeufigkeit):")
        sorted_6 = sorted(jackpot_6_numbers.items(), key=lambda x: x[1], reverse=True)
        for z, count in sorted_6:
            pred = ""
            if z in predicted_under:
                pred = "(vorh. UNTER)"
            elif z in predicted_over:
                pred = "(vorh. UEBER)"
            print(f"    {z}: {count}x {pred}")

    # === FINALE AUSWERTUNG ===
    print(f"\n{'='*100}")
    print("FINALE AUSWERTUNG: War die Vorhersage korrekt?")
    print(f"{'='*100}")

    # Berechne tatsaechliche Unter/Ueber-Repraesentierung
    total_pool_in_draws = {z: 0 for z in pool}
    for draw in test_draws:
        for z in pool:
            if z in draw["zahlen"]:
                total_pool_in_draws[z] += 1

    expected_per_number = len(test_draws) * 20 / 70
    actual_under = {z for z in pool if total_pool_in_draws[z] < expected_per_number * 0.85}
    actual_over = {z for z in pool if total_pool_in_draws[z] > expected_per_number * 1.15}

    print(f"\n  Erwartete Ziehungen pro Zahl: {expected_per_number:.1f}")
    print(f"\n  TATSAECHLICH unter-repraesentiert (<85%): {sorted(actual_under)}")
    print(f"  TATSAECHLICH ueber-repraesentiert (>115%): {sorted(actual_over)}")

    print(f"\n  VORHERSAGE vs. REALITAET:")
    print(f"\n    Vorhergesagt UNTER: {sorted(predicted_under)}")
    print(f"    Davon KORREKT:      {sorted(predicted_under & actual_under)}")
    print(f"    Davon FALSCH:       {sorted(predicted_under - actual_under)}")

    print(f"\n    Vorhergesagt UEBER: {sorted(predicted_over)}")
    print(f"    Davon KORREKT:      {sorted(predicted_over & actual_over)}")
    print(f"    Davon FALSCH:       {sorted(predicted_over - actual_over)}")

    # Precision/Recall
    if predicted_under:
        precision_under = len(predicted_under & actual_under) / len(predicted_under) * 100
        print(f"\n    Precision UNTER: {precision_under:.1f}%")

    if predicted_over:
        precision_over = len(predicted_over & actual_over) / len(predicted_over) * 100
        print(f"    Precision UEBER: {precision_over:.1f}%")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
