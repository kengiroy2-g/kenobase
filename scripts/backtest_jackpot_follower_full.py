#!/usr/bin/env python3
"""
WALK-FORWARD BACKTEST: Jackpot Follower Strategie (2023-2025)

WICHTIG: Dieser Backtest simuliert das System als ob es die Zukunft NICHT kennt!
- Nach jedem Jackpot wird ein Ticket generiert basierend NUR auf vergangenen Daten
- Das Ticket wird gespielt bis zum naechsten Jackpot
- Alle Ziehungen zwischen Jackpots werden getrackt

Zeitraum: Januar 2023 - Dezember 2025

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kenobase.core.keno_quotes import get_fixed_quote


KENO_TYPE = 9
EINSATZ = 1  # EUR pro Ziehung


def load_all_data(base_path):
    """Lade ALLE Daten ab 2022 (fuer historische Berechnung)."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_all_jackpot_dates(base_path):
    """Lade alle Jackpot-Daten."""
    dates = set()

    # 2025 Jackpots
    path_2025 = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path_2025.exists():
        timeline = pd.read_csv(path_2025)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())

    # Versuche auch 2024 und 2023 Daten zu laden falls vorhanden
    for year in [2024, 2023]:
        path = base_path / "data" / "processed" / "ecosystem" / f"timeline_{year}.csv"
        if path.exists():
            timeline = pd.read_csv(path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())

    return dates


def analyze_historical_transitions(df, jackpot_dates, cutoff_date):
    """
    Analysiere Jackpot-Uebergaenge NUR bis zum cutoff_date.
    Dies simuliert das "Wissen" das zu dem Zeitpunkt verfuegbar war.
    """
    df_hist = df[df["Datum"] < cutoff_date].copy()

    # Finde Jackpots vor dem cutoff
    hist_jackpots = sorted([d for d in jackpot_dates if d < cutoff_date])

    if len(hist_jackpots) < 2:
        return None, None, None

    transitions = []
    for i in range(len(hist_jackpots) - 1):
        jp1_date = hist_jackpots[i]
        jp2_date = hist_jackpots[i + 1]

        jp1_row = df_hist[df_hist["Datum"] == jp1_date]
        jp2_row = df_hist[df_hist["Datum"] == jp2_date]

        if len(jp1_row) == 0 or len(jp2_row) == 0:
            continue

        set1 = jp1_row.iloc[0]["numbers_set"]
        set2 = jp2_row.iloc[0]["numbers_set"]

        transitions.append({
            "numbers1": set1,
            "numbers2": set2
        })

    if len(transitions) < 2:
        return None, None, None

    # Berechne Persistenz-Statistiken
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
    pers_rates = {}
    for n, d in persistence.items():
        if d["appeared"] > 0:
            pers_rates[n] = d["persisted"] / d["appeared"]

    pair_rates = {}
    for p, d in pair_persist.items():
        if d["in_first"] >= 2:
            pair_rates[p] = d["in_both"] / d["in_first"]

    fresh_rates = {}
    for n, d in fresh_success.items():
        if d["opportunities"] > 0:
            fresh_rates[n] = d["appeared"] / d["opportunities"]

    return pers_rates, pair_rates, fresh_rates


def generate_ticket_at_date(last_jp_numbers, pers_rates, pair_rates, fresh_rates, ticket_size=9):
    """
    Generiere ein Ticket basierend auf historischen Daten.
    Verwendet NUR Informationen die zum Zeitpunkt verfuegbar waren.
    """
    if pers_rates is None:
        # Fallback: Zufaellige Auswahl wenn keine Historie
        import random
        return sorted(random.sample(range(1, 71), ticket_size))

    last_jp_set = set(last_jp_numbers)

    # 1. Persistente Zahlen aus letztem Jackpot (Top 4)
    persistent_candidates = [(n, pers_rates.get(n, 0)) for n in last_jp_set]
    persistent_candidates.sort(key=lambda x: -x[1])
    persistent_picks = [n for n, _ in persistent_candidates[:4]]

    # 2. Frische Zahlen mit hoher Erfolgsrate
    fresh_candidates = [(n, fresh_rates.get(n, 0))
                        for n in range(1, 71) if n not in last_jp_set]
    fresh_candidates.sort(key=lambda x: -x[1])

    # 3. Paar-Bonus berechnen
    pair_bonus = defaultdict(float)
    for pair, rate in pair_rates.items():
        if rate > 0.3:
            n1, n2 = pair
            if n1 in persistent_picks:
                pair_bonus[n2] += rate
            if n2 in persistent_picks:
                pair_bonus[n1] += rate

    # Kombiniere fresh mit pair bonus
    fresh_with_bonus = [(n, fresh_rates.get(n, 0) + pair_bonus.get(n, 0))
                        for n, _ in fresh_candidates if n not in persistent_picks]
    fresh_with_bonus.sort(key=lambda x: -x[1])

    # Baue Ticket
    ticket = set(persistent_picks)
    for n, _ in fresh_with_bonus:
        if len(ticket) >= ticket_size:
            break
        ticket.add(n)

    # Fallback falls nicht genug
    if len(ticket) < ticket_size:
        for n, _ in fresh_candidates:
            if n not in ticket:
                ticket.add(n)
            if len(ticket) >= ticket_size:
                break

    return sorted(ticket)[:ticket_size]


def simulate_ticket(ticket, draw_set):
    """Simuliere ein Ticket gegen eine Ziehung."""
    hits = len(set(ticket) & draw_set)
    win = get_fixed_quote(KENO_TYPE, hits)
    return hits, int(win)


def main():
    print("=" * 80)
    print("WALK-FORWARD BACKTEST: Jackpot Follower (2023-2025)")
    print("=" * 80)
    print("""
WICHTIG: Dieser Test simuliert REALES Spielen!
- Das System kennt die Zukunft NICHT
- Tickets werden NUR aus vergangenen Daten generiert
- Jede Ziehung zwischen Jackpots wird getrackt
""")

    base_path = Path(__file__).parent.parent
    df = load_all_data(base_path)
    jackpot_dates = get_all_jackpot_dates(base_path)

    print(f"Geladene Daten: {len(df)} Ziehungen")
    print(f"Bekannte Jackpots: {len(jackpot_dates)}")

    # Markiere Jackpots
    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)

    # Filter auf Testperiode (2023-2025)
    test_start = pd.Timestamp("2023-01-01")
    test_end = pd.Timestamp("2025-12-31")

    df_test = df[(df["Datum"] >= test_start) & (df["Datum"] <= test_end)].copy()
    df_test = df_test.sort_values("Datum").reset_index(drop=True)

    # Finde alle Jackpots im Testzeitraum
    test_jackpots = sorted([d for d in jackpot_dates
                           if test_start <= d <= test_end])

    print(f"\nTestzeitraum: {test_start.strftime('%d.%m.%Y')} - {test_end.strftime('%d.%m.%Y')}")
    print(f"Ziehungen im Test: {len(df_test)}")
    print(f"Jackpots im Test: {len(test_jackpots)}")

    if len(test_jackpots) < 2:
        print("\nFEHLER: Nicht genug Jackpots fuer Backtest!")
        print("Verfuegbare Jackpots:")
        for d in sorted(jackpot_dates):
            print(f"  {d.strftime('%d.%m.%Y')}")
        return

    # =========================================================================
    # WALK-FORWARD BACKTEST
    # =========================================================================
    print("\n" + "=" * 80)
    print("WALK-FORWARD BACKTEST")
    print("=" * 80)

    all_results = []
    period_results = []

    for i in range(len(test_jackpots)):
        current_jp = test_jackpots[i]
        current_jp_row = df[df["Datum"] == current_jp]

        if len(current_jp_row) == 0:
            continue

        current_jp_numbers = current_jp_row.iloc[0]["numbers_set"]

        # Analysiere Historie NUR bis zu diesem Jackpot (kein Zukunftswissen!)
        pers_rates, pair_rates, fresh_rates = analyze_historical_transitions(
            df, jackpot_dates, current_jp
        )

        # Generiere Ticket basierend auf aktuellem Jackpot und historischen Mustern
        ticket = generate_ticket_at_date(
            current_jp_numbers, pers_rates, pair_rates, fresh_rates
        )

        # Bestimme Spielperiode (bis zum naechsten Jackpot oder Ende)
        if i < len(test_jackpots) - 1:
            next_jp = test_jackpots[i + 1]
            period_end = next_jp
        else:
            period_end = test_end

        # Finde alle Ziehungen in dieser Periode
        period_df = df_test[(df_test["Datum"] > current_jp) &
                            (df_test["Datum"] <= period_end)]

        if len(period_df) == 0:
            continue

        # Simuliere jede Ziehung
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
                "is_jackpot_draw": row["is_jackpot"]
            })

        # Periode zusammenfassen
        period_cost = len(period_df) * EINSATZ
        period_win = sum(period_wins)
        period_netto = period_win - period_cost

        period_results.append({
            "period": i + 1,
            "jp_date": current_jp,
            "ticket": ticket,
            "n_draws": len(period_df),
            "total_cost": period_cost,
            "total_win": period_win,
            "netto": period_netto,
            "avg_hits": np.mean(period_hits),
            "max_hits": max(period_hits),
            "hit_dist": Counter(period_hits),
            "ended_with_jp": i < len(test_jackpots) - 1
        })

    # =========================================================================
    # ERGEBNIS-AUSGABE
    # =========================================================================
    print(f"\n{'Per.':>4} {'Nach JP':>12} {'Ticket':>45} {'Zieh':>6} {'Netto':>10} {'Max':>4}")
    print("-" * 95)

    for p in period_results:
        ticket_str = str(p["ticket"])
        if len(ticket_str) > 40:
            ticket_str = ticket_str[:40] + "..."
        jp_str = p["jp_date"].strftime("%d.%m.%Y") if p["jp_date"] else "-"
        print(f"{p['period']:>4} {jp_str:>12} {ticket_str:>45} {p['n_draws']:>6} "
              f"{p['netto']:>+9} EUR {p['max_hits']:>4}")

    # =========================================================================
    # JAHRES-ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("JAHRES-ZUSAMMENFASSUNG")
    print("=" * 80)

    # Gruppiere nach Jahr
    yearly_stats = defaultdict(lambda: {"draws": 0, "cost": 0, "win": 0, "hits": []})

    for r in all_results:
        year = r["date"].year
        yearly_stats[year]["draws"] += 1
        yearly_stats[year]["cost"] += EINSATZ
        yearly_stats[year]["win"] += r["win"]
        yearly_stats[year]["hits"].append(r["hits"])

    print(f"\n{'Jahr':>6} {'Ziehungen':>10} {'Einsatz':>10} {'Gewinn':>10} {'Netto':>12} {'ROI':>10} {'Avg Hits':>10}")
    print("-" * 75)

    total_draws = 0
    total_cost = 0
    total_win = 0

    for year in sorted(yearly_stats.keys()):
        stats = yearly_stats[year]
        netto = stats["win"] - stats["cost"]
        roi = (netto / stats["cost"] * 100) if stats["cost"] > 0 else 0
        avg_hits = np.mean(stats["hits"])

        total_draws += stats["draws"]
        total_cost += stats["cost"]
        total_win += stats["win"]

        print(f"{year:>6} {stats['draws']:>10} {stats['cost']:>9} EUR {stats['win']:>9} EUR "
              f"{netto:>+11} EUR {roi:>+9.1f}% {avg_hits:>10.2f}")

    total_netto = total_win - total_cost
    total_roi = (total_netto / total_cost * 100) if total_cost > 0 else 0

    print("-" * 75)
    print(f"{'GESAMT':>6} {total_draws:>10} {total_cost:>9} EUR {total_win:>9} EUR "
          f"{total_netto:>+11} EUR {total_roi:>+9.1f}%")

    # =========================================================================
    # TREFFER-VERTEILUNG GESAMT
    # =========================================================================
    print("\n" + "=" * 80)
    print("TREFFER-VERTEILUNG GESAMT")
    print("=" * 80)

    all_hits = [r["hits"] for r in all_results]
    hit_dist = Counter(all_hits)

    print(f"\n{'Treffer':>8} {'Anzahl':>10} {'Prozent':>10} {'Gewinn/Hit':>12} {'Gesamt':>12}")
    print("-" * 55)

    for hits in range(10):
        count = hit_dist.get(hits, 0)
        pct = count / len(all_hits) * 100 if all_hits else 0
        win_per = get_fixed_quote(KENO_TYPE, hits)
        total_for_hits = count * win_per
        print(f"{hits:>8} {count:>10} {pct:>9.1f}% {win_per:>11} EUR {total_for_hits:>11} EUR")

    # =========================================================================
    # JACKPOT-PERFORMANCE
    # =========================================================================
    print("\n" + "=" * 80)
    print("PERFORMANCE AN JACKPOT-TAGEN")
    print("=" * 80)

    jp_results = [r for r in all_results if r["is_jackpot_draw"]]

    print(f"\n{'Datum':>12} {'Hits':>6} {'Gewinn':>10} {'Ticket'}")
    print("-" * 70)

    for r in jp_results:
        print(f"{r['date'].strftime('%d.%m.%Y'):>12} {r['hits']:>6} {r['win']:>9} EUR {r['ticket']}")

    jp_avg_hits = np.mean([r["hits"] for r in jp_results]) if jp_results else 0
    jp_total_win = sum(r["win"] for r in jp_results)

    print(f"\nJackpot-Tage: {len(jp_results)}")
    print(f"Avg Hits an JP-Tagen: {jp_avg_hits:.2f}")
    print(f"Gewinn an JP-Tagen: {jp_total_win} EUR")

    # =========================================================================
    # HIGH-WIN EVENTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("HIGH-WIN EVENTS (6+ Treffer)")
    print("=" * 80)

    high_wins = [r for r in all_results if r["hits"] >= 6]

    print(f"\n{'Datum':>12} {'Hits':>6} {'Gewinn':>10}")
    print("-" * 35)

    for r in sorted(high_wins, key=lambda x: -x["hits"]):
        print(f"{r['date'].strftime('%d.%m.%Y'):>12} {r['hits']:>6} {r['win']:>9} EUR")

    print(f"\nGesamt High-Win Events: {len(high_wins)}")
    print(f"High-Win Gewinn: {sum(r['win'] for r in high_wins)} EUR")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: JACKPOT FOLLOWER WALK-FORWARD BACKTEST")
    print("=" * 80)

    print(f"""
BACKTEST-ZEITRAUM: 2023-2025

GESAMTERGEBNIS:
  Ziehungen gespielt: {total_draws}
  Einsatz:            {total_cost} EUR
  Gewinn:             {total_win} EUR
  NETTO:              {total_netto:+} EUR
  ROI:                {total_roi:+.1f}%

STRATEGIE-MERKMALE:
  - Perioden gespielt:     {len(period_results)}
  - Tickets generiert:     {len(period_results)}
  - Avg Hits gesamt:       {np.mean(all_hits):.2f}
  - High-Win Events (6+):  {len(high_wins)}

JACKPOT-TAGE PERFORMANCE:
  - Avg Hits an JP-Tagen:  {jp_avg_hits:.2f}
  - Gewinn an JP-Tagen:    {jp_total_win} EUR

BEWERTUNG:
  {'PROFITABEL' if total_netto > 0 else 'VERLUST'} - Die Strategie haette {abs(total_netto)} EUR {'Gewinn' if total_netto > 0 else 'Verlust'} erzielt.

WICHTIG: Dies ist ein REALISTISCHER Test ohne Zukunftswissen!
""")

    # Speichere Ergebnisse
    output = {
        "backtest_period": "2023-2025",
        "total_draws": total_draws,
        "total_cost": total_cost,
        "total_win": total_win,
        "total_netto": total_netto,
        "total_roi": total_roi,
        "yearly_results": {
            str(year): {
                "draws": stats["draws"],
                "cost": stats["cost"],
                "win": stats["win"],
                "netto": stats["win"] - stats["cost"],
                "roi": (stats["win"] - stats["cost"]) / stats["cost"] * 100 if stats["cost"] > 0 else 0
            }
            for year, stats in yearly_stats.items()
        },
        "periods": [
            {
                "period": p["period"],
                "jp_date": p["jp_date"].strftime("%Y-%m-%d") if p["jp_date"] else None,
                "ticket": p["ticket"],
                "n_draws": p["n_draws"],
                "netto": p["netto"]
            }
            for p in period_results
        ],
        "hit_distribution": dict(hit_dist),
        "high_win_count": len(high_wins)
    }

    output_path = base_path / "results" / "jackpot_follower_backtest_2023_2025.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
