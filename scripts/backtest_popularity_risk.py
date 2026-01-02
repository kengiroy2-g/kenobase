#!/usr/bin/env python
"""Backtest Script fuer Popularity-Risk Strategie (POP-001).

Testet ob die Vermeidung populaerer Zahlen zu hoeherem ROI fuehrt.

Hypothese:
- Zahlen mit niedrigem Popularity-Risk haben weniger Konkurrenz
- Weniger Konkurrenz = hoeherer individueller Gewinn bei Treffer
- Erwartung: >10% ROI-Verbesserung vs Random-Baseline

Usage:
    python scripts/backtest_popularity_risk.py --config config/keno.yaml
    python scripts/backtest_popularity_risk.py --draws-file data/keno_draws.csv
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.popularity_risk import (
    calculate_popularity_risk_score,
    should_play,
    PopularityRiskLevel,
)
from kenobase.core.data_loader import DataLoader
from kenobase.core.config import Config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Ergebnis eines Popularity-Risk Backtests."""

    strategy_name: str
    period_start: str
    period_end: str
    n_draws: int

    # Popularity-Metriken
    avg_popularity_score: float
    low_popularity_draws: int
    high_popularity_draws: int

    # Treffer-Statistiken
    avg_matches_random: float
    avg_matches_low_pop: float
    avg_matches_high_pop: float

    # ROI-Schaetzung (relativ)
    estimated_roi_improvement: float
    competition_reduction: float

    # Null-Model Vergleich
    null_model_mean: float
    null_model_std: float
    p_value_estimate: float

    def to_dict(self) -> dict:
        """Serialisiere zu Dictionary."""
        return asdict(self)


def run_backtest(
    draws_df,
    keno_type: int = 6,
    n_random_samples: int = 100,
    max_risk_score: float = 0.5,
) -> BacktestResult:
    """
    Fuehre Popularity-Risk Backtest durch.

    Vergleicht:
    1. Random-Baseline (zufaellige Zahlen)
    2. Low-Popularity Strategie (Score < max_risk_score)
    3. High-Popularity Strategie (Score > 0.7)

    Args:
        draws_df: DataFrame mit Ziehungen (Spalten: datum, n1-n20)
        keno_type: KENO-Typ (Anzahl Zahlen)
        n_random_samples: Anzahl Random-Samples pro Ziehung
        max_risk_score: Grenzwert fuer Low-Popularity

    Returns:
        BacktestResult
    """
    np.random.seed(42)

    results = {
        "random": [],
        "low_pop": [],
        "high_pop": [],
    }
    popularity_scores = []

    # Identifiziere Zahlen-Spalten
    num_cols = [c for c in draws_df.columns if c.startswith('n') and c[1:].isdigit()]
    num_cols = sorted(num_cols, key=lambda x: int(x[1:]))[:20]

    low_pop_count = 0
    high_pop_count = 0

    for idx, row in draws_df.iterrows():
        # Extrahiere gezogene Zahlen
        try:
            drawn = [int(row[c]) for c in num_cols if not np.isnan(row[c])]
        except (ValueError, TypeError):
            continue

        if len(drawn) != 20:
            continue

        drawn_set = set(drawn)

        # Analysiere Popularitaet der Ziehung
        draw_risk = calculate_popularity_risk_score(drawn)
        popularity_scores.append(draw_risk.score)

        if draw_risk.score < max_risk_score:
            low_pop_count += 1
        if draw_risk.score > 0.7:
            high_pop_count += 1

        # 1. Random Baseline
        for _ in range(n_random_samples):
            random_nums = set(np.random.choice(range(1, 71), size=keno_type, replace=False))
            matches = len(random_nums & drawn_set)
            results["random"].append(matches)

        # 2. Low-Popularity Strategie
        # Generiere Kombination mit niedrigem Popularity-Score
        low_pop_nums = generate_low_popularity_numbers(keno_type, max_risk_score)
        low_matches = len(set(low_pop_nums) & drawn_set)
        results["low_pop"].append(low_matches)

        # 3. High-Popularity Strategie (Gegenprobe)
        high_pop_nums = generate_high_popularity_numbers(keno_type)
        high_matches = len(set(high_pop_nums) & drawn_set)
        results["high_pop"].append(high_matches)

    if not results["random"]:
        raise ValueError("Keine validen Ziehungen gefunden")

    # Berechne Statistiken
    avg_random = np.mean(results["random"])
    avg_low_pop = np.mean(results["low_pop"])
    avg_high_pop = np.mean(results["high_pop"])

    # ROI-Schaetzung basierend auf Winner-Korrelation (HYP-004)
    # Weniger Konkurrenz bei Low-Pop = hoeherer individueller Gewinn
    # Annahme: 30% mehr Gewinner bei High-Pop (aus Birthday-Analyse)
    competition_reduction = 1.0 - (np.mean(popularity_scores) / 1.3)

    # Geschaetzter ROI-Improvement (relativ zu Random)
    # Treffer-Rate * Konkurrenz-Reduktion
    if avg_random > 0:
        roi_improvement = (avg_low_pop / avg_random) * (1 + competition_reduction) - 1
    else:
        roi_improvement = 0.0

    # Null-Model: Permutations-Test Schaetzung
    null_model_mean = np.mean(results["random"])
    null_model_std = np.std(results["random"]) / np.sqrt(len(results["low_pop"]))

    if null_model_std > 0:
        z_score = (avg_low_pop - null_model_mean) / null_model_std
        # Einfache p-Value Schaetzung (normal approximation)
        from scipy import stats
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    else:
        p_value = 1.0

    return BacktestResult(
        strategy_name=f"PopularityRisk-{max_risk_score:.0%}",
        period_start=str(draws_df['datum'].min()),
        period_end=str(draws_df['datum'].max()),
        n_draws=len(results["low_pop"]),
        avg_popularity_score=float(np.mean(popularity_scores)),
        low_popularity_draws=low_pop_count,
        high_popularity_draws=high_pop_count,
        avg_matches_random=float(avg_random),
        avg_matches_low_pop=float(avg_low_pop),
        avg_matches_high_pop=float(avg_high_pop),
        estimated_roi_improvement=float(roi_improvement),
        competition_reduction=float(competition_reduction),
        null_model_mean=float(null_model_mean),
        null_model_std=float(null_model_std),
        p_value_estimate=float(p_value),
    )


def generate_low_popularity_numbers(
    n: int,
    max_risk_score: float = 0.5,
    max_attempts: int = 100,
) -> list[int]:
    """Generiere n Zahlen mit niedrigem Popularity-Score."""
    # Bevorzuge Non-Birthday Zahlen (32-70)
    for _ in range(max_attempts):
        # 80% aus 32-70, 20% aus 1-31
        n_high = int(n * 0.8)
        n_low = n - n_high

        high_nums = list(np.random.choice(range(32, 71), size=min(n_high, 39), replace=False))
        low_nums = list(np.random.choice(range(1, 32), size=min(n_low, 31), replace=False))

        numbers = high_nums + low_nums
        if len(numbers) < n:
            # Auffuellen falls noetig
            remaining = list(set(range(1, 71)) - set(numbers))
            numbers.extend(np.random.choice(remaining, size=n - len(numbers), replace=False))

        numbers = numbers[:n]

        try:
            risk = calculate_popularity_risk_score(numbers)
            if risk.score < max_risk_score:
                return sorted(numbers)
        except ValueError:
            continue

    # Fallback: Nur hohe Zahlen
    return sorted(np.random.choice(range(40, 71), size=n, replace=False))


def generate_high_popularity_numbers(n: int) -> list[int]:
    """Generiere n Zahlen mit hohem Popularity-Score."""
    # Bevorzuge Birthday-Zahlen (1-31) und Pattern-Zahlen
    pattern_pool = [7, 11, 13, 17, 21, 10, 20, 30, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    pattern_pool = list(set(pattern_pool))

    if len(pattern_pool) >= n:
        return sorted(np.random.choice(pattern_pool, size=n, replace=False))
    else:
        # Auffuellen mit anderen Birthday-Zahlen
        remaining = list(set(range(1, 32)) - set(pattern_pool))
        combined = pattern_pool + list(np.random.choice(remaining, size=n - len(pattern_pool), replace=False))
        return sorted(combined[:n])


def main():
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="Backtest Popularity-Risk Strategie"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/default.yaml",
        help="Pfad zur Config-Datei",
    )
    parser.add_argument(
        "--draws-file",
        type=str,
        help="Pfad zur Ziehungs-Datei (ueberschreibt Config)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/popularity_risk_backtest.json",
        help="Ausgabe-Pfad",
    )
    parser.add_argument(
        "--keno-type",
        type=int,
        default=6,
        help="KENO-Typ (Anzahl Zahlen)",
    )
    parser.add_argument(
        "--max-risk-score",
        type=float,
        default=0.5,
        help="Max Popularity-Score fuer Low-Pop Strategie",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=100,
        help="Anzahl Random-Samples pro Ziehung",
    )

    args = parser.parse_args()

    # Lade Config
    config_path = Path(args.config)
    if config_path.exists():
        config = Config.from_yaml(config_path)
    else:
        logger.warning(f"Config nicht gefunden: {config_path}")
        config = Config()

    # Lade Daten
    if args.draws_file:
        draws_path = Path(args.draws_file)
    else:
        draws_path = Path(config.data.raw_path) / "keno_draws.csv"

    if not draws_path.exists():
        # Fallback auf Keno_GPTs Daten
        alt_paths = [
            Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv"),
            Path("data/keno_draws.csv"),
        ]
        for alt in alt_paths:
            if alt.exists():
                draws_path = alt
                break

    if not draws_path.exists():
        logger.error(f"Keine Ziehungsdaten gefunden: {draws_path}")
        sys.exit(1)

    logger.info(f"Lade Daten von: {draws_path}")

    # Lade DataFrame
    import pandas as pd
    draws_df = pd.read_csv(draws_path, encoding="utf-8")

    # Normalisiere Datums-Spalte
    if "Datum" in draws_df.columns:
        draws_df = draws_df.rename(columns={"Datum": "datum"})
    if "datum" in draws_df.columns:
        draws_df["datum"] = pd.to_datetime(draws_df["datum"], format="%d.%m.%Y", errors="coerce")

    logger.info(f"Geladen: {len(draws_df)} Zeilen")

    # Fuehre Backtest durch
    try:
        result = run_backtest(
            draws_df,
            keno_type=args.keno_type,
            n_random_samples=args.n_samples,
            max_risk_score=args.max_risk_score,
        )
    except Exception as e:
        logger.error(f"Backtest fehlgeschlagen: {e}")
        sys.exit(1)

    # Ausgabe
    print("\n" + "=" * 60)
    print("POPULARITY-RISK BACKTEST ERGEBNISSE")
    print("=" * 60)
    print(f"\nStrategie: {result.strategy_name}")
    print(f"Zeitraum: {result.period_start} bis {result.period_end}")
    print(f"Ziehungen: {result.n_draws}")
    print(f"\n--- Popularity Metriken ---")
    print(f"Durchschn. Popularity-Score: {result.avg_popularity_score:.4f}")
    print(f"Low-Popularity Ziehungen: {result.low_popularity_draws}")
    print(f"High-Popularity Ziehungen: {result.high_popularity_draws}")
    print(f"\n--- Treffer-Statistiken ---")
    print(f"Random Baseline: {result.avg_matches_random:.4f} Treffer/Ziehung")
    print(f"Low-Popularity: {result.avg_matches_low_pop:.4f} Treffer/Ziehung")
    print(f"High-Popularity: {result.avg_matches_high_pop:.4f} Treffer/Ziehung")
    print(f"\n--- ROI-Schaetzung ---")
    print(f"Geschaetzter ROI-Improvement: {result.estimated_roi_improvement:.2%}")
    print(f"Konkurrenz-Reduktion: {result.competition_reduction:.2%}")
    print(f"\n--- Null-Model Validierung ---")
    print(f"Null-Model Mean: {result.null_model_mean:.4f}")
    print(f"Null-Model Std: {result.null_model_std:.4f}")
    print(f"P-Value (geschaetzt): {result.p_value_estimate:.4f}")

    # Bewertung
    print(f"\n--- BEWERTUNG ---")
    if result.estimated_roi_improvement > 0.1:
        print("POSITIV: >10% ROI-Verbesserung geschaetzt")
    else:
        print(f"NEUTRAL: ROI-Verbesserung unter 10% ({result.estimated_roi_improvement:.1%})")

    if result.p_value_estimate < 0.1:
        print("SIGNIFIKANT: p < 0.1 (Null-Model rejected)")
    else:
        print(f"NICHT SIGNIFIKANT: p = {result.p_value_estimate:.2f}")

    # Speichere Ergebnis
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    logger.info(f"Ergebnis gespeichert: {output_path}")
    print(f"\n[Ergebnis gespeichert: {output_path}]")


if __name__ == "__main__":
    main()
