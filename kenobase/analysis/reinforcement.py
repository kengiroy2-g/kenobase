"""HYP-001: Reinforcement-Muster Analyse (Restbetrag).

Analysiert den Restbetrag nach Auszahlung um Muster zu erkennen.
Fragestellung: Gibt es eine Regularitaet im Restbetrag die auf
gesteuerte Gewinnverteilung hindeutet?

Metriken:
- Regularity Score: Wie gleichmaessig ist der Restbetrag ueber Zeit?
- Trend-Analyse: Steigt/faellt der kumulierte Restbetrag?
- Volatilitaet: Wie stark schwankt der Restbetrag?
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class ReinforcementResult:
    """Ergebnis der Restbetrag-Analyse.

    Attributes:
        mean_restbetrag: Durchschnittlicher Restbetrag
        std_restbetrag: Standardabweichung
        cv: Variationskoeffizient
        regularity_score: 1 - CV, Mass fuer Gleichmaessigkeit (0-1)
        trend_slope: Steigung der Trendlinie
        trend_pvalue: p-Wert des Trend-Tests
        has_trend: True wenn signifikanter Trend (p < 0.05)
        autocorr_lag1: Autokorrelation Lag 1
        mean_payout_ratio: Durchschnittliches Auszahlungs-Verhaeltnis
        n_days: Anzahl analysierter Tage
    """

    mean_restbetrag: float
    std_restbetrag: float
    cv: float
    regularity_score: float
    trend_slope: float
    trend_pvalue: float
    has_trend: bool
    autocorr_lag1: float
    mean_payout_ratio: float
    n_days: int


def load_restbetrag_data(
    path: str,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """Laedt Restbetrag-Daten.

    Args:
        path: Pfad zur CSV-Datei
        encoding: Encoding der Datei

    Returns:
        DataFrame mit Restbetrag-Spalten
    """
    df = pd.read_csv(path, delimiter=";", encoding=encoding)

    # Bereinige Spaltennamen
    df.columns = df.columns.str.strip()

    # Parse Datum
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Konvertiere numerische Spalten
    numeric_cols = [
        "Spieleinsatz", "Total_gewinner", "Total_Auszahlung",
        "Restbetrag_nach_Auszahlung", "Kasse"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def calculate_regularity_score(values: np.ndarray) -> float:
    """Berechnet Regularity Score.

    Score = 1 - CV (Variationskoeffizient)
    - Score nahe 1: sehr gleichmaessig
    - Score nahe 0: stark schwankend
    - Score negativ: extrem schwankend (std > mean)

    Args:
        values: Array von numerischen Werten

    Returns:
        Regularity Score (0-1, kann negativ sein)
    """
    mean = np.mean(values)
    std = np.std(values)

    if mean <= 0:
        return 0.0

    cv = std / mean
    return max(0.0, 1 - cv)


def analyze_trend(values: np.ndarray) -> tuple[float, float]:
    """Analysiert linearen Trend in Zeitreihe.

    Args:
        values: Array von numerischen Werten

    Returns:
        (slope, p_value) - Steigung und Signifikanz
    """
    x = np.arange(len(values))
    slope, _, r_value, p_value, _ = stats.linregress(x, values)
    return float(slope), float(p_value)


def calculate_autocorrelation(values: np.ndarray, lag: int = 1) -> float:
    """Berechnet Autokorrelation.

    Args:
        values: Array von numerischen Werten
        lag: Zeitverzoegerung

    Returns:
        Autokorrelation bei gegebenem Lag
    """
    if len(values) <= lag:
        return 0.0

    n = len(values)
    mean = np.mean(values)

    numerator = np.sum((values[lag:] - mean) * (values[:-lag] - mean))
    denominator = np.sum((values - mean) ** 2)

    if denominator == 0:
        return 0.0

    return float(numerator / denominator)


def analyze_reinforcement(
    df: pd.DataFrame,
    restbetrag_col: str = "Restbetrag_nach_Auszahlung",
    spieleinsatz_col: str = "Spieleinsatz",
    auszahlung_col: str = "Total_Auszahlung",
) -> ReinforcementResult:
    """Analysiert Reinforcement-Muster im Restbetrag.

    Args:
        df: DataFrame mit Restbetrag-Daten
        restbetrag_col: Name der Restbetrag-Spalte
        spieleinsatz_col: Name der Spieleinsatz-Spalte
        auszahlung_col: Name der Auszahlungs-Spalte

    Returns:
        ReinforcementResult
    """
    # Sortiere nach Datum
    data = df.sort_values("Datum").copy()

    # Extrahiere Werte
    restbetrag = data[restbetrag_col].dropna().values

    if len(restbetrag) < 10:
        logger.warning(f"Only {len(restbetrag)} rows with Restbetrag data")
        return ReinforcementResult(
            mean_restbetrag=0.0,
            std_restbetrag=0.0,
            cv=0.0,
            regularity_score=0.0,
            trend_slope=0.0,
            trend_pvalue=1.0,
            has_trend=False,
            autocorr_lag1=0.0,
            mean_payout_ratio=0.0,
            n_days=len(restbetrag),
        )

    # Grundlegende Statistiken
    mean_rb = float(np.mean(restbetrag))
    std_rb = float(np.std(restbetrag))
    cv = std_rb / mean_rb if mean_rb > 0 else 0.0

    # Regularity Score
    regularity = calculate_regularity_score(restbetrag)

    # Trend-Analyse
    slope, p_value = analyze_trend(restbetrag)
    has_trend = p_value < 0.05

    # Autokorrelation
    autocorr = calculate_autocorrelation(restbetrag, lag=1)

    # Auszahlungs-Verhaeltnis
    if spieleinsatz_col in data.columns and auszahlung_col in data.columns:
        spieleinsatz = data[spieleinsatz_col].dropna().values
        auszahlung = data[auszahlung_col].dropna().values

        if len(spieleinsatz) > 0 and len(auszahlung) > 0:
            payout_ratio = np.sum(auszahlung) / np.sum(spieleinsatz)
        else:
            payout_ratio = 0.0
    else:
        payout_ratio = 0.0

    logger.info(
        f"Reinforcement Analysis: regularity={regularity:.3f}, "
        f"trend_slope={slope:.1f}, has_trend={has_trend}, "
        f"autocorr={autocorr:.3f}"
    )

    return ReinforcementResult(
        mean_restbetrag=round(mean_rb, 2),
        std_restbetrag=round(std_rb, 2),
        cv=round(cv, 4),
        regularity_score=round(regularity, 4),
        trend_slope=round(slope, 2),
        trend_pvalue=round(p_value, 6),
        has_trend=has_trend,
        autocorr_lag1=round(autocorr, 4),
        mean_payout_ratio=round(float(payout_ratio), 4),
        n_days=len(restbetrag),
    )


def is_suspicious(result: ReinforcementResult, regularity_threshold: float = 0.5) -> bool:
    """Prueft ob Restbetrag-Muster verdaechtig ist.

    Verdaechtig wenn:
    - Regularity Score > threshold (zu gleichmaessig)
    - Signifikanter Trend (p < 0.05)
    - Hohe Autokorrelation (> 0.5)

    Args:
        result: ReinforcementResult
        regularity_threshold: Schwelle fuer Regularity Score

    Returns:
        True wenn verdaechtig
    """
    is_too_regular = result.regularity_score > regularity_threshold
    has_strong_autocorr = abs(result.autocorr_lag1) > 0.5

    return is_too_regular or (result.has_trend and has_strong_autocorr)


__all__ = [
    "ReinforcementResult",
    "load_restbetrag_data",
    "calculate_regularity_score",
    "analyze_trend",
    "calculate_autocorrelation",
    "analyze_reinforcement",
    "is_suspicious",
]
