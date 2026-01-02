#!/usr/bin/env python3
"""
POOL-MIX ANALYSE

Hypothese: Gewinner-Tickets haben Zahlen aus UNTERSCHIEDLICHEN Pool-Typen.
Die Verteilung variiert je nach System-Zustand.

Untersucht:
1. Wie setzen sich die 20 gezogenen Zahlen zusammen?
2. Gibt es ein optimales Verhaeltnis (HOT/COLD, Birthday/Non-Birthday)?
3. Aendert sich das Verhaeltnis ueber Zeit / nach Events?
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

# Dekaden
DECADES = {
    "D1": set(range(1, 11)),
    "D2": set(range(11, 21)),
    "D3": set(range(21, 31)),
    "D4": set(range(31, 41)),
    "D5": set(range(41, 51)),
    "D6": set(range(51, 61)),
    "D7": set(range(61, 71)),
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


def analyze_draw_composition(draws: List[Dict], idx: int) -> Dict:
    """Analysiert die Zusammensetzung einer Ziehung."""
    drawn = draws[idx]["zahlen"]
    hot = get_hot_numbers(draws, idx, lookback=3)
    cold = ALL_NUMBERS - hot

    # Pool-Zugehoerigkeiten
    composition = {
        "total": 20,
        "birthday": len(drawn & BIRTHDAY_NUMBERS),
        "non_birthday": len(drawn & NON_BIRTHDAY_NUMBERS),
        "hot": len(drawn & hot),
        "cold": len(drawn & cold),
        "hot_birthday": len(drawn & hot & BIRTHDAY_NUMBERS),
        "hot_non_birthday": len(drawn & hot & NON_BIRTHDAY_NUMBERS),
        "cold_birthday": len(drawn & cold & BIRTHDAY_NUMBERS),
        "cold_non_birthday": len(drawn & cold & NON_BIRTHDAY_NUMBERS),
        "correction_candidates": len(drawn & TOP_20_CORRECTION),
    }

    # Dekaden-Verteilung
    for decade_name, decade_set in DECADES.items():
        composition[decade_name] = len(drawn & decade_set)

    # Verhaeltnisse
    composition["birthday_ratio"] = composition["birthday"] / 20
    composition["hot_ratio"] = composition["hot"] / 20
    composition["hot_of_hot"] = composition["hot"] / len(hot) if hot else 0

    return composition


def main():
    print("=" * 100)
    print("POOL-MIX ANALYSE: Zusammensetzung erfolgreicher Ziehungen")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Analysiere alle Ziehungen ab Index 100
    start_idx = 100
    all_compositions = []

    for idx in range(start_idx, len(draws)):
        comp = analyze_draw_composition(draws, idx)
        comp["datum"] = draws[idx]["datum"]
        comp["idx"] = idx
        all_compositions.append(comp)

    # === DURCHSCHNITTLICHE ZUSAMMENSETZUNG ===
    print(f"\n{'='*100}")
    print("DURCHSCHNITTLICHE ZUSAMMENSETZUNG (20 gezogene Zahlen)")
    print(f"{'='*100}")

    # Berechne Durchschnitte
    avg_comp = {}
    for key in ["birthday", "non_birthday", "hot", "cold", "hot_birthday",
                "hot_non_birthday", "cold_birthday", "cold_non_birthday",
                "correction_candidates", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]:
        values = [c[key] for c in all_compositions]
        avg_comp[key] = sum(values) / len(values)
        std = (sum((v - avg_comp[key])**2 for v in values) / len(values)) ** 0.5
        avg_comp[f"{key}_std"] = std

    print(f"\n  POOL-TYP VERTEILUNG:")
    print(f"  {'Kategorie':<25} {'Durchschn.':<12} {'Std.Abw.':<10} {'Erwartung'}")
    print("  " + "-" * 70)

    # Erwartungswerte
    expected = {
        "birthday": 31 * 20 / 70,  # ~8.86
        "non_birthday": 39 * 20 / 70,  # ~11.14
        "hot": 11 * 20 / 70,  # ~3.14 (bei ~11 HOT Zahlen)
        "cold": 59 * 20 / 70,  # ~16.86
    }

    for cat in ["birthday", "non_birthday", "hot", "cold"]:
        exp = expected.get(cat, "?")
        exp_str = f"{exp:.2f}" if isinstance(exp, float) else exp
        print(f"  {cat:<25} {avg_comp[cat]:<12.2f} {avg_comp[f'{cat}_std']:<10.2f} {exp_str}")

    print(f"\n  KOMBINIERTE KATEGORIEN:")
    print("  " + "-" * 70)
    for cat in ["hot_birthday", "hot_non_birthday", "cold_birthday", "cold_non_birthday"]:
        print(f"  {cat:<25} {avg_comp[cat]:<12.2f} {avg_comp[f'{cat}_std']:<10.2f}")

    print(f"\n  DEKADEN-VERTEILUNG:")
    print("  " + "-" * 70)
    expected_per_decade = 10 * 20 / 70  # ~2.86
    for d in ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]:
        print(f"  {d} (Zahlen {(int(d[1])-1)*10+1}-{int(d[1])*10})      "
              f"{avg_comp[d]:<12.2f} {avg_comp[f'{d}_std']:<10.2f} {expected_per_decade:.2f}")

    # === VERTEILUNG DER VERHAELTNISSE ===
    print(f"\n{'='*100}")
    print("VERTEILUNG DER VERHAELTNISSE")
    print(f"{'='*100}")

    # Birthday-Ratio Verteilung
    birthday_ratios = [c["birthday"] for c in all_compositions]
    print(f"\n  BIRTHDAY-ZAHLEN pro Ziehung (von 20):")
    for n in range(0, 21):
        count = birthday_ratios.count(n)
        pct = count / len(birthday_ratios) * 100
        bar = "#" * int(pct / 2)
        if count > 0:
            print(f"  {n:>3}: {count:>5} ({pct:>5.1f}%) {bar}")

    # HOT-Zahlen Verteilung
    hot_counts = [c["hot"] for c in all_compositions]
    print(f"\n  HOT-ZAHLEN pro Ziehung (von 20):")
    for n in range(0, 15):
        count = hot_counts.count(n)
        pct = count / len(hot_counts) * 100
        bar = "#" * int(pct / 2)
        if count > 0:
            print(f"  {n:>3}: {count:>5} ({pct:>5.1f}%) {bar}")

    # === OPTIMALE MIX-ANALYSE ===
    print(f"\n{'='*100}")
    print("OPTIMALE MIX-ANALYSE: Welche Zusammensetzung ist am erfolgreichsten?")
    print(f"{'='*100}")

    # Gruppiere nach HOT-Anzahl und analysiere "Qualitaet"
    # Qualitaet = Wie viele der gezogenen Zahlen waren in einem kleinen Pool?

    print(f"\n  Analyse: Bei wie vielen HOT-Zahlen ist die 'Trefferkonzentration' am hoechsten?")
    print(f"\n  {'HOT in Ziehung':<16} {'Anzahl Tage':<14} {'HOT Pool Groesse':<18} {'Trefferquote im HOT Pool'}")
    print("  " + "-" * 80)

    for hot_drawn in range(0, 12):
        matching = [c for c in all_compositions if c["hot"] == hot_drawn]
        if matching:
            # Durchschnittliche HOT Pool Groesse an diesen Tagen
            # (HOT Pool ist immer ~11, aber variiert etwas)
            avg_hot_pool = sum(len(get_hot_numbers(draws, c["idx"], 3)) for c in matching) / len(matching)
            # Trefferquote = hot_drawn / hot_pool_size
            if avg_hot_pool > 0:
                hit_rate = hot_drawn / avg_hot_pool * 100
            else:
                hit_rate = 0
            print(f"  {hot_drawn:<16} {len(matching):<14} {avg_hot_pool:<18.1f} {hit_rate:.1f}%")

    # === MIX-STRATEGIE ABLEITEN ===
    print(f"\n{'='*100}")
    print("MIX-STRATEGIE: Optimales Verhaeltnis fuer Tickets")
    print(f"{'='*100}")

    # Analysiere: Bei welchem Mix sind die meisten "6er" oder "7er" moeglich?
    print(f"\n  Frage: Welcher Mix maximiert die Chance auf 6+ Treffer?")

    # Simuliere verschiedene Ticket-Zusammensetzungen
    ticket_strategies = [
        ("6 HOT", {"hot": 6, "cold": 0}),
        ("5 HOT + 1 COLD", {"hot": 5, "cold": 1}),
        ("4 HOT + 2 COLD", {"hot": 4, "cold": 2}),
        ("3 HOT + 3 COLD", {"hot": 3, "cold": 3}),
        ("2 HOT + 4 COLD", {"hot": 2, "cold": 4}),
        ("1 HOT + 5 COLD", {"hot": 1, "cold": 5}),
        ("6 COLD", {"hot": 0, "cold": 6}),
    ]

    print(f"\n  {'Strategie':<20} {'6/6 Jackpot Tage':<20} {'5/6 Near-Miss Tage':<20}")
    print("  " + "-" * 60)

    for strat_name, strat_mix in ticket_strategies:
        jackpot_days = 0
        near_miss_days = 0

        for comp in all_compositions:
            # Maximale Treffer mit dieser Strategie
            hot_available = comp["hot"]
            cold_available = comp["cold"]

            hot_hits = min(strat_mix["hot"], hot_available)
            cold_hits = min(strat_mix["cold"], cold_available)
            total_hits = hot_hits + cold_hits

            if total_hits >= 6:
                jackpot_days += 1
            if total_hits >= 5:
                near_miss_days += 1

        print(f"  {strat_name:<20} {jackpot_days:<20} {near_miss_days:<20}")

    # === ZEITLICHE VARIATION ===
    print(f"\n{'='*100}")
    print("ZEITLICHE VARIATION: Aendert sich der optimale Mix?")
    print(f"{'='*100}")

    # Teile in Quartale
    quarters = defaultdict(list)
    for comp in all_compositions:
        q = f"{comp['datum'].year}-Q{(comp['datum'].month-1)//3 + 1}"
        quarters[q].append(comp)

    print(f"\n  {'Quartal':<12} {'Avg Birthday':<15} {'Avg HOT':<12} {'Avg COLD':<12}")
    print("  " + "-" * 55)

    for q in sorted(quarters.keys()):
        comps = quarters[q]
        avg_bd = sum(c["birthday"] for c in comps) / len(comps)
        avg_hot = sum(c["hot"] for c in comps) / len(comps)
        avg_cold = sum(c["cold"] for c in comps) / len(comps)
        print(f"  {q:<12} {avg_bd:<15.2f} {avg_hot:<12.2f} {avg_cold:<12.2f}")

    # === FAZIT ===
    print(f"\n{'='*100}")
    print("FAZIT: Pool-Mix Empfehlung")
    print(f"{'='*100}")

    # Berechne optimalen Mix basierend auf Daten
    avg_hot_in_draw = avg_comp["hot"]
    avg_cold_in_draw = avg_comp["cold"]

    hot_ratio_optimal = avg_hot_in_draw / 20
    cold_ratio_optimal = avg_cold_in_draw / 20

    print(f"""
    ERKENNTNISSE:

    1. DURCHSCHNITTLICHE ZUSAMMENSETZUNG (20 Zahlen):
       - Birthday:     {avg_comp['birthday']:.1f} Zahlen ({avg_comp['birthday']/20*100:.0f}%)
       - Non-Birthday: {avg_comp['non_birthday']:.1f} Zahlen ({avg_comp['non_birthday']/20*100:.0f}%)
       - HOT:          {avg_comp['hot']:.1f} Zahlen ({avg_comp['hot']/20*100:.0f}%)
       - COLD:         {avg_comp['cold']:.1f} Zahlen ({avg_comp['cold']/20*100:.0f}%)

    2. OPTIMALER MIX FUER TYP 6:
       - HOT Zahlen:  {int(round(6 * hot_ratio_optimal))} (proportional: {6 * hot_ratio_optimal:.1f})
       - COLD Zahlen: {int(round(6 * cold_ratio_optimal))} (proportional: {6 * cold_ratio_optimal:.1f})

    3. ZEITLICHE STABILITAET:
       - Der Mix ist relativ STABIL ueber Quartale
       - Kleine Schwankungen, aber kein klarer Trend

    4. EMPFEHLUNG:
       - Typ 6: 1-2 HOT + 4-5 COLD (spiegelt natuerliche Verteilung)
       - Typ 7: 1-2 HOT + 5-6 COLD
       - Birthday/Non-Birthday: ca. 45%/55% (entspricht 31:39 Verhaeltnis)
    """)


if __name__ == "__main__":
    main()
