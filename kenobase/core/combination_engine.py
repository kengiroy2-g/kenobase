"""Kenobase Combination Engine - Generator fuer gefilterte Zahlenkombinationen.

Dieses Modul implementiert die Kombinations-Engine fuer Kenobase V2.0.
Generiert 6er-Kombinationen aus einem Zahlenpool mit konfigurierbaren Filtern.

Filter:
1. Zehnergruppen-Filter: Max N Zahlen pro Dekade (1-10, 11-20, etc.)
2. Summen-Filter: Kombinations-Summe im konfigurierbaren Bereich

Design-Entscheidungen:
- Generator-Pattern fuer Memory-Effizienz bei grossen Pools
- Dekaden-Definition: 1-10=Dekade0, 11-20=Dekade1, etc. (number-1)//10
- Config-Integration via from_config() Factory-Methode

Usage:
    from kenobase.core.combination_engine import CombinationEngine
    from kenobase.core.number_pool import NumberPoolGenerator

    # Pool generieren
    pool = NumberPoolGenerator().generate(draws)

    # Kombinationen generieren
    engine = CombinationEngine(
        pool=pool,
        combination_size=6,
        max_per_decade=3,
        min_sum=100,
        max_sum=300
    )

    for combination in engine.generate():
        print(combination.numbers, combination.sum_value)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import combinations
from typing import TYPE_CHECKING, Iterator, Optional

if TYPE_CHECKING:
    from kenobase.core.config import KenobaseConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CombinationResult:
    """Ergebnis einer generierten Kombination.

    Attributes:
        numbers: Tuple der Zahlen in der Kombination (sortiert)
        sum_value: Summe aller Zahlen
        decade_distribution: Dict mit Dekade -> Anzahl Zahlen
    """

    numbers: tuple[int, ...]
    sum_value: int
    decade_distribution: dict[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Berechnet decade_distribution nach Initialisierung."""
        if not self.decade_distribution:
            dist = {}
            for num in self.numbers:
                decade = (num - 1) // 10
                dist[decade] = dist.get(decade, 0) + 1
            # frozen=True erfordert object.__setattr__
            object.__setattr__(self, "decade_distribution", dist)


class CombinationEngine:
    """Generiert gefilterte Zahlenkombinationen aus einem Pool.

    Der Engine nimmt einen Zahlenpool (set[int]) und generiert alle
    gueltigen Kombinationen nach konfigurierten Filterregeln.

    Attributes:
        pool: Set von Kandidatenzahlen
        combination_size: Groesse der Kombinationen (default 6)
        max_per_decade: Max Zahlen pro Dekade (default 3)
        min_sum: Minimale Kombinationssumme (optional)
        max_sum: Maximale Kombinationssumme (optional)

    Example:
        >>> engine = CombinationEngine(pool={1,2,3,11,12,21}, combination_size=3)
        >>> list(engine.generate())
        [CombinationResult(numbers=(1, 11, 21), ...), ...]
    """

    def __init__(
        self,
        pool: set[int],
        combination_size: int = 6,
        max_per_decade: int = 3,
        min_sum: Optional[int] = None,
        max_sum: Optional[int] = None,
    ) -> None:
        """Initialisiert CombinationEngine.

        Args:
            pool: Set von Kandidatenzahlen aus NumberPoolGenerator
            combination_size: Anzahl Zahlen pro Kombination
            max_per_decade: Max Zahlen pro Zehnergruppe (1-10, 11-20, etc.)
            min_sum: Minimale Summe der Kombination (None = kein Filter)
            max_sum: Maximale Summe der Kombination (None = kein Filter)

        Raises:
            ValueError: Bei ungueltigem pool oder combination_size
        """
        if not pool:
            raise ValueError("Pool cannot be empty")
        if combination_size < 1:
            raise ValueError(f"combination_size must be >= 1, got {combination_size}")
        if len(pool) < combination_size:
            raise ValueError(
                f"Pool size ({len(pool)}) must be >= combination_size ({combination_size})"
            )
        if max_per_decade < 1:
            raise ValueError(f"max_per_decade must be >= 1, got {max_per_decade}")

        self.pool = pool
        self.combination_size = combination_size
        self.max_per_decade = max_per_decade
        self.min_sum = min_sum
        self.max_sum = max_sum

        # Sortierte Liste fuer konsistente Iteration
        self._sorted_pool = sorted(pool)

        logger.debug(
            f"CombinationEngine initialized: pool_size={len(pool)}, "
            f"combination_size={combination_size}, max_per_decade={max_per_decade}"
        )

    def generate(self) -> Iterator[CombinationResult]:
        """Generiert alle gueltigen Kombinationen.

        Verwendet Generator-Pattern fuer Memory-Effizienz.
        Filtert nach:
        1. Zehnergruppen-Regel (max_per_decade)
        2. Summen-Schwelle (min_sum, max_sum)

        Yields:
            CombinationResult fuer jede gueltige Kombination

        Example:
            >>> engine = CombinationEngine(pool={1,2,11,12,21,22}, combination_size=3)
            >>> for combo in engine.generate():
            ...     print(combo.numbers)
        """
        total_generated = 0
        filtered_decade = 0
        filtered_sum = 0

        for combo_tuple in combinations(self._sorted_pool, self.combination_size):
            # Schritt 1: Zehnergruppen-Filter
            if not self._passes_decade_filter(combo_tuple):
                filtered_decade += 1
                continue

            # Schritt 2: Summen-Filter
            combo_sum = sum(combo_tuple)
            if not self._passes_sum_filter(combo_sum):
                filtered_sum += 1
                continue

            # Gueltige Kombination
            total_generated += 1
            yield CombinationResult(
                numbers=combo_tuple,
                sum_value=combo_sum,
            )

        logger.info(
            f"Generated {total_generated} combinations "
            f"(filtered: {filtered_decade} by decade, {filtered_sum} by sum)"
        )

    def _passes_decade_filter(self, numbers: tuple[int, ...]) -> bool:
        """Prueft ob Kombination die Zehnergruppen-Regel erfuellt.

        Die Regel: Max max_per_decade Zahlen pro Dekade.
        Dekaden: 1-10=0, 11-20=1, 21-30=2, etc.
        Formel: decade = (number - 1) // 10

        Args:
            numbers: Tuple von Zahlen

        Returns:
            True wenn keine Dekade mehr als max_per_decade Zahlen hat
        """
        decade_counts: dict[int, int] = {}
        for num in numbers:
            decade = (num - 1) // 10
            decade_counts[decade] = decade_counts.get(decade, 0) + 1
            if decade_counts[decade] > self.max_per_decade:
                return False
        return True

    def _passes_sum_filter(self, combo_sum: int) -> bool:
        """Prueft ob Kombination die Summen-Schwelle erfuellt.

        Args:
            combo_sum: Summe der Kombination

        Returns:
            True wenn Summe im erlaubten Bereich liegt
        """
        if self.min_sum is not None and combo_sum < self.min_sum:
            return False
        if self.max_sum is not None and combo_sum > self.max_sum:
            return False
        return True

    def count_combinations(self) -> int:
        """Zaehlt gueltige Kombinationen ohne sie zu speichern.

        Nuetzlich fuer Performance-Schaetzungen vor vollstaendiger Generierung.

        Returns:
            Anzahl gueltiger Kombinationen
        """
        count = 0
        for _ in self.generate():
            count += 1
        return count

    def get_statistics(self) -> dict:
        """Berechnet Statistiken ueber generierbare Kombinationen.

        Returns:
            Dict mit:
            - pool_size: Groesse des Eingabepools
            - combination_size: Kombinationsgroesse
            - theoretical_max: Theoretisches Maximum ohne Filter
            - decade_distribution: Verteilung des Pools auf Dekaden
        """
        from math import comb

        # Dekaden-Verteilung des Pools
        pool_decades: dict[int, int] = {}
        for num in self.pool:
            decade = (num - 1) // 10
            pool_decades[decade] = pool_decades.get(decade, 0) + 1

        return {
            "pool_size": len(self.pool),
            "combination_size": self.combination_size,
            "theoretical_max": comb(len(self.pool), self.combination_size),
            "max_per_decade": self.max_per_decade,
            "min_sum": self.min_sum,
            "max_sum": self.max_sum,
            "pool_decade_distribution": dict(sorted(pool_decades.items())),
        }

    @classmethod
    def from_config(
        cls,
        pool: set[int],
        config: KenobaseConfig,
        min_sum: Optional[int] = None,
        max_sum: Optional[int] = None,
    ) -> CombinationEngine:
        """Factory-Methode zur Erstellung aus Kenobase-Konfiguration.

        Liest combination_size vom aktiven Spiel und max_per_decade
        aus analysis.zehnergruppen_max_per_group.

        Args:
            pool: Set von Kandidatenzahlen
            config: KenobaseConfig-Instanz
            min_sum: Optionale minimale Summe (ueberschreibt Config)
            max_sum: Optionale maximale Summe (ueberschreibt Config)

        Returns:
            Konfigurierte CombinationEngine-Instanz

        Example:
            >>> from kenobase.core.config import load_config
            >>> config = load_config("config/default.yaml")
            >>> engine = CombinationEngine.from_config(pool, config)
        """
        # Lese combination_size vom aktiven Spiel
        # Fuer KENO: numbers_to_draw=20, aber wir generieren 6er-Kombis
        # Convention: 6er-Kombis sind Standard fuer Tippschein-Analyse
        combination_size = 6

        # Lese max_per_decade aus Analysis-Config
        max_per_decade = config.analysis.zehnergruppen_max_per_group

        logger.info(
            f"Creating CombinationEngine from config: "
            f"combination_size={combination_size}, max_per_decade={max_per_decade}"
        )

        return cls(
            pool=pool,
            combination_size=combination_size,
            max_per_decade=max_per_decade,
            min_sum=min_sum,
            max_sum=max_sum,
        )


__all__ = [
    "CombinationEngine",
    "CombinationResult",
]
