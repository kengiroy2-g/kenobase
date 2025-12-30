#!/usr/bin/env python3
"""
SUPER-MODELL V1 - Birthday-Avoidance Strategy

Basiert auf empirischen Befunden aus der Jackpot-Analyse:
- KENO Typ10/10 vermeidet Birthday-Zahlen (1-31) um -10.5%
- Spezifische Zahlen sind bei Jackpots stark unter/ueberrepraesentiert

Neue Komponenten:
- BirthdayAvoidanceV1: Nutzt empirische Jackpot-Daten
- JackpotTargetingV1: Bevorzugt Zahlen die bei Jackpots ueberrepraesentiert sind

Autor: Kenobase V2.2 - Birthday-Avoidance Strategy
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import numpy as np

# Import base components from original
from super_model_synthesis import (
    ModelComponent,
    JackpotWarningComponent,
    ExclusionRulesComponent,
    TemporalComponent,
    WeekdayComponent,
    SumContextComponent,
    PairSynergyComponent,
    CorrelatedAbsenceComponent,
    KENO_QUOTES,
    OPTIMAL_TICKETS_KI1,
    UNIFIED_CORE,
    load_data,
    simulate_ticket,
)


# ============================================================================
# EMPIRISCHE DATEN AUS HIGH-WINS ANALYSE
# ============================================================================

# Zahlen die bei KENO Typ10/10 Jackpots UNTERREPRAESENTIERT sind
# (sollten vermieden werden wenn man auf Jackpot zielt)
JACKPOT_UNDER_REPRESENTED = [
    (6, 0.55),    # 45% weniger als erwartet
    (68, 0.55),
    (27, 0.55),
    (5, 0.56),
    (16, 0.58),
    (1, 0.58),
    (25, 0.66),
    (20, 0.67),
    (8, 0.68),
]

# Zahlen die bei KENO Typ10/10 Jackpots UEBERREPRAESENTIERT sind
# (sollten bevorzugt werden wenn man auf Jackpot zielt)
JACKPOT_OVER_REPRESENTED = [
    (51, 1.58),   # 58% mehr als erwartet
    (58, 1.46),
    (61, 1.45),
    (7, 1.45),
    (36, 1.42),
    (13, 1.40),
    (43, 1.39),
    (15, 1.38),
    (3, 1.36),
    (48, 1.36),
]

# Birthday-Zahlen (1-31) - bei Jackpots vermieden
BIRTHDAY_NUMBERS = set(range(1, 32))

# Hohe Zahlen (32-70) - bei Jackpots bevorzugt
HIGH_NUMBERS = set(range(32, 71))

# Statistiken aus der Analyse
BIRTHDAY_AVOIDANCE_EFFECT = -0.105  # -10.5% bei Typ10/10
JACKPOT_SAMPLE_SIZE = 31  # Anzahl Typ10/10 Jackpots analysiert


# ============================================================================
# NEUE V1 KOMPONENTEN
# ============================================================================

class BirthdayAvoidanceV1Component(ModelComponent):
    """
    V1: Empirisch basierte Birthday-Vermeidung.

    Basiert auf der Analyse von 31 KENO Typ10/10 Jackpots:
    - Birthday-Zahlen (1-31) sind um 10.5% unterrepraesentiert
    - Spezifische Zahlen (6, 5, 27, 16, 1, 8, 20, 25) stark vermieden

    Strategie: Bei Jackpot-Zielen diese Zahlen meiden.
    """

    def __init__(self, strength: float = 1.0):
        super().__init__("birthday_avoidance_v1")
        self.strength = strength

        # Extrahiere nur die Zahlen (ohne Ratio)
        self.avoid_numbers = [z for z, _ in JACKPOT_UNDER_REPRESENTED]
        self.avoid_ratios = {z: r for z, r in JACKPOT_UNDER_REPRESENTED}

    def apply(self, context: Dict) -> Dict:
        result = {
            "exclude": set(),
            "penalties": {},
            "reason": "Birthday-Avoidance V1 (empirisch)"
        }

        # Starke Vermeidung: Zahlen die bei Jackpots <70% Erwartung haben
        for num, ratio in self.avoid_ratios.items():
            if ratio < 0.70:
                result["exclude"].add(num)
            else:
                # Penalty fuer Zahlen 70-80%
                result["penalties"][num] = (1 - ratio) * self.strength

        return result


class JackpotTargetingV1Component(ModelComponent):
    """
    V1: Bevorzuge Zahlen die bei Jackpots ueberrepraesentiert sind.

    Basiert auf der Analyse von 31 KENO Typ10/10 Jackpots:
    - Zahlen wie 51, 58, 61 sind 45-58% haeufiger als erwartet
    - Hohe Zahlen (>31) generell bevorzugt

    Strategie: Bei Jackpot-Zielen diese Zahlen bevorzugen.
    """

    def __init__(self, strength: float = 1.0):
        super().__init__("jackpot_targeting_v1")
        self.strength = strength

        # Extrahiere Zahlen mit Boost-Faktor
        self.boost_numbers = {z: r for z, r in JACKPOT_OVER_REPRESENTED}

    def apply(self, context: Dict) -> Dict:
        result = {
            "boost": list(self.boost_numbers.keys()),
            "boost_scores": {},
            "reason": "Jackpot-Targeting V1 (empirisch)"
        }

        # Boost proportional zum Ueberrepraesentations-Faktor
        for num, ratio in self.boost_numbers.items():
            # ratio=1.58 -> boost_score = 0.58 * strength
            result["boost_scores"][num] = (ratio - 1.0) * self.strength

        return result


class HighNumberPreferenceV1Component(ModelComponent):
    """
    V1: Allgemeine Praeferenz fuer hohe Zahlen (32-70).

    Bei KENO Jackpots sind hohe Zahlen bevorzugt, weil:
    - Weniger Spieler tippen sie (weniger Birthday-Bias)
    - System vermeidet Dauerschein-Treffer

    Strategie: Mindestens 60% hohe Zahlen im Ticket.
    """

    def __init__(self, min_high_ratio: float = 0.6):
        super().__init__("high_number_preference_v1")
        self.min_high_ratio = min_high_ratio

    def apply(self, context: Dict) -> Dict:
        result = {
            "boost": list(HIGH_NUMBERS),
            "constraint": f"min {self.min_high_ratio*100:.0f}% hohe Zahlen",
            "reason": "High-Number Preference V1"
        }
        return result


class LottoContrastV1Component(ModelComponent):
    """
    V1: Kontrast zu Lotto-Strategie.

    Bei Lotto 6aus49 Jackpots sind Birthday-Zahlen BEVORZUGT (+13%).
    Das deutet auf unterschiedliche System-Logik hin.

    Fuer KENO: Nutze das Gegenteil von typischen Lotto-Tipps.
    """

    TYPICAL_LOTTO_NUMBERS = [3, 7, 9, 11, 13, 19, 23, 27, 33, 42, 49]

    def __init__(self):
        super().__init__("lotto_contrast_v1")

    def apply(self, context: Dict) -> Dict:
        result = {
            "slight_avoid": set(self.TYPICAL_LOTTO_NUMBERS),
            "reason": "Lotto-Kontrast (verschiedene System-Logik)"
        }
        return result


# ============================================================================
# SUPER-MODELL V1 KLASSE
# ============================================================================

class SuperModelV1:
    """
    Super-Model V1: Birthday-Avoidance Strategy.

    Erweitert das Original-Modell um empirisch basierte Komponenten:
    - BirthdayAvoidanceV1: Vermeidet bei Jackpots unterrepraesentierte Zahlen
    - JackpotTargetingV1: Bevorzugt bei Jackpots ueberrepraesentierte Zahlen
    - HighNumberPreferenceV1: Allgemeine Praeferenz fuer Zahlen >31

    Unterschied zum Original:
    - Original: Einfache Anti-Birthday Liste (>31)
    - V1: Empirisch gewichtete Vermeidung/Bevorzugung
    """

    def __init__(self):
        # Original-Komponenten
        self.components = {
            "jackpot_warning": JackpotWarningComponent(),
            "exclusion_rules": ExclusionRulesComponent(),
            "temporal": TemporalComponent(),
            "weekday": WeekdayComponent(),
            "sum_context": SumContextComponent(),
            "pair_synergy": PairSynergyComponent(),
            "correlated_absence": CorrelatedAbsenceComponent(),
            # V1 Komponenten (ersetzen anti_birthday)
            "birthday_avoidance_v1": BirthdayAvoidanceV1Component(),
            "jackpot_targeting_v1": JackpotTargetingV1Component(),
            "high_number_pref_v1": HighNumberPreferenceV1Component(),
            "lotto_contrast_v1": LottoContrastV1Component(),
        }

        # Standard: Alle V1 Komponenten aktiv
        self.active_components = set(self.components.keys())

        # V1-spezifische Optimal-Tickets (angepasst an Birthday-Avoidance)
        self.optimal_tickets_v1 = {
            10: [3, 7, 13, 15, 36, 43, 48, 51, 58, 61],  # Top Jackpot-Zahlen
            9: [3, 7, 13, 36, 43, 48, 51, 58, 61],
            8: [3, 13, 36, 43, 48, 51, 58, 61],
            7: [3, 36, 43, 51, 58, 61, 64],
            6: [36, 43, 51, 58, 61, 64],
        }

    def set_active_components(self, component_names: List[str]):
        """Aktiviert nur bestimmte Komponenten."""
        self.active_components = set(component_names)

    def generate_ticket(
        self,
        keno_type: int,
        context: Dict,
        strategy: str = "jackpot"  # "jackpot" oder "balanced"
    ) -> Tuple[List[int], Dict]:
        """
        Generiert optimiertes Ticket basierend auf V1-Strategie.

        Args:
            keno_type: KENO-Typ (6-10)
            context: Kontext-Dict mit Datum, vorherige Ziehung, etc.
            strategy: "jackpot" fuer maximale Jackpot-Chance,
                     "balanced" fuer ausgewogenere Strategie

        Returns:
            Tuple aus (ticket, metadata)
        """
        # Starte mit V1-optimierten Tickets
        base_ticket = self.optimal_tickets_v1.get(keno_type, [])

        # Sammle alle Modifikationen
        exclude = set()
        boost_scores = defaultdict(float)
        component_results = {}

        for name, component in self.components.items():
            if name not in self.active_components:
                continue

            result = component.apply(context)
            component_results[name] = result

            # Sammle Exclusions
            if "exclude" in result:
                exclude.update(result["exclude"])
            if "likely_absent" in result:
                exclude.update(result["likely_absent"])
            if "slight_avoid" in result and strategy == "jackpot":
                # Bei Jackpot-Strategie: auch leichte Vermeidungen beachten
                exclude.update(result["slight_avoid"])

            # Sammle Boosts
            if "boost" in result:
                for z in result["boost"]:
                    boost_scores[z] += component.weight

            if "boost_scores" in result:
                for z, score in result["boost_scores"].items():
                    boost_scores[z] += score

            if "pair_bonus" in result:
                for z, bonus in result["pair_bonus"].items():
                    boost_scores[z] += bonus

        # Generiere finales Ticket
        candidates = [z for z in base_ticket if z not in exclude]

        # Fuege Boost-Zahlen hinzu (sortiert nach Score)
        boost_sorted = sorted(boost_scores.items(), key=lambda x: -x[1])
        for z, score in boost_sorted:
            if z not in exclude and z not in candidates:
                candidates.append(z)

        # Bei Jackpot-Strategie: bevorzuge hohe Zahlen
        if strategy == "jackpot":
            high_candidates = [z for z in candidates if z > 31]
            low_candidates = [z for z in candidates if z <= 31]

            # Mindestens 60% hohe Zahlen
            min_high = int(keno_type * 0.6)

            final_candidates = high_candidates[:min_high]
            remaining = keno_type - len(final_candidates)

            # Fuelle mit restlichen Kandidaten auf
            for z in low_candidates + high_candidates[min_high:]:
                if len(final_candidates) >= keno_type:
                    break
                if z not in final_candidates:
                    final_candidates.append(z)

            candidates = final_candidates

        # Fuelle mit hohen Zahlen auf falls noetig
        all_high = sorted(HIGH_NUMBERS - exclude)
        np.random.shuffle(all_high)
        for z in all_high:
            if len(candidates) >= keno_type:
                break
            if z not in candidates:
                candidates.append(z)

        final_ticket = sorted(candidates[:keno_type])

        # Berechne V1-Metriken
        high_count = sum(1 for z in final_ticket if z > 31)
        birthday_count = sum(1 for z in final_ticket if z in BIRTHDAY_NUMBERS)
        jackpot_favored_count = sum(
            1 for z in final_ticket
            if z in [x[0] for x in JACKPOT_OVER_REPRESENTED]
        )

        metadata = {
            "version": "V1",
            "strategy": strategy,
            "excluded": sorted(exclude),
            "boost_scores": dict(boost_scores),
            "component_results": component_results,
            "base_ticket": base_ticket,
            "v1_metrics": {
                "high_number_ratio": high_count / keno_type,
                "birthday_count": birthday_count,
                "jackpot_favored_count": jackpot_favored_count,
            }
        }

        return final_ticket, metadata

    def should_skip(self, context: Dict) -> Tuple[bool, str]:
        """Prueft ob Ziehung uebersprungen werden soll."""
        if "jackpot_warning" in self.active_components:
            result = self.components["jackpot_warning"].apply(context)
            if result.get("skip"):
                return True, result.get("reason", "Jackpot Cooldown")
        return False, None


# ============================================================================
# BACKTEST FUNKTIONEN
# ============================================================================

def backtest_model(
    model,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365,
    strategy: str = "jackpot"
) -> Dict:
    """Fuehrt Backtest fuer ein Modell durch."""

    results = {
        "model_version": getattr(model, "version", "original"),
        "strategy": strategy,
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],  # Gewinne >= 100
        "daily_results": []
    }

    for i in range(start_idx, len(keno_df)):
        prev_row = keno_df.iloc[i - 1]
        curr_row = keno_df.iloc[i]

        context = {
            "date": curr_row["Datum"],
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Pruefe ob uebersprungen werden soll
        should_skip, reason = model.should_skip(context)
        if should_skip:
            results["skipped"] += 1
            continue

        # Generiere Ticket
        if hasattr(model, "generate_ticket"):
            if "strategy" in model.generate_ticket.__code__.co_varnames:
                ticket, metadata = model.generate_ticket(keno_type, context, strategy=strategy)
            else:
                ticket, metadata = model.generate_ticket(keno_type, context)
        else:
            ticket = list(range(1, keno_type + 1))
            metadata = {}

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_row["Datum"].date()),
                "ticket": ticket,
                "hits": hits,
                "win": win
            })

        results["daily_results"].append({
            "date": str(curr_row["Datum"].date()),
            "ticket": ticket,
            "hits": hits,
            "win": win,
            "v1_metrics": metadata.get("v1_metrics", {})
        })

    # Berechne ROI
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    return results


def compare_models(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [8, 9, 10]
) -> Dict:
    """Vergleicht Original-Modell mit V1."""

    from super_model_synthesis import SuperModel

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "results": {}
    }

    for keno_type in keno_types:
        print(f"\n{'='*60}")
        print(f"VERGLEICH FUER TYP {keno_type}")
        print(f"{'='*60}")

        # Original-Modell
        original = SuperModel()
        original.set_active_components([
            "jackpot_warning", "exclusion_rules", "temporal",
            "weekday", "sum_context", "pair_synergy",
            "correlated_absence", "anti_birthday"
        ])

        original_result = backtest_model(
            original, keno_df, jackpot_dates, keno_type
        )

        # V1-Modell (Jackpot-Strategie)
        v1_model = SuperModelV1()
        v1_result = backtest_model(
            v1_model, keno_df, jackpot_dates, keno_type, strategy="jackpot"
        )

        # V1-Modell (Balanced-Strategie)
        v1_balanced_result = backtest_model(
            v1_model, keno_df, jackpot_dates, keno_type, strategy="balanced"
        )

        comparison["results"][f"typ_{keno_type}"] = {
            "original": {
                "roi": original_result["roi"],
                "played": original_result["played"],
                "won": original_result["won"],
                "high_wins_count": len(original_result["high_wins"]),
            },
            "v1_jackpot": {
                "roi": v1_result["roi"],
                "played": v1_result["played"],
                "won": v1_result["won"],
                "high_wins_count": len(v1_result["high_wins"]),
            },
            "v1_balanced": {
                "roi": v1_balanced_result["roi"],
                "played": v1_balanced_result["played"],
                "won": v1_balanced_result["won"],
                "high_wins_count": len(v1_balanced_result["high_wins"]),
            }
        }

        print(f"\nOriginal:      ROI {original_result['roi']:+.1f}%, "
              f"Gespielt: {original_result['played']}, "
              f"High-Wins: {len(original_result['high_wins'])}")
        print(f"V1 (Jackpot):  ROI {v1_result['roi']:+.1f}%, "
              f"Gespielt: {v1_result['played']}, "
              f"High-Wins: {len(v1_result['high_wins'])}")
        print(f"V1 (Balanced): ROI {v1_balanced_result['roi']:+.1f}%, "
              f"Gespielt: {v1_balanced_result['played']}, "
              f"High-Wins: {len(v1_balanced_result['high_wins'])}")

        # Delta
        delta_jackpot = v1_result["roi"] - original_result["roi"]
        delta_balanced = v1_balanced_result["roi"] - original_result["roi"]

        print(f"\nDelta V1-Jackpot vs Original: {delta_jackpot:+.1f}%")
        print(f"Delta V1-Balanced vs Original: {delta_balanced:+.1f}%")

    return comparison


def main():
    """Hauptfunktion: Vergleicht Original mit V1."""
    print("=" * 70)
    print("SUPER-MODELL V1 - BIRTHDAY-AVOIDANCE STRATEGY")
    print("=" * 70)
    print()
    print("Basiert auf empirischen Befunden:")
    print(f"  - Birthday-Avoidance Effekt: {BIRTHDAY_AVOIDANCE_EFFECT*100:.1f}%")
    print(f"  - Analysierte Jackpots: {JACKPOT_SAMPLE_SIZE}")
    print()
    print("Unter-repraesentierte Zahlen bei Jackpots:")
    for z, r in JACKPOT_UNDER_REPRESENTED[:5]:
        print(f"  {z:2d}: {r:.2f}x (vermieden)")
    print()
    print("Ueber-repraesentierte Zahlen bei Jackpots:")
    for z, r in JACKPOT_OVER_REPRESENTED[:5]:
        print(f"  {z:2d}: {r:.2f}x (bevorzugt)")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Vergleiche Modelle
    comparison = compare_models(keno_df, jackpot_dates, keno_types=[8, 9, 10])

    # Speichern
    output_path = base_path / "results" / "super_model_v1_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Empfehlung generieren
    print("\n" + "=" * 70)
    print("V1 TICKET-EMPFEHLUNG (naechste Ziehung)")
    print("=" * 70)

    v1_model = SuperModelV1()

    last_row = keno_df.iloc[-1]
    context = {
        "date": last_row["Datum"] + timedelta(days=1),
        "prev_date": last_row["Datum"],
        "prev_positions": last_row["positions"],
        "prev_numbers": list(last_row["numbers_set"]),
        "jackpot_dates": jackpot_dates,
    }

    should_skip, reason = v1_model.should_skip(context)

    if should_skip:
        print(f"\n  WARNUNG: {reason}")
        print("  EMPFEHLUNG: NICHT SPIELEN!")
    else:
        print(f"\n  Keine Warnung aktiv")

        for keno_type in [10, 9, 8]:
            ticket, metadata = v1_model.generate_ticket(keno_type, context, strategy="jackpot")
            metrics = metadata.get("v1_metrics", {})
            print(f"\n  Typ {keno_type} (Jackpot-Strategie):")
            print(f"    Ticket: {ticket}")
            print(f"    Hohe Zahlen: {metrics.get('high_number_ratio', 0)*100:.0f}%")
            print(f"    Birthday-Zahlen: {metrics.get('birthday_count', 0)}")
            print(f"    Jackpot-Favoriten: {metrics.get('jackpot_favored_count', 0)}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
