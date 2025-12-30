#!/usr/bin/env python3
"""
SUPER-MODELL V2 - BIRTHDAY-SIGNAL STRATEGY

NEUER ANSATZ:
Statt Birthday-Avoidance im Ticket zu nutzen,
nutzen wir es als SIGNAL fuer Jackpot-Wahrscheinlichkeit.

HYPOTHESE:
- Bei Jackpots sind Birthday-Zahlen um 10.5% unterrepraesentiert
- UMKEHRSCHLUSS: Wenn die vorherige Ziehung wenig Birthday-Zahlen hatte,
  ist die Wahrscheinlichkeit hoeher, dass es ein "Jackpot-nahes" Event war
- Das System koennte nach solchen Events "resetten"

STRATEGIE:
- Analysiere Birthday-Ratio der letzten Ziehung
- Wenn niedrig (< 0.45): Potentielles Jackpot-Signal
- Bei Jackpot-Signal: Auf die Jackpot-Favoriten-Zahlen setzen

Autor: Kenobase V2.2 - Birthday-Signal Strategy
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

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
# KONSTANTEN
# ============================================================================

BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31
EXPECTED_BIRTHDAY_IN_20 = 20 * (31/70)  # ~8.86 von 20 Zahlen

# Jackpot-Favoriten (aus Analyse)
JACKPOT_FAVORITES = [51, 58, 61, 7, 36, 13, 43, 15, 3, 48]
JACKPOT_AVOID = [6, 68, 27, 5, 16, 1, 25, 20, 8]

# Tickets fuer verschiedene Modi
JACKPOT_OPTIMIZED_TICKETS = {
    10: [3, 7, 13, 15, 36, 43, 48, 51, 58, 61],
    9: [3, 7, 13, 36, 43, 48, 51, 58, 61],
    8: [3, 13, 36, 43, 48, 51, 58, 64],
}


# ============================================================================
# V2 KOMPONENTEN
# ============================================================================

class BirthdaySignalComponent(ModelComponent):
    """
    V2: Birthday-Signal als Jackpot-Indikator.

    Analysiert die Birthday-Ratio der letzten Ziehung:
    - Normal: 8-9 von 20 Zahlen sind Birthday (43-45%)
    - Niedrig: <8 Birthday-Zahlen -> Potentielles Jackpot-Signal
    - Hoch: >9 Birthday-Zahlen -> Kein Jackpot erwartet

    Bei niedrigem Birthday-Count: Wechsle zu Jackpot-Ticket
    """

    def __init__(self, low_threshold: float = 0.40, high_threshold: float = 0.50):
        super().__init__("birthday_signal_v2")
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def apply(self, context: Dict) -> Dict:
        result = {
            "birthday_ratio": None,
            "signal": "neutral",
            "ticket_mode": "normal",
            "reason": "Birthday-Signal V2"
        }

        prev_numbers = context.get("prev_numbers", [])
        if not prev_numbers:
            return result

        # Berechne Birthday-Ratio
        prev_set = set(prev_numbers)
        birthday_count = len(prev_set & BIRTHDAY_NUMBERS)
        birthday_ratio = birthday_count / len(prev_set)

        result["birthday_ratio"] = birthday_ratio
        result["birthday_count"] = birthday_count

        if birthday_ratio < self.low_threshold:
            # Wenig Birthday -> Potentielles Jackpot-Signal
            result["signal"] = "jackpot_likely"
            result["ticket_mode"] = "jackpot"
            result["reason"] = f"Low Birthday ({birthday_count}/20 = {birthday_ratio:.1%}) -> Jackpot-Mode"
        elif birthday_ratio > self.high_threshold:
            # Viel Birthday -> Kein Jackpot erwartet
            result["signal"] = "normal_draw"
            result["ticket_mode"] = "conservative"
            result["reason"] = f"High Birthday ({birthday_count}/20 = {birthday_ratio:.1%}) -> Conservative"
        else:
            result["signal"] = "neutral"
            result["ticket_mode"] = "normal"
            result["reason"] = f"Neutral Birthday ({birthday_count}/20 = {birthday_ratio:.1%})"

        return result


class ConsecutiveLowBirthdayComponent(ModelComponent):
    """
    V2: Zaehlt aufeinanderfolgende Ziehungen mit niedrigem Birthday-Count.

    Wenn mehrere Ziehungen hintereinander wenig Birthday haben,
    koennte das System in einem "Anti-Birthday" Modus sein.
    """

    def __init__(self, threshold: int = 7):
        super().__init__("consecutive_low_birthday_v2")
        self.threshold = threshold
        self.history = []

    def apply(self, context: Dict) -> Dict:
        result = {
            "consecutive_low": 0,
            "boost": [],
            "reason": "Consecutive Low Birthday V2"
        }

        prev_numbers = context.get("prev_numbers", [])
        if not prev_numbers:
            return result

        prev_set = set(prev_numbers)
        birthday_count = len(prev_set & BIRTHDAY_NUMBERS)

        if birthday_count <= self.threshold:
            self.history.append(True)
        else:
            self.history = []

        result["consecutive_low"] = len(self.history)

        if len(self.history) >= 2:
            # Zwei oder mehr aufeinanderfolgende niedrige Birthday-Ziehungen
            result["boost"] = JACKPOT_FAVORITES
            result["reason"] = f"Streak: {len(self.history)} niedrige Birthday-Ziehungen"

        return result


# ============================================================================
# SUPER-MODELL V2
# ============================================================================

class SuperModelV2:
    """
    Super-Model V2: Birthday-Signal Strategy.

    Nutzt Birthday-Ratio der letzten Ziehung als Signal:
    - Niedrig (<40%): Wechsle zu Jackpot-optimiertem Ticket
    - Normal (40-50%): Standard-Ticket
    - Hoch (>50%): Conservative Ticket (weniger Risiko)
    """

    VERSION = "V2"

    def __init__(self):
        self.components = {
            # Original-Komponenten
            "jackpot_warning": JackpotWarningComponent(),
            "exclusion_rules": ExclusionRulesComponent(),
            "temporal": TemporalComponent(),
            "weekday": WeekdayComponent(),
            "sum_context": SumContextComponent(),
            "pair_synergy": PairSynergyComponent(),
            "correlated_absence": CorrelatedAbsenceComponent(),
            "anti_birthday": AntiBirthdayComponent(),
            # V2 Komponenten
            "birthday_signal": BirthdaySignalComponent(),
            "consecutive_low": ConsecutiveLowBirthdayComponent(),
        }

        self.active_components = set(self.components.keys())

    def set_active_components(self, component_names: List[str]):
        self.active_components = set(component_names)

    def generate_ticket(
        self,
        keno_type: int,
        context: Dict,
        base_ticket: List[int] = None
    ) -> Tuple[List[int], Dict]:
        """
        Generiert Ticket basierend auf Birthday-Signal.

        Ticket-Modi:
        - "jackpot": Jackpot-optimiertes Ticket (wenn Birthday-Signal niedrig)
        - "normal": Standard OPTIMAL_TICKETS
        - "conservative": Sicheres Ticket (wenn Birthday-Signal hoch)
        """
        # Zuerst Birthday-Signal auswerten
        birthday_signal = self.components["birthday_signal"].apply(context)
        ticket_mode = birthday_signal.get("ticket_mode", "normal")

        # Waehle Basis-Ticket basierend auf Mode
        if ticket_mode == "jackpot":
            base_ticket = JACKPOT_OPTIMIZED_TICKETS.get(
                keno_type,
                OPTIMAL_TICKETS_KI1.get(keno_type, [])
            )
        elif ticket_mode == "conservative":
            # Conservative: Mehr niedrige Zahlen (hoehere Trefferchance, niedrigere Auszahlung)
            base_ticket = list(range(1, keno_type + 5))[:keno_type]
        else:
            base_ticket = OPTIMAL_TICKETS_KI1.get(keno_type, UNIFIED_CORE[:keno_type])

        # Sammle Modifikationen
        exclude = set()
        boost_scores = defaultdict(float)
        component_results = {}

        for name, component in self.components.items():
            if name not in self.active_components:
                continue

            result = component.apply(context)
            component_results[name] = result

            if "exclude" in result:
                exclude.update(result["exclude"])
            if "likely_absent" in result:
                exclude.update(result["likely_absent"])

            if "boost" in result:
                for z in result["boost"]:
                    boost_scores[z] += component.weight

            if "pair_bonus" in result:
                for z, bonus in result["pair_bonus"].items():
                    boost_scores[z] += bonus

        # Generiere finales Ticket
        candidates = [z for z in base_ticket if z not in exclude]

        # Fuege Boost-Zahlen hinzu
        boost_sorted = sorted(boost_scores.items(), key=lambda x: -x[1])
        for z, score in boost_sorted:
            if score > 0 and z not in exclude and z not in candidates:
                candidates.append(z)

        # Auffuellen
        for z in UNIFIED_CORE:
            if len(candidates) >= keno_type:
                break
            if z not in exclude and z not in candidates:
                candidates.append(z)

        # Zufaellig auffuellen
        all_numbers = list(range(1, 71))
        np.random.shuffle(all_numbers)
        for z in all_numbers:
            if len(candidates) >= keno_type:
                break
            if z not in exclude and z not in candidates:
                candidates.append(z)

        final_ticket = sorted(candidates[:keno_type])

        metadata = {
            "version": self.VERSION,
            "ticket_mode": ticket_mode,
            "birthday_signal": birthday_signal,
            "excluded": sorted(exclude),
            "component_results": component_results,
            "base_ticket": list(base_ticket) if base_ticket else [],
        }

        return final_ticket, metadata

    def should_skip(self, context: Dict) -> Tuple[bool, str]:
        if "jackpot_warning" in self.active_components:
            result = self.components["jackpot_warning"].apply(context)
            if result.get("skip"):
                return True, result.get("reason", "Jackpot Cooldown")
        return False, None


# ============================================================================
# BACKTEST
# ============================================================================

def backtest_v2(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365
) -> Dict:
    """Backtest fuer V2."""

    model = SuperModelV2()

    results = {
        "model_version": "V2",
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "mode_counts": defaultdict(int),
        "mode_wins": defaultdict(int),
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

        should_skip, reason = model.should_skip(context)
        if should_skip:
            results["skipped"] += 1
            continue

        ticket, metadata = model.generate_ticket(keno_type, context)
        ticket_mode = metadata.get("ticket_mode", "normal")

        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1
        results["mode_counts"][ticket_mode] += 1
        results["mode_wins"][ticket_mode] += win

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_row["Datum"].date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "mode": ticket_mode,
            })

    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    # ROI pro Mode
    results["mode_roi"] = {}
    for mode, count in results["mode_counts"].items():
        if count > 0:
            mode_win = results["mode_wins"][mode]
            results["mode_roi"][mode] = (mode_win - count) / count * 100

    return results


def compare_all(keno_df: pd.DataFrame, jackpot_dates: List[datetime]) -> Dict:
    """Vergleicht Original mit V2."""

    from super_model_synthesis import SuperModel

    comparison = {
        "analysis_date": datetime.now().isoformat(),
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

            if win >= 100:
                orig_results["high_wins"].append({"win": win})

        orig_roi = (orig_results["won"] - orig_results["invested"]) / orig_results["invested"] * 100

        # V2
        v2_results = backtest_v2(keno_df, jackpot_dates, keno_type)

        comparison["results"][f"typ_{keno_type}"] = {
            "original": {
                "roi": orig_roi,
                "played": orig_results["played"],
                "won": orig_results["won"],
                "high_wins": len(orig_results["high_wins"]),
            },
            "v2": {
                "roi": v2_results["roi"],
                "played": v2_results["played"],
                "won": v2_results["won"],
                "high_wins": len(v2_results["high_wins"]),
                "mode_distribution": dict(v2_results["mode_counts"]),
                "mode_roi": v2_results["mode_roi"],
            }
        }

        delta = v2_results["roi"] - orig_roi

        print(f"\nOriginal: ROI {orig_roi:+.1f}%, High-Wins: {len(orig_results['high_wins'])}")
        print(f"V2:       ROI {v2_results['roi']:+.1f}%, High-Wins: {len(v2_results['high_wins'])}")
        print(f"\nMode-Verteilung:")
        for mode, count in v2_results["mode_counts"].items():
            roi = v2_results["mode_roi"].get(mode, 0)
            print(f"  {mode:12s}: {count:4d} Spiele, ROI {roi:+.1f}%")
        print(f"\nDelta V2 vs Original: {delta:+.1f}%")

    return comparison


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL V2 - BIRTHDAY-SIGNAL STRATEGY")
    print("=" * 70)
    print()
    print("KONZEPT:")
    print("  Die Birthday-Ratio der letzten Ziehung als Signal nutzen.")
    print("  - Niedrig (<40%): Jackpot-optimiertes Ticket")
    print("  - Normal (40-50%): Standard-Ticket")
    print("  - Hoch (>50%): Conservative Ticket")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Birthday-Ratio Verteilung analysieren
    print("\n" + "-" * 60)
    print("BIRTHDAY-RATIO VERTEILUNG (historisch)")
    print("-" * 60)

    ratios = []
    for i in range(len(keno_df)):
        numbers = keno_df.iloc[i]["numbers_set"]
        birthday_count = len(numbers & BIRTHDAY_NUMBERS)
        ratios.append(birthday_count / 20)

    ratios = np.array(ratios)
    print(f"  Mean: {ratios.mean():.1%}")
    print(f"  Std:  {ratios.std():.1%}")
    print(f"  Min:  {ratios.min():.1%}")
    print(f"  Max:  {ratios.max():.1%}")
    print(f"  <40%: {(ratios < 0.40).sum()} Ziehungen ({(ratios < 0.40).mean():.1%})")
    print(f"  >50%: {(ratios > 0.50).sum()} Ziehungen ({(ratios > 0.50).mean():.1%})")

    # Vergleich
    comparison = compare_all(keno_df, jackpot_dates)

    # Speichern
    output_path = base_path / "results" / "super_model_v2_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Empfehlung
    print("\n" + "=" * 70)
    print("V2 TICKET-EMPFEHLUNG")
    print("=" * 70)

    model = SuperModelV2()
    last_row = keno_df.iloc[-1]

    # Letzte Birthday-Ratio
    last_birthday = len(last_row["numbers_set"] & BIRTHDAY_NUMBERS)
    print(f"\nLetzte Ziehung: {last_birthday}/20 Birthday ({last_birthday/20:.1%})")

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
            mode = metadata.get("ticket_mode", "normal")

            print(f"\n  Typ {keno_type} (Mode: {mode.upper()}):")
            print(f"    Ticket: {ticket}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
