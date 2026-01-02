#!/usr/bin/env python
"""
Analyse der KENO-Gewinnverteilung

Hypothese: Die Ziehungszahlen werden so gewaehlt, dass:
1. Die Gesamtausschuettung pro Periode konstant bleibt (~50% Einnahmen)
2. Jackpots zeitlich verteilt werden (nicht zu oft, nicht zu selten)
3. Viele kleine Gewinner = beliebte Zahlen wurden gezogen
4. Wenige grosse Gewinner = unbeliebte Zahlen wurden gezogen

Dieses Script analysiert die Keno_GQ Daten um diese Muster zu erkennen.

Usage:
    python scripts/analyze_distribution.py                    # Standard-Analyse
    python scripts/analyze_distribution.py --mode payout-ratio --data Keno_GPTs/KENO_Quote_details_2023.csv
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np

from kenobase.analysis.distribution import (
    load_gq_data,
    load_quote_details_data,
    analyze_payout_ratio,
    detect_payout_ratio_anomalies,
    PayoutRatioResult,
)


def load_gewinnquoten(filepath: Path) -> pd.DataFrame:
    """Lade Gewinnquoten-Daten."""
    df = load_gq_data(str(filepath))
    if df.empty:
        return df

    df["Gewinner"] = df["Anzahl der Gewinner"].astype(float)
    df["Quote"] = df["1 Euro Gewinn"].astype(float)
    df["Auszahlung"] = df["Gewinner"] * df["Quote"]
    return df

    # Legacy parsing fallback (kept for reference)
    df = pd.read_csv(filepath, encoding='utf-8-sig')

    # Parse date
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Parse winner count (handle German number format: 3.462 = 3462)
    def parse_german_number(x):
        if pd.isna(x):
            return 0
        if isinstance(x, (int, float)):
            return float(x)
        # Remove dots (thousand separator) but keep comma as decimal
        s = str(x).replace('.', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0

    df['Gewinner'] = df['Anzahl der Gewinner'].apply(parse_german_number)

    # Parse prize amount
    def parse_euro(x):
        if pd.isna(x):
            return 0
        s = str(x).replace('€', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(s)
        except:
            return 0

    df['Quote'] = df['1 Euro Gewinn'].apply(parse_euro)

    # Calculate payout per row
    df['Auszahlung'] = df['Gewinner'] * df['Quote']

    return df


def analyze_daily_payouts(df: pd.DataFrame) -> pd.DataFrame:
    """Berechne taegliche Gesamtauszahlung."""
    daily = df.groupby('Datum').agg({
        'Auszahlung': 'sum',
        'Gewinner': 'sum'
    }).reset_index()

    daily.columns = ['Datum', 'Gesamtauszahlung', 'Gesamtgewinner']

    return daily


def analyze_jackpots(df: pd.DataFrame) -> pd.DataFrame:
    """Analysiere Jackpot-Haeufigkeit (10/10, 9/9, 8/8)."""
    jackpots = []

    for (keno_typ, matches), group in df.groupby(['Keno-Typ', 'Anzahl richtiger Zahlen']):
        if keno_typ == matches and keno_typ >= 8:  # Hauptgewinn
            hits = group[group['Gewinner'] > 0]
            jackpots.append({
                'Keno_Typ': keno_typ,
                'Matches': matches,
                'Total_Ziehungen': len(group),
                'Jackpot_Hits': len(hits),
                'Hit_Rate': len(hits) / len(group) if len(group) > 0 else 0,
                'Avg_Winners_When_Hit': hits['Gewinner'].mean() if len(hits) > 0 else 0,
            })

    return pd.DataFrame(jackpots)


def analyze_winner_distribution(df: pd.DataFrame) -> dict:
    """Analysiere Gewinner-Verteilung ueber Zeit."""
    # Gruppiere nach Woche
    df['Woche'] = df['Datum'].dt.isocalendar().week
    df['Jahr'] = df['Datum'].dt.year

    weekly = df.groupby(['Jahr', 'Woche']).agg({
        'Auszahlung': 'sum',
        'Gewinner': 'sum'
    }).reset_index()

    return {
        'weekly_mean_payout': weekly['Auszahlung'].mean(),
        'weekly_std_payout': weekly['Auszahlung'].std(),
        'weekly_cv': weekly['Auszahlung'].std() / weekly['Auszahlung'].mean(),  # Coefficient of Variation
        'weekly_min': weekly['Auszahlung'].min(),
        'weekly_max': weekly['Auszahlung'].max(),
    }


def analyze_high_low_winner_days(df: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Vergleiche Tage mit vielen vs. wenigen Gewinnern."""
    median_winners = daily['Gesamtgewinner'].median()

    high_winner_days = daily[daily['Gesamtgewinner'] > median_winners * 1.2]['Datum']
    low_winner_days = daily[daily['Gesamtgewinner'] < median_winners * 0.8]['Datum']

    return {
        'median_daily_winners': median_winners,
        'high_winner_days_count': len(high_winner_days),
        'low_winner_days_count': len(low_winner_days),
        'high_winner_days': high_winner_days.tolist()[:10],  # Sample
        'low_winner_days': low_winner_days.tolist()[:10],
    }


def simulate_distribution_target(df: pd.DataFrame) -> dict:
    """
    Simuliere das Verteilungsziel.

    Annahme: Das System strebt an:
    - ~50% der Einnahmen auszuschuetten
    - Gleichmaessige regionale Verteilung (ueber Zeit)
    - Keine langen Jackpot-Durststrecken (max ~X Tage)
    """
    daily = analyze_daily_payouts(df)

    # Berechne Auszahlungs-Varianz
    payout_stats = {
        'mean_daily_payout': daily['Gesamtauszahlung'].mean(),
        'std_daily_payout': daily['Gesamtauszahlung'].std(),
        'cv_payout': daily['Gesamtauszahlung'].std() / daily['Gesamtauszahlung'].mean(),
    }

    # Jackpot-Intervalle (Tage zwischen Jackpots)
    jackpot_days = df[
        (df['Keno-Typ'] == 10) &
        (df['Anzahl richtiger Zahlen'] == 10) &
        (df['Gewinner'] > 0)
    ]['Datum'].unique()

    if len(jackpot_days) > 1:
        jackpot_days_sorted = sorted(jackpot_days)
        intervals = [(jackpot_days_sorted[i+1] - jackpot_days_sorted[i]).days
                     for i in range(len(jackpot_days_sorted)-1)]
        payout_stats['jackpot_10_count'] = len(jackpot_days)
        payout_stats['jackpot_10_avg_interval'] = np.mean(intervals) if intervals else None
        payout_stats['jackpot_10_max_interval'] = max(intervals) if intervals else None
    else:
        payout_stats['jackpot_10_count'] = len(jackpot_days)
        payout_stats['jackpot_10_avg_interval'] = None
        payout_stats['jackpot_10_max_interval'] = None

    return payout_stats


def main(data_path: Path | None = None, output_path: Path | None = None) -> dict:
    """Hauptanalyse."""
    print("=" * 60)
    print("KENO Gewinnverteilungs-Analyse")
    print("=" * 60)

    # Lade Daten
    if data_path is None:
        data_path = Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv")

    if not data_path.exists():
        alt = Path(__file__).parent.parent / data_path
        if alt.exists():
            data_path = alt

    print(f"\nLade: {data_path}")
    df = load_gewinnquoten(data_path)
    print(f"Zeilen: {len(df)}")
    print(f"Zeitraum: {df['Datum'].min()} bis {df['Datum'].max()}")

    # 1. Taegliche Auszahlungen
    print("\n" + "-" * 60)
    print("1. TAEGLICHE AUSZAHLUNGEN")
    daily = analyze_daily_payouts(df)
    print(f"   Durchschnitt: {daily['Gesamtauszahlung'].mean():,.0f} EUR/Tag")
    print(f"   Std.Abw.:     {daily['Gesamtauszahlung'].std():,.0f} EUR")
    print(f"   Min:          {daily['Gesamtauszahlung'].min():,.0f} EUR")
    print(f"   Max:          {daily['Gesamtauszahlung'].max():,.0f} EUR")

    # 2. Jackpot-Analyse
    print("\n" + "-" * 60)
    print("2. JACKPOT-HAEUFIGKEIT")
    jackpots = analyze_jackpots(df)
    for _, row in jackpots.iterrows():
        print(f"   KENO-{int(row['Keno_Typ'])}/{int(row['Matches'])}: "
              f"{int(row['Jackpot_Hits'])} Hits in {int(row['Total_Ziehungen'])} Ziehungen "
              f"({row['Hit_Rate']*100:.2f}%)")

    # 3. Woechentliche Verteilung
    print("\n" + "-" * 60)
    print("3. WOECHENTLICHE VERTEILUNG")
    weekly = analyze_winner_distribution(df)
    print(f"   Durchschnitt: {weekly['weekly_mean_payout']:,.0f} EUR/Woche")
    print(f"   Variationskoeff.: {weekly['weekly_cv']:.2%}")
    print(f"   -> {'STABIL' if weekly['weekly_cv'] < 0.3 else 'VARIABEL'}")

    # 4. Verteilungsziel-Simulation
    print("\n" + "-" * 60)
    print("4. VERTEILUNGS-MUSTER")
    sim = simulate_distribution_target(df)
    print(f"   Taegliche CV: {sim['cv_payout']:.2%}")
    if sim['jackpot_10_count'] > 0:
        print(f"   10/10 Jackpots: {sim['jackpot_10_count']}")
        if sim['jackpot_10_avg_interval']:
            print(f"   Avg. Intervall: {sim['jackpot_10_avg_interval']:.1f} Tage")
            print(f"   Max. Intervall: {sim['jackpot_10_max_interval']} Tage")

    # 5. High/Low Winner Tage
    print("\n" + "-" * 60)
    print("5. GEWINNER-VERTEILUNG NACH TAGEN")
    hl = analyze_high_low_winner_days(df, daily)
    print(f"   Median Gewinner/Tag: {hl['median_daily_winners']:,.0f}")
    print(f"   Tage mit vielen Gewinnern (>120%): {hl['high_winner_days_count']}")
    print(f"   Tage mit wenigen Gewinnern (<80%): {hl['low_winner_days_count']}")

    # Speichern
    print("\n" + "-" * 60)
    results = {
        'analysis_date': datetime.now().isoformat(),
        'data_source': str(data_path),
        'period': {
            'start': df['Datum'].min().isoformat(),
            'end': df['Datum'].max().isoformat(),
            'days': (df['Datum'].max() - df['Datum'].min()).days,
        },
        'daily_payout': {
            'mean': daily['Gesamtauszahlung'].mean(),
            'std': daily['Gesamtauszahlung'].std(),
            'cv': daily['Gesamtauszahlung'].std() / daily['Gesamtauszahlung'].mean(),
        },
        'jackpots': jackpots.to_dict('records'),
        'weekly_distribution': weekly,
        'distribution_target': sim,
    }

    if output_path is None:
        output_path = Path("results/distribution_analysis.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"Ergebnisse gespeichert: {output_path}")

    print("\n" + "=" * 60)
    print("FAZIT:")
    print("-" * 60)
    if weekly['weekly_cv'] < 0.25:
        print("-> Woechentliche Auszahlung ist SEHR STABIL")
        print("   Dies deutet auf aktive Steuerung der Verteilung hin!")
    elif weekly['weekly_cv'] < 0.4:
        print("-> Woechentliche Auszahlung ist MODERAT STABIL")
    else:
        print("-> Woechentliche Auszahlung ist VARIABEL (zufaellig)")
    print("=" * 60)

    return results


def analyze_payout_ratio_mode(data_path: Path, output_path: Path) -> dict:
    """DIST-002: Auszahlung-Gewinner Ratio Analyse.

    Berechnet payout_per_winner = Auszahlung / Anzahl der Gewinner
    fuer jede Gewinnklasse und erkennt Anomalien.

    Args:
        data_path: Pfad zur CSV-Datei (KENO_Quote_details_2023.csv)
        output_path: Pfad fuer JSON-Output

    Returns:
        Analyse-Ergebnisse als dict
    """
    print("=" * 60)
    print("DIST-002: Auszahlung-Gewinner Ratio Analyse")
    print("=" * 60)

    # Lade Daten
    print(f"\nLade: {data_path}")
    df = load_quote_details_data(str(data_path))
    print(f"Zeilen: {len(df)}")
    print(f"Zeitraum: {df['Datum'].min()} bis {df['Datum'].max()}")
    print(f"Spalten: {list(df.columns)}")

    # Analyse durchfuehren
    print("\n" + "-" * 60)
    print("1. PAYOUT-PER-WINNER ANALYSE")
    results = analyze_payout_ratio(df)
    print(f"   Analysierte Kombinationen: {len(results)}")

    # Ergebnisse nach Keno-Typ gruppiert ausgeben
    print("\n" + "-" * 60)
    print("2. ERGEBNISSE PRO GEWINNKLASSE")
    for r in sorted(results, key=lambda x: (x.keno_type, -x.matches)):
        print(
            f"   Keno-{r.keno_type}/{r.matches}: "
            f"mean={r.mean_payout_per_winner:.2f} EUR, "
            f"CV={r.cv:.4f}, "
            f"n={r.n_draws}, "
            f"zero_draws={r.zero_winner_draws}"
        )

    # Anomalien erkennen
    print("\n" + "-" * 60)
    print("3. ANOMALIEN (CV > 10%)")
    anomalies = detect_payout_ratio_anomalies(results, cv_threshold=0.1)
    if anomalies:
        for kt, m, reason in anomalies:
            print(f"   Keno-{kt}/{m}: {reason}")
    else:
        print("   Keine Anomalien erkannt - Quoten sind konsistent")

    # Ergebnisse speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "task_id": "DIST-002",
        "data_source": str(data_path),
        "period": {
            "start": df["Datum"].min().isoformat(),
            "end": df["Datum"].max().isoformat(),
            "total_rows": len(df),
        },
        "results": [asdict(r) for r in results],
        "anomalies": [
            {"keno_type": kt, "matches": m, "reason": reason}
            for kt, m, reason in anomalies
        ],
        "summary": {
            "total_combinations": len(results),
            "anomaly_count": len(anomalies),
            "mean_cv": float(np.mean([r.cv for r in results])) if results else 0.0,
        },
    }

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nErgebnisse gespeichert: {output_path}")

    # Fazit
    print("\n" + "=" * 60)
    print("FAZIT:")
    print("-" * 60)
    mean_cv = output["summary"]["mean_cv"]
    if mean_cv < 0.01:
        print("-> Payout-per-Winner ist SEHR KONSISTENT (CV < 1%)")
        print("   Quoten sind fix, keine Variation erwartet")
    elif mean_cv < 0.1:
        print("-> Payout-per-Winner ist KONSISTENT (CV < 10%)")
    else:
        print("-> Payout-per-Winner VARIIERT (CV >= 10%)")
        print("   Dies koennte auf Datenfehler oder variable Quoten hindeuten")
    print("=" * 60)

    return output


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="KENO Gewinnverteilungs-Analyse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "payout-ratio"],
        default="standard",
        help="Analyse-Modus: 'standard' (default) oder 'payout-ratio' (DIST-002)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Pfad zur Daten-CSV (fuer payout-ratio: KENO_Quote_details_2023.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Pfad fuer JSON-Output",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "payout-ratio":
        # DIST-002: Payout Ratio Analyse
        data_path = args.data or Path("Keno_GPTs/KENO_Quote_details_2023.csv")
        output_path = args.output or Path("results/dist002_payout_ratio.json")
        analyze_payout_ratio_mode(data_path, output_path)
    else:
        # Standard-Analyse
        data_path = args.data or Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv")
        output_path = args.output or Path("results/distribution_analysis.json")
        main(data_path=data_path, output_path=output_path)
