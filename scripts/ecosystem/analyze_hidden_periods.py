#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Versteckte Perioden-Analyse
===========================

Sucht nach NICHT-TRIVIALEN Perioden im Oekosystem.

WARNUNG:
- Triviale Perioden (7, 14, 30, 90, 365 Tage) existieren NICHT
- Das System wurde gegen solche Muster immunisiert
- Wir suchen nach: Primzahl-basierten, irrationalen, adaptiven Perioden

Methoden:
- Lomb-Scargle Periodogramm (unregelmaessige Daten)
- Continuous Wavelet Transform (zeitabhaengig)
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import pearsonr

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
OUTPUT_DIR = BASE_DIR / "results" / "ecosystem"

# Triviale Perioden die wir IGNORIEREN
TRIVIAL_PERIODS = [7, 14, 21, 28, 30, 31, 60, 90, 120, 180, 365]
TRIVIAL_TOLERANCE = 0.5  # +/- 0.5 Tage

# Primzahl-Perioden die interessant waeren
PRIME_PERIODS = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Irrationale Perioden
IRRATIONAL_PERIODS = {
    'sqrt2_7': np.sqrt(2) * 7,      # 9.899
    'phi_10': (1 + np.sqrt(5)) / 2 * 10,  # 16.18 (goldener Schnitt)
    'e_5': np.e * 5,                # 13.59
    'pi_3': np.pi * 3,              # 9.42
}


def is_trivial_period(period: float) -> bool:
    """Prueft ob eine Periode trivial ist."""
    for trivial in TRIVIAL_PERIODS:
        if abs(period - trivial) < TRIVIAL_TOLERANCE:
            return True
    return False


def lomb_scargle_analysis(times: np.ndarray, values: np.ndarray,
                           min_period: float = 3, max_period: float = 60) -> dict:
    """
    Lomb-Scargle Periodogramm fuer unregelmaessig gesampelte Daten.

    Args:
        times: Zeit-Array (Tage seit Start)
        values: Signal-Werte
        min_period: Minimale Periode in Tagen
        max_period: Maximale Periode in Tagen

    Returns:
        Dict mit Perioden und Power-Werten
    """
    # Entferne NaN
    mask = ~np.isnan(values)
    times = times[mask]
    values = values[mask]

    if len(times) < 10:
        return {'error': 'Nicht genug Daten'}

    # Frequenz-Bereich
    min_freq = 1 / max_period
    max_freq = 1 / min_period
    frequencies = np.linspace(min_freq, max_freq, 1000)

    # Lomb-Scargle Periodogramm
    angular_freqs = 2 * np.pi * frequencies
    power = signal.lombscargle(times, values - values.mean(), angular_freqs)

    # Normalisiere Power
    power = power / power.max() if power.max() > 0 else power

    # Perioden
    periods = 1 / frequencies

    # Finde Peaks
    peak_indices, _ = signal.find_peaks(power, height=0.3, distance=10)

    peaks = []
    for idx in peak_indices:
        period = periods[idx]
        power_val = power[idx]

        peaks.append({
            'period_days': round(period, 2),
            'power': round(power_val, 4),
            'is_trivial': is_trivial_period(period),
            'is_prime': any(abs(period - p) < 0.5 for p in PRIME_PERIODS),
            'is_irrational': any(abs(period - v) < 0.3 for v in IRRATIONAL_PERIODS.values()),
        })

    # Sortiere nach Power
    peaks = sorted(peaks, key=lambda x: x['power'], reverse=True)

    return {
        'periods': periods.tolist(),
        'power': power.tolist(),
        'peaks': peaks[:20],  # Top 20 Peaks
        'non_trivial_peaks': [p for p in peaks if not p['is_trivial']][:10]
    }


def cross_correlation_analysis(df: pd.DataFrame) -> dict:
    """
    Cross-Korrelation zwischen KENO und Lotto.

    Sucht nach zeitversetzten Korrelationen.
    """
    # Extrahiere Signale
    keno = df['keno_total_winners'].fillna(0).values
    lotto = df['lotto_total_winners'].fillna(0).values

    # Nur Tage wo beide Spiele Daten haben
    mask = (df['keno_total_winners'].notna()) & (df['lotto_total_winners'].notna())

    results = []
    max_lag = 30  # Bis zu 30 Tage Versatz

    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            keno_shifted = keno[lag:]
            lotto_shifted = lotto[:len(lotto) - lag] if lag > 0 else lotto
        else:
            keno_shifted = keno[:len(keno) + lag]
            lotto_shifted = lotto[-lag:]

        if len(keno_shifted) < 10 or len(lotto_shifted) < 10:
            continue

        min_len = min(len(keno_shifted), len(lotto_shifted))
        keno_shifted = keno_shifted[:min_len]
        lotto_shifted = lotto_shifted[:min_len]

        # Pearson Korrelation
        r, p = pearsonr(keno_shifted, lotto_shifted)

        results.append({
            'lag_days': lag,
            'correlation': round(r, 4),
            'p_value': round(p, 6),
            'significant': p < 0.05
        })

    # Finde staerkste Korrelationen
    results = sorted(results, key=lambda x: abs(x['correlation']), reverse=True)

    return {
        'all_lags': results,
        'strongest': results[:5],
        'significant_lags': [r for r in results if r['significant']][:10]
    }


def jackpot_impact_analysis(df: pd.DataFrame) -> dict:
    """
    Analysiert wie Jackpots das Oekosystem beeinflussen.

    Hypothese: Nach einem Jackpot bei KENO/Lotto aendert sich
    das Verhalten der anderen Spiele.
    """
    results = {
        'keno_jackpot_impact': [],
        'lotto_jackpot_impact': [],
    }

    # KENO Jackpot -> Einfluss auf Lotto?
    keno_jackpot_days = df[df['keno_jackpot'] == 1].index.tolist()

    for jp_idx in keno_jackpot_days:
        # Lotto-Gewinner in den naechsten 7 Tagen
        window_start = jp_idx + 1
        window_end = min(jp_idx + 8, len(df))

        if window_end > window_start:
            lotto_after = df.iloc[window_start:window_end]['lotto_total_winners'].mean()
            lotto_before = df.iloc[max(0, jp_idx - 7):jp_idx]['lotto_total_winners'].mean()

            if not np.isnan(lotto_after) and not np.isnan(lotto_before) and lotto_before > 0:
                change = (lotto_after - lotto_before) / lotto_before * 100
                results['keno_jackpot_impact'].append({
                    'jp_date': str(df.iloc[jp_idx]['datum']),
                    'lotto_change_pct': round(change, 2)
                })

    # Lotto Jackpot -> Einfluss auf KENO?
    lotto_jackpot_days = df[df['lotto_jackpot'] == 1].index.tolist()

    for jp_idx in lotto_jackpot_days:
        window_start = jp_idx + 1
        window_end = min(jp_idx + 8, len(df))

        if window_end > window_start:
            keno_after = df.iloc[window_start:window_end]['keno_total_winners'].mean()
            keno_before = df.iloc[max(0, jp_idx - 7):jp_idx]['keno_total_winners'].mean()

            if not np.isnan(keno_after) and not np.isnan(keno_before) and keno_before > 0:
                change = (keno_after - keno_before) / keno_before * 100
                results['lotto_jackpot_impact'].append({
                    'jp_date': str(df.iloc[jp_idx]['datum']),
                    'keno_change_pct': round(change, 2)
                })

    # Durchschnittlicher Effekt
    if results['keno_jackpot_impact']:
        avg_lotto_change = np.mean([x['lotto_change_pct'] for x in results['keno_jackpot_impact']])
        results['avg_lotto_change_after_keno_jp'] = round(avg_lotto_change, 2)

    if results['lotto_jackpot_impact']:
        avg_keno_change = np.mean([x['keno_change_pct'] for x in results['lotto_jackpot_impact']])
        results['avg_keno_change_after_lotto_jp'] = round(avg_keno_change, 2)

    return results


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("VERSTECKTE PERIODEN-ANALYSE")
    print("=" * 60)
    print("\nWARNUNG: Triviale Perioden (7, 14, 30 Tage) werden IGNORIERT!")
    print("Das System wurde gegen solche Muster immunisiert.\n")

    # Output-Verzeichnis erstellen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print(f"Lade Daten von {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, parse_dates=['datum'])
    print(f"Geladen: {len(df)} Tage")

    # Zeit-Array (Tage seit Start)
    df['days'] = (df['datum'] - df['datum'].min()).dt.days
    times = df['days'].values

    results = {
        'metadata': {
            'data_source': str(DATA_PATH),
            'days_analyzed': len(df),
            'trivial_periods_ignored': TRIVIAL_PERIODS,
            'prime_periods_searched': PRIME_PERIODS,
            'irrational_periods_searched': list(IRRATIONAL_PERIODS.keys()),
        }
    }

    # 1. Lomb-Scargle auf Oekosystem-Signal
    print("\n--- Lomb-Scargle: Oekosystem-Gewinner ---")
    eco_ls = lomb_scargle_analysis(times, df['ecosystem_winners'].values)
    results['ecosystem_winners_periodogram'] = eco_ls

    print("Top 5 Peaks (inkl. triviale):")
    for i, peak in enumerate(eco_ls.get('peaks', [])[:5], 1):
        trivial = " [TRIVIAL]" if peak['is_trivial'] else ""
        prime = " [PRIME]" if peak['is_prime'] else ""
        irr = " [IRRATIONAL]" if peak['is_irrational'] else ""
        print(f"  {i}. {peak['period_days']:.1f} Tage (Power: {peak['power']:.3f}){trivial}{prime}{irr}")

    print("\nNicht-triviale Peaks:")
    non_trivial = eco_ls.get('non_trivial_peaks', [])
    if non_trivial:
        for i, peak in enumerate(non_trivial[:5], 1):
            prime = " [PRIME]" if peak['is_prime'] else ""
            irr = " [IRRATIONAL]" if peak['is_irrational'] else ""
            print(f"  {i}. {peak['period_days']:.1f} Tage (Power: {peak['power']:.3f}){prime}{irr}")
    else:
        print("  Keine gefunden.")

    # 2. Lomb-Scargle auf KENO Near-Miss
    print("\n--- Lomb-Scargle: KENO Near-Miss ---")
    keno_nm_ls = lomb_scargle_analysis(times, df['keno_near_miss'].values)
    results['keno_near_miss_periodogram'] = keno_nm_ls

    print("Nicht-triviale Peaks:")
    non_trivial = keno_nm_ls.get('non_trivial_peaks', [])
    if non_trivial:
        for i, peak in enumerate(non_trivial[:5], 1):
            print(f"  {i}. {peak['period_days']:.1f} Tage (Power: {peak['power']:.3f})")
    else:
        print("  Keine gefunden.")

    # 3. Cross-Korrelation KENO <-> Lotto
    print("\n--- Cross-Korrelation: KENO <-> Lotto ---")
    cross_corr = cross_correlation_analysis(df)
    results['cross_correlation'] = cross_corr

    print("Staerkste Korrelationen:")
    for r in cross_corr.get('strongest', [])[:5]:
        sig = " *" if r['significant'] else ""
        print(f"  Lag {r['lag_days']:+3d} Tage: r={r['correlation']:+.3f} (p={r['p_value']:.4f}){sig}")

    # 4. Jackpot-Impact Analyse
    print("\n--- Jackpot-Impact Analyse ---")
    jp_impact = jackpot_impact_analysis(df)
    results['jackpot_impact'] = jp_impact

    if 'avg_lotto_change_after_keno_jp' in jp_impact:
        print(f"Nach KENO-Jackpot: Lotto aendert sich um {jp_impact['avg_lotto_change_after_keno_jp']:+.1f}%")
    if 'avg_keno_change_after_lotto_jp' in jp_impact:
        print(f"Nach Lotto-Jackpot: KENO aendert sich um {jp_impact['avg_keno_change_after_lotto_jp']:+.1f}%")

    # Speichern
    output_file = OUTPUT_DIR / "hidden_periods_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    # Finde beste nicht-triviale Periode
    all_non_trivial = eco_ls.get('non_trivial_peaks', []) + keno_nm_ls.get('non_trivial_peaks', [])
    if all_non_trivial:
        best = max(all_non_trivial, key=lambda x: x['power'])
        print(f"\nBeste nicht-triviale Periode: {best['period_days']:.1f} Tage")
        print(f"Power: {best['power']:.3f}")

        if best['is_prime']:
            print("Typ: PRIMZAHL-basiert")
        elif best['is_irrational']:
            print("Typ: IRRATIONAL")
        else:
            print("Typ: Unbekannt (weitere Analyse noetig)")
    else:
        print("\nKeine starken nicht-trivialen Perioden gefunden.")
        print("Das System ist gut gegen einfache Perioden-Erkennung geschuetzt.")

    return results


if __name__ == '__main__':
    main()
