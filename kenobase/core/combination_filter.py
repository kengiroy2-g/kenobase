"""Kenobase Combination Filter - Bridge between Sum Distribution and CombinationEngine.

Dieses Modul verbindet die Summen-Verteilungsanalyse (sum_distribution.py) mit dem
CombinationEngine, um min_sum/max_sum Filter dynamisch aus erkannten Clustern zu setzen.

TASK-P05: Summen-Filter Integration

Design:
- SumBounds dataclass fuer min_sum/max_sum Grenzen
- derive_sum_bounds_from_clusters() extrahiert Grenzen aus SumCluster-Liste
- derive_sum_bounds_from_config() liest manuelle Overrides oder verwendet Cluster
- FilteredCombinationEngine Factory kombiniert alles

Usage:
    from kenobase.core.combination_filter import (
        SumBounds,
        derive_sum_bounds_from_clusters,
        create_filtered_engine,
    )
    from kenobase.analysis.sum_distribution import detect_sum_clusters

    # Aus Cluster-Analyse
    clusters = detect_sum_clusters(sums, histogram)
    bounds = derive_sum_bounds_from_clusters(clusters)

    # Engine mit Summen-Filter
    engine = create_filtered_engine(pool, config, sum_bounds=bounds)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kenobase.analysis.sum_distribution import SumCluster, SumDistributionResult
    from kenobase.core.config import KenobaseConfig

logger = logging.getLogger(__name__)


@dataclass
class SumBounds:
    """Grenzen fuer den Summen-Filter.

    Attributes:
        min_sum: Minimale erlaubte Summe (None = kein Filter)
        max_sum: Maximale erlaubte Summe (None = kein Filter)
        source: Quelle der Grenzen ("cluster", "config", "manual")
        cluster_density: Dichte der Cluster die diese Grenzen ergaben (optional)
    """

    min_sum: Optional[int]
    max_sum: Optional[int]
    source: str = "unknown"
    cluster_density: Optional[float] = None

    def is_active(self) -> bool:
        """True wenn mindestens eine Grenze gesetzt ist."""
        return self.min_sum is not None or self.max_sum is not None

    def __repr__(self) -> str:
        if not self.is_active():
            return "SumBounds(inactive)"
        return f"SumBounds({self.min_sum}-{self.max_sum}, source={self.source})"


def derive_sum_bounds_from_clusters(
    clusters: list[SumCluster],
    use_union: bool = True,
) -> SumBounds:
    """Leitet Summen-Grenzen aus erkannten Clustern ab.

    Args:
        clusters: Liste von SumCluster aus detect_sum_clusters()
        use_union: True = Union aller Cluster, False = nur groesster Cluster

    Returns:
        SumBounds mit min_sum/max_sum aus Cluster-Ranges
    """
    if not clusters:
        logger.debug("No clusters provided, returning inactive SumBounds")
        return SumBounds(min_sum=None, max_sum=None, source="cluster")

    if use_union:
        # Union: Verwende min(range_min) und max(range_max) aller Cluster
        min_sum = min(c.range_min for c in clusters)
        max_sum = max(c.range_max for c in clusters)
        total_density = sum(c.density for c in clusters)
    else:
        # Nur groesster Cluster nach Dichte
        largest = max(clusters, key=lambda c: c.density)
        min_sum = largest.range_min
        max_sum = largest.range_max
        total_density = largest.density

    logger.info(
        f"Derived sum bounds from {len(clusters)} clusters: "
        f"[{min_sum}, {max_sum}] (density={total_density:.2%})"
    )

    return SumBounds(
        min_sum=min_sum,
        max_sum=max_sum,
        source="cluster",
        cluster_density=total_density,
    )


def derive_sum_bounds_from_result(
    result: SumDistributionResult,
    use_union: bool = True,
) -> SumBounds:
    """Convenience: Extrahiert Grenzen direkt aus SumDistributionResult.

    Args:
        result: Vollstaendiges Analyse-Ergebnis
        use_union: True = Union aller Cluster

    Returns:
        SumBounds
    """
    return derive_sum_bounds_from_clusters(result.clusters, use_union=use_union)


def derive_sum_bounds_from_config(
    config: KenobaseConfig,
    clusters: Optional[list[SumCluster]] = None,
) -> SumBounds:
    """Leitet Summen-Grenzen aus Config ab (mit optionalen Clustern als Fallback).

    Prioritaet:
    1. Manual overrides aus config.analysis.sum_windows.manual_min_sum/max_sum
    2. Cluster-basierte Grenzen falls clusters != None
    3. None (kein Filter)

    Args:
        config: Kenobase-Konfiguration
        clusters: Optionale Cluster fuer automatische Grenzen

    Returns:
        SumBounds
    """
    sum_cfg = config.analysis.sum_windows

    # Prioritaet 1: Manuelle Overrides
    if sum_cfg.manual_min_sum is not None or sum_cfg.manual_max_sum is not None:
        logger.info(
            f"Using manual sum bounds from config: "
            f"[{sum_cfg.manual_min_sum}, {sum_cfg.manual_max_sum}]"
        )
        return SumBounds(
            min_sum=sum_cfg.manual_min_sum,
            max_sum=sum_cfg.manual_max_sum,
            source="config",
        )

    # Prioritaet 2: Cluster-basiert
    if clusters:
        return derive_sum_bounds_from_clusters(clusters, use_union=True)

    # Prioritaet 3: Kein Filter
    logger.debug("No sum bounds configured or detected")
    return SumBounds(min_sum=None, max_sum=None, source="none")


def create_filtered_engine(
    pool: set[int],
    config: KenobaseConfig,
    sum_bounds: Optional[SumBounds] = None,
) -> "CombinationEngine":
    """Factory: Erstellt CombinationEngine mit Summen-Filter.

    Args:
        pool: Zahlenpool
        config: Kenobase-Konfiguration
        sum_bounds: Optionale explizite Grenzen (sonst aus Config)

    Returns:
        Konfigurierte CombinationEngine-Instanz
    """
    from kenobase.core.combination_engine import CombinationEngine

    # Bestimme Grenzen
    if sum_bounds is None:
        sum_bounds = derive_sum_bounds_from_config(config, clusters=None)

    min_sum = sum_bounds.min_sum
    max_sum = sum_bounds.max_sum

    logger.info(f"Creating filtered engine with sum_bounds={sum_bounds}")

    return CombinationEngine.from_config(
        pool=pool,
        config=config,
        min_sum=min_sum,
        max_sum=max_sum,
    )


def analyze_and_filter(
    pool: set[int],
    draws: list,
    config: KenobaseConfig,
    use_detected_clusters: bool = True,
) -> tuple["CombinationEngine", SumBounds, Optional["SumDistributionResult"]]:
    """Vollstaendiger Workflow: Analyse + Engine-Erstellung.

    Fuehrt Summen-Analyse durch, extrahiert Cluster, und erstellt gefilterten Engine.

    Args:
        pool: Zahlenpool
        draws: Liste von DrawResult fuer Summen-Berechnung
        config: Kenobase-Konfiguration
        use_detected_clusters: True = verwende erkannte Cluster

    Returns:
        Tuple (engine, sum_bounds, sum_result)
    """
    from kenobase.analysis.sum_distribution import (
        SumDistributionResult,
        analyze_sum_distribution,
    )
    from kenobase.core.combination_engine import CombinationEngine

    sum_cfg = config.analysis.sum_windows
    sum_result: Optional[SumDistributionResult] = None
    sum_bounds: SumBounds

    if not sum_cfg.enabled:
        logger.info("Sum windows analysis disabled in config")
        sum_bounds = SumBounds(min_sum=None, max_sum=None, source="disabled")
    elif sum_cfg.manual_min_sum is not None or sum_cfg.manual_max_sum is not None:
        # Manuelle Grenzen
        sum_bounds = SumBounds(
            min_sum=sum_cfg.manual_min_sum,
            max_sum=sum_cfg.manual_max_sum,
            source="config",
        )
    elif use_detected_clusters and draws:
        # Automatische Cluster-Erkennung
        sums = [sum(d.numbers) for d in draws]
        sum_result = analyze_sum_distribution(
            sums=sums,
            expected_mean=sum_cfg.expected_mean,
            bin_width=sum_cfg.bin_width,
        )
        sum_bounds = derive_sum_bounds_from_result(sum_result, use_union=True)
    else:
        sum_bounds = SumBounds(min_sum=None, max_sum=None, source="none")

    engine = CombinationEngine.from_config(
        pool=pool,
        config=config,
        min_sum=sum_bounds.min_sum,
        max_sum=sum_bounds.max_sum,
    )

    return engine, sum_bounds, sum_result


__all__ = [
    "SumBounds",
    "derive_sum_bounds_from_clusters",
    "derive_sum_bounds_from_result",
    "derive_sum_bounds_from_config",
    "create_filtered_engine",
    "analyze_and_filter",
]
