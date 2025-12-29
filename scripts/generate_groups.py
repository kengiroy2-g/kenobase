#!/usr/bin/env python
"""
KENO Number-GROUP Generator v1.0

Paradigmenwechsel: System ist manipuliert (Grundwahrheit).
Alle Anomalien werden ins Modell integriert.

Generiert optimale Zahlen-GRUPPEN (Typ 5-10) basierend auf:
- Hot/Cold Status
- Jackpot-Preference
- Temporal Context (Monatsperiode)
- Pair/Trio Synergien
- Near-Miss Indikatoren
- Decade Distribution
"""

import json
import datetime
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import random

# Pfade
RESULTS_DIR = Path(__file__).parent.parent / "results"
FREQUENCY_FILE = RESULTS_DIR / "number_frequency_context.json"
PAIRS_FILE = RESULTS_DIR / "number_pairs_analysis.json"
NEAR_MISS_FILE = RESULTS_DIR / "near_miss_numbers.json"


class NumberGroupModel:
    """
    Zahlen-Gruppen-Modell basierend auf allen Anomalien.

    Grundwahrheit: Das System ist manipuliert.
    Ziel: Finde Gruppen mit erhoehter Near-Miss oder Jackpot Wahrscheinlichkeit.
    """

    def __init__(self):
        self.frequency_data = None
        self.pairs_data = None
        self.near_miss_data = None

        # Anomalie-Kategorien (aus Analysen)
        self.hot_numbers = set()
        self.cold_numbers = set()
        self.jackpot_favored = set()
        self.jackpot_low = set()
        self.month_start_favored = set()
        self.month_end_favored = set()
        self.near_miss_indicators = set()
        self.jackpot_indicators = set()

        # Pair/Trio Synergien
        self.strong_pairs = []
        self.strong_trios = []

        # Number scores
        self.number_scores = {}

        self._load_data()
        self._build_categories()
        self._calculate_scores()

    def _load_data(self):
        """Lade alle Analysedaten."""
        with open(FREQUENCY_FILE, "r", encoding="utf-8") as f:
            self.frequency_data = json.load(f)

        with open(PAIRS_FILE, "r", encoding="utf-8") as f:
            self.pairs_data = json.load(f)

        with open(NEAR_MISS_FILE, "r", encoding="utf-8") as f:
            self.near_miss_data = json.load(f)

    def _build_categories(self):
        """Baue Anomalie-Kategorien aus den Daten."""
        summary = self.frequency_data["summary"]

        # Hot/Cold
        self.hot_numbers = set(summary["hot_numbers"]["numbers"])
        self.cold_numbers = set(summary["cold_numbers"]["numbers"])

        # Jackpot-Preference
        self.jackpot_favored = set(summary["jackpot_context"]["jackpot_favored_numbers"])

        # Temporal
        self.month_start_favored = set(summary["temporal_context"]["month_start_favored"])
        self.month_end_favored = set(summary["temporal_context"]["month_end_favored"])

        # Near-Miss vs Jackpot Indicators
        self.near_miss_indicators = set(
            self.near_miss_data["summary"]["strongest_near_miss_numbers"]
        )
        self.jackpot_indicators = set(
            self.near_miss_data["summary"]["strongest_jackpot_numbers"]
        )

        # Low jackpot preference (from frequency data)
        for num_str, details in self.frequency_data["numbers_detail"].items():
            if details["jackpot_context"]["jackpot_preference"] == "LOW":
                self.jackpot_low.add(int(num_str))

        # Strong Pairs (>15% above expected)
        for pair_info in self.frequency_data["number_clusters"]["top_pairs"][:30]:
            self.strong_pairs.append(tuple(pair_info["pair"]))

        # Strong Trios
        for trio_info in self.pairs_data["trio_analysis"]["top_20_trios"]:
            self.strong_trios.append(tuple(trio_info["trio"]))

    def _calculate_scores(self):
        """Berechne Score fuer jede Zahl (1-70)."""
        for num in range(1, 71):
            num_str = str(num)
            score = 0.0

            if num_str in self.frequency_data["numbers_detail"]:
                detail = self.frequency_data["numbers_detail"][num_str]

                # Predictability Score (from analysis)
                score += detail["predictability_score"] * 0.5

                # Jackpot Lift Bonus
                lift = detail["jackpot_context"]["lift"]
                if lift > 1.2:
                    score += (lift - 1.0) * 20  # Jackpot-favored bonus
                elif lift < 0.8:
                    score -= (1.0 - lift) * 10  # Jackpot-avoided penalty

                # Deviation Bonus (extreme values = more predictable)
                dev_pct = abs(detail["global"]["deviation_pct"])
                if dev_pct > 5:
                    score += dev_pct * 0.5

            # Near-Miss Indicator
            nm_entry = next(
                (x for x in self.near_miss_data["all_numbers_by_near_miss_score"]
                 if x["number"] == num), None
            )
            if nm_entry:
                score += nm_entry["near_miss_score"] * 50

            self.number_scores[num] = score

    def get_context_multiplier(self, num: int, date: datetime.date = None) -> float:
        """Kontext-Multiplikator basierend auf Datum."""
        if date is None:
            date = datetime.date.today()

        day = date.day
        multiplier = 1.0

        # Monat-Start (1-5)
        if day <= 5:
            if num in self.month_start_favored:
                multiplier *= 1.3
            elif num in self.month_end_favored:
                multiplier *= 0.8

        # Monat-Ende (25-31)
        elif day >= 25:
            if num in self.month_end_favored:
                multiplier *= 1.3
            elif num in self.month_start_favored:
                multiplier *= 0.8

        return multiplier

    def calculate_group_score(
        self,
        numbers: list[int],
        strategy: str = "balanced",
        date: datetime.date = None
    ) -> dict:
        """
        Berechne Score fuer eine Zahlen-Gruppe.

        Strategy:
        - "near_miss": Optimiere fuer k-1 Treffer (Near-Miss)
        - "jackpot": Optimiere fuer k/k Treffer (Jackpot)
        - "balanced": Ausgewogener Ansatz
        """
        if date is None:
            date = datetime.date.today()

        numbers = sorted(numbers)
        n = len(numbers)

        # 1. Basis-Score (Summe der Einzel-Scores)
        base_score = sum(self.number_scores.get(num, 0) for num in numbers)

        # 2. Kontext-Multiplikator
        context_mult = sum(
            self.get_context_multiplier(num, date) for num in numbers
        ) / n

        # 3. Pair Synergy Bonus
        pair_bonus = 0
        for i, j in combinations(numbers, 2):
            if (i, j) in self.strong_pairs or (j, i) in self.strong_pairs:
                pair_bonus += 5

        # 4. Trio Synergy Bonus
        trio_bonus = 0
        for trio in combinations(numbers, 3):
            if tuple(sorted(trio)) in [tuple(sorted(t)) for t in self.strong_trios]:
                trio_bonus += 10

        # 5. Decade Distribution Bonus (gut verteilt = besser)
        decades = defaultdict(int)
        for num in numbers:
            decades[(num - 1) // 10] += 1
        max_per_decade = max(decades.values())
        decade_penalty = (max_per_decade - 2) * 5 if max_per_decade > 2 else 0

        # 6. Strategy-spezifische Anpassungen
        strategy_bonus = 0

        if strategy == "near_miss":
            # Bevorzuge Near-Miss Indikatoren
            nm_count = len(set(numbers) & self.near_miss_indicators)
            strategy_bonus += nm_count * 10
            # Vermeide Jackpot-Indikatoren
            jp_count = len(set(numbers) & self.jackpot_indicators)
            strategy_bonus -= jp_count * 5

        elif strategy == "jackpot":
            # Bevorzuge Jackpot-favored Zahlen
            jf_count = len(set(numbers) & self.jackpot_favored)
            strategy_bonus += jf_count * 15
            # Bevorzuge Jackpot-Indikatoren
            ji_count = len(set(numbers) & self.jackpot_indicators)
            strategy_bonus += ji_count * 10

        else:  # balanced
            # Mix aus beiden
            jf_count = len(set(numbers) & self.jackpot_favored)
            nm_count = len(set(numbers) & self.near_miss_indicators)
            strategy_bonus += jf_count * 5 + nm_count * 5

        # 7. Hot/Cold Balance
        hot_count = len(set(numbers) & self.hot_numbers)
        cold_count = len(set(numbers) & self.cold_numbers)

        # Gesamt-Score
        total_score = (
            base_score * context_mult
            + pair_bonus
            + trio_bonus
            - decade_penalty
            + strategy_bonus
        )

        return {
            "numbers": numbers,
            "total_score": round(total_score, 2),
            "components": {
                "base_score": round(base_score, 2),
                "context_multiplier": round(context_mult, 3),
                "pair_bonus": pair_bonus,
                "trio_bonus": trio_bonus,
                "decade_penalty": decade_penalty,
                "strategy_bonus": strategy_bonus
            },
            "characteristics": {
                "hot_count": hot_count,
                "cold_count": cold_count,
                "jackpot_favored_count": len(set(numbers) & self.jackpot_favored),
                "near_miss_indicator_count": len(set(numbers) & self.near_miss_indicators),
                "jackpot_indicator_count": len(set(numbers) & self.jackpot_indicators),
                "decades_used": len(decades),
                "max_per_decade": max_per_decade
            }
        }

    def generate_optimal_group(
        self,
        size: int = 10,
        strategy: str = "balanced",
        date: datetime.date = None,
        iterations: int = 5000
    ) -> dict:
        """
        Generiere optimale Zahlen-Gruppe fuer gegebene Strategie.

        Verwendet Greedy + Monte-Carlo Optimierung.
        """
        if date is None:
            date = datetime.date.today()

        best_group = None
        best_score = float("-inf")

        # Strategie-spezifische Kandidaten-Pool
        if strategy == "near_miss":
            # Priorisiere Near-Miss Indikatoren
            priority_pool = list(self.near_miss_indicators)
            secondary_pool = [n for n in range(1, 71)
                            if n not in self.jackpot_indicators]
        elif strategy == "jackpot":
            # Priorisiere Jackpot-favored
            priority_pool = list(self.jackpot_favored | self.jackpot_indicators)
            secondary_pool = list(range(1, 71))
        else:
            # Balanced: Top-scored numbers
            sorted_nums = sorted(
                range(1, 71),
                key=lambda x: self.number_scores.get(x, 0),
                reverse=True
            )
            priority_pool = sorted_nums[:20]
            secondary_pool = list(range(1, 71))

        for _ in range(iterations):
            # Starte mit Priority-Zahlen
            n_priority = min(size // 2 + 1, len(priority_pool))
            group = random.sample(priority_pool, min(n_priority, len(priority_pool)))

            # Fuelle mit Secondary auf
            remaining = size - len(group)
            available = [n for n in secondary_pool if n not in group]
            if remaining > 0 and available:
                group.extend(random.sample(available, min(remaining, len(available))))

            if len(group) != size:
                continue

            result = self.calculate_group_score(group, strategy, date)
            if result["total_score"] > best_score:
                best_score = result["total_score"]
                best_group = result

        return best_group

    def generate_recommendations(
        self,
        date: datetime.date = None,
        keno_types: list[int] = None
    ) -> dict:
        """
        Generiere Empfehlungen fuer verschiedene KENO-Typen und Strategien.
        """
        if date is None:
            date = datetime.date.today()

        if keno_types is None:
            keno_types = [5, 6, 7, 8, 9, 10]

        recommendations = {
            "generated_at": datetime.datetime.now().isoformat(),
            "target_date": date.isoformat(),
            "day_of_month": date.day,
            "period": "month_start" if date.day <= 5 else (
                "month_end" if date.day >= 25 else "month_middle"
            ),
            "model_version": "1.0",
            "paradigm": "System als manipuliert angenommen",
            "keno_types": {}
        }

        strategies = ["near_miss", "jackpot", "balanced"]

        for keno_type in keno_types:
            recommendations["keno_types"][f"typ_{keno_type}"] = {}

            for strategy in strategies:
                group = self.generate_optimal_group(
                    size=keno_type,
                    strategy=strategy,
                    date=date,
                    iterations=3000
                )
                recommendations["keno_types"][f"typ_{keno_type}"][strategy] = group

        # Summary der besten Zahlen
        all_scores = [(num, score) for num, score in self.number_scores.items()]
        all_scores.sort(key=lambda x: x[1], reverse=True)

        recommendations["summary"] = {
            "top_20_numbers": [x[0] for x in all_scores[:20]],
            "jackpot_favored_today": sorted(list(
                self.jackpot_favored &
                (self.month_start_favored if date.day <= 5 else
                 self.month_end_favored if date.day >= 25 else set())
            )) or sorted(list(self.jackpot_favored))[:10],
            "near_miss_favored_today": sorted(list(
                self.near_miss_indicators &
                (self.month_start_favored if date.day <= 5 else
                 self.month_end_favored if date.day >= 25 else set())
            )) or sorted(list(self.near_miss_indicators)),
            "strong_pairs_in_model": self.strong_pairs[:10],
            "strong_trios_in_model": self.strong_trios[:5]
        }

        return recommendations


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("KENO Zahlen-GRUPPEN Generator v1.0")
    print("Paradigma: System ist manipuliert (Grundwahrheit)")
    print("=" * 60)

    model = NumberGroupModel()

    # Generiere Empfehlungen fuer heute
    today = datetime.date.today()
    recommendations = model.generate_recommendations(date=today)

    # Speichern
    output_file = RESULTS_DIR / "group_recommendations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_file}")

    # Ausgabe
    print(f"\n{'=' * 60}")
    print(f"EMPFEHLUNGEN FUER {today.isoformat()}")
    print(f"Periode: {recommendations['period']}")
    print(f"{'=' * 60}")

    print("\n--- TOP 20 ZAHLEN (nach Gesamt-Score) ---")
    print(recommendations["summary"]["top_20_numbers"])

    print("\n--- STARKE PAARE ---")
    for pair in recommendations["summary"]["strong_pairs_in_model"]:
        print(f"  {pair}")

    print("\n--- STARKE TRIOS ---")
    for trio in recommendations["summary"]["strong_trios_in_model"]:
        print(f"  {trio}")

    # Beste Gruppen pro Typ
    for typ in [6, 8, 10]:
        typ_key = f"typ_{typ}"
        print(f"\n{'=' * 60}")
        print(f"KENO TYP {typ}")
        print(f"{'=' * 60}")

        for strategy in ["near_miss", "jackpot", "balanced"]:
            group = recommendations["keno_types"][typ_key][strategy]
            print(f"\n[{strategy.upper()}] Score: {group['total_score']}")
            print(f"  Zahlen: {group['numbers']}")
            chars = group["characteristics"]
            print(f"  Hot: {chars['hot_count']}, Cold: {chars['cold_count']}")
            print(f"  Jackpot-favored: {chars['jackpot_favored_count']}")
            print(f"  Near-Miss-Ind.: {chars['near_miss_indicator_count']}")
            print(f"  Jackpot-Ind.: {chars['jackpot_indicator_count']}")


if __name__ == "__main__":
    main()
