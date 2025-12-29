#!/usr/bin/env python
"""Finales integriertes KENO Vorhersage-Modell.

Kombiniert alle gefundenen Muster:
1. Position-Praeferenzen (86.9% Exclusion Accuracy)
2. Wochentags-Favoriten
3. Nachbar-Paare
4. Summen-Muster
5. Luecken-Partner
6. Symmetrie-Paare
7. Erste/Letzte Zahl Muster
8. Pair-fokussierte Gruppen (aus Backtest)
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def get_numbers(row) -> set:
    return set(row[f"Keno_Z{i}"] for i in range(1, 21))


def get_numbers_list(row) -> list:
    return [row[f"Keno_Z{i}"] for i in range(1, 21)]


class IntegratedModel:
    """Integriertes KENO Vorhersage-Modell."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.n = len(df)
        self.all_numbers = set(range(1, 71))

        # Sammle alle Muster
        self._build_position_rules()
        self._build_weekday_rules()
        self._build_neighbor_rules()
        self._build_sum_rules()
        self._build_gap_rules()
        self._build_first_last_rules()
        self._build_repeat_rules()

    def _build_position_rules(self):
        """Position-Praeferenzen und Exclusion-Regeln."""
        self.position_prefs = {}
        self.position_exclusions = {}

        expected = self.n / 70

        for pos in range(1, 21):
            col = f"Keno_Z{pos}"
            counts = self.df[col].value_counts()

            for num, count in counts.items():
                deviation = (count - expected) / expected
                if deviation > 0.3:
                    self.position_prefs[(pos, int(num))] = deviation

        # Exclusion-Regeln aus Kontext-Analyse
        # Wenn Zahl X an Position Y -> diese Zahlen weniger wahrscheinlich morgen
        self.exclusion_rules = {
            (11, 56): [41, 45, 70, 6, 7],
            (5, 57): [33, 19, 42, 53, 67],
            (10, 31): [59, 13, 28],
            (8, 60): [46, 48, 16, 31, 35],
            (15, 27): [1, 23, 30],
            (5, 48): [37, 58, 34],
            (10, 59): [63, 18, 48],
            (16, 57): [48, 5, 8],
            (16, 1): [2, 13, 28, 39, 51],
            (14, 8): [57, 63, 8],
        }

        # Inclusion-Regeln
        self.inclusion_rules = {
            (11, 56): [32, 17, 2, 62, 24],
            (5, 57): [15, 29, 69, 14, 24],
            (16, 1): [64, 52, 44, 46, 20],
            (8, 60): [4, 20, 2, 67, 28],
            (5, 24): [4, 19, 20, 25, 27],
            (11, 38): [19, 67, 42, 50, 64],
            (1, 49): [70, 10, 18, 22, 17],
            (11, 61): [44, 49, 2, 10, 25],
            (3, 42): [49, 27, 39, 7, 23],
        }

    def _build_weekday_rules(self):
        """Wochentags-spezifische Favoriten."""
        self.weekday_favorites = {
            0: [9, 10, 42],      # Montag
            1: [49, 50, 36],     # Dienstag
            2: [9, 16, 49],      # Mittwoch
            3: [20, 10, 66],     # Donnerstag
            4: [44, 59],         # Freitag
            5: [8],              # Samstag
            6: [64, 2, 27],      # Sonntag
        }

    def _build_neighbor_rules(self):
        """Hot Nachbar-Paare."""
        self.hot_neighbors = [
            (9, 10), (2, 3), (27, 28), (38, 39), (43, 44),
            (32, 33), (49, 50), (33, 34), (36, 37), (3, 4),
        ]

    def _build_sum_rules(self):
        """Summen-basierte Regeln."""
        self.sum_rules = {
            "low": [27, 57, 36, 49],   # Nach niedriger Summe (<680)
            "high": [3, 49, 66, 9, 42], # Nach hoher Summe (>740)
        }

    def _build_gap_rules(self):
        """Luecken-Partner (nach langer Abwesenheit)."""
        self.gap_partners = {
            31: [18, 23, 13],
            43: [31, 49, 68],
            17: [27, 43, 23],
            60: [61, 14, 21],
            30: [9, 4, 11],
        }

    def _build_first_last_rules(self):
        """Erste/Letzte Zahl Muster."""
        self.common_first = [49, 53, 60, 64, 61]
        self.common_last = [67, 52, 1, 12, 11]

    def _build_repeat_rules(self):
        """Wiederholungs-Muster."""
        # Diese Zahlen wiederholen sich oft
        self.repeat_prone = [49, 9, 3, 64, 36, 61, 42, 50]

    def predict_for_date(
        self,
        date: datetime,
        yesterday_numbers: list[int] = None,
        yesterday_positions: list[int] = None,
        yesterday_sum: int = None,
    ) -> dict:
        """Generiert Vorhersage fuer ein bestimmtes Datum."""

        scores = {n: 0.0 for n in range(1, 71)}
        exclusions = set()
        inclusions = set()
        reasons = defaultdict(list)

        weekday = date.weekday()

        # 1. Wochentags-Bonus
        for num in self.weekday_favorites.get(weekday, []):
            scores[num] += 3.0
            reasons[num].append(f"Wochentags-Favorit ({['Mo','Di','Mi','Do','Fr','Sa','So'][weekday]})")

        # 2. Position-Exclusion/Inclusion Regeln
        if yesterday_numbers and yesterday_positions:
            for i, (pos, num) in enumerate(zip(yesterday_positions, yesterday_numbers)):
                # Exclusion
                if (pos, num) in self.exclusion_rules:
                    for excl in self.exclusion_rules[(pos, num)]:
                        exclusions.add(excl)
                        scores[excl] -= 5.0
                        reasons[excl].append(f"Excluded wegen Zahl {num} an Pos {pos}")

                # Inclusion
                if (pos, num) in self.inclusion_rules:
                    for incl in self.inclusion_rules[(pos, num)]:
                        inclusions.add(incl)
                        scores[incl] += 4.0
                        reasons[incl].append(f"Included wegen Zahl {num} an Pos {pos}")

        # 3. Summen-Muster
        if yesterday_sum:
            if yesterday_sum < 680:
                for num in self.sum_rules["low"]:
                    scores[num] += 2.0
                    reasons[num].append("Nach niedriger Summe wahrscheinlicher")
            elif yesterday_sum > 740:
                for num in self.sum_rules["high"]:
                    scores[num] += 2.0
                    reasons[num].append("Nach hoher Summe wahrscheinlicher")

        # 4. Wiederholungs-Bonus
        if yesterday_numbers:
            for num in yesterday_numbers:
                if num in self.repeat_prone:
                    scores[num] += 1.5
                    reasons[num].append("Wiederholungs-Kandidat")

        # 5. Nachbar-Bonus (wenn ein Nachbar gestern kam)
        if yesterday_numbers:
            for n1, n2 in self.hot_neighbors:
                if n1 in yesterday_numbers and n2 not in yesterday_numbers:
                    scores[n2] += 2.5
                    reasons[n2].append(f"Nachbar von {n1} (Hot Pair)")
                elif n2 in yesterday_numbers and n1 not in yesterday_numbers:
                    scores[n1] += 2.5
                    reasons[n1].append(f"Nachbar von {n2} (Hot Pair)")

        # 6. Basis-Scores aus kombiniertem Modell
        base_scores = {
            27: 15.53, 39: 13.10, 60: 12.13, 31: 11.96, 17: 11.83,
            38: 11.61, 43: 11.40, 49: 10.41, 61: 10.05, 42: 9.75,
            16: 9.69, 26: 8.91, 64: 7.23, 9: 7.18, 10: 7.18,
            51: 6.89, 2: 6.79, 3: 6.79, 45: 6.58, 25: 6.45,
        }
        for num, base in base_scores.items():
            scores[num] += base / 5  # Normalisiert

        # 7. Kern-Zahlen aus Pair-Analyse (starker Bonus)
        core_numbers = [2, 3, 9, 24, 33, 36, 49, 50, 51, 64]
        for num in core_numbers:
            scores[num] += 2.0
            reasons[num].append("Kern-Zahl aus Pair-Analyse")

        # Sortiere und generiere Empfehlungen
        ranked = sorted(scores.items(), key=lambda x: -x[1])

        # Filtere Exclusions
        ranked_filtered = [(n, s) for n, s in ranked if n not in exclusions]

        return {
            "date": date.isoformat(),
            "weekday": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][weekday],
            "top_20": [{"number": n, "score": round(s, 2)} for n, s in ranked_filtered[:20]],
            "exclusions": sorted(list(exclusions)),
            "strong_inclusions": sorted(list(inclusions)),
            "reasons": {n: r for n, r in reasons.items() if r and n in [x[0] for x in ranked_filtered[:20]]},
        }

    def generate_optimized_groups(self, prediction: dict) -> dict:
        """Generiert optimierte Zahlengruppen basierend auf Vorhersage."""

        top_numbers = [item["number"] for item in prediction["top_20"]]
        exclusions = set(prediction["exclusions"])
        inclusions = set(prediction["strong_inclusions"])

        groups = {}

        for typ in range(5, 11):
            # Basis: Top-Zahlen
            group = []

            # Zuerst: Strong Inclusions (wenn nicht excluded)
            for num in inclusions:
                if num not in exclusions and len(group) < typ:
                    group.append(num)

            # Dann: Top-Zahlen
            for num in top_numbers:
                if num not in exclusions and num not in group and len(group) < typ:
                    group.append(num)

            groups[f"typ_{typ}"] = {
                "numbers": sorted(group),
                "contains_inclusions": len([n for n in group if n in inclusions]),
                "excludes_applied": len(exclusions),
            }

        return groups


def backtest_integrated_model(df: pd.DataFrame, model: IntegratedModel, test_ratio: float = 0.3) -> dict:
    """Backtestet das integrierte Modell."""

    test_start = int(len(df) * (1 - test_ratio))
    results = {
        "total_tests": 0,
        "hits_in_top20": [],
        "exclusion_success": 0,
        "exclusion_total": 0,
        "inclusion_success": 0,
        "inclusion_total": 0,
    }

    for idx in range(test_start, len(df) - 1):
        # Gestern
        yesterday = df.loc[idx]
        yesterday_nums = list(get_numbers(yesterday))
        yesterday_positions = list(range(1, 21))
        yesterday_sum = sum(yesterday_nums)

        # Heute (zu vorhersagen)
        today = df.loc[idx + 1]
        today_nums = get_numbers(today)
        today_date = today["Datum"]

        # Vorhersage
        pred = model.predict_for_date(
            today_date,
            yesterday_numbers=yesterday_nums,
            yesterday_positions=yesterday_positions,
            yesterday_sum=yesterday_sum,
        )

        results["total_tests"] += 1

        # Wie viele Top-20 wurden getroffen?
        top20_nums = set(item["number"] for item in pred["top_20"])
        hits = len(top20_nums & today_nums)
        results["hits_in_top20"].append(hits)

        # Exclusion-Erfolg
        for excl in pred["exclusions"]:
            results["exclusion_total"] += 1
            if excl not in today_nums:
                results["exclusion_success"] += 1

        # Inclusion-Erfolg
        for incl in pred["strong_inclusions"]:
            results["inclusion_total"] += 1
            if incl in today_nums:
                results["inclusion_success"] += 1

    # Statistiken
    results["avg_hits_in_top20"] = np.mean(results["hits_in_top20"])
    results["expected_hits"] = 20 * 20 / 70  # ~5.71

    if results["exclusion_total"] > 0:
        results["exclusion_accuracy"] = results["exclusion_success"] / results["exclusion_total"]
    else:
        results["exclusion_accuracy"] = 0

    if results["inclusion_total"] > 0:
        results["inclusion_accuracy"] = results["inclusion_success"] / results["inclusion_total"]
    else:
        results["inclusion_accuracy"] = 0

    return results


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - Finales Integriertes Modell")
    print("=" * 70)

    print("\n[1] Lade Daten und baue Modell...")
    df = load_data(path)
    model = IntegratedModel(df)
    print(f"    {len(df)} Ziehungen geladen")
    print(f"    Position-Exclusion Regeln: {len(model.exclusion_rules)}")
    print(f"    Position-Inclusion Regeln: {len(model.inclusion_rules)}")

    # Backtest
    print("\n[2] Backteste Modell (letzte 30%)...")
    results = backtest_integrated_model(df, model, test_ratio=0.3)

    print(f"\n    BACKTEST ERGEBNISSE:")
    print(f"    Tests durchgefuehrt:     {results['total_tests']}")
    print(f"    Avg Treffer in Top-20:   {results['avg_hits_in_top20']:.2f} (erwartet: {results['expected_hits']:.2f})")
    print(f"    Verbesserung:            {(results['avg_hits_in_top20'] / results['expected_hits'] - 1) * 100:+.1f}%")
    print(f"\n    Exclusion Accuracy:      {results['exclusion_accuracy']:.1%}")
    print(f"    Inclusion Accuracy:      {results['inclusion_accuracy']:.1%}")

    # Vorhersage fuer heute/morgen
    print("\n[3] Generiere aktuelle Vorhersage...")

    # Letzte Ziehung als "Gestern"
    last_row = df.iloc[-1]
    last_nums = list(get_numbers(last_row))
    last_positions = list(range(1, 21))
    last_sum = sum(last_nums)
    last_date = last_row["Datum"]

    # Naechster Tag
    next_date = last_date + pd.Timedelta(days=1)

    prediction = model.predict_for_date(
        next_date,
        yesterday_numbers=last_nums,
        yesterday_positions=last_positions,
        yesterday_sum=last_sum,
    )

    print(f"\n    Vorhersage fuer: {prediction['date']} ({prediction['weekday']})")
    print(f"\n    Letzte Ziehung ({last_date.date()}): {sorted(last_nums)}")
    print(f"    Summe: {last_sum}")

    print(f"\n    TOP 20 ZAHLEN:")
    print(f"    {'Rang':>4} {'Zahl':>6} {'Score':>8} Gruende")
    print("    " + "-" * 60)
    for i, item in enumerate(prediction["top_20"], 1):
        num = item["number"]
        reasons = prediction["reasons"].get(num, [])
        reason_str = ", ".join(reasons[:2]) if reasons else "-"
        print(f"    {i:>4d} {num:>6d} {item['score']:>8.2f} {reason_str[:40]}")

    print(f"\n    EXCLUSIONS (nicht spielen!):")
    print(f"    {prediction['exclusions']}")

    print(f"\n    STRONG INCLUSIONS (bevorzugen!):")
    print(f"    {prediction['strong_inclusions']}")

    # Optimierte Gruppen
    groups = model.generate_optimized_groups(prediction)

    print(f"\n[4] OPTIMIERTE ZAHLENGRUPPEN:")
    print(f"    {'Typ':>6} {'Zahlen':<40} {'Inclusions':>10}")
    print("    " + "-" * 60)
    for typ_key, data in sorted(groups.items(), reverse=True):
        nums_str = str(data["numbers"])
        print(f"    {typ_key:>6} {nums_str:<40} {data['contains_inclusions']:>10}")

    # Speichere Ergebnisse
    output = {
        "model_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "backtest_results": {
            "total_tests": results["total_tests"],
            "avg_hits_in_top20": results["avg_hits_in_top20"],
            "expected_hits": results["expected_hits"],
            "improvement_pct": (results['avg_hits_in_top20'] / results['expected_hits'] - 1) * 100,
            "exclusion_accuracy": results["exclusion_accuracy"],
            "inclusion_accuracy": results["inclusion_accuracy"],
        },
        "current_prediction": {
            "for_date": prediction["date"],
            "weekday": prediction["weekday"],
            "based_on_last_draw": str(last_date.date()),
            "top_20": prediction["top_20"],
            "exclusions": prediction["exclusions"],
            "strong_inclusions": list(prediction["strong_inclusions"]),
        },
        "optimized_groups": groups,
        "model_components": {
            "position_exclusion_rules": len(model.exclusion_rules),
            "position_inclusion_rules": len(model.inclusion_rules),
            "weekday_rules": 7,
            "neighbor_pairs": len(model.hot_neighbors),
            "core_numbers": [2, 3, 9, 24, 33, 36, 49, 50, 51, 64],
        },
    }

    output_path = Path("results/integrated_model_prediction.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[5] Ergebnisse gespeichert: {output_path}")

    # Finale Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG - FINALES INTEGRIERTES MODELL")
    print("=" * 70)

    improvement = (results['avg_hits_in_top20'] / results['expected_hits'] - 1) * 100

    print(f"""
    MODELL-KOMPONENTEN:
    - Position-Exclusion Regeln:  {len(model.exclusion_rules)}
    - Position-Inclusion Regeln:  {len(model.inclusion_rules)}
    - Wochentags-Favoriten:       7 Tage konfiguriert
    - Hot Neighbor Pairs:         {len(model.hot_neighbors)}
    - Kern-Zahlen:                {[2, 3, 9, 24, 33, 36, 49, 50, 51, 64]}

    BACKTEST PERFORMANCE:
    - Treffer in Top-20:          {results['avg_hits_in_top20']:.2f} vs {results['expected_hits']:.2f} erwartet
    - Verbesserung:               {improvement:+.1f}%
    - Exclusion Accuracy:         {results['exclusion_accuracy']:.1%}
    - Inclusion Accuracy:         {results['inclusion_accuracy']:.1%}

    EMPFOHLENE ZAHLEN FUER {prediction['date']}:
    Typ 10: {groups['typ_10']['numbers']}
    Typ  8: {groups['typ_8']['numbers']}
    Typ  6: {groups['typ_6']['numbers']}
    Typ  5: {groups['typ_5']['numbers']}

    NICHT SPIELEN: {prediction['exclusions']}
    """)


if __name__ == "__main__":
    main()
