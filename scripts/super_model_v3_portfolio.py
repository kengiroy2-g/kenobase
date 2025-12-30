#!/usr/bin/env python3
"""
SUPER-MODELL V3 - PORTFOLIO STRATEGY

KONZEPT:
Statt einer einzigen Strategie fuer alle Situationen,
verwenden wir SPEZIALISIERTE Strategien parallel:

1. SMALL-WINS Strategie (Typ 2-4):
   - Hohe Trefferquote, niedrige Gewinne
   - Birthday-Zahlen OK (viele Spieler = geteilte kleine Gewinne sind egal)
   - Ziel: Konsistente kleine Gewinne

2. MEDIUM-WINS Strategie (Typ 5-7):
   - Balance zwischen Treffer und Gewinn
   - Original-Optimierung funktioniert hier gut
   - Ziel: Stabiler positiver ROI

3. JACKPOT Strategie (Typ 8-10):
   - Birthday-Avoidance AKTIV (weniger Gewinner-Teilung bei grossen Gewinnen)
   - Jackpot-Favoriten bevorzugen
   - Ziel: Maximale Auszahlung wenn Treffer

4. LOTTO Strategie (6aus49):
   - Andere Logik als KENO (Birthday NICHT vermieden bei Jackpots)
   - Eigene Optimierung noetig

BUDGET-ALLOKATION:
- Taeglich X EUR Budget
- Aufgeteilt auf verschiedene Strategien
- Gewichtung basierend auf erwarteter Performance

Autor: Kenobase V2.2 - Portfolio Strategy
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

BIRTHDAY_NUMBERS = set(range(1, 32))
HIGH_NUMBERS = set(range(32, 71))

# Jackpot-Favoriten (aus Analyse)
JACKPOT_FAVORITES = [51, 58, 61, 7, 36, 13, 43, 15, 3, 48]
JACKPOT_AVOID = [6, 68, 27, 5, 16, 1, 25, 20, 8]

# Spezialisierte Tickets pro Strategie
SMALL_WIN_TICKETS = {
    2: [7, 49],
    3: [7, 13, 49],
    4: [3, 7, 13, 49],
}

MEDIUM_WIN_TICKETS = {
    5: [3, 9, 24, 49, 64],
    6: [3, 9, 10, 32, 49, 64],
    7: [3, 24, 30, 49, 51, 59, 64],
}

JACKPOT_TICKETS = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}


# ============================================================================
# SPEZIALISIERTE STRATEGIEN
# ============================================================================

@dataclass
class StrategyResult:
    """Ergebnis einer Strategie-Anwendung."""
    ticket: List[int]
    keno_type: int
    strategy_name: str
    confidence: float
    metadata: Dict = field(default_factory=dict)


class BaseStrategy:
    """Basis-Klasse fuer Strategien."""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    def should_play(self, context: Dict) -> Tuple[bool, str]:
        """Prueft ob Strategie heute spielen soll."""
        return True, "OK"

    def generate_tickets(self, context: Dict) -> List[StrategyResult]:
        """Generiert Tickets fuer diese Strategie."""
        raise NotImplementedError


class SmallWinsStrategy(BaseStrategy):
    """
    Strategie fuer kleine, konsistente Gewinne (Typ 2-4).

    Logik:
    - Hohe Trefferwahrscheinlichkeit
    - Birthday-Zahlen sind OK (Teilung bei kleinen Gewinnen egal)
    - Fokus auf "sichere" Zahlen mit hoher Frequenz
    """

    def __init__(self):
        super().__init__("small_wins")
        self.types = [2, 3, 4]

    def generate_tickets(self, context: Dict) -> List[StrategyResult]:
        results = []

        for keno_type in self.types:
            base = SMALL_WIN_TICKETS.get(keno_type, list(range(1, keno_type + 1)))

            # Kleine Anpassungen basierend auf Kontext
            ticket = list(base)

            # Wochentags-Bonus
            date = context.get("date")
            if date:
                weekday = date.weekday()
                # Montag/Dienstag: 9, 10 sind stark
                if weekday in [0, 1] and keno_type >= 3:
                    if 9 not in ticket:
                        ticket[-1] = 9

            results.append(StrategyResult(
                ticket=sorted(ticket[:keno_type]),
                keno_type=keno_type,
                strategy_name=self.name,
                confidence=0.7,
                metadata={"focus": "consistency"}
            ))

        return results


class MediumWinsStrategy(BaseStrategy):
    """
    Strategie fuer mittlere Gewinne (Typ 5-7).

    Logik:
    - Balance zwischen Treffer und Auszahlung
    - Original OPTIMAL_TICKETS funktionieren hier gut
    - Exclusion-Regeln anwenden
    """

    def __init__(self):
        super().__init__("medium_wins")
        self.types = [5, 6, 7]
        self.exclusion = ExclusionRulesComponent()
        self.temporal = TemporalComponent()

    def generate_tickets(self, context: Dict) -> List[StrategyResult]:
        results = []

        # Sammle Exclusions
        excl_result = self.exclusion.apply(context)
        exclude = excl_result.get("exclude", set())

        # Temporale Boosts
        temp_result = self.temporal.apply(context)
        boost = temp_result.get("boost", [])

        for keno_type in self.types:
            base = MEDIUM_WIN_TICKETS.get(
                keno_type,
                OPTIMAL_TICKETS_KI1.get(keno_type, [])
            )

            ticket = [z for z in base if z not in exclude]

            # Boost-Zahlen hinzufuegen
            for z in boost:
                if z not in ticket and z not in exclude and len(ticket) < keno_type:
                    ticket.append(z)

            # Auffuellen
            for z in UNIFIED_CORE:
                if len(ticket) >= keno_type:
                    break
                if z not in ticket and z not in exclude:
                    ticket.append(z)

            results.append(StrategyResult(
                ticket=sorted(ticket[:keno_type]),
                keno_type=keno_type,
                strategy_name=self.name,
                confidence=0.8,
                metadata={"focus": "balance", "excluded": list(exclude)}
            ))

        return results


class JackpotStrategy(BaseStrategy):
    """
    Strategie fuer Jackpots (Typ 8-10).

    Logik:
    - Birthday-Avoidance AKTIV (Teilung bei grossen Gewinnen vermeiden)
    - Jackpot-Favoriten bevorzugen
    - Nur spielen wenn kein Jackpot-Cooldown
    """

    def __init__(self, cooldown_days: int = 30):
        super().__init__("jackpot")
        self.types = [8, 9, 10]
        self.cooldown_days = cooldown_days

    def should_play(self, context: Dict) -> Tuple[bool, str]:
        """Jackpot-Cooldown pruefen."""
        jackpot_dates = context.get("jackpot_dates", [])
        check_date = context.get("date")

        if not jackpot_dates or not check_date:
            return True, "No jackpot data"

        past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
        if past_jackpots:
            last_jp = max(past_jackpots)
            days_since = (check_date - last_jp).days
            if days_since <= self.cooldown_days:
                return False, f"Jackpot-Cooldown ({days_since}/{self.cooldown_days} Tage)"

        return True, "OK"

    def generate_tickets(self, context: Dict) -> List[StrategyResult]:
        results = []

        should_play, reason = self.should_play(context)
        if not should_play:
            # Keine Tickets wenn Cooldown
            return results

        for keno_type in self.types:
            # Jackpot-optimierte Tickets
            base = JACKPOT_TICKETS.get(keno_type, [])

            ticket = list(base)

            # Stelle sicher dass Jackpot-Favoriten drin sind
            for z in JACKPOT_FAVORITES[:5]:
                if z not in ticket and len(ticket) < keno_type:
                    ticket.append(z)

            # Entferne Jackpot-Avoid Zahlen
            ticket = [z for z in ticket if z not in JACKPOT_AVOID]

            # Auffuellen mit hohen Zahlen
            for z in sorted(HIGH_NUMBERS):
                if len(ticket) >= keno_type:
                    break
                if z not in ticket:
                    ticket.append(z)

            results.append(StrategyResult(
                ticket=sorted(ticket[:keno_type]),
                keno_type=keno_type,
                strategy_name=self.name,
                confidence=0.6,  # Niedriger weil Jackpots selten
                metadata={"focus": "jackpot", "birthday_avoidance": True}
            ))

        return results


class OriginalStrategy(BaseStrategy):
    """
    Original Super-Model Strategie (als Vergleich).

    Verwendet die bewaehrten OPTIMAL_TICKETS fuer alle Typen.
    """

    def __init__(self):
        super().__init__("original")
        self.types = [8, 9, 10]
        self.jackpot_warning = JackpotWarningComponent()

    def should_play(self, context: Dict) -> Tuple[bool, str]:
        result = self.jackpot_warning.apply(context)
        if result.get("skip"):
            return False, result.get("reason", "Cooldown")
        return True, "OK"

    def generate_tickets(self, context: Dict) -> List[StrategyResult]:
        results = []

        should_play, reason = self.should_play(context)
        if not should_play:
            return results

        for keno_type in self.types:
            ticket = OPTIMAL_TICKETS_KI1.get(keno_type, UNIFIED_CORE[:keno_type])

            results.append(StrategyResult(
                ticket=sorted(list(ticket)),
                keno_type=keno_type,
                strategy_name=self.name,
                confidence=0.85,
                metadata={"focus": "proven_performance"}
            ))

        return results


# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

@dataclass
class PortfolioConfig:
    """Konfiguration fuer Portfolio-Allokation."""
    daily_budget: float = 10.0  # EUR pro Tag
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        "small_wins": 0.2,   # 20% Budget
        "medium_wins": 0.3,  # 30% Budget
        "jackpot": 0.25,     # 25% Budget
        "original": 0.25,    # 25% Budget
    })
    min_bet: float = 1.0  # Minimum pro Ticket


class PortfolioManager:
    """
    Verwaltet ein Portfolio von Strategien.

    Generiert taeglich Tickets aus allen aktiven Strategien
    und allokiert Budget entsprechend der Gewichtung.
    """

    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()

        self.strategies = {
            "small_wins": SmallWinsStrategy(),
            "medium_wins": MediumWinsStrategy(),
            "jackpot": JackpotStrategy(),
            "original": OriginalStrategy(),
        }

    def generate_daily_portfolio(self, context: Dict) -> Dict[str, List[StrategyResult]]:
        """
        Generiert das taegliche Ticket-Portfolio.

        Returns:
            Dict mit Strategy-Name als Key und Liste von StrategyResults als Value
        """
        portfolio = {}

        for name, strategy in self.strategies.items():
            if not strategy.enabled:
                continue

            weight = self.config.strategy_weights.get(name, 0)
            if weight <= 0:
                continue

            should_play, reason = strategy.should_play(context)
            if not should_play:
                portfolio[name] = []
                continue

            tickets = strategy.generate_tickets(context)
            portfolio[name] = tickets

        return portfolio

    def allocate_budget(self, portfolio: Dict[str, List[StrategyResult]]) -> Dict[str, float]:
        """
        Allokiert Budget auf die Strategien.

        Returns:
            Dict mit Strategy-Name als Key und Budget als Value
        """
        allocation = {}
        total_weight = 0

        # Berechne aktive Gewichte
        for name, tickets in portfolio.items():
            if tickets:
                weight = self.config.strategy_weights.get(name, 0)
                allocation[name] = weight
                total_weight += weight

        # Normalisiere auf Gesamt-Budget
        if total_weight > 0:
            for name in allocation:
                allocation[name] = (allocation[name] / total_weight) * self.config.daily_budget

        return allocation


# ============================================================================
# BACKTEST
# ============================================================================

def backtest_portfolio(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    config: PortfolioConfig = None,
    start_idx: int = 365
) -> Dict:
    """Backtest des Portfolio-Ansatzes."""

    manager = PortfolioManager(config)

    results = {
        "config": {
            "daily_budget": manager.config.daily_budget,
            "weights": manager.config.strategy_weights,
        },
        "total_invested": 0,
        "total_won": 0,
        "days_played": 0,
        "strategy_results": defaultdict(lambda: {
            "invested": 0, "won": 0, "played": 0,
            "hits_by_type": defaultdict(lambda: defaultdict(int)),
            "high_wins": []
        }),
        "daily_log": []
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

        # Generiere Portfolio
        portfolio = manager.generate_daily_portfolio(context)
        budget_allocation = manager.allocate_budget(portfolio)

        day_invested = 0
        day_won = 0
        day_log = {"date": str(curr_row["Datum"].date()), "tickets": []}

        draw_set = curr_row["numbers_set"]

        for strategy_name, tickets in portfolio.items():
            strategy_budget = budget_allocation.get(strategy_name, 0)

            if not tickets or strategy_budget < manager.config.min_bet:
                continue

            # Budget pro Ticket dieser Strategie
            budget_per_ticket = strategy_budget / len(tickets)

            for ticket_result in tickets:
                if budget_per_ticket < manager.config.min_bet:
                    continue

                ticket = ticket_result.ticket
                keno_type = ticket_result.keno_type

                # Simuliere
                win, hits = simulate_ticket(ticket, keno_type, draw_set)

                # Skaliere Gewinn mit Einsatz (KENO: Gewinn proportional zu Einsatz)
                bet = min(budget_per_ticket, 10.0)  # Max 10 EUR pro Ticket
                scaled_win = win * bet  # KENO Gewinne sind fuer 1 EUR Einsatz

                day_invested += bet
                day_won += scaled_win

                # Tracking
                sr = results["strategy_results"][strategy_name]
                sr["invested"] += bet
                sr["won"] += scaled_win
                sr["played"] += 1
                sr["hits_by_type"][keno_type][hits] += 1

                if scaled_win >= 100:
                    sr["high_wins"].append({
                        "date": str(curr_row["Datum"].date()),
                        "ticket": ticket,
                        "keno_type": keno_type,
                        "hits": hits,
                        "win": scaled_win,
                        "bet": bet
                    })

                day_log["tickets"].append({
                    "strategy": strategy_name,
                    "type": keno_type,
                    "ticket": ticket,
                    "hits": hits,
                    "bet": bet,
                    "win": scaled_win
                })

        results["total_invested"] += day_invested
        results["total_won"] += day_won
        results["days_played"] += 1
        results["daily_log"].append(day_log)

    # Berechne ROIs
    if results["total_invested"] > 0:
        results["total_roi"] = (results["total_won"] - results["total_invested"]) / results["total_invested"] * 100
    else:
        results["total_roi"] = 0

    for name, sr in results["strategy_results"].items():
        if sr["invested"] > 0:
            sr["roi"] = (sr["won"] - sr["invested"]) / sr["invested"] * 100
        else:
            sr["roi"] = 0

    return results


def compare_portfolio_vs_single(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime]
) -> Dict:
    """Vergleicht Portfolio-Ansatz mit Einzel-Strategien."""

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "results": {}
    }

    # 1. Nur Original (wie bisher)
    print("\n" + "=" * 60)
    print("1. NUR ORIGINAL STRATEGIE")
    print("=" * 60)

    original_config = PortfolioConfig(
        daily_budget=10.0,
        strategy_weights={"original": 1.0}
    )
    original_results = backtest_portfolio(keno_df, jackpot_dates, original_config)

    comparison["results"]["original_only"] = {
        "roi": original_results["total_roi"],
        "invested": original_results["total_invested"],
        "won": original_results["total_won"],
    }
    print(f"ROI: {original_results['total_roi']:+.1f}%")
    print(f"Investiert: {original_results['total_invested']:.0f} EUR")
    print(f"Gewonnen: {original_results['total_won']:.0f} EUR")

    # 2. Nur Jackpot-Strategie
    print("\n" + "=" * 60)
    print("2. NUR JACKPOT STRATEGIE")
    print("=" * 60)

    jackpot_config = PortfolioConfig(
        daily_budget=10.0,
        strategy_weights={"jackpot": 1.0}
    )
    jackpot_results = backtest_portfolio(keno_df, jackpot_dates, jackpot_config)

    comparison["results"]["jackpot_only"] = {
        "roi": jackpot_results["total_roi"],
        "invested": jackpot_results["total_invested"],
        "won": jackpot_results["total_won"],
    }
    print(f"ROI: {jackpot_results['total_roi']:+.1f}%")
    print(f"Investiert: {jackpot_results['total_invested']:.0f} EUR")
    print(f"Gewonnen: {jackpot_results['total_won']:.0f} EUR")

    # 3. Portfolio: Original + Jackpot parallel
    print("\n" + "=" * 60)
    print("3. PORTFOLIO: ORIGINAL + JACKPOT (50/50)")
    print("=" * 60)

    mixed_config = PortfolioConfig(
        daily_budget=10.0,
        strategy_weights={"original": 0.5, "jackpot": 0.5}
    )
    mixed_results = backtest_portfolio(keno_df, jackpot_dates, mixed_config)

    comparison["results"]["original_jackpot_50_50"] = {
        "roi": mixed_results["total_roi"],
        "invested": mixed_results["total_invested"],
        "won": mixed_results["total_won"],
        "strategy_breakdown": {
            name: {"roi": sr["roi"], "invested": sr["invested"], "won": sr["won"]}
            for name, sr in mixed_results["strategy_results"].items()
        }
    }
    print(f"Gesamt-ROI: {mixed_results['total_roi']:+.1f}%")
    for name, sr in mixed_results["strategy_results"].items():
        print(f"  {name}: ROI {sr['roi']:+.1f}%, Investiert: {sr['invested']:.0f} EUR")

    # 4. Volles Portfolio (alle Strategien)
    print("\n" + "=" * 60)
    print("4. VOLLES PORTFOLIO (alle Strategien)")
    print("=" * 60)

    full_config = PortfolioConfig(
        daily_budget=10.0,
        strategy_weights={
            "small_wins": 0.15,
            "medium_wins": 0.25,
            "jackpot": 0.30,
            "original": 0.30,
        }
    )
    full_results = backtest_portfolio(keno_df, jackpot_dates, full_config)

    comparison["results"]["full_portfolio"] = {
        "roi": full_results["total_roi"],
        "invested": full_results["total_invested"],
        "won": full_results["total_won"],
        "strategy_breakdown": {
            name: {"roi": sr["roi"], "invested": sr["invested"], "won": sr["won"]}
            for name, sr in full_results["strategy_results"].items()
        }
    }
    print(f"Gesamt-ROI: {full_results['total_roi']:+.1f}%")
    for name, sr in full_results["strategy_results"].items():
        print(f"  {name}: ROI {sr['roi']:+.1f}%, Investiert: {sr['invested']:.0f} EUR")

    # 5. Optimiertes Portfolio (basierend auf Typ-Spezialisierung)
    print("\n" + "=" * 60)
    print("5. OPTIMIERTES PORTFOLIO (typ-spezialisiert)")
    print("=" * 60)

    # Original fuer Typ 9 (bester ROI), Jackpot fuer Typ 10
    optimized_config = PortfolioConfig(
        daily_budget=10.0,
        strategy_weights={
            "small_wins": 0.10,
            "medium_wins": 0.20,
            "jackpot": 0.35,  # Mehr fuer Jackpot
            "original": 0.35,
        }
    )
    optimized_results = backtest_portfolio(keno_df, jackpot_dates, optimized_config)

    comparison["results"]["optimized_portfolio"] = {
        "roi": optimized_results["total_roi"],
        "invested": optimized_results["total_invested"],
        "won": optimized_results["total_won"],
        "strategy_breakdown": {
            name: {"roi": sr["roi"], "invested": sr["invested"], "won": sr["won"]}
            for name, sr in optimized_results["strategy_results"].items()
        }
    }
    print(f"Gesamt-ROI: {optimized_results['total_roi']:+.1f}%")
    for name, sr in optimized_results["strategy_results"].items():
        print(f"  {name}: ROI {sr['roi']:+.1f}%, Investiert: {sr['invested']:.0f} EUR")

    return comparison


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL V3 - PORTFOLIO STRATEGY")
    print("=" * 70)
    print()
    print("KONZEPT:")
    print("  Mehrere spezialisierte Strategien parallel verfolgen:")
    print("  - Small-Wins (Typ 2-4): Konsistente kleine Gewinne")
    print("  - Medium-Wins (Typ 5-7): Balance")
    print("  - Jackpot (Typ 8-10): Birthday-Avoidance fuer grosse Gewinne")
    print("  - Original (Typ 8-10): Bewaehrte OPTIMAL_TICKETS")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Vergleich
    comparison = compare_portfolio_vs_single(keno_df, jackpot_dates)

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    print("\n{:<30} {:>12} {:>15} {:>12}".format(
        "Strategie", "ROI", "Investiert", "Gewonnen"
    ))
    print("-" * 70)

    for name, data in comparison["results"].items():
        print("{:<30} {:>+11.1f}% {:>14.0f} {:>11.0f}".format(
            name, data["roi"], data["invested"], data["won"]
        ))

    # Speichern
    output_path = base_path / "results" / "super_model_v3_portfolio.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Beste Konfiguration empfehlen
    best = max(comparison["results"].items(), key=lambda x: x[1]["roi"])
    print(f"\nBESTE KONFIGURATION: {best[0]} (ROI: {best[1]['roi']:+.1f}%)")


if __name__ == "__main__":
    main()
