#!/usr/bin/env python3
"""
SUPER-MODELL V1.1 - ADAPTIVE Birthday-Avoidance Strategy

ERKENNTNISSE AUS V1:
- Birthday-Avoidance wirkt NUR bei Jackpots (-10.5%)
- Bei normalen Ziehungen ist der Effekt negativ
- Zu aggressive Exclusion schadet dem ROI

V1.1 VERBESSERUNGEN:
- Adaptive Strategie: Birthday-Avoidance nur wenn Jackpot "faellig"
- Dynamische Gewichtung basierend auf Tagen seit letztem Jackpot
- Erhalt der bewaehrten Original-Komponenten

Autor: Kenobase V2.2 - Adaptive Strategy
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

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
    AntiBirthdayComponent,
    KENO_QUOTES,
    OPTIMAL_TICKETS_KI1,
    UNIFIED_CORE,
    ANTI_BIRTHDAY,
    load_data,
    simulate_ticket,
)


# ============================================================================
# EMPIRISCHE DATEN
# ============================================================================

# Jackpot-ueberrepraesentierte Zahlen (aus high_wins_analysis.json)
JACKPOT_FAVORITES = [51, 58, 61, 7, 36, 13, 43, 15, 3, 48]

# Jackpot-unterrepraesentierte Zahlen
JACKPOT_AVOID = [6, 68, 27, 5, 16, 1, 25, 20, 8]

# Durchschnittliche Tage zwischen Jackpots (aus axiom_first_analysis.json)
AVG_DAYS_BETWEEN_JACKPOTS = 10.06
STD_DAYS_BETWEEN_JACKPOTS = 6.50


# ============================================================================
# V1.1 ADAPTIVE KOMPONENTEN
# ============================================================================

class AdaptiveBirthdayComponent(ModelComponent):
    """
    V1.1: Adaptive Birthday-Vermeidung.

    Logik:
    - Wenn lange kein Jackpot war -> Birthday vermeiden (Jackpot wird faellig)
    - Kurz nach Jackpot -> Birthday normal behandeln

    Parameter:
    - jackpot_due_threshold: Tage ohne Jackpot ab dem Birthday vermieden wird
    - strength: 0.0 = keine Vermeidung, 1.0 = volle Vermeidung
    """

    def __init__(
        self,
        jackpot_due_threshold: int = 15,  # ~1.5x Durchschnitt
        max_strength: float = 0.5
    ):
        super().__init__("adaptive_birthday_v1_1")
        self.threshold = jackpot_due_threshold
        self.max_strength = max_strength

    def apply(self, context: Dict) -> Dict:
        result = {
            "boost": [],
            "soft_avoid": set(),
            "strength": 0.0,
            "reason": "Adaptive Birthday V1.1"
        }

        jackpot_dates = context.get("jackpot_dates", [])
        check_date = context.get("date")

        if not jackpot_dates or not check_date:
            return result

        # Berechne Tage seit letztem Jackpot
        past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
        if not past_jackpots:
            return result

        last_jp = max(past_jackpots)
        days_since = (check_date - last_jp).days

        # Adaptive Strength: steigt mit Tagen seit Jackpot
        if days_since > self.threshold:
            # Linear ansteigende Strength
            excess_days = days_since - self.threshold
            result["strength"] = min(
                self.max_strength,
                0.1 + (excess_days / 20) * self.max_strength
            )

            # Bei hoher Strength: Jackpot-Favoriten boosten
            if result["strength"] > 0.3:
                result["boost"] = JACKPOT_FAVORITES[:5]

            # Bei sehr hoher Strength: Birthday-Zahlen vermeiden
            if result["strength"] > 0.4:
                result["soft_avoid"] = set(JACKPOT_AVOID)

            result["reason"] = f"Jackpot faellig ({days_since} Tage, Strength {result['strength']:.2f})"

        return result


class JackpotDueIndicator(ModelComponent):
    """
    V1.1: Indikator ob Jackpot "faellig" ist.

    Nutzt statistische Analyse:
    - AVG 10 Tage zwischen Jackpots
    - STD 6.5 Tage

    Wenn > AVG + 1*STD (16.5 Tage): Jackpot wird wahrscheinlicher
    """

    def __init__(self, sigma_threshold: float = 1.0):
        super().__init__("jackpot_due_v1_1")
        self.sigma_threshold = sigma_threshold
        self.threshold_days = AVG_DAYS_BETWEEN_JACKPOTS + sigma_threshold * STD_DAYS_BETWEEN_JACKPOTS

    def apply(self, context: Dict) -> Dict:
        result = {
            "jackpot_probability": "normal",
            "days_since_jackpot": 0,
            "boost": [],
            "reason": "Jackpot-Due Indicator V1.1"
        }

        jackpot_dates = context.get("jackpot_dates", [])
        check_date = context.get("date")

        if not jackpot_dates or not check_date:
            return result

        past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
        if not past_jackpots:
            return result

        last_jp = max(past_jackpots)
        days_since = (check_date - last_jp).days
        result["days_since_jackpot"] = days_since

        if days_since > self.threshold_days:
            result["jackpot_probability"] = "elevated"
            result["boost"] = JACKPOT_FAVORITES[:7]
            result["reason"] = f"Jackpot wahrscheinlicher ({days_since} > {self.threshold_days:.1f} Tage)"
        elif days_since > AVG_DAYS_BETWEEN_JACKPOTS:
            result["jackpot_probability"] = "above_average"
            result["boost"] = JACKPOT_FAVORITES[:3]
            result["reason"] = f"Leicht erhoehte Jackpot-Chance ({days_since} Tage)"

        return result


class SmartAntiBirthdayComponent(ModelComponent):
    """
    V1.1: Smarte Anti-Birthday Komponente.

    Kombiniert:
    - Original Anti-Birthday (>31 bevorzugen)
    - Jackpot-spezifische Favoriten
    - Aber NICHT zu aggressiv
    """

    def __init__(self):
        super().__init__("smart_anti_birthday_v1_1")

    def apply(self, context: Dict) -> Dict:
        # Basis: Original Anti-Birthday
        boost_list = list(ANTI_BIRTHDAY)

        # Zusaetzlich: Jackpot-Favoriten die noch nicht drin sind
        for z in JACKPOT_FAVORITES:
            if z not in boost_list:
                boost_list.append(z)

        return {
            "boost": boost_list,
            "reason": "Smart Anti-Birthday V1.1 (Original + Jackpot-Favoriten)"
        }


# ============================================================================
# SUPER-MODELL V1.1 KLASSE
# ============================================================================

class SuperModelV1_1:
    """
    Super-Model V1.1: Adaptive Birthday-Avoidance Strategy.

    Unterschied zu V1:
    - Nicht immer Birthday vermeiden, sondern nur wenn Jackpot "faellig"
    - Behaelt bewaehrte Original-Komponenten bei
    - Fuegt neue V1.1-Komponenten als ERGAENZUNG hinzu

    Strategie-Modi:
    - "normal": Original + leichte V1.1 Anpassungen
    - "jackpot": Aggressive Jackpot-Optimierung wenn Jackpot faellig
    """

    VERSION = "V1.1"

    def __init__(self):
        # Original-Komponenten (unveraendert)
        self.components = {
            "jackpot_warning": JackpotWarningComponent(),
            "exclusion_rules": ExclusionRulesComponent(),
            "temporal": TemporalComponent(),
            "weekday": WeekdayComponent(),
            "sum_context": SumContextComponent(),
            "pair_synergy": PairSynergyComponent(),
            "correlated_absence": CorrelatedAbsenceComponent(),
            # Ersetze simple anti_birthday durch smart version
            "smart_anti_birthday": SmartAntiBirthdayComponent(),
            # Neue V1.1 Komponenten
            "adaptive_birthday": AdaptiveBirthdayComponent(),
            "jackpot_due": JackpotDueIndicator(),
        }

        self.active_components = set(self.components.keys())

    def set_active_components(self, component_names: List[str]):
        """Aktiviert nur bestimmte Komponenten."""
        self.active_components = set(component_names)

    def generate_ticket(
        self,
        keno_type: int,
        context: Dict,
        base_ticket: List[int] = None
    ) -> Tuple[List[int], Dict]:
        """
        Generiert Ticket mit adaptiver Strategie.

        Die Strategie passt sich automatisch an:
        - Normal: Standard-Ticket mit leichter Anti-Birthday Tendenz
        - Jackpot-Mode: Wenn Jackpot faellig, staerkere Anpassung
        """
        # Starte mit Basis-Ticket
        if base_ticket is None:
            base_ticket = OPTIMAL_TICKETS_KI1.get(keno_type, UNIFIED_CORE[:keno_type])

        # Sammle alle Modifikationen
        exclude = set()
        boost_scores = defaultdict(float)
        component_results = {}
        jackpot_mode = False

        for name, component in self.components.items():
            if name not in self.active_components:
                continue

            result = component.apply(context)
            component_results[name] = result

            # Check ob Jackpot-Mode aktiv sein sollte
            if name == "jackpot_due":
                if result.get("jackpot_probability") == "elevated":
                    jackpot_mode = True

            # Sammle Exclusions
            if "exclude" in result:
                exclude.update(result["exclude"])
            if "likely_absent" in result:
                exclude.update(result["likely_absent"])

            # Soft-Avoid nur in Jackpot-Mode beachten
            if jackpot_mode and "soft_avoid" in result:
                # Nicht hart excludieren, aber Penalty geben
                for z in result["soft_avoid"]:
                    boost_scores[z] -= 0.5

            # Sammle Boosts
            if "boost" in result:
                weight = component.weight
                # In Jackpot-Mode: V1.1 Komponenten staerker gewichten
                if jackpot_mode and "v1_1" in name:
                    weight *= 1.5

                for z in result["boost"]:
                    boost_scores[z] += weight

            if "pair_bonus" in result:
                for z, bonus in result["pair_bonus"].items():
                    boost_scores[z] += bonus

        # Generiere finales Ticket
        candidates = [z for z in base_ticket if z not in exclude]

        # Fuege Boost-Zahlen hinzu (sortiert nach Score)
        boost_sorted = sorted(boost_scores.items(), key=lambda x: -x[1])
        for z, score in boost_sorted:
            if score > 0 and z not in exclude and z not in candidates:
                candidates.append(z)

        # Fuelle mit UNIFIED_CORE auf
        for z in UNIFIED_CORE:
            if len(candidates) >= keno_type:
                break
            if z not in exclude and z not in candidates:
                candidates.append(z)

        # Fuelle mit zufaelligen hohen Zahlen auf
        high_numbers = [z for z in range(32, 71) if z not in exclude and z not in candidates]
        np.random.shuffle(high_numbers)
        for z in high_numbers:
            if len(candidates) >= keno_type:
                break
            candidates.append(z)

        final_ticket = sorted(candidates[:keno_type])

        # Metriken
        high_count = sum(1 for z in final_ticket if z > 31)
        jackpot_fav_count = sum(1 for z in final_ticket if z in JACKPOT_FAVORITES)

        metadata = {
            "version": self.VERSION,
            "jackpot_mode": jackpot_mode,
            "excluded": sorted(exclude),
            "boost_scores": {k: v for k, v in boost_sorted[:10]},
            "component_results": component_results,
            "base_ticket": base_ticket,
            "v1_1_metrics": {
                "high_number_ratio": high_count / keno_type,
                "jackpot_favorites_count": jackpot_fav_count,
                "jackpot_mode_active": jackpot_mode,
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
# BACKTEST
# ============================================================================

def backtest_v1_1(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365
) -> Dict:
    """Backtest fuer V1.1 Modell."""

    model = SuperModelV1_1()

    results = {
        "model_version": "V1.1",
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "jackpot_mode_count": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
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

        # Pruefe Skip
        should_skip, reason = model.should_skip(context)
        if should_skip:
            results["skipped"] += 1
            continue

        # Generiere Ticket
        ticket, metadata = model.generate_ticket(keno_type, context)

        if metadata.get("jackpot_mode"):
            results["jackpot_mode_count"] += 1

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
                "win": win,
                "jackpot_mode": metadata.get("jackpot_mode", False)
            })

    # ROI berechnen
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    return results


def compare_all_versions(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime]
) -> Dict:
    """Vergleicht Original, V1 und V1.1."""

    from super_model_synthesis import SuperModel

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "models_compared": ["Original", "V1.1"],
        "results": {}
    }

    for keno_type in [8, 9, 10]:
        print(f"\n{'='*60}")
        print(f"TYP {keno_type}")
        print(f"{'='*60}")

        # Original
        original = SuperModel()
        original.set_active_components([
            "jackpot_warning", "exclusion_rules", "temporal",
            "weekday", "sum_context", "pair_synergy",
            "correlated_absence", "anti_birthday"
        ])

        orig_results = {
            "invested": 0, "won": 0, "skipped": 0, "played": 0,
            "hits_distribution": defaultdict(int), "high_wins": []
        }

        for i in range(365, len(keno_df)):
            prev_row = keno_df.iloc[i - 1]
            curr_row = keno_df.iloc[i]

            context = {
                "date": curr_row["Datum"],
                "prev_date": prev_row["Datum"],
                "prev_positions": prev_row["positions"],
                "prev_numbers": list(prev_row["numbers_set"]),
                "jackpot_dates": jackpot_dates,
            }

            should_skip, _ = original.should_skip(context)
            if should_skip:
                orig_results["skipped"] += 1
                continue

            ticket, _ = original.generate_ticket(keno_type, context)
            draw_set = curr_row["numbers_set"]
            win, hits = simulate_ticket(ticket, keno_type, draw_set)

            orig_results["invested"] += 1
            orig_results["won"] += win
            orig_results["played"] += 1
            orig_results["hits_distribution"][hits] += 1

            if win >= 100:
                orig_results["high_wins"].append({"win": win, "hits": hits})

        orig_roi = (orig_results["won"] - orig_results["invested"]) / orig_results["invested"] * 100

        # V1.1
        v1_1_results = backtest_v1_1(keno_df, jackpot_dates, keno_type)

        comparison["results"][f"typ_{keno_type}"] = {
            "original": {
                "roi": orig_roi,
                "played": orig_results["played"],
                "won": orig_results["won"],
                "high_wins": len(orig_results["high_wins"]),
            },
            "v1_1": {
                "roi": v1_1_results["roi"],
                "played": v1_1_results["played"],
                "won": v1_1_results["won"],
                "high_wins": len(v1_1_results["high_wins"]),
                "jackpot_mode_activations": v1_1_results["jackpot_mode_count"],
            }
        }

        delta = v1_1_results["roi"] - orig_roi

        print(f"\nOriginal: ROI {orig_roi:+.1f}%, High-Wins: {len(orig_results['high_wins'])}")
        print(f"V1.1:     ROI {v1_1_results['roi']:+.1f}%, High-Wins: {len(v1_1_results['high_wins'])}")
        print(f"          Jackpot-Mode aktiviert: {v1_1_results['jackpot_mode_count']}x")
        print(f"\nDelta V1.1 vs Original: {delta:+.1f}%")

    return comparison


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL V1.1 - ADAPTIVE BIRTHDAY-AVOIDANCE")
    print("=" * 70)
    print()
    print("Verbesserungen gegenueber V1:")
    print("  - Birthday-Avoidance NUR wenn Jackpot 'faellig'")
    print("  - Dynamische Aktivierung basierend auf Tagen seit Jackpot")
    print("  - Behaelt bewaehrte Original-Komponenten")
    print()
    print(f"  Jackpot-Durchschnitt: {AVG_DAYS_BETWEEN_JACKPOTS:.1f} Tage")
    print(f"  Jackpot-StdDev: {STD_DAYS_BETWEEN_JACKPOTS:.1f} Tage")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Vergleich
    comparison = compare_all_versions(keno_df, jackpot_dates)

    # Speichern
    output_path = base_path / "results" / "super_model_v1_1_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Aktuelle Empfehlung
    print("\n" + "=" * 70)
    print("V1.1 TICKET-EMPFEHLUNG")
    print("=" * 70)

    model = SuperModelV1_1()
    last_row = keno_df.iloc[-1]

    context = {
        "date": last_row["Datum"] + timedelta(days=1),
        "prev_date": last_row["Datum"],
        "prev_positions": last_row["positions"],
        "prev_numbers": list(last_row["numbers_set"]),
        "jackpot_dates": jackpot_dates,
    }

    should_skip, reason = model.should_skip(context)

    if should_skip:
        print(f"\n  WARNUNG: {reason}")
        print("  EMPFEHLUNG: NICHT SPIELEN!")
    else:
        for keno_type in [10, 9, 8]:
            ticket, metadata = model.generate_ticket(keno_type, context)
            mode = "JACKPOT-MODE" if metadata.get("jackpot_mode") else "NORMAL"
            metrics = metadata.get("v1_1_metrics", {})

            print(f"\n  Typ {keno_type} ({mode}):")
            print(f"    Ticket: {ticket}")
            print(f"    Hohe Zahlen: {metrics.get('high_number_ratio', 0)*100:.0f}%")
            print(f"    Jackpot-Favoriten: {metrics.get('jackpot_favorites_count', 0)}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
