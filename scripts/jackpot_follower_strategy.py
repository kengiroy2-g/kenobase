#!/usr/bin/env python3
"""
JACKPOT FOLLOWER STRATEGIE

Analysiert Jackpots und erstellt ein Ticket fuer den NAECHSTEN Jackpot.

LOGIK (basierend auf KERNPRAEMISSEN):
1. Nach einem Jackpot "weiss" das System welche Zahlen "gefaehrlich" waren
2. Das System wird diese Zahlen teilweise meiden (aber nicht komplett)
3. Es gibt einen Overlap von 4-9 Zahlen zwischen aufeinanderfolgenden Jackpots
4. Bestimmte PAARE erscheinen haeufiger in Jackpot-Sequenzen

STRATEGIE:
- Analysiere den letzten Jackpot
- Identifiziere "sichere" Ueberlaeufer (Zahlen die oft wiederkommen)
- Ergaenze mit Zahlen aus der "Lauer-Zone" (frische Zahlen)
- Beruecksichtige starke Paar-Verbindungen

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import pandas as pd
import numpy as np
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kenobase.core.keno_quotes import get_fixed_quote


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df["numbers_list"] = df[pos_cols].apply(lambda row: sorted(row.dropna().astype(int).tolist()), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots(df, base_path):
    """Lade Jackpot-Daten und gib DataFrame mit Jackpot-Ziehungen zurueck."""
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in dates)
    return df[df["is_jackpot"]].copy()


def analyze_jackpot_transitions(jackpot_df):
    """Analysiere Uebergaenge zwischen aufeinanderfolgenden Jackpots."""
    transitions = []

    jackpots = jackpot_df.sort_values("Datum").reset_index(drop=True)

    for i in range(len(jackpots) - 1):
        jp1 = jackpots.iloc[i]
        jp2 = jackpots.iloc[i + 1]

        set1 = jp1["numbers_set"]
        set2 = jp2["numbers_set"]

        overlap = set1 & set2
        only_in_first = set1 - set2
        only_in_second = set2 - set1

        transitions.append({
            "date1": jp1["Datum"],
            "date2": jp2["Datum"],
            "numbers1": set1,
            "numbers2": set2,
            "overlap": overlap,
            "overlap_count": len(overlap),
            "dropped": only_in_first,
            "new": only_in_second
        })

    return transitions


def calculate_number_persistence(transitions):
    """Berechne wie oft jede Zahl im naechsten Jackpot wiederkehrt."""
    persistence = defaultdict(lambda: {"appeared": 0, "persisted": 0})

    for t in transitions:
        for n in t["numbers1"]:
            persistence[n]["appeared"] += 1
            if n in t["numbers2"]:
                persistence[n]["persisted"] += 1

    # Berechne Persistenz-Rate
    result = {}
    for n, data in persistence.items():
        if data["appeared"] > 0:
            result[n] = {
                "appeared": data["appeared"],
                "persisted": data["persisted"],
                "rate": data["persisted"] / data["appeared"]
            }

    return result


def calculate_pair_persistence(transitions):
    """Berechne wie oft Paare in aufeinanderfolgenden Jackpots erscheinen."""
    pair_stats = defaultdict(lambda: {"in_first": 0, "in_both": 0})

    for t in transitions:
        # Paare im ersten Jackpot
        pairs1 = set(combinations(sorted(t["numbers1"]), 2))
        pairs2 = set(combinations(sorted(t["numbers2"]), 2))

        for pair in pairs1:
            pair_stats[pair]["in_first"] += 1
            if pair in pairs2:
                pair_stats[pair]["in_both"] += 1

    # Berechne Persistenz-Rate
    result = {}
    for pair, data in pair_stats.items():
        if data["in_first"] >= 2:  # Mindestens 2x erschienen
            result[pair] = {
                "in_first": data["in_first"],
                "in_both": data["in_both"],
                "rate": data["in_both"] / data["in_first"]
            }

    return result


def calculate_fresh_number_success(transitions, all_df):
    """Berechne wie oft 'frische' Zahlen (nicht im letzten JP) im naechsten JP erscheinen."""
    fresh_success = defaultdict(lambda: {"opportunities": 0, "appeared": 0})

    for t in transitions:
        fresh_numbers = set(range(1, 71)) - t["numbers1"]

        for n in fresh_numbers:
            fresh_success[n]["opportunities"] += 1
            if n in t["numbers2"]:
                fresh_success[n]["appeared"] += 1

    result = {}
    for n, data in fresh_success.items():
        if data["opportunities"] > 0:
            result[n] = {
                "opportunities": data["opportunities"],
                "appeared": data["appeared"],
                "rate": data["appeared"] / data["opportunities"]
            }

    return result


def generate_post_jackpot_ticket(last_jackpot_numbers, persistence_data, pair_persistence,
                                  fresh_success, ticket_size=9):
    """
    Generiere ein Ticket basierend auf dem letzten Jackpot.

    Strategie:
    1. Nimm 3-4 Zahlen mit hoher Persistenz-Rate aus dem letzten Jackpot
    2. Nimm 2-3 "frische" Zahlen mit hoher Erfolgsrate
    3. Ergaenze mit Zahlen die starke Paar-Verbindungen haben
    """
    last_jp_set = set(last_jackpot_numbers)

    # 1. Persistente Zahlen aus letztem Jackpot (Top 4)
    persistent_candidates = []
    for n in last_jp_set:
        if n in persistence_data:
            persistent_candidates.append((n, persistence_data[n]["rate"]))

    persistent_candidates.sort(key=lambda x: -x[1])
    persistent_picks = [n for n, _ in persistent_candidates[:4]]

    # 2. Frische Zahlen (nicht im letzten JP) mit hoher Erfolgsrate (Top 3)
    fresh_candidates = []
    for n in range(1, 71):
        if n not in last_jp_set and n in fresh_success:
            fresh_candidates.append((n, fresh_success[n]["rate"]))

    fresh_candidates.sort(key=lambda x: -x[1])
    fresh_picks = [n for n, _ in fresh_candidates[:5]]  # Mehr Kandidaten

    # 3. Finde Zahlen mit starken Paar-Verbindungen zu den persistent_picks
    pair_bonus = defaultdict(float)
    for pair, data in pair_persistence.items():
        if data["rate"] > 0.3:  # Mindestens 30% Persistenz
            n1, n2 = pair
            if n1 in persistent_picks:
                pair_bonus[n2] += data["rate"]
            if n2 in persistent_picks:
                pair_bonus[n1] += data["rate"]

    # Sortiere fresh_picks nach Paar-Bonus
    fresh_with_bonus = [(n, fresh_success[n]["rate"] + pair_bonus.get(n, 0))
                        for n in fresh_picks if n not in persistent_picks]
    fresh_with_bonus.sort(key=lambda x: -x[1])

    # Kombiniere: 4 persistent + 5 frische (mit Paar-Bonus)
    ticket = set(persistent_picks)

    for n, _ in fresh_with_bonus:
        if len(ticket) >= ticket_size:
            break
        ticket.add(n)

    # Falls noch nicht genug, fuege Top-Fresh hinzu
    if len(ticket) < ticket_size:
        for n, _ in fresh_candidates:
            if n not in ticket:
                ticket.add(n)
            if len(ticket) >= ticket_size:
                break

    return sorted(ticket)[:ticket_size]


def backtest_strategy(df, jackpot_df, persistence_data, pair_persistence, fresh_success):
    """Teste die Strategie: Nach jedem Jackpot ein neues Ticket fuer den naechsten."""
    results = []

    jackpots = jackpot_df.sort_values("Datum").reset_index(drop=True)

    for i in range(len(jackpots) - 1):
        jp1 = jackpots.iloc[i]
        jp2 = jackpots.iloc[i + 1]

        # Generiere Ticket basierend auf JP1
        ticket = generate_post_jackpot_ticket(
            jp1["numbers_set"],
            persistence_data,
            pair_persistence,
            fresh_success,
            ticket_size=9
        )

        # Teste gegen JP2
        jp2_set = jp2["numbers_set"]
        hits = len(set(ticket) & jp2_set)
        win = get_fixed_quote(9, hits)

        results.append({
            "jp1_date": jp1["Datum"],
            "jp2_date": jp2["Datum"],
            "ticket": ticket,
            "jp2_numbers": sorted(jp2_set),
            "hits": hits,
            "win": win,
            "matching": sorted(set(ticket) & jp2_set)
        })

    return results


def main():
    print("=" * 80)
    print("JACKPOT FOLLOWER STRATEGIE")
    print("=" * 80)

    print("""
LOGIK:
- Nach jedem Jackpot wird ein NEUES Ticket generiert
- Basiert auf Jackpot-Uebergangs-Mustern
- Kombiniert persistente Zahlen mit frischen Zahlen
- Beruecksichtigt Paar-Verbindungen
""")

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_df = get_jackpots(df, base_path)

    print(f"Daten geladen: {len(df)} Ziehungen, {len(jackpot_df)} Jackpots")

    # =========================================================================
    # 1. JACKPOT-UEBERGANGS-ANALYSE
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. JACKPOT-UEBERGANGS-ANALYSE")
    print("=" * 80)

    transitions = analyze_jackpot_transitions(jackpot_df)

    overlaps = [t["overlap_count"] for t in transitions]
    print(f"\nOverlap zwischen aufeinanderfolgenden Jackpots:")
    print(f"  Min: {min(overlaps)}, Max: {max(overlaps)}, Mean: {np.mean(overlaps):.1f}")

    # =========================================================================
    # 2. ZAHLEN-PERSISTENZ
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. ZAHLEN-PERSISTENZ (Wiederkehr im naechsten Jackpot)")
    print("=" * 80)

    persistence_data = calculate_number_persistence(transitions)

    # Top persistente Zahlen
    sorted_persistence = sorted(persistence_data.items(), key=lambda x: -x[1]["rate"])

    print(f"\n{'Zahl':>6} {'Erschienen':>12} {'Wiedergekehrt':>14} {'Rate':>8}")
    print("-" * 45)
    for n, data in sorted_persistence[:15]:
        print(f"{n:>6} {data['appeared']:>12} {data['persisted']:>14} {data['rate']:>7.1%}")

    # =========================================================================
    # 3. PAAR-PERSISTENZ
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. PAAR-PERSISTENZ (Paare die in Folge-Jackpots wiederkehren)")
    print("=" * 80)

    pair_persistence = calculate_pair_persistence(transitions)

    sorted_pairs = sorted(pair_persistence.items(), key=lambda x: -x[1]["rate"])

    print(f"\n{'Paar':<12} {'In JP1':>8} {'In Beiden':>10} {'Rate':>8}")
    print("-" * 42)
    for pair, data in sorted_pairs[:15]:
        print(f"{str(pair):<12} {data['in_first']:>8} {data['in_both']:>10} {data['rate']:>7.1%}")

    # =========================================================================
    # 4. FRISCHE ZAHLEN ERFOLGSRATE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. FRISCHE ZAHLEN (Zahlen die NICHT im letzten JP waren)")
    print("=" * 80)

    fresh_success = calculate_fresh_number_success(transitions, df)

    sorted_fresh = sorted(fresh_success.items(), key=lambda x: -x[1]["rate"])

    print(f"\n{'Zahl':>6} {'Moeglichkeiten':>15} {'Erschienen':>12} {'Rate':>8}")
    print("-" * 45)
    for n, data in sorted_fresh[:15]:
        print(f"{n:>6} {data['opportunities']:>15} {data['appeared']:>12} {data['rate']:>7.1%}")

    # =========================================================================
    # 5. BACKTEST DER STRATEGIE
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. BACKTEST: Dynamisches Ticket nach jedem Jackpot")
    print("=" * 80)

    results = backtest_strategy(df, jackpot_df, persistence_data, pair_persistence, fresh_success)

    print(f"\n{'Nach JP':>12} {'Naechster JP':>12} {'Hits':>6} {'Gewinn':>8} {'Ticket'}")
    print("-" * 80)

    total_wins = 0
    total_cost = len(results)
    hit_distribution = Counter()

    for r in results:
        total_wins += r["win"]
        hit_distribution[r["hits"]] += 1
        print(f"{r['jp1_date'].strftime('%d.%m.%Y'):>12} {r['jp2_date'].strftime('%d.%m.%Y'):>12} "
              f"{r['hits']:>6} {r['win']:>7} EUR {r['ticket']}")

    # =========================================================================
    # 6. ERGEBNIS-ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. ERGEBNIS-ZUSAMMENFASSUNG")
    print("=" * 80)

    netto = total_wins - total_cost
    roi = (netto / total_cost * 100) if total_cost > 0 else 0

    print(f"""
BACKTEST ERGEBNIS (Jackpot-zu-Jackpot):
  Anzahl Transitionen:  {len(results)}
  Einsatz (1 EUR/JP):   {total_cost} EUR
  Gewinn:               {total_wins} EUR
  NETTO:                {netto:+} EUR
  ROI:                  {roi:+.1f}%

TREFFER-VERTEILUNG:
""")
    for hits in range(10):
        count = hit_distribution.get(hits, 0)
        pct = count / len(results) * 100 if results else 0
        win_per = get_fixed_quote(9, hits)
        bar = "#" * int(pct / 2)
        print(f"  {hits} Treffer: {count:>3}x ({pct:>5.1f}%) {win_per:>6} EUR  {bar}")

    # =========================================================================
    # 7. EMPFEHLUNG FUER NAECHSTES TICKET
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. EMPFEHLUNG: Ticket nach dem LETZTEN Jackpot")
    print("=" * 80)

    last_jackpot = jackpot_df.sort_values("Datum").iloc[-1]

    print(f"\nLetzter Jackpot: {last_jackpot['Datum'].strftime('%d.%m.%Y')}")
    print(f"Zahlen: {sorted(last_jackpot['numbers_set'])}")

    recommended_ticket = generate_post_jackpot_ticket(
        last_jackpot["numbers_set"],
        persistence_data,
        pair_persistence,
        fresh_success,
        ticket_size=9
    )

    # Zeige Aufschuesselung
    persistent_in_ticket = [n for n in recommended_ticket if n in last_jackpot["numbers_set"]]
    fresh_in_ticket = [n for n in recommended_ticket if n not in last_jackpot["numbers_set"]]

    print(f"""
EMPFOHLENES TICKET (Typ 9):

  {recommended_ticket}

AUFSCHLUESSELUNG:
  Aus letztem JP (persistent): {persistent_in_ticket}
  Frische Zahlen:              {fresh_in_ticket}

LOGIK:
  - {len(persistent_in_ticket)} Zahlen aus dem letzten Jackpot mit hoher Wiederkehr-Rate
  - {len(fresh_in_ticket)} frische Zahlen mit hoher Erfolgsrate wenn sie "neu" sind
  - Paare mit historisch starker Persistenz wurden beruecksichtigt
""")

    # Speichere Empfehlung
    output = {
        "generated_after_jackpot": last_jackpot["Datum"].strftime("%Y-%m-%d"),
        "jackpot_numbers": sorted(last_jackpot["numbers_set"]),
        "recommended_ticket": recommended_ticket,
        "persistent_numbers": persistent_in_ticket,
        "fresh_numbers": fresh_in_ticket,
        "backtest_results": {
            "transitions": len(results),
            "total_wins": total_wins,
            "roi_percent": roi,
            "avg_hits": np.mean([r["hits"] for r in results])
        }
    }

    output_path = base_path / "results" / "jackpot_follower_ticket.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Empfehlung gespeichert: {output_path}")


if __name__ == "__main__":
    main()
