"""DIST-003: Payout Inference - Reverse Engineering von Zahlen aus Auszahlung.

Ziel: Aus Auszahlungsdaten (payout) auf gezogene Zahlen-Typen zurueckschliessen.
Bei KENO festen Quoten sollte payout_per_winner konstant sein.
Anomalien (hoher CV) deuten auf "unpopulaere" Zahlen-Kombinationen hin.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from kenobase.analysis.distribution import load_quote_details_data
from kenobase.core.keno_quotes import KENO_FIXED_ODDS as EXPECTED_ODDS

logger = logging.getLogger(__name__)


# Erwartete Quoten pro Keno-Typ und Matches (feste KENO-Quoten, 1 Euro Einsatz)
# Single source of truth: kenobase.core.keno_quotes.KENO_FIXED_ODDS


@dataclass
class PayoutInferenceResult:
    """Ergebnis der Payout-Inference Analyse pro Ziehung.

    Attributes:
        date: Ziehungsdatum
        keno_type: Keno-Typ (2-10)
        matches: Anzahl richtiger Zahlen
        winners: Anzahl der Gewinner
        expected_payout: Erwartete Auszahlung (winners * expected_odds)
        actual_payout: Tatsaechliche Auszahlung
        payout_per_winner: Tatsaechliche Auszahlung / Gewinner
        anomaly_score: Abweichung vom Erwartungswert (als Faktor)
        popularity_class: LOW_POPULARITY, NORMAL, HIGH_POPULARITY
    """

    date: str
    keno_type: int
    matches: int
    winners: int
    expected_payout: float
    actual_payout: float
    payout_per_winner: float
    anomaly_score: float
    popularity_class: str


@dataclass
class NumberUnpopularityResult:
    """Aggregiertes Ergebnis pro Zahl ueber alle Ziehungen.

    Attributes:
        number: Die Keno-Zahl (1-70)
        low_popularity_count: Anzahl Ziehungen mit LOW_POPULARITY wo Zahl gezogen
        total_count: Gesamtzahl Ziehungen wo Zahl gezogen
        unpopularity_ratio: low_popularity_count / total_count
    """

    number: int
    low_popularity_count: int
    total_count: int
    unpopularity_ratio: float


@dataclass
class PayoutInferenceSummary:
    """Zusammenfassung der Payout-Inference Analyse.

    Attributes:
        results: Liste aller PayoutInferenceResult
        n_draws: Anzahl analysierter Ziehungen
        low_popularity_count: Anzahl LOW_POPULARITY Tage
        high_popularity_count: Anzahl HIGH_POPULARITY Tage
        normal_count: Anzahl NORMAL Tage
        anomaly_threshold: Verwendeter Schwellwert
        number_rankings: Optional - Liste von NumberUnpopularityResult
    """

    results: list[PayoutInferenceResult]
    n_draws: int
    low_popularity_count: int
    high_popularity_count: int
    normal_count: int
    anomaly_threshold: float
    number_rankings: list[NumberUnpopularityResult] = field(default_factory=list)


def calculate_payout_inference(
    df: pd.DataFrame,
    anomaly_threshold: float = 0.1,
) -> list[PayoutInferenceResult]:
    """Berechnet Payout-Inference fuer alle Ziehungen.

    Fuer jede Ziehung wird geprueft ob payout_per_winner von der
    erwarteten Quote abweicht. Bei festen Quoten sollte CV sehr
    niedrig sein (< 0.01). Abweichungen deuten auf Datenfehler
    oder besondere Ziehungen hin.

    Da KENO feste Quoten hat, fokussieren wir auf Gewinner-Anzahl
    als Signal fuer Zahlen-Popularitaet.

    Args:
        df: DataFrame mit Quote Details Daten
        anomaly_threshold: Relative Abweichung ab der Anomalie erkannt wird

    Returns:
        Liste von PayoutInferenceResult
    """
    results = []

    for _, row in df.iterrows():
        keno_type = int(row["Keno-Typ"])
        matches = int(row["Anzahl richtiger Zahlen"])
        winners = int(row["Anzahl der Gewinner"])
        actual_payout = float(row["Auszahlung"])
        date_str = row["Datum"].strftime("%Y-%m-%d")

        # Erwartete Quote holen
        expected_odds = EXPECTED_ODDS.get((keno_type, matches))
        if expected_odds is None:
            logger.debug(f"No expected odds for ({keno_type}, {matches})")
            continue

        # Berechne erwartete Auszahlung
        expected_payout = winners * expected_odds

        # payout_per_winner (0 wenn keine Gewinner)
        if winners > 0:
            payout_per_winner = actual_payout / winners
        else:
            payout_per_winner = 0.0

        # Anomaly Score: relative Abweichung
        if expected_payout > 0:
            anomaly_score = abs(actual_payout - expected_payout) / expected_payout
        else:
            anomaly_score = 0.0 if actual_payout == 0 else 1.0

        # Popularity Class basierend auf Anomaly Score
        # Bei festen Quoten: Anomaly_Score sollte ~0 sein (Rundungsfehler)
        # Fokus auf Gewinner-Anzahl: wenige Gewinner = unpopulaere Zahlen
        # Viele Gewinner = populaere Zahlen (Birthday-Effekt)
        if anomaly_score > anomaly_threshold:
            # Hohe Abweichung - klassifizieren basierend auf Richtung
            if actual_payout < expected_payout:
                popularity_class = "HIGH_POPULARITY"  # Mehr Gewinner erwartet
            else:
                popularity_class = "LOW_POPULARITY"
        else:
            popularity_class = "NORMAL"

        results.append(
            PayoutInferenceResult(
                date=date_str,
                keno_type=keno_type,
                matches=matches,
                winners=winners,
                expected_payout=round(expected_payout, 2),
                actual_payout=round(actual_payout, 2),
                payout_per_winner=round(payout_per_winner, 2),
                anomaly_score=round(anomaly_score, 4),
                popularity_class=popularity_class,
            )
        )

    logger.info(f"Calculated payout inference for {len(results)} records")
    return results


def aggregate_by_date_and_type(
    results: list[PayoutInferenceResult],
    min_winners: int = 10,
) -> dict[str, dict[int, str]]:
    """Aggregiert Popularity-Class pro Datum und Keno-Typ.

    Args:
        results: Liste von PayoutInferenceResult
        min_winners: Mindest-Gewinner um als relevant zu gelten

    Returns:
        Dict[date][keno_type] -> popularity_class
    """
    aggregated: dict[str, dict[int, str]] = {}

    for r in results:
        if r.winners < min_winners:
            continue

        if r.date not in aggregated:
            aggregated[r.date] = {}

        # Pro Datum und Keno-Typ die dominante Klasse speichern
        # Bei mehreren matches pro Type: LOW_POPULARITY dominiert
        current = aggregated[r.date].get(r.keno_type)
        if current is None:
            aggregated[r.date][r.keno_type] = r.popularity_class
        elif r.popularity_class == "LOW_POPULARITY":
            aggregated[r.date][r.keno_type] = "LOW_POPULARITY"

    return aggregated


def calculate_winner_statistics(
    df: pd.DataFrame,
) -> dict[tuple[int, int], dict[str, float]]:
    """Berechnet Gewinner-Statistiken pro Keno-Typ und Matches.

    Dies ist der Kern-Ansatz: Bei festen Quoten ist die Varianz
    in der Gewinner-Anzahl das Signal fuer Zahlen-Popularitaet.

    Args:
        df: DataFrame mit Quote Details Daten

    Returns:
        Dict[(keno_type, matches)] -> {mean, std, cv, min, max, n}
    """
    stats: dict[tuple[int, int], dict[str, float]] = {}

    grouped = df.groupby(["Keno-Typ", "Anzahl richtiger Zahlen"])

    for (kt, m), group in grouped:
        winners = group["Anzahl der Gewinner"].values

        if len(winners) < 10:
            continue

        mean_w = float(np.mean(winners))
        std_w = float(np.std(winners))
        cv = std_w / mean_w if mean_w > 0 else 0.0

        stats[(int(kt), int(m))] = {
            "mean": round(mean_w, 2),
            "std": round(std_w, 2),
            "cv": round(cv, 4),
            "min": int(np.min(winners)),
            "max": int(np.max(winners)),
            "n": len(winners),
        }

    return stats


def identify_low_popularity_days(
    df: pd.DataFrame,
    winner_stats: dict[tuple[int, int], dict[str, float]],
    z_threshold: float = -1.5,
) -> list[tuple[str, int, int, float]]:
    """Identifiziert Tage mit unterdurchschnittlich vielen Gewinnern.

    Ein Tag gilt als "low_popularity" wenn die Gewinner-Anzahl
    signifikant unter dem Durchschnitt liegt (z-score < threshold).
    Dies deutet auf unpopulaere (nicht-Birthday) Zahlen hin.

    Args:
        df: DataFrame mit Quote Details Daten
        winner_stats: Vorab berechnete Gewinner-Statistiken
        z_threshold: Z-Score unter dem LOW_POPULARITY erkannt wird

    Returns:
        Liste von (date, keno_type, matches, z_score) Tupeln
    """
    low_popularity_days = []

    for _, row in df.iterrows():
        kt = int(row["Keno-Typ"])
        m = int(row["Anzahl richtiger Zahlen"])
        winners = int(row["Anzahl der Gewinner"])
        date_str = row["Datum"].strftime("%Y-%m-%d")

        stats = winner_stats.get((kt, m))
        if stats is None:
            continue

        # Z-Score berechnen
        if stats["std"] > 0:
            z_score = (winners - stats["mean"]) / stats["std"]
        else:
            z_score = 0.0

        if z_score < z_threshold:
            low_popularity_days.append((date_str, kt, m, round(z_score, 2)))

    return low_popularity_days


def join_with_drawn_numbers(
    df_quote: pd.DataFrame,
    df_draws: pd.DataFrame,
) -> pd.DataFrame:
    """Joint Quote-Details mit Ziehungsdaten.

    Args:
        df_quote: Quote Details DataFrame
        df_draws: Ziehungsdaten DataFrame (mit Keno_Z1-Z20)

    Returns:
        Merged DataFrame
    """
    # Normalisiere Datum-Format
    df_quote = df_quote.copy()
    df_draws = df_draws.copy()

    df_quote["Datum"] = pd.to_datetime(df_quote["Datum"])
    df_draws["Datum"] = pd.to_datetime(df_draws["Datum"], format="%d.%m.%Y")

    # Merge auf Datum
    merged = df_quote.merge(df_draws, on="Datum", how="left")

    return merged


def aggregate_number_unpopularity(
    low_popularity_days: list[tuple[str, int, int, float]],
    df_draws: pd.DataFrame,
    min_occurrences: int = 100,
) -> list[NumberUnpopularityResult]:
    """Aggregiert Unpopularitaet auf Zahlen-Ebene.

    Fuer jede Zahl 1-70 wird berechnet wie oft sie an
    LOW_POPULARITY Tagen gezogen wurde relativ zur Gesamtzahl.

    Args:
        low_popularity_days: Liste von LOW_POPULARITY Tagen
        df_draws: Ziehungsdaten DataFrame
        min_occurrences: Mindest-Ziehungen pro Zahl

    Returns:
        Liste von NumberUnpopularityResult, sortiert nach unpopularity_ratio
    """
    # Extrahiere LOW_POPULARITY Daten als Set
    low_pop_dates = {date for date, _, _, _ in low_popularity_days}

    # Normalisiere Datum in df_draws
    df_draws = df_draws.copy()
    df_draws["Datum"] = pd.to_datetime(df_draws["Datum"], format="%d.%m.%Y")
    df_draws["date_str"] = df_draws["Datum"].dt.strftime("%Y-%m-%d")

    # Zahlen-Spalten identifizieren
    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Zaehle pro Zahl
    number_counts: dict[int, dict[str, int]] = {
        n: {"low_pop": 0, "total": 0} for n in range(1, 71)
    }

    for _, row in df_draws.iterrows():
        date_str = row["date_str"]
        is_low_pop = date_str in low_pop_dates

        for col in number_cols:
            if col in row and pd.notna(row[col]):
                number = int(row[col])
                if 1 <= number <= 70:
                    number_counts[number]["total"] += 1
                    if is_low_pop:
                        number_counts[number]["low_pop"] += 1

    # Erstelle Results
    results = []
    for number in range(1, 71):
        total = number_counts[number]["total"]
        low_pop = number_counts[number]["low_pop"]

        if total < min_occurrences:
            continue

        unpop_ratio = low_pop / total if total > 0 else 0.0

        results.append(
            NumberUnpopularityResult(
                number=number,
                low_popularity_count=low_pop,
                total_count=total,
                unpopularity_ratio=round(unpop_ratio, 4),
            )
        )

    # Sortiere nach unpopularity_ratio (absteigend = hoehere Unpopularitaet zuerst)
    results.sort(key=lambda x: x.unpopularity_ratio, reverse=True)

    return results


def run_payout_inference(
    quote_path: str,
    draws_path: Optional[str] = None,
    anomaly_threshold: float = 0.1,
    z_threshold: float = -1.5,
) -> PayoutInferenceSummary:
    """Fuehrt vollstaendige Payout-Inference Analyse durch.

    Args:
        quote_path: Pfad zu Quote Details CSV
        draws_path: Optional - Pfad zu Ziehungsdaten CSV fuer Zahlen-Aggregation
        anomaly_threshold: Schwellwert fuer Anomalie-Erkennung
        z_threshold: Z-Score Schwellwert fuer LOW_POPULARITY

    Returns:
        PayoutInferenceSummary mit allen Ergebnissen
    """
    # Lade Quote Details
    df_quote = load_quote_details_data(quote_path)
    logger.info(f"Loaded {len(df_quote)} quote detail records")

    # Berechne Gewinner-Statistiken
    winner_stats = calculate_winner_statistics(df_quote)
    logger.info(f"Calculated stats for {len(winner_stats)} (keno_type, matches) combinations")

    # Identifiziere LOW_POPULARITY Tage
    low_pop_days = identify_low_popularity_days(df_quote, winner_stats, z_threshold)
    logger.info(f"Found {len(low_pop_days)} low-popularity records")

    # Berechne Payout-Inference fuer alle Records
    results = calculate_payout_inference(df_quote, anomaly_threshold)

    # Zaehle Klassen
    low_count = sum(1 for r in results if r.popularity_class == "LOW_POPULARITY")
    high_count = sum(1 for r in results if r.popularity_class == "HIGH_POPULARITY")
    normal_count = sum(1 for r in results if r.popularity_class == "NORMAL")

    # Zahlen-Aggregation wenn Ziehungsdaten verfuegbar
    number_rankings: list[NumberUnpopularityResult] = []
    if draws_path:
        try:
            df_draws = pd.read_csv(draws_path, encoding="utf-8", sep=";")
            number_rankings = aggregate_number_unpopularity(low_pop_days, df_draws)
            logger.info(f"Aggregated unpopularity for {len(number_rankings)} numbers")
        except Exception as e:
            logger.warning(f"Could not load draws data: {e}")

    summary = PayoutInferenceSummary(
        results=results,
        n_draws=len(results),
        low_popularity_count=low_count,
        high_popularity_count=high_count,
        normal_count=normal_count,
        anomaly_threshold=anomaly_threshold,
        number_rankings=number_rankings,
    )

    return summary


__all__ = [
    "PayoutInferenceResult",
    "NumberUnpopularityResult",
    "PayoutInferenceSummary",
    "EXPECTED_ODDS",
    "calculate_payout_inference",
    "calculate_winner_statistics",
    "identify_low_popularity_days",
    "join_with_drawn_numbers",
    "aggregate_number_unpopularity",
    "run_payout_inference",
]
