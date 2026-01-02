#!/usr/bin/env python3
"""
Analyse: Wie wählt das KENO-System die Jackpot-Zahlen aus?

METHODIK:
1. Nehme die 20 gezogenen Zahlen eines Jackpot-Tages
2. Generiere alle C(20,10) = 184.756 mögliche 10er-Kombinationen
3. Analysiere jede Kombination nach verschiedenen Kriterien
4. Finde was die ECHTE Gewinner-Kombination von den anderen unterscheidet

KYRITZ-FALL (25.10.2025):
- 20 Gezogene: [2,5,9,12,19,20,26,34,35,36,39,42,45,48,49,54,55,62,64,66]
- Gewinner:    [5,12,20,26,34,36,42,45,48,66]
"""

import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations
from collections import Counter
from datetime import datetime
import json

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Kyritz-Daten
KYRITZ_DATE = "2025-10-25"
KYRITZ_DRAWN_20 = [2, 5, 9, 12, 19, 20, 26, 34, 35, 36, 39, 42, 45, 48, 49, 54, 55, 62, 64, 66]
KYRITZ_WINNER_10 = [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]


def load_data():
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def calculate_combo_metrics(combo, df, target_date):
    """Berechne verschiedene Metriken für eine Kombination."""
    combo_set = set(combo)
    combo_list = sorted(list(combo))

    metrics = {
        'combo': combo_list,
        'sum': sum(combo),
        'mean': sum(combo) / len(combo),
        'std': np.std(combo_list),
        'range': max(combo) - min(combo),
        'gaps': [],  # Abstände zwischen Zahlen
        'decades': {},  # Verteilung auf Zehnergruppen
        'odd_count': sum(1 for n in combo if n % 2 == 1),
        'even_count': sum(1 for n in combo if n % 2 == 0),
        'prime_count': 0,
        'consecutive_pairs': 0,
        'historical_freq': 0,  # Wie oft diese Kombi historisch 10/10 war
        'historical_hits': [],  # Treffer-Verteilung historisch
        'avg_hits': 0,
        'max_hits': 0,
    }

    # Gaps (Abstände)
    for i in range(len(combo_list) - 1):
        metrics['gaps'].append(combo_list[i+1] - combo_list[i])
    metrics['avg_gap'] = np.mean(metrics['gaps']) if metrics['gaps'] else 0
    metrics['max_gap'] = max(metrics['gaps']) if metrics['gaps'] else 0
    metrics['min_gap'] = min(metrics['gaps']) if metrics['gaps'] else 0

    # Zehnergruppen (1-10, 11-20, ..., 61-70)
    for n in combo:
        decade = (n - 1) // 10
        metrics['decades'][decade] = metrics['decades'].get(decade, 0) + 1
    metrics['decades_used'] = len(metrics['decades'])
    metrics['max_per_decade'] = max(metrics['decades'].values()) if metrics['decades'] else 0

    # Primzahlen
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67}
    metrics['prime_count'] = sum(1 for n in combo if n in primes)

    # Aufeinanderfolgende Paare
    for i in range(len(combo_list) - 1):
        if combo_list[i+1] - combo_list[i] == 1:
            metrics['consecutive_pairs'] += 1

    # Historische Analyse (vor dem Jackpot-Tag)
    hist_df = df[df['datum'] < pd.Timestamp(target_date)]

    hits_list = []
    for _, row in hist_df.iterrows():
        drawn = row['zahlen']
        hits = len(combo_set & drawn)
        hits_list.append(hits)
        if hits == 10:
            metrics['historical_freq'] += 1

    metrics['historical_hits'] = hits_list
    metrics['avg_hits'] = np.mean(hits_list) if hits_list else 0
    metrics['max_hits'] = max(hits_list) if hits_list else 0

    # Treffer-Verteilung
    hit_dist = Counter(hits_list)
    metrics['hits_6plus'] = sum(hit_dist.get(i, 0) for i in range(6, 11))
    metrics['hits_7plus'] = sum(hit_dist.get(i, 0) for i in range(7, 11))
    metrics['hits_8plus'] = sum(hit_dist.get(i, 0) for i in range(8, 11))

    return metrics


def analyze_all_combinations(drawn_20, winner_10, df, target_date, sample_size=None):
    """Analysiere alle oder eine Stichprobe der Kombinationen."""

    all_combos = list(combinations(drawn_20, 10))
    total_combos = len(all_combos)
    print(f"Generiere {total_combos:,} Kombinationen...")

    # Finde Index der Gewinner-Kombination
    winner_tuple = tuple(sorted(winner_10))
    winner_idx = None
    for i, combo in enumerate(all_combos):
        if tuple(sorted(combo)) == winner_tuple:
            winner_idx = i
            break

    print(f"Gewinner-Kombination ist Kombination #{winner_idx + 1}")

    # Bei großer Anzahl: Sample nehmen (aber immer Gewinner einschließen)
    if sample_size and sample_size < total_combos:
        print(f"Analysiere Stichprobe von {sample_size} Kombinationen...")
        import random
        sample_indices = set(random.sample(range(total_combos), sample_size - 1))
        sample_indices.add(winner_idx)  # Immer Gewinner einschließen
        combos_to_analyze = [(i, all_combos[i]) for i in sorted(sample_indices)]
    else:
        combos_to_analyze = list(enumerate(all_combos))

    # Analysiere jede Kombination
    results = []
    winner_metrics = None

    for count, (idx, combo) in enumerate(combos_to_analyze):
        if count % 1000 == 0:
            print(f"  Analysiere {count}/{len(combos_to_analyze)}...")

        metrics = calculate_combo_metrics(combo, df, target_date)
        metrics['combo_idx'] = idx
        metrics['is_winner'] = (idx == winner_idx)

        # Speichere nur Zusammenfassung (ohne historische Hits-Liste)
        summary = {k: v for k, v in metrics.items() if k != 'historical_hits'}
        results.append(summary)

        if idx == winner_idx:
            winner_metrics = metrics.copy()

    return results, winner_metrics


def find_distinguishing_features(results, winner_metrics):
    """Finde Merkmale die den Gewinner von anderen unterscheiden."""

    print()
    print("=" * 80)
    print("ANALYSE: Was unterscheidet die Gewinner-Kombination?")
    print("=" * 80)
    print()

    winner = winner_metrics
    others = [r for r in results if not r['is_winner']]

    # Metriken zum Vergleichen
    metrics_to_compare = [
        ('sum', 'Summe'),
        ('mean', 'Mittelwert'),
        ('std', 'Standardabweichung'),
        ('range', 'Spannweite'),
        ('avg_gap', 'Durchschn. Abstand'),
        ('max_gap', 'Max. Abstand'),
        ('min_gap', 'Min. Abstand'),
        ('decades_used', 'Zehnergruppen genutzt'),
        ('max_per_decade', 'Max. pro Zehnergruppe'),
        ('odd_count', 'Ungerade Zahlen'),
        ('even_count', 'Gerade Zahlen'),
        ('prime_count', 'Primzahlen'),
        ('consecutive_pairs', 'Aufeinanderfolgende Paare'),
        ('avg_hits', 'Durchschn. hist. Treffer'),
        ('max_hits', 'Max. hist. Treffer'),
        ('hits_6plus', 'Tage mit 6+ Treffern'),
        ('hits_7plus', 'Tage mit 7+ Treffern'),
        ('hits_8plus', 'Tage mit 8+ Treffern'),
        ('historical_freq', 'Historische 10/10'),
    ]

    print(f"Gewinner-Kombination: {winner['combo']}")
    print()
    print(f"{'Metrik':<30} {'Gewinner':>12} {'Andere (Avg)':>12} {'Andere (Min)':>12} {'Andere (Max)':>12} {'Percentile':>12}")
    print("-" * 90)

    distinguishing = []

    for metric_key, metric_name in metrics_to_compare:
        winner_val = winner[metric_key]
        other_vals = [r[metric_key] for r in others]

        if not other_vals:
            continue

        avg_other = np.mean(other_vals)
        min_other = min(other_vals)
        max_other = max(other_vals)

        # Berechne Percentile des Gewinners
        percentile = sum(1 for v in other_vals if v <= winner_val) / len(other_vals) * 100

        # Markiere extreme Werte
        marker = ""
        if percentile <= 5 or percentile >= 95:
            marker = " ***"
            distinguishing.append({
                'metric': metric_name,
                'winner_val': winner_val,
                'avg_other': avg_other,
                'percentile': percentile
            })
        elif percentile <= 10 or percentile >= 90:
            marker = " **"
        elif percentile <= 20 or percentile >= 80:
            marker = " *"

        print(f"{metric_name:<30} {winner_val:>12.2f} {avg_other:>12.2f} {min_other:>12.2f} {max_other:>12.2f} {percentile:>11.1f}%{marker}")

    print()
    print("Legende: *** = Top/Bottom 5%, ** = Top/Bottom 10%, * = Top/Bottom 20%")
    print()

    # Zusammenfassung der unterscheidenden Merkmale
    if distinguishing:
        print("=" * 80)
        print("STARK UNTERSCHEIDENDE MERKMALE (Top/Bottom 5%)")
        print("=" * 80)
        for d in distinguishing:
            direction = "HOCH" if d['percentile'] >= 95 else "NIEDRIG"
            print(f"  - {d['metric']}: {d['winner_val']:.2f} ({direction}, Percentile: {d['percentile']:.1f}%)")
    else:
        print("Keine stark unterscheidenden Merkmale gefunden (alle im Normalbereich)")

    return distinguishing


def analyze_number_selection(drawn_20, winner_10):
    """Analysiere welche Zahlen gewählt/nicht gewählt wurden."""

    winner_set = set(winner_10)
    not_chosen = [n for n in drawn_20 if n not in winner_set]

    print()
    print("=" * 80)
    print("ZAHLEN-AUSWAHL ANALYSE")
    print("=" * 80)
    print()
    print(f"20 Gezogene:      {sorted(drawn_20)}")
    print(f"10 Gewählt:       {sorted(winner_10)}")
    print(f"10 NICHT gewählt: {sorted(not_chosen)}")
    print()

    # Vergleiche Eigenschaften
    print(f"{'Eigenschaft':<25} {'Gewählt':>15} {'Nicht gewählt':>15}")
    print("-" * 60)

    comparisons = [
        ('Summe', sum(winner_10), sum(not_chosen)),
        ('Mittelwert', np.mean(winner_10), np.mean(not_chosen)),
        ('Min', min(winner_10), min(not_chosen)),
        ('Max', max(winner_10), max(not_chosen)),
        ('Spannweite', max(winner_10)-min(winner_10), max(not_chosen)-min(not_chosen)),
    ]

    # Zehnergruppen
    chosen_decades = [(n-1)//10 for n in winner_10]
    not_chosen_decades = [(n-1)//10 for n in not_chosen]

    for dec in range(7):
        name = f"Zehner {dec*10+1}-{dec*10+10}"
        chosen_count = sum(1 for d in chosen_decades if d == dec)
        not_count = sum(1 for d in not_chosen_decades if d == dec)
        comparisons.append((name, chosen_count, not_count))

    # Gerade/Ungerade
    chosen_odd = sum(1 for n in winner_10 if n % 2 == 1)
    not_chosen_odd = sum(1 for n in not_chosen if n % 2 == 1)
    comparisons.append(('Ungerade', chosen_odd, not_chosen_odd))
    comparisons.append(('Gerade', 10 - chosen_odd, 10 - not_chosen_odd))

    for name, chosen_val, not_val in comparisons:
        print(f"{name:<25} {chosen_val:>15} {not_val:>15}")

    return not_chosen


def main():
    print("=" * 80)
    print("KENO JACKPOT-AUSWAHL ANALYSE")
    print("Reverse-Engineering: Wie wählt das System die Gewinner-Zahlen?")
    print("=" * 80)
    print()

    print("Lade historische Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print()

    # Zahlen-Auswahl Analyse
    not_chosen = analyze_number_selection(KYRITZ_DRAWN_20, KYRITZ_WINNER_10)

    print()
    print("Starte Kombinations-Analyse...")
    print("(Dies kann einige Minuten dauern...)")
    print()

    # Analysiere alle Kombinationen (oder Sample für Schnelligkeit)
    # Für vollständige Analyse: sample_size=None
    # Für schnellen Test: sample_size=10000
    results, winner_metrics = analyze_all_combinations(
        KYRITZ_DRAWN_20,
        KYRITZ_WINNER_10,
        df,
        KYRITZ_DATE,
        sample_size=20000  # Erst mal 20k für schnellen Test
    )

    # Finde unterscheidende Merkmale
    distinguishing = find_distinguishing_features(results, winner_metrics)

    # Speichere Ergebnisse
    output = {
        'date': KYRITZ_DATE,
        'drawn_20': KYRITZ_DRAWN_20,
        'winner_10': KYRITZ_WINNER_10,
        'not_chosen': not_chosen,
        'winner_metrics': {k: v for k, v in winner_metrics.items() if k != 'historical_hits'},
        'distinguishing_features': distinguishing,
        'sample_size': len(results)
    }

    output_file = BASE_DIR / "results" / "kyritz_selection_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print()
    print(f"Ergebnisse gespeichert: {output_file}")

    print()
    print("=" * 80)
    print("FAZIT")
    print("=" * 80)
    print()
    print("Die Gewinner-Kombination wurde mit folgenden Kriterien analysiert:")
    print("  - Statistische Eigenschaften (Summe, Mittelwert, Streuung)")
    print("  - Verteilung (Zehnergruppen, Gerade/Ungerade, Primzahlen)")
    print("  - Muster (Abstände, aufeinanderfolgende Zahlen)")
    print("  - Historische Performance (Treffer in vergangenen Ziehungen)")
    print()
    if distinguishing:
        print("GEFUNDENE UNTERSCHEIDUNGSMERKMALE:")
        for d in distinguishing:
            print(f"  → {d['metric']}")
    else:
        print("Keine stark unterscheidenden Merkmale gefunden.")
        print("Dies könnte bedeuten:")
        print("  a) Die Auswahl folgt anderen, noch nicht getesteten Kriterien")
        print("  b) Das System wählt basierend auf Spieler-Tippscheinen")
        print("  c) Die Stichprobe ist zu klein")


if __name__ == "__main__":
    main()
