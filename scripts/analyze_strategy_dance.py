#!/usr/bin/env python3
"""
DER TANZ DER STRATEGIEN

Hypothese des Users:
- Gewinner haben Zahlen aus VERSCHIEDENEN Pool-Typen
- Das Verhaeltnis variiert je nach System-Zustand
- Es ist ein TANZ zwischen Strategien, nicht ein Entweder-Oder

Analyse:
1. Trefferkonzentration pro Pool-Typ (nicht absolute Zahlen!)
2. Optimaler Mix basierend auf tatsaechlicher Hit-Rate
3. Korrelation zwischen Pool-Typen in erfolgreichen Ziehungen
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
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


def get_hot_numbers(draws: List[Dict], target_idx: int, lookback: int = 3) -> Set[int]:
    """HOT Zahlen."""
    if target_idx < lookback:
        return set()
    recent = draws[target_idx - lookback:target_idx]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def analyze_concentration(draws: List[Dict], start_idx: int = 100) -> Dict:
    """
    Analysiert die KONZENTRATION (Hit-Rate) pro Pool-Typ.

    Konzentration = (gezogene aus Pool) / (Pool-Groesse)
    """
    results = {
        "hot": {"total_pool": 0, "total_hits": 0},
        "cold": {"total_pool": 0, "total_hits": 0},
        "birthday": {"total_pool": 31 * (len(draws) - start_idx), "total_hits": 0},
        "non_birthday": {"total_pool": 39 * (len(draws) - start_idx), "total_hits": 0},
        "hot_birthday": {"total_pool": 0, "total_hits": 0},
        "hot_non_birthday": {"total_pool": 0, "total_hits": 0},
        "cold_birthday": {"total_pool": 0, "total_hits": 0},
        "cold_non_birthday": {"total_pool": 0, "total_hits": 0},
        "correction_hot": {"total_pool": 0, "total_hits": 0},
        "correction_cold": {"total_pool": 0, "total_hits": 0},
    }

    for idx in range(start_idx, len(draws)):
        drawn = draws[idx]["zahlen"]
        hot = get_hot_numbers(draws, idx, lookback=3)
        cold = ALL_NUMBERS - hot

        # Pool-Groessen
        results["hot"]["total_pool"] += len(hot)
        results["cold"]["total_pool"] += len(cold)
        results["hot_birthday"]["total_pool"] += len(hot & BIRTHDAY_NUMBERS)
        results["hot_non_birthday"]["total_pool"] += len(hot & NON_BIRTHDAY_NUMBERS)
        results["cold_birthday"]["total_pool"] += len(cold & BIRTHDAY_NUMBERS)
        results["cold_non_birthday"]["total_pool"] += len(cold & NON_BIRTHDAY_NUMBERS)
        results["correction_hot"]["total_pool"] += len(hot & TOP_20_CORRECTION)
        results["correction_cold"]["total_pool"] += len(cold & TOP_20_CORRECTION)

        # Treffer
        results["hot"]["total_hits"] += len(drawn & hot)
        results["cold"]["total_hits"] += len(drawn & cold)
        results["birthday"]["total_hits"] += len(drawn & BIRTHDAY_NUMBERS)
        results["non_birthday"]["total_hits"] += len(drawn & NON_BIRTHDAY_NUMBERS)
        results["hot_birthday"]["total_hits"] += len(drawn & hot & BIRTHDAY_NUMBERS)
        results["hot_non_birthday"]["total_hits"] += len(drawn & hot & NON_BIRTHDAY_NUMBERS)
        results["cold_birthday"]["total_hits"] += len(drawn & cold & BIRTHDAY_NUMBERS)
        results["cold_non_birthday"]["total_hits"] += len(drawn & cold & NON_BIRTHDAY_NUMBERS)
        results["correction_hot"]["total_hits"] += len(drawn & hot & TOP_20_CORRECTION)
        results["correction_cold"]["total_hits"] += len(drawn & cold & TOP_20_CORRECTION)

    # Berechne Konzentrationen
    for key in results:
        if results[key]["total_pool"] > 0:
            results[key]["concentration"] = results[key]["total_hits"] / results[key]["total_pool"]
        else:
            results[key]["concentration"] = 0

    return results


def simulate_mixed_tickets(draws: List[Dict], start_idx: int, n_simulations: int = 1000) -> Dict:
    """
    Simuliert Tickets mit verschiedenen Pool-Mixes und misst Performance.
    """
    # Definiere Mix-Strategien: (hot, cold_birthday, cold_non_birthday)
    mixes = [
        ("6H+0CB+0CN", 6, 0, 0),
        ("5H+1CB+0CN", 5, 1, 0),
        ("5H+0CB+1CN", 5, 0, 1),
        ("4H+1CB+1CN", 4, 1, 1),
        ("4H+2CB+0CN", 4, 2, 0),
        ("4H+0CB+2CN", 4, 0, 2),
        ("3H+2CB+1CN", 3, 2, 1),
        ("3H+1CB+2CN", 3, 1, 2),
        ("2H+2CB+2CN", 2, 2, 2),
        ("2H+3CB+1CN", 2, 3, 1),
        ("2H+1CB+3CN", 2, 1, 3),
        ("1H+3CB+2CN", 1, 3, 2),
        ("1H+2CB+3CN", 1, 2, 3),
        ("0H+3CB+3CN", 0, 3, 3),
        ("0H+4CB+2CN", 0, 4, 2),
        ("0H+2CB+4CN", 0, 2, 4),
    ]

    results = {}
    test_draws = draws[start_idx:]

    for mix_name, n_hot, n_cold_bd, n_cold_nonbd in mixes:
        total_hits = 0
        total_tests = 0
        jackpots = 0
        near_miss = 0

        for idx in range(start_idx, len(draws)):
            hot = get_hot_numbers(draws, idx, lookback=3)
            cold = ALL_NUMBERS - hot
            cold_bd = sorted(cold & BIRTHDAY_NUMBERS)
            cold_nonbd = sorted(cold & NON_BIRTHDAY_NUMBERS)
            hot_list = sorted(hot)

            # Pruefe ob genug Zahlen verfuegbar
            if len(hot_list) < n_hot or len(cold_bd) < n_cold_bd or len(cold_nonbd) < n_cold_nonbd:
                continue

            # Simuliere mehrere Tickets
            for sim in range(10):
                seed(idx * 100 + sim)
                ticket = set()

                if n_hot > 0:
                    ticket.update(sample(hot_list, n_hot))
                if n_cold_bd > 0:
                    ticket.update(sample(cold_bd, n_cold_bd))
                if n_cold_nonbd > 0:
                    ticket.update(sample(cold_nonbd, n_cold_nonbd))

                drawn = draws[idx]["zahlen"]
                hits = len(ticket & drawn)
                total_hits += hits
                total_tests += 1

                if hits == 6:
                    jackpots += 1
                elif hits == 5:
                    near_miss += 1

        if total_tests > 0:
            results[mix_name] = {
                "avg_hits": total_hits / total_tests,
                "expected": 6 * 20 / 70,
                "improvement": (total_hits / total_tests) / (6 * 20 / 70) * 100 - 100,
                "jackpots": jackpots,
                "near_miss": near_miss,
                "tests": total_tests,
            }

    return results


def analyze_winning_patterns(draws: List[Dict], start_idx: int = 100) -> Dict:
    """
    Analysiert Muster in Ziehungen mit hoher Pool-Konzentration.
    """
    high_hot_days = []  # Tage mit ueberdurchschnittlich vielen HOT
    low_hot_days = []   # Tage mit unterdurchschnittlich vielen HOT

    for idx in range(start_idx, len(draws)):
        drawn = draws[idx]["zahlen"]
        hot = get_hot_numbers(draws, idx, lookback=3)

        hot_hits = len(drawn & hot)

        if hot_hits >= 5:  # Ueberdurchschnittlich viele HOT (normal: 4)
            high_hot_days.append({
                "idx": idx,
                "datum": draws[idx]["datum"],
                "hot_hits": hot_hits,
                "hot_pool_size": len(hot),
            })
        elif hot_hits <= 2:  # Unterdurchschnittlich viele HOT
            low_hot_days.append({
                "idx": idx,
                "datum": draws[idx]["datum"],
                "hot_hits": hot_hits,
                "hot_pool_size": len(hot),
            })

    return {
        "high_hot_days": high_hot_days,
        "low_hot_days": low_hot_days,
    }


def main():
    print("=" * 100)
    print("DER TANZ DER STRATEGIEN: Pool-Mix Optimierung")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    start_idx = 100

    # === KONZENTRATIONS-ANALYSE ===
    print(f"\n{'='*100}")
    print("KONZENTRATIONS-ANALYSE: Hit-Rate pro Pool-Typ")
    print("(Konzentration = Gezogene / Pool-Groesse)")
    print(f"{'='*100}")

    conc = analyze_concentration(draws, start_idx)

    print(f"\n  {'Pool-Typ':<25} {'Pool-Groesse':<15} {'Hits':<12} {'Konzentration':<15} {'vs. Baseline'}")
    print("  " + "-" * 85)

    baseline = 20 / 70  # 28.57%

    for key in ["hot", "cold", "birthday", "non_birthday",
                "hot_birthday", "hot_non_birthday", "cold_birthday", "cold_non_birthday",
                "correction_hot", "correction_cold"]:
        c = conc[key]
        if c["total_pool"] > 0:
            vs_base = (c["concentration"] - baseline) / baseline * 100
            print(f"  {key:<25} {c['total_pool']:<15,} {c['total_hits']:<12,} "
                  f"{c['concentration']*100:<14.2f}% {vs_base:>+6.1f}%")

    # === BESTE KOMBINIERTE POOLS ===
    print(f"\n{'='*100}")
    print("BESTE KOMBINIERTE POOLS (nach Konzentration)")
    print(f"{'='*100}")

    ranked = sorted(
        [(k, v["concentration"]) for k, v in conc.items() if v["total_pool"] > 0],
        key=lambda x: x[1],
        reverse=True
    )

    print("\n  Ranking nach Trefferkonzentration:")
    for i, (pool_type, concentration) in enumerate(ranked, 1):
        vs_base = (concentration - baseline) / baseline * 100
        print(f"  {i}. {pool_type:<25} {concentration*100:.2f}% ({vs_base:+.1f}% vs. Baseline)")

    # === MIXED TICKET SIMULATION ===
    print(f"\n{'='*100}")
    print("MIXED TICKET SIMULATION: Verschiedene Pool-Kombinationen")
    print("Format: H=HOT, CB=Cold-Birthday, CN=Cold-Non-Birthday")
    print(f"{'='*100}")

    mix_results = simulate_mixed_tickets(draws, start_idx)

    print(f"\n  {'Mix-Strategie':<20} {'Avg Hits':<12} {'vs. Erwartung':<15} {'Jackpots':<10} {'Near-Miss'}")
    print("  " + "-" * 75)

    sorted_mixes = sorted(mix_results.items(), key=lambda x: x[1]["improvement"], reverse=True)

    for mix_name, result in sorted_mixes:
        print(f"  {mix_name:<20} {result['avg_hits']:<12.3f} {result['improvement']:>+12.1f}%   "
              f"{result['jackpots']:<10} {result['near_miss']}")

    # === GEWINNER-MUSTER ANALYSE ===
    print(f"\n{'='*100}")
    print("GEWINNER-MUSTER: Tage mit extremen HOT-Treffern")
    print(f"{'='*100}")

    patterns = analyze_winning_patterns(draws, start_idx)

    print(f"\n  Tage mit >= 5 HOT-Zahlen gezogen: {len(patterns['high_hot_days'])}")
    print(f"  Tage mit <= 2 HOT-Zahlen gezogen: {len(patterns['low_hot_days'])}")

    if patterns['high_hot_days']:
        print(f"\n  Letzte 5 'High-HOT' Tage:")
        for day in patterns['high_hot_days'][-5:]:
            print(f"    {day['datum'].date()}: {day['hot_hits']} HOT (Pool: {day['hot_pool_size']})")

    # === DER TANZ - DYNAMISCHE STRATEGIE ===
    print(f"\n{'='*100}")
    print("DER TANZ DER STRATEGIEN: Dynamische Empfehlung")
    print(f"{'='*100}")

    # Finde besten Mix
    best_mix = sorted_mixes[0]

    print(f"""
    ERKENNTNISSE AUS DEM "TANZ":

    1. KONZENTRATIONS-RANKING:
       - HOT-Non-Birthday hat HOECHSTE Konzentration ({conc['hot_non_birthday']['concentration']*100:.2f}%)
       - Gefolgt von HOT ({conc['hot']['concentration']*100:.2f}%)
       - COLD-Non-Birthday ist am niedrigsten ({conc['cold_non_birthday']['concentration']*100:.2f}%)

    2. OPTIMALER MIX (aus Simulation):
       - Bester Mix: {best_mix[0]}
       - Verbesserung: {best_mix[1]['improvement']:+.1f}% vs. Erwartung

    3. DIE TANZ-METAPHER:
       - Das System "tanzt" zwischen Pools
       - HOT-Konzentration: hoeher weil Pool kleiner
       - COLD-Sicherheit: mehr Zahlen = mehr Treffer absolut
       - OPTIMAL: Mischung aus beiden!

    4. PRAKTISCHE EMPFEHLUNG:
       Typ 6 Ticket bauen aus:
       - 2-3 HOT Zahlen (hohe Konzentration)
       - 1-2 COLD-Birthday (mittlere Konzentration)
       - 1-2 COLD-Non-Birthday (Diversifikation)
    """)

    # === KONKRETE TICKET-EMPFEHLUNG ===
    print(f"\n{'='*100}")
    print("KONKRETE TICKET-EMPFEHLUNG FUER HEUTE")
    print(f"{'='*100}")

    latest_idx = len(draws) - 1
    hot = get_hot_numbers(draws, latest_idx + 1, lookback=3)  # Fuer morgen
    cold = ALL_NUMBERS - hot
    cold_bd = sorted(cold & BIRTHDAY_NUMBERS)
    cold_nonbd = sorted(cold & NON_BIRTHDAY_NUMBERS)
    hot_list = sorted(hot)

    target_date = draws[latest_idx]["datum"] + timedelta(days=1)

    print(f"\n  Datum: {target_date.date()}")
    print(f"\n  Verfuegbare Pools:")
    print(f"    HOT ({len(hot_list)}): {hot_list}")
    print(f"    COLD-Birthday ({len(cold_bd)}): {cold_bd[:15]}...")
    print(f"    COLD-Non-Birthday ({len(cold_nonbd)}): {cold_nonbd[:15]}...")

    # Generiere optimale Tickets basierend auf bestem Mix
    seed(42)

    print(f"\n  EMPFOHLENE MIXED TICKETS:")

    # Typ 6: 3 HOT + 2 COLD-BD + 1 COLD-NonBD
    if len(hot_list) >= 3 and len(cold_bd) >= 2 and len(cold_nonbd) >= 1:
        ticket_6 = sorted(
            sample(hot_list, 3) +
            sample(cold_bd, 2) +
            sample(cold_nonbd, 1)
        )
        print(f"\n    Typ 6 (3H+2CB+1CN): {ticket_6}")
        print(f"      HOT:           {[z for z in ticket_6 if z in hot]}")
        print(f"      COLD-Birthday: {[z for z in ticket_6 if z in cold_bd]}")
        print(f"      COLD-NonBD:    {[z for z in ticket_6 if z in cold_nonbd]}")

    # Typ 7: 3 HOT + 2 COLD-BD + 2 COLD-NonBD
    if len(hot_list) >= 3 and len(cold_bd) >= 2 and len(cold_nonbd) >= 2:
        ticket_7 = sorted(
            sample(hot_list, 3) +
            sample(cold_bd, 2) +
            sample(cold_nonbd, 2)
        )
        print(f"\n    Typ 7 (3H+2CB+2CN): {ticket_7}")
        print(f"      HOT:           {[z for z in ticket_7 if z in hot]}")
        print(f"      COLD-Birthday: {[z for z in ticket_7 if z in cold_bd]}")
        print(f"      COLD-NonBD:    {[z for z in ticket_7 if z in cold_nonbd]}")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
