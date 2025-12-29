"""HYP-002: GK1 Wartezeit-Verteilungs-Analyse.

Analysiert die Verteilung der Wartezeiten (vergangene_tage) zwischen
Gewinnklasse 1 (GK1) Treffern in KENO. Testet ob die Verteilung
der erwarteten geometrischen Verteilung entspricht.

Acceptance Criteria:
- Chi-Quadrat Uniformitaetstest p > 0.05 -> keine Manipulation
- p < 0.05 -> signifikante Abweichung von Zufallsverteilung
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats

from kenobase.core.data_loader import DataLoader, GK1Summary

logger = logging.getLogger(__name__)


@dataclass
class WaitingTimeStats:
    """Deskriptive Statistik fuer Wartezeiten.

    Attributes:
        keno_typ: Keno-Typ (9 oder 10)
        n_events: Anzahl GK1-Ereignisse
        mean_days: Durchschnittliche Wartezeit in Tagen
        std_days: Standardabweichung
        median_days: Median
        min_days: Minimum
        max_days: Maximum
        cv: Variationskoeffizient (std/mean)
        skewness: Schiefe der Verteilung
        kurtosis: Woelbung der Verteilung
    """

    keno_typ: int
    n_events: int
    mean_days: float
    std_days: float
    median_days: float
    min_days: int
    max_days: int
    cv: float
    skewness: float
    kurtosis: float


@dataclass
class ChiSquareResult:
    """Ergebnis des Chi-Quadrat Uniformitaetstests.

    Attributes:
        keno_typ: Keno-Typ (9 oder 10)
        chi2_statistic: Chi-Quadrat Teststatistik
        p_value: p-Wert des Tests
        df: Freiheitsgrade
        is_uniform: True wenn p > 0.05 (keine signifikante Abweichung)
        interpretation: Textuelle Interpretation
    """

    keno_typ: int
    chi2_statistic: float
    p_value: float
    df: int
    is_uniform: bool
    interpretation: str


@dataclass
class OutlierInfo:
    """Information ueber Outlier in Wartezeiten.

    Attributes:
        keno_typ: Keno-Typ (9 oder 10)
        n_outliers: Anzahl Outlier (>= Q3 + 1.5*IQR)
        outlier_threshold: Schwellwert fuer Outlier
        outlier_values: Liste der Outlier-Werte
        outlier_dates: Liste der Daten der Outlier-Ereignisse
    """

    keno_typ: int
    n_outliers: int
    outlier_threshold: float
    outlier_values: list[int]
    outlier_dates: list[str]


@dataclass
class HistogramBin:
    """Ein Bin des Wartezeit-Histogramms.

    Attributes:
        bin_start: Untere Grenze des Bins (inklusiv)
        bin_end: Obere Grenze des Bins (exklusiv)
        count: Anzahl Ereignisse in diesem Bin
        expected: Erwartete Anzahl bei Gleichverteilung
        frequency: Relative Haeufigkeit
    """

    bin_start: int
    bin_end: int
    count: int
    expected: float
    frequency: float


@dataclass
class GK1WaitingResult:
    """Gesamtergebnis der GK1 Wartezeit-Analyse.

    Attributes:
        analysis_date: Datum der Analyse
        data_source: Pfad zur Quelldatei
        stats_keno9: Statistik fuer Keno-Typ 9
        stats_keno10: Statistik fuer Keno-Typ 10
        chi2_keno9: Chi-Quadrat Test fuer Keno-Typ 9
        chi2_keno10: Chi-Quadrat Test fuer Keno-Typ 10
        histogram_keno9: Histogramm fuer Keno-Typ 9
        histogram_keno10: Histogramm fuer Keno-Typ 10
        outliers_keno9: Outlier fuer Keno-Typ 9
        outliers_keno10: Outlier fuer Keno-Typ 10
        hypothesis_result: Ergebnis der Hypothesentestung
        acceptance_criteria_met: True wenn keine Manipulation erkannt
    """

    analysis_date: str
    data_source: str
    stats_keno9: Optional[WaitingTimeStats]
    stats_keno10: Optional[WaitingTimeStats]
    chi2_keno9: Optional[ChiSquareResult]
    chi2_keno10: Optional[ChiSquareResult]
    histogram_keno9: list[HistogramBin]
    histogram_keno10: list[HistogramBin]
    outliers_keno9: Optional[OutlierInfo]
    outliers_keno10: Optional[OutlierInfo]
    hypothesis_result: str
    acceptance_criteria_met: bool


def load_gk1_summary_data(path: str | Path) -> list[GK1Summary]:
    """Laedt GK1Summary Daten aus CSV.

    Args:
        path: Pfad zur CSV-Datei (10-9_KGDaten_gefiltert.csv)

    Returns:
        Liste von GK1Summary Objekten
    """
    loader = DataLoader()
    return loader.load(path)


def calculate_waiting_stats(
    data: list[GK1Summary],
    keno_typ: int,
) -> Optional[WaitingTimeStats]:
    """Berechnet deskriptive Statistik fuer Wartezeiten.

    Args:
        data: Liste von GK1Summary Objekten
        keno_typ: 9 oder 10

    Returns:
        WaitingTimeStats oder None wenn keine Daten
    """
    # Filter nach Keno-Typ
    filtered = [d for d in data if d.keno_typ == keno_typ]
    if not filtered:
        logger.warning(f"Keine Daten fuer Keno-Typ {keno_typ}")
        return None

    waiting_times = [d.vergangene_tage for d in filtered]
    arr = np.array(waiting_times)

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    cv = std_val / mean_val if mean_val > 0 else 0.0

    # Schiefe und Woelbung
    skew = float(stats.skew(arr)) if len(arr) >= 3 else 0.0
    kurt = float(stats.kurtosis(arr)) if len(arr) >= 4 else 0.0

    return WaitingTimeStats(
        keno_typ=keno_typ,
        n_events=len(filtered),
        mean_days=round(mean_val, 2),
        std_days=round(std_val, 2),
        median_days=float(np.median(arr)),
        min_days=int(np.min(arr)),
        max_days=int(np.max(arr)),
        cv=round(cv, 4),
        skewness=round(skew, 4),
        kurtosis=round(kurt, 4),
    )


def calculate_histogram(
    data: list[GK1Summary],
    keno_typ: int,
    n_bins: int = 10,
) -> list[HistogramBin]:
    """Erstellt Histogramm der Wartezeiten.

    Args:
        data: Liste von GK1Summary Objekten
        keno_typ: 9 oder 10
        n_bins: Anzahl Bins

    Returns:
        Liste von HistogramBin Objekten
    """
    filtered = [d for d in data if d.keno_typ == keno_typ]
    if not filtered:
        return []

    waiting_times = [d.vergangene_tage for d in filtered]
    arr = np.array(waiting_times)

    # Berechne Histogramm
    counts, bin_edges = np.histogram(arr, bins=n_bins)
    total = len(waiting_times)
    expected = total / n_bins

    bins = []
    for i in range(len(counts)):
        bins.append(
            HistogramBin(
                bin_start=int(bin_edges[i]),
                bin_end=int(bin_edges[i + 1]),
                count=int(counts[i]),
                expected=round(expected, 2),
                frequency=round(counts[i] / total, 4) if total > 0 else 0.0,
            )
        )

    return bins


def chi_square_uniformity_test(
    data: list[GK1Summary],
    keno_typ: int,
    n_bins: int = 10,
    alpha: float = 0.05,
) -> Optional[ChiSquareResult]:
    """Fuehrt Chi-Quadrat Uniformitaetstest durch.

    Testet ob die Wartezeiten einer Gleichverteilung folgen.
    H0: Wartezeiten sind gleichverteilt
    H1: Wartezeiten sind nicht gleichverteilt

    Args:
        data: Liste von GK1Summary Objekten
        keno_typ: 9 oder 10
        n_bins: Anzahl Bins fuer den Test
        alpha: Signifikanzniveau (default 0.05)

    Returns:
        ChiSquareResult oder None wenn zu wenige Daten
    """
    filtered = [d for d in data if d.keno_typ == keno_typ]
    if len(filtered) < 20:
        logger.warning(
            f"Zu wenige Daten fuer Chi-Quadrat Test: {len(filtered)} < 20"
        )
        return None

    waiting_times = [d.vergangene_tage for d in filtered]
    arr = np.array(waiting_times)

    # Berechne beobachtete Haeufigkeiten
    counts, _ = np.histogram(arr, bins=n_bins)

    # Erwartete Haeufigkeit bei Gleichverteilung
    expected = np.full(n_bins, len(waiting_times) / n_bins)

    # Chi-Quadrat Test
    # Mindestens 5 erwartete Beobachtungen pro Bin empfohlen
    if np.any(expected < 5):
        logger.warning(
            f"Einige Bins haben weniger als 5 erwartete Beobachtungen"
        )

    chi2_stat, p_value = stats.chisquare(counts, f_exp=expected)

    is_uniform = p_value > alpha

    if is_uniform:
        interpretation = (
            f"p-Wert {p_value:.4f} > {alpha}: "
            f"Keine signifikante Abweichung von Gleichverteilung. "
            f"Wartezeiten erscheinen zufaellig."
        )
    else:
        interpretation = (
            f"p-Wert {p_value:.4f} <= {alpha}: "
            f"Signifikante Abweichung von Gleichverteilung! "
            f"Wartezeiten folgen nicht dem erwarteten Zufallsmuster."
        )

    return ChiSquareResult(
        keno_typ=keno_typ,
        chi2_statistic=round(float(chi2_stat), 4),
        p_value=round(float(p_value), 6),
        df=n_bins - 1,
        is_uniform=is_uniform,
        interpretation=interpretation,
    )


def detect_outliers(
    data: list[GK1Summary],
    keno_typ: int,
    iqr_multiplier: float = 1.5,
) -> Optional[OutlierInfo]:
    """Erkennt Outlier in Wartezeiten mittels IQR-Methode.

    Outlier sind Werte >= Q3 + iqr_multiplier * IQR

    Args:
        data: Liste von GK1Summary Objekten
        keno_typ: 9 oder 10
        iqr_multiplier: Multiplikator fuer IQR (default 1.5)

    Returns:
        OutlierInfo oder None wenn keine Daten
    """
    filtered = [d for d in data if d.keno_typ == keno_typ]
    if not filtered:
        return None

    waiting_times = np.array([d.vergangene_tage for d in filtered])

    q1 = np.percentile(waiting_times, 25)
    q3 = np.percentile(waiting_times, 75)
    iqr = q3 - q1
    threshold = q3 + iqr_multiplier * iqr

    # Finde Outlier
    outlier_mask = waiting_times >= threshold
    outlier_values = waiting_times[outlier_mask].tolist()
    outlier_dates = [
        filtered[i].datum.strftime("%Y-%m-%d")
        for i, is_outlier in enumerate(outlier_mask)
        if is_outlier
    ]

    return OutlierInfo(
        keno_typ=keno_typ,
        n_outliers=int(np.sum(outlier_mask)),
        outlier_threshold=round(float(threshold), 2),
        outlier_values=[int(v) for v in outlier_values],
        outlier_dates=outlier_dates,
    )


def analyze_gk1_waiting(
    data_path: str | Path,
    n_bins: int = 10,
    alpha: float = 0.05,
) -> GK1WaitingResult:
    """Fuehrt vollstaendige GK1 Wartezeit-Analyse durch.

    Args:
        data_path: Pfad zur GK1Summary CSV-Datei
        n_bins: Anzahl Bins fuer Histogramm und Chi-Quadrat Test
        alpha: Signifikanzniveau fuer Chi-Quadrat Test

    Returns:
        GK1WaitingResult mit allen Analyseergebnissen
    """
    data_path = Path(data_path)
    data = load_gk1_summary_data(data_path)

    logger.info(f"Loaded {len(data)} GK1 records from {data_path.name}")

    # Analyse fuer beide Keno-Typen
    stats_keno9 = calculate_waiting_stats(data, keno_typ=9)
    stats_keno10 = calculate_waiting_stats(data, keno_typ=10)

    chi2_keno9 = chi_square_uniformity_test(data, keno_typ=9, n_bins=n_bins, alpha=alpha)
    chi2_keno10 = chi_square_uniformity_test(data, keno_typ=10, n_bins=n_bins, alpha=alpha)

    histogram_keno9 = calculate_histogram(data, keno_typ=9, n_bins=n_bins)
    histogram_keno10 = calculate_histogram(data, keno_typ=10, n_bins=n_bins)

    outliers_keno9 = detect_outliers(data, keno_typ=9)
    outliers_keno10 = detect_outliers(data, keno_typ=10)

    # Bestimme Gesamtergebnis
    keno9_uniform = chi2_keno9.is_uniform if chi2_keno9 else True
    keno10_uniform = chi2_keno10.is_uniform if chi2_keno10 else True
    acceptance_criteria_met = keno9_uniform and keno10_uniform

    if acceptance_criteria_met:
        hypothesis_result = (
            "HYP-002 NICHT BESTAETIGT: Wartezeiten folgen Zufallsverteilung. "
            "Keine Hinweise auf Jackpot-Bildungs-Zyklen erkennbar."
        )
    else:
        failed_types = []
        if not keno9_uniform:
            failed_types.append("Keno-9")
        if not keno10_uniform:
            failed_types.append("Keno-10")
        hypothesis_result = (
            f"HYP-002 BESTAETIGT: Signifikante Abweichung bei {', '.join(failed_types)}. "
            f"Wartezeit-Muster weichen von Zufallsverteilung ab."
        )

    return GK1WaitingResult(
        analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data_source=str(data_path),
        stats_keno9=stats_keno9,
        stats_keno10=stats_keno10,
        chi2_keno9=chi2_keno9,
        chi2_keno10=chi2_keno10,
        histogram_keno9=histogram_keno9,
        histogram_keno10=histogram_keno10,
        outliers_keno9=outliers_keno9,
        outliers_keno10=outliers_keno10,
        hypothesis_result=hypothesis_result,
        acceptance_criteria_met=acceptance_criteria_met,
    )


def export_result_to_json(
    result: GK1WaitingResult,
    output_path: str | Path,
) -> None:
    """Exportiert Analyseergebnis als JSON.

    Args:
        result: GK1WaitingResult Objekt
        output_path: Pfad zur Ausgabedatei
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Konvertiere dataclasses zu dict
    def to_dict(obj):
        if obj is None:
            return None
        if isinstance(obj, list):
            return [to_dict(item) for item in obj]
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return obj

    data = {
        "analysis_date": result.analysis_date,
        "data_source": result.data_source,
        "stats_keno9": to_dict(result.stats_keno9),
        "stats_keno10": to_dict(result.stats_keno10),
        "chi2_keno9": to_dict(result.chi2_keno9),
        "chi2_keno10": to_dict(result.chi2_keno10),
        "histogram_keno9": to_dict(result.histogram_keno9),
        "histogram_keno10": to_dict(result.histogram_keno10),
        "outliers_keno9": to_dict(result.outliers_keno9),
        "outliers_keno10": to_dict(result.outliers_keno10),
        "hypothesis_result": result.hypothesis_result,
        "acceptance_criteria_met": result.acceptance_criteria_met,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported result to {output_path}")


def run_hyp002_waiting_analysis(
    data_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> GK1WaitingResult:
    """Convenience-Funktion fuer HYP-002 Wartezeit-Analyse.

    Args:
        data_path: Pfad zur GK1Summary CSV-Datei
        output_path: Optional, Pfad zur JSON-Ausgabedatei

    Returns:
        GK1WaitingResult
    """
    result = analyze_gk1_waiting(data_path)

    if output_path:
        export_result_to_json(result, output_path)

    return result


__all__ = [
    "WaitingTimeStats",
    "ChiSquareResult",
    "OutlierInfo",
    "HistogramBin",
    "GK1WaitingResult",
    "load_gk1_summary_data",
    "calculate_waiting_stats",
    "calculate_histogram",
    "chi_square_uniformity_test",
    "detect_outliers",
    "analyze_gk1_waiting",
    "export_result_to_json",
    "run_hyp002_waiting_analysis",
]
