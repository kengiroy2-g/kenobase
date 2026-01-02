#!/usr/bin/env python3
"""
Analyse: Koennen wir unter/ueber-repraesentierte Zahlen VORHERSAGEN?

Methode:
1. Pool definieren (Birthday + Momentum am 01.02.2025)
2. Metriken 2 Wochen VOR Stichtag analysieren (18.01. - 31.01.2025)
3. Metriken waehrend Testphase verfolgen (01.02. - 31.07.2025)
4. Korrelation pruefen: Waren unter-repraesentierte Zahlen schon vorher "anders"?

Bekannte Ergebnisse:
- Unter-repraesentiert bei Jackpots: 21, 29, 45, 67
- Ueber-repraesentiert bei Jackpots: 26, 2, 27
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

# Bekannte Ergebnisse aus vorheriger Analyse
UNDER_REPRESENTED = {21, 29, 45, 67}
OVER_REPRESENTED = {26, 2, 27}
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
    """Holt Momentum-Zahlen (2+ mal in letzten X Tagen)."""
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
    """Berechnet alle Metriken fuer eine Zahl an einem Tag."""
    # Index und Count (letzte 20 Tage)
    lookback_20 = draws[max(0, target_idx-20):target_idx]
    count_20 = sum(1 for d in lookback_20 if zahl in d["zahlen"])

    index = 0
    for d in lookback_20:
        if zahl in d["zahlen"]:
            index += 1
        else:
            index -= 1

    # MCount (letzte 3 Tage)
    lookback_3 = draws[max(0, target_idx-3):target_idx]
    mcount = sum(1 for d in lookback_3 if zahl in d["zahlen"])

    # Gap
    gap = 0
    for i in range(target_idx - 1, -1, -1):
        if zahl in draws[i]["zahlen"]:
            break
        gap += 1

    return {
        "index": index,
        "count_20": count_20,
        "mcount_3": mcount,
        "gap": gap,
    }


def main():
    print("=" * 100)
    print("VORHERSAGE-ANALYSE: Koennen unter/ueber-repraesentierte Zahlen erkannt werden?")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Definiere Zeitraeume
    stichtag = datetime(2025, 2, 1)
    pre_start = datetime(2025, 1, 18)  # 2 Wochen vorher
    test_end = datetime(2025, 7, 31)

    # Finde Indizes
    pre_start_idx = None
    stichtag_idx = None
    test_end_idx = None

    for i, d in enumerate(draws):
        if d["datum"] >= pre_start and pre_start_idx is None:
            pre_start_idx = i
        if d["datum"] >= stichtag and stichtag_idx is None:
            stichtag_idx = i
        if d["datum"] <= test_end:
            test_end_idx = i

    print(f"\nZeitraeume:")
    print(f"  Pre-Phase:  {draws[pre_start_idx]['datum_str']} bis {draws[stichtag_idx-1]['datum_str']} (Index {pre_start_idx}-{stichtag_idx-1})")
    print(f"  Test-Phase: {draws[stichtag_idx]['datum_str']} bis {draws[test_end_idx]['datum_str']} (Index {stichtag_idx}-{test_end_idx})")

    # Pool am Stichtag ermitteln
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum
    pool_list = sorted(pool)

    print(f"\nPOOL am {stichtag.date()} ({len(pool)} Zahlen):")
    print(f"  Birthday:  {sorted(BIRTHDAY_POPULAR)}")
    print(f"  Momentum:  {sorted(momentum)}")
    print(f"  Gesamt:    {pool_list}")

    print(f"\nBekannte Ergebnisse (aus Jackpot-Analyse):")
    print(f"  UNTER-repraesentiert: {sorted(UNDER_REPRESENTED)}")
    print(f"  UEBER-repraesentiert: {sorted(OVER_REPRESENTED)}")

    # === ANALYSE 1: Metriken am Stichtag (VORHER-Snapshot) ===
    print(f"\n{'='*100}")
    print("ANALYSE 1: Metriken AM STICHTAG (01.02.2025) - Was wussten wir vorher?")
    print(f"{'='*100}")

    stichtag_metrics = {}
    for z in pool_list:
        stichtag_metrics[z] = calculate_metrics(draws, stichtag_idx, z)

    print(f"\n{'Zahl':<6} {'Index':<8} {'Cnt20':<8} {'MCnt3':<8} {'Gap':<8} {'Kategorie'}")
    print("-" * 60)

    for z in pool_list:
        m = stichtag_metrics[z]
        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"
        print(f"{z:<6} {m['index']:>+6}   {m['count_20']:<8} {m['mcount_3']:<8} {m['gap']:<8} {cat}")

    # === ANALYSE 2: 2 Wochen VOR Stichtag ===
    print(f"\n{'='*100}")
    print("ANALYSE 2: Durchschnitt 2 WOCHEN VOR Stichtag (18.01. - 31.01.2025)")
    print(f"{'='*100}")

    pre_metrics = {z: [] for z in pool_list}

    for idx in range(pre_start_idx, stichtag_idx):
        for z in pool_list:
            m = calculate_metrics(draws, idx, z)
            pre_metrics[z].append(m)

    print(f"\n{'Zahl':<6} {'Avg Idx':<10} {'Avg Cnt':<10} {'Avg MCnt':<10} {'Avg Gap':<10} {'Kategorie'}")
    print("-" * 70)

    pre_averages = {}
    for z in pool_list:
        if pre_metrics[z]:
            avg_idx = sum(m["index"] for m in pre_metrics[z]) / len(pre_metrics[z])
            avg_cnt = sum(m["count_20"] for m in pre_metrics[z]) / len(pre_metrics[z])
            avg_mcnt = sum(m["mcount_3"] for m in pre_metrics[z]) / len(pre_metrics[z])
            avg_gap = sum(m["gap"] for m in pre_metrics[z]) / len(pre_metrics[z])
            pre_averages[z] = {"avg_idx": avg_idx, "avg_cnt": avg_cnt, "avg_mcnt": avg_mcnt, "avg_gap": avg_gap}
        else:
            pre_averages[z] = {"avg_idx": 0, "avg_cnt": 0, "avg_mcnt": 0, "avg_gap": 0}

        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"

        pa = pre_averages[z]
        print(f"{z:<6} {pa['avg_idx']:>+8.2f}   {pa['avg_cnt']:<10.2f} {pa['avg_mcnt']:<10.2f} {pa['avg_gap']:<10.2f} {cat}")

    # === ANALYSE 3: Vergleich Pre vs. Test ===
    print(f"\n{'='*100}")
    print("ANALYSE 3: Durchschnitt waehrend TEST-PHASE (01.02. - 31.07.2025)")
    print(f"{'='*100}")

    test_metrics = {z: [] for z in pool_list}

    for idx in range(stichtag_idx, test_end_idx + 1):
        for z in pool_list:
            m = calculate_metrics(draws, idx, z)
            test_metrics[z].append(m)

    print(f"\n{'Zahl':<6} {'Avg Idx':<10} {'Avg Cnt':<10} {'Avg MCnt':<10} {'Avg Gap':<10} {'Kategorie'}")
    print("-" * 70)

    test_averages = {}
    for z in pool_list:
        if test_metrics[z]:
            avg_idx = sum(m["index"] for m in test_metrics[z]) / len(test_metrics[z])
            avg_cnt = sum(m["count_20"] for m in test_metrics[z]) / len(test_metrics[z])
            avg_mcnt = sum(m["mcount_3"] for m in test_metrics[z]) / len(test_metrics[z])
            avg_gap = sum(m["gap"] for m in test_metrics[z]) / len(test_metrics[z])
            test_averages[z] = {"avg_idx": avg_idx, "avg_cnt": avg_cnt, "avg_mcnt": avg_mcnt, "avg_gap": avg_gap}
        else:
            test_averages[z] = {"avg_idx": 0, "avg_cnt": 0, "avg_mcnt": 0, "avg_gap": 0}

        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"

        ta = test_averages[z]
        print(f"{z:<6} {ta['avg_idx']:>+8.2f}   {ta['avg_cnt']:<10.2f} {ta['avg_mcnt']:<10.2f} {ta['avg_gap']:<10.2f} {cat}")

    # === ANALYSE 4: Delta Pre vs. Test ===
    print(f"\n{'='*100}")
    print("ANALYSE 4: DELTA (Test - Pre) - Wie haben sich die Zahlen veraendert?")
    print(f"{'='*100}")

    print(f"\n{'Zahl':<6} {'Pre Idx':<10} {'Test Idx':<10} {'Delta':<10} {'Kategorie'}")
    print("-" * 55)

    for z in pool_list:
        pa = pre_averages[z]
        ta = test_averages[z]
        delta = ta["avg_idx"] - pa["avg_idx"]

        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"

        print(f"{z:<6} {pa['avg_idx']:>+8.2f}   {ta['avg_idx']:>+8.2f}   {delta:>+8.2f}   {cat}")

    # === ANALYSE 5: Vorhersage-Potential ===
    print(f"\n{'='*100}")
    print("ANALYSE 5: VORHERSAGE-POTENTIAL")
    print(f"{'='*100}")

    # Gruppiere nach Pre-Index
    low_pre_idx = [z for z in pool_list if pre_averages[z]["avg_idx"] < -5]
    med_pre_idx = [z for z in pool_list if -5 <= pre_averages[z]["avg_idx"] <= 5]
    high_pre_idx = [z for z in pool_list if pre_averages[z]["avg_idx"] > 5]

    print(f"\nGruppierung nach PRE-INDEX (2 Wochen vor Stichtag):")
    print(f"\n  NIEDRIGER Pre-Index (< -5): {sorted(low_pre_idx)}")
    print(f"    Davon UNTER-repraesentiert: {sorted(set(low_pre_idx) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER-repraesentiert: {sorted(set(low_pre_idx) & OVER_REPRESENTED)}")

    print(f"\n  MITTLERER Pre-Index (-5 bis +5): {sorted(med_pre_idx)}")
    print(f"    Davon UNTER-repraesentiert: {sorted(set(med_pre_idx) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER-repraesentiert: {sorted(set(med_pre_idx) & OVER_REPRESENTED)}")

    print(f"\n  HOHER Pre-Index (> +5): {sorted(high_pre_idx)}")
    print(f"    Davon UNTER-repraesentiert: {sorted(set(high_pre_idx) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER-repraesentiert: {sorted(set(high_pre_idx) & OVER_REPRESENTED)}")

    # === ANALYSE 6: Korrelation berechnen ===
    print(f"\n{'='*100}")
    print("ANALYSE 6: KORRELATION Pre-Index vs. Jackpot-Beteiligung")
    print(f"{'='*100}")

    # Berechne Durchschnitte pro Kategorie
    under_pre_avg = sum(pre_averages[z]["avg_idx"] for z in UNDER_REPRESENTED if z in pool) / max(len(UNDER_REPRESENTED & pool), 1)
    over_pre_avg = sum(pre_averages[z]["avg_idx"] for z in OVER_REPRESENTED if z in pool) / max(len(OVER_REPRESENTED & pool), 1)
    neutral = pool - UNDER_REPRESENTED - OVER_REPRESENTED
    neutral_pre_avg = sum(pre_averages[z]["avg_idx"] for z in neutral) / max(len(neutral), 1)

    print(f"\n  Durchschnittlicher Pre-Index nach Kategorie:")
    print(f"    UNTER-repraesentiert ({len(UNDER_REPRESENTED & pool)} Zahlen): {under_pre_avg:+.2f}")
    print(f"    UEBER-repraesentiert ({len(OVER_REPRESENTED & pool)} Zahlen): {over_pre_avg:+.2f}")
    print(f"    Neutral ({len(neutral)} Zahlen): {neutral_pre_avg:+.2f}")

    # === FAZIT ===
    print(f"\n{'='*100}")
    print("VORLAEUFIGES FAZIT (ohne Schlussfolgerung)")
    print(f"{'='*100}")

    print(f"""
    Beobachtungen:

    1. Pre-Index (2 Wochen vor Stichtag):
       - UNTER-repraesentierte Zahlen: Avg Index = {under_pre_avg:+.2f}
       - UEBER-repraesentierte Zahlen: Avg Index = {over_pre_avg:+.2f}
       - Neutrale Zahlen: Avg Index = {neutral_pre_avg:+.2f}

    2. Zahlen mit niedrigem Pre-Index (< -5):
       {sorted(low_pre_idx)}
       - Enthaelt {len(set(low_pre_idx) & UNDER_REPRESENTED)} von {len(UNDER_REPRESENTED & pool)} unter-repraesentierten
       - Enthaelt {len(set(low_pre_idx) & OVER_REPRESENTED)} von {len(OVER_REPRESENTED & pool)} ueber-repraesentierten

    3. Test-Entwicklung:
       - Unter-repraesentierte: Pre {under_pre_avg:+.2f} → Test {sum(test_averages[z]['avg_idx'] for z in UNDER_REPRESENTED if z in pool) / max(len(UNDER_REPRESENTED & pool), 1):+.2f}
       - Ueber-repraesentierte: Pre {over_pre_avg:+.2f} → Test {sum(test_averages[z]['avg_idx'] for z in OVER_REPRESENTED if z in pool) / max(len(OVER_REPRESENTED & pool), 1):+.2f}

    [Analyse laeuft - keine Schlussfolgerungen]
    """)


if __name__ == "__main__":
    main()
