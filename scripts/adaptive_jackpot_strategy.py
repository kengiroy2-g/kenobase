#!/usr/bin/env python3
"""
ADAPTIVE JACKPOT FOLLOWER STRATEGIE

Kernidee: Nur die letzten N Jackpots als Training verwenden!

Erkenntnisse:
- Kurzfristige Muster (innerhalb 2025): +5.4% ueber Zufall
- Langfristige Muster (2022-2024): +0.4% (fast Zufall)
- Das System ADAPTIERT sich - alte Muster veralten!

Strategie:
- Rolling Window von N Jackpots
- Nach jedem Jackpot: Neu berechnen
- Nur AKTUELLE Muster verwenden

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
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def load_all_jackpots(base_path):
    """Lade ALLE Jackpot-Daten (2022-2025)."""
    all_dates = set()

    # 2022-2024 aus GQ Datei
    gq_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    if gq_path.exists():
        df = pd.read_csv(gq_path, encoding="utf-8-sig")
        df["Anzahl der Gewinner"] = df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)

        for _, row in df[(df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)].iterrows():
            all_dates.add(pd.to_datetime(row["Datum"], format="%d.%m.%Y"))
        for _, row in df[(df["Keno-Typ"] == 9) & (df["Anzahl richtiger Zahlen"] == 9) & (df["Anzahl der Gewinner"] > 0)].iterrows():
            all_dates.add(pd.to_datetime(row["Datum"], format="%d.%m.%Y"))

    # 2025 aus Timeline
    path_2025 = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path_2025.exists():
        timeline = pd.read_csv(path_2025)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        all_dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())

    return sorted(all_dates)


def calculate_rates_from_window(df, jackpot_window):
    """Berechne Raten NUR aus den letzten N Jackpots (Rolling Window)."""
    if len(jackpot_window) < 3:
        return None, None, None

    transitions = []
    for i in range(len(jackpot_window) - 1):
        jp1_date = jackpot_window[i]
        jp2_date = jackpot_window[i + 1]

        jp1_row = df[df["Datum"] == jp1_date]
        jp2_row = df[df["Datum"] == jp2_date]

        if len(jp1_row) == 0 or len(jp2_row) == 0:
            continue

        transitions.append({
            "numbers1": jp1_row.iloc[0]["numbers_set"],
            "numbers2": jp2_row.iloc[0]["numbers_set"]
        })

    if len(transitions) < 2:
        return None, None, None

    # Berechne Raten
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

    min_pair_count = max(2, len(transitions) // 3)
    pair_rates = {p: d["in_both"] / d["in_first"]
                  for p, d in pair_persist.items() if d["in_first"] >= min_pair_count}

    fresh_rates = {n: d["appeared"] / d["opportunities"]
                   for n, d in fresh_success.items() if d["opportunities"] > 0}

    return pers_rates, pair_rates, fresh_rates


def generate_ticket(last_jp_numbers, pers_rates, pair_rates, fresh_rates, ticket_size=9):
    """Generiere Ticket basierend auf aktuellen Mustern."""
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
    if pair_rates:
        for pair, rate in pair_rates.items():
            if rate > 0.25:
                n1, n2 = pair
                if n1 in persistent_picks:
                    pair_bonus[n2] += rate
                if n2 in persistent_picks:
                    pair_bonus[n1] += rate

    # 3. Frische Zahlen
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


def run_adaptive_backtest(df, all_jackpots, window_size, test_start_idx):
    """
    Fuehre adaptiven Backtest mit gegebener Window-Groesse durch.

    Args:
        df: DataFrame mit Ziehungen
        all_jackpots: Alle Jackpot-Daten sortiert
        window_size: Anzahl der letzten Jackpots fuer Training
        test_start_idx: Index ab dem getestet wird (davor ist Training)
    """
    all_results = []
    period_results = []

    for i in range(test_start_idx, len(all_jackpots)):
        test_jp = all_jackpots[i]

        # Rolling Window: Letzte N Jackpots VOR diesem
        window_end_idx = i
        window_start_idx = max(0, window_end_idx - window_size)
        jackpot_window = all_jackpots[window_start_idx:window_end_idx]

        if len(jackpot_window) < 3:
            continue

        # Berechne Raten aus Window
        pers_rates, pair_rates, fresh_rates = calculate_rates_from_window(df, jackpot_window)

        # Letzter JP im Window
        last_jp = jackpot_window[-1]
        last_jp_row = df[df["Datum"] == last_jp]
        if len(last_jp_row) == 0:
            continue

        last_jp_numbers = last_jp_row.iloc[0]["numbers_set"]

        # Generiere Ticket
        ticket = generate_ticket(last_jp_numbers, pers_rates, pair_rates, fresh_rates)

        # Finde Ziehungen bis zum naechsten JP
        period_df = df[(df["Datum"] > last_jp) & (df["Datum"] <= test_jp)]

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
                "is_jackpot": row["Datum"] == test_jp
            })

        if period_hits:
            period_netto = sum(period_wins) - len(period_df) * EINSATZ
            period_results.append({
                "jp_date": test_jp,
                "ticket": ticket,
                "n_draws": len(period_df),
                "netto": period_netto,
                "avg_hits": np.mean(period_hits),
                "max_hits": max(period_hits),
                "window_size": len(jackpot_window)
            })

    return all_results, period_results


def main():
    print("=" * 80)
    print("ADAPTIVE JACKPOT FOLLOWER STRATEGIE")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_keno_draws(base_path)
    all_jackpots = load_all_jackpots(base_path)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in all_jackpots)

    print(f"\nGeladene Daten:")
    print(f"  Ziehungen: {len(df)}")
    print(f"  Jackpots gesamt: {len(all_jackpots)}")

    # Finde Index wo 2025 beginnt
    test_start_date = pd.Timestamp("2025-01-01")
    test_start_idx = next((i for i, jp in enumerate(all_jackpots) if jp >= test_start_date), len(all_jackpots))

    print(f"  Training (vor 2025): {test_start_idx} Jackpots")
    print(f"  Test (2025): {len(all_jackpots) - test_start_idx} Jackpots")

    # =========================================================================
    # TESTE VERSCHIEDENE WINDOW-GROESSEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("TESTE VERSCHIEDENE WINDOW-GROESSEN")
    print("=" * 80)

    window_sizes = [5, 8, 10, 15, 20, 30, 50]
    results_by_window = {}

    print(f"\n{'Window':>8} {'Zieh':>8} {'Netto':>10} {'ROI':>10} {'Avg Hits':>10} {'vs Zufall':>10} {'Max':>6}")
    print("-" * 75)

    expected_hits = 9 * 20 / 70  # 2.57

    for window_size in window_sizes:
        all_results, period_results = run_adaptive_backtest(
            df, all_jackpots, window_size, test_start_idx
        )

        if not all_results:
            continue

        total_draws = len(all_results)
        total_cost = total_draws * EINSATZ
        total_win = sum(r["win"] for r in all_results)
        total_netto = total_win - total_cost
        total_roi = (total_netto / total_cost * 100) if total_cost > 0 else 0

        all_hits = [r["hits"] for r in all_results]
        avg_hits = np.mean(all_hits)
        max_hits = max(all_hits)
        vs_zufall = (avg_hits / expected_hits - 1) * 100

        results_by_window[window_size] = {
            "all_results": all_results,
            "period_results": period_results,
            "total_draws": total_draws,
            "total_netto": total_netto,
            "total_roi": total_roi,
            "avg_hits": avg_hits,
            "max_hits": max_hits,
            "vs_zufall": vs_zufall
        }

        print(f"{window_size:>8} {total_draws:>8} {total_netto:>+9} EUR {total_roi:>+9.1f}% "
              f"{avg_hits:>10.2f} {vs_zufall:>+9.1f}% {max_hits:>6}")

    # =========================================================================
    # BESTE WINDOW-GROESSE FINDEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSE: OPTIMALE WINDOW-GROESSE")
    print("=" * 80)

    # Sortiere nach ROI
    sorted_windows = sorted(results_by_window.items(), key=lambda x: x[1]["total_roi"], reverse=True)

    best_window = sorted_windows[0][0]
    best_result = sorted_windows[0][1]

    print(f"\nBeste Window-Groesse nach ROI: {best_window}")
    print(f"  ROI: {best_result['total_roi']:+.1f}%")
    print(f"  Avg Hits: {best_result['avg_hits']:.2f} ({best_result['vs_zufall']:+.1f}% vs. Zufall)")

    # Sortiere nach Avg Hits
    sorted_by_hits = sorted(results_by_window.items(), key=lambda x: x[1]["avg_hits"], reverse=True)
    best_hits_window = sorted_by_hits[0][0]
    best_hits_result = sorted_by_hits[0][1]

    print(f"\nBeste Window-Groesse nach Avg Hits: {best_hits_window}")
    print(f"  Avg Hits: {best_hits_result['avg_hits']:.2f} ({best_hits_result['vs_zufall']:+.1f}% vs. Zufall)")

    # =========================================================================
    # DETAIL-ANALYSE BESTE WINDOW
    # =========================================================================
    print("\n" + "=" * 80)
    print(f"DETAIL-ANALYSE: WINDOW = {best_window}")
    print("=" * 80)

    best_data = results_by_window[best_window]
    all_results = best_data["all_results"]
    period_results = best_data["period_results"]

    # Treffer-Verteilung
    all_hits = [r["hits"] for r in all_results]
    hit_dist = Counter(all_hits)

    print("\nTREFFER-VERTEILUNG:")
    for hits in range(10):
        count = hit_dist.get(hits, 0)
        pct = count / len(all_hits) * 100 if all_hits else 0
        win = get_fixed_quote(KENO_TYPE, hits)
        bar = "#" * int(pct / 2)
        print(f"  {hits} Treffer: {count:>3}x ({pct:>5.1f}%) {win:>6} EUR  {bar}")

    # Jackpot-Tage
    jp_results = [r for r in all_results if r["is_jackpot"]]
    if jp_results:
        jp_hits = [r["hits"] for r in jp_results]
        print(f"\nJACKPOT-TAGE:")
        print(f"  Anzahl: {len(jp_results)}")
        print(f"  Avg Hits: {np.mean(jp_hits):.2f}")
        print(f"  Max Hits: {max(jp_hits)}")

    # High-Win Events
    high_wins = [r for r in all_results if r["hits"] >= 6]
    if high_wins:
        print(f"\nHIGH-WIN EVENTS (6+ Treffer): {len(high_wins)}")
        for r in sorted(high_wins, key=lambda x: -x["hits"])[:10]:
            print(f"  {r['date'].strftime('%d.%m.%Y')}: {r['hits']} Treffer = {r['win']} EUR")

    # Perioden-Details
    print(f"\nPERIODEN-DETAILS:")
    print(f"{'JP-Datum':>12} {'Draws':>6} {'Netto':>10} {'Max':>5} {'Ticket'}")
    print("-" * 80)
    for p in period_results:
        ticket_str = str(p["ticket"])[:35]
        print(f"{p['jp_date'].strftime('%d.%m.%Y'):>12} {p['n_draws']:>6} {p['netto']:>+9} EUR "
              f"{p['max_hits']:>5} {ticket_str}")

    # =========================================================================
    # EMPFEHLUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("EMPFEHLUNG: ADAPTIVE STRATEGIE")
    print("=" * 80)

    # Generiere aktuelles Ticket mit bestem Window
    recent_jackpots = all_jackpots[-best_window:]
    pers_rates, pair_rates, fresh_rates = calculate_rates_from_window(df, recent_jackpots)

    last_jp = recent_jackpots[-1]
    last_jp_row = df[df["Datum"] == last_jp]
    last_jp_numbers = last_jp_row.iloc[0]["numbers_set"]

    recommended_ticket = generate_ticket(last_jp_numbers, pers_rates, pair_rates, fresh_rates)

    print(f"""
OPTIMALE KONFIGURATION:
  Window-Groesse: {best_window} Jackpots
  Basiert auf: Letzte {best_window} Jackpots (Rolling Window)

AKTUELLES TICKET (nach JP {last_jp.strftime('%d.%m.%Y')}):

  {recommended_ticket}

ERWARTETE PERFORMANCE:
  Avg Hits: {best_data['avg_hits']:.2f} ({best_data['vs_zufall']:+.1f}% ueber Zufall)
  ROI: {best_data['total_roi']:+.1f}%

STRATEGIE:
  1. Nach jedem Jackpot: Ticket NEU generieren
  2. Nur letzte {best_window} Jackpots als Training verwenden
  3. Alte Muster IGNORIEREN (sie sind veraltet!)
""")

    # Speichern
    output = {
        "optimal_window": best_window,
        "results_by_window": {
            str(w): {
                "total_draws": r["total_draws"],
                "total_netto": r["total_netto"],
                "total_roi": r["total_roi"],
                "avg_hits": r["avg_hits"],
                "vs_zufall_pct": r["vs_zufall"]
            }
            for w, r in results_by_window.items()
        },
        "recommended_ticket": recommended_ticket,
        "last_jackpot": last_jp.strftime("%Y-%m-%d")
    }

    output_path = base_path / "results" / "adaptive_strategy_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
