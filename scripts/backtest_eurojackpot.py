#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EuroJackpot Backtest - Jackpot-Cooldown Strategie
=================================================

Testet die Jackpot-Cooldown Strategie (WL-003) auf EuroJackpot.

Strategie:
- NICHT spielen in den 30 Tagen nach einem Jackpot-Gewinn
- Nur spielen wenn kein kuerzlicher Jackpot

EuroJackpot Gewinnklassen (Beispiel):
- GK1: 5+2 richtig (Jackpot) - variable Quote
- GK2: 5+1 richtig - ca. 500.000 EUR
- GK3: 5+0 richtig - ca. 100.000 EUR
- GK4: 4+2 richtig - ca. 5.000 EUR
- GK5: 4+1 richtig - ca. 200 EUR
- GK6: 4+0 richtig - ca. 100 EUR
- GK7: 3+2 richtig - ca. 50 EUR
- GK8: 2+2 richtig - ca. 20 EUR
- GK9: 3+1 richtig - ca. 17 EUR
- GK10: 3+0 richtig - ca. 13 EUR
- GK11: 1+2 richtig - ca. 10 EUR
- GK12: 2+1 richtig - ca. 7 EUR
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import random

import numpy as np

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "eurojackpot" / "EJ_ab_2022_bereinigt.csv"
OUTPUT_DIR = BASE_DIR / "results" / "eurojackpot"

# EuroJackpot Einsatz pro Tipp
TICKET_PRICE = 2.0  # EUR

# Durchschnittliche Quoten (EUR) - vereinfacht
EXPECTED_QUOTES = {
    '5+2': 90_000_000,  # Jackpot (variabel, hier Durchschnitt)
    '5+1': 500_000,
    '5+0': 100_000,
    '4+2': 5_000,
    '4+1': 200,
    '4+0': 100,
    '3+2': 50,
    '2+2': 20,
    '3+1': 17,
    '3+0': 13,
    '1+2': 10,
    '2+1': 7,
}


def load_eurojackpot_data(filepath: Path) -> list[dict]:
    """Lade EuroJackpot Ziehungsdaten."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                datum = datetime.strptime(row['Datum'], '%d.%m.%Y')
                hauptzahlen = sorted([
                    int(row['E1']), int(row['E2']), int(row['E3']),
                    int(row['E4']), int(row['E5'])
                ])
                eurozahlen = sorted([int(row['Euro1']), int(row['Euro2'])])
                spieleinsatz = float(row.get('Spieleinsatz', '0').replace(',', '.'))
                jackpot = int(row.get('Jackpot', '0'))

                draws.append({
                    'datum': datum,
                    'hauptzahlen': set(hauptzahlen),
                    'eurozahlen': set(eurozahlen),
                    'spieleinsatz': spieleinsatz,
                    'jackpot_winners': jackpot
                })
            except (ValueError, KeyError):
                continue

    draws.sort(key=lambda x: x['datum'])
    return draws


def calculate_gewinnklasse(tipp_haupt: set, tipp_euro: set,
                           ziehung_haupt: set, ziehung_euro: set) -> str | None:
    """
    Berechne Gewinnklasse basierend auf Uebereinstimmungen.

    Returns: String wie '5+2', '4+1' oder None wenn kein Gewinn
    """
    haupt_richtig = len(tipp_haupt & ziehung_haupt)
    euro_richtig = len(tipp_euro & ziehung_euro)

    # EuroJackpot Gewinnklassen
    if haupt_richtig == 5 and euro_richtig == 2:
        return '5+2'
    elif haupt_richtig == 5 and euro_richtig == 1:
        return '5+1'
    elif haupt_richtig == 5 and euro_richtig == 0:
        return '5+0'
    elif haupt_richtig == 4 and euro_richtig == 2:
        return '4+2'
    elif haupt_richtig == 4 and euro_richtig == 1:
        return '4+1'
    elif haupt_richtig == 4 and euro_richtig == 0:
        return '4+0'
    elif haupt_richtig == 3 and euro_richtig == 2:
        return '3+2'
    elif haupt_richtig == 2 and euro_richtig == 2:
        return '2+2'
    elif haupt_richtig == 3 and euro_richtig == 1:
        return '3+1'
    elif haupt_richtig == 3 and euro_richtig == 0:
        return '3+0'
    elif haupt_richtig == 1 and euro_richtig == 2:
        return '1+2'
    elif haupt_richtig == 2 and euro_richtig == 1:
        return '2+1'
    return None


def generate_random_tipps(n_tipps: int = 100, seed: int = 42) -> list[dict]:
    """
    Generiere zufaellige EuroJackpot Tipps.

    Returns: Liste von {'haupt': set, 'euro': set}
    """
    random.seed(seed)
    tipps = []
    for _ in range(n_tipps):
        haupt = set(random.sample(range(1, 51), 5))
        euro = set(random.sample(range(1, 13), 2))
        tipps.append({'haupt': haupt, 'euro': euro})
    return tipps


def generate_popular_tipps() -> list[dict]:
    """
    Generiere Tipps basierend auf haeufigen Zahlen aus der Analyse.

    Top Hauptzahlen: 11, 20, 30, 21, 17
    Top Eurozahlen: 3, 5
    """
    return [
        # Tipp 1: Top 5 Hauptzahlen + Top 2 Eurozahlen
        {'haupt': {11, 20, 30, 21, 17}, 'euro': {3, 5}},
        # Tipp 2: Variation
        {'haupt': {11, 20, 30, 17, 28}, 'euro': {3, 9}},
        # Tipp 3: Weitere Variation
        {'haupt': {11, 16, 27, 41, 30}, 'euro': {5, 10}},
    ]


def backtest_strategy(draws: list[dict], tipps: list[dict],
                      cooldown_days: int = 30,
                      strategy_name: str = "baseline") -> dict:
    """
    Fuehre Backtest fuer eine Strategie durch.

    Args:
        draws: Ziehungsdaten
        tipps: Liste von Tipps
        cooldown_days: Tage nach Jackpot ohne Spielen (0 = immer spielen)
        strategy_name: Name der Strategie

    Returns:
        Backtest-Ergebnisse
    """
    jackpot_dates = [d['datum'] for d in draws if d['jackpot_winners'] > 0]

    results = {
        'strategy': strategy_name,
        'cooldown_days': cooldown_days,
        'plays': 0,
        'skipped': 0,
        'invested': 0,
        'won': 0,
        'gewinnklassen': defaultdict(int),
        'details': []
    }

    for draw in draws:
        # Pruefe Cooldown
        in_cooldown = False
        if cooldown_days > 0:
            for jp_date in jackpot_dates:
                if timedelta(0) < (draw['datum'] - jp_date) <= timedelta(days=cooldown_days):
                    in_cooldown = True
                    break

        if in_cooldown:
            results['skipped'] += 1
            continue

        # Spiele alle Tipps
        results['plays'] += 1
        results['invested'] += len(tipps) * TICKET_PRICE

        for tipp in tipps:
            gk = calculate_gewinnklasse(
                tipp['haupt'], tipp['euro'],
                draw['hauptzahlen'], draw['eurozahlen']
            )
            if gk:
                gewinn = EXPECTED_QUOTES.get(gk, 0)
                results['won'] += gewinn
                results['gewinnklassen'][gk] += 1
                results['details'].append({
                    'datum': draw['datum'].strftime('%Y-%m-%d'),
                    'gewinnklasse': gk,
                    'gewinn': gewinn
                })

    # ROI berechnen
    if results['invested'] > 0:
        results['roi'] = (results['won'] - results['invested']) / results['invested'] * 100
    else:
        results['roi'] = 0

    results['gewinnklassen'] = dict(results['gewinnklassen'])

    return results


def run_full_backtest(draws: list[dict]) -> dict:
    """Fuehre vollstaendigen Backtest mit verschiedenen Strategien durch."""

    # Generiere Tipps
    random_tipps = generate_random_tipps(n_tipps=10, seed=42)
    popular_tipps = generate_popular_tipps()

    all_results = {
        'metadata': {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_draws': len(draws),
            'date_range': {
                'start': draws[0]['datum'].strftime('%Y-%m-%d'),
                'end': draws[-1]['datum'].strftime('%Y-%m-%d')
            },
            'ticket_price': TICKET_PRICE
        },
        'strategies': []
    }

    print("\n" + "=" * 60)
    print("BACKTEST ERGEBNISSE")
    print("=" * 60)

    # Strategie 1: Baseline (immer spielen, zufaellige Tipps)
    baseline_random = backtest_strategy(draws, random_tipps, cooldown_days=0,
                                        strategy_name="baseline_random")
    all_results['strategies'].append(baseline_random)
    print(f"\n{baseline_random['strategy']}:")
    print(f"  Spiele: {baseline_random['plays']}, Investiert: {baseline_random['invested']:,.0f} EUR")
    print(f"  Gewonnen: {baseline_random['won']:,.0f} EUR")
    print(f"  ROI: {baseline_random['roi']:+.1f}%")

    # Strategie 2: Cooldown (30 Tage), zufaellige Tipps
    cooldown_random = backtest_strategy(draws, random_tipps, cooldown_days=30,
                                        strategy_name="cooldown_30d_random")
    all_results['strategies'].append(cooldown_random)
    print(f"\n{cooldown_random['strategy']}:")
    print(f"  Spiele: {cooldown_random['plays']}, Uebersprungen: {cooldown_random['skipped']}")
    print(f"  Investiert: {cooldown_random['invested']:,.0f} EUR")
    print(f"  Gewonnen: {cooldown_random['won']:,.0f} EUR")
    print(f"  ROI: {cooldown_random['roi']:+.1f}%")

    # Strategie 3: Baseline, populaere Zahlen
    baseline_popular = backtest_strategy(draws, popular_tipps, cooldown_days=0,
                                         strategy_name="baseline_popular")
    all_results['strategies'].append(baseline_popular)
    print(f"\n{baseline_popular['strategy']}:")
    print(f"  Spiele: {baseline_popular['plays']}, Investiert: {baseline_popular['invested']:,.0f} EUR")
    print(f"  Gewonnen: {baseline_popular['won']:,.0f} EUR")
    print(f"  ROI: {baseline_popular['roi']:+.1f}%")
    print(f"  Gewinnklassen: {baseline_popular['gewinnklassen']}")

    # Strategie 4: Cooldown + populaere Zahlen
    cooldown_popular = backtest_strategy(draws, popular_tipps, cooldown_days=30,
                                         strategy_name="cooldown_30d_popular")
    all_results['strategies'].append(cooldown_popular)
    print(f"\n{cooldown_popular['strategy']}:")
    print(f"  Spiele: {cooldown_popular['plays']}, Uebersprungen: {cooldown_popular['skipped']}")
    print(f"  Investiert: {cooldown_popular['invested']:,.0f} EUR")
    print(f"  Gewonnen: {cooldown_popular['won']:,.0f} EUR")
    print(f"  ROI: {cooldown_popular['roi']:+.1f}%")
    print(f"  Gewinnklassen: {cooldown_popular['gewinnklassen']}")

    # Vergleich
    print("\n" + "-" * 60)
    print("VERGLEICH: Baseline vs Cooldown-Strategie")
    print("-" * 60)

    if baseline_popular['roi'] != 0:
        improvement = cooldown_popular['roi'] - baseline_popular['roi']
        print(f"Baseline ROI (populaer): {baseline_popular['roi']:+.1f}%")
        print(f"Cooldown ROI (populaer): {cooldown_popular['roi']:+.1f}%")
        print(f"Verbesserung: {improvement:+.1f} Prozentpunkte")
    else:
        print("Keine Gewinne in beiden Strategien")

    all_results['comparison'] = {
        'baseline_roi': baseline_popular['roi'],
        'cooldown_roi': cooldown_popular['roi'],
        'improvement_pp': cooldown_popular['roi'] - baseline_popular['roi']
    }

    return all_results


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("EUROJACKPOT BACKTEST - Jackpot-Cooldown Strategie")
    print("=" * 60)

    # Output-Verzeichnis erstellen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print(f"\nLade Daten von {DATA_PATH}...")
    draws = load_eurojackpot_data(DATA_PATH)
    print(f"Geladen: {len(draws)} Ziehungen")

    # Backtest durchfuehren
    results = run_full_backtest(draws)

    # Speichern
    output_file = OUTPUT_DIR / "eurojackpot_backtest.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("FAZIT")
    print("=" * 60)

    best = max(results['strategies'], key=lambda x: x['roi'])
    print(f"\nBeste Strategie: {best['strategy']}")
    print(f"ROI: {best['roi']:+.1f}%")

    # Gewinnklassen-Uebersicht
    if best['gewinnklassen']:
        print("\nGewinnklassen:")
        for gk, count in sorted(best['gewinnklassen'].items()):
            quote = EXPECTED_QUOTES.get(gk, 0)
            print(f"  {gk}: {count}x (je {quote:,.0f} EUR)")

    return results


if __name__ == '__main__':
    main()
