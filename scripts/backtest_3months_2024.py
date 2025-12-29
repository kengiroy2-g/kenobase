#!/usr/bin/env python
"""3-Monats Backtest des integrierten Modells (Nov 2023 - Feb 2024).

Testet:
- Tägliche Vorhersagen basierend auf Vortag
- Treffer pro Typ (5-10)
- ROI Berechnung
- Monatliche Aufschlüsselung
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import json


# KENO Gewinnplan
KENO_GEWINNPLAN = {
    10: {10: 100000, 9: 1000, 8: 100, 7: 15, 6: 5, 5: 2, 0: 2},
    9: {9: 50000, 8: 1000, 7: 20, 6: 5, 5: 2, 0: 2},
    8: {8: 10000, 7: 100, 6: 15, 5: 2, 4: 1, 0: 2},
    7: {7: 5000, 6: 100, 5: 12, 4: 1, 0: 2},
    6: {6: 1000, 5: 15, 4: 2, 3: 1, 0: 2},
    5: {5: 500, 4: 7, 3: 2, 0: 2},
}


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def get_numbers(row) -> set:
    return set(int(row[f"Keno_Z{i}"]) for i in range(1, 21))


def get_numbers_list(row) -> list:
    return [int(row[f"Keno_Z{i}"]) for i in range(1, 21)]


class PredictionModel:
    """Vereinfachtes Vorhersage-Modell für Backtest."""

    def __init__(self):
        # Wochentags-Favoriten
        self.weekday_favorites = {
            0: [9, 10, 42],      # Montag
            1: [49, 50, 36],     # Dienstag
            2: [9, 16, 49],      # Mittwoch
            3: [20, 10, 66],     # Donnerstag
            4: [44, 59],         # Freitag
            5: [8],              # Samstag
            6: [64, 2, 27],      # Sonntag
        }

        # Hot Neighbor Pairs
        self.hot_neighbors = [
            (9, 10), (2, 3), (27, 28), (38, 39), (43, 44),
            (32, 33), (49, 50), (33, 34), (36, 37), (3, 4),
        ]

        # Kern-Zahlen aus Pair-Analyse
        self.core_numbers = [2, 3, 9, 24, 33, 36, 49, 50, 51, 64]

        # Basis-Scores
        self.base_scores = {
            27: 15.53, 39: 13.10, 60: 12.13, 31: 11.96, 17: 11.83,
            38: 11.61, 43: 11.40, 49: 10.41, 61: 10.05, 42: 9.75,
            16: 9.69, 26: 8.91, 64: 7.23, 9: 7.18, 10: 7.18,
            51: 6.89, 2: 6.79, 3: 6.79, 45: 6.58, 25: 6.45,
        }

        # Summen-Regeln
        self.sum_rules = {
            "low": [27, 57, 36, 49],
            "high": [3, 49, 66, 9, 42],
        }

        # Wiederholungs-Kandidaten
        self.repeat_prone = [49, 9, 3, 64, 36, 61, 42, 50]

        # Position-Exclusion Regeln
        self.exclusion_rules = {
            (11, 56): [41, 45, 70, 6, 7],
            (5, 57): [33, 19, 42, 53, 67],
            (10, 31): [59, 13, 28],
            (8, 60): [46, 48, 16, 31, 35],
            (15, 27): [1, 23, 30],
        }

        # Position-Inclusion Regeln
        self.inclusion_rules = {
            (11, 56): [32, 17, 2, 62, 24],
            (5, 57): [15, 29, 69, 14, 24],
            (11, 38): [19, 67, 42, 50, 64],
            (1, 49): [70, 10, 18, 22, 17],
        }

    def predict(
        self,
        date: datetime,
        yesterday_nums: list[int],
        yesterday_sum: int,
    ) -> dict:
        """Generiert Vorhersage."""

        scores = {n: 0.0 for n in range(1, 71)}
        exclusions = set()

        weekday = date.weekday()

        # 1. Wochentags-Bonus
        for num in self.weekday_favorites.get(weekday, []):
            scores[num] += 5.0

        # 2. Summen-Muster
        if yesterday_sum < 680:
            for num in self.sum_rules["low"]:
                scores[num] += 3.0
        elif yesterday_sum > 740:
            for num in self.sum_rules["high"]:
                scores[num] += 3.0

        # 3. Wiederholungs-Bonus
        for num in yesterday_nums:
            if num in self.repeat_prone:
                scores[num] += 2.0

        # 4. Nachbar-Bonus
        for n1, n2 in self.hot_neighbors:
            if n1 in yesterday_nums and n2 not in yesterday_nums:
                scores[n2] += 3.0
            elif n2 in yesterday_nums and n1 not in yesterday_nums:
                scores[n1] += 3.0

        # 5. Basis-Scores
        for num, base in self.base_scores.items():
            scores[num] += base / 3

        # 6. Kern-Zahlen Bonus
        for num in self.core_numbers:
            scores[num] += 4.0

        # 7. Position-Exclusion (vereinfacht - ohne Position-Info)
        # Wir nutzen nur die Zahlen, nicht die Positionen

        # Sortiere und generiere Top-Zahlen
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        ranked_filtered = [(n, s) for n, s in ranked if n not in exclusions]

        return {
            "top_20": [n for n, s in ranked_filtered[:20]],
            "scores": {n: round(s, 2) for n, s in ranked_filtered[:20]},
        }

    def generate_groups(self, prediction: dict) -> dict:
        """Generiert Zahlengruppen für Typ 5-10."""
        top = prediction["top_20"]
        groups = {}
        for typ in range(5, 11):
            groups[typ] = top[:typ]
        return groups


def calculate_winnings(hits: int, keno_typ: int) -> int:
    """Berechnet Gewinn für gegebene Treffer."""
    plan = KENO_GEWINNPLAN.get(keno_typ, {})
    return plan.get(hits, 0)


def run_backtest(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> dict:
    """Führt Backtest für einen Zeitraum durch."""

    model = PredictionModel()

    # Filter Daten
    mask = (df["Datum"] >= start_date) & (df["Datum"] <= end_date)
    test_df = df[mask].copy()

    results = {
        "period": f"{start_date.date()} bis {end_date.date()}",
        "total_days": 0,
        "by_type": {typ: {
            "total_hits": 0,
            "hit_distribution": defaultdict(int),
            "total_winnings": 0,
            "total_cost": 0,
            "jackpots": 0,
            "gk2": 0,
            "gk3": 0,
        } for typ in range(5, 11)},
        "daily_results": [],
        "monthly_summary": defaultdict(lambda: {
            "days": 0,
            "winnings": defaultdict(int),
            "costs": defaultdict(int),
        }),
    }

    # Finde Index des Start-Datums
    all_indices = df[df["Datum"] >= start_date - timedelta(days=1)].index.tolist()

    for i, idx in enumerate(all_indices[1:], 1):
        if df.loc[idx, "Datum"] > end_date:
            break

        # Gestern
        yesterday_idx = all_indices[i - 1]
        yesterday_row = df.loc[yesterday_idx]
        yesterday_nums = get_numbers_list(yesterday_row)
        yesterday_sum = sum(yesterday_nums)

        # Heute
        today_row = df.loc[idx]
        today_date = today_row["Datum"]
        today_nums = get_numbers(today_row)

        # Vorhersage
        pred = model.predict(today_date, yesterday_nums, yesterday_sum)
        groups = model.generate_groups(pred)

        results["total_days"] += 1
        month_key = today_date.strftime("%Y-%m")

        daily = {
            "date": str(today_date.date()),
            "weekday": today_date.strftime("%a"),
            "actual_numbers": sorted(list(today_nums)),
        }

        # Teste jede Gruppe
        for typ in range(5, 11):
            group = set(groups[typ])
            hits = len(group & today_nums)
            winnings = calculate_winnings(hits, typ)

            results["by_type"][typ]["total_hits"] += hits
            results["by_type"][typ]["hit_distribution"][hits] += 1
            results["by_type"][typ]["total_winnings"] += winnings
            results["by_type"][typ]["total_cost"] += 1

            if hits == typ:
                results["by_type"][typ]["jackpots"] += 1
            elif hits == typ - 1:
                results["by_type"][typ]["gk2"] += 1
            elif hits == typ - 2:
                results["by_type"][typ]["gk3"] += 1

            results["monthly_summary"][month_key]["winnings"][typ] += winnings
            results["monthly_summary"][month_key]["costs"][typ] += 1

            daily[f"typ_{typ}"] = {
                "predicted": groups[typ],
                "hits": hits,
                "winnings": winnings,
            }

        results["monthly_summary"][month_key]["days"] += 1
        results["daily_results"].append(daily)

    # Berechne Statistiken
    for typ in range(5, 11):
        data = results["by_type"][typ]
        if data["total_cost"] > 0:
            data["roi_pct"] = (data["total_winnings"] - data["total_cost"]) / data["total_cost"] * 100
            data["avg_hits"] = data["total_hits"] / results["total_days"]
            data["expected_hits"] = typ * 20 / 70
            data["hit_improvement"] = (data["avg_hits"] / data["expected_hits"] - 1) * 100
        data["hit_distribution"] = dict(data["hit_distribution"])

    return results


def print_results(results: dict):
    """Gibt Ergebnisse formatiert aus."""

    print(f"\n{'='*70}")
    print(f"BACKTEST ERGEBNISSE: {results['period']}")
    print(f"{'='*70}")
    print(f"\nTotal Tage getestet: {results['total_days']}")

    # Pro Typ
    print(f"\n{'Typ':>5} {'Avg Hits':>10} {'Erwartet':>10} {'Verbesserung':>12} "
          f"{'GK1':>5} {'GK2':>5} {'GK3':>5} {'Gewinn':>10} {'Kosten':>8} {'ROI':>10}")
    print("-" * 95)

    for typ in range(10, 4, -1):
        data = results["by_type"][typ]
        print(f"{typ:>5} {data['avg_hits']:>10.2f} {data['expected_hits']:>10.2f} "
              f"{data['hit_improvement']:>+11.1f}% "
              f"{data['jackpots']:>5} {data['gk2']:>5} {data['gk3']:>5} "
              f"{data['total_winnings']:>10}€ {data['total_cost']:>8}€ "
              f"{data['roi_pct']:>+9.1f}%")

    # Monatliche Zusammenfassung
    print(f"\n{'='*70}")
    print("MONATLICHE AUFSCHLÜSSELUNG")
    print(f"{'='*70}")

    for month, mdata in sorted(results["monthly_summary"].items()):
        print(f"\n{month} ({mdata['days']} Tage):")
        print(f"  {'Typ':>5} {'Gewinn':>10} {'Kosten':>8} {'ROI':>10}")
        print("  " + "-" * 40)
        for typ in range(10, 4, -1):
            w = mdata["winnings"][typ]
            c = mdata["costs"][typ]
            roi = (w - c) / c * 100 if c > 0 else 0
            print(f"  {typ:>5} {w:>10}€ {c:>8}€ {roi:>+9.1f}%")

    # Hit-Verteilung für Typ 10
    print(f"\n{'='*70}")
    print("HIT-VERTEILUNG TYP 10")
    print(f"{'='*70}")
    dist = results["by_type"][10]["hit_distribution"]
    for hits in range(11):
        count = dist.get(hits, 0)
        bar = "█" * (count // 2)
        print(f"  {hits:>2} Treffer: {count:>4}x {bar}")

    # Beste Tage
    print(f"\n{'='*70}")
    print("TOP 10 BESTE TAGE")
    print(f"{'='*70}")

    sorted_days = sorted(
        results["daily_results"],
        key=lambda x: x["typ_10"]["winnings"],
        reverse=True
    )

    for day in sorted_days[:10]:
        typ10 = day["typ_10"]
        print(f"  {day['date']} ({day['weekday']}): {typ10['hits']} Treffer, "
              f"{typ10['winnings']}€ - Pred: {typ10['predicted']}")


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - 3-Monats Backtest (Nov 2023 - Feb 2024)")
    print("=" * 70)

    print("\n[1] Lade Daten...")
    df = load_data(path)
    print(f"    {len(df)} Ziehungen geladen")

    # Definiere Testzeitraum: Nov 2023 - Feb 2024
    start_date = datetime(2023, 11, 1)
    end_date = datetime(2024, 2, 20)

    print(f"\n[2] Starte Backtest: {start_date.date()} bis {end_date.date()}")

    results = run_backtest(df, start_date, end_date)

    print_results(results)

    # Speichere Ergebnisse
    output = {
        "period": results["period"],
        "total_days": results["total_days"],
        "by_type": {
            str(k): {
                "avg_hits": v["avg_hits"],
                "expected_hits": v["expected_hits"],
                "hit_improvement_pct": v["hit_improvement"],
                "jackpots": v["jackpots"],
                "gk2": v["gk2"],
                "gk3": v["gk3"],
                "total_winnings": v["total_winnings"],
                "total_cost": v["total_cost"],
                "roi_pct": v["roi_pct"],
                "hit_distribution": v["hit_distribution"],
            }
            for k, v in results["by_type"].items()
        },
        "monthly_summary": {
            k: {
                "days": v["days"],
                "winnings": dict(v["winnings"]),
                "costs": dict(v["costs"]),
            }
            for k, v in results["monthly_summary"].items()
        },
    }

    output_path = Path("results/backtest_3months_2024.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[3] Ergebnisse gespeichert: {output_path}")

    # Finale Zusammenfassung
    print(f"\n{'='*70}")
    print("FINALE ZUSAMMENFASSUNG")
    print(f"{'='*70}")

    best_typ = max(results["by_type"].items(), key=lambda x: x[1]["roi_pct"])
    worst_typ = min(results["by_type"].items(), key=lambda x: x[1]["roi_pct"])

    total_winnings = sum(d["total_winnings"] for d in results["by_type"].values())
    total_cost = sum(d["total_cost"] for d in results["by_type"].values())
    total_roi = (total_winnings - total_cost) / total_cost * 100

    print(f"""
    Testzeitraum:           {results['total_days']} Tage

    BESTER TYP:             Typ {best_typ[0]}
      - ROI:                {best_typ[1]['roi_pct']:+.1f}%
      - Jackpots (GK1):     {best_typ[1]['jackpots']}
      - Treffer-Verbess.:   {best_typ[1]['hit_improvement']:+.1f}%

    SCHLECHTESTER TYP:      Typ {worst_typ[0]}
      - ROI:                {worst_typ[1]['roi_pct']:+.1f}%

    GESAMT (alle Typen):
      - Gewinne:            {total_winnings}€
      - Kosten:             {total_cost}€
      - ROI:                {total_roi:+.1f}%
    """)


if __name__ == "__main__":
    main()
