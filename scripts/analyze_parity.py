#!/usr/bin/env python3
"""Analyse-Script fuer Gerade/Ungerade Ratio (TRANS-003).

Analysiert die Verteilung von geraden und ungeraden Zahlen
in Lotterieziehungen und testet gegen 50/50 Erwartung.

Verwendung:
    python scripts/analyze_parity.py --game keno
    python scripts/analyze_parity.py --game lotto --output results/lotto_parity.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.parity_ratio import (
    ParityRatioResult,
    analyze_parity_ratio,
)
from kenobase.core.data_loader import load_draws, GameType


def result_to_dict(result: ParityRatioResult) -> dict:
    """Konvertiert ParityRatioResult zu serialisierbarem dict."""
    return {
        "total_draws": result.total_draws,
        "numbers_per_draw": result.numbers_per_draw,
        "total_numbers": result.total_numbers,
        "even_count": result.even_count,
        "odd_count": result.odd_count,
        "parity_ratio": result.parity_ratio,
        "chi_square": result.chi_square,
        "chi_p_value": result.chi_p_value,
        "binomial_p_value": result.binomial_p_value,
        "max_deviation_ratio": result.max_deviation_ratio,
        "guardrail_breached": result.guardrail_breached,
        "bins": [
            {
                "category": b.category,
                "count": b.count,
                "expected_count": b.expected_count,
                "relative_frequency": b.relative_frequency,
                "deviation_ratio": b.deviation_ratio,
                "within_guardrail": b.within_guardrail,
            }
            for b in result.bins
        ],
        "warnings": result.warnings,
    }


def main() -> int:
    """Hauptfunktion fuer Paritaets-Analyse."""
    parser = argparse.ArgumentParser(
        description="Analysiert Gerade/Ungerade Ratio in Lotterieziehungen",
    )
    parser.add_argument(
        "--game",
        type=str,
        default="keno",
        choices=["keno", "lotto", "eurojackpot"],
        help="Spiel-Typ (default: keno)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Verzeichnis mit Ziehungsdaten",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output-Pfad fuer JSON-Ergebnisse (default: results/parity_ratio.json)",
    )
    parser.add_argument(
        "--guardrail",
        type=float,
        default=0.10,
        help="Guardrail-Schwelle fuer Abweichung (default: 0.10 = 10%%)",
    )

    args = parser.parse_args()

    # Bestimme Output-Pfad
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("results") / "parity_ratio.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Lade Daten
    data_dir = Path(args.data_dir)
    game_type = GameType(args.game)

    print(f"Loading {args.game} draws from {data_dir}...")

    try:
        draws = load_draws(str(data_dir), game_type=game_type)
    except Exception as e:
        print(f"Error loading data: {e}")
        return 1

    if not draws:
        print("No draws found. Please check data directory.")
        return 1

    print(f"Loaded {len(draws)} draws")

    # Fuehre Analyse durch
    print(f"Analyzing parity ratio with guardrail={args.guardrail:.1%}...")
    result = analyze_parity_ratio(
        draws=draws,
        guardrail_ratio=args.guardrail,
    )

    # Ausgabe
    print("\n" + "=" * 60)
    print("PARITY RATIO ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Game:             {args.game.upper()}")
    print(f"Total Draws:      {result.total_draws:,}")
    print(f"Total Numbers:    {result.total_numbers:,}")
    print(f"Numbers/Draw:     {result.numbers_per_draw}")
    print("-" * 60)
    print(f"Even Count:       {result.even_count:,} ({result.even_count/result.total_numbers*100:.2f}%)")
    print(f"Odd Count:        {result.odd_count:,} ({result.odd_count/result.total_numbers*100:.2f}%)")
    print(f"Parity Ratio:     {result.parity_ratio:.4f}")
    print("-" * 60)
    print(f"Chi-Square:       {result.chi_square:.4f}")
    print(f"Chi p-value:      {result.chi_p_value:.6f}")
    print(f"Binomial p-value: {result.binomial_p_value:.6f}")
    print("-" * 60)
    print(f"Max Deviation:    {result.max_deviation_ratio:.4f} ({result.max_deviation_ratio*100:.2f}%)")
    print(f"Guardrail ({args.guardrail*100:.0f}%): {'BREACHED' if result.guardrail_breached else 'OK'}")
    print("=" * 60)

    # Signifikanz-Interpretation
    if result.binomial_p_value < 0.001:
        sig = "HIGHLY SIGNIFICANT (p < 0.001)"
    elif result.binomial_p_value < 0.01:
        sig = "VERY SIGNIFICANT (p < 0.01)"
    elif result.binomial_p_value < 0.05:
        sig = "SIGNIFICANT (p < 0.05)"
    else:
        sig = "NOT SIGNIFICANT (p >= 0.05)"
    print(f"Statistical:      {sig}")
    print("=" * 60)

    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f"  - {w}")

    # Speichere Ergebnisse
    output_data = {
        "analysis": "parity_ratio",
        "task_id": "TRANS-003",
        "game": args.game,
        "timestamp": datetime.now().isoformat(),
        "result": result_to_dict(result),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
