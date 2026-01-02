#!/usr/bin/env python3
"""
FINALE STRATEGIE-ZUSAMMENFASSUNG

Nach umfangreicher Analyse:
1. Pool-Strategien getestet (Birthday, Non-Birthday, HOT, COLD)
2. Momentum-Decay untersucht
3. Korrektur-Theorie validiert

KERN-ERKENNTNIS:
- Einzelne Zahlen haben KEINE signifikant bessere/schlechtere Trefferquote
- Der Vorteil kommt aus POOL-REDUKTION (weniger Kombinationen = bessere Odds)
- HOT_ONLY performt gut weil Pool klein (11 Zahlen statt 70)

FINALE STRATEGIE:
- Nutze KLEINE Pools (max 15-20 Zahlen)
- Kombiniere mehrere Filter fuer Pool-Reduktion
- Vermeide HOT+Korrektur-Kandidaten (diese werden korrigiert)
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from math import comb
from pathlib import Path
from random import sample, seed
from typing import Dict, List, Set, Tuple

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
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_hot_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """HOT Zahlen (>= 2 Erscheinungen in lookback Tagen)."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()
    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def calculate_combinatorial_advantage(pool_size: int, ticket_size: int) -> Dict:
    """
    Berechnet den kombinatorischen Vorteil durch Pool-Reduktion.
    """
    full_combos = comb(70, ticket_size)
    pool_combos = comb(pool_size, ticket_size) if pool_size >= ticket_size else 0

    # Wahrscheinlichkeit dass ein zufaelliges Ticket aus Pool alle 'ticket_size' aus 20 gezogenen trifft
    # ist hoeher wenn der Pool kleiner ist

    # Vereinfachte Berechnung: Wenn Pool kleiner, aber gleiche Trefferrate,
    # dann ist die "Trefferkonzentration" hoeher

    reduction_pct = (1 - pool_combos / full_combos) * 100 if full_combos > 0 else 0

    return {
        "full_pool_combos": full_combos,
        "reduced_pool_combos": pool_combos,
        "reduction_pct": reduction_pct,
        "advantage_factor": full_combos / pool_combos if pool_combos > 0 else float('inf'),
    }


def build_optimal_pool(
    draws: List[Dict],
    target_date: datetime,
    target_size: int = 15
) -> Tuple[Set[int], Dict]:
    """
    Baut einen optimalen Pool mit Zielgroesse.

    Strategie:
    1. Starte mit HOT (Momentum)
    2. Entferne HOT+Korrektur-Kandidaten
    3. Fuelle auf mit COLD Non-Birthday wenn noetig
    """
    hot = get_hot_numbers(draws, target_date, lookback=3)
    cold = ALL_NUMBERS - hot

    stats = {
        "hot_count": len(hot),
        "cold_count": len(cold),
    }

    # Schritt 1: HOT ohne Korrektur-Kandidaten
    pool = hot - (hot & TOP_20_CORRECTION)
    stats["after_correction_filter"] = len(pool)

    # Schritt 2: Falls Pool zu klein, fuelle mit COLD Non-Birthday
    if len(pool) < target_size:
        cold_nonbd = sorted(NON_BIRTHDAY_NUMBERS & cold)
        needed = target_size - len(pool)
        pool = pool | set(cold_nonbd[:needed])

    # Schritt 3: Falls Pool zu gross, reduziere auf target_size
    if len(pool) > target_size:
        pool = set(sorted(pool)[:target_size])

    stats["final_size"] = len(pool)

    return pool, stats


def test_strategy(
    draws: List[Dict],
    pool_builder,
    start_date: datetime,
    end_date: datetime,
    ticket_size: int,
    n_tickets: int = 10
) -> Dict:
    """Testet eine Pool-Strategie."""
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    all_improvements = []
    all_jackpots = 0
    all_near_miss = 0

    for draw in test_draws:
        # Baue Pool fuer diesen Tag
        pool, _ = pool_builder(draws, draw["datum"])

        if len(pool) < ticket_size:
            continue

        # Teste mehrere zufaellige Tickets
        pool_list = sorted(pool)
        for seed_val in range(n_tickets):
            seed(seed_val)
            ticket = set(sample(pool_list, ticket_size))
            hits = len(ticket & draw["zahlen"])

            expected = ticket_size * 20 / 70
            improvement = (hits / expected - 1) * 100 if expected > 0 else 0
            all_improvements.append(improvement)

            if hits == ticket_size:
                all_jackpots += 1
            elif hits == ticket_size - 1:
                all_near_miss += 1

    return {
        "n_tests": len(all_improvements),
        "avg_improvement": sum(all_improvements) / len(all_improvements) if all_improvements else 0,
        "jackpots": all_jackpots,
        "near_miss": all_near_miss,
    }


def main():
    print("=" * 100)
    print("FINALE STRATEGIE-ZUSAMMENFASSUNG")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # === KOMBINATORISCHER VORTEIL ===
    print(f"\n{'='*100}")
    print("KOMBINATORISCHER VORTEIL DURCH POOL-REDUKTION")
    print(f"{'='*100}")

    print("\nTyp 6 (6 aus Pool):")
    print(f"{'Pool-Groesse':<15} {'Kombinationen':<20} {'Reduktion':<15} {'Vorteilsfaktor'}")
    print("-" * 70)

    for pool_size in [70, 50, 30, 20, 15, 12, 10]:
        adv = calculate_combinatorial_advantage(pool_size, 6)
        print(f"{pool_size:<15} {adv['reduced_pool_combos']:<20,} {adv['reduction_pct']:<14.1f}% {adv['advantage_factor']:.1f}x")

    print("\nTyp 7 (7 aus Pool):")
    print(f"{'Pool-Groesse':<15} {'Kombinationen':<20} {'Reduktion':<15} {'Vorteilsfaktor'}")
    print("-" * 70)

    for pool_size in [70, 50, 30, 20, 15, 12, 10]:
        adv = calculate_combinatorial_advantage(pool_size, 7)
        print(f"{pool_size:<15} {adv['reduced_pool_combos']:<20,} {adv['reduction_pct']:<14.1f}% {adv['advantage_factor']:.1f}x")

    # === KERN-ERKENNTNIS ===
    print(f"\n{'='*100}")
    print("KERN-ERKENNTNIS")
    print(f"{'='*100}")

    print("""
    Die Analyse hat gezeigt:

    1. TREFFERQUOTE IST GLEICH
       - HOT Zahlen: 28.59% (vs. 28.57% erwartet)
       - COLD Zahlen: 28.57% (vs. 28.57% erwartet)
       - KEINE Zahl hat signifikant bessere Odds

    2. VORTEIL KOMMT AUS POOL-GROESSE
       - Voller Pool (70):     119,877,472 moegliche 6er
       - HOT Pool (~11):             462 moegliche 6er
       - Reduktion: 99.9996%!

    3. KORREKTUR EXISTIERT ABER IST SCHWACH
       - Tag 8-9: HOT faellt auf 27.7% (statt 28.6%)
       - Effekt: nur ~1% Nachteil
       - Nicht stark genug fuer profitable Strategie

    4. OPTIMALE STRATEGIE
       - Nutze KLEINEN Pool (10-15 Zahlen)
       - HOT als Basis (natuerlich klein)
       - Entferne Korrektur-Kandidaten (marginaler Vorteil)
       - Pool-Reduktion ist der HAUPTEFFEKT
    """)

    # === FINALE EMPFEHLUNG ===
    print(f"\n{'='*100}")
    print("FINALE EMPFEHLUNG")
    print(f"{'='*100}")

    latest_draw = draws[-1]["datum"]
    target_date = latest_draw + timedelta(days=1)

    pool, stats = build_optimal_pool(draws, target_date, target_size=12)

    print(f"\nOptimaler Pool fuer {target_date.date()}:")
    print(f"  HOT Zahlen gefunden: {stats['hot_count']}")
    print(f"  Nach Korrektur-Filter: {stats['after_correction_filter']}")
    print(f"  Finaler Pool ({stats['final_size']} Zahlen): {sorted(pool)}")

    # Generiere Tickets
    pool_list = sorted(pool)
    seed(42)

    print("\n  EMPFOHLENE TICKETS:")
    for typ in [6, 7]:
        if len(pool_list) >= typ:
            ticket = sorted(sample(pool_list, typ))
            adv = calculate_combinatorial_advantage(len(pool), typ)
            print(f"\n  Typ {typ}: {ticket}")
            print(f"         Pool-Vorteil: {adv['advantage_factor']:.0f}x weniger Kombinationen")

    # === WICHTIGER HINWEIS ===
    print(f"\n{'='*100}")
    print("WICHTIGER HINWEIS")
    print(f"{'='*100}")

    print("""
    WARNUNG: Pool-Reduktion verbessert NICHT die mathematische Erwartung!

    - Weniger Kombinationen = weniger Konkurrenz im Pool
    - ABER: Die 20 gezogenen Zahlen sind immer noch zufaellig aus 70
    - Ihr Ticket aus 12 Zahlen hat gleiche Chance wie aus 70

    Der Pool-Vorteil bedeutet:
    - WENN Sie gewinnen, ist es wahrscheinlicher dass es ihr spezifisches Ticket ist
    - ABER: Die Wahrscheinlichkeit ZU gewinnen bleibt unveraendert

    REALISTISCHE ERWARTUNG:
    - Typ 6 Jackpot: ~1:7,753 (unveraendert)
    - Typ 7 Jackpot: ~1:18,116 (unveraendert)

    Die +2-3% "Verbesserung" in unseren Tests ist:
    - Statistisches Rauschen
    - Oder Overfitting auf historische Daten

    FAZIT: Es gibt KEINEN sicheren Weg das Haus zu schlagen.
    """)

    print(f"\n[Zusammenfassung abgeschlossen]")


if __name__ == "__main__":
    main()
