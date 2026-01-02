#!/usr/bin/env python3
"""
VOLLSTAENDIGER WALK-FORWARD BACKTEST: 2022-2025

Mit den neuen Jackpot-Daten aus Keno_GQ_2022_2023-2024.csv:
- TRAINING: 2022-2024 Jackpots (56 Jackpot-Tage)
- TEST: 2025 (17 Jackpots)

Dies ist ein ECHTER Out-of-Sample Test!

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


KENO_TYPE = 9
EINSATZ = 1


def load_keno_draws(base_path):
    """Lade alle KENO Ziehungen."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates_2022_2024(base_path):
    """Lade Jackpot-Daten aus 2022-2024."""
    gq_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    df = pd.read_csv(gq_path, encoding="utf-8-sig")

    # Konvertiere Gewinner-Anzahl
    df["Anzahl der Gewinner"] = df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)

    # Finde Jackpots (Typ 10 mit 10/10 ODER Typ 9 mit 9/9)
    jackpots_10 = df[(df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)]
    jackpots_9 = df[(df["Keno-Typ"] == 9) & (df["Anzahl richtiger Zahlen"] == 9) & (df["Anzahl der Gewinner"] > 0)]

    all_dates = set()
    for _, row in jackpots_10.iterrows():
        all_dates.add(pd.to_datetime(row["Datum"], format="%d.%m.%Y"))
    for _, row in jackpots_9.iterrows():
        all_dates.add(pd.to_datetime(row["Datum"], format="%d.%m.%Y"))

    return sorted(all_dates)


def load_jackpot_dates_2025(base_path):
    """Lade Jackpot-Daten aus 2025."""
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        return sorted(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return []


def analyze_transitions(df, jackpot_dates):
    """Analysiere Jackpot-Uebergaenge."""
    transitions = []

    for i in range(len(jackpot_dates) - 1):
        jp1_date = jackpot_dates[i]
        jp2_date = jackpot_dates[i + 1]

        jp1_row = df[df["Datum"] == jp1_date]
        jp2_row = df[df["Datum"] == jp2_date]

        if len(jp1_row) == 0 or len(jp2_row) == 0:
            continue

        set1 = jp1_row.iloc[0]["numbers_set"]
        set2 = jp2_row.iloc[0]["numbers_set"]

        transitions.append({
            "date1": jp1_date,
            "date2": jp2_date,
            "numbers1": set1,
            "numbers2": set2
        })

    return transitions


def calculate_rates(transitions):
    """Berechne Persistenz-Raten aus Transitionen."""
    if len(transitions) < 3:
        return None, None, None

    persistence = defaultdict(lambda: {"appeared": 0, "persisted": 0})
    pair_persist = defaultdict(lambda: {"in_first": 0, "in_both": 0})
    fresh_success = defaultdict(lambda: {"opportunities": 0, "appeared": 0})

    for t in transitions:
        for n in t["numbers1"]:
            persistence[n]["appeared"] += 1
            if n in t["numbers2"]:
                persistence[n]["persisted"] += 1

        pairs1 = set(combinations(sorted(t["numbers1"]), 2))
        pairs2 = set(combinations(sorted(t["numbers2"]), 2))
        for pair in pairs1:
            pair_persist[pair]["in_first"] += 1
            if pair in pairs2:
                pair_persist[pair]["in_both"] += 1

        fresh = set(range(1, 71)) - t["numbers1"]
        for n in fresh:
            fresh_success[n]["opportunities"] += 1
            if n in t["numbers2"]:
                fresh_success[n]["appeared"] += 1

    pers_rates = {n: d["persisted"] / d["appeared"]
                  for n, d in persistence.items() if d["appeared"] > 0}

    pair_rates = {p: d["in_both"] / d["in_first"]
                  for p, d in pair_persist.items() if d["in_first"] >= 3}

    fresh_rates = {n: d["appeared"] / d["opportunities"]
                   for n, d in fresh_success.items() if d["opportunities"] > 0}

    return pers_rates, pair_rates, fresh_rates


def generate_ticket(last_jp_numbers, pers_rates, pair_rates, fresh_rates, ticket_size=9):
    """Generiere Ticket basierend auf gelernten Mustern."""
    if pers_rates is None:
        import random
        return sorted(random.sample(range(1, 71), ticket_size))

    last_jp_set = set(last_jp_numbers)

    # 1. Persistente Zahlen (Top 4)
    persistent_candidates = [(n, pers_rates.get(n, 0)) for n in last_jp_set]
    persistent_candidates.sort(key=lambda x: -x[1])
    persistent_picks = [n for n, _ in persistent_candidates[:4]]

    # 2. Paar-Bonus
    pair_bonus = defaultdict(float)
    for pair, rate in pair_rates.items():
        if rate > 0.2:
            n1, n2 = pair
            if n1 in persistent_picks:
                pair_bonus[n2] += rate
            if n2 in persistent_picks:
                pair_bonus[n1] += rate

    # 3. Frische Zahlen mit Bonus
    fresh_candidates = [(n, fresh_rates.get(n, 0) + pair_bonus.get(n, 0))
                        for n in range(1, 71) if n not in last_jp_set]
    fresh_candidates.sort(key=lambda x: -x[1])

    # Baue Ticket
    ticket = set(persistent_picks)
    for n, _ in fresh_candidates:
        if len(ticket) >= ticket_size:
            break
        if n not in ticket:
            ticket.add(n)

    return sorted(ticket)[:ticket_size]


def simulate_ticket(ticket, draw_set):
    hits = len(set(ticket) & draw_set)
    return hits, get_fixed_quote(KENO_TYPE, hits)


def main():
    print("=" * 80)
    print("VOLLSTAENDIGER WALK-FORWARD BACKTEST: 2022-2025")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_keno_draws(base_path)

    # Lade Jackpot-Daten
    jackpots_2022_2024 = load_jackpot_dates_2022_2024(base_path)
    jackpots_2025 = load_jackpot_dates_2025(base_path)

    print(f"\nGeladene Daten:")
    print(f"  KENO Ziehungen: {len(df)}")
    print(f"  Jackpots 2022-2024: {len(jackpots_2022_2024)}")
    print(f"  Jackpots 2025: {len(jackpots_2025)}")

    # =========================================================================
    # TRAINING auf 2022-2024
    # =========================================================================
    print("\n" + "=" * 80)
    print("TRAINING PHASE (2022-2024)")
    print("=" * 80)

    # Filter DF auf 2022-2024
    df_train = df[df["Datum"].dt.year < 2025].copy()

    train_transitions = analyze_transitions(df_train, jackpots_2022_2024)
    pers_rates, pair_rates, fresh_rates = calculate_rates(train_transitions)

    print(f"\nTraining-Daten:")
    print(f"  Ziehungen: {len(df_train)}")
    print(f"  Jackpot-Transitionen: {len(train_transitions)}")

    # Top persistente Zahlen
    if pers_rates:
        top_persistent = sorted(pers_rates.items(), key=lambda x: -x[1])[:15]
        print(f"\nTop 15 persistente Zahlen (2022-2024):")
        for n, rate in top_persistent:
            print(f"  {n:>3}: {rate:.1%}")

    # Top Paare
    if pair_rates:
        top_pairs = sorted(pair_rates.items(), key=lambda x: -x[1])[:10]
        print(f"\nTop 10 persistente Paare (2022-2024):")
        for pair, rate in top_pairs:
            print(f"  {pair}: {rate:.1%}")

    # =========================================================================
    # TEST auf 2025
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST PHASE (2025) - Out-of-Sample!")
    print("=" * 80)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpots_2025)

    all_results = []
    period_results = []

    # Startpunkt: Letzter JP aus 2024
    last_training_jp = jackpots_2022_2024[-1]
    last_jp_row = df[df["Datum"] == last_training_jp]

    if len(last_jp_row) == 0:
        print(f"WARNUNG: Letzter Training-JP {last_training_jp} nicht in Ziehungsdaten!")
        return

    current_jp_numbers = last_jp_row.iloc[0]["numbers_set"]

    print(f"\nLetzter Training-JP: {last_training_jp.strftime('%d.%m.%Y')}")
    print(f"Test-Start: {jackpots_2025[0].strftime('%d.%m.%Y')}")

    print(f"\n{'Periode':>3} {'Nach JP':>12} {'Ticket':>45} {'Zieh':>6} {'Netto':>10} {'Max':>4}")
    print("-" * 90)

    for i, test_jp in enumerate(jackpots_2025):
        # Generiere Ticket basierend auf TRAINING-Mustern
        ticket = generate_ticket(current_jp_numbers, pers_rates, pair_rates, fresh_rates)

        # Finde Ziehungen bis zum Test-JP
        if i == 0:
            period_start = last_training_jp
        else:
            period_start = jackpots_2025[i - 1]

        period_df = df[(df["Datum"] > period_start) & (df["Datum"] <= test_jp)]

        period_hits = []
        period_wins = []

        for _, row in period_df.iterrows():
            hits, win = simulate_ticket(ticket, row["numbers_set"])
            period_hits.append(hits)
            period_wins.append(win)

            all_results.append({
                "date": row["Datum"],
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "is_jackpot": row["is_jackpot"]
            })

        period_netto = sum(period_wins) - len(period_df) * EINSATZ
        max_hits = max(period_hits) if period_hits else 0

        period_results.append({
            "period": i + 1,
            "jp_date": test_jp,
            "ticket": ticket,
            "n_draws": len(period_df),
            "netto": period_netto,
            "max_hits": max_hits
        })

        ticket_str = str(ticket)[:40]
        print(f"{i+1:>3} {period_start.strftime('%d.%m.%Y'):>12} {ticket_str:>45} {len(period_df):>6} "
              f"{period_netto:>+9} EUR {max_hits:>4}")

        # Update fuer naechste Periode
        current_jp_row = df[df["Datum"] == test_jp]
        if len(current_jp_row) > 0:
            current_jp_numbers = current_jp_row.iloc[0]["numbers_set"]

    # =========================================================================
    # ERGEBNISSE
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST-ERGEBNISSE 2025")
    print("=" * 80)

    total_draws = len(all_results)
    total_cost = total_draws * EINSATZ
    total_win = sum(r["win"] for r in all_results)
    total_netto = total_win - total_cost
    total_roi = (total_netto / total_cost * 100) if total_cost > 0 else 0

    all_hits = [r["hits"] for r in all_results]
    hit_dist = Counter(all_hits)

    print(f"""
GESAMT-ERGEBNIS:
  Ziehungen:     {total_draws}
  Einsatz:       {total_cost} EUR
  Gewinn:        {total_win} EUR
  NETTO:         {total_netto:+} EUR
  ROI:           {total_roi:+.1f}%

STATISTIK:
  Avg Hits:      {np.mean(all_hits):.2f}
  Max Hits:      {max(all_hits)}
""")

    # Treffer-Verteilung
    print("TREFFER-VERTEILUNG:")
    for hits in range(10):
        count = hit_dist.get(hits, 0)
        pct = count / total_draws * 100 if total_draws > 0 else 0
        win = get_fixed_quote(KENO_TYPE, hits)
        bar = "#" * int(pct / 2)
        print(f"  {hits} Treffer: {count:>3}x ({pct:>5.1f}%) {win:>6} EUR  {bar}")

    # Jackpot-Tage
    jp_results = [r for r in all_results if r["is_jackpot"]]
    if jp_results:
        jp_avg = np.mean([r["hits"] for r in jp_results])
        print(f"\nJACKPOT-TAGE PERFORMANCE:")
        print(f"  Anzahl: {len(jp_results)}")
        print(f"  Avg Hits: {jp_avg:.2f}")
        print(f"  Max Hits: {max(r['hits'] for r in jp_results)}")

        print(f"\n  {'Datum':>12} {'Hits':>6} {'Gewinn':>8}")
        print("  " + "-" * 30)
        for r in jp_results:
            print(f"  {r['date'].strftime('%d.%m.%Y'):>12} {r['hits']:>6} {r['win']:>7} EUR")

    # High-Win Events
    high_wins = [r for r in all_results if r["hits"] >= 6]
    if high_wins:
        print(f"\nHIGH-WIN EVENTS (6+ Treffer): {len(high_wins)}")
        for r in sorted(high_wins, key=lambda x: -x["hits"]):
            print(f"  {r['date'].strftime('%d.%m.%Y')}: {r['hits']} Treffer = {r['win']} EUR")

    # =========================================================================
    # VERGLEICH
    # =========================================================================
    print("\n" + "=" * 80)
    print("VERGLEICH MIT BASELINE")
    print("=" * 80)

    expected_hits = 9 * 20 / 70  # 2.57
    print(f"\nTheoretische Erwartung (Zufall): {expected_hits:.2f} Hits")
    print(f"Unsere Avg Hits: {np.mean(all_hits):.2f}")
    print(f"Differenz: {np.mean(all_hits) - expected_hits:+.2f} ({(np.mean(all_hits) / expected_hits - 1) * 100:+.1f}%)")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: VOLLSTAENDIGER OUT-OF-SAMPLE TEST")
    print("=" * 80)

    print(f"""
TRAINING (2022-2024):
  - {len(train_transitions)} Jackpot-Transitionen gelernt
  - Persistenz-Muster aus 3 Jahren Daten

TEST (2025 - KOMPLETT OUT-OF-SAMPLE):
  - {len(jackpots_2025)} Jackpot-Perioden getestet
  - ROI: {total_roi:+.1f}%
  - Avg Hits: {np.mean(all_hits):.2f} vs. {expected_hits:.2f} erwartet

BEWERTUNG:
  {'✓ BESSER als Zufall' if np.mean(all_hits) > expected_hits else '✗ NICHT besser als Zufall'}
  {'✓ PROFITABEL' if total_netto > 0 else '✗ VERLUST'}

WICHTIG:
  - Die 2025-Daten waren NICHT Teil des Trainings!
  - Dies ist ein echter Out-of-Sample Test
  - Die Muster wurden NUR aus 2022-2024 gelernt
""")

    # Speichern
    output = {
        "training": {
            "years": "2022-2024",
            "jackpots": len(jackpots_2022_2024),
            "transitions": len(train_transitions)
        },
        "test": {
            "year": "2025",
            "jackpots": len(jackpots_2025),
            "draws": total_draws,
            "netto": total_netto,
            "roi": total_roi,
            "avg_hits": float(np.mean(all_hits)),
            "expected_hits": expected_hits
        },
        "hit_distribution": dict(hit_dist),
        "high_wins": len(high_wins)
    }

    output_path = base_path / "results" / "jackpot_follower_full_backtest_2022_2025.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
