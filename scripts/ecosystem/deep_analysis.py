#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tiefenanalyse der Oekosystem-Erkenntnisse
=========================================

1. 3.5-Tage Periode: Was passiert in dieser Halbwochen-Phase?
2. Lag +26 Exploitation: Kann KENO Lotto vorhersagen?
3. Wavelet-Analyse: Sind die Perioden zeitlich stabil?
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import pearsonr, ttest_ind
import warnings
warnings.filterwarnings('ignore')

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
OUTPUT_DIR = BASE_DIR / "results" / "ecosystem"


def analyze_3_5_day_period(df: pd.DataFrame) -> dict:
    """
    Analyse der 3.5-Tage Periode.

    Hypothese: Das System hat einen Halbwochen-Zyklus.
    Wir teilen die Daten in Phasen (0-3.5 Tage, 3.5-7 Tage) und vergleichen.
    """
    print("\n" + "=" * 60)
    print("ANALYSE 1: 3.5-TAGE PERIODE")
    print("=" * 60)

    df = df.copy()
    df['days'] = (df['datum'] - df['datum'].min()).dt.days

    # Phase innerhalb 7-Tage Zyklus (0-6.99)
    df['week_phase'] = df['days'] % 7

    # Teile in erste Hälfte (0-3.5) und zweite Hälfte (3.5-7)
    df['half_week'] = (df['week_phase'] < 3.5).astype(int)  # 1 = erste Hälfte, 0 = zweite

    # Vergleiche Oekosystem-Gewinner
    first_half = df[df['half_week'] == 1]['ecosystem_winners'].dropna()
    second_half = df[df['half_week'] == 0]['ecosystem_winners'].dropna()

    first_mean = first_half.mean()
    second_mean = second_half.mean()
    t_stat, p_val = ttest_ind(first_half, second_half)

    print(f"\nErste Halbwoche (Tag 0-3.5):")
    print(f"  Durchschnitt Gewinner: {first_mean:,.0f}")
    print(f"  Anzahl Tage: {len(first_half)}")

    print(f"\nZweite Halbwoche (Tag 3.5-7):")
    print(f"  Durchschnitt Gewinner: {second_mean:,.0f}")
    print(f"  Anzahl Tage: {len(second_half)}")

    diff_pct = (second_mean - first_mean) / first_mean * 100
    print(f"\nUnterschied: {diff_pct:+.1f}%")
    print(f"T-Test p-Wert: {p_val:.4f}")
    print(f"Signifikant: {'JA' if p_val < 0.05 else 'NEIN'}")

    # Jackpot-Verteilung
    jp_first = df[df['half_week'] == 1]['ecosystem_jackpots'].sum()
    jp_second = df[df['half_week'] == 0]['ecosystem_jackpots'].sum()

    print(f"\nJackpots erste Halbwoche: {int(jp_first)}")
    print(f"Jackpots zweite Halbwoche: {int(jp_second)}")

    # Detaillierte Tages-Analyse
    print("\n--- Gewinner nach Wochentag ---")
    df['weekday'] = df['datum'].dt.dayofweek
    weekday_names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    for wd in range(7):
        wd_data = df[df['weekday'] == wd]['ecosystem_winners'].dropna()
        if len(wd_data) > 0:
            print(f"  {weekday_names[wd]}: {wd_data.mean():,.0f} (n={len(wd_data)})")

    return {
        'first_half_mean': first_mean,
        'second_half_mean': second_mean,
        'difference_pct': diff_pct,
        'p_value': p_val,
        'significant': p_val < 0.05,
        'jackpots_first_half': int(jp_first),
        'jackpots_second_half': int(jp_second),
    }


def analyze_lag_26_exploitation(df: pd.DataFrame) -> dict:
    """
    Analyse des Lag +26: Kann KENO heute Lotto in 26 Tagen vorhersagen?

    Strategie: Wenn KENO heute viele Gewinner hat, hat Lotto in 26 Tagen auch viele?
    """
    print("\n" + "=" * 60)
    print("ANALYSE 2: LAG +26 EXPLOITATION")
    print("=" * 60)

    df = df.copy()

    # Erstelle verschobene Spalten
    df['lotto_26_ahead'] = df['lotto_total_winners'].shift(-26)
    df['lotto_jackpot_26_ahead'] = df['lotto_jackpot'].shift(-26)

    # Nur Zeilen wo beide Werte existieren
    valid = df.dropna(subset=['keno_total_winners', 'lotto_26_ahead'])

    # Korrelation
    r, p = pearsonr(valid['keno_total_winners'], valid['lotto_26_ahead'])
    print(f"\nKorrelation KENO(heute) vs Lotto(+26 Tage): r={r:.3f}, p={p:.4f}")

    # Teile KENO in Quartile
    valid['keno_quartile'] = pd.qcut(valid['keno_total_winners'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

    print("\n--- Lotto-Gewinner 26 Tage nach KENO-Quartil ---")
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        q_data = valid[valid['keno_quartile'] == q]['lotto_26_ahead']
        print(f"  {q} (KENO {'niedrig' if q == 'Q1' else 'hoch' if q == 'Q4' else 'mittel'}): "
              f"Lotto = {q_data.mean():,.0f} Gewinner")

    # Strategie-Test: Spiele Lotto nur wenn KENO vor 26 Tagen im Q4 war
    q4_lotto = valid[valid['keno_quartile'] == 'Q4']['lotto_26_ahead'].mean()
    q1_lotto = valid[valid['keno_quartile'] == 'Q1']['lotto_26_ahead'].mean()
    improvement = (q4_lotto - q1_lotto) / q1_lotto * 100 if q1_lotto > 0 else 0

    print(f"\nStrategie-Potential:")
    print(f"  Lotto nach KENO-Q4: {q4_lotto:,.0f} Gewinner")
    print(f"  Lotto nach KENO-Q1: {q1_lotto:,.0f} Gewinner")
    print(f"  Unterschied: {improvement:+.1f}%")

    # Jackpot-Vorhersage
    print("\n--- Jackpot-Vorhersage ---")
    keno_high = valid['keno_total_winners'] > valid['keno_total_winners'].median()
    jp_after_high = valid[keno_high]['lotto_jackpot_26_ahead'].mean()
    jp_after_low = valid[~keno_high]['lotto_jackpot_26_ahead'].mean()

    print(f"  Lotto-Jackpot-Rate nach hohem KENO: {jp_after_high*100:.1f}%")
    print(f"  Lotto-Jackpot-Rate nach niedrigem KENO: {jp_after_low*100:.1f}%")

    return {
        'correlation': r,
        'p_value': p,
        'q4_lotto_winners': q4_lotto,
        'q1_lotto_winners': q1_lotto,
        'improvement_pct': improvement,
        'jp_rate_after_high_keno': jp_after_high,
        'jp_rate_after_low_keno': jp_after_low,
    }


def wavelet_analysis(df: pd.DataFrame) -> dict:
    """
    Wavelet-Analyse: Sind die Perioden zeitlich stabil?

    Verwendet Continuous Wavelet Transform (CWT) mit Morlet-Wavelet.
    """
    print("\n" + "=" * 60)
    print("ANALYSE 3: WAVELET (ZEITLICHE STABILITAET)")
    print("=" * 60)

    # Signal vorbereiten
    eco_winners = df['ecosystem_winners'].fillna(df['ecosystem_winners'].mean()).values

    # Normalisieren
    eco_winners = (eco_winners - eco_winners.mean()) / eco_winners.std()

    # Wavelet-Skalen (entsprechen Perioden in Tagen)
    # Wir suchen nach Perioden von 3-30 Tagen
    scales = np.arange(3, 31)

    # CWT mit Ricker-Wavelet (scipy's cwt)
    try:
        # Ricker wavelet (Mexican hat)
        widths = scales
        cwt_matrix = signal.cwt(eco_winners, signal.ricker, widths)

        # Power-Spektrum
        power = np.abs(cwt_matrix) ** 2

        # Zeitliche Mittelung für jede Periode
        avg_power = power.mean(axis=1)

        # Finde dominante Perioden
        peak_indices, _ = signal.find_peaks(avg_power, height=avg_power.mean())

        print("\nDominante Perioden (zeitlich gemittelt):")
        for idx in peak_indices[:5]:
            period = scales[idx]
            pwr = avg_power[idx]
            print(f"  {period} Tage (Power: {pwr:.2f})")

        # Zeitliche Stabilität der 3.5-Tage-Periode
        # Approximieren mit Skala 3 oder 4
        scale_3_5 = 3  # Nächste ganzzahlige Skala
        power_3_5_over_time = power[scale_3_5 - 3, :]  # Index anpassen

        # Teile in 4 Quartale
        n = len(power_3_5_over_time)
        q_size = n // 4

        print("\n--- Stabilität der ~3.5-Tage Periode über Zeit ---")
        quarters = ['Q1 (Jan-Mrz)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Okt-Dez)']
        quarter_powers = []

        for i, q_name in enumerate(quarters):
            start = i * q_size
            end = (i + 1) * q_size if i < 3 else n
            q_power = power_3_5_over_time[start:end].mean()
            quarter_powers.append(q_power)
            print(f"  {q_name}: Power = {q_power:.2f}")

        # Stabilität = 1 - (std / mean)
        stability = 1 - (np.std(quarter_powers) / np.mean(quarter_powers))
        print(f"\nZeitliche Stabilität: {stability:.2%}")
        print(f"Interpretation: {'STABIL' if stability > 0.7 else 'INSTABIL'}")

        return {
            'dominant_periods': [int(scales[idx]) for idx in peak_indices[:5]],
            'quarter_powers': quarter_powers,
            'stability': stability,
            'is_stable': stability > 0.7,
        }

    except Exception as e:
        print(f"Wavelet-Analyse fehlgeschlagen: {e}")
        return {'error': str(e)}


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("TIEFENANALYSE DER OEKOSYSTEM-ERKENNTNISSE")
    print("=" * 60)

    # Output-Verzeichnis
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print(f"\nLade Daten von {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, parse_dates=['datum'])
    print(f"Geladen: {len(df)} Tage")

    results = {}

    # Analyse 1: 3.5-Tage Periode
    results['period_3_5'] = analyze_3_5_day_period(df)

    # Analyse 2: Lag +26 Exploitation
    results['lag_26'] = analyze_lag_26_exploitation(df)

    # Analyse 3: Wavelet
    results['wavelet'] = wavelet_analysis(df)

    # Speichern
    output_file = OUTPUT_DIR / "deep_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG & EMPFEHLUNGEN")
    print("=" * 60)

    # 3.5-Tage
    p35 = results['period_3_5']
    print(f"\n1. 3.5-TAGE PERIODE:")
    if p35['significant']:
        print(f"   SIGNIFIKANT! Unterschied: {p35['difference_pct']:+.1f}%")
        if p35['difference_pct'] > 0:
            print("   → Zweite Halbwoche hat MEHR Gewinner")
        else:
            print("   → Erste Halbwoche hat MEHR Gewinner")
    else:
        print("   Nicht signifikant - möglicherweise Artefakt")

    # Lag 26
    l26 = results['lag_26']
    print(f"\n2. LAG +26 EXPLOITATION:")
    print(f"   Korrelation: r={l26['correlation']:.3f}")
    if l26['improvement_pct'] > 10:
        print(f"   POTENTIAL: +{l26['improvement_pct']:.1f}% mehr Gewinner nach KENO-Q4")
        print("   → Strategie: Lotto spielen 26 Tage nach hohem KENO-Tag")
    else:
        print("   Verbesserung zu gering für praktische Nutzung")

    # Wavelet
    wav = results.get('wavelet', {})
    if 'is_stable' in wav:
        print(f"\n3. WAVELET-STABILITÄT:")
        print(f"   Stabilität: {wav['stability']:.1%}")
        print(f"   → Periode ist {'ZEITLICH STABIL' if wav['is_stable'] else 'ZEITLICH INSTABIL'}")

    return results


if __name__ == '__main__':
    main()
