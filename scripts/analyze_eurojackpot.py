#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EuroJackpot Analyse - Super-Model Methodik Anwendung
=====================================================

Wendet die bewaehrte KENO Super-Model Methodik auf EuroJackpot an.

EuroJackpot Format:
- 5 Hauptzahlen aus 50 (E1-E5)
- 2 Eurozahlen aus 12 (Euro1, Euro2)
- Spieleinsatz und Jackpot-Gewinner

Hypothesen zu testen:
1. WL-003: Jackpot-Cooldown (nach Jackpot weniger ROI)
2. WL-008: Positions-Praeferenzen
3. Zahlen-Paar Analyse
"""

import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path

import numpy as np

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "eurojackpot" / "EJ_ab_2022_bereinigt.csv"
OUTPUT_DIR = BASE_DIR / "results" / "eurojackpot"


def load_eurojackpot_data(filepath: Path) -> list[dict]:
    """Lade EuroJackpot Ziehungsdaten."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                datum = datetime.strptime(row['Datum'], '%d.%m.%Y')

                # Hauptzahlen (5 aus 50)
                hauptzahlen = sorted([
                    int(row['E1']), int(row['E2']), int(row['E3']),
                    int(row['E4']), int(row['E5'])
                ])

                # Eurozahlen (2 aus 12)
                eurozahlen = sorted([int(row['Euro1']), int(row['Euro2'])])

                # Spieleinsatz und Jackpot
                spieleinsatz = float(row.get('Spieleinsatz', '0').replace(',', '.'))
                jackpot = int(row.get('Jackpot', '0'))

                draws.append({
                    'datum': datum,
                    'hauptzahlen': hauptzahlen,
                    'eurozahlen': eurozahlen,
                    'spieleinsatz': spieleinsatz,
                    'jackpot_winners': jackpot
                })
            except (ValueError, KeyError) as e:
                continue

    # Sortiere nach Datum
    draws.sort(key=lambda x: x['datum'])
    return draws


def analyze_jackpot_cooldown(draws: list[dict], cooldown_days: int = 30) -> dict:
    """
    Hypothese WL-003: Nach Jackpot-Gewinnen sind die naechsten Ziehungen "kalt".

    Bei KENO: 30 Tage Cooldown nach GK10_10 = -66% ROI
    Teste ob aehnliches Muster bei EuroJackpot existiert.
    """
    results = {
        'after_jackpot': {'count': 0, 'total_stake': 0, 'next_jackpots': 0},
        'normal': {'count': 0, 'total_stake': 0, 'next_jackpots': 0}
    }

    jackpot_dates = [d['datum'] for d in draws if d['jackpot_winners'] > 0]

    for i, draw in enumerate(draws):
        # Pruefe ob innerhalb Cooldown-Phase
        in_cooldown = False
        for jp_date in jackpot_dates:
            if timedelta(0) < (draw['datum'] - jp_date) <= timedelta(days=cooldown_days):
                in_cooldown = True
                break

        key = 'after_jackpot' if in_cooldown else 'normal'
        results[key]['count'] += 1
        results[key]['total_stake'] += draw['spieleinsatz']

        # Zaehle ob diese Ziehung selbst einen Jackpot hatte
        if draw['jackpot_winners'] > 0:
            results[key]['next_jackpots'] += 1

    # Berechne Jackpot-Raten
    for key in results:
        if results[key]['count'] > 0:
            results[key]['jackpot_rate'] = results[key]['next_jackpots'] / results[key]['count']
            results[key]['avg_stake'] = results[key]['total_stake'] / results[key]['count']
        else:
            results[key]['jackpot_rate'] = 0
            results[key]['avg_stake'] = 0

    # Vergleich
    if results['normal']['jackpot_rate'] > 0:
        cooldown_effect = (results['after_jackpot']['jackpot_rate'] - results['normal']['jackpot_rate']) / results['normal']['jackpot_rate']
    else:
        cooldown_effect = 0

    return {
        'cooldown_days': cooldown_days,
        'total_draws': len(draws),
        'total_jackpots': len(jackpot_dates),
        'after_jackpot_stats': results['after_jackpot'],
        'normal_stats': results['normal'],
        'cooldown_effect_percent': round(cooldown_effect * 100, 2),
        'hypothesis_confirmed': cooldown_effect < -0.1  # 10% weniger Jackpots nach Jackpot
    }


def analyze_hauptzahlen_pairs(draws: list[dict]) -> dict:
    """
    Analysiere Haeufigkeit von Zahlenpaaren bei Hauptzahlen (5 aus 50).

    Erwartungswert: P(Paar) = (5/50) * (4/49) = 0.00816
    """
    pair_counter = Counter()

    for draw in draws:
        for pair in combinations(draw['hauptzahlen'], 2):
            pair_counter[pair] += 1

    n_draws = len(draws)
    expected = (5/50) * (4/49) * n_draws

    # Top 50 Paare
    top_pairs = []
    for pair, count in pair_counter.most_common(50):
        deviation = count - expected
        deviation_pct = (deviation / expected) * 100 if expected > 0 else 0
        top_pairs.append({
            'pair': list(pair),
            'frequency': count,
            'expected': round(expected, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    return {
        'total_draws': n_draws,
        'expected_pair_frequency': round(expected, 2),
        'total_possible_pairs': 1225,  # 50 choose 2
        'top_50_pairs': top_pairs,
        'max_deviation_percent': max(p['deviation_percent'] for p in top_pairs) if top_pairs else 0
    }


def analyze_eurozahlen_pairs(draws: list[dict]) -> dict:
    """
    Analysiere Eurozahlen-Paare (2 aus 12).

    Da immer 2 Eurozahlen gezogen werden, ist die Paar-Frequenz
    gleich der Ziehungs-Anzahl fuer jedes Paar das erscheint.
    """
    pair_counter = Counter()

    for draw in draws:
        pair = tuple(sorted(draw['eurozahlen']))
        pair_counter[pair] += 1

    n_draws = len(draws)
    n_possible_pairs = 66  # 12 choose 2
    expected = n_draws / n_possible_pairs

    # Alle Paare sortiert
    all_pairs = []
    for pair, count in pair_counter.most_common():
        deviation = count - expected
        deviation_pct = (deviation / expected) * 100 if expected > 0 else 0
        all_pairs.append({
            'pair': list(pair),
            'frequency': count,
            'expected': round(expected, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    return {
        'total_draws': n_draws,
        'expected_pair_frequency': round(expected, 2),
        'total_possible_pairs': n_possible_pairs,
        'all_pairs': all_pairs,
        'most_frequent': all_pairs[0] if all_pairs else None,
        'least_frequent': all_pairs[-1] if all_pairs else None
    }


def analyze_number_frequency(draws: list[dict]) -> dict:
    """Analysiere Zahlen-Frequenz fuer Haupt- und Eurozahlen."""
    haupt_freq = Counter()
    euro_freq = Counter()

    for draw in draws:
        for z in draw['hauptzahlen']:
            haupt_freq[z] += 1
        for z in draw['eurozahlen']:
            euro_freq[z] += 1

    n_draws = len(draws)

    # Erwartungswerte
    haupt_expected = 5 / 50 * n_draws  # Jede Hauptzahl erwartet
    euro_expected = 2 / 12 * n_draws   # Jede Eurozahl erwartet

    # Analyse Hauptzahlen
    haupt_analysis = []
    for num in range(1, 51):
        freq = haupt_freq.get(num, 0)
        deviation = freq - haupt_expected
        deviation_pct = (deviation / haupt_expected) * 100 if haupt_expected > 0 else 0
        haupt_analysis.append({
            'number': num,
            'frequency': freq,
            'expected': round(haupt_expected, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    # Analyse Eurozahlen
    euro_analysis = []
    for num in range(1, 13):
        freq = euro_freq.get(num, 0)
        deviation = freq - euro_expected
        deviation_pct = (deviation / euro_expected) * 100 if euro_expected > 0 else 0
        euro_analysis.append({
            'number': num,
            'frequency': freq,
            'expected': round(euro_expected, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    # Sortiere nach Frequenz
    haupt_analysis.sort(key=lambda x: x['frequency'], reverse=True)
    euro_analysis.sort(key=lambda x: x['frequency'], reverse=True)

    return {
        'hauptzahlen': {
            'expected_per_number': round(haupt_expected, 2),
            'by_frequency': haupt_analysis,
            'most_frequent': haupt_analysis[:10],
            'least_frequent': haupt_analysis[-10:]
        },
        'eurozahlen': {
            'expected_per_number': round(euro_expected, 2),
            'by_frequency': euro_analysis,
            'most_frequent': euro_analysis[:5],
            'least_frequent': euro_analysis[-5:]
        }
    }


def analyze_spieleinsatz_correlation(draws: list[dict]) -> dict:
    """
    Analysiere Korrelation zwischen Spieleinsatz und Jackpot-Gewinnen.

    Hypothese: Hoher Spieleinsatz = mehr Spieler = weniger attraktiv fuer Jackpot-Manipulation
    """
    einsatz_values = [d['spieleinsatz'] for d in draws]
    median_einsatz = np.median(einsatz_values)

    high_stake = {'count': 0, 'jackpots': 0}
    low_stake = {'count': 0, 'jackpots': 0}

    for draw in draws:
        if draw['spieleinsatz'] > median_einsatz:
            high_stake['count'] += 1
            if draw['jackpot_winners'] > 0:
                high_stake['jackpots'] += 1
        else:
            low_stake['count'] += 1
            if draw['jackpot_winners'] > 0:
                low_stake['jackpots'] += 1

    # Jackpot-Raten
    high_rate = high_stake['jackpots'] / high_stake['count'] if high_stake['count'] > 0 else 0
    low_rate = low_stake['jackpots'] / low_stake['count'] if low_stake['count'] > 0 else 0

    return {
        'median_spieleinsatz': round(median_einsatz, 2),
        'high_stake_draws': high_stake['count'],
        'high_stake_jackpots': high_stake['jackpots'],
        'high_stake_jackpot_rate': round(high_rate * 100, 2),
        'low_stake_draws': low_stake['count'],
        'low_stake_jackpots': low_stake['jackpots'],
        'low_stake_jackpot_rate': round(low_rate * 100, 2),
        'hypothesis_confirmed': high_rate < low_rate  # Weniger Jackpots bei hohem Einsatz
    }


def analyze_weekday_patterns(draws: list[dict]) -> dict:
    """Analysiere Muster nach Wochentag."""
    weekday_stats = {i: {'count': 0, 'jackpots': 0, 'total_stake': 0} for i in range(7)}
    weekday_names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    for draw in draws:
        wd = draw['datum'].weekday()
        weekday_stats[wd]['count'] += 1
        weekday_stats[wd]['total_stake'] += draw['spieleinsatz']
        if draw['jackpot_winners'] > 0:
            weekday_stats[wd]['jackpots'] += 1

    result = []
    for wd in range(7):
        stats = weekday_stats[wd]
        if stats['count'] > 0:
            result.append({
                'weekday': weekday_names[wd],
                'draws': stats['count'],
                'jackpots': stats['jackpots'],
                'jackpot_rate': round(stats['jackpots'] / stats['count'] * 100, 2),
                'avg_stake': round(stats['total_stake'] / stats['count'], 2)
            })

    return {'by_weekday': result}


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("EUROJACKPOT ANALYSE - Super-Model Methodik")
    print("=" * 60)

    # Output-Verzeichnis erstellen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print(f"\nLade Daten von {DATA_PATH}...")
    draws = load_eurojackpot_data(DATA_PATH)
    print(f"Geladen: {len(draws)} Ziehungen")
    print(f"Zeitraum: {draws[0]['datum'].strftime('%d.%m.%Y')} - {draws[-1]['datum'].strftime('%d.%m.%Y')}")

    # Jackpot-Statistik
    jackpots = [d for d in draws if d['jackpot_winners'] > 0]
    print(f"Jackpot-Gewinne: {len(jackpots)}")

    results = {
        'metadata': {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': str(DATA_PATH),
            'total_draws': len(draws),
            'date_range': {
                'start': draws[0]['datum'].strftime('%Y-%m-%d'),
                'end': draws[-1]['datum'].strftime('%Y-%m-%d')
            },
            'total_jackpots': len(jackpots)
        }
    }

    # 1. Jackpot-Cooldown Analyse
    print("\n--- Hypothese WL-003: Jackpot-Cooldown ---")
    cooldown_result = analyze_jackpot_cooldown(draws, cooldown_days=30)
    results['jackpot_cooldown'] = cooldown_result
    print(f"Ziehungen nach Jackpot (30 Tage): {cooldown_result['after_jackpot_stats']['count']}")
    print(f"Normale Ziehungen: {cooldown_result['normal_stats']['count']}")
    print(f"Jackpot-Rate nach Jackpot: {cooldown_result['after_jackpot_stats']['jackpot_rate']*100:.1f}%")
    print(f"Jackpot-Rate normal: {cooldown_result['normal_stats']['jackpot_rate']*100:.1f}%")
    print(f"Cooldown-Effekt: {cooldown_result['cooldown_effect_percent']:+.1f}%")
    print(f"Hypothese bestaetigt: {cooldown_result['hypothesis_confirmed']}")

    # 2. Hauptzahlen-Paare
    print("\n--- Hauptzahlen-Paar Analyse ---")
    haupt_pairs = analyze_hauptzahlen_pairs(draws)
    results['hauptzahlen_pairs'] = haupt_pairs
    print(f"Erwartungswert pro Paar: {haupt_pairs['expected_pair_frequency']}")
    print(f"Max Abweichung: {haupt_pairs['max_deviation_percent']:+.1f}%")
    print("Top 5 Paare:")
    for p in haupt_pairs['top_50_pairs'][:5]:
        print(f"  {p['pair'][0]:2d}-{p['pair'][1]:2d}: {p['frequency']}x ({p['deviation_percent']:+.1f}%)")

    # 3. Eurozahlen-Paare
    print("\n--- Eurozahlen-Paar Analyse ---")
    euro_pairs = analyze_eurozahlen_pairs(draws)
    results['eurozahlen_pairs'] = euro_pairs
    print(f"Erwartungswert pro Paar: {euro_pairs['expected_pair_frequency']}")
    if euro_pairs['most_frequent']:
        print(f"Haeufigste: {euro_pairs['most_frequent']['pair']} - {euro_pairs['most_frequent']['frequency']}x")
    if euro_pairs['least_frequent']:
        print(f"Seltenste: {euro_pairs['least_frequent']['pair']} - {euro_pairs['least_frequent']['frequency']}x")

    # 4. Zahlen-Frequenz
    print("\n--- Zahlen-Frequenz ---")
    freq_result = analyze_number_frequency(draws)
    results['number_frequency'] = freq_result
    print("Top 5 Hauptzahlen:")
    for n in freq_result['hauptzahlen']['most_frequent'][:5]:
        print(f"  {n['number']:2d}: {n['frequency']}x ({n['deviation_percent']:+.1f}%)")
    print("Top 3 Eurozahlen:")
    for n in freq_result['eurozahlen']['most_frequent'][:3]:
        print(f"  {n['number']:2d}: {n['frequency']}x ({n['deviation_percent']:+.1f}%)")

    # 5. Spieleinsatz-Korrelation
    print("\n--- Spieleinsatz-Korrelation ---")
    stake_result = analyze_spieleinsatz_correlation(draws)
    results['spieleinsatz_correlation'] = stake_result
    print(f"Median Spieleinsatz: {stake_result['median_spieleinsatz']:,.0f} EUR")
    print(f"Jackpot-Rate bei hohem Einsatz: {stake_result['high_stake_jackpot_rate']}%")
    print(f"Jackpot-Rate bei niedrigem Einsatz: {stake_result['low_stake_jackpot_rate']}%")
    print(f"Hypothese bestaetigt: {stake_result['hypothesis_confirmed']}")

    # 6. Wochentags-Muster
    print("\n--- Wochentags-Muster ---")
    weekday_result = analyze_weekday_patterns(draws)
    results['weekday_patterns'] = weekday_result
    for wd in weekday_result['by_weekday']:
        if wd['draws'] > 0:
            print(f"  {wd['weekday']}: {wd['draws']} Ziehungen, {wd['jackpots']} Jackpots ({wd['jackpot_rate']}%)")

    # Speichern
    output_file = OUTPUT_DIR / "eurojackpot_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG - EuroJackpot Hypothesen")
    print("=" * 60)

    hypotheses = [
        ("WL-003 Jackpot-Cooldown", cooldown_result['hypothesis_confirmed'],
         f"{cooldown_result['cooldown_effect_percent']:+.1f}% Effekt"),
        ("Spieleinsatz-Korrelation", stake_result['hypothesis_confirmed'],
         f"High: {stake_result['high_stake_jackpot_rate']}% vs Low: {stake_result['low_stake_jackpot_rate']}%")
    ]

    for name, confirmed, detail in hypotheses:
        status = "BESTAETIGT" if confirmed else "NICHT BESTAETIGT"
        print(f"{name}: {status}")
        print(f"  → {detail}")

    return results


if __name__ == '__main__':
    main()
