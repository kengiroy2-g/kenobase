"""Kenobase Number Pool Generator - Zahlenpool-Generierung aus Haeufigkeitsanalyse.

Dieses Modul implementiert die Zahlenpool-Generierung fuer Kenobase V2.0.
Migriert aus Legacy V9: generiere_zahlenpool_optimiert().

Algorithmus:
1. Teile historische Ziehungen in 3 Zeitraeume (je 10 Ziehungen)
2. Ermittle Top-11 haeufigste Zahlen pro Zeitraum
3. Berechne Schnittmengen zwischen Top-11 jedes Zeitraums und Top-20 gesamt
4. Kombiniere paarweise Schnittmengen der Zeitraeume
5. Rueckgabe: Union aller relevanten Zahlen

Usage:
    from kenobase.core.number_pool import NumberPoolGenerator
    from kenobase.core.data_loader import DataLoader

    loader = DataLoader()
    draws = loader.load("data/KENO_ab_2018.csv")

    generator = NumberPoolGenerator()
    pool = generator.generate(draws)
    # pool = {3, 7, 15, 23, ...}  (set of candidate numbers)
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


@dataclass
class PeriodAnalysis:
    """Analyse-Ergebnis fuer einen Zeitraum.

    Attributes:
        period_name: Name des Zeitraums (z.B. "Zeitraum_1")
        frequency_counts: Counter mit Zahlen -> Haeufigkeit
        top_n: Top-N haeufigste Zahlen als Set
    """

    period_name: str
    frequency_counts: Counter
    top_n: set[int]


class NumberPoolGenerator:
    """Generiert Zahlenpool aus historischen Ziehungsdaten.

    Der Zahlenpool ist eine gefilterte Menge von Kandidaten-Zahlen,
    die auf Haeufigkeitsanalyse ueber mehrere Zeitraeume basiert.

    Attributes:
        n_periods: Anzahl der Zeitraeume (default 3)
        draws_per_period: Ziehungen pro Zeitraum (default 10)
        top_n_per_period: Top-N pro Zeitraum (default 11)
        top_n_total: Top-N fuer Gesamtanalyse (default 20)

    Example:
        >>> generator = NumberPoolGenerator()
        >>> pool = generator.generate(draws[:30])
        >>> len(pool)
        15
        >>> 42 in pool
        True
    """

    def __init__(
        self,
        n_periods: int = 3,
        draws_per_period: int = 10,
        top_n_per_period: int = 11,
        top_n_total: int = 20,
    ) -> None:
        """Initialisiert NumberPoolGenerator.

        Args:
            n_periods: Anzahl der Zeitraeume fuer Analyse
            draws_per_period: Anzahl Ziehungen pro Zeitraum
            top_n_per_period: Anzahl Top-Zahlen pro Zeitraum
            top_n_total: Anzahl Top-Zahlen fuer Gesamtanalyse
        """
        self.n_periods = n_periods
        self.draws_per_period = draws_per_period
        self.top_n_per_period = top_n_per_period
        self.top_n_total = top_n_total

    def generate(self, draws: list[DrawResult]) -> set[int]:
        """Generiert Zahlenpool aus Ziehungsdaten.

        Implementiert den Algorithmus aus Legacy V9:
        1. Teile Ziehungen in n_periods Zeitraeume
        2. Ermittle Top-N haeufigste Zahlen pro Zeitraum
        3. Schnittmenge mit Top-N total
        4. Union aller paarweisen Schnittmengen

        Args:
            draws: Liste von DrawResult-Objekten (mindestens
                   n_periods * draws_per_period erforderlich)

        Returns:
            Set von Kandidaten-Zahlen

        Raises:
            ValueError: Wenn nicht genuegend Ziehungen vorhanden
        """
        min_required = self.n_periods * self.draws_per_period
        if len(draws) < min_required:
            raise ValueError(
                f"Need at least {min_required} draws, got {len(draws)}"
            )

        # Schritt 1: Teile in Zeitraeume
        periods = self._split_into_periods(draws)

        # Schritt 2: Haeufigkeitsanalyse pro Zeitraum
        period_analyses = [
            self._analyze_period(name, period_draws)
            for name, period_draws in periods.items()
        ]

        # Schritt 3: Gesamtanalyse
        all_draws = []
        for period_draws in periods.values():
            all_draws.extend(period_draws)
        total_top_n = self.get_top_n(all_draws, self.top_n_total)

        # Schritt 4: Schnittmengen mit Top-N total
        intersections_with_total = [
            analysis.top_n.intersection(total_top_n)
            for analysis in period_analyses
        ]

        # Schritt 5: Kombiniere Schnittmengen ohne Duplikate
        combined_intersections = set().union(*intersections_with_total)

        # Schritt 6: Paarweise Schnittmengen der Zeitraeume
        pairwise_intersections = self.get_intersections(
            [analysis.top_n for analysis in period_analyses]
        )

        # Finale Union
        pool = combined_intersections.union(pairwise_intersections)

        logger.info(
            f"Generated number pool with {len(pool)} candidates "
            f"from {len(draws)} draws ({self.n_periods} periods)"
        )

        return pool

    def _split_into_periods(
        self, draws: list[DrawResult]
    ) -> dict[str, list[DrawResult]]:
        """Teilt Ziehungen in Zeitraeume auf.

        Args:
            draws: Liste von DrawResult-Objekten

        Returns:
            Dict mit Zeitraum-Namen als Keys und Ziehungslisten als Values
        """
        periods = {}
        for i in range(self.n_periods):
            start = i * self.draws_per_period
            end = start + self.draws_per_period
            period_name = f"Zeitraum_{i + 1}"
            periods[period_name] = draws[start:end]
        return periods

    def _analyze_period(
        self, period_name: str, draws: list[DrawResult]
    ) -> PeriodAnalysis:
        """Analysiert einen Zeitraum.

        Args:
            period_name: Name des Zeitraums
            draws: Ziehungen dieses Zeitraums

        Returns:
            PeriodAnalysis mit Haeufigkeiten und Top-N
        """
        counts = self._count_frequencies(draws)
        top_n = set(self._get_top_n_from_counter(counts, self.top_n_per_period))

        return PeriodAnalysis(
            period_name=period_name,
            frequency_counts=counts,
            top_n=top_n,
        )

    def _count_frequencies(self, draws: list[DrawResult]) -> Counter:
        """Zaehlt Haeufigkeit jeder Zahl in Ziehungen.

        Args:
            draws: Liste von DrawResult-Objekten

        Returns:
            Counter mit Zahl -> Anzahl Vorkommen
        """
        counter: Counter = Counter()
        for draw in draws:
            counter.update(draw.numbers)
        return counter

    def _get_top_n_from_counter(self, counter: Counter, n: int) -> list[int]:
        """Extrahiert Top-N haeufigste Zahlen aus Counter.

        Args:
            counter: Counter mit Haeufigkeiten
            n: Anzahl Top-Zahlen

        Returns:
            Liste der n haeufigsten Zahlen
        """
        return [num for num, _ in counter.most_common(n)]

    def get_top_n(self, draws: list[DrawResult], n: int) -> set[int]:
        """Ermittelt Top-N haeufigste Zahlen aus Ziehungen.

        Oeffentliche Hilfsmethode fuer externe Verwendung.

        Args:
            draws: Liste von DrawResult-Objekten
            n: Anzahl Top-Zahlen

        Returns:
            Set der n haeufigsten Zahlen
        """
        counts = self._count_frequencies(draws)
        return set(self._get_top_n_from_counter(counts, n))

    def get_intersections(self, sets: list[set[int]]) -> set[int]:
        """Berechnet Union aller paarweisen Schnittmengen.

        Fuer jedes Paar von Sets wird die Schnittmenge berechnet,
        dann werden alle Schnittmengen vereinigt.

        Args:
            sets: Liste von Sets

        Returns:
            Union aller paarweisen Schnittmengen

        Example:
            >>> generator = NumberPoolGenerator()
            >>> sets = [{1, 2, 3}, {2, 3, 4}, {3, 4, 5}]
            >>> generator.get_intersections(sets)
            {2, 3, 4}  # {2,3} | {3} | {3,4}
        """
        if len(sets) < 2:
            return set()

        all_intersections: set[int] = set()
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                intersection = sets[i].intersection(sets[j])
                all_intersections.update(intersection)

        return all_intersections

    @classmethod
    def from_draws(
        cls,
        draws: list[DrawResult],
        n_periods: int = 3,
        draws_per_period: int = 10,
        top_n_per_period: int = 11,
        top_n_total: int = 20,
    ) -> set[int]:
        """Factory-Methode fuer direkte Pool-Generierung.

        Convenience-Methode die Generator-Erstellung und generate()
        kombiniert.

        Args:
            draws: Liste von DrawResult-Objekten
            n_periods: Anzahl der Zeitraeume
            draws_per_period: Ziehungen pro Zeitraum
            top_n_per_period: Top-N pro Zeitraum
            top_n_total: Top-N fuer Gesamtanalyse

        Returns:
            Set von Kandidaten-Zahlen

        Example:
            >>> pool = NumberPoolGenerator.from_draws(draws)
            >>> len(pool)
            18
        """
        generator = cls(
            n_periods=n_periods,
            draws_per_period=draws_per_period,
            top_n_per_period=top_n_per_period,
            top_n_total=top_n_total,
        )
        return generator.generate(draws)


__all__ = [
    "NumberPoolGenerator",
    "PeriodAnalysis",
]
