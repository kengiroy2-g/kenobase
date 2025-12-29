#!/usr/bin/env python
"""
Backtest fuer Anti-Birthday Strategie.

Testet die Strategie gegen historische KENO-Ziehungen.
Vergleicht mit Random-Baseline und misst Konkurrenz-Vorteil.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np

from kenobase.strategy.anti_birthday import (
    AntiBirthdayStrategy,
    BacktestResult,
    run_backtest,
    BIRTHDAY_NUMBERS,
    NON_BIRTHDAY_NUMBERS,
)


def load_draws(filepath: Path) -> pd.DataFrame:
    """Lade Ziehungsdaten."""
    # Auto-detect delimiter
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','

    df = pd.read_csv(filepath, delimiter=delimiter, encoding='utf-8-sig')

    # Standardize columns
    df.columns = df.columns.str.strip().str.lower()

    # Parse date
    date_col = [c for c in df.columns if 'datum' in c.lower()][0]
    df['datum'] = pd.to_datetime(df[date_col], format='%d.%m.%Y', errors='coerce')

    # Find number columns (z1-z20 or keno_z1-keno_z20)
    num_cols = [f'z{i}' for i in range(1, 21) if f'z{i}' in df.columns]

    if not num_cols:
        # Try keno_z format
        num_cols = [f'keno_z{i}' for i in range(1, 21) if f'keno_z{i}' in df.columns]

    if not num_cols:
        raise ValueError(f"Keine Zahlen-Spalten gefunden. Spalten: {df.columns.tolist()}")

    # Rename to n1-n20
    for i, col in enumerate(num_cols, 1):
        df[f'n{i}'] = pd.to_numeric(df[col], errors='coerce')

    return df


def analyze_birthday_distribution(draws_df: pd.DataFrame) -> dict:
    """Analysiere Birthday-Verteilung in historischen Ziehungen."""
    num_cols = [f'n{i}' for i in range(1, 21)]

    birthday_scores = []
    for _, row in draws_df.iterrows():
        numbers = [int(row[c]) for c in num_cols if pd.notna(row[c])]
        if len(numbers) == 20:
            score = sum(1 for n in numbers if n in BIRTHDAY_NUMBERS) / 20
            birthday_scores.append(score)

    return {
        'n_draws': len(birthday_scores),
        'mean_birthday_score': np.mean(birthday_scores),
        'std_birthday_score': np.std(birthday_scores),
        'min_birthday_score': np.min(birthday_scores),
        'max_birthday_score': np.max(birthday_scores),
        'draws_above_50pct': sum(1 for s in birthday_scores if s > 0.5),
        'draws_below_50pct': sum(1 for s in birthday_scores if s < 0.5),
    }


def run_threshold_comparison(
    draws_df: pd.DataFrame,
    keno_type: int = 6,
    thresholds: list[float] = None
) -> dict:
    """Vergleiche verschiedene Anti-Birthday Schwellenwerte."""
    if thresholds is None:
        thresholds = [0.4, 0.5, 0.6, 0.7, 0.8]

    results = {}
    for threshold in thresholds:
        print(f"  Testing threshold {threshold:.0%}...", end=" ")
        try:
            result = run_backtest(
                draws_df,
                keno_type=keno_type,
                min_anti_birthday_ratio=threshold,
                n_random_samples=50,
            )
            results[f"{threshold:.0%}"] = result.to_dict()
            print(f"Done (Advantage: {result.avg_strategy_advantage:.2f}x)")
        except Exception as e:
            print(f"Error: {e}")
            results[f"{threshold:.0%}"] = {"error": str(e)}

    return results


def main():
    """Haupt-Backtest."""
    parser = argparse.ArgumentParser(
        description="Backtest Anti-Birthday Strategie"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("Keno_GPTs/Daten/KENO_Stats_ab-2004.csv"),
        help="Pfad zu Ziehungsdaten"
    )
    parser.add_argument(
        "--keno-type",
        type=int,
        default=6,
        choices=range(2, 11),
        help="KENO-Typ (2-10)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Anti-Birthday Mindest-Ratio (0.0-1.0)"
    )
    parser.add_argument(
        "--compare-thresholds",
        action="store_true",
        help="Vergleiche verschiedene Schwellenwerte"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/anti_birthday_backtest.json"),
        help="Output-Datei"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ANTI-BIRTHDAY STRATEGIE - BACKTEST")
    print("=" * 60)

    # Lade Daten
    print(f"\nLade Daten: {args.data}")
    if not args.data.exists():
        # Fallback
        args.data = Path("data/raw/keno/KENO_ab_2018.csv")

    draws_df = load_draws(args.data)
    print(f"Ziehungen: {len(draws_df)}")
    print(f"Zeitraum: {draws_df['datum'].min()} bis {draws_df['datum'].max()}")

    # Birthday-Verteilung
    print("\n" + "-" * 60)
    print("BIRTHDAY-VERTEILUNG IN ZIEHUNGEN")
    birthday_dist = analyze_birthday_distribution(draws_df)
    print(f"  Durchschnitt Birthday-Score: {birthday_dist['mean_birthday_score']:.1%}")
    print(f"  Std.Abweichung: {birthday_dist['std_birthday_score']:.1%}")
    print(f"  Ziehungen >50% Birthday: {birthday_dist['draws_above_50pct']}")
    print(f"  Ziehungen <50% Birthday: {birthday_dist['draws_below_50pct']}")

    # Threshold-Vergleich
    if args.compare_thresholds:
        print("\n" + "-" * 60)
        print("SCHWELLENWERT-VERGLEICH")
        threshold_results = run_threshold_comparison(draws_df, args.keno_type)

        print("\n  Zusammenfassung:")
        for thresh, res in threshold_results.items():
            if "error" not in res:
                adv = res['competition']['avg_strategy_advantage']
                matches = res['matches']['avg_per_draw']
                print(f"    {thresh}: Vorteil={adv:.2f}x, Treffer={matches:.2f}")

    # Haupt-Backtest
    print("\n" + "-" * 60)
    print(f"BACKTEST (Threshold: {args.threshold:.0%}, KENO-{args.keno_type})")

    result = run_backtest(
        draws_df,
        keno_type=args.keno_type,
        min_anti_birthday_ratio=args.threshold,
        n_random_samples=100,
    )

    print(f"\n  Ziehungen analysiert: {result.n_draws}")
    print(f"\n  TREFFER:")
    print(f"    Gesamt: {result.total_matches}")
    print(f"    Durchschnitt: {result.avg_matches_per_draw:.2f} pro Ziehung")

    print(f"\n  BIRTHDAY-METRIKEN:")
    print(f"    Strategie Anti-Birthday: {result.avg_anti_birthday_score:.1%}")
    print(f"    Ziehungen Birthday: {result.avg_drawn_birthday_score:.1%}")

    print(f"\n  KONKURRENZ-VORTEIL:")
    print(f"    Durchschnittlicher Vorteil: {result.avg_strategy_advantage:.2f}x")
    print(f"    Vorteilhafte Ziehungen: {result.advantageous_draws} "
          f"({result.advantageous_draws/result.n_draws:.1%})")
    print(f"    Nachteilige Ziehungen: {result.disadvantageous_draws} "
          f"({result.disadvantageous_draws/result.n_draws:.1%})")

    print(f"\n  VS. RANDOM:")
    print(f"    Random Durchschnitt: {result.random_avg_matches:.2f} Treffer")
    print(f"    Strategie Durchschnitt: {result.avg_matches_per_draw:.2f} Treffer")
    print(f"    Verbesserung: {result.improvement_vs_random:+.1%}")

    # Erwarteter Gewinn-Vorteil
    print("\n" + "-" * 60)
    print("FAZIT:")
    if result.avg_strategy_advantage > 1.0:
        vorteil_pct = (result.avg_strategy_advantage - 1) * 100
        print(f"  -> STRATEGIE EMPFOHLEN")
        print(f"  -> Bei Gewinn: ~{vorteil_pct:.0f}% weniger Konkurrenz erwartet")
        print(f"  -> In {result.advantageous_draws/result.n_draws:.0%} der Ziehungen vorteilhaft")
    else:
        print(f"  -> STRATEGIE NEUTRAL")
        print(f"  -> Kein signifikanter Vorteil messbar")

    # Speichern
    print("\n" + "-" * 60)
    output_data = {
        "backtest_date": datetime.now().isoformat(),
        "parameters": {
            "data_source": str(args.data),
            "keno_type": args.keno_type,
            "anti_birthday_threshold": args.threshold,
        },
        "birthday_distribution": birthday_dist,
        "main_result": result.to_dict(),
    }

    if args.compare_thresholds:
        output_data["threshold_comparison"] = threshold_results

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"Ergebnisse gespeichert: {args.output}")

    print("=" * 60)
    return result


if __name__ == "__main__":
    main()
