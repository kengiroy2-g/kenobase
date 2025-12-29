#!/usr/bin/env python
"""
KENO Data Synthesizer - Kombiniert Ziehungen mit Gewinnquoten.

Kernfunktionen:
1. Ziehungsdaten + Gewinnquoten zusammenfuehren
2. Birthday-Score pro Ziehung berechnen
3. Korrelation Birthday vs. Gewinner analysieren
4. Verteilungsmuster erkennen
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np

from kenobase.core.parsing import parse_int_mixed_german


class KenoSynthesizer:
    """Kombiniert KENO Ziehungen mit Gewinnquoten-Daten."""

    def __init__(
        self,
        draws_path: Path,
        quotes_path: Path,
        encoding: str = 'utf-8-sig'
    ):
        """
        Args:
            draws_path: Pfad zu Ziehungsdaten (z1-z20)
            quotes_path: Pfad zu Gewinnquoten (Anzahl Gewinner)
            encoding: Datei-Encoding
        """
        self.draws_path = Path(draws_path)
        self.quotes_path = Path(quotes_path)
        self.encoding = encoding

        self.draws_df: Optional[pd.DataFrame] = None
        self.quotes_df: Optional[pd.DataFrame] = None
        self.combined_df: Optional[pd.DataFrame] = None

    def load_draws(self) -> pd.DataFrame:
        """Lade Ziehungsdaten."""
        # Auto-detect delimiter
        with open(self.draws_path, 'r', encoding=self.encoding) as f:
            first_line = f.readline()
            delimiter = ';' if ';' in first_line else ','

        df = pd.read_csv(
            self.draws_path,
            delimiter=delimiter,
            encoding=self.encoding
        )

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()

        # Parse date
        date_col = [c for c in df.columns if 'datum' in c.lower()][0]
        df['datum'] = pd.to_datetime(df[date_col], format='%d.%m.%Y', errors='coerce')

        # Extract number columns
        num_cols = []
        for col in df.columns:
            if any(x in col.lower() for x in ['z1', 'z2', 'z3', 'keno_z']):
                num_cols.append(col)

        # If using z1-z20 format
        if not num_cols:
            num_cols = [f'z{i}' for i in range(1, 21) if f'z{i}' in df.columns]

        # Rename to standard format
        number_mapping = {}
        for i, col in enumerate(sorted(num_cols), 1):
            number_mapping[col] = f'n{i}'

        df = df.rename(columns=number_mapping)

        self.draws_df = df
        return df

    def load_quotes(self) -> pd.DataFrame:
        """Lade Gewinnquoten-Daten."""
        # Auto-detect delimiter
        with open(self.quotes_path, 'r', encoding=self.encoding) as f:
            first_line = f.readline()
            delimiter = ';' if ';' in first_line else ','

        df = pd.read_csv(
            self.quotes_path,
            delimiter=delimiter,
            encoding=self.encoding
        )

        # Clean column names
        df.columns = df.columns.str.strip()

        # Parse date
        date_col = [c for c in df.columns if 'datum' in c.lower()][0]
        df['datum'] = pd.to_datetime(df[date_col], format='%d.%m.%Y', errors='coerce')

        winner_col = [c for c in df.columns if 'gewinner' in c.lower()][0]
        df['gewinner'] = df[winner_col].apply(parse_int_mixed_german)

        # Parse Keno-Typ
        typ_col = [c for c in df.columns if 'typ' in c.lower()][0]
        df['keno_typ'] = pd.to_numeric(df[typ_col], errors='coerce')

        # Parse matches
        match_col = [c for c in df.columns if 'richtig' in c.lower()][0]
        df['treffer'] = pd.to_numeric(df[match_col], errors='coerce')

        self.quotes_df = df
        return df

    def calculate_birthday_score(self, numbers: list[int]) -> float:
        """
        Berechne Birthday-Score (Anteil Zahlen 1-31).

        Menschen waehlen oft Geburtstage (1-31).
        Wenn viele Birthday-Zahlen gezogen werden = mehr Gewinner.
        """
        if not numbers:
            return 0.0
        birthday_count = sum(1 for n in numbers if 1 <= n <= 31)
        return birthday_count / len(numbers)

    def calculate_decade_distribution(self, numbers: list[int]) -> dict:
        """
        Berechne Verteilung ueber Zehnergruppen (1-10, 11-20, ..., 61-70).
        """
        decades = {f'{i*10+1}-{(i+1)*10}': 0 for i in range(7)}
        for n in numbers:
            decade_idx = (n - 1) // 10
            decade_key = f'{decade_idx*10+1}-{(decade_idx+1)*10}'
            decades[decade_key] = decades.get(decade_key, 0) + 1
        return decades

    def combine_data(self) -> pd.DataFrame:
        """
        Kombiniere Ziehungen mit Gewinnquoten.

        Returns:
            DataFrame mit: datum, zahlen, birthday_score, total_winners, ...
        """
        if self.draws_df is None:
            self.load_draws()
        if self.quotes_df is None:
            self.load_quotes()

        # Aggregate winners per date
        daily_winners = self.quotes_df.groupby('datum').agg({
            'gewinner': 'sum'
        }).reset_index()
        daily_winners.columns = ['datum', 'total_gewinner']

        # Aggregate jackpot winners (10/10, 9/9, 8/8)
        jackpot_data = self.quotes_df[
            (self.quotes_df['keno_typ'] == self.quotes_df['treffer']) &
            (self.quotes_df['keno_typ'] >= 8)
        ].groupby('datum').agg({
            'gewinner': 'sum'
        }).reset_index()
        jackpot_data.columns = ['datum', 'jackpot_gewinner']

        # Extract numbers from draws
        num_cols = [f'n{i}' for i in range(1, 21)]

        # Filter to columns that exist
        available_num_cols = [c for c in num_cols if c in self.draws_df.columns]

        draws_subset = self.draws_df[['datum'] + available_num_cols].copy()

        # Calculate birthday score per draw
        def row_birthday_score(row):
            numbers = [int(row[c]) for c in available_num_cols if pd.notna(row[c])]
            return self.calculate_birthday_score(numbers)

        draws_subset['birthday_score'] = draws_subset.apply(row_birthday_score, axis=1)

        # Calculate decade distribution
        def row_decade_dist(row):
            numbers = [int(row[c]) for c in available_num_cols if pd.notna(row[c])]
            return json.dumps(self.calculate_decade_distribution(numbers))

        draws_subset['decade_dist'] = draws_subset.apply(row_decade_dist, axis=1)

        # Sum of all numbers (characteristic)
        draws_subset['zahlen_summe'] = draws_subset[available_num_cols].sum(axis=1)

        # Merge all data
        combined = draws_subset.merge(daily_winners, on='datum', how='left')
        combined = combined.merge(jackpot_data, on='datum', how='left')

        # Fill NaN
        combined['total_gewinner'] = combined['total_gewinner'].fillna(0)
        combined['jackpot_gewinner'] = combined['jackpot_gewinner'].fillna(0)

        self.combined_df = combined
        return combined

    def analyze_birthday_correlation(self) -> dict:
        """
        Analysiere Korrelation zwischen Birthday-Score und Gewinnerzahl.

        Hypothese: Mehr Birthday-Zahlen (1-31) = mehr Gewinner.
        """
        if self.combined_df is None:
            self.combine_data()

        df = self.combined_df[self.combined_df['total_gewinner'] > 0].copy()

        if len(df) < 10:
            return {'error': 'Nicht genug Daten fuer Korrelationsanalyse'}

        # Pearson correlation
        correlation = df['birthday_score'].corr(df['total_gewinner'])

        # Categorize
        high_birthday = df[df['birthday_score'] > 0.5]
        low_birthday = df[df['birthday_score'] < 0.35]

        avg_winners_high = high_birthday['total_gewinner'].mean() if len(high_birthday) > 0 else 0
        avg_winners_low = low_birthday['total_gewinner'].mean() if len(low_birthday) > 0 else 0

        # Interpretation
        if correlation > 0.1:
            interpretation = "BESTAETIGT: Mehr Birthday-Zahlen = mehr Gewinner"
        elif correlation < -0.1:
            interpretation = "INVERS: Weniger Birthday-Zahlen = mehr Gewinner"
        else:
            interpretation = "NICHT SIGNIFIKANT: Kein klarer Zusammenhang"

        return {
            'n_draws': len(df),
            'correlation': round(correlation, 4),
            'interpretation': interpretation,
            'high_birthday_draws': len(high_birthday),
            'low_birthday_draws': len(low_birthday),
            'avg_winners_high_birthday': round(avg_winners_high, 1),
            'avg_winners_low_birthday': round(avg_winners_low, 1),
            'winner_ratio': round(avg_winners_high / avg_winners_low, 2) if avg_winners_low > 0 else None,
        }

    def analyze_distribution_stability(self) -> dict:
        """
        Analysiere Stabilitaet der Gewinnverteilung.

        Hypothese: Die Ausschuettung wird aktiv gesteuert (CV < 30%).
        """
        if self.combined_df is None:
            self.combine_data()

        df = self.combined_df[self.combined_df['total_gewinner'] > 0].copy()

        # Weekly aggregation
        df['week'] = df['datum'].dt.isocalendar().week
        df['year'] = df['datum'].dt.year

        weekly = df.groupby(['year', 'week']).agg({
            'total_gewinner': 'sum',
            'birthday_score': 'mean',
        }).reset_index()

        # Calculate stability metrics
        mean_winners = weekly['total_gewinner'].mean()
        std_winners = weekly['total_gewinner'].std()
        cv = std_winners / mean_winners if mean_winners > 0 else 0

        # Interpretation
        if cv < 0.25:
            stability = "SEHR STABIL (moegl. aktive Steuerung)"
        elif cv < 0.4:
            stability = "MODERAT STABIL"
        else:
            stability = "VARIABEL (eher zufaellig)"

        return {
            'weekly_mean_winners': round(mean_winners, 0),
            'weekly_std_winners': round(std_winners, 0),
            'coefficient_of_variation': round(cv, 4),
            'stability_interpretation': stability,
            'n_weeks': len(weekly),
        }

    def find_anomalies(self, threshold: float = 2.0) -> pd.DataFrame:
        """
        Finde Anomalien in der Gewinnverteilung.

        Args:
            threshold: Z-Score Schwelle fuer Anomalie

        Returns:
            DataFrame mit anomalen Ziehungen
        """
        if self.combined_df is None:
            self.combine_data()

        df = self.combined_df.copy()

        # Calculate z-score for winners
        mean_winners = df['total_gewinner'].mean()
        std_winners = df['total_gewinner'].std()

        if std_winners == 0:
            return pd.DataFrame()

        df['z_score'] = (df['total_gewinner'] - mean_winners) / std_winners

        # Filter anomalies
        anomalies = df[abs(df['z_score']) > threshold].copy()
        anomalies = anomalies.sort_values('z_score', ascending=False)

        return anomalies[['datum', 'birthday_score', 'total_gewinner', 'z_score', 'jackpot_gewinner']]


def main():
    """Haupt-Analyse."""
    print("=" * 60)
    print("KENO DATA SYNTHESIZER")
    print("=" * 60)

    # Paths
    draws_path = Path("Keno_GPTs/Daten/KENO_Stats_ab-2004.csv")
    quotes_path = Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv")

    if not draws_path.exists():
        draws_path = Path("data/raw/keno/KENO_ab_2018.csv")

    print(f"\nZiehungen: {draws_path}")
    print(f"Quoten: {quotes_path}")

    # Create synthesizer
    synth = KenoSynthesizer(draws_path, quotes_path)

    # Load and combine
    print("\n" + "-" * 60)
    print("Lade und kombiniere Daten...")
    combined = synth.combine_data()
    print(f"Kombinierte Datensaetze: {len(combined)}")
    print(f"Zeitraum: {combined['datum'].min()} bis {combined['datum'].max()}")

    # Birthday correlation
    print("\n" + "-" * 60)
    print("BIRTHDAY-KORRELATION")
    birthday = synth.analyze_birthday_correlation()
    for k, v in birthday.items():
        print(f"  {k}: {v}")

    # Distribution stability
    print("\n" + "-" * 60)
    print("VERTEILUNGS-STABILITAET")
    stability = synth.analyze_distribution_stability()
    for k, v in stability.items():
        print(f"  {k}: {v}")

    # Anomalies
    print("\n" + "-" * 60)
    print("ANOMALIEN (Z-Score > 2)")
    anomalies = synth.find_anomalies(threshold=2.0)
    if len(anomalies) > 0:
        print(f"  Gefunden: {len(anomalies)} anomale Ziehungen")
        print("\n  Top 5 High-Anomalies:")
        for _, row in anomalies.head(5).iterrows():
            print(f"    {row['datum'].strftime('%Y-%m-%d')}: "
                  f"Gewinner={int(row['total_gewinner']):,}, "
                  f"Z={row['z_score']:.2f}, "
                  f"Birthday={row['birthday_score']:.0%}")

        print("\n  Top 5 Low-Anomalies:")
        for _, row in anomalies.tail(5).iterrows():
            print(f"    {row['datum'].strftime('%Y-%m-%d')}: "
                  f"Gewinner={int(row['total_gewinner']):,}, "
                  f"Z={row['z_score']:.2f}, "
                  f"Birthday={row['birthday_score']:.0%}")
    else:
        print("  Keine Anomalien gefunden.")

    # Save results
    print("\n" + "-" * 60)
    results = {
        'analysis_date': datetime.now().isoformat(),
        'data_sources': {
            'draws': str(draws_path),
            'quotes': str(quotes_path),
        },
        'n_combined_draws': len(combined),
        'birthday_correlation': birthday,
        'distribution_stability': stability,
        'anomalies_count': len(anomalies),
    }

    output_path = Path("results/synthesizer_analysis.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"Ergebnisse gespeichert: {output_path}")

    # Save combined data
    combined_path = Path("results/combined_keno_data.csv")
    combined.to_csv(combined_path, index=False, encoding='utf-8-sig')
    print(f"Kombinierte Daten: {combined_path}")

    print("\n" + "=" * 60)
    print("FAZIT:")
    print("-" * 60)

    if birthday.get('correlation', 0) > 0.05:
        print("-> Birthday-Hypothese: WAHRSCHEINLICH BESTAETIGT")
        print(f"   Korrelation r={birthday.get('correlation', 0):.4f}")
    else:
        print("-> Birthday-Hypothese: NICHT BESTAETIGT")

    if stability.get('coefficient_of_variation', 1) < 0.3:
        print("-> Verteilung: AKTIVE STEUERUNG MOEGLICH")
    else:
        print("-> Verteilung: EHER ZUFAELLIG")

    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
