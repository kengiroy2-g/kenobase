#!/usr/bin/env python
"""
HYP-001: Vollstaendige Gewinnklassen-Verteilungsmuster Analyse

Kombiniert:
1. Gewinnverteilungs-Statistiken (distribution.py)
2. Near-Miss Analyse (near_miss.py)
3. Gewinnklassen-Matrix (9 Keno-Typen x bis 11 Matches)
4. Zeitliche Korrelation (Autocorrelation der Gewinner-Zeitreihe)

Akzeptanzkriterien:
- AC1: Near-Miss Haeufigkeit fuer Typ 8/9/10 berechnet
- AC2: Gewinnklassen-Matrix erstellt (9x11)
- AC3: Zeitliche Korrelation dokumentiert
- AC4: Hypothese bewertet (BESTAETIGT/TEILWEISE/FALSIFIZIERT)
- AC5: Report in results/hyp001_distribution_complete.json
- AC6: Unit-Tests >= 3 PASSED (separat in tests/unit/test_distribution.py)

Repro: python scripts/analyze_hyp001_complete.py -> results/hyp001_distribution_complete.json
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import argparse
import numpy as np
import pandas as pd
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.distribution import (
    DistributionResult,
    analyze_distribution,
    create_summary,
    detect_anomalies,
    load_gq_data,
)
from kenobase.analysis.near_miss import (
    NearMissResult,
    analyze_all_near_miss,
    count_significant_anomalies,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class TemporalCorrelationResult:
    """Ergebnis der zeitlichen Korrelationsanalyse.

    Attributes:
        lag: Lag in Tagen
        autocorr: Autocorrelation-Koeffizient
        p_value: p-Wert (H0: keine Korrelation)
        is_significant: True wenn p < 0.05
    """

    lag: int
    autocorr: float
    p_value: float
    is_significant: bool


@dataclass
class GewinnklassenMatrixEntry:
    """Eintrag in der Gewinnklassen-Matrix.

    Attributes:
        keno_type: Keno-Typ (2-10)
        matches: Anzahl richtiger Zahlen
        total_winners: Gesamtzahl Gewinner im Zeitraum
        mean_winners: Durchschnittliche Gewinner pro Ziehung
        cv: Variationskoeffizient
        n_draws: Anzahl Ziehungen
    """

    keno_type: int
    matches: int
    total_winners: int
    mean_winners: float
    cv: float
    n_draws: int


@dataclass
class HYP001CompleteResult:
    """Vollstaendiges Ergebnis der HYP-001 Analyse.

    Attributes:
        analysis_date: Datum der Analyse
        data_source: Pfad zur Datenquelle
        period_start: Startdatum
        period_end: Enddatum
        n_draws: Anzahl Ziehungen
        distribution_results: Verteilungsanalyse pro Gewinnklasse
        near_miss_results: Near-Miss Analyse pro Keno-Typ
        gewinnklassen_matrix: Matrix aller Gewinnklassen
        temporal_correlations: Zeitliche Autokorrelation
        anomalies: Erkannte Anomalien
        hypothesis_evaluation: Bewertung der Hypothese
        summary_stats: Zusammenfassende Statistiken
    """

    analysis_date: str
    data_source: str
    period_start: str
    period_end: str
    n_draws: int
    distribution_results: list[dict]
    near_miss_results: list[dict]
    gewinnklassen_matrix: list[dict]
    temporal_correlations: list[dict]
    anomalies: list[dict]
    hypothesis_evaluation: dict
    summary_stats: dict


def calculate_temporal_correlation(
    df: pd.DataFrame,
    max_lag: int = 7,
) -> list[TemporalCorrelationResult]:
    """Berechnet zeitliche Autokorrelation der Gewinnerzahlen.

    Testet ob Gewinnerzahlen von einem Tag mit folgenden Tagen korrelieren.
    Eine signifikante Autokorrelation wuerde auf nicht-zufaellige Steuerung hindeuten.

    Args:
        df: DataFrame mit GQ-Daten
        max_lag: Maximaler Lag in Tagen

    Returns:
        Liste von TemporalCorrelationResult pro Lag
    """
    results = []

    # Aggregiere Gewinner pro Tag
    daily = df.groupby("Datum")["Anzahl der Gewinner"].sum().sort_index()

    if len(daily) < max_lag + 10:
        logger.warning(f"Nicht genuegend Daten fuer Autokorrelation: {len(daily)} Tage")
        return results

    values = daily.values

    for lag in range(1, max_lag + 1):
        if len(values) <= lag:
            continue

        # Berechne Autokorrelation
        x = values[:-lag]
        y = values[lag:]

        if len(x) < 10:
            continue

        # Pearson Korrelation
        corr, p_value = stats.pearsonr(x, y)

        results.append(
            TemporalCorrelationResult(
                lag=lag,
                autocorr=round(float(corr), 4),
                p_value=round(float(p_value), 6),
                is_significant=float(p_value) < 0.05,
            )
        )

    return results


def create_gewinnklassen_matrix(
    df: pd.DataFrame,
) -> list[GewinnklassenMatrixEntry]:
    """Erstellt vollstaendige Gewinnklassen-Matrix (9x11).

    Args:
        df: DataFrame mit GQ-Daten

    Returns:
        Liste aller Gewinnklassen-Eintraege
    """
    matrix = []

    for keno_type in range(2, 11):  # 9 Keno-Typen
        type_data = df[df["Keno-Typ"] == keno_type]

        for matches in range(0, keno_type + 1):  # 0 bis max Treffer
            match_data = type_data[type_data["Anzahl richtiger Zahlen"] == matches]

            if len(match_data) == 0:
                continue

            winners = match_data["Anzahl der Gewinner"].values
            total = int(np.sum(winners))
            mean_w = float(np.mean(winners)) if len(winners) > 0 else 0.0
            std_w = float(np.std(winners)) if len(winners) > 1 else 0.0
            cv = std_w / mean_w if mean_w > 0 else 0.0

            matrix.append(
                GewinnklassenMatrixEntry(
                    keno_type=keno_type,
                    matches=matches,
                    total_winners=total,
                    mean_winners=round(mean_w, 2),
                    cv=round(cv, 4),
                    n_draws=len(match_data),
                )
            )

    return matrix


def evaluate_hypothesis(
    distribution_results: list[DistributionResult],
    near_miss_results: list[NearMissResult],
    temporal_correlations: list[TemporalCorrelationResult],
    anomalies: list[tuple],
) -> dict:
    """Bewertet die HYP-001 Hypothese.

    Hypothese: Gewinnklassen werden so gesteuert dass:
    1. Auszahlungsquote stabil bleibt
    2. Near-Miss Faelle ueberdurchschnittlich haeufig sind
    3. Zeitliche Muster existieren

    Args:
        distribution_results: Verteilungsanalyse
        near_miss_results: Near-Miss Analyse
        temporal_correlations: Autokorrelation
        anomalies: Erkannte Anomalien

    Returns:
        Dict mit Bewertung
    """
    # 1. Pruefe Stabilitaet (niedrige CV = verdaechtig stabil)
    avg_cv = np.mean([r.cv for r in distribution_results]) if distribution_results else 0
    stability_suspicious = avg_cv < 0.3  # Sehr stabil = verdaechtig

    # 2. Pruefe Near-Miss Anomalien
    near_miss_significant = count_significant_anomalies(near_miss_results)
    near_miss_suspicious = near_miss_significant >= 2  # >= 2 Keno-Typen mit Anomalie

    # 3. Pruefe zeitliche Korrelation
    significant_correlations = [r for r in temporal_correlations if r.is_significant]
    temporal_suspicious = len(significant_correlations) >= 2

    # 4. Anzahl Anomalien
    anomaly_count = len(anomalies)
    anomaly_suspicious = anomaly_count >= 3

    # Gesamtbewertung
    suspicious_count = sum([
        stability_suspicious,
        near_miss_suspicious,
        temporal_suspicious,
        anomaly_suspicious,
    ])

    if suspicious_count >= 3:
        verdict = "BESTAETIGT"
        confidence = "HOCH"
        explanation = "Mehrere Indikatoren deuten auf nicht-zufaellige Steuerung hin"
    elif suspicious_count >= 2:
        verdict = "TEILWEISE"
        confidence = "MITTEL"
        explanation = "Einige Anomalien gefunden, aber nicht eindeutig"
    else:
        verdict = "FALSIFIZIERT"
        confidence = "MITTEL"
        explanation = "Verteilung entspricht weitgehend zufaelligem Verhalten"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": explanation,
        "indicators": {
            "stability_suspicious": stability_suspicious,
            "avg_cv": round(avg_cv, 4),
            "near_miss_significant_count": near_miss_significant,
            "near_miss_suspicious": near_miss_suspicious,
            "temporal_significant_count": len(significant_correlations),
            "temporal_suspicious": temporal_suspicious,
            "anomaly_count": anomaly_count,
            "anomaly_suspicious": anomaly_suspicious,
        },
        "suspicious_indicators": suspicious_count,
        "total_indicators": 4,
    }


def run_hyp001_complete(
    data_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> HYP001CompleteResult:
    """Fuehrt vollstaendige HYP-001 Analyse durch.

    Args:
        data_path: Pfad zur GQ-Datendatei
        output_path: Pfad fuer JSON-Output

    Returns:
        HYP001CompleteResult
    """
    # Bestimme Pfade
    if data_path is None:
        data_path = "Keno_GPTs/Keno_GQ_2022_2023-2024.csv"

    if output_path is None:
        output_path = "results/hyp001_distribution_complete.json"

    data_file = Path(data_path)
    if not data_file.exists():
        # Versuche absoluten Pfad
        data_file = Path(__file__).parent.parent / data_path

    logger.info(f"Lade Daten von: {data_file}")

    # Lade Daten
    df = load_gq_data(str(data_file))
    n_draws = df["Datum"].nunique()

    logger.info(f"Geladene Zeilen: {len(df)}, Ziehungstage: {n_draws}")
    logger.info(f"Zeitraum: {df['Datum'].min()} bis {df['Datum'].max()}")

    # 1. Verteilungsanalyse
    logger.info("1/4: Verteilungsanalyse...")
    distribution_results = analyze_distribution(df)

    # 2. Near-Miss Analyse
    logger.info("2/4: Near-Miss Analyse...")
    near_miss_results = analyze_all_near_miss(df)

    # 3. Gewinnklassen-Matrix
    logger.info("3/4: Gewinnklassen-Matrix erstellen...")
    gewinnklassen_matrix = create_gewinnklassen_matrix(df)

    # 4. Zeitliche Korrelation
    logger.info("4/4: Zeitliche Korrelation berechnen...")
    temporal_correlations = calculate_temporal_correlation(df)

    # Anomalien erkennen
    anomalies = detect_anomalies(distribution_results)

    # Hypothese bewerten
    logger.info("Bewerte Hypothese...")
    hypothesis_eval = evaluate_hypothesis(
        distribution_results,
        near_miss_results,
        temporal_correlations,
        anomalies,
    )

    # Zusammenfassende Statistiken
    summary_stats = {
        "total_distribution_results": len(distribution_results),
        "total_near_miss_results": len(near_miss_results),
        "total_matrix_entries": len(gewinnklassen_matrix),
        "total_temporal_lags": len(temporal_correlations),
        "total_anomalies": len(anomalies),
        "near_miss_significant": count_significant_anomalies(near_miss_results),
        "avg_cv": round(
            np.mean([r.cv for r in distribution_results]) if distribution_results else 0,
            4,
        ),
        "max_cv": round(
            max([r.cv for r in distribution_results]) if distribution_results else 0,
            4,
        ),
    }

    # Erstelle Ergebnis
    result = HYP001CompleteResult(
        analysis_date=datetime.now().isoformat(),
        data_source=str(data_file),
        period_start=df["Datum"].min().isoformat(),
        period_end=df["Datum"].max().isoformat(),
        n_draws=n_draws,
        distribution_results=[asdict(r) for r in distribution_results],
        near_miss_results=[asdict(r) for r in near_miss_results],
        gewinnklassen_matrix=[asdict(e) for e in gewinnklassen_matrix],
        temporal_correlations=[asdict(r) for r in temporal_correlations],
        anomalies=[
            {"keno_type": kt, "matches": m, "reason": reason}
            for kt, m, reason in anomalies
        ],
        hypothesis_evaluation=hypothesis_eval,
        summary_stats=summary_stats,
    )

    # Speichere Ergebnis
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"Ergebnis gespeichert: {output_file}")

    return result


def print_summary(result: HYP001CompleteResult) -> None:
    """Druckt Zusammenfassung der Analyse."""
    print("\n" + "=" * 70)
    print("HYP-001: GEWINNKLASSEN-VERTEILUNGSMUSTER - VOLLSTAENDIGE ANALYSE")
    print("=" * 70)

    print(f"\nDatenquelle: {result.data_source}")
    print(f"Zeitraum: {result.period_start[:10]} bis {result.period_end[:10]}")
    print(f"Ziehungstage: {result.n_draws}")

    print("\n" + "-" * 70)
    print("1. VERTEILUNGSANALYSE")
    print(f"   Analysierte Gewinnklassen: {result.summary_stats['total_distribution_results']}")
    print(f"   Durchschnittliche CV: {result.summary_stats['avg_cv']:.4f}")
    print(f"   Maximale CV: {result.summary_stats['max_cv']:.4f}")

    print("\n" + "-" * 70)
    print("2. NEAR-MISS ANALYSE")
    print(f"   Analysierte Keno-Typen: {result.summary_stats['total_near_miss_results']}")
    print(f"   Signifikante Anomalien: {result.summary_stats['near_miss_significant']}")

    # Near-Miss Details fuer Typ 8/9/10
    for nm in result.near_miss_results:
        if nm["keno_type"] in [8, 9, 10]:
            status = "SIGNIFIKANT" if nm["is_significant"] else "normal"
            print(
                f"   Typ {nm['keno_type']}: ratio={nm['near_miss_ratio']:.2f}, "
                f"expected={nm['expected_ratio']:.2f}, p={nm['p_value']:.4f} [{status}]"
            )

    print("\n" + "-" * 70)
    print("3. GEWINNKLASSEN-MATRIX")
    print(f"   Matrix-Eintraege: {result.summary_stats['total_matrix_entries']}")

    # Zeige Hauptgewinnklassen
    print("\n   Hauptgewinnklassen (Jackpots):")
    for entry in result.gewinnklassen_matrix:
        if entry["keno_type"] == entry["matches"] and entry["keno_type"] >= 8:
            print(
                f"   Typ {entry['keno_type']}/{entry['matches']}: "
                f"Total={entry['total_winners']}, Mean={entry['mean_winners']:.2f}, CV={entry['cv']:.4f}"
            )

    print("\n" + "-" * 70)
    print("4. ZEITLICHE KORRELATION")
    print(f"   Getestete Lags: {result.summary_stats['total_temporal_lags']}")

    sig_count = 0
    for tc in result.temporal_correlations:
        if tc["is_significant"]:
            sig_count += 1
            print(f"   Lag {tc['lag']}: r={tc['autocorr']:.4f}, p={tc['p_value']:.6f} [SIGNIFIKANT]")

    if sig_count == 0:
        print("   Keine signifikanten Autokorrelationen gefunden")

    print("\n" + "-" * 70)
    print("5. ANOMALIEN")
    print(f"   Erkannte Anomalien: {result.summary_stats['total_anomalies']}")

    for anom in result.anomalies[:5]:  # Max 5 zeigen
        print(f"   Typ {anom['keno_type']}/{anom['matches']}: {anom['reason']}")

    print("\n" + "=" * 70)
    print("HYPOTHESEN-BEWERTUNG")
    print("=" * 70)

    eval_data = result.hypothesis_evaluation
    print(f"\n   VERDICT: {eval_data['verdict']}")
    print(f"   Konfidenz: {eval_data['confidence']}")
    print(f"   Erklaerung: {eval_data['explanation']}")
    print(f"\n   Verdaechtige Indikatoren: {eval_data['suspicious_indicators']}/{eval_data['total_indicators']}")

    indicators = eval_data["indicators"]
    print(f"   - Stabilitaet verdaechtig (CV < 0.3): {indicators['stability_suspicious']} (CV={indicators['avg_cv']:.4f})")
    print(f"   - Near-Miss verdaechtig (>=2 sig.): {indicators['near_miss_suspicious']} ({indicators['near_miss_significant_count']} sig.)")
    print(f"   - Temporal verdaechtig (>=2 sig.): {indicators['temporal_suspicious']} ({indicators['temporal_significant_count']} sig.)")
    print(f"   - Anomalien verdaechtig (>=3): {indicators['anomaly_suspicious']} ({indicators['anomaly_count']} Anomalien)")

    print("\n" + "=" * 70)


def main() -> int:
    """Hauptfunktion."""
    try:
        parser = argparse.ArgumentParser(
            description="HYP-001: Vollstaendige Gewinnklassen-Verteilungsmuster Analyse",
        )
        parser.add_argument(
            "--data",
            type=str,
            default=None,
            help="Pfad zur GQ-CSV (default: Keno_GPTs/Keno_GQ_2022_2023-2024.csv)",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default=None,
            help="Output JSON (default: results/hyp001_distribution_complete.json)",
        )
        args = parser.parse_args()

        result = run_hyp001_complete(data_path=args.data, output_path=args.output)
        print_summary(result)

        # AC Checklist
        print("\nACCEPTANCE CRITERIA CHECK:")
        print("-" * 40)

        # AC1: Near-Miss fuer Typ 8/9/10
        nm_types = {r["keno_type"] for r in result.near_miss_results}
        ac1 = all(t in nm_types for t in [8, 9, 10])
        print(f"[{'x' if ac1 else ' '}] AC1: Near-Miss fuer Typ 8/9/10 berechnet")

        # AC2: Gewinnklassen-Matrix
        ac2 = result.summary_stats["total_matrix_entries"] >= 30  # 9 Typen * min 3 Klassen
        print(f"[{'x' if ac2 else ' '}] AC2: Gewinnklassen-Matrix erstellt ({result.summary_stats['total_matrix_entries']} Eintraege)")

        # AC3: Zeitliche Korrelation
        ac3 = result.summary_stats["total_temporal_lags"] >= 5
        print(f"[{'x' if ac3 else ' '}] AC3: Zeitliche Korrelation dokumentiert ({result.summary_stats['total_temporal_lags']} Lags)")

        # AC4: Hypothese bewertet
        ac4 = result.hypothesis_evaluation["verdict"] in ["BESTAETIGT", "TEILWEISE", "FALSIFIZIERT"]
        print(f"[{'x' if ac4 else ' '}] AC4: Hypothese bewertet ({result.hypothesis_evaluation['verdict']})")

        # AC5: Report gespeichert
        report_exists = Path("results/hyp001_distribution_complete.json").exists()
        print(f"[{'x' if report_exists else ' '}] AC5: Report in results/hyp001_distribution_complete.json")

        # AC6: Unit-Tests (extern)
        print("[ ] AC6: Unit-Tests >= 3 PASSED (extern validieren)")

        print("-" * 40)

        return 0

    except FileNotFoundError as e:
        logger.error(f"Datei nicht gefunden: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
