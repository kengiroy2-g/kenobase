#!/usr/bin/env python3
"""Kenobase Prediction CLI - Generiert Zahlen-Empfehlungen.

Usage:
    python scripts/predict.py --config config/default.yaml
    python scripts/predict.py --top 6 --output results/prediction.json
    python scripts/predict.py --format text
    python scripts/predict.py --ensemble --alpha 0.4  # Ensemble mode

Dieses Script bietet zwei Modi:
1. Rule-Based (default): HypothesisSynthesizer
2. Ensemble (--ensemble): Kombiniert Rule-Based + ML Model

Ensemble-Modus:
- Laedt trainiertes ML-Modell oder trainiert on-the-fly
- Kombiniert mit alpha * rules + (1-alpha) * ml
- Default: alpha=0.4 (40% rules, 60% ML)

Rule-Based Modus:
1. Laedt alle HYP-Ergebnisse aus results/
2. Kombiniert Scores per HypothesisSynthesizer
3. Generiert Empfehlungen unter Beruecksichtigung von:
   - Zehnergruppen-Filter (max 2 pro Gruppe)
   - Avalanche-Theorie (max 4 Zahlen empfohlen)
   - Tier-basierte Klassifikation (A/B/C)
4. Gibt Ergebnisse als JSON oder Text aus
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.config import load_config
from kenobase.core.data_loader import DataLoader
from kenobase.prediction.synthesizer import HypothesisSynthesizer
from kenobase.prediction.recommendation import (
    generate_recommendations,
    recommendations_to_dict,
    format_recommendations,
)
from kenobase.prediction.ensemble import (
    EnsemblePredictor,
    EnsemblePrediction,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parst Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(
        description="Kenobase Prediction - Zahlen-Empfehlungen basierend auf Hypothesen-Synthese",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python scripts/predict.py                          # Standard-Ausgabe
  python scripts/predict.py --top 4                  # Top 4 Zahlen (Anti-Avalanche)
  python scripts/predict.py --output prediction.json # JSON-Ausgabe
  python scripts/predict.py --format text --verbose  # Detaillierte Text-Ausgabe
        """,
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/default.yaml",
        help="Pfad zur Konfigurationsdatei (default: config/default.yaml)",
    )

    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Pfad zum Ergebnis-Verzeichnis (default: results)",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=6,
        help="Anzahl der Top-Empfehlungen (default: 6)",
    )

    parser.add_argument(
        "--max-per-decade",
        type=int,
        default=2,
        help="Maximum Zahlen pro Zehnergruppe (default: 2)",
    )

    parser.add_argument(
        "--no-avalanche-limit",
        action="store_true",
        help="Deaktiviert Anti-Avalanche-Limit (default: 4 Zahlen)",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Pfad fuer JSON-Ausgabe (optional)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "text", "both"],
        default="both",
        help="Ausgabeformat (default: both)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detaillierte Ausgabe inkl. aller Hypothesen-Scores",
    )

    parser.add_argument(
        "--all-scores",
        action="store_true",
        help="Zeigt Scores fuer alle 70 Zahlen (nicht nur Top-N)",
    )

    # Ensemble mode arguments
    parser.add_argument(
        "--ensemble",
        action="store_true",
        help="Aktiviert Ensemble-Modus (Rule-Based + ML)",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=0.4,
        help="Gewicht fuer Rule-Based im Ensemble (default: 0.4 = 40%% rules, 60%% ML)",
    )

    parser.add_argument(
        "--model-path",
        type=str,
        help="Pfad zum gespeicherten ML-Modell (optional)",
    )

    parser.add_argument(
        "--data-path",
        type=str,
        default="data/keno_historical.csv",
        help="Pfad zu Ziehungsdaten (fuer Ensemble-Training)",
    )

    parser.add_argument(
        "--tune",
        action="store_true",
        help="Hyperparameter-Tuning fuer ML-Modell aktivieren",
    )

    return parser.parse_args()


def run_ensemble_mode(args: argparse.Namespace) -> int:
    """Fuehrt Ensemble-Modus aus (Rule-Based + ML).

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 = success)
    """
    print("=" * 60)
    print("KENOBASE ENSEMBLE PREDICTION")
    print(f"Mode: Ensemble (alpha={args.alpha})")
    print(f"  Rule-Based Weight: {args.alpha * 100:.0f}%")
    print(f"  ML Model Weight: {(1 - args.alpha) * 100:.0f}%")
    print("=" * 60)
    print()

    # Check data availability
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        print(f"\nFehler: Datendatei nicht gefunden: {data_path}")
        print("Bitte geben Sie einen gueltigen Pfad mit --data-path an.")
        return 1

    # Load draws
    logger.info(f"Loading draws from {data_path}")
    loader = DataLoader()
    draws = loader.load(str(data_path))

    if not draws:
        logger.error("No draws loaded")
        print("\nFehler: Keine Ziehungen geladen.")
        return 1

    logger.info(f"Loaded {len(draws)} draws")

    # Initialize ensemble
    ensemble = EnsemblePredictor(
        alpha=args.alpha,
        numbers_range=(1, 70),
        results_dir=args.results_dir,
    )

    # Check for saved model or train
    model_path = Path(args.model_path) if args.model_path else None

    if model_path and model_path.with_suffix(".lgb").exists():
        logger.info(f"Loading saved model from {model_path}")
        ensemble.load(model_path)
        print(f"Modell geladen: {model_path}")
    else:
        logger.info("Training ensemble...")
        print("Training Ensemble-Modell (kann einige Minuten dauern)...")
        report = ensemble.fit(
            draws,
            tune_hyperparameters=args.tune,
            n_cv_folds=5,
        )

        if report.ensemble_metrics:
            print(f"\nTraining abgeschlossen:")
            print(f"  Ensemble F1: {report.ensemble_metrics.f1:.4f}")
            print(f"  ML F1: {report.ml_report.wf_metrics.f1:.4f}" if report.ml_report and report.ml_report.wf_metrics else "")
            print(f"  Hypothesen: {', '.join(report.hypotheses_used)}")

        # Save model if path provided
        if args.model_path:
            model_path = Path(args.model_path)
            ensemble.save(model_path)
            print(f"\nModell gespeichert: {model_path}")

    # Generate predictions
    predictions = ensemble.predict(draws, top_n=args.top)

    # Format output
    print("\n" + "=" * 60)
    print("ENSEMBLE VORHERSAGEN")
    print("=" * 60 + "\n")

    for i, pred in enumerate(predictions, 1):
        print(
            f"{i}. Zahl {pred.number:2d}  [Tier {pred.tier}]  "
            f"Score: {pred.ensemble_score:.3f}"
        )
        print(
            f"   Rule: {pred.rule_score:.3f}  |  "
            f"ML: {pred.ml_probability:.3f}  |  "
            f"Conf: {pred.confidence:.3f}"
        )
        print()

    # Summary
    tier_a = len([p for p in predictions if p.tier == "A"])
    tier_b = len([p for p in predictions if p.tier == "B"])
    tier_c = len([p for p in predictions if p.tier == "C"])

    print("-" * 60)
    print(f"Zusammenfassung: {len(predictions)} Zahlen")
    print(f"  Tier A (stark): {tier_a}")
    print(f"  Tier B (moderat): {tier_b}")
    print(f"  Tier C (neutral): {tier_c}")
    print()
    print(f"Empfohlene Zahlen: {', '.join(str(p.number) for p in predictions)}")
    print("=" * 60)

    # Output JSON if requested
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": "ensemble",
            "config": {
                "alpha": args.alpha,
                "top_n": args.top,
                "data_path": str(args.data_path),
            },
            "predictions": [p.to_dict() for p in predictions],
            "summary": {
                "tier_a": tier_a,
                "tier_b": tier_b,
                "tier_c": tier_c,
                "numbers": [p.number for p in predictions],
            },
        }

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nJSON-Ausgabe: {output_path}")

    return 0


def run_rule_based_mode(args: argparse.Namespace) -> int:
    """Fuehrt Rule-Based Modus aus (nur HypothesisSynthesizer).

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 = success)
    """
    # Synthesizer initialisieren
    synthesizer = HypothesisSynthesizer(
        results_dir=args.results_dir,
        numbers_range=(1, 70),  # KENO
    )

    # Ergebnisse laden
    loaded = synthesizer.load_results()
    if not loaded:
        logger.error("Keine Hypothesen-Ergebnisse gefunden!")
        print("\nFehler: Keine HYP-Ergebnisse in", args.results_dir)
        print("Fuehren Sie zuerst die Hypothesen-Analysen aus:")
        print("  python scripts/analyze_hyp007.py")
        print("  python scripts/analyze_hyp010.py")
        print("  python scripts/analyze_hyp011.py")
        print("  python scripts/analyze_hyp012.py")
        return 1

    logger.info(f"Geladene Hypothesen: {list(loaded.keys())}")

    # Synthese durchfuehren
    scores = synthesizer.synthesize()

    # Empfehlungen generieren
    avalanche_limit = None if args.no_avalanche_limit else 4
    recommendations = generate_recommendations(
        scores=scores,
        top_n=args.top,
        max_per_decade=args.max_per_decade,
        anti_avalanche_limit=avalanche_limit,
    )

    # Output vorbereiten
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "rule_based",
        "config": {
            "results_dir": args.results_dir,
            "top_n": args.top,
            "max_per_decade": args.max_per_decade,
            "anti_avalanche_limit": avalanche_limit,
        },
        "hypotheses_used": list(loaded.keys()),
        "recommendations": recommendations_to_dict(recommendations),
    }

    # Alle Scores hinzufuegen wenn angefordert
    if args.all_scores or args.verbose:
        output_data["all_scores"] = synthesizer.to_dict()["scores"]

    # Ausgabe
    if args.format in ("text", "both"):
        print(format_recommendations(recommendations))

        if args.verbose:
            print("\nDetails pro Hypothese:")
            for num, ns in sorted(
                [(n, s) for n, s in scores.items() if s.tier == "A"],
                key=lambda x: x[1].combined_score,
                reverse=True,
            ):
                print(f"\nZahl {num} (Tier {ns.tier}, Score: {ns.combined_score:.3f}):")
                for hyp_id, hs in ns.hypothesis_scores.items():
                    sig = " [SIGNIFIKANT]" if hs.is_significant else ""
                    print(f"  {hyp_id}: {hs.score:.3f} (weight: {hs.weight:.2f}){sig}")
                    print(f"    Grund: {hs.reason}")

    if args.format in ("json", "both"):
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Ergebnisse gespeichert: {output_path}")
            print(f"\nJSON-Ausgabe: {output_path}")
        elif args.format == "json":
            print(json.dumps(output_data, indent=2, ensure_ascii=False))

    # Avalanche-Warnung
    if len(recommendations) > 4 and avalanche_limit is None:
        print("\n" + "=" * 60)
        print("WARNUNG: Anti-Avalanche-Theorie (ADR-021)")
        print(f"Mit {len(recommendations)} Zahlen steigt theta exponentiell:")
        print(f"  theta = 1 - p^n = 1 - 0.7^{len(recommendations)} = {1 - 0.7**len(recommendations):.2%}")
        print("Empfehlung: Maximal 4 Zahlen pro Tipp verwenden.")
        print("=" * 60)

    return 0


def main() -> int:
    """Hauptfunktion."""
    args = parse_args()

    # Config laden (optional, fuer zukuenftige Erweiterungen)
    config = load_config(args.config)
    logger.info(f"Config loaded: {args.config}")

    # Dispatch based on mode
    if args.ensemble:
        return run_ensemble_mode(args)
    else:
        return run_rule_based_mode(args)


if __name__ == "__main__":
    sys.exit(main())
