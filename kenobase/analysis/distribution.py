"""HYP-001: Gewinnverteilungs-Analyse.

Analysiert die Verteilung von Gewinnen pro Keno-Typ und Gewinnklasse.
Berechnet statistische Kennzahlen und erkennt Anomalien.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.parsing import parse_float_mixed_german, parse_int_mixed_german

logger = logging.getLogger(__name__)


@dataclass
class DistributionResult:
    """Ergebnis der Verteilungsanalyse.

    Attributes:
        keno_type: Keno-Typ (2-10)
        matches: Anzahl richtiger Zahlen
        mean_winners: Durchschnittliche Gewinner pro Ziehung
        std_winners: Standardabweichung
        cv: Variationskoeffizient (std/mean)
        skewness: Schiefe der Verteilung
        kurtosis: Woelbung der Verteilung
        min_winners: Minimum
        max_winners: Maximum
        n_draws: Anzahl analysierter Ziehungen
    """

    keno_type: int
    matches: int
    mean_winners: float
    std_winners: float
    cv: float
    skewness: float
    kurtosis: float
    min_winners: int
    max_winners: int
    n_draws: int


@dataclass
class PayoutRatioResult:
    """Ergebnis der Auszahlung-Gewinner Ratio Analyse.

    Attributes:
        keno_type: Keno-Typ (2-10)
        matches: Anzahl richtiger Zahlen
        mean_payout_per_winner: Durchschnittliche Auszahlung pro Gewinner
        std_payout_per_winner: Standardabweichung
        cv: Variationskoeffizient (std/mean)
        min_payout_per_winner: Minimum
        max_payout_per_winner: Maximum
        n_draws: Anzahl analysierter Ziehungen (mit Gewinner > 0)
        zero_winner_draws: Anzahl Ziehungen ohne Gewinner
    """

    keno_type: int
    matches: int
    mean_payout_per_winner: float
    std_payout_per_winner: float
    cv: float
    min_payout_per_winner: float
    max_payout_per_winner: float
    n_draws: int
    zero_winner_draws: int


@dataclass
class DistributionSummary:
    """Zusammenfassung ueber alle Keno-Typen.

    Attributes:
        results: Liste aller DistributionResult
        total_draws: Gesamtzahl Ziehungen
        anomalies: Liste von (keno_type, matches) mit auffaelliger Verteilung
        overall_cv: Durchschnittlicher Variationskoeffizient
    """

    results: list[DistributionResult]
    total_draws: int
    anomalies: list[tuple[int, int]]
    overall_cv: float


def load_gq_data(
    path: str,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """Laedt Keno GQ (Gewinnquoten) Daten.

    Args:
        path: Pfad zur CSV-Datei
        encoding: Encoding der Datei

    Returns:
        DataFrame mit Spalten: Datum, Keno-Typ, Anzahl richtiger Zahlen,
                               Anzahl der Gewinner, 1 Euro Gewinn
    """
    df = pd.read_csv(path, encoding=encoding)

    # Bereinige Spaltennamen
    df.columns = df.columns.str.strip()

    # Parse Datum
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Bereinige Gewinner-Spalte (mixed formats: 275.0, 3.462, 2.91, ...)
    if "Anzahl der Gewinner" in df.columns:
        df["Anzahl der Gewinner"] = df["Anzahl der Gewinner"].apply(parse_int_mixed_german)

    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def analyze_distribution(
    df: pd.DataFrame,
    keno_type: Optional[int] = None,
    matches: Optional[int] = None,
) -> list[DistributionResult]:
    """Analysiert Gewinner-Verteilung pro Keno-Typ und Gewinnklasse.

    Args:
        df: DataFrame mit GQ-Daten
        keno_type: Optional, filtert auf spezifischen Keno-Typ
        matches: Optional, filtert auf spezifische Anzahl richtiger Zahlen

    Returns:
        Liste von DistributionResult fuer jede Kombination
    """
    results = []

    # Filter anwenden
    data = df.copy()
    if keno_type is not None:
        data = data[data["Keno-Typ"] == keno_type]
    if matches is not None:
        data = data[data["Anzahl richtiger Zahlen"] == matches]

    # Gruppiere nach Keno-Typ und Anzahl richtiger Zahlen
    grouped = data.groupby(["Keno-Typ", "Anzahl richtiger Zahlen"])

    for (kt, m), group in grouped:
        winners = group["Anzahl der Gewinner"].values

        if len(winners) < 10:
            logger.warning(f"Skipping Keno-Typ {kt}, Matches {m}: only {len(winners)} draws")
            continue

        mean_w = float(np.mean(winners))
        std_w = float(np.std(winners))
        cv = std_w / mean_w if mean_w > 0 else 0.0

        # Schiefe und Woelbung
        skew = float(stats.skew(winners)) if len(winners) >= 3 else 0.0
        kurt = float(stats.kurtosis(winners)) if len(winners) >= 4 else 0.0

        results.append(
            DistributionResult(
                keno_type=int(kt),
                matches=int(m),
                mean_winners=round(mean_w, 2),
                std_winners=round(std_w, 2),
                cv=round(cv, 4),
                skewness=round(skew, 4),
                kurtosis=round(kurt, 4),
                min_winners=int(np.min(winners)),
                max_winners=int(np.max(winners)),
                n_draws=len(winners),
            )
        )

    logger.info(f"Analyzed {len(results)} Keno-Typ/Matches combinations")
    return results


def detect_anomalies(
    results: list[DistributionResult],
    cv_threshold: float = 1.0,
    skew_threshold: float = 2.0,
) -> list[tuple[int, int, str]]:
    """Erkennt Anomalien in der Gewinner-Verteilung.

    Anomalien sind:
    - Hoher Variationskoeffizient (CV > threshold): stark schwankend
    - Hohe Schiefe (|skewness| > threshold): asymmetrisch

    Args:
        results: Liste von DistributionResult
        cv_threshold: Schwelle fuer Variationskoeffizient
        skew_threshold: Schwelle fuer Schiefe

    Returns:
        Liste von (keno_type, matches, reason) Tupeln
    """
    anomalies = []

    for r in results:
        reasons = []
        if r.cv > cv_threshold:
            reasons.append(f"high_cv={r.cv:.2f}")
        if abs(r.skewness) > skew_threshold:
            reasons.append(f"high_skew={r.skewness:.2f}")

        if reasons:
            anomalies.append((r.keno_type, r.matches, ", ".join(reasons)))

    return anomalies


def create_summary(
    results: list[DistributionResult],
    anomalies: list[tuple[int, int, str]],
) -> DistributionSummary:
    """Erstellt Zusammenfassung der Verteilungsanalyse.

    Args:
        results: Liste von DistributionResult
        anomalies: Liste von erkannten Anomalien

    Returns:
        DistributionSummary
    """
    total_draws = sum(r.n_draws for r in results) // len(results) if results else 0
    overall_cv = float(np.mean([r.cv for r in results])) if results else 0.0

    return DistributionSummary(
        results=results,
        total_draws=total_draws,
        anomalies=[(kt, m) for kt, m, _ in anomalies],
        overall_cv=round(overall_cv, 4),
    )


def load_quote_details_data(
    path: str,
    encoding: str = "utf-8-sig",
) -> pd.DataFrame:
    """Laedt Keno Quote Details Daten (mit Auszahlung-Spalte).

    Args:
        path: Pfad zur CSV-Datei
        encoding: Encoding der Datei

    Returns:
        DataFrame mit Spalten: Datum, Keno-Typ, Anzahl richtiger Zahlen,
                               Anzahl der Gewinner, Gewinn/1Eur, Auszahlung
    """
    df = pd.read_csv(path, encoding=encoding, sep=";")

    # Bereinige Spaltennamen
    df.columns = df.columns.str.strip()

    # Parse Datum
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Bereinige Gewinner-Spalte (mixed formats possible)
    if "Anzahl der Gewinner" in df.columns:
        df["Anzahl der Gewinner"] = df["Anzahl der Gewinner"].apply(parse_int_mixed_german)

    # Bereinige Auszahlung-Spalte
    if "Auszahlung" in df.columns:
        df["Auszahlung"] = df["Auszahlung"].apply(parse_float_mixed_german)

    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def analyze_payout_ratio(
    df: pd.DataFrame,
    keno_type: Optional[int] = None,
    matches: Optional[int] = None,
) -> list[PayoutRatioResult]:
    """Analysiert Auszahlung-Gewinner Ratio pro Keno-Typ und Gewinnklasse.

    Berechnet payout_per_winner = Auszahlung / Anzahl der Gewinner
    fuer jede Ziehung und aggregiert Statistiken.

    Args:
        df: DataFrame mit Quote Details Daten (muss Auszahlung-Spalte enthalten)
        keno_type: Optional, filtert auf spezifischen Keno-Typ
        matches: Optional, filtert auf spezifische Anzahl richtiger Zahlen

    Returns:
        Liste von PayoutRatioResult fuer jede Kombination
    """
    results = []

    # Filter anwenden
    data = df.copy()
    if keno_type is not None:
        data = data[data["Keno-Typ"] == keno_type]
    if matches is not None:
        data = data[data["Anzahl richtiger Zahlen"] == matches]

    # Gruppiere nach Keno-Typ und Anzahl richtiger Zahlen
    grouped = data.groupby(["Keno-Typ", "Anzahl richtiger Zahlen"])

    for (kt, m), group in grouped:
        winners = group["Anzahl der Gewinner"].values
        payouts = group["Auszahlung"].values

        # Zaehle Ziehungen ohne Gewinner
        zero_winner_mask = winners == 0
        zero_winner_draws = int(np.sum(zero_winner_mask))

        # Berechne payout_per_winner nur fuer Ziehungen mit Gewinnern
        non_zero_mask = ~zero_winner_mask
        n_draws_with_winners = int(np.sum(non_zero_mask))

        if n_draws_with_winners < 5:
            logger.warning(
                f"Skipping Keno-Typ {kt}, Matches {m}: only {n_draws_with_winners} draws with winners"
            )
            continue

        # payout_per_winner = Auszahlung / Anzahl der Gewinner
        payout_per_winner = payouts[non_zero_mask] / winners[non_zero_mask]

        mean_ppw = float(np.mean(payout_per_winner))
        std_ppw = float(np.std(payout_per_winner))
        cv = std_ppw / mean_ppw if mean_ppw > 0 else 0.0

        results.append(
            PayoutRatioResult(
                keno_type=int(kt),
                matches=int(m),
                mean_payout_per_winner=round(mean_ppw, 2),
                std_payout_per_winner=round(std_ppw, 2),
                cv=round(cv, 4),
                min_payout_per_winner=round(float(np.min(payout_per_winner)), 2),
                max_payout_per_winner=round(float(np.max(payout_per_winner)), 2),
                n_draws=n_draws_with_winners,
                zero_winner_draws=zero_winner_draws,
            )
        )

    logger.info(f"Analyzed payout ratio for {len(results)} Keno-Typ/Matches combinations")
    return results


def detect_payout_ratio_anomalies(
    results: list[PayoutRatioResult],
    cv_threshold: float = 0.1,
) -> list[tuple[int, int, str]]:
    """Erkennt Anomalien in der Auszahlung-Gewinner Ratio.

    Bei festen Quoten sollte payout_per_winner = Quote sein.
    Hoher CV deutet auf Anomalien hin (z.B. Rundungsfehler, Datenfehler).

    Args:
        results: Liste von PayoutRatioResult
        cv_threshold: Schwelle fuer Variationskoeffizient (Standard: 0.1 = 10%)

    Returns:
        Liste von (keno_type, matches, reason) Tupeln
    """
    anomalies = []

    for r in results:
        reasons = []
        if r.cv > cv_threshold:
            reasons.append(f"high_cv={r.cv:.4f}")
        if r.zero_winner_draws > r.n_draws * 0.5:
            reasons.append(f"many_zero_draws={r.zero_winner_draws}/{r.n_draws + r.zero_winner_draws}")

        if reasons:
            anomalies.append((r.keno_type, r.matches, ", ".join(reasons)))

    return anomalies


__all__ = [
    "DistributionResult",
    "DistributionSummary",
    "PayoutRatioResult",
    "load_gq_data",
    "load_quote_details_data",
    "analyze_distribution",
    "analyze_payout_ratio",
    "detect_anomalies",
    "detect_payout_ratio_anomalies",
    "create_summary",
]
