#!/usr/bin/env python3
"""
SPLIT-TEST: Jackpot Follower mit Train/Test Split

Da wir nur 2025 Jackpot-Daten haben (17 Jackpots), teilen wir:
- TRAINING: Jackpots 1-8 (Januar-Mai 2025) → Lerne Muster
- TEST:     Jackpots 9-17 (Juni-Dezember 2025) → Teste Vorhersagen

Dies ist der ehrlichste Test den wir mit den verfuegbaren Daten machen koennen.

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
TRAIN_JACKPOTS = 8  # Erste 8 Jackpots zum Training


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpot_dates(base_path):
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


def calculate_rates_from_transitions(transitions):
    """Berechne Persistenz-Raten aus Transitionen."""
    if len(transitions) < 2:
        return None, None, None

    persistence = defaultdict(lambda: {"appeared": 0, "persisted": 0})
    pair_persist = defaultdict(lambda: {"in_first": 0, "in_both": 0})
    fresh_success = defaultdict(lambda: {"opportunities": 0, "appeared": 0})

    for t in transitions:
        # Zahlen-Persistenz
        for n in t["numbers1"]:
            persistence[n]["appeared"] += 1
            if n in t["numbers2"]:
                persistence[n]["persisted"] += 1

        # Paar-Persistenz
        pairs1 = set(combinations(sorted(t["numbers1"]), 2))
        pairs2 = set(combinations(sorted(t["numbers2"]), 2))
        for pair in pairs1:
            pair_persist[pair]["in_first"] += 1
            if pair in pairs2:
                pair_persist[pair]["in_both"] += 1

        # Frische Zahlen
        fresh = set(range(1, 71)) - t["numbers1"]
        for n in fresh:
            fresh_success[n]["opportunities"] += 1
            if n in t["numbers2"]:
                fresh_success[n]["appeared"] += 1

    # Konvertiere zu Rates
    pers_rates = {n: d["persisted"] / d["appeared"]
                  for n, d in persistence.items() if d["appeared"] > 0}

    pair_rates = {p: d["in_both"] / d["in_first"]
                  for p, d in pair_persist.items() if d["in_first"] >= 2}

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

    # 2. Frische Zahlen mit Paar-Bonus
    pair_bonus = defaultdict(float)
    for pair, rate in pair_rates.items():
        if rate > 0.3:
            n1, n2 = pair
            if n1 in persistent_picks:
                pair_bonus[n2] += rate
            if n2 in persistent_picks:
                pair_bonus[n1] += rate

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
    print("SPLIT-TEST: Jackpot Follower (Train/Test)")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpot_dates(base_path)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)

    print(f"\nGesamte Jackpots: {len(jackpot_dates)}")
    print(f"Training: Erste {TRAIN_JACKPOTS} Jackpots")
    print(f"Test: Letzte {len(jackpot_dates) - TRAIN_JACKPOTS} Jackpots")

    # Split
    train_jackpots = jackpot_dates[:TRAIN_JACKPOTS]
    test_jackpots = jackpot_dates[TRAIN_JACKPOTS:]

    print(f"\nTraining-Periode: {train_jackpots[0].strftime('%d.%m.%Y')} - {train_jackpots[-1].strftime('%d.%m.%Y')}")
    print(f"Test-Periode: {test_jackpots[0].strftime('%d.%m.%Y')} - {test_jackpots[-1].strftime('%d.%m.%Y')}")

    # =========================================================================
    # TRAINING: Lerne Muster aus ersten 8 Jackpots
    # =========================================================================
    print("\n" + "=" * 80)
    print("TRAINING PHASE")
    print("=" * 80)

    train_transitions = analyze_transitions(df, train_jackpots)
    pers_rates, pair_rates, fresh_rates = calculate_rates_from_transitions(train_transitions)

    print(f"\nGelernte Transitionen: {len(train_transitions)}")

    # Zeige Top persistente Zahlen
    if pers_rates:
        top_persistent = sorted(pers_rates.items(), key=lambda x: -x[1])[:10]
        print(f"\nTop 10 persistente Zahlen (aus Training):")
        for n, rate in top_persistent:
            print(f"  {n:>3}: {rate:.1%}")

    # Zeige Top persistente Paare
    if pair_rates:
        top_pairs = sorted(pair_rates.items(), key=lambda x: -x[1])[:5]
        print(f"\nTop 5 persistente Paare (aus Training):")
        for pair, rate in top_pairs:
            print(f"  {pair}: {rate:.1%}")

    # =========================================================================
    # TEST: Wende gelernte Muster an
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST PHASE")
    print("=" * 80)

    all_results = []
    period_results = []

    # Der letzte Training-Jackpot ist der Startpunkt fuer den Test
    start_jp = train_jackpots[-1]
    start_jp_row = df[df["Datum"] == start_jp]
    current_jp_numbers = start_jp_row.iloc[0]["numbers_set"]

    print(f"\n{'Nach JP':>12} {'Ticket':>50} {'Zieh':>6} {'Hits':>6} {'Netto':>10}")
    print("-" * 95)

    for i, test_jp in enumerate(test_jackpots):
        # Generiere Ticket basierend auf aktuellem JP und TRAINING-Mustern
        ticket = generate_ticket(current_jp_numbers, pers_rates, pair_rates, fresh_rates)

        # Finde alle Ziehungen zwischen aktuellem und naechstem JP
        if i == 0:
            period_start = start_jp
        else:
            period_start = test_jackpots[i - 1]

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
        avg_hits = np.mean(period_hits) if period_hits else 0
        max_hits = max(period_hits) if period_hits else 0

        period_results.append({
            "period": i + 1,
            "jp_date": test_jp,
            "ticket": ticket,
            "n_draws": len(period_df),
            "netto": period_netto,
            "avg_hits": avg_hits,
            "max_hits": max_hits
        })

        print(f"{period_start.strftime('%d.%m.%Y'):>12} {str(ticket):>50} {len(period_df):>6} "
              f"{avg_hits:>5.2f} {period_netto:>+9} EUR")

        # Update: Der aktuelle Test-JP wird zum neuen "letzten JP"
        current_jp_row = df[df["Datum"] == test_jp]
        if len(current_jp_row) > 0:
            current_jp_numbers = current_jp_row.iloc[0]["numbers_set"]

    # =========================================================================
    # ERGEBNIS-ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("TEST-ERGEBNIS")
    print("=" * 80)

    total_draws = len(all_results)
    total_cost = total_draws * EINSATZ
    total_win = sum(r["win"] for r in all_results)
    total_netto = total_win - total_cost
    total_roi = (total_netto / total_cost * 100) if total_cost > 0 else 0

    all_hits = [r["hits"] for r in all_results]
    hit_dist = Counter(all_hits)

    print(f"""
TEST-PERIODE: {test_jackpots[0].strftime('%d.%m.%Y')} - {test_jackpots[-1].strftime('%d.%m.%Y')}

ERGEBNIS:
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
        bar = "#" * int(pct / 2)
        win = get_fixed_quote(KENO_TYPE, hits)
        print(f"  {hits} Treffer: {count:>3}x ({pct:>5.1f}%) {win:>6} EUR  {bar}")

    # Jackpot-Tage Performance
    jp_results = [r for r in all_results if r["is_jackpot"]]
    if jp_results:
        jp_avg = np.mean([r["hits"] for r in jp_results])
        jp_max = max([r["hits"] for r in jp_results])
        jp_wins = sum(r["win"] for r in jp_results)

        print(f"\nJACKPOT-TAGE PERFORMANCE:")
        print(f"  Anzahl:    {len(jp_results)}")
        print(f"  Avg Hits:  {jp_avg:.2f}")
        print(f"  Max Hits:  {jp_max}")
        print(f"  Gewinn:    {jp_wins} EUR")

        print(f"\n  {'Datum':>12} {'Hits':>6} {'Gewinn':>8}")
        print("  " + "-" * 30)
        for r in jp_results:
            print(f"  {r['date'].strftime('%d.%m.%Y'):>12} {r['hits']:>6} {r['win']:>7} EUR")

    # High-Win Events
    high_wins = [r for r in all_results if r["hits"] >= 6]
    if high_wins:
        print(f"\nHIGH-WIN EVENTS (6+ Treffer): {len(high_wins)}")
        for r in high_wins:
            print(f"  {r['date'].strftime('%d.%m.%Y')}: {r['hits']} Treffer = {r['win']} EUR")

    # =========================================================================
    # VERGLEICH MIT RANDOM BASELINE
    # =========================================================================
    print("\n" + "=" * 80)
    print("VERGLEICH MIT BASELINE")
    print("=" * 80)

    # Theoretische Erwartung bei zufaelligem Ticket
    # E[hits] fuer 9 aus 70 bei 20 gezogenen = 9 * 20/70 = 2.57
    expected_hits = 9 * 20 / 70
    print(f"\nTheoretische Erwartung (Zufall):")
    print(f"  E[Hits] = 9 * 20/70 = {expected_hits:.2f}")
    print(f"  Unsere Avg Hits: {np.mean(all_hits):.2f}")
    print(f"  Differenz: {np.mean(all_hits) - expected_hits:+.2f}")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT")
    print("=" * 80)

    print(f"""
SPLIT-TEST ERGEBNIS:

Training: {len(train_transitions)} Jackpot-Transitionen (JP 1-8)
Test:     {len(test_jackpots)} Jackpot-Perioden (JP 9-17)

PERFORMANCE:
  ROI:           {total_roi:+.1f}%
  Netto:         {total_netto:+} EUR
  Avg Hits:      {np.mean(all_hits):.2f} (vs. {expected_hits:.2f} erwartet)

BEWERTUNG:
  {'✓ BESSER als Zufall' if np.mean(all_hits) > expected_hits else '✗ NICHT besser als Zufall'}
  {'✓ PROFITABEL' if total_netto > 0 else '✗ VERLUST'}

WICHTIG:
  - Dieser Test verwendet NUR Training-Daten fuer die Muster
  - Die Test-Periode war dem Algorithmus UNBEKANNT
  - Dies ist ein realistischer Out-of-Sample Test
""")

    # Speichere Ergebnisse
    output = {
        "test_type": "split_test",
        "train_jackpots": TRAIN_JACKPOTS,
        "test_jackpots": len(test_jackpots),
        "total_draws": total_draws,
        "total_netto": total_netto,
        "total_roi": total_roi,
        "avg_hits": float(np.mean(all_hits)),
        "expected_hits": expected_hits,
        "hit_distribution": dict(hit_dist),
        "periods": [
            {
                "jp_date": p["jp_date"].strftime("%Y-%m-%d"),
                "ticket": p["ticket"],
                "n_draws": p["n_draws"],
                "netto": p["netto"],
                "max_hits": p["max_hits"]
            }
            for p in period_results
        ]
    }

    output_path = base_path / "results" / "jackpot_follower_split_test.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
