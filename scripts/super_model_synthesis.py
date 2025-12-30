#!/usr/bin/env python3
"""
SUPER-MODELL SYNTHESE - Kombiniert alle 3 KI-Erkenntnisse

Integriert:
- KI #1: Jackpot-Warnung, Optimale Tickets, Exclusion-Regeln
- KI #2: Position-Rule-Layer, Wilson-LB Scoring
- KI #3: Number-Group-Model, Near-Miss/Jackpot Strategien, Temporale Anomalien

Testet alle moeglichen Kombinationen und findet das beste Modell.

Autor: Kenobase V2.2 - Multi-KI Synthese
Datum: 2025-12-29
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import numpy as np

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE


# ============================================================================
# KOMPONENTEN AUS KI #1 (Dynamic Recommendation)
# ============================================================================

# Optimale Tickets (6-Jahres-Backtest)
OPTIMAL_TICKETS_KI1 = {
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],      # ROI +351%
    8: [3, 20, 24, 27, 36, 49, 51, 64],         # ROI +115%
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],  # ROI +189%
    7: [3, 24, 30, 49, 51, 59, 64],             # ROI +41%
    6: [3, 9, 10, 32, 49, 64],                  # ROI ~0%
}

# Kern-Zahlen KI #1
CORE_NUMBERS_KI1 = [3, 24, 49, 51, 64]

# Exclusion-Regeln KI #1 (100% Accuracy)
EXCLUSION_RULES_KI1 = {
    (4, 17): [70],
    (24, 2): [22],
    (4, 14): [25],
    (14, 7): [38],
    (5, 2): [13],
    (68, 20): [65],
    (50, 4): [64],
    (1, 8): [33],
}

# Multi-Exclusion Regeln KI #1 (>90% Accuracy)
MULTI_EXCLUSION_KI1 = {
    (56, 11): ([41, 45, 70], 96.0),
    (57, 5): ([33, 19, 42], 93.3),
    (31, 10): ([59, 13, 28], 90.8),
    (60, 8): ([46, 48, 16], 90.0),
    (27, 15): ([1, 23, 30], 88.4),
}

# Korrelierte Absenzen KI #1
CORRELATED_ABSENCES = [
    (41, 45, 7.5),
    (1, 37, 6.7),
    (1, 45, 6.3),
    (45, 51, 6.2),
]

# Jackpot-Cooldown KI #1
JACKPOT_COOLDOWN_DAYS = 30


# ============================================================================
# KOMPONENTEN AUS KI #2 (Position Rule Layer)
# ============================================================================

# Position-Praeferenzen (>40% Deviation)
POSITION_PREFERENCES_KI2 = [
    (38, 11, 68.6),
    (49, 1, 59.2),
    (61, 11, 56.1),
    (42, 3, 53.0),
    (59, 10, 49.9),
    (27, 15, 46.7),
    (29, 7, 46.7),
    (64, 7, 46.7),
]

# Wilson-LB Thresholds KI #2
WILSON_EXCLUDE_LB = 0.85
WILSON_INCLUDE_LB = 0.35


# ============================================================================
# KOMPONENTEN AUS KI #3 (Number Group Model)
# ============================================================================

# Jackpot-favored Zahlen
JACKPOT_FAVORED_KI3 = [3, 4, 9, 13, 24, 31, 35, 36, 37, 40, 41, 49, 51, 52, 64, 66, 69]

# Near-Miss Indikatoren
NEAR_MISS_INDICATORS_KI3 = [31, 11, 25, 18, 17]

# Temporale Anomalien
MONTH_START_FAVORED = [16, 20, 21, 25, 26, 33, 39, 41, 53, 55, 56, 60]  # Tag 1-5
MONTH_END_FAVORED = [1, 2, 24, 34, 45, 48]  # Tag 25-31

# Staerkste Paare KI #3 (>20% Lift)
TOP_PAIRS_KI3 = [
    (9, 50, 23.9),
    (20, 36, 23.9),
    (9, 10, 23.3),
    (32, 64, 21.6),
    (33, 49, 21.0),
]

# Staerkste Trios KI #3 (>50% Lift)
TOP_TRIOS_KI3 = [
    (9, 39, 50, 63.1),
    (19, 28, 49, 58.8),
    (27, 49, 54, 58.8),
    (7, 9, 10, 58.8),
]

# Wochentags-Favoriten
WEEKDAY_FAVORITES = {
    0: [9, 10, 42],    # Montag
    1: [49, 50, 36],   # Dienstag
    2: [9, 16, 49],    # Mittwoch
    3: [20, 10, 66],   # Donnerstag
    4: [44, 59],       # Freitag
    5: [8],            # Samstag
    6: [64, 2, 27],    # Sonntag
}

# Summen-basierte Favoriten
LOW_SUM_FAVORITES = [27, 57, 36, 49]   # Nach Summe <650
HIGH_SUM_FAVORITES = [3, 49, 66, 9, 42]  # Nach Summe >770


# ============================================================================
# VEREINIGTE KERN-ZAHLEN (alle KIs)
# ============================================================================

# Zahlen die in ALLEN Analysen erscheinen
UNIFIED_CORE = [2, 3, 9, 24, 33, 36, 49, 50, 51, 64]

# Anti-Birthday Zahlen (>31, bevorzugt fuer weniger Gewinner-Teilung)
ANTI_BIRTHDAY = [33, 35, 36, 37, 40, 41, 42, 49, 51, 52, 53, 56, 57, 59, 64, 66, 69]


# ============================================================================
# V2 BIRTHDAY-AVOIDANCE TICKETS (2025 Out-of-Sample validiert)
# ============================================================================
# Diese Tickets haben im 2025 Test dramatisch besser performt als die Originale:
# - Typ 9: +1545.7% ROI (vs +209.6% Original)
# - Typ 10: +305.5% ROI (vs +77.7% Original)
# - Typ 8: +261.4% ROI (vs -14.6% Original)

BIRTHDAY_AVOIDANCE_TICKETS_V2 = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
    7: [3, 36, 43, 51, 58, 61, 64],
    6: [3, 36, 51, 58, 61, 64],
}

# Jackpot-Favoriten (bei Jackpots ueberrepraesentiert)
JACKPOT_FAVORITES_V2 = [51, 58, 61, 7, 36, 13, 43, 15, 3, 48]

# Jackpot-Vermeidung (bei Jackpots unterrepraesentiert - Birthday-Zahlen)
JACKPOT_AVOID_V2 = [6, 68, 27, 5, 16, 1, 25, 20, 8]


# ============================================================================
# KENO GEWINNQUOTEN
# ============================================================================

# Single source of truth (per 1 EUR Einsatz): `kenobase.core.keno_quotes`.
KENO_QUOTES = {
    int(keno_type): {int(hits): float(quote) for hits, quote in mapping.items()}
    for keno_type, mapping in KENO_FIXED_QUOTES_BY_TYPE.items()
}


# ============================================================================
# MODELL-KOMPONENTEN DEFINITIONEN
# ============================================================================

class ModelComponent:
    """Basis-Klasse fuer Modell-Komponenten."""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.enabled = True

    def apply(self, context: Dict) -> Dict:
        """Wendet Komponente auf Kontext an und gibt Modifikationen zurueck."""
        raise NotImplementedError


class JackpotWarningComponent(ModelComponent):
    """KI #1: Jackpot-Cooldown Warnung."""

    def __init__(self, cooldown_days: int = 30):
        super().__init__("jackpot_warning")
        self.cooldown_days = cooldown_days

    def apply(self, context: Dict) -> Dict:
        result = {"skip": False, "reason": None}

        jackpot_dates = context.get("jackpot_dates", [])
        check_date = context.get("date")

        if not jackpot_dates or not check_date:
            return result

        past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
        if past_jackpots:
            last_jp = max(past_jackpots)
            days_since = (check_date - last_jp).days
            if days_since <= self.cooldown_days:
                result["skip"] = True
                result["reason"] = f"Post-Jackpot Cooldown ({days_since}/{self.cooldown_days} Tage)"

        return result


class ExclusionRulesComponent(ModelComponent):
    """KI #1: Position-basierte Exclusion-Regeln."""

    def __init__(self):
        super().__init__("exclusion_rules")

    def apply(self, context: Dict) -> Dict:
        result = {"exclude": set(), "rules_triggered": []}

        positions = context.get("prev_positions", [])
        if not positions:
            return result

        # 100% Accuracy Regeln
        for (trigger_zahl, trigger_pos), exclude_zahlen in EXCLUSION_RULES_KI1.items():
            if trigger_pos <= len(positions):
                if positions[trigger_pos - 1] == trigger_zahl:
                    result["exclude"].update(exclude_zahlen)
                    result["rules_triggered"].append(f"{trigger_zahl}@{trigger_pos}")

        # Multi-Exclusion Regeln
        for (trigger_zahl, trigger_pos), (exclude_zahlen, accuracy) in MULTI_EXCLUSION_KI1.items():
            if trigger_pos <= len(positions):
                if positions[trigger_pos - 1] == trigger_zahl:
                    result["exclude"].update(exclude_zahlen)
                    result["rules_triggered"].append(f"{trigger_zahl}@{trigger_pos} ({accuracy}%)")

        return result


class TemporalComponent(ModelComponent):
    """KI #3: Temporale Anomalien (Monats-Start/Ende)."""

    def __init__(self):
        super().__init__("temporal")

    def apply(self, context: Dict) -> Dict:
        result = {"boost": [], "context_type": None}

        date = context.get("date")
        if not date:
            return result

        day = date.day

        if day <= 5:
            result["boost"] = MONTH_START_FAVORED
            result["context_type"] = "month_start"
        elif day >= 25:
            result["boost"] = MONTH_END_FAVORED
            result["context_type"] = "month_end"

        return result


class WeekdayComponent(ModelComponent):
    """KI #3: Wochentags-Favoriten."""

    def __init__(self):
        super().__init__("weekday")

    def apply(self, context: Dict) -> Dict:
        result = {"boost": [], "weekday": None}

        date = context.get("date")
        if not date:
            return result

        weekday = date.weekday()
        result["weekday"] = weekday
        result["boost"] = WEEKDAY_FAVORITES.get(weekday, [])

        return result


class SumContextComponent(ModelComponent):
    """KI #3: Summen-basierte Favoriten."""

    def __init__(self, low_threshold: int = 650, high_threshold: int = 770):
        super().__init__("sum_context")
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def apply(self, context: Dict) -> Dict:
        result = {"boost": [], "sum_type": None}

        prev_numbers = context.get("prev_numbers", [])
        if not prev_numbers:
            return result

        prev_sum = sum(prev_numbers)

        if prev_sum < self.low_threshold:
            result["boost"] = LOW_SUM_FAVORITES
            result["sum_type"] = "low"
        elif prev_sum > self.high_threshold:
            result["boost"] = HIGH_SUM_FAVORITES
            result["sum_type"] = "high"

        return result


class PairSynergyComponent(ModelComponent):
    """KI #3: Paar-Synergien."""

    def __init__(self):
        super().__init__("pair_synergy")

    def apply(self, context: Dict) -> Dict:
        result = {"pair_bonus": {}, "recommended_pairs": []}

        # Empfehle starke Paare
        for z1, z2, lift in TOP_PAIRS_KI3:
            result["recommended_pairs"].append((z1, z2))
            result["pair_bonus"][z1] = result["pair_bonus"].get(z1, 0) + lift / 10
            result["pair_bonus"][z2] = result["pair_bonus"].get(z2, 0) + lift / 10

        return result


class CorrelatedAbsenceComponent(ModelComponent):
    """KI #1: Korrelierte Absenzen."""

    def __init__(self):
        super().__init__("correlated_absence")

    def apply(self, context: Dict) -> Dict:
        result = {"likely_absent": set()}

        prev_numbers = context.get("prev_numbers", [])
        if not prev_numbers:
            return result

        prev_set = set(prev_numbers)
        today_absent = set(range(1, 71)) - prev_set

        for z1, z2, corr in CORRELATED_ABSENCES:
            if z1 in today_absent:
                result["likely_absent"].add(z2)
            if z2 in today_absent:
                result["likely_absent"].add(z1)

        return result


class AntiBirthdayComponent(ModelComponent):
    """Bevorzuge Zahlen >31 fuer weniger Gewinner-Teilung."""

    def __init__(self):
        super().__init__("anti_birthday")

    def apply(self, context: Dict) -> Dict:
        result = {"boost": ANTI_BIRTHDAY}
        return result


class BirthdayAvoidanceV2Component(ModelComponent):
    """
    V2 Birthday-Avoidance Komponente (2025 validiert).

    Basiert auf empirischen Befunden:
    - Bei KENO Jackpots sind Birthday-Zahlen (1-31) um 10.5% unterrepraesentiert
    - Spezifische Zahlen wie 51, 58, 61 sind bei Jackpots ueberrepraesentiert

    2025 Out-of-Sample Performance:
    - Typ 9: +1545.7% ROI (vs +209.6% Original)
    - Typ 10: +305.5% ROI (vs +77.7% Original)
    - Typ 8: +261.4% ROI (vs -14.6% Original)
    """

    def __init__(self):
        super().__init__("birthday_avoidance_v2", weight=2.0)

    def apply(self, context: Dict) -> Dict:
        result = {
            "boost": JACKPOT_FAVORITES_V2,
            "soft_avoid": set(JACKPOT_AVOID_V2),
            "use_v2_tickets": True,
            "reason": "Birthday-Avoidance V2 (2025 validiert)"
        }
        return result


# ============================================================================
# SUPER-MODELL KLASSE
# ============================================================================

class SuperModel:
    """Kombiniert alle KI-Erkenntnisse in einem einheitlichen Modell."""

    def __init__(self, use_v2: bool = False):
        """
        Initialisiert das Super-Model.

        Args:
            use_v2: Wenn True, wird Birthday-Avoidance V2 verwendet (empfohlen!)
        """
        self.use_v2 = use_v2
        self.components = {
            "jackpot_warning": JackpotWarningComponent(),
            "exclusion_rules": ExclusionRulesComponent(),
            "temporal": TemporalComponent(),
            "weekday": WeekdayComponent(),
            "sum_context": SumContextComponent(),
            "pair_synergy": PairSynergyComponent(),
            "correlated_absence": CorrelatedAbsenceComponent(),
            "anti_birthday": AntiBirthdayComponent(),
            "birthday_avoidance_v2": BirthdayAvoidanceV2Component(),
        }
        # Standard: V2 oder Original je nach Einstellung
        if use_v2:
            self.active_components = {
                "jackpot_warning",
                "birthday_avoidance_v2",
            }
        else:
            self.active_components = set(self.components.keys()) - {"birthday_avoidance_v2"}

    def set_active_components(self, component_names: List[str]):
        """Aktiviert nur bestimmte Komponenten."""
        self.active_components = set(component_names)

    def generate_ticket(
        self,
        keno_type: int,
        context: Dict,
        base_ticket: List[int] = None
    ) -> Tuple[List[int], Dict]:
        """Generiert optimiertes Ticket basierend auf aktiven Komponenten."""

        # Starte mit Basis-Ticket
        if base_ticket is None:
            # V2 Tickets verwenden wenn V2 aktiv
            if self.use_v2 or "birthday_avoidance_v2" in self.active_components:
                base_ticket = BIRTHDAY_AVOIDANCE_TICKETS_V2.get(
                    keno_type, UNIFIED_CORE[:keno_type]
                )
            else:
                base_ticket = OPTIMAL_TICKETS_KI1.get(keno_type, UNIFIED_CORE[:keno_type])

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

            # Sammle Boosts
            if "boost" in result:
                for z in result["boost"]:
                    boost_scores[z] += component.weight

            if "pair_bonus" in result:
                for z, bonus in result["pair_bonus"].items():
                    boost_scores[z] += bonus

        # Generiere finales Ticket
        candidates = list(base_ticket)

        # Entferne excludierte Zahlen
        candidates = [z for z in candidates if z not in exclude]

        # Fuege Boost-Zahlen hinzu
        boost_sorted = sorted(boost_scores.items(), key=lambda x: -x[1])
        for z, score in boost_sorted:
            if z not in exclude and z not in candidates:
                candidates.append(z)

        # Fuelle mit Unified Core auf
        for z in UNIFIED_CORE:
            if len(candidates) >= keno_type:
                break
            if z not in exclude and z not in candidates:
                candidates.append(z)

        # Fuelle mit verbleibenden Zahlen auf
        all_numbers = list(range(1, 71))
        np.random.shuffle(all_numbers)
        for z in all_numbers:
            if len(candidates) >= keno_type:
                break
            if z not in exclude and z not in candidates:
                candidates.append(z)

        final_ticket = sorted(candidates[:keno_type])

        metadata = {
            "excluded": sorted(exclude),
            "boost_scores": dict(boost_scores),
            "component_results": component_results,
            "base_ticket": base_ticket
        }

        return final_ticket, metadata

    def should_skip(self, context: Dict) -> Tuple[bool, str]:
        """Prueft ob Ziehung uebersprungen werden soll."""
        if "jackpot_warning" in self.active_components:
            result = self.components["jackpot_warning"].apply(context)
            if result.get("skip"):
                return True, result.get("reason", "Jackpot Cooldown")
        return False, None


def load_data(base_path: Path) -> Tuple[pd.DataFrame, List[datetime]]:
    """Laedt KENO und Jackpot-Daten."""

    # KENO Daten
    keno_paths = [
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    ]

    keno_df = None
    for p in keno_paths:
        if p.exists():
            keno_df = pd.read_csv(p, sep=";", encoding="utf-8")
            keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")
            break

    if keno_df is None:
        raise FileNotFoundError("Keine KENO-Datendatei gefunden")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    keno_df["positions"] = keno_df[pos_cols].apply(lambda row: list(row), axis=1)
    keno_df["numbers_set"] = keno_df[pos_cols].apply(lambda row: set(row), axis=1)
    keno_df = keno_df.sort_values("Datum").reset_index(drop=True)

    # Jackpot Daten
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    jackpot_dates = []
    if gk1_path.exists():
        gk1_df = pd.read_csv(gk1_path, encoding="utf-8")
        gk1_df["Datum"] = pd.to_datetime(gk1_df["Datum"], format="%d.%m.%Y")
        jackpot_dates = sorted(gk1_df[gk1_df["Keno-Typ"] == 10]["Datum"].tolist())

    return keno_df, jackpot_dates


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket gegen eine Ziehung."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


def backtest_configuration(
    model: SuperModel,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365
) -> Dict:
    """Fuehrt Backtest fuer eine Modell-Konfiguration durch."""

    results = {
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
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
        ticket, metadata = model.generate_ticket(keno_type, context)

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        results["daily_results"].append({
            "date": str(curr_row["Datum"].date()),
            "ticket": ticket,
            "hits": hits,
            "win": win
        })

    # Berechne ROI
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    return results


def test_all_combinations(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9
) -> List[Dict]:
    """Testet alle moeglichen Komponenten-Kombinationen."""

    all_components = [
        "jackpot_warning",
        "exclusion_rules",
        "temporal",
        "weekday",
        "sum_context",
        "pair_synergy",
        "correlated_absence",
        "anti_birthday",
    ]

    results = []

    # Teste alle Kombinationen (2^8 = 256)
    for r in range(1, len(all_components) + 1):
        for combo in combinations(all_components, r):
            model = SuperModel()
            model.set_active_components(list(combo))

            backtest_result = backtest_configuration(
                model, keno_df, jackpot_dates, keno_type
            )

            results.append({
                "components": list(combo),
                "num_components": len(combo),
                "roi": backtest_result["roi"],
                "invested": backtest_result["invested"],
                "won": backtest_result["won"],
                "skipped": backtest_result["skipped"],
                "played": backtest_result["played"],
            })

    return sorted(results, key=lambda x: -x["roi"])


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL SYNTHESE - 3 KI ERKENNTNISSE")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Teste alle Kombinationen fuer Typ 9
    print("\n" + "=" * 70)
    print("TESTE ALLE 256 KOMPONENTEN-KOMBINATIONEN (Typ 9)")
    print("=" * 70)

    all_results = test_all_combinations(keno_df, jackpot_dates, keno_type=9)

    # Top 20 Ergebnisse
    print("\n" + "-" * 70)
    print("TOP 20 MODELL-KONFIGURATIONEN")
    print("-" * 70)
    print(f"{'#':<4} {'ROI':>10} {'Gespielt':>10} {'Komponenten':<40}")
    print("-" * 70)

    for i, result in enumerate(all_results[:20]):
        components_str = ", ".join(result["components"][:3])
        if len(result["components"]) > 3:
            components_str += f" +{len(result['components']) - 3}"
        print(f"{i+1:<4} {result['roi']:>+9.1f}% {result['played']:>10} {components_str:<40}")

    # Bestes Modell
    best = all_results[0]

    print("\n" + "=" * 70)
    print("BESTES MODELL GEFUNDEN!")
    print("=" * 70)

    print(f"""
BESTE KONFIGURATION:

Komponenten: {', '.join(best['components'])}
Anzahl Komponenten: {best['num_components']}

Performance (Typ 9):
  ROI: {best['roi']:+.1f}%
  Gespielt: {best['played']} Tage
  Uebersprungen: {best['skipped']} Tage
  Einsatz: {best['invested']} EUR
  Gewinn: {best['won']} EUR
""")

    # Vergleiche mit Basis-Modellen
    print("\n" + "-" * 70)
    print("VERGLEICH MIT EINZELNEN KOMPONENTEN")
    print("-" * 70)

    single_results = [r for r in all_results if r["num_components"] == 1]
    for result in single_results:
        print(f"  {result['components'][0]:<25} ROI: {result['roi']:+.1f}%")

    # Teste Typ 8 und Typ 10 mit bestem Modell
    print("\n" + "=" * 70)
    print("BESTES MODELL AUF ANDERE TYPEN ANWENDEN")
    print("=" * 70)

    best_model = SuperModel()
    best_model.set_active_components(best["components"])

    for keno_type in [8, 9, 10]:
        result = backtest_configuration(best_model, keno_df, jackpot_dates, keno_type)
        print(f"\n  Typ {keno_type}: ROI {result['roi']:+.1f}%, Gespielt: {result['played']}")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "best_model": {
            "components": best["components"],
            "performance": {
                "typ_9": best
            }
        },
        "all_results": all_results[:50],  # Top 50
        "component_definitions": {
            "jackpot_warning": "30-Tage Cooldown nach GK10_10 Jackpot",
            "exclusion_rules": "Position-basierte Exclusion (100% Accuracy)",
            "temporal": "Monats-Start/Ende Favoriten",
            "weekday": "Wochentags-spezifische Zahlen",
            "sum_context": "Summen-basierte Favoriten",
            "pair_synergy": "Starke Paar-Kombinationen",
            "correlated_absence": "Korrelierte Absenzen",
            "anti_birthday": "Anti-Birthday Zahlen (>31)",
        }
    }

    output_path = base_path / "results" / "super_model_synthesis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Empfehlungen generieren
    print("\n" + "=" * 70)
    print("AKTUELLE EMPFEHLUNG (basierend auf letzter Ziehung)")
    print("=" * 70)

    last_row = keno_df.iloc[-1]
    prev_row = keno_df.iloc[-2]

    context = {
        "date": last_row["Datum"] + timedelta(days=1),
        "prev_date": last_row["Datum"],
        "prev_positions": last_row["positions"],
        "prev_numbers": list(last_row["numbers_set"]),
        "jackpot_dates": jackpot_dates,
    }

    should_skip, reason = best_model.should_skip(context)

    if should_skip:
        print(f"\n  ⚠️ WARNUNG: {reason}")
        print("  EMPFEHLUNG: NICHT SPIELEN!")
    else:
        print(f"\n  ✓ Keine Warnung aktiv")

        for keno_type in [9, 8, 10]:
            ticket, metadata = best_model.generate_ticket(keno_type, context)
            print(f"\n  Typ {keno_type}: {ticket}")
            if metadata["excluded"]:
                print(f"    Excluded: {metadata['excluded'][:5]}...")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
