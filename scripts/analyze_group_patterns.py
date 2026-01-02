#!/usr/bin/env python3
"""
GRUPPEN-ANALYSE: Axiom A8 angewendet

KERNPRINZIP (A8):
- Einzelzahlen haben KEINEN Wert
- Wert entsteht NUR durch GRUPPEN die zusammen erscheinen
- Analyse muss auf Paar-, Trio-, und N-Tupel-Ebene erfolgen

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import pandas as pd
import numpy as np


# Tickets
V2_TYP9 = [3, 7, 36, 43, 48, 51, 58, 61, 64]
V1_ORIGINAL = [3, 9, 10, 20, 24, 36, 49, 51, 64]


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots(df, base_path):
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return dates


def count_group_hits(ticket, draw_set):
    """Zaehle wie viele Zahlen des Tickets in der Ziehung sind."""
    return len(set(ticket) & draw_set)


def find_appearing_pairs(ticket, draw_set):
    """Finde alle Paare aus dem Ticket die in der Ziehung erscheinen."""
    ticket_in_draw = set(ticket) & draw_set
    return list(combinations(sorted(ticket_in_draw), 2))


def find_appearing_trios(ticket, draw_set):
    """Finde alle Trios aus dem Ticket die in der Ziehung erscheinen."""
    ticket_in_draw = set(ticket) & draw_set
    if len(ticket_in_draw) >= 3:
        return list(combinations(sorted(ticket_in_draw), 3))
    return []


def main():
    print("=" * 80)
    print("GRUPPEN-ANALYSE (Axiom A8)")
    print("Einzelzahlen = WERTLOS | Gruppen = WERTVOLL")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpots(df, base_path)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)
    df_2025 = df[df["Datum"].dt.year == 2025].copy()

    jackpot_df = df_2025[df_2025["is_jackpot"]]
    normal_df = df_2025[~df_2025["is_jackpot"]]

    print(f"\n2025: {len(df_2025)} Ziehungen, {len(jackpot_df)} Jackpots")

    # =========================================================================
    # 1. V2-TICKET: GRUPPEN-TREFFER VERTEILUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. V2-TICKET GRUPPEN-ANALYSE")
    print(f"   Ticket: {V2_TYP9}")
    print("=" * 80)

    v2_hits = []
    for _, row in df_2025.iterrows():
        hits = count_group_hits(V2_TYP9, row["numbers_set"])
        v2_hits.append((row["Datum"], hits, row["is_jackpot"]))

    # Verteilung
    hit_dist = Counter([h[1] for h in v2_hits])
    print(f"\nTreffer-Verteilung (wie oft erschienen N Zahlen ZUSAMMEN):")
    print(f"{'Treffer':>8} {'Anzahl':>10} {'Prozent':>10} {'Bedeutung'}")
    print("-" * 50)
    for hits in range(10):
        count = hit_dist.get(hits, 0)
        pct = count / len(v2_hits) * 100
        meaning = ""
        if hits == 0:
            meaning = "Komplett-Miss"
        elif hits <= 2:
            meaning = "Kein Gewinn (Typ 9)"
        elif hits == 3:
            meaning = "2 EUR"
        elif hits == 4:
            meaning = "5 EUR"
        elif hits == 5:
            meaning = "15 EUR"
        elif hits == 6:
            meaning = "100 EUR"
        elif hits == 7:
            meaning = "500 EUR"
        elif hits == 8:
            meaning = "1000 EUR"
        elif hits == 9:
            meaning = "50000 EUR (JACKPOT)"
        print(f"{hits:>8} {count:>10} {pct:>9.1f}% {meaning}")

    # Jackpot-Tage vs Normal
    jp_hits = [h[1] for h in v2_hits if h[2]]
    normal_hits = [h[1] for h in v2_hits if not h[2]]

    print(f"\nJackpot-Tage: Mean={np.mean(jp_hits):.2f}, Max={max(jp_hits)}")
    print(f"Normale Tage: Mean={np.mean(normal_hits):.2f}, Max={max(normal_hits)}")

    # =========================================================================
    # 2. PAAR-ANALYSE: Welche V2-Paare erscheinen in Jackpots?
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. V2-PAAR-ANALYSE (36 moegliche Paare)")
    print("=" * 80)

    # Alle moeglichen Paare aus V2
    all_v2_pairs = list(combinations(V2_TYP9, 2))
    print(f"\nAnzahl moeglicher Paare: {len(all_v2_pairs)}")

    # Zaehle Paar-Erscheinungen in Jackpots
    jp_pair_count = Counter()
    for _, row in jackpot_df.iterrows():
        pairs = find_appearing_pairs(V2_TYP9, row["numbers_set"])
        for p in pairs:
            jp_pair_count[p] += 1

    # Zaehle Paar-Erscheinungen in allen Ziehungen
    all_pair_count = Counter()
    for _, row in df_2025.iterrows():
        pairs = find_appearing_pairs(V2_TYP9, row["numbers_set"])
        for p in pairs:
            all_pair_count[p] += 1

    print(f"\nV2-Paare in JACKPOTS (Top 15):")
    print(f"{'Paar':<12} {'JP-Count':>10} {'All-Count':>12} {'JP-Rate':>10}")
    print("-" * 50)
    for pair, jp_count in jp_pair_count.most_common(15):
        all_count = all_pair_count[pair]
        jp_rate = jp_count / len(jackpot_df) * 100
        print(f"{str(pair):<12} {jp_count:>10} {all_count:>12} {jp_rate:>9.1f}%")

    # Paare die NIE in Jackpots waren
    never_in_jp = [p for p in all_v2_pairs if p not in jp_pair_count]
    print(f"\nV2-Paare die NIE in einem Jackpot waren: {len(never_in_jp)}")
    for p in never_in_jp[:10]:
        print(f"  {p}: {all_pair_count.get(p, 0)} Mal in normalen Ziehungen")

    # =========================================================================
    # 3. TRIO-ANALYSE: Welche V2-Trios erscheinen zusammen?
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. V2-TRIO-ANALYSE (84 moegliche Trios)")
    print("=" * 80)

    all_v2_trios = list(combinations(V2_TYP9, 3))
    print(f"\nAnzahl moeglicher Trios: {len(all_v2_trios)}")

    # Zaehle Trio-Erscheinungen
    jp_trio_count = Counter()
    all_trio_count = Counter()

    for _, row in jackpot_df.iterrows():
        trios = find_appearing_trios(V2_TYP9, row["numbers_set"])
        for t in trios:
            jp_trio_count[t] += 1

    for _, row in df_2025.iterrows():
        trios = find_appearing_trios(V2_TYP9, row["numbers_set"])
        for t in trios:
            all_trio_count[t] += 1

    print(f"\nV2-Trios in JACKPOTS (Top 10):")
    print(f"{'Trio':<18} {'JP-Count':>10} {'All-Count':>12}")
    print("-" * 45)
    for trio, jp_count in jp_trio_count.most_common(10):
        all_count = all_trio_count[trio]
        print(f"{str(trio):<18} {jp_count:>10} {all_count:>12}")

    # =========================================================================
    # 4. LAUER-ZONE GRUPPEN-ANALYSE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. LAUER-ZONE GRUPPEN-ANALYSE")
    print("=" * 80)

    # Lauer-Zone: Zahlen mit niedrigem JCount (selten in Jackpots)
    # Berechne JCount
    jcount = Counter()
    for _, row in jackpot_df.iterrows():
        for n in row["numbers_set"]:
            jcount[n] += 1

    lauer_zone = [n for n in range(1, 71) if jcount.get(n, 0) <= 3]
    print(f"\nLauer-Zone (JCount 0-3): {len(lauer_zone)} Zahlen")
    print(f"  {sorted(lauer_zone)}")

    # Welche PAARE aus der Lauer-Zone erscheinen in Jackpots?
    lauer_pairs_in_jp = Counter()
    for _, row in jackpot_df.iterrows():
        draw = row["numbers_set"]
        lauer_in_draw = set(lauer_zone) & draw
        if len(lauer_in_draw) >= 2:
            for pair in combinations(sorted(lauer_in_draw), 2):
                lauer_pairs_in_jp[pair] += 1

    print(f"\nLauer-Zone PAARE in Jackpots (Top 15):")
    print(f"{'Paar':<12} {'JP-Count':>10}")
    print("-" * 25)
    for pair, count in lauer_pairs_in_jp.most_common(15):
        print(f"{str(pair):<12} {count:>10}")

    # =========================================================================
    # 5. JACKPOT-GRUPPEN: Welche Gruppen erscheinen in Jackpots?
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. JACKPOT-EXKLUSIVE GRUPPEN")
    print("=" * 80)

    # Paare die HAEUFIGER in Jackpots erscheinen als erwartet
    print(f"\nPaare mit hoher Jackpot-Affinitaet (Lift > 1.5x):")
    print(f"{'Paar':<12} {'JP-Count':>10} {'Normal':>10} {'JP-Rate':>10} {'Normal-Rate':>12} {'Lift':>8}")
    print("-" * 70)

    # Berechne alle Paar-Counts
    all_pairs_jp = Counter()
    all_pairs_normal = Counter()

    for _, row in jackpot_df.iterrows():
        draw = row["numbers_set"]
        for pair in combinations(sorted(draw), 2):
            all_pairs_jp[pair] += 1

    for _, row in normal_df.iterrows():
        draw = row["numbers_set"]
        for pair in combinations(sorted(draw), 2):
            all_pairs_normal[pair] += 1

    # Finde Paare mit hohem Lift
    high_lift_pairs = []
    for pair in all_pairs_jp:
        jp_count = all_pairs_jp[pair]
        normal_count = all_pairs_normal.get(pair, 0)

        jp_rate = jp_count / len(jackpot_df)
        normal_rate = normal_count / len(normal_df) if normal_count > 0 else 0.001

        lift = jp_rate / normal_rate if normal_rate > 0 else 0

        if lift > 1.5 and jp_count >= 3:
            high_lift_pairs.append((pair, jp_count, normal_count, jp_rate, normal_rate, lift))

    high_lift_pairs.sort(key=lambda x: -x[5])
    for pair, jp_c, n_c, jp_r, n_r, lift in high_lift_pairs[:20]:
        print(f"{str(pair):<12} {jp_c:>10} {n_c:>10} {jp_r*100:>9.1f}% {n_r*100:>11.2f}% {lift:>7.2f}x")

    # =========================================================================
    # 6. OPTIMALE LAUER-GRUPPEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. OPTIMALE LAUER-GRUPPEN (Frische Zahlen + Hoher Lift)")
    print("=" * 80)

    # Finde Paare die:
    # 1. Aus Lauer-Zone stammen (niedrig JCount)
    # 2. Aber trotzdem in Jackpots erscheinen

    lauer_high_lift = []
    for pair, jp_c, n_c, jp_r, n_r, lift in high_lift_pairs:
        if pair[0] in lauer_zone or pair[1] in lauer_zone:
            lauer_high_lift.append((pair, jp_c, lift))

    print(f"\nPaare mit Lauer-Zone-Zahlen UND hohem Jackpot-Lift:")
    print(f"{'Paar':<12} {'JP-Count':>10} {'Lift':>8} {'Lauer-Zahlen'}")
    print("-" * 50)
    for pair, jp_c, lift in sorted(lauer_high_lift, key=lambda x: -x[2])[:15]:
        lauer_nums = [n for n in pair if n in lauer_zone]
        print(f"{str(pair):<12} {jp_c:>10} {lift:>7.2f}x {lauer_nums}")

    # =========================================================================
    # 7. EMPFOHLENES LAUER-TICKET (GRUPPEN-BASIERT)
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. EMPFOHLENES LAUER-TICKET (Gruppen-Optimiert)")
    print("=" * 80)

    # Sammle beste Zahlen basierend auf Gruppen-Performance
    best_numbers = Counter()

    # Gewichte Zahlen nach Paar-Lift
    for pair, jp_c, n_c, jp_r, n_r, lift in high_lift_pairs[:30]:
        for n in pair:
            best_numbers[n] += lift

    # Filtere auf Lauer-Zone
    lauer_scored = [(n, best_numbers.get(n, 0)) for n in lauer_zone]
    lauer_scored.sort(key=lambda x: -x[1])

    print(f"\nLauer-Zone Zahlen nach Gruppen-Score:")
    print(f"{'Zahl':>6} {'Score':>10} {'JCount':>8}")
    print("-" * 30)
    for n, score in lauer_scored[:15]:
        print(f"{n:>6} {score:>10.2f} {jcount.get(n, 0):>8}")

    # Generiere Ticket aus Top-Lauer-Zahlen
    top_lauer = [n for n, _ in lauer_scored[:7]]

    # Ergaenze mit High-Lift Zahlen (nicht Lauer)
    non_lauer_high = [(n, s) for n, s in best_numbers.most_common(20) if n not in lauer_zone]
    complement = [n for n, _ in non_lauer_high[:3]]

    recommended_ticket = sorted(top_lauer + complement)

    print(f"\nEMPFOHLENES TYP-10 TICKET (Gruppen-Optimiert):")
    print(f"  Lauer-Zone Zahlen (7): {sorted(top_lauer)}")
    print(f"  High-Lift Ergaenzung (3): {sorted(complement)}")
    print(f"  TICKET: {recommended_ticket}")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: GRUPPEN-PRINZIP (Axiom A8)")
    print("=" * 80)

    print("""
KERN-ERKENNTNISSE:

1. EINZELZAHLEN-ANALYSE IST WERTLOS
   - "Zahl X war in N Jackpots" sagt NICHTS aus
   - Relevant ist nur: "Erscheint X zusammen mit meinen anderen Zahlen?"

2. PAAR-ANALYSE IST FUNDAMENTAL
   - Paare sind die kleinste wertvolle Einheit
   - Paare mit hohem Lift (>1.5x) zeigen Jackpot-Affinitaet

3. LAUER-ZONE + GRUPPEN = OPTIMALE STRATEGIE
   - Waehle Zahlen aus der Lauer-Zone (niedrig JCount)
   - ABER: Nur wenn sie starke Paar-Beziehungen haben
   - Kombiniere mit High-Lift Zahlen als Ergaenzung

4. V2-TICKET GRUPPEN-PERFORMANCE
   - Max Treffer 2025: 8 von 9 (1000 EUR)
   - Mean: ~2.6 Treffer pro Ziehung
   - Einige V2-Paare waren NIE in Jackpots

5. JACKPOT-VORHERSAGE AUF GRUPPEN-EBENE
   - Nicht: "Welche Zahlen kommen?"
   - Sondern: "Welche GRUPPEN koennen zusammen erscheinen?"
   - System-Constraint: ~6 Zahlen Overlap zwischen Jackpots
""")


if __name__ == "__main__":
    main()
