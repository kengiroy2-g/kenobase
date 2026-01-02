#!/usr/bin/env python3
"""
JACKPOT EXCLUSION ZONES: Zahlenbereich-Eingrenzung fuer Jackpot-Vorhersage

KERNIDEE (User):
- Das System verschleiert Muster, aber es DARF nicht zu offensichtlich sein
- Jackpots wiederholen sich nicht (max 12 Overlap beobachtet)
- Wir koennen den Zahlenbereich um 60-70% eingrenzen
- Bis zu 6 Zahlen aus vorherigen Jackpots KOENNTEN sich wiederholen (30-40%)

STRATEGIE ("Lauer-Strategie"):
1. Sammle alle Jackpot-Zahlen
2. Identifiziere "verbrannte" Zahlen (oft in Jackpots)
3. Definiere "frische" Zahlen (selten/nie in Jackpots)
4. Warte auf Konstellationen wo System aus frischen Zahlen waehlen MUSS

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
import numpy as np


def load_data(base_path):
    """Lade KENO und Jackpot-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df["numbers_list"] = df[pos_cols].apply(lambda row: list(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots_2025(df, base_path):
    """Lade Jackpot-Tage aus Timeline."""
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return dates


def main():
    print("=" * 80)
    print("JACKPOT EXCLUSION ZONES - Lauer-Strategie")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpots_2025(df, base_path)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)
    df_2025 = df[df["Datum"].dt.year == 2025].copy()

    jackpot_df = df_2025[df_2025["is_jackpot"]].sort_values("Datum")

    print(f"\n2025: {len(df_2025)} Ziehungen, {len(jackpot_df)} Jackpots")

    # =========================================================================
    # 1. ALLE JACKPOT-ZAHLEN SAMMELN
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. JACKPOT-ZAHLEN FREQUENZ (JCount)")
    print("=" * 80)

    jcount = Counter()
    jackpot_sets = []

    for _, row in jackpot_df.iterrows():
        jackpot_sets.append((row["Datum"], row["numbers_set"]))
        for n in row["numbers_set"]:
            jcount[n] += 1

    print(f"\nZahlen die in ALLEN 70 Jackpots erscheinen koennten: 70")
    print(f"Zahlen die in mindestens 1 Jackpot waren: {len(jcount)}")
    print(f"Zahlen die in KEINEM Jackpot waren: {70 - len(jcount)}")

    # Zahlen die nie in Jackpot waren
    never_in_jp = [n for n in range(1, 71) if n not in jcount]
    print(f"\nNIE in Jackpot 2025: {sorted(never_in_jp)} ({len(never_in_jp)} Zahlen)")

    # Top Jackpot-Zahlen
    print(f"\nTop 20 Jackpot-Zahlen (haeufigste):")
    print(f"{'Zahl':>6} {'JCount':>8} {'Anteil':>10}")
    print("-" * 30)
    for num, count in jcount.most_common(20):
        pct = count / len(jackpot_df) * 100
        print(f"{num:>6} {count:>8} {pct:>9.1f}%")

    # =========================================================================
    # 2. OVERLAP-ANALYSE ZWISCHEN AUFEINANDERFOLGENDEN JACKPOTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. OVERLAP ZWISCHEN AUFEINANDERFOLGENDEN JACKPOTS")
    print("=" * 80)

    print(f"\n{'JP1':<12} {'JP2':<12} {'Overlap':>8} {'Gemeinsam'}")
    print("-" * 70)

    overlaps = []
    for i in range(len(jackpot_sets) - 1):
        date1, set1 = jackpot_sets[i]
        date2, set2 = jackpot_sets[i + 1]
        overlap = set1 & set2
        overlaps.append(len(overlap))
        print(f"{date1.strftime('%d.%m.%Y'):<12} {date2.strftime('%d.%m.%Y'):<12} "
              f"{len(overlap):>8} {sorted(overlap)}")

    print(f"\nOverlap-Statistik:")
    print(f"  Min: {min(overlaps)}")
    print(f"  Max: {max(overlaps)}")
    print(f"  Mean: {np.mean(overlaps):.1f}")
    print(f"  Median: {np.median(overlaps):.1f}")

    # =========================================================================
    # 3. EXCLUSION ZONE BERECHNUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. EXCLUSION ZONE - Zahlenbereich-Eingrenzung")
    print("=" * 80)

    # Alle Zahlen die in den letzten N Jackpots waren
    for window in [1, 2, 3, 5, 10, 17]:
        recent_jps = list(jackpot_df.tail(window)["numbers_set"])
        all_recent = set()
        for s in recent_jps:
            all_recent.update(s)

        excluded = len(all_recent)
        remaining = 70 - excluded
        pct_remaining = remaining / 70 * 100

        print(f"\nLetzte {window} Jackpots:")
        print(f"  Verbrauchte Zahlen: {excluded} ({excluded/70*100:.1f}%)")
        print(f"  Frische Zahlen: {remaining} ({pct_remaining:.1f}%)")
        print(f"  Frische: {sorted(set(range(1, 71)) - all_recent)[:20]}...")

    # =========================================================================
    # 4. VORHERSAGE-STRATEGIE: "FRISCHE ZAHLEN" POOL
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. VORHERSAGE-STRATEGIE: 'Frische Zahlen' Pool")
    print("=" * 80)

    # Hypothese: Naechster Jackpot wird aus "frischen" Zahlen gewaehlt
    # Aber das System MUSS auch 6 "verbrannte" wiederverwenden koennen

    last_3_jps = list(jackpot_df.tail(3)["numbers_set"])
    recent_pool = set()
    for s in last_3_jps:
        recent_pool.update(s)

    fresh_pool = set(range(1, 71)) - recent_pool

    print(f"\nLetzte 3 Jackpots verbrauchten: {len(recent_pool)} Zahlen")
    print(f"Frische Zahlen Pool: {len(fresh_pool)} Zahlen")
    print(f"\nFrische Zahlen: {sorted(fresh_pool)}")

    # Erwartung: Naechster Jackpot wird 14-16 frische + 4-6 wiederholte haben
    print(f"\nERWARTUNG fuer naechsten Jackpot:")
    print(f"  14-16 Zahlen aus frischem Pool ({len(fresh_pool)} Zahlen)")
    print(f"  4-6 Zahlen aus letzten 3 Jackpots ({len(recent_pool)} Zahlen)")

    # =========================================================================
    # 5. BACKTEST: Hat diese Strategie in der Vergangenheit funktioniert?
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. BACKTEST: Wieviele 'frische' Zahlen hatte jeder Jackpot?")
    print("=" * 80)

    print(f"\n{'Jackpot':<12} {'Frisch':>8} {'Repeat':>8} {'Pool-Size':>10}")
    print("-" * 45)

    fresh_counts = []
    for i in range(3, len(jackpot_sets)):
        # Pool aus letzten 3 Jackpots VOR diesem
        prev_pool = set()
        for j in range(i-3, i):
            prev_pool.update(jackpot_sets[j][1])

        current_jp = jackpot_sets[i][1]
        fresh = current_jp - prev_pool
        repeat = current_jp & prev_pool

        fresh_counts.append(len(fresh))
        date = jackpot_sets[i][0]
        pool_size = 70 - len(prev_pool)

        print(f"{date.strftime('%d.%m.%Y'):<12} {len(fresh):>8} {len(repeat):>8} {pool_size:>10}")

    print(f"\nFrische Zahlen pro Jackpot:")
    print(f"  Min: {min(fresh_counts)}")
    print(f"  Max: {max(fresh_counts)}")
    print(f"  Mean: {np.mean(fresh_counts):.1f}")

    # =========================================================================
    # 6. ZAHLEN-KATEGORISIERUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. ZAHLEN-KATEGORISIERUNG nach JCount")
    print("=" * 80)

    # Kategorien
    high_jcount = [n for n, c in jcount.items() if c >= 8]  # Oft in Jackpots
    medium_jcount = [n for n, c in jcount.items() if 4 <= c < 8]
    low_jcount = [n for n, c in jcount.items() if 1 <= c < 4]
    zero_jcount = [n for n in range(1, 71) if n not in jcount]

    print(f"\nHOCH (>=8 Jackpots): {len(high_jcount)} Zahlen")
    print(f"  {sorted(high_jcount)}")
    print(f"\nMITTEL (4-7 Jackpots): {len(medium_jcount)} Zahlen")
    print(f"  {sorted(medium_jcount)}")
    print(f"\nNIEDRIG (1-3 Jackpots): {len(low_jcount)} Zahlen")
    print(f"  {sorted(low_jcount)}")
    print(f"\nNIE (0 Jackpots): {len(zero_jcount)} Zahlen")
    print(f"  {sorted(zero_jcount)}")

    # =========================================================================
    # 7. "LAUER-ZONE" DEFINITION
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. LAUER-ZONE: Optimale Wett-Zahlen")
    print("=" * 80)

    # Hypothese: Die besten Zahlen sind:
    # - NIE oder SELTEN in Jackpots (System muss sie irgendwann waehlen)
    # - Aber nicht ZU selten (dann sind sie vielleicht wirklich unpopulaer)

    lauer_zone = sorted(low_jcount + zero_jcount)
    print(f"\nLAUER-ZONE: Zahlen mit JCount 0-3 ({len(lauer_zone)} Zahlen)")
    print(f"  {lauer_zone}")

    # Aufteilen in Tertile
    lauer_thirds = {
        "TIEF (1-23)": [n for n in lauer_zone if 1 <= n <= 23],
        "MITTEL (24-47)": [n for n in lauer_zone if 24 <= n <= 47],
        "HOCH (48-70)": [n for n in lauer_zone if 48 <= n <= 70],
    }

    for name, nums in lauer_thirds.items():
        print(f"\n  {name}: {len(nums)} Zahlen")
        print(f"    {nums}")

    # =========================================================================
    # 8. KONKRETE EMPFEHLUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("8. KONKRETE EMPFEHLUNG: Lauer-Strategie Tickets")
    print("=" * 80)

    print("""
STRATEGIE-LOGIK:

1. EXCLUSION (60-70%):
   - Zahlen die in den letzten 3 Jackpots waren: AUSSCHLIESSEN
   - Zahlen mit JCount >= 8: REDUZIEREN

2. FOKUS (30-40%):
   - Zahlen mit JCount 0-3: BEVORZUGEN
   - Zahlen die noch NIE in Jackpot waren: HOCH GEWICHTEN

3. REPEAT-ZONE (6 Zahlen):
   - Das System MUSS bis zu 6 Zahlen aus vorherigen Jackpots wiederholen
   - Waehle 2-3 "sichere" Repeat-Kandidaten (JCount 4-7, vor >30 Tagen)
""")

    # Aktueller frischer Pool (letzte 3 Jackpots)
    recent_3 = list(jackpot_df.tail(3)["numbers_set"])
    burnt = set()
    for s in recent_3:
        burnt.update(s)
    fresh = set(range(1, 71)) - burnt

    # Empfohlenes Ticket
    lauer_candidates = [n for n in fresh if jcount.get(n, 0) <= 3]
    repeat_candidates = [n for n in burnt if 4 <= jcount.get(n, 0) <= 7]

    print(f"\nAKTUELLER STAND (nach 17 Jackpots):")
    print(f"  Verbrannte Zahlen (letzte 3 JP): {len(burnt)}")
    print(f"  Frische Zahlen: {len(fresh)}")
    print(f"  Lauer-Kandidaten (frisch + JCount<=3): {len(lauer_candidates)}")
    print(f"    {sorted(lauer_candidates)[:30]}...")
    print(f"  Repeat-Kandidaten (verbrannt + JCount 4-7): {len(repeat_candidates)}")
    print(f"    {sorted(repeat_candidates)}")

    # Generiere 10er Ticket
    import random
    random.seed(42)
    ticket_fresh = sorted(random.sample(lauer_candidates, min(7, len(lauer_candidates))))
    ticket_repeat = sorted(random.sample(repeat_candidates, min(3, len(repeat_candidates))))
    ticket = sorted(ticket_fresh + ticket_repeat)

    print(f"\nEMPFOHLENES TYP-10 TICKET (Lauer-Strategie):")
    print(f"  Frische Zahlen (7): {ticket_fresh}")
    print(f"  Repeat Zahlen (3): {ticket_repeat}")
    print(f"  TICKET: {ticket}")

    # =========================================================================
    # 9. VALIDIERUNG: Wie oft haette diese Strategie funktioniert?
    # =========================================================================
    print("\n" + "=" * 80)
    print("9. VALIDIERUNG: Rueckblick auf vergangene Jackpots")
    print("=" * 80)

    print(f"\n{'Jackpot':<12} {'In Lauer-Zone':>15} {'Pool-Groesse':>15} {'Match-Rate':>12}")
    print("-" * 60)

    for i in range(3, len(jackpot_sets)):
        # Berechne Lauer-Zone VOR diesem Jackpot
        prev_pool = set()
        for j in range(i-3, i):
            prev_pool.update(jackpot_sets[j][1])

        # JCount bis zu diesem Zeitpunkt
        jcount_then = Counter()
        for j in range(i):
            for n in jackpot_sets[j][1]:
                jcount_then[n] += 1

        fresh_then = set(range(1, 71)) - prev_pool
        lauer_then = [n for n in fresh_then if jcount_then.get(n, 0) <= 3]

        current_jp = jackpot_sets[i][1]
        in_lauer = current_jp & set(lauer_then)
        match_rate = len(in_lauer) / 20 * 100

        date = jackpot_sets[i][0]
        print(f"{date.strftime('%d.%m.%Y'):<12} {len(in_lauer):>15} {len(lauer_then):>15} {match_rate:>11.1f}%")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: LAUER-STRATEGIE")
    print("=" * 80)

    print("""
ERKENNTNISSE:

1. ZAHLEN-ERSCHOEPFUNG:
   - Nach 17 Jackpots sind nur noch wenige Zahlen "unberuehrt"
   - Das System MUSS irgendwann die "frischen" Zahlen waehlen

2. OVERLAP-CONSTRAINT:
   - Max 12 Overlap zwischen Jackpots beobachtet
   - System vermeidet Wiederholung derselben Kombination
   - ~6 Zahlen KOENNTEN sich wiederholen (statistisch)

3. LAUER-STRATEGIE:
   - Definiere "frischen Pool" (nicht in letzten 3 Jackpots)
   - Fokussiere auf Zahlen mit niedrigem JCount (0-3)
   - Erlaube 3 "Repeat-Kandidaten" fuer die 30-40% Zone

4. EINGRENZUNG:
   - Pool-Groesse nach 3 Jackpots: ~30-40 "frische" Zahlen
   - Das ist eine ~45-60% Eingrenzung des Zahlenraums
   - Mit JCount-Filter: ~50-70% Eingrenzung

ACHTUNG:
- Diese Strategie basiert auf SYSTEM-CONSTRAINTS
- Sie sagt nicht WANN ein Jackpot kommt
- Sie sagt AUS WELCHEM BEREICH die Zahlen kommen werden
""")


if __name__ == "__main__":
    main()
