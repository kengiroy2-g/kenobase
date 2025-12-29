#!/usr/bin/env python
"""
Anti-Birthday Strategie fuer KENO.

Basiert auf der bestaetigen Hypothese HYP-004/HYP-010:
- Korrelation r=0.3921 zwischen Birthday-Score und Gewinner-Anzahl
- 30% mehr Gewinner bei Birthday-lastigen Ziehungen (1-31)
- Strategie: Bevorzuge Zahlen 32-70 fuer weniger Konkurrenz

Wissenschaftliche Grundlage:
- Menschen waehlen bevorzugt Geburtstage (1-31)
- Wenn "unbeliebte" Zahlen (32-70) gezogen werden -> weniger Mitspieler
- Bei Gewinn: Hoeherer individueller Anteil
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

import numpy as np


# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31
NON_BIRTHDAY_NUMBERS = set(range(32, 71))  # 32-70
ALL_KENO_NUMBERS = set(range(1, 71))  # 1-70


@dataclass
class AntiBirthdayResult:
    """Ergebnis der Anti-Birthday Strategie."""

    numbers: list[int]  # Ausgewaehlte Zahlen
    anti_birthday_score: float  # Anteil Nicht-Birthday-Zahlen (0-1)
    expected_competition_reduction: float  # Erwartete Konkurrenz-Reduktion
    keno_type: int  # KENO-Typ (2-10)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Konvertiere zu Dictionary."""
        return {
            "numbers": self.numbers,
            "anti_birthday_score": round(self.anti_birthday_score, 4),
            "expected_competition_reduction": round(self.expected_competition_reduction, 4),
            "keno_type": self.keno_type,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class AntiBirthdayStrategy:
    """Anti-Birthday Strategie fuer KENO Zahlenauswahl."""

    # Strategie-Parameter
    min_anti_birthday_ratio: float = 0.6  # Mindestens 60% Nicht-Birthday
    prefer_high_numbers: bool = True  # Bevorzuge hohe Zahlen (50-70)
    avoid_patterns: bool = True  # Vermeide offensichtliche Muster

    # Korrelations-Daten (aus Analyse)
    birthday_correlation: float = 0.3921
    winner_ratio: float = 1.3  # High-Birthday hat 1.3x mehr Gewinner

    def calculate_anti_birthday_score(self, numbers: list[int]) -> float:
        """
        Berechne Anti-Birthday-Score.

        Args:
            numbers: Liste von KENO-Zahlen

        Returns:
            Score 0-1 (1 = alle Nicht-Birthday-Zahlen)
        """
        if not numbers:
            return 0.0
        non_birthday_count = sum(1 for n in numbers if n in NON_BIRTHDAY_NUMBERS)
        return non_birthday_count / len(numbers)

    def calculate_expected_reduction(self, anti_birthday_score: float) -> float:
        """
        Berechne erwartete Konkurrenz-Reduktion.

        Basiert auf Winner-Ratio 1.3x:
        - Bei 100% Birthday-Zahlen: 1.3x mehr Konkurrenz
        - Bei 100% Nicht-Birthday: Baseline Konkurrenz
        - Linear interpoliert

        Args:
            anti_birthday_score: Anti-Birthday Score (0-1)

        Returns:
            Erwartete Reduktion (0 = keine, 0.23 = 23% weniger Konkurrenz)
        """
        # Winner-Ratio bei Birthday-lastigen Ziehungen: 1.3x
        # Bei Anti-Birthday: 1/1.3 = 0.77x = 23% weniger Konkurrenz
        max_reduction = 1 - (1 / self.winner_ratio)  # 0.23
        return anti_birthday_score * max_reduction

    def generate_numbers(
        self,
        keno_type: int = 6,
        seed: Optional[int] = None
    ) -> AntiBirthdayResult:
        """
        Generiere Anti-Birthday optimierte Zahlen.

        Args:
            keno_type: Anzahl zu waehlender Zahlen (2-10)
            seed: Optional seed fuer Reproduzierbarkeit

        Returns:
            AntiBirthdayResult mit optimierten Zahlen
        """
        if seed is not None:
            random.seed(seed)

        # Berechne Mindestanzahl Nicht-Birthday-Zahlen
        min_non_birthday = int(np.ceil(keno_type * self.min_anti_birthday_ratio))

        # Waehle Nicht-Birthday-Zahlen
        non_birthday_pool = list(NON_BIRTHDAY_NUMBERS)

        # Optionale Praeferenz fuer hohe Zahlen
        if self.prefer_high_numbers:
            # Gewichte hohe Zahlen (50-70) staerker
            weights = []
            for n in non_birthday_pool:
                if n >= 50:
                    weights.append(2.0)
                elif n >= 40:
                    weights.append(1.5)
                else:
                    weights.append(1.0)
            # Normalisiere
            total = sum(weights)
            weights = [w / total for w in weights]
            non_birthday_selected = list(np.random.choice(
                non_birthday_pool,
                size=min(min_non_birthday, len(non_birthday_pool)),
                replace=False,
                p=weights
            ))
        else:
            non_birthday_selected = random.sample(
                non_birthday_pool,
                min(min_non_birthday, len(non_birthday_pool))
            )

        # Restliche Zahlen zufaellig auffuellen
        remaining_count = keno_type - len(non_birthday_selected)
        remaining_pool = list(ALL_KENO_NUMBERS - set(non_birthday_selected))

        if remaining_count > 0:
            remaining_selected = random.sample(remaining_pool, remaining_count)
        else:
            remaining_selected = []

        # Kombiniere und sortiere
        numbers = sorted(non_birthday_selected + remaining_selected)

        # Vermeide Muster (optional)
        if self.avoid_patterns:
            numbers = self._avoid_obvious_patterns(numbers, keno_type)

        # Berechne Metriken
        anti_score = self.calculate_anti_birthday_score(numbers)
        reduction = self.calculate_expected_reduction(anti_score)

        return AntiBirthdayResult(
            numbers=numbers,
            anti_birthday_score=anti_score,
            expected_competition_reduction=reduction,
            keno_type=keno_type,
        )

    def _avoid_obvious_patterns(
        self,
        numbers: list[int],
        keno_type: int
    ) -> list[int]:
        """Vermeide offensichtliche Muster (konsekutive Zahlen etc.)."""
        # Pruefe auf zu viele konsekutive Zahlen
        max_consecutive = 3
        consecutive_count = 0
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                consecutive_count += 1

        # Wenn zu viele konsekutive, ersetze eine
        if consecutive_count >= max_consecutive:
            # Ersetze mittlere konsekutive Zahl
            for i in range(1, len(numbers) - 1):
                if (numbers[i] - numbers[i-1] == 1 and
                    numbers[i+1] - numbers[i] == 1):
                    # Finde Ersatz
                    available = list(
                        NON_BIRTHDAY_NUMBERS - set(numbers)
                    )
                    if available:
                        numbers[i] = random.choice(available)
                        numbers = sorted(numbers)
                        break

        return numbers

    def evaluate_combination(
        self,
        numbers: list[int],
        drawn_numbers: list[int]
    ) -> dict:
        """
        Bewerte eine Kombination gegen gezogene Zahlen.

        Args:
            numbers: Gespielte Zahlen
            drawn_numbers: Gezogene Zahlen (20 Stueck)

        Returns:
            Bewertungs-Dictionary
        """
        # Treffer
        matches = set(numbers) & set(drawn_numbers)

        # Birthday-Score der Ziehung
        drawn_birthday_score = sum(
            1 for n in drawn_numbers if n in BIRTHDAY_NUMBERS
        ) / len(drawn_numbers)

        # Anti-Birthday-Score der Kombination
        combo_anti_score = self.calculate_anti_birthday_score(numbers)

        # Erwartete Gewinner-Anzahl (relativ)
        # Je hoeher der Birthday-Score der Ziehung, desto mehr Gewinner
        expected_winner_multiplier = 1 + (drawn_birthday_score - 0.5) * 0.6

        return {
            "matches": len(matches),
            "matched_numbers": sorted(list(matches)),
            "drawn_birthday_score": round(drawn_birthday_score, 4),
            "combo_anti_birthday_score": round(combo_anti_score, 4),
            "expected_winner_multiplier": round(expected_winner_multiplier, 4),
            "strategy_advantage": round(1 / expected_winner_multiplier, 4),
        }


def calculate_anti_birthday_score(numbers: list[int]) -> float:
    """Berechne Anti-Birthday-Score fuer eine Zahlenliste."""
    strategy = AntiBirthdayStrategy()
    return strategy.calculate_anti_birthday_score(numbers)


def generate_anti_birthday_numbers(
    keno_type: int = 6,
    min_ratio: float = 0.6
) -> list[int]:
    """Generiere Anti-Birthday optimierte Zahlen."""
    strategy = AntiBirthdayStrategy(min_anti_birthday_ratio=min_ratio)
    result = strategy.generate_numbers(keno_type)
    return result.numbers


def evaluate_combination(
    numbers: list[int],
    drawn_numbers: list[int]
) -> dict:
    """Bewerte Kombination gegen Ziehung."""
    strategy = AntiBirthdayStrategy()
    return strategy.evaluate_combination(numbers, drawn_numbers)


# =============================================================================
# BACKTEST FUNKTIONEN
# =============================================================================

@dataclass
class BacktestResult:
    """Ergebnis eines Anti-Birthday Backtests."""

    strategy_name: str
    period_start: datetime
    period_end: datetime
    n_draws: int

    # Treffer-Statistiken
    total_matches: int
    avg_matches_per_draw: float

    # Birthday-Metriken
    avg_anti_birthday_score: float
    avg_drawn_birthday_score: float

    # Konkurrenz-Metriken
    avg_strategy_advantage: float
    advantageous_draws: int  # Ziehungen mit Vorteil (birthday_score > 0.5)
    disadvantageous_draws: int

    # Vergleich mit Random
    random_avg_matches: float
    improvement_vs_random: float

    def to_dict(self) -> dict:
        """Konvertiere zu Dictionary."""
        return {
            "strategy_name": self.strategy_name,
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
            },
            "n_draws": self.n_draws,
            "matches": {
                "total": self.total_matches,
                "avg_per_draw": round(self.avg_matches_per_draw, 4),
            },
            "birthday_metrics": {
                "avg_anti_birthday_score": round(self.avg_anti_birthday_score, 4),
                "avg_drawn_birthday_score": round(self.avg_drawn_birthday_score, 4),
            },
            "competition": {
                "avg_strategy_advantage": round(self.avg_strategy_advantage, 4),
                "advantageous_draws": self.advantageous_draws,
                "disadvantageous_draws": self.disadvantageous_draws,
                "advantage_ratio": round(
                    self.advantageous_draws / self.n_draws if self.n_draws > 0 else 0,
                    4
                ),
            },
            "vs_random": {
                "random_avg_matches": round(self.random_avg_matches, 4),
                "improvement": round(self.improvement_vs_random, 4),
            },
        }


def run_backtest(
    draws_df,
    keno_type: int = 6,
    min_anti_birthday_ratio: float = 0.6,
    n_random_samples: int = 100,
) -> BacktestResult:
    """
    Fuehre Backtest der Anti-Birthday Strategie durch.

    Args:
        draws_df: DataFrame mit Ziehungen (Spalten: datum, n1-n20)
        keno_type: KENO-Typ (Anzahl Zahlen)
        min_anti_birthday_ratio: Mindest Anti-Birthday Ratio
        n_random_samples: Anzahl Random-Samples pro Ziehung

    Returns:
        BacktestResult
    """
    strategy = AntiBirthdayStrategy(min_anti_birthday_ratio=min_anti_birthday_ratio)

    results = []
    random_results = []

    # Identifiziere Zahlen-Spalten
    num_cols = [c for c in draws_df.columns if c.startswith('n') and c[1:].isdigit()]
    num_cols = sorted(num_cols, key=lambda x: int(x[1:]))[:20]

    for _, row in draws_df.iterrows():
        # Extrahiere gezogene Zahlen
        drawn = [int(row[c]) for c in num_cols if not np.isnan(row[c])]

        if len(drawn) != 20:
            continue

        # Generiere Anti-Birthday Kombination
        ab_result = strategy.generate_numbers(keno_type)

        # Bewerte
        evaluation = strategy.evaluate_combination(ab_result.numbers, drawn)
        evaluation['anti_birthday_score'] = ab_result.anti_birthday_score
        results.append(evaluation)

        # Random-Baseline
        for _ in range(n_random_samples):
            random_nums = random.sample(range(1, 71), keno_type)
            matches = len(set(random_nums) & set(drawn))
            random_results.append(matches)

    if not results:
        raise ValueError("Keine validen Ziehungen gefunden")

    # Aggregiere Ergebnisse
    total_matches = sum(r['matches'] for r in results)
    avg_matches = total_matches / len(results)

    avg_anti_score = np.mean([r['anti_birthday_score'] for r in results])
    avg_drawn_birthday = np.mean([r['drawn_birthday_score'] for r in results])

    avg_advantage = np.mean([r['strategy_advantage'] for r in results])
    advantageous = sum(1 for r in results if r['drawn_birthday_score'] > 0.5)
    disadvantageous = len(results) - advantageous

    random_avg = np.mean(random_results)
    improvement = (avg_matches - random_avg) / random_avg if random_avg > 0 else 0

    return BacktestResult(
        strategy_name=f"AntiBirthday-{min_anti_birthday_ratio:.0%}",
        period_start=draws_df['datum'].min(),
        period_end=draws_df['datum'].max(),
        n_draws=len(results),
        total_matches=total_matches,
        avg_matches_per_draw=avg_matches,
        avg_anti_birthday_score=avg_anti_score,
        avg_drawn_birthday_score=avg_drawn_birthday,
        avg_strategy_advantage=avg_advantage,
        advantageous_draws=advantageous,
        disadvantageous_draws=disadvantageous,
        random_avg_matches=random_avg,
        improvement_vs_random=improvement,
    )


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("ANTI-BIRTHDAY STRATEGIE - Demo")
    print("=" * 60)

    strategy = AntiBirthdayStrategy(min_anti_birthday_ratio=0.7)

    print("\nGeneriere 5 Anti-Birthday Kombinationen (KENO-6):")
    for i in range(5):
        result = strategy.generate_numbers(keno_type=6, seed=i)
        print(f"  {i+1}. {result.numbers}")
        print(f"     Anti-Birthday: {result.anti_birthday_score:.0%}")
        print(f"     Erwartete Reduktion: {result.expected_competition_reduction:.1%}")

    print("\n" + "-" * 60)
    print("Beispiel-Bewertung gegen Ziehung:")
    example_combo = [35, 42, 51, 58, 64, 69]
    example_draw = [3, 7, 15, 22, 35, 42, 48, 51, 55, 58,
                   61, 64, 66, 67, 68, 69, 70, 1, 2, 4]

    eval_result = strategy.evaluate_combination(example_combo, example_draw)
    print(f"  Kombination: {example_combo}")
    print(f"  Treffer: {eval_result['matches']} ({eval_result['matched_numbers']})")
    print(f"  Ziehung Birthday-Score: {eval_result['drawn_birthday_score']:.0%}")
    print(f"  Strategie-Vorteil: {eval_result['strategy_advantage']:.2f}x")
