#!/usr/bin/env python
"""
Monthly Win Frequency Analysis
==============================

Analysiert wie oft verschiedene Gewinnklassen pro Monat vorkommen.
Fokus auf Typ 6, 7, 8 mit unserer Constraint-Strategie.

Autor: Think Tank
Datum: 2025-12-31
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from datetime import datetime
import json
import random

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"

# KENO Quoten
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 100, 7: 5000},
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 15, 7: 100, 8: 10000},
}

# Verbotene Paare
FORBIDDEN_PAIRS = {
    (22, 57), (22, 69), (13, 69), (19, 29), (22, 60), (53, 60),
    (1, 19), (5, 32), (7, 29), (7, 60), (22, 66), (29, 37),
}

FAVORED_PAIRS = {
    (3, 9), (9, 36), (9, 39), (49, 55), (3, 25), (9, 45),
    (10, 45), (12, 45), (36, 42), (45, 61), (5, 9), (9, 16),
}


def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].apply(
        lambda row: [int(x) for x in row if pd.notna(x)], axis=1
    )

    df = df.dropna(subset=["datum"])
    df = df.sort_values("datum").reset_index(drop=True)
    df["year_month"] = df["datum"].dt.to_period("M")
    df["year"] = df["datum"].dt.year
    df["month"] = df["datum"].dt.month
    return df


def has_consecutive_triplet(numbers):
    if len(numbers) < 3:
        return False
    sorted_nums = sorted(numbers)
    for i in range(len(sorted_nums) - 2):
        if sorted_nums[i+1] == sorted_nums[i] + 1 and sorted_nums[i+2] == sorted_nums[i] + 2:
            return True
    return False


def calculate_spread(numbers):
    return max(numbers) - min(numbers)


def count_decades_covered(numbers):
    decades = set((n - 1) // 10 for n in numbers)
    return len(decades)


def count_forbidden_pairs(numbers):
    count = 0
    for pair in combinations(sorted(numbers), 2):
        if pair in FORBIDDEN_PAIRS:
            count += 1
    return count


def is_valid_ticket(numbers, ticket_type):
    if has_consecutive_triplet(numbers):
        return False
    spread_req = {6: 30, 7: 35, 8: 45}
    if calculate_spread(numbers) < spread_req.get(ticket_type, 30):
        return False
    decade_req = {6: 3, 7: 4, 8: 4}
    if count_decades_covered(numbers) < decade_req.get(ticket_type, 3):
        return False
    if count_forbidden_pairs(numbers) > 1:
        return False
    return True


def generate_ticket(pool, size, max_attempts=500):
    favored_nums = set()
    for p1, p2 in FAVORED_PAIRS:
        if p1 in pool: favored_nums.add(p1)
        if p2 in pool: favored_nums.add(p2)

    weighted = sorted(pool, key=lambda x: 10 if x in favored_nums else 0, reverse=True)

    for _ in range(max_attempts):
        ticket = random.sample(weighted[:min(25, len(weighted))], min(size, len(weighted)))
        if len(ticket) == size and is_valid_ticket(ticket, size):
            return sorted(ticket)
    return sorted(pool[:size])


def calculate_frequency_zone(df, window=50):
    recent = df.tail(window)
    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:35]]


def analyze_monthly_wins(df, ticket_type, year_filter=None):
    """
    Analysiert Gewinne pro Monat für einen bestimmten Ticket-Typ.
    """
    if year_filter:
        df_filtered = df[df["year"] == year_filter].copy()
    else:
        df_filtered = df.copy()

    quotes = KENO_QUOTES[ticket_type]
    monthly_results = defaultdict(lambda: {
        "draws": 0,
        "hits": defaultdict(int),
        "wins": defaultdict(int),
        "total_stake": 0,
        "total_win": 0,
    })

    # Walk-forward für jeden Tag
    for i in range(len(df_filtered)):
        idx = df_filtered.index[i]
        current = df_filtered.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])
        year_month = str(current["year_month"])

        # Historische Daten (alles vor diesem Index im Original-DF)
        hist = df.loc[:idx-1] if idx > 0 else df.iloc[:0]

        if len(hist) < 50:
            continue

        hot_zone = calculate_frequency_zone(hist, window=50)
        ticket = generate_ticket(hot_zone, ticket_type)
        ticket_set = set(ticket)

        hits = len(current_numbers & ticket_set)
        win = quotes.get(hits, 0)

        monthly_results[year_month]["draws"] += 1
        monthly_results[year_month]["hits"][hits] += 1
        monthly_results[year_month]["wins"][hits] += win
        monthly_results[year_month]["total_stake"] += 1
        monthly_results[year_month]["total_win"] += win

    return dict(monthly_results)


def print_monthly_summary(monthly_data, ticket_type, year):
    """Druckt monatliche Zusammenfassung."""
    quotes = KENO_QUOTES[ticket_type]

    print(f"\n{'='*80}")
    print(f"TYP {ticket_type} - MONATLICHE GEWINN-ANALYSE {year}")
    print(f"{'='*80}")

    # Gewinnklassen-Namen
    gk_names = {
        6: {3: "GK4_6", 4: "GK3_6", 5: "GK2_6", 6: "GK1_6 (JACKPOT)"},
        7: {3: "GK5_7", 4: "GK4_7", 5: "GK3_7", 6: "GK2_7", 7: "GK1_7 (JACKPOT)"},
        8: {4: "GK5_8", 5: "GK4_8", 6: "GK3_8", 7: "GK2_8", 8: "GK1_8 (JACKPOT)"},
    }

    # Header
    win_classes = [h for h in range(ticket_type + 1) if quotes.get(h, 0) > 0]

    header = f"{'Monat':<10} {'Zieh.':<6}"
    for h in win_classes:
        gk = gk_names[ticket_type].get(h, f"{h}er")
        header += f" {gk:<12}"
    header += f" {'Einsatz':<8} {'Gewinn':<8} {'Netto':<8}"

    print(header)
    print("-" * len(header))

    # Sortiere nach Datum
    sorted_months = sorted(monthly_data.keys())

    yearly_totals = {
        "draws": 0,
        "stake": 0,
        "win": 0,
        "hits": defaultdict(int),
    }

    for month in sorted_months:
        if not month.startswith(str(year)):
            continue

        data = monthly_data[month]

        row = f"{month:<10} {data['draws']:<6}"

        for h in win_classes:
            count = data['hits'].get(h, 0)
            row += f" {count:<12}"

        netto = data['total_win'] - data['total_stake']
        row += f" {data['total_stake']:<8} {data['total_win']:<8} {netto:>+7}"

        print(row)

        yearly_totals["draws"] += data["draws"]
        yearly_totals["stake"] += data["total_stake"]
        yearly_totals["win"] += data["total_win"]
        for h, c in data["hits"].items():
            yearly_totals["hits"][h] += c

    print("-" * len(header))

    # Jahres-Summe
    row = f"{'SUMME':<10} {yearly_totals['draws']:<6}"
    for h in win_classes:
        count = yearly_totals['hits'].get(h, 0)
        row += f" {count:<12}"
    netto = yearly_totals['win'] - yearly_totals['stake']
    row += f" {yearly_totals['stake']:<8} {yearly_totals['win']:<8} {netto:>+7}"
    print(row)

    # Durchschnitt pro Monat
    n_months = len([m for m in sorted_months if m.startswith(str(year))])
    if n_months > 0:
        print(f"\nDurchschnitt pro Monat:")
        print(f"  Ziehungen: {yearly_totals['draws'] / n_months:.1f}")
        for h in win_classes:
            avg = yearly_totals['hits'].get(h, 0) / n_months
            gk = gk_names[ticket_type].get(h, f"{h}er")
            quote = quotes[h]
            print(f"  {gk}: {avg:.2f}x pro Monat (à {quote} EUR)")

    return yearly_totals


def main():
    print("=" * 80)
    print("MONTHLY WIN FREQUENCY ANALYSIS")
    print("Wie oft kommen welche Gewinne pro Monat vor?")
    print("=" * 80)

    df = load_data()
    print(f"\nDaten geladen: {len(df)} Ziehungen")
    print(f"Zeitraum: {df['datum'].min().date()} bis {df['datum'].max().date()}")

    # Verfügbare Jahre
    years = sorted(df['year'].unique())
    print(f"Verfügbare Jahre: {years}")

    all_results = {}

    # Analyse für jeden Typ und jedes Jahr
    for ticket_type in [6, 7, 8]:
        print(f"\n\n{'#'*80}")
        print(f"# ANALYSE TYP {ticket_type}")
        print(f"{'#'*80}")

        monthly_data = analyze_monthly_wins(df, ticket_type)
        all_results[ticket_type] = monthly_data

        for year in [2024, 2025]:
            if year in years:
                print_monthly_summary(monthly_data, ticket_type, year)

    # Vergleichende Zusammenfassung
    print("\n\n" + "=" * 80)
    print("VERGLEICH: ERWARTETE GEWINNE PRO MONAT (basierend auf 2024-2025)")
    print("=" * 80)

    summary = {}

    for ticket_type in [6, 7, 8]:
        quotes = KENO_QUOTES[ticket_type]
        monthly_data = all_results[ticket_type]

        # Nur 2024-2025
        relevant_months = [m for m in monthly_data.keys() if m.startswith("2024") or m.startswith("2025")]

        if not relevant_months:
            continue

        total_draws = sum(monthly_data[m]["draws"] for m in relevant_months)
        n_months = len(relevant_months)

        avg_per_month = {}
        for h in range(ticket_type + 1):
            if quotes.get(h, 0) > 0:
                total_hits = sum(monthly_data[m]["hits"].get(h, 0) for m in relevant_months)
                avg_per_month[h] = total_hits / n_months

        total_win = sum(monthly_data[m]["total_win"] for m in relevant_months)
        total_stake = sum(monthly_data[m]["total_stake"] for m in relevant_months)

        summary[ticket_type] = {
            "months_analyzed": n_months,
            "total_draws": total_draws,
            "draws_per_month": total_draws / n_months,
            "avg_hits_per_month": avg_per_month,
            "avg_win_per_month": total_win / n_months,
            "avg_stake_per_month": total_stake / n_months,
            "avg_netto_per_month": (total_win - total_stake) / n_months,
            "roi": (total_win / total_stake - 1) * 100 if total_stake > 0 else 0,
        }

    # Tabelle
    print(f"\n{'Typ':<6} {'Monate':<8} {'Zieh/Mo':<10} ", end="")
    print(f"{'GK3+':<8} {'GK2+':<8} {'GK1':<8} {'Ø Gewinn':<10} {'Ø Netto':<10} {'ROI':<8}")
    print("-" * 90)

    for t in [6, 7, 8]:
        s = summary[t]
        quotes = KENO_QUOTES[t]

        # Gewinne ab GK3 (mittlere Gewinne)
        gk3_hits = sum(s["avg_hits_per_month"].get(h, 0) for h in range(t-2, t+1) if quotes.get(h, 0) >= 5)
        gk2_hits = sum(s["avg_hits_per_month"].get(h, 0) for h in range(t-1, t+1) if quotes.get(h, 0) >= 15)
        gk1_hits = s["avg_hits_per_month"].get(t, 0)

        print(f"Typ {t:<3} {s['months_analyzed']:<8} {s['draws_per_month']:<10.1f} "
              f"{gk3_hits:<8.2f} {gk2_hits:<8.2f} {gk1_hits:<8.2f} "
              f"{s['avg_win_per_month']:<10.1f} {s['avg_netto_per_month']:>+9.1f} {s['roi']:>+6.1f}%")

    # Detaillierte Gewinnerwartung
    print("\n\nDETAILLIERTE GEWINNERWARTUNG PRO MONAT:")
    print("-" * 60)

    for t in [6, 7, 8]:
        quotes = KENO_QUOTES[t]
        s = summary[t]

        print(f"\nTYP {t}:")
        print(f"  Ziehungen pro Monat: ~{s['draws_per_month']:.0f}")

        for hits in sorted(s["avg_hits_per_month"].keys(), reverse=True):
            avg = s["avg_hits_per_month"][hits]
            quote = quotes[hits]
            monthly_win = avg * quote

            if avg >= 0.01:  # Nur wenn mindestens 1x pro 100 Monate
                freq_text = f"{avg:.2f}x/Monat" if avg >= 1 else f"alle {1/avg:.0f} Monate"
                print(f"  {hits}/{t} ({quote:>6} EUR): {freq_text:<20} = {monthly_win:>6.1f} EUR/Monat")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "timestamp": datetime.now().isoformat(),
        "analysis": "Monthly Win Frequency",
        "summary": {str(k): v for k, v in summary.items()},
        "monthly_details": {str(k): v for k, v in all_results.items()},
    }

    output_file = RESULTS_DIR / "monthly_win_analysis.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_file}")


if __name__ == "__main__":
    main()
