"""Kenobase Sum Distribution Analysis - Histogramm und Cluster-Erkennung.

Dieses Modul implementiert die Summen-Fenster Analyse fuer Kenobase V2.0.
Hypothese: KENO-Summenwerte clustern in bestimmten Fenstern (z.B. [140-170], [190-220]).

KENO-Kontext:
- 20 Zahlen werden aus [1,70] gezogen
- Erwartungswert: E[sum] = 20 * (1+70)/2 = 710
- Theoretische Standardabweichung: ~58 (basierend auf hypergeometrischer Verteilung)
- Tatsaechliche Verteilung sollte nahezu normalverteilt sein (CLT)

Metriken:
- Chi-Quadrat-Test gegen Gleichverteilung in Bins
- Cluster-Identifikation durch Peak-Erkennung
- Konfidenzintervalle fuer Summen-Fenster

Usage:
    from kenobase.analysis.sum_distribution import (
        SumDistributionResult,
        analyze_sum_distribution,
        detect_sum_clusters,
        run_sum_window_analysis,
    )

    results = run_sum_window_analysis(data_path="data/raw/keno/KENO_ab_2018.csv")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class HistogramBin:
    """Ein Bin des Summen-Histogramms.

    Attributes:
        bin_start: Untere Grenze des Bins (inklusiv)
        bin_end: Obere Grenze des Bins (exklusiv)
        count: Anzahl Ziehungen in diesem Bin
        frequency: Relative Haeufigkeit (count / total)
    """

    bin_start: int
    bin_end: int
    count: int
    frequency: float


@dataclass
class SumCluster:
    """Identifizierter Cluster in der Summen-Verteilung.

    Attributes:
        center: Mittelpunkt des Clusters
        range_min: Untere Grenze des Clusters
        range_max: Obere Grenze des Clusters
        density: Relative Dichte (Anteil der Ziehungen)
        z_score: Abweichung von Erwartungswert in Standardabweichungen
    """

    center: float
    range_min: int
    range_max: int
    density: float
    z_score: float


@dataclass
class ChiSquareResult:
    """Ergebnis des Chi-Quadrat-Tests.

    Attributes:
        statistic: Chi-Quadrat-Statistik
        p_value: p-Wert des Tests
        degrees_of_freedom: Freiheitsgrade
        is_significant: True wenn p < 0.05 (Verteilung weicht signifikant ab)
    """

    statistic: float
    p_value: float
    degrees_of_freedom: int
    is_significant: bool


@dataclass
class SumDistributionResult:
    """Vollstaendiges Ergebnis der Summen-Verteilungsanalyse.

    Attributes:
        total_draws: Anzahl analysierter Ziehungen
        sum_min: Minimale beobachtete Summe
        sum_max: Maximale beobachtete Summe
        sum_mean: Mittelwert der Summen
        sum_std: Standardabweichung der Summen
        expected_mean: Theoretischer Erwartungswert (710 fuer KENO)
        histogram: Liste von HistogramBin-Objekten
        clusters: Identifizierte Cluster
        chi_square: Chi-Quadrat-Testergebnis
        analysis_date: Zeitpunkt der Analyse
        data_source: Pfad zur Quelldatei
    """

    total_draws: int
    sum_min: int
    sum_max: int
    sum_mean: float
    sum_std: float
    expected_mean: float
    histogram: list[HistogramBin]
    clusters: list[SumCluster]
    chi_square: ChiSquareResult
    analysis_date: datetime = field(default_factory=datetime.now)
    data_source: str = ""


def calculate_sum_histogram(
    sums: list[int],
    bin_width: int = 20,
    range_min: Optional[int] = None,
    range_max: Optional[int] = None,
) -> list[HistogramBin]:
    """Berechnet Histogramm der Summen-Verteilung.

    Args:
        sums: Liste der Summen pro Ziehung
        bin_width: Breite jedes Bins (default 20)
        range_min: Untere Grenze des Histogramms (default: min(sums) - 10)
        range_max: Obere Grenze des Histogramms (default: max(sums) + 10)

    Returns:
        Liste von HistogramBin-Objekten
    """
    if not sums:
        return []

    sums_arr = np.array(sums)
    r_min = range_min if range_min is not None else int(sums_arr.min()) - 10
    r_max = range_max if range_max is not None else int(sums_arr.max()) + 10

    # Erstelle Bins
    bins = list(range(r_min, r_max + bin_width, bin_width))
    counts, bin_edges = np.histogram(sums_arr, bins=bins)

    total = len(sums)
    histogram = []
    for i, count in enumerate(counts):
        histogram.append(
            HistogramBin(
                bin_start=int(bin_edges[i]),
                bin_end=int(bin_edges[i + 1]),
                count=int(count),
                frequency=count / total if total > 0 else 0.0,
            )
        )

    return histogram


def chi_square_uniformity_test(
    histogram: list[HistogramBin],
) -> ChiSquareResult:
    """Fuehrt Chi-Quadrat-Test gegen Gleichverteilung durch.

    Args:
        histogram: Liste von HistogramBin-Objekten

    Returns:
        ChiSquareResult mit Statistik und p-Wert
    """
    if not histogram:
        return ChiSquareResult(
            statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
        )

    observed = np.array([h.count for h in histogram])
    total = observed.sum()

    if total == 0:
        return ChiSquareResult(
            statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
        )

    # Erwartete Haeufigkeit bei Gleichverteilung
    expected = np.full_like(observed, total / len(observed), dtype=float)

    # Filter Bins mit expected >= 5 (Chi-Quadrat Voraussetzung)
    valid_mask = expected >= 5
    if valid_mask.sum() < 2:
        # Nicht genug Bins fuer aussagekraeftigen Test
        return ChiSquareResult(
            statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
        )

    obs = observed[valid_mask]
    exp = expected[valid_mask]

    statistic, p_value = stats.chisquare(obs, f_exp=exp)
    dof = len(obs) - 1

    return ChiSquareResult(
        statistic=float(statistic),
        p_value=float(p_value),
        degrees_of_freedom=dof,
        is_significant=p_value < 0.05,
    )


def detect_sum_clusters(
    sums: list[int],
    histogram: list[HistogramBin],
    expected_mean: float = 710.0,
    expected_std: float = 58.0,
    min_density: float = 0.10,
) -> list[SumCluster]:
    """Identifiziert Cluster in der Summen-Verteilung.

    Ein Cluster ist eine zusammenhaengende Region mit ueberdurchschnittlicher Dichte.

    Args:
        sums: Liste der Summen pro Ziehung
        histogram: Berechnetes Histogramm
        expected_mean: Erwartungswert (default 710 fuer KENO)
        expected_std: Erwartete Standardabweichung (default 58)
        min_density: Minimale Dichte fuer Cluster-Erkennung (default 0.10)

    Returns:
        Liste von SumCluster-Objekten
    """
    if not histogram or not sums:
        return []

    clusters = []
    total = len(sums)

    # Finde Bins mit ueberdurchschnittlicher Dichte
    avg_frequency = 1.0 / len(histogram) if histogram else 0.0

    i = 0
    while i < len(histogram):
        h = histogram[i]
        if h.frequency > avg_frequency * 1.2:  # 20% ueber Durchschnitt
            # Start eines potenziellen Clusters
            cluster_start = h.bin_start
            cluster_count = h.count
            j = i + 1

            # Erweitere Cluster solange Dichte hoch bleibt
            while j < len(histogram) and histogram[j].frequency > avg_frequency * 0.8:
                cluster_count += histogram[j].count
                j += 1

            cluster_end = histogram[j - 1].bin_end
            cluster_center = (cluster_start + cluster_end) / 2
            cluster_density = cluster_count / total if total > 0 else 0.0

            if cluster_density >= min_density:
                z_score = (cluster_center - expected_mean) / expected_std
                clusters.append(
                    SumCluster(
                        center=cluster_center,
                        range_min=cluster_start,
                        range_max=cluster_end,
                        density=cluster_density,
                        z_score=z_score,
                    )
                )

            i = j
        else:
            i += 1

    return clusters


def analyze_sum_distribution(
    sums: list[int],
    expected_mean: float = 710.0,
    bin_width: int = 20,
    data_source: str = "",
) -> SumDistributionResult:
    """Fuehrt vollstaendige Summen-Verteilungsanalyse durch.

    Args:
        sums: Liste der Summen pro Ziehung
        expected_mean: Theoretischer Erwartungswert (710 fuer KENO)
        bin_width: Histogramm-Bin-Breite
        data_source: Pfad zur Quelldatei

    Returns:
        SumDistributionResult mit allen Analyseergebnissen
    """
    if not sums:
        return SumDistributionResult(
            total_draws=0,
            sum_min=0,
            sum_max=0,
            sum_mean=0.0,
            sum_std=0.0,
            expected_mean=expected_mean,
            histogram=[],
            clusters=[],
            chi_square=ChiSquareResult(0.0, 1.0, 0, False),
            data_source=data_source,
        )

    sums_arr = np.array(sums)

    # Grundstatistiken
    sum_min = int(sums_arr.min())
    sum_max = int(sums_arr.max())
    sum_mean = float(sums_arr.mean())
    sum_std = float(sums_arr.std())

    # Histogramm
    histogram = calculate_sum_histogram(sums, bin_width=bin_width)

    # Chi-Quadrat-Test
    chi_square = chi_square_uniformity_test(histogram)

    # Cluster-Erkennung
    clusters = detect_sum_clusters(
        sums, histogram, expected_mean=expected_mean, expected_std=sum_std
    )

    logger.info(
        f"Sum distribution analysis: n={len(sums)}, "
        f"mean={sum_mean:.1f}, std={sum_std:.1f}, "
        f"clusters={len(clusters)}"
    )

    return SumDistributionResult(
        total_draws=len(sums),
        sum_min=sum_min,
        sum_max=sum_max,
        sum_mean=sum_mean,
        sum_std=sum_std,
        expected_mean=expected_mean,
        histogram=histogram,
        clusters=clusters,
        chi_square=chi_square,
        data_source=data_source,
    )


def run_sum_window_analysis(
    data_path: str | Path,
    bin_width: int = 20,
    output_path: Optional[str | Path] = None,
) -> SumDistributionResult:
    """Fuehrt vollstaendige Summen-Fenster-Analyse auf KENO-Daten durch.

    Args:
        data_path: Pfad zur KENO-CSV-Datei
        bin_width: Histogramm-Bin-Breite (default 20)
        output_path: Optionaler Pfad fuer JSON-Output

    Returns:
        SumDistributionResult mit Analyseergebnissen
    """
    from kenobase.core.data_loader import DataLoader

    data_path = Path(data_path)
    loader = DataLoader()

    logger.info(f"Loading KENO data from {data_path}")
    results = loader.load(data_path)

    if not results:
        logger.warning(f"No draws loaded from {data_path}")
        return analyze_sum_distribution([], data_source=str(data_path))

    # Berechne Summen: sum(20 gezogene Zahlen)
    sums = [sum(draw.numbers) for draw in results]

    logger.info(f"Loaded {len(sums)} draws, analyzing sum distribution")

    result = analyze_sum_distribution(
        sums,
        expected_mean=710.0,  # E[sum] = 20 * (1+70)/2 = 710
        bin_width=bin_width,
        data_source=str(data_path),
    )

    if output_path:
        export_result_to_json(result, output_path)

    return result


def export_result_to_json(
    result: SumDistributionResult,
    output_path: str | Path,
) -> None:
    """Exportiert Analyseergebnis als JSON.

    Args:
        result: SumDistributionResult
        output_path: Zielpfad fuer JSON-Datei
    """
    import json

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "total_draws": result.total_draws,
        "sum_min": result.sum_min,
        "sum_max": result.sum_max,
        "sum_mean": result.sum_mean,
        "sum_std": result.sum_std,
        "expected_mean": result.expected_mean,
        "histogram": [
            {
                "bin_start": h.bin_start,
                "bin_end": h.bin_end,
                "count": h.count,
                "frequency": h.frequency,
            }
            for h in result.histogram
        ],
        "clusters": [
            {
                "center": c.center,
                "range_min": c.range_min,
                "range_max": c.range_max,
                "density": c.density,
                "z_score": c.z_score,
            }
            for c in result.clusters
        ],
        "chi_square": {
            "statistic": float(result.chi_square.statistic),
            "p_value": float(result.chi_square.p_value),
            "degrees_of_freedom": int(result.chi_square.degrees_of_freedom),
            "is_significant": bool(result.chi_square.is_significant),
        },
        "analysis_date": result.analysis_date.isoformat(),
        "data_source": result.data_source,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported sum distribution result to {output_path}")


def plot_sum_distribution(
    result: SumDistributionResult,
    output_path: Optional[str | Path] = None,
    show: bool = False,
) -> None:
    """Plottet die Summen-Verteilung als Histogramm.

    Args:
        result: SumDistributionResult
        output_path: Optionaler Pfad fuer PNG-Datei
        show: True um Plot anzuzeigen
    """
    import matplotlib.pyplot as plt

    if not result.histogram:
        logger.warning("No histogram data to plot")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogramm-Balken
    bin_centers = [(h.bin_start + h.bin_end) / 2 for h in result.histogram]
    counts = [h.count for h in result.histogram]
    bin_width = result.histogram[0].bin_end - result.histogram[0].bin_start

    ax.bar(bin_centers, counts, width=bin_width * 0.9, alpha=0.7, color="steelblue")

    # Erwartungswert-Linie
    ax.axvline(
        result.expected_mean,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"E[sum] = {result.expected_mean:.0f}",
    )

    # Beobachteter Mittelwert
    ax.axvline(
        result.sum_mean,
        color="green",
        linestyle="-",
        linewidth=2,
        label=f"Observed mean = {result.sum_mean:.1f}",
    )

    # Cluster markieren
    for cluster in result.clusters:
        ax.axvspan(
            cluster.range_min,
            cluster.range_max,
            alpha=0.2,
            color="orange",
            label=f"Cluster [{cluster.range_min}-{cluster.range_max}]",
        )

    ax.set_xlabel("Sum of 20 drawn numbers")
    ax.set_ylabel("Count")
    ax.set_title(
        f"KENO Sum Distribution (n={result.total_draws}, "
        f"Chi2 p={result.chi_square.p_value:.4f})"
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved plot to {output_path}")

    if show:
        plt.show()

    plt.close()


__all__ = [
    "HistogramBin",
    "SumCluster",
    "ChiSquareResult",
    "SumDistributionResult",
    "calculate_sum_histogram",
    "chi_square_uniformity_test",
    "detect_sum_clusters",
    "analyze_sum_distribution",
    "run_sum_window_analysis",
    "export_result_to_json",
    "plot_sum_distribution",
]
