#!/usr/bin/env python
"""Generiert optimale Zahlengruppen fuer ALLE Gewinnklassen (nicht nur Jackpot).

Paradigma: Das System IST manipuliert. Wir nutzen ALLE Anomalien (moderat, extrem,
insignifikant) um Zahlen zu identifizieren die hoehere Wahrscheinlichkeit haben.

Signale die kombiniert werden:
1. Top-Paare (co-occurrence >15% ueber Erwartung)
2. Top-Trios (co-occurrence >50% ueber Erwartung)
3. Near-Miss Indikatoren (fuer kleinere Treffer)
4. Jackpot Indikatoren (fuer GK1)
5. Hot/Cold Numbers
6. Jackpot-favored Numbers (hoher Lift)
7. Temporal Context (Monatsende/Anfang)
8. Predictability Ranking
9. Cluster-Reset Status
10. Anti-Birthday Zahlen (32-70)
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Optional


@dataclass
class NumberSignal:
    """Alle Signale fuer eine einzelne Zahl."""
    number: int

    # Frequenz-Signale
    is_hot: bool = False
    is_cold: bool = False
    deviation_pct: float = 0.0

    # Jackpot-Kontext
    jackpot_lift: float = 1.0
    is_jackpot_favored: bool = False

    # Near-Miss Signale
    near_miss_score: float = 0.0
    near_miss_ratio: float = 1.0
    is_near_miss_indicator: bool = False
    is_jackpot_indicator: bool = False

    # Temporal
    temporal_preference: str = "NO_PREFERENCE"
    is_month_end_favored: bool = False
    is_month_start_favored: bool = False

    # Predictability
    predictability_score: float = 0.0
    predictability_rank: int = 70

    # Pair/Trio Bonus
    pair_count: int = 0  # In wie vielen Top-Paaren
    trio_count: int = 0  # In wie vielen Top-Trios
    connected_numbers: set = field(default_factory=set)

    # Anti-Birthday
    is_anti_birthday: bool = False

    # Combined Score
    combined_score: float = 0.0

    def calculate_combined_score(self, weights: dict) -> float:
        """Berechnet gewichteten Gesamt-Score."""
        score = 0.0

        # Frequenz (leicht positiv fuer Hot, neutral fuer Cold)
        if self.is_hot:
            score += weights.get("hot", 0.5) * 0.3

        # Jackpot-Lift (wichtig fuer GK1, aber auch fuer kleinere Klassen)
        score += weights.get("jackpot_lift", 1.0) * min(self.jackpot_lift - 1, 0.5) * 0.5

        # Near-Miss (wichtig fuer kleinere Gewinnklassen!)
        if self.near_miss_score > 0:
            score += weights.get("near_miss", 1.0) * min(self.near_miss_score * 5, 0.5)

        # Predictability (hoechste Gewichtung - diese Zahlen sind "vorhersagbarer")
        score += weights.get("predictability", 1.5) * (self.predictability_score / 30) * 0.4

        # Pair/Trio Bonus (Zahlen in Clustern haben hoehere Chance zusammen zu erscheinen)
        score += weights.get("pair_bonus", 1.0) * min(self.pair_count * 0.02, 0.3)
        score += weights.get("trio_bonus", 1.0) * min(self.trio_count * 0.05, 0.3)

        # Anti-Birthday (weniger Mitspieler = bessere Quote)
        if self.is_anti_birthday:
            score += weights.get("anti_birthday", 0.5) * 0.15

        # Temporal Bonus (je nach aktuellem Datum)
        if self.is_month_end_favored:
            score += weights.get("month_end", 0.3) * 0.1

        self.combined_score = max(0, min(score, 1.0))
        return self.combined_score


def load_all_signals(results_dir: Path) -> dict[int, NumberSignal]:
    """Laedt alle Signal-Daten aus den Ergebnis-Dateien."""
    signals = {i: NumberSignal(number=i) for i in range(1, 71)}

    # 1. Lade number_frequency_context.json
    freq_file = results_dir / "number_frequency_context.json"
    if freq_file.exists():
        with open(freq_file, "r", encoding="utf-8") as f:
            freq_data = json.load(f)

        # Hot/Cold Numbers
        for num in freq_data.get("summary", {}).get("hot_numbers", {}).get("numbers", []):
            signals[num].is_hot = True
        for num in freq_data.get("summary", {}).get("cold_numbers", {}).get("numbers", []):
            signals[num].is_cold = True

        # Jackpot-favored
        for num in freq_data.get("summary", {}).get("jackpot_context", {}).get("jackpot_favored_numbers", []):
            signals[num].is_jackpot_favored = True

        # Temporal preferences
        for num in freq_data.get("summary", {}).get("temporal_context", {}).get("month_end_favored", []):
            signals[num].is_month_end_favored = True
            signals[num].temporal_preference = "MONTH_END"
        for num in freq_data.get("summary", {}).get("temporal_context", {}).get("month_start_favored", []):
            signals[num].is_month_start_favored = True
            signals[num].temporal_preference = "MONTH_START"

        # Predictability Ranking
        for item in freq_data.get("predictability_ranking", []):
            num = item.get("number")
            if num and num in signals:
                signals[num].predictability_score = item.get("score", 0)
                signals[num].predictability_rank = item.get("rank", 70)

        # Detail-Daten pro Zahl
        for num_str, detail in freq_data.get("numbers_detail", {}).items():
            num = int(num_str)
            if num in signals:
                signals[num].deviation_pct = detail.get("global", {}).get("deviation_pct", 0)
                signals[num].jackpot_lift = detail.get("jackpot_context", {}).get("lift", 1.0)

        # Top-Paare
        for pair_info in freq_data.get("number_clusters", {}).get("top_pairs", []):
            pair = pair_info.get("pair", [])
            if len(pair) == 2:
                n1, n2 = pair
                signals[n1].pair_count += 1
                signals[n2].pair_count += 1
                signals[n1].connected_numbers.add(n2)
                signals[n2].connected_numbers.add(n1)

    # 2. Lade near_miss_numbers.json
    nm_file = results_dir / "near_miss_numbers.json"
    if nm_file.exists():
        with open(nm_file, "r", encoding="utf-8") as f:
            nm_data = json.load(f)

        for item in nm_data.get("all_numbers_by_near_miss_score", []):
            num = item.get("number")
            if num and num in signals:
                signals[num].near_miss_score = item.get("near_miss_score", 0)
                signals[num].near_miss_ratio = item.get("ratio", 1.0)

        for item in nm_data.get("top_20_near_miss_indicators", []):
            num = item.get("number")
            if num and num in signals:
                signals[num].is_near_miss_indicator = True

        for item in nm_data.get("top_20_jackpot_indicators", []):
            num = item.get("number")
            if num and num in signals:
                signals[num].is_jackpot_indicator = True

    # 3. Lade number_pairs_analysis.json fuer Trios
    pairs_file = results_dir / "number_pairs_analysis.json"
    if pairs_file.exists():
        with open(pairs_file, "r", encoding="utf-8") as f:
            pairs_data = json.load(f)

        for trio_info in pairs_data.get("top_trios", []):
            trio = trio_info.get("trio", [])
            for num in trio:
                if num in signals:
                    signals[num].trio_count += 1

    # 4. Anti-Birthday (32-70)
    for num in range(32, 71):
        signals[num].is_anti_birthday = True

    return signals


def calculate_group_score(
    numbers: list[int],
    signals: dict[int, NumberSignal],
    top_pairs: list[tuple[int, int]],
    top_trios: list[tuple[int, int, int]],
) -> tuple[float, dict]:
    """Berechnet den Score einer Zahlengruppe."""

    # Basis-Score: Summe der Einzel-Scores
    base_score = sum(signals[n].combined_score for n in numbers)

    # Pair-Bonus: Wenn bekannte Paare in der Gruppe sind
    pair_bonus = 0
    pairs_found = []
    for p in top_pairs:
        if p[0] in numbers and p[1] in numbers:
            pair_bonus += 5
            pairs_found.append(p)

    # Trio-Bonus: Wenn bekannte Trios in der Gruppe sind
    trio_bonus = 0
    trios_found = []
    for t in top_trios:
        if all(n in numbers for n in t):
            trio_bonus += 15
            trios_found.append(t)

    # Dekaden-Verteilung (max 2 pro Dekade ist gut)
    decades = defaultdict(int)
    for n in numbers:
        decade = (n - 1) // 10
        decades[decade] += 1

    decade_penalty = 0
    for count in decades.values():
        if count > 2:
            decade_penalty += (count - 2) * 3

    # Anti-Birthday Bonus
    anti_birthday_count = sum(1 for n in numbers if signals[n].is_anti_birthday)
    anti_birthday_ratio = anti_birthday_count / len(numbers)
    anti_birthday_bonus = anti_birthday_ratio * 5

    # Near-Miss Coverage
    nm_indicators = sum(1 for n in numbers if signals[n].is_near_miss_indicator)
    jp_indicators = sum(1 for n in numbers if signals[n].is_jackpot_indicator)

    # Jackpot-Favored Coverage
    jackpot_favored = sum(1 for n in numbers if signals[n].is_jackpot_favored)

    # Predictability Coverage (wichtig!)
    high_pred_count = sum(1 for n in numbers if signals[n].predictability_score > 10)

    total_score = (
        base_score
        + pair_bonus
        + trio_bonus
        - decade_penalty
        + anti_birthday_bonus
        + high_pred_count * 2
    )

    details = {
        "base_score": round(base_score, 2),
        "pair_bonus": pair_bonus,
        "trio_bonus": trio_bonus,
        "decade_penalty": decade_penalty,
        "anti_birthday_bonus": round(anti_birthday_bonus, 2),
        "pairs_found": pairs_found,
        "trios_found": trios_found,
        "decades_used": len(decades),
        "max_per_decade": max(decades.values()) if decades else 0,
        "anti_birthday_count": anti_birthday_count,
        "nm_indicators": nm_indicators,
        "jp_indicators": jp_indicators,
        "jackpot_favored": jackpot_favored,
        "high_predictability": high_pred_count,
    }

    return total_score, details


def generate_optimal_groups(
    signals: dict[int, NumberSignal],
    top_pairs: list[tuple[int, int]],
    top_trios: list[tuple[int, int, int]],
    group_size: int,
    strategy: str = "balanced",
    num_groups: int = 3,
) -> list[dict]:
    """Generiert optimale Zahlengruppen fuer eine bestimmte Groesse."""

    # Sortiere Zahlen nach combined_score
    sorted_numbers = sorted(
        signals.values(),
        key=lambda s: s.combined_score,
        reverse=True
    )

    # Strategie-spezifische Filterung
    if strategy == "near_miss":
        # Fokus auf Near-Miss Indikatoren (kleinere Gewinnklassen)
        candidates = [s.number for s in sorted_numbers if s.near_miss_score > 0][:40]
    elif strategy == "jackpot":
        # Fokus auf Jackpot-Favored
        candidates = [s.number for s in sorted_numbers if s.is_jackpot_favored]
        candidates += [s.number for s in sorted_numbers if s.number not in candidates][:30]
    elif strategy == "predictable":
        # Fokus auf hohe Predictability
        candidates = [s.number for s in sorted_numbers if s.predictability_score > 5][:40]
    elif strategy == "pair_focused":
        # Fokus auf Zahlen in Top-Paaren
        candidates = [s.number for s in sorted_numbers if s.pair_count > 0][:40]
    else:  # balanced
        # Top 40 nach combined_score
        candidates = [s.number for s in sorted_numbers][:40]

    # Sicherstellen dass genug Kandidaten
    if len(candidates) < group_size:
        candidates = [s.number for s in sorted_numbers][:max(40, group_size + 10)]

    # Generiere und bewerte Gruppen
    best_groups = []

    # Greedy-Ansatz: Baue Gruppen um starke Paare/Trios herum
    for start_pair in top_pairs[:20]:
        if all(n in candidates for n in start_pair):
            group = list(start_pair)
            remaining = [n for n in candidates if n not in group]

            # Fuege Zahlen hinzu die mit der Gruppe verbunden sind
            while len(group) < group_size and remaining:
                # Bevorzuge Zahlen die mit bestehenden verbunden sind
                best_add = None
                best_add_score = -1

                for n in remaining[:20]:
                    # Score basierend auf Verbindungen + combined_score
                    connections = sum(1 for g in group if n in signals[g].connected_numbers)
                    add_score = signals[n].combined_score + connections * 0.1
                    if add_score > best_add_score:
                        best_add_score = add_score
                        best_add = n

                if best_add:
                    group.append(best_add)
                    remaining.remove(best_add)
                else:
                    break

            if len(group) == group_size:
                score, details = calculate_group_score(group, signals, top_pairs, top_trios)
                best_groups.append({
                    "numbers": sorted(group),
                    "score": score,
                    "details": details,
                    "seed": f"pair_{start_pair}",
                })

    # Auch rein score-basierte Gruppen
    score_based = sorted(candidates, key=lambda n: signals[n].combined_score, reverse=True)[:group_size]
    score, details = calculate_group_score(score_based, signals, top_pairs, top_trios)
    best_groups.append({
        "numbers": sorted(score_based),
        "score": score,
        "details": details,
        "seed": "top_scores",
    })

    # Sortiere nach Score und nimm die besten
    best_groups = sorted(best_groups, key=lambda g: g["score"], reverse=True)

    # Dedupliziere (gleiche Zahlen)
    seen = set()
    unique_groups = []
    for g in best_groups:
        key = tuple(g["numbers"])
        if key not in seen:
            seen.add(key)
            unique_groups.append(g)

    return unique_groups[:num_groups]


def main():
    """Hauptfunktion."""
    results_dir = Path("results")

    print("=" * 60)
    print("KENOBASE - Alle-Gewinnklassen Zahlengruppen Generator")
    print("Paradigma: System als manipuliert angenommen")
    print("=" * 60)

    # Lade alle Signale
    print("\n[1] Lade alle Signale...")
    signals = load_all_signals(results_dir)

    # Berechne combined scores
    weights = {
        "hot": 0.5,
        "jackpot_lift": 1.0,
        "near_miss": 1.2,  # Wichtig fuer kleinere Klassen!
        "predictability": 1.5,  # Hoechste Gewichtung
        "pair_bonus": 1.0,
        "trio_bonus": 1.0,
        "anti_birthday": 0.5,
        "month_end": 0.3,
    }

    for sig in signals.values():
        sig.calculate_combined_score(weights)

    # Top-Paare und Trios laden
    top_pairs = []
    top_trios = []

    freq_file = results_dir / "number_frequency_context.json"
    if freq_file.exists():
        with open(freq_file, "r", encoding="utf-8") as f:
            freq_data = json.load(f)
        for p in freq_data.get("number_clusters", {}).get("top_pairs", [])[:30]:
            pair = tuple(p.get("pair", []))
            if len(pair) == 2:
                top_pairs.append(pair)

    pairs_file = results_dir / "number_pairs_analysis.json"
    if pairs_file.exists():
        with open(pairs_file, "r", encoding="utf-8") as f:
            pairs_data = json.load(f)
        for t in pairs_data.get("top_trios", [])[:20]:
            trio = tuple(t.get("trio", []))
            if len(trio) == 3:
                top_trios.append(trio)

    # Generiere Gruppen fuer alle Typen und Strategien
    print("\n[2] Generiere optimale Zahlengruppen...")

    strategies = ["balanced", "near_miss", "jackpot", "predictable", "pair_focused"]
    all_results = {
        "generated_at": datetime.now().isoformat(),
        "paradigm": "System als manipuliert angenommen - ALLE Anomalien genutzt",
        "focus": "Alle Gewinnklassen (GK1-GK10), nicht nur Jackpot",
        "weights_used": weights,
        "signals_summary": {
            "total_numbers": 70,
            "jackpot_favored": sum(1 for s in signals.values() if s.is_jackpot_favored),
            "near_miss_indicators": sum(1 for s in signals.values() if s.is_near_miss_indicator),
            "high_predictability": sum(1 for s in signals.values() if s.predictability_score > 10),
            "in_top_pairs": sum(1 for s in signals.values() if s.pair_count > 0),
            "anti_birthday": sum(1 for s in signals.values() if s.is_anti_birthday),
        },
        "top_20_numbers_by_score": [],
        "groups_by_type": {},
    }

    # Top 20 Zahlen
    sorted_signals = sorted(signals.values(), key=lambda s: s.combined_score, reverse=True)
    for i, sig in enumerate(sorted_signals[:20], 1):
        all_results["top_20_numbers_by_score"].append({
            "rank": i,
            "number": sig.number,
            "combined_score": round(sig.combined_score, 4),
            "predictability": round(sig.predictability_score, 2),
            "near_miss_score": round(sig.near_miss_score, 4),
            "jackpot_lift": round(sig.jackpot_lift, 3),
            "pair_count": sig.pair_count,
            "is_anti_birthday": sig.is_anti_birthday,
            "is_jackpot_favored": sig.is_jackpot_favored,
            "is_near_miss_indicator": sig.is_near_miss_indicator,
        })

    # Generiere Gruppen fuer Typ 5-10
    for typ in range(5, 11):
        print(f"\n  Typ {typ}:")
        all_results["groups_by_type"][f"typ_{typ}"] = {}

        for strategy in strategies:
            groups = generate_optimal_groups(
                signals, top_pairs, top_trios,
                group_size=typ,
                strategy=strategy,
                num_groups=1
            )

            if groups:
                best = groups[0]
                all_results["groups_by_type"][f"typ_{typ}"][strategy] = {
                    "numbers": best["numbers"],
                    "score": round(best["score"], 2),
                    "details": best["details"],
                }
                print(f"    {strategy:15}: {best['numbers']} (Score: {best['score']:.2f})")

    # Speichere Ergebnisse
    output_file = results_dir / "all_class_groups.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[3] Ergebnisse gespeichert: {output_file}")

    # Zusammenfassung ausgeben
    print("\n" + "=" * 60)
    print("EMPFOHLENE ZAHLENGRUPPEN (Alle Gewinnklassen)")
    print("=" * 60)

    for typ in range(10, 4, -1):
        typ_key = f"typ_{typ}"
        if typ_key in all_results["groups_by_type"]:
            balanced = all_results["groups_by_type"][typ_key].get("balanced", {})
            if balanced:
                nums = balanced.get("numbers", [])
                score = balanced.get("score", 0)
                details = balanced.get("details", {})
                print(f"\nTyp {typ}: {nums}")
                print(f"  Score: {score:.2f}")
                print(f"  Paare gefunden: {len(details.get('pairs_found', []))}")
                print(f"  Trios gefunden: {len(details.get('trios_found', []))}")
                print(f"  Near-Miss Indikatoren: {details.get('nm_indicators', 0)}")
                print(f"  Jackpot-Favored: {details.get('jackpot_favored', 0)}")
                print(f"  High Predictability: {details.get('high_predictability', 0)}")


if __name__ == "__main__":
    main()
