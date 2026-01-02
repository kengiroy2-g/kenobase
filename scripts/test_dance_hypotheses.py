#!/usr/bin/env python3
"""
TEST: Zwei kritische Tanz-Hypothesen

HYPOTHESE 1 (Kleine Gewinne):
- Der "Tanz" funktioniert nur fuer kleine Gewinne (<10.000 EUR)
- Pool auf <=17 Zahlen reduzieren (Haelfte von jedem Pool-Typ eliminieren)
- Erwartung: 1x 6/6 oder 5/5 innerhalb von 56 Tagen mit Random-Ticket

HYPOTHESE 2 (Grosse Gewinne):
- Grosse Gewinne (8/8, 9/9, 10/10) bestehen hauptsaechlich aus Zahlen
  AUSSERHALB des Tanz-Bereichs (nicht HOT, nicht typische Pools)
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
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


def get_cold_numbers(draws: List[Dict], target_idx: int, lookback: int = 3) -> Set[int]:
    """COLD Zahlen."""
    hot = get_hot_numbers(draws, target_idx, lookback)
    return ALL_NUMBERS - hot


def build_reduced_pool(draws: List[Dict], target_idx: int, target_size: int = 17) -> Set[int]:
    """
    Baut reduzierten Pool durch Eliminierung der Haelfte jedes Pool-Typs.

    Strategie:
    1. HOT: Behalte obere Haelfte (nach Index sortiert)
    2. COLD-Birthday: Behalte untere Haelfte
    3. COLD-Non-Birthday: Behalte untere Haelfte
    4. Kombiniere bis target_size erreicht
    """
    hot = get_hot_numbers(draws, target_idx, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_bd = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # Berechne Index fuer Sortierung
    def get_index(z):
        if target_idx < 20:
            return 0
        lookback_20 = draws[target_idx-20:target_idx]
        return sum(1 if z in d["zahlen"] else -1 for d in lookback_20)

    # HOT: Behalte Haelfte mit niedrigstem Index (unter-repraesentiert)
    hot_sorted = sorted(hot, key=get_index)
    hot_keep = set(hot_sorted[:len(hot_sorted)//2 + 1])

    # COLD-Birthday: Behalte Haelfte mit niedrigstem Index
    cold_bd_sorted = sorted(cold_bd, key=get_index)
    cold_bd_keep = set(cold_bd_sorted[:len(cold_bd_sorted)//2 + 1])

    # COLD-Non-Birthday: Behalte Haelfte mit niedrigstem Index
    cold_nonbd_sorted = sorted(cold_nonbd, key=get_index)
    cold_nonbd_keep = set(cold_nonbd_sorted[:len(cold_nonbd_sorted)//2 + 1])

    # Kombiniere
    pool = hot_keep | cold_bd_keep | cold_nonbd_keep

    # Reduziere auf target_size falls noetig
    if len(pool) > target_size:
        pool_sorted = sorted(pool, key=get_index)
        pool = set(pool_sorted[:target_size])

    return pool


def test_hypothesis_1(draws: List[Dict], start_idx: int = 100) -> Dict:
    """
    HYPOTHESE 1: Reduzierter Pool (<=17) erzielt 6/6 oder 5/5 in 56 Tagen.

    Test:
    - Fuer jeden 56-Tage-Block
    - Generiere reduzierten Pool am Start des Blocks
    - Teste ob irgendein 6er oder 5er aus dem Pool einen Jackpot erzielt
    """
    results = {
        "blocks_tested": 0,
        "blocks_with_6_6": 0,
        "blocks_with_5_5": 0,
        "blocks_with_any_jackpot": 0,
        "avg_pool_size": 0,
        "avg_best_hits_typ6": 0,
        "avg_best_hits_typ5": 0,
        "jackpot_details": [],
        "days_to_first_jackpot": [],
    }

    block_size = 56
    total_pool_sizes = []
    best_hits_typ6 = []
    best_hits_typ5 = []

    idx = start_idx
    while idx + block_size < len(draws):
        # Generiere Pool am Start des Blocks
        pool = build_reduced_pool(draws, idx, target_size=17)
        pool_list = sorted(pool)
        total_pool_sizes.append(len(pool))

        if len(pool) < 6:
            idx += block_size
            continue

        results["blocks_tested"] += 1

        # Teste alle Tage im Block
        block_best_6 = 0
        block_best_5 = 0
        jackpot_6_found = False
        jackpot_5_found = False
        days_to_jp = None

        for day_offset in range(block_size):
            if idx + day_offset >= len(draws):
                break

            drawn = draws[idx + day_offset]["zahlen"]
            pool_hits = len(pool & drawn)

            # Beste Treffer fuer Typ 6 (wenn 6+ aus Pool gezogen)
            if pool_hits >= 6:
                block_best_6 = max(block_best_6, 6)
                if not jackpot_6_found:
                    jackpot_6_found = True
                    if days_to_jp is None:
                        days_to_jp = day_offset + 1
                    results["jackpot_details"].append({
                        "block_start": draws[idx]["datum_str"],
                        "jackpot_day": draws[idx + day_offset]["datum_str"],
                        "days": day_offset + 1,
                        "type": "6/6",
                        "pool_hits": pool_hits,
                    })
            else:
                block_best_6 = max(block_best_6, pool_hits)

            # Beste Treffer fuer Typ 5 (wenn 5+ aus Pool gezogen)
            if pool_hits >= 5:
                block_best_5 = max(block_best_5, 5)
                if not jackpot_5_found:
                    jackpot_5_found = True
                    if days_to_jp is None:
                        days_to_jp = day_offset + 1

        best_hits_typ6.append(block_best_6)
        best_hits_typ5.append(block_best_5)

        if jackpot_6_found:
            results["blocks_with_6_6"] += 1
        if jackpot_5_found:
            results["blocks_with_5_5"] += 1
        if jackpot_6_found or jackpot_5_found:
            results["blocks_with_any_jackpot"] += 1
            results["days_to_first_jackpot"].append(days_to_jp)

        idx += block_size

    # Durchschnitte berechnen
    if total_pool_sizes:
        results["avg_pool_size"] = sum(total_pool_sizes) / len(total_pool_sizes)
    if best_hits_typ6:
        results["avg_best_hits_typ6"] = sum(best_hits_typ6) / len(best_hits_typ6)
    if best_hits_typ5:
        results["avg_best_hits_typ5"] = sum(best_hits_typ5) / len(best_hits_typ5)
    if results["days_to_first_jackpot"]:
        results["avg_days_to_jackpot"] = sum(results["days_to_first_jackpot"]) / len(results["days_to_first_jackpot"])

    return results


def test_hypothesis_2(draws: List[Dict], start_idx: int = 100) -> Dict:
    """
    HYPOTHESE 2: Grosse Gewinne (8/8, 9/9, 10/10) bestehen aus Zahlen
    AUSSERHALB des Tanz-Bereichs.

    Test:
    - Finde Tage mit hohen Pool-Hits (>=8 aus Pool)
    - Analysiere: Sind die gezogenen Zahlen im "Tanz" oder ausserhalb?
    - "Ausserhalb" = Weder HOT noch in typischen Pools
    """
    results = {
        "high_hit_days": [],
        "avg_hot_in_high_hits": 0,
        "avg_cold_in_high_hits": 0,
        "avg_outside_dance_in_high_hits": 0,
        "outside_dance_numbers": defaultdict(int),
    }

    for idx in range(start_idx, len(draws)):
        drawn = draws[idx]["zahlen"]
        hot = get_hot_numbers(draws, idx, lookback=3)
        cold = ALL_NUMBERS - hot

        # Definiere "Tanz-Bereich"
        # Tanz = HOT + COLD-Birthday + COLD-Non-Birthday (mit Konzentration > Baseline)
        dance_pool = hot | (cold & NON_BIRTHDAY_NUMBERS)  # HOT + COLD-NonBD haben beste Konzentration

        # Ausserhalb des Tanz = Zahlen die weder HOT noch COLD-NonBD sind
        outside_dance = ALL_NUMBERS - dance_pool  # Das sind COLD-Birthday

        # Alternative Definition: "Ausserhalb" = nicht in den Top-Pools
        # Top-Pools: HOT-Birthday (28.95%), COLD-NonBD (28.72%), HOT (28.64%)
        top_pools = (hot & BIRTHDAY_NUMBERS) | (cold & NON_BIRTHDAY_NUMBERS) | hot
        outside_top = ALL_NUMBERS - top_pools

        # Zaehle Treffer
        hot_hits = len(drawn & hot)
        cold_hits = len(drawn & cold)

        # Hohe Treffer-Tage (8+ von 20 sind nicht in typischen Pools)
        outside_hits = len(drawn & outside_top)

        # Speichere wenn viele Zahlen ausserhalb des Tanz
        if outside_hits >= 8:  # Mehr als 40% ausserhalb
            results["high_hit_days"].append({
                "datum": draws[idx]["datum_str"],
                "drawn": sorted(drawn),
                "hot_hits": hot_hits,
                "cold_hits": cold_hits,
                "outside_hits": outside_hits,
                "outside_numbers": sorted(drawn & outside_top),
            })

            for z in drawn & outside_top:
                results["outside_dance_numbers"][z] += 1

    # Berechne Durchschnitte
    if results["high_hit_days"]:
        results["avg_hot_in_high_hits"] = sum(d["hot_hits"] for d in results["high_hit_days"]) / len(results["high_hit_days"])
        results["avg_outside_in_high_hits"] = sum(d["outside_hits"] for d in results["high_hit_days"]) / len(results["high_hit_days"])

    return results


def analyze_jackpot_composition(draws: List[Dict], start_idx: int = 100) -> Dict:
    """
    Analysiert die Zusammensetzung von Ziehungen wo theoretisch
    grosse Gewinne moeglich waren.
    """
    results = {
        "jackpot_potential_days": [],  # Tage wo 10+ aus kleinem Pool
        "composition_stats": {
            "hot_ratio": [],
            "cold_bd_ratio": [],
            "cold_nonbd_ratio": [],
            "outside_ratio": [],
        }
    }

    for idx in range(start_idx, len(draws)):
        drawn = draws[idx]["zahlen"]
        hot = get_hot_numbers(draws, idx, lookback=3)
        cold = ALL_NUMBERS - hot
        cold_bd = cold & BIRTHDAY_NUMBERS
        cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

        # Berechne Anteile
        hot_in_draw = len(drawn & hot)
        cold_bd_in_draw = len(drawn & cold_bd)
        cold_nonbd_in_draw = len(drawn & cold_nonbd)

        # "Ausserhalb" = COLD-Birthday (schlechteste Konzentration)
        outside = cold_bd
        outside_in_draw = cold_bd_in_draw

        results["composition_stats"]["hot_ratio"].append(hot_in_draw / 20)
        results["composition_stats"]["cold_bd_ratio"].append(cold_bd_in_draw / 20)
        results["composition_stats"]["cold_nonbd_ratio"].append(cold_nonbd_in_draw / 20)
        results["composition_stats"]["outside_ratio"].append(outside_in_draw / 20)

        # Tage mit extremer Zusammensetzung
        if cold_bd_in_draw >= 10:  # >=50% sind COLD-Birthday (schlechteste Pool)
            results["jackpot_potential_days"].append({
                "datum": draws[idx]["datum_str"],
                "hot": hot_in_draw,
                "cold_bd": cold_bd_in_draw,
                "cold_nonbd": cold_nonbd_in_draw,
                "composition": f"{hot_in_draw}H + {cold_bd_in_draw}CB + {cold_nonbd_in_draw}CN",
            })

    # Durchschnitte
    keys_to_process = list(results["composition_stats"].keys())
    for key in keys_to_process:
        vals = results["composition_stats"][key]
        if vals:
            results["composition_stats"][f"{key}_avg"] = sum(vals) / len(vals)

    return results


def main():
    print("=" * 100)
    print("TEST: Tanz-Hypothesen - Kleine vs. Grosse Gewinne")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    start_idx = 100

    # =================================================================
    # HYPOTHESE 1: Reduzierter Pool fuer kleine Gewinne
    # =================================================================
    print(f"\n{'='*100}")
    print("HYPOTHESE 1: Reduzierter Pool (<=17) -> 6/6 oder 5/5 in 56 Tagen")
    print(f"{'='*100}")

    h1_results = test_hypothesis_1(draws, start_idx)

    print(f"\n  ERGEBNISSE:")
    print(f"    56-Tage-Bloecke getestet: {h1_results['blocks_tested']}")
    print(f"    Durchschnittliche Pool-Groesse: {h1_results['avg_pool_size']:.1f}")
    print(f"\n    Bloecke mit 6/6 (alle 6 aus Pool gezogen): {h1_results['blocks_with_6_6']}")
    print(f"    Bloecke mit 5/5 (mind. 5 aus Pool gezogen): {h1_results['blocks_with_5_5']}")
    print(f"    Bloecke mit IRGENDEINEM Jackpot: {h1_results['blocks_with_any_jackpot']}")

    if h1_results['blocks_tested'] > 0:
        success_rate_6 = h1_results['blocks_with_6_6'] / h1_results['blocks_tested'] * 100
        success_rate_5 = h1_results['blocks_with_5_5'] / h1_results['blocks_tested'] * 100
        success_rate_any = h1_results['blocks_with_any_jackpot'] / h1_results['blocks_tested'] * 100

        print(f"\n    Erfolgsrate 6/6: {success_rate_6:.1f}%")
        print(f"    Erfolgsrate 5/5: {success_rate_5:.1f}%")
        print(f"    Erfolgsrate ANY: {success_rate_any:.1f}%")

    if h1_results.get('avg_days_to_jackpot'):
        print(f"\n    Durchschnittliche Tage bis zum ersten Jackpot: {h1_results['avg_days_to_jackpot']:.1f}")

    print(f"\n    Durchschnittlich beste Treffer Typ6: {h1_results['avg_best_hits_typ6']:.2f} von 6")
    print(f"    Durchschnittlich beste Treffer Typ5: {h1_results['avg_best_hits_typ5']:.2f} von 5")

    if h1_results['jackpot_details'][:5]:
        print(f"\n    Beispiele fuer Jackpots:")
        for jp in h1_results['jackpot_details'][:5]:
            print(f"      {jp['block_start']} -> {jp['jackpot_day']}: {jp['type']} nach {jp['days']} Tagen")

    # Mathematische Erwartung
    print(f"\n  MATHEMATISCHE ERWARTUNG:")
    # Bei Pool von 17, Typ 6: Wie oft sind 6 aus 17 in den 20 gezogenen?
    # P = C(17,6) * C(53,14) / C(70,20) pro Tag
    # Fuer 56 Tage: 1 - (1-P)^56

    from math import comb as c
    pool_size = 17
    for ticket_size in [5, 6]:
        p_single = c(pool_size, ticket_size) * c(70-pool_size, 20-ticket_size) / c(70, 20)
        p_56_days = 1 - (1 - p_single) ** 56
        print(f"    Typ {ticket_size}: P(Jackpot in 56 Tagen bei Pool {pool_size}) = {p_56_days*100:.2f}%")

    # =================================================================
    # HYPOTHESE 2: Grosse Gewinne ausserhalb des Tanz
    # =================================================================
    print(f"\n{'='*100}")
    print("HYPOTHESE 2: Grosse Gewinne bestehen aus Zahlen AUSSERHALB des Tanz")
    print(f"{'='*100}")

    h2_results = test_hypothesis_2(draws, start_idx)

    print(f"\n  Definition 'Ausserhalb des Tanz':")
    print(f"    Tanz-Pools (beste Konzentration): HOT-Birthday, COLD-NonBD, HOT")
    print(f"    Ausserhalb: COLD-Birthday (schlechteste Konzentration: 28.35%)")

    print(f"\n  ERGEBNISSE:")
    print(f"    Tage mit >=8 Zahlen ausserhalb des Tanz: {len(h2_results['high_hit_days'])}")

    if h2_results['high_hit_days']:
        print(f"\n    Durchschnittlich HOT in diesen Tagen: {h2_results['avg_hot_in_high_hits']:.1f}")
        print(f"    Durchschnittlich AUSSERHALB in diesen Tagen: {h2_results['avg_outside_in_high_hits']:.1f}")

        print(f"\n    Beispiele (Tage mit vielen 'Ausserhalb'-Zahlen):")
        for day in h2_results['high_hit_days'][:5]:
            print(f"      {day['datum']}: {day['outside_hits']} ausserhalb, HOT={day['hot_hits']}")
            print(f"        Ausserhalb-Zahlen: {day['outside_numbers']}")

    # Haeufigste "Ausserhalb"-Zahlen
    if h2_results['outside_dance_numbers']:
        sorted_outside = sorted(h2_results['outside_dance_numbers'].items(), key=lambda x: x[1], reverse=True)
        print(f"\n    Haeufigste 'Ausserhalb'-Zahlen:")
        for z, count in sorted_outside[:10]:
            print(f"      {z}: {count}x")

    # =================================================================
    # DETAILLIERTE ZUSAMMENSETZUNGS-ANALYSE
    # =================================================================
    print(f"\n{'='*100}")
    print("DETAILLIERTE ZUSAMMENSETZUNGS-ANALYSE")
    print(f"{'='*100}")

    comp_results = analyze_jackpot_composition(draws, start_idx)

    print(f"\n  DURCHSCHNITTLICHE ZUSAMMENSETZUNG ALLER ZIEHUNGEN:")
    print(f"    HOT:            {comp_results['composition_stats']['hot_ratio_avg']*100:.1f}% ({comp_results['composition_stats']['hot_ratio_avg']*20:.1f} von 20)")
    print(f"    COLD-Birthday:  {comp_results['composition_stats']['cold_bd_ratio_avg']*100:.1f}% ({comp_results['composition_stats']['cold_bd_ratio_avg']*20:.1f} von 20)")
    print(f"    COLD-Non-BD:    {comp_results['composition_stats']['cold_nonbd_ratio_avg']*100:.1f}% ({comp_results['composition_stats']['cold_nonbd_ratio_avg']*20:.1f} von 20)")

    print(f"\n  TAGE MIT >=10 COLD-BIRTHDAY (>=50% 'ausserhalb' bester Pools):")
    print(f"    Anzahl: {len(comp_results['jackpot_potential_days'])}")

    if comp_results['jackpot_potential_days']:
        print(f"\n    Beispiele:")
        for day in comp_results['jackpot_potential_days'][:10]:
            print(f"      {day['datum']}: {day['composition']}")

    # =================================================================
    # HYPOTHESEN-BEWERTUNG
    # =================================================================
    print(f"\n{'='*100}")
    print("HYPOTHESEN-BEWERTUNG")
    print(f"{'='*100}")

    print(f"""
    HYPOTHESE 1: "Pool <=17 -> 6/6 in 56 Tagen"

    Ergebnis:
    - Getestete Bloecke: {h1_results['blocks_tested']}
    - Erfolgsrate 6/6:   {success_rate_6:.1f}%
    - Erfolgsrate 5/5:   {success_rate_5:.1f}%

    Bewertung:
    """)

    if success_rate_6 >= 80:
        print("    -> BESTAETIGT: Hohe Erfolgsrate fuer 6/6!")
    elif success_rate_5 >= 80:
        print("    -> TEILWEISE BESTAETIGT: Hohe Erfolgsrate fuer 5/5, aber nicht 6/6")
    else:
        print("    -> NICHT BESTAETIGT: Erfolgsrate unter Erwartung")

    print(f"""
    HYPOTHESE 2: "Grosse Gewinne = ausserhalb des Tanz"

    Ergebnis:
    - Tage mit >=8 'Ausserhalb'-Zahlen: {len(h2_results['high_hit_days'])}
    - Durchschn. 'Ausserhalb' an diesen Tagen: {h2_results.get('avg_outside_in_high_hits', 0):.1f}

    Bewertung:
    """)

    outside_percentage = len(h2_results['high_hit_days']) / (len(draws) - start_idx) * 100 if len(draws) > start_idx else 0

    if outside_percentage > 5:
        print(f"    -> MOEGLICH: {outside_percentage:.1f}% der Tage haben viele 'Ausserhalb'-Zahlen")
        print("    -> Grosse Gewinne koennten tatsaechlich 'ausserhalb' des Tanz entstehen")
    else:
        print(f"    -> NICHT BESTAETIGT: Nur {outside_percentage:.1f}% der Tage")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
