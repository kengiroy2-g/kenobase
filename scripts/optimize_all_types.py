#!/usr/bin/env python3
"""
Optimale Tickets fuer ALLE KENO Typen (2-10)

Findet das beste Ticket fuer jede Gewinnklasse basierend auf:
- Starke Paare
- Historische Win-Rate
- ROI pro Typ

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

# Ensure project root is importable when running `python scripts/...`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.keno_quotes import get_fixed_quote


def load_keno_draws(path: str) -> pd.DataFrame:
    """Laedt KENO Ziehungen."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers"] = df[number_cols].values.tolist()
    df["numbers_set"] = df["numbers"].apply(set)
    return df


def get_strong_pairs(keno_df: pd.DataFrame, min_count: int = 180) -> List[Tuple[int, int]]:
    """Ermittelt starke Paare."""
    pair_counts = defaultdict(int)
    for numbers in keno_df["numbers"].tolist():
        sorted_nums = sorted(numbers)
        for pair in combinations(sorted_nums, 2):
            pair_counts[pair] += 1

    strong = [(k, v) for k, v in pair_counts.items() if v >= min_count]
    strong.sort(key=lambda x: -x[1])
    return strong


def simulate_ticket(ticket: List[int], keno_type: int, draws: pd.DataFrame) -> Dict:
    """Simuliert ein Ticket ueber alle Ziehungen."""
    total_invested = 0
    total_won = 0
    wins_by_hits = defaultdict(int)
    monthly_wins = defaultdict(lambda: {"count": 0, "amount": 0})

    draws["month"] = draws["Datum"].dt.to_period("M")

    for _, row in draws.iterrows():
        draw_set = row["numbers_set"]
        month = str(row["month"])

        hits = sum(1 for n in ticket if n in draw_set)
        win = get_fixed_quote(keno_type, hits)

        total_invested += 1
        total_won += win

        if win > 0:
            wins_by_hits[hits] += 1
            monthly_wins[month]["count"] += 1
            monthly_wins[month]["amount"] += win

    months = list(draws["month"].unique())
    months_with_win = sum(1 for m in months if str(m) in monthly_wins)

    return {
        "total_invested": total_invested,
        "total_won": total_won,
        "roi": (total_won - total_invested) / total_invested if total_invested > 0 else 0,
        "wins_by_hits": dict(wins_by_hits),
        "months_with_win": months_with_win,
        "total_months": len(months),
        "monthly_win_rate": months_with_win / len(months) if months else 0,
        "avg_win_per_draw": total_won / total_invested if total_invested > 0 else 0
    }


def generate_candidates(keno_type: int, strong_pairs: List, hot_numbers: List[int]) -> List[List[int]]:
    """Generiert Ticket-Kandidaten fuer einen KENO Typ."""
    candidates = []

    # Strategie 1: Nur starke Paare
    for pair, count in strong_pairs[:30]:
        ticket = list(pair)
        # Fuelle mit Hot Numbers auf
        for n in hot_numbers:
            if n not in ticket and len(ticket) < keno_type:
                ticket.append(n)
        if len(ticket) == keno_type:
            candidates.append(sorted(ticket))

    # Strategie 2: Multiple Paare kombinieren
    for i, (pair1, _) in enumerate(strong_pairs[:15]):
        for pair2, _ in strong_pairs[i+1:i+10]:
            ticket = list(set(pair1 + pair2))
            for n in hot_numbers:
                if n not in ticket and len(ticket) < keno_type:
                    ticket.append(n)
            if len(ticket) == keno_type:
                candidates.append(sorted(ticket[:keno_type]))

    # Strategie 3: Hot Numbers first
    ticket = hot_numbers[:keno_type]
    candidates.append(sorted(ticket))

    # Deduplizieren
    unique = []
    seen = set()
    for c in candidates:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique[:50]  # Max 50 Kandidaten pro Typ


def find_best_ticket(keno_type: int, candidates: List[List[int]], draws: pd.DataFrame) -> Dict:
    """Findet das beste Ticket fuer einen KENO Typ."""
    best_result = None
    best_roi = -float('inf')

    for ticket in candidates:
        result = simulate_ticket(ticket, keno_type, draws)
        result["ticket"] = ticket

        if result["roi"] > best_roi:
            best_roi = result["roi"]
            best_result = result

    return best_result


def main():
    """Hauptfunktion."""
    print("=" * 80)
    print("OPTIMALE TICKETS FUER ALLE KENO TYPEN (2-10)")
    print("=" * 80)
    print()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"

    # Daten laden
    print("Lade Daten...")
    draws = load_keno_draws(str(keno_path))
    print(f"  Ziehungen: {len(draws)}")
    print(f"  Zeitraum: {draws['Datum'].min().date()} bis {draws['Datum'].max().date()}")
    print()

    # Starke Paare ermitteln
    print("Ermittle starke Paare...")
    strong_pairs = get_strong_pairs(draws, min_count=180)
    print(f"  Gefunden: {len(strong_pairs)} Paare")
    print()

    # Hot Numbers (aus vorheriger Analyse)
    hot_numbers = [49, 64, 3, 51, 24, 2, 9, 36, 41, 37, 4, 25, 31, 13, 66, 52, 45, 40, 21, 1,
                   33, 50, 20, 53, 39, 32, 42, 68, 27, 65]

    results = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_draws": len(draws),
            "date_range": f"{draws['Datum'].min().date()} - {draws['Datum'].max().date()}"
        },
        "by_type": {}
    }

    # Fuer jeden KENO Typ das beste Ticket finden
    print("Analysiere jeden KENO Typ...")
    print()

    for keno_type in range(2, 11):
        print(f"--- TYP {keno_type} ---")

        # Generiere Kandidaten
        candidates = generate_candidates(keno_type, strong_pairs, hot_numbers)
        print(f"  Kandidaten: {len(candidates)}")

        # Finde bestes Ticket
        best = find_best_ticket(keno_type, candidates, draws)

        if best:
            results["by_type"][f"typ_{keno_type}"] = {
                "ticket": best["ticket"],
                "roi": round(best["roi"] * 100, 2),
                "roi_per_draw": round(best["avg_win_per_draw"] - 1, 4),
                "total_invested": best["total_invested"],
                "total_won": best["total_won"],
                "monthly_win_rate": round(best["monthly_win_rate"] * 100, 1),
                "wins_by_hits": best["wins_by_hits"]
            }

            print(f"  Beste Zahlen: {best['ticket']}")
            print(f"  ROI: {best['roi']*100:+.2f}%")
            print(f"  Pro 1 EUR: {best['avg_win_per_draw']:.2f} EUR")
            print(f"  Monatliche Gewinnrate: {best['monthly_win_rate']*100:.1f}%")
            print()

    # Zusammenfassung
    print("=" * 80)
    print("ZUSAMMENFASSUNG: BESTE TICKETS PRO TYP")
    print("=" * 80)
    print()
    print(f"{'Typ':<6} {'Zahlen':<45} {'ROI':>10} {'1 EUR =':>10}")
    print("-" * 80)

    for keno_type in range(2, 11):
        key = f"typ_{keno_type}"
        if key in results["by_type"]:
            data = results["by_type"][key]
            zahlen = ", ".join(map(str, data["ticket"]))
            roi = f"{data['roi']:+.1f}%"
            per_eur = f"{1 + data['roi']/100:.2f} EUR"
            print(f"Typ {keno_type:<3} {zahlen:<45} {roi:>10} {per_eur:>10}")

    print()
    print("=" * 80)
    print("GEWINN PRO 1 EUR EINSATZ (DETAIL)")
    print("=" * 80)
    print()

    for keno_type in range(2, 11):
        key = f"typ_{keno_type}"
        if key in results["by_type"]:
            data = results["by_type"][key]
            roi_per_draw = data["roi"] / 100

            print(f"TYP {keno_type}: {data['ticket']}")
            print(f"  Pro Ziehung:  1 EUR -> {1+roi_per_draw:.2f} EUR ({roi_per_draw:+.2f} EUR)")
            print(f"  Pro Monat:   30 EUR -> {30*(1+roi_per_draw):.0f} EUR ({30*roi_per_draw:+.0f} EUR)")
            print(f"  Pro Jahr:   365 EUR -> {365*(1+roi_per_draw):.0f} EUR ({365*roi_per_draw:+.0f} EUR)")
            print(f"  Gewinnrate: {data['monthly_win_rate']}% der Monate")
            print()

    # Speichern
    output_path = base_path / "results" / "optimal_tickets_all_types.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
