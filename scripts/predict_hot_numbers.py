#!/usr/bin/env python
"""
Ermittelt welche Hot-Zahlen aktuell die höchste Trefferwahrscheinlichkeit haben.
Basiert auf historischen Hot-Zone Analysen und der Abkühlungs-Theorie.
"""

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime, timedelta
import statistics

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)

TODAY = datetime.now()
LAST_DRAW = df['datum'].max()


def get_frequency_ranking(df, end_date, window):
    """Berechnet Frequenz-Ranking für alle 70 Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    # Alle 70 Zahlen mit ihrer Frequenz
    return {n: freq.get(n, 0) for n in range(1, 71)}


def get_hot_zone(df, end_date, window, top_n=7):
    """Top-N häufigste Zahlen."""
    freq = get_frequency_ranking(df, end_date, window)
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:top_n]]


def find_jackpots(df, numbers, start_date, end_date):
    """Findet Typ-6 Jackpots für eine Zahlenmenge."""
    numbers = sorted(numbers)[:7]
    if len(numbers) < 6:
        return []

    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append({
                    'datum': row['datum'],
                    'gruppe': tuple(sorted(group)),
                    'gezogen': tuple(sorted(drawn))
                })
    return jackpots


def analyze_number_success_rate(df, window=50):
    """
    Analysiert für jede Zahl: Wie oft war sie in einer Hot-Zone
    und wie oft führte das zu einem Jackpot innerhalb von 48-120 Tagen.
    """
    # Test-Monate generieren
    months = []
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            if month == 1:
                end_date = f'{year-1}-12-31'
            else:
                last_day = (pd.Timestamp(f'{year}-{month:02d}-01') - timedelta(days=1)).strftime('%Y-%m-%d')
                end_date = last_day
            months.append({
                'end_date': pd.Timestamp(end_date),
                'start_test': pd.Timestamp(f'{year}-{month:02d}-01')
            })

    min_date = df['datum'].min() + timedelta(days=100)
    months = [m for m in months if m['end_date'] >= min_date]

    # Tracking pro Zahl
    number_stats = defaultdict(lambda: {
        'hz_count': 0,           # Wie oft in Hot-Zone
        'jp_count': 0,           # Wie oft zu Jackpot geführt
        'jp_within_optimal': 0,  # Jackpots im optimalen Fenster (48-120 Tage)
        'avg_gap': [],           # Durchschnittlicher Abstand zum Jackpot
        'last_hz_date': None,    # Letztes Mal in Hot-Zone
        'current_rank': 0        # Aktueller Rang
    })

    for m in months:
        hz = get_hot_zone(df, m['end_date'], window, top_n=7)

        # Optimal window: 48-120 Tage nach Ermittlung
        optimal_start = m['start_test'] + timedelta(days=48)
        optimal_end = m['start_test'] + timedelta(days=120)
        optimal_end = min(optimal_end, pd.Timestamp('2025-12-31'))

        jackpots = find_jackpots(df, hz, m['start_test'], pd.Timestamp('2025-12-31'))
        jackpots_optimal = find_jackpots(df, hz, optimal_start, optimal_end)

        for num in hz:
            number_stats[num]['hz_count'] += 1
            number_stats[num]['last_hz_date'] = m['end_date']

        # Welche Zahlen waren bei Jackpots dabei?
        for jp in jackpots:
            gap = (jp['datum'] - m['end_date']).days
            for num in jp['gruppe']:
                if num in hz:
                    number_stats[num]['jp_count'] += 1
                    number_stats[num]['avg_gap'].append(gap)

        for jp in jackpots_optimal:
            for num in jp['gruppe']:
                if num in hz:
                    number_stats[num]['jp_within_optimal'] += 1

    return dict(number_stats)


def calculate_current_scores(df, number_stats):
    """
    Berechnet einen Score für jede Zahl basierend auf:
    1. Aktuellem Rang (Hot-Zone Position)
    2. Historischer Erfolgsrate
    3. Zeit seit letzter Hot-Zone Zugehörigkeit (Abkühlung)
    4. Median-Abstand zum Jackpot
    """
    scores = {}

    # Aktuelles Frequenz-Ranking
    current_freq = get_frequency_ranking(df, LAST_DRAW, 50)
    sorted_nums = sorted(current_freq.items(), key=lambda x: -x[1])
    current_ranks = {n: i+1 for i, (n, _) in enumerate(sorted_nums)}

    for num in range(1, 71):
        stats = number_stats.get(num, {
            'hz_count': 0, 'jp_count': 0, 'jp_within_optimal': 0,
            'avg_gap': [], 'last_hz_date': None
        })

        # 1. Rang-Score (Top-7 = beste, dann abnehmend)
        rank = current_ranks.get(num, 70)
        if rank <= 7:
            rank_score = 1.0 - (rank - 1) * 0.1  # 1.0 bis 0.4
        elif rank <= 14:
            rank_score = 0.3
        elif rank <= 35:
            rank_score = 0.2  # Rang 29-35 hat kürzeren Median!
        else:
            rank_score = 0.1

        # 2. Historische Erfolgsrate
        if stats['hz_count'] > 0:
            success_rate = stats['jp_count'] / stats['hz_count']
            optimal_rate = stats['jp_within_optimal'] / stats['hz_count']
        else:
            success_rate = 0
            optimal_rate = 0

        # 3. Abkühlungs-Score
        cooling_score = 0
        if stats['last_hz_date']:
            days_since_hz = (LAST_DRAW - stats['last_hz_date']).days
            # Optimal: 48-60 Tage seit Hot-Zone
            if 48 <= days_since_hz <= 60:
                cooling_score = 1.0
            elif 30 <= days_since_hz < 48:
                cooling_score = 0.5
            elif 60 < days_since_hz <= 120:
                cooling_score = 0.7
            elif days_since_hz < 30:
                cooling_score = 0.3  # Noch zu "heiß"
            else:
                cooling_score = 0.4  # Zu lange her

        # 4. Median-Gap Score (kürzerer Gap = besser)
        gap_score = 0
        if stats['avg_gap']:
            median_gap = statistics.median(stats['avg_gap'])
            if median_gap < 60:
                gap_score = 1.0
            elif median_gap < 120:
                gap_score = 0.8
            elif median_gap < 200:
                gap_score = 0.6
            elif median_gap < 300:
                gap_score = 0.4
            else:
                gap_score = 0.2

        # Gesamtscore (gewichtet)
        total_score = (
            rank_score * 0.25 +
            success_rate * 0.30 +
            cooling_score * 0.25 +
            gap_score * 0.20
        )

        scores[num] = {
            'total_score': total_score,
            'rank': rank,
            'rank_score': rank_score,
            'success_rate': success_rate,
            'optimal_rate': optimal_rate,
            'cooling_score': cooling_score,
            'gap_score': gap_score,
            'hz_count': stats['hz_count'],
            'jp_count': stats['jp_count'],
            'median_gap': statistics.median(stats['avg_gap']) if stats['avg_gap'] else None,
            'last_hz_date': stats['last_hz_date'],
            'current_freq': current_freq.get(num, 0)
        }

    return scores


def main():
    print("=" * 80)
    print("HOT-ZAHLEN VORHERSAGE - Welche Zahlen haben die höchste Trefferwahrscheinlichkeit?")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print(f"Analyse-Datum: {TODAY.strftime('%d.%m.%Y')}")
    print()

    # Historische Analyse
    print("Analysiere historische Hot-Zone Performance...")
    number_stats = analyze_number_success_rate(df, window=50)

    # Aktuelle Scores berechnen
    print("Berechne aktuelle Scores...")
    scores = calculate_current_scores(df, number_stats)

    # Sortieren nach Score
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1]['total_score'])

    # =========================================================================
    # TOP 20 ZAHLEN
    # =========================================================================
    print()
    print("=" * 80)
    print("TOP 20 ZAHLEN MIT HÖCHSTER TREFFERWAHRSCHEINLICHKEIT")
    print("=" * 80)
    print()
    print(f"{'#':>3} {'Zahl':>6} {'Score':>8} {'Rang':>6} {'Erfolg%':>9} {'Optimal%':>10} {'Abkühl':>8} {'Median':>8}")
    print("-" * 80)

    for i, (num, s) in enumerate(sorted_scores[:20], 1):
        median_str = f"{s['median_gap']:.0f}d" if s['median_gap'] else "N/A"
        print(f"{i:>3} {num:>6} {s['total_score']:>8.3f} {s['rank']:>6} "
              f"{s['success_rate']*100:>8.1f}% {s['optimal_rate']*100:>9.1f}% "
              f"{s['cooling_score']:>8.2f} {median_str:>8}")

    # =========================================================================
    # EMPFOHLENE 7 ZAHLEN
    # =========================================================================
    print()
    print("=" * 80)
    print("EMPFOHLENE 7 ZAHLEN (Optimale Kombination)")
    print("=" * 80)
    print()

    # Top 7 nach Score
    top7 = [num for num, _ in sorted_scores[:7]]
    print(f"Zahlen: {sorted(top7)}")
    print()

    # Detail zu jeder Zahl
    print("Detail:")
    for num, s in sorted_scores[:7]:
        days_since = (LAST_DRAW - s['last_hz_date']).days if s['last_hz_date'] else "N/A"
        print(f"  {num:>2}: Score={s['total_score']:.3f}, Rang={s['rank']}, "
              f"Erfolg={s['success_rate']*100:.1f}%, Abstand={days_since}d")

    # =========================================================================
    # AKTUELLE HOT-ZONE VS EMPFEHLUNG
    # =========================================================================
    print()
    print("=" * 80)
    print("VERGLEICH: Aktuelle Hot-Zone vs. Empfehlung")
    print("=" * 80)
    print()

    current_hz = get_hot_zone(df, LAST_DRAW, 50, 7)
    print(f"Aktuelle Hot-Zone (W50):  {sorted(current_hz)}")
    print(f"Score-basierte Empfehlung: {sorted(top7)}")
    print()

    overlap = set(current_hz) & set(top7)
    print(f"Überschneidung: {len(overlap)} Zahlen - {sorted(overlap)}")
    print(f"Nur in Hot-Zone: {sorted(set(current_hz) - set(top7))}")
    print(f"Nur in Empfehlung: {sorted(set(top7) - set(current_hz))}")

    # =========================================================================
    # ALTERNATIVE: "ABGEKÜHLTE" ZAHLEN
    # =========================================================================
    print()
    print("=" * 80)
    print("ALTERNATIVE: Zahlen im optimalen Abkühlungs-Fenster (48-60 Tage)")
    print("=" * 80)
    print()

    cooled_nums = []
    for num, s in scores.items():
        if s['last_hz_date']:
            days_since = (LAST_DRAW - s['last_hz_date']).days
            if 48 <= days_since <= 60:
                cooled_nums.append((num, s, days_since))

    cooled_nums.sort(key=lambda x: -x[1]['total_score'])

    if cooled_nums:
        print(f"Gefunden: {len(cooled_nums)} Zahlen im optimalen Fenster")
        print()
        for num, s, days in cooled_nums[:10]:
            print(f"  {num:>2}: Score={s['total_score']:.3f}, {days} Tage seit Hot-Zone, "
                  f"Erfolg={s['success_rate']*100:.1f}%")
    else:
        print("Keine Zahlen im optimalen Abkühlungs-Fenster gefunden.")

    # =========================================================================
    # 7 KOMBINATIONEN
    # =========================================================================
    print()
    print("=" * 80)
    print("7 KOMBINATIONEN FÜR TYP-6 SPIEL")
    print("=" * 80)
    print()

    for i, exclude in enumerate(sorted(top7), 1):
        combo = sorted([n for n in top7 if n != exclude])
        print(f"Kombi {i}: {combo}")

    print()
    print("Einsatz: 7 x 1 EUR = 7 EUR")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Hot-Zahlen Vorhersage

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {LAST_DRAW.strftime('%d.%m.%Y')}

---

## Top 20 Zahlen mit höchster Trefferwahrscheinlichkeit

| # | Zahl | Score | Rang | Erfolg% | Optimal% | Abkühl-Score | Median-Gap |
|---|------|-------|------|---------|----------|--------------|------------|
"""

    for i, (num, s) in enumerate(sorted_scores[:20], 1):
        median_str = f"{s['median_gap']:.0f}d" if s['median_gap'] else "N/A"
        md += f"| {i} | {num} | {s['total_score']:.3f} | {s['rank']} | {s['success_rate']*100:.1f}% | {s['optimal_rate']*100:.1f}% | {s['cooling_score']:.2f} | {median_str} |\n"

    md += f"""

---

## Empfohlene 7 Zahlen

**{sorted(top7)}**

| Zahl | Score | Rang | Erfolgsrate | Tage seit HZ |
|------|-------|------|-------------|--------------|
"""

    for num, s in sorted_scores[:7]:
        days_since = (LAST_DRAW - s['last_hz_date']).days if s['last_hz_date'] else "N/A"
        md += f"| {num} | {s['total_score']:.3f} | {s['rank']} | {s['success_rate']*100:.1f}% | {days_since} |\n"

    md += f"""

---

## Vergleich: Hot-Zone vs. Empfehlung

| Methode | Zahlen |
|---------|--------|
| Aktuelle Hot-Zone (W50) | {sorted(current_hz)} |
| Score-basierte Empfehlung | {sorted(top7)} |
| Überschneidung | {sorted(overlap)} |

---

## 7 Kombinationen für Typ-6

| # | Kombination |
|---|-------------|
"""

    for i, exclude in enumerate(sorted(top7), 1):
        combo = sorted([n for n in top7 if n != exclude])
        md += f"| {i} | {combo} |\n"

    md += f"""

**Einsatz:** 7 EUR

---

## Scoring-Methodik

Der Score setzt sich zusammen aus:

1. **Rang-Score (25%):** Position in aktueller Hot-Zone
2. **Erfolgsrate (30%):** Historische Jackpot-Rate wenn in Hot-Zone
3. **Abkühlungs-Score (25%):** Optimale Zeit seit letzter Hot-Zone (48-60 Tage)
4. **Gap-Score (20%):** Median-Abstand bis Jackpot (kürzer = besser)

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "hot_zahlen_vorhersage.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
