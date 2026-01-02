#!/usr/bin/env python
"""
Hot-Zahlen Vorhersage V2 - Verbesserte Methodik

Kombiniert:
1. Aktuelle Hot-Zone Position
2. Historische Erfolgsrate WENN in Hot-Zone
3. Abkühlungs-Fenster (wann war die Zahl zuletzt "hot")
4. Trend: Steigt oder fällt der Rang?
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
    return {n: freq.get(n, 0) for n in range(1, 71)}


def get_hot_zone(df, end_date, window, top_n=7):
    """Top-N häufigste Zahlen."""
    freq = get_frequency_ranking(df, end_date, window)
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:top_n]]


def find_jackpots_for_number(df, number, start_date, end_date):
    """Findet alle Jackpots wo eine bestimmte Zahl beteiligt war."""
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]
    jackpots = []
    for _, row in test_df.iterrows():
        if number in row['zahlen']:
            jackpots.append(row['datum'])
    return jackpots


def analyze_number_history(df, window=50):
    """
    Analysiert für jede Zahl ihre komplette Historie:
    - Wann war sie in der Hot-Zone?
    - Wie oft führte das zu Jackpots?
    - Trend: Steigt oder fällt ihr Rang?
    """
    # Alle Monate analysieren
    test_dates = pd.date_range(start='2022-06-01', end=LAST_DRAW, freq='MS')

    number_history = defaultdict(lambda: {
        'hz_appearances': [],       # Datum wenn in Hot-Zone
        'jackpot_hits': [],         # Datum wenn bei Jackpot gezogen
        'rank_history': [],         # (Datum, Rang) für Trend
        'success_when_hot': 0,      # Jackpots innerhalb 120 Tage nach Hot-Zone
        'total_hot_periods': 0
    })

    for test_date in test_dates:
        hz = get_hot_zone(df, test_date, window, top_n=7)
        freq = get_frequency_ranking(df, test_date, window)
        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        ranks = {n: i+1 for i, (n, _) in enumerate(sorted_nums)}

        for num in range(1, 71):
            number_history[num]['rank_history'].append((test_date, ranks.get(num, 70)))

        for num in hz:
            number_history[num]['hz_appearances'].append(test_date)
            number_history[num]['total_hot_periods'] += 1

            # Prüfe ob innerhalb 120 Tage ein Jackpot mit dieser Zahl kam
            end_check = min(test_date + timedelta(days=120), LAST_DRAW)
            hits = find_jackpots_for_number(df, num, test_date, end_check)
            if hits:
                number_history[num]['success_when_hot'] += 1
                number_history[num]['jackpot_hits'].extend(hits)

    return dict(number_history)


def calculate_trend(rank_history, lookback=6):
    """Berechnet Trend: negativ = Rang verbessert sich (wird kleiner)."""
    if len(rank_history) < lookback:
        return 0

    recent = [r for _, r in rank_history[-lookback:]]
    older = [r for _, r in rank_history[-lookback*2:-lookback]]

    if not older:
        return 0

    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)

    # Negativer Wert = Rang wurde besser (kleiner)
    return recent_avg - older_avg


def main():
    print("=" * 80)
    print("HOT-ZAHLEN VORHERSAGE V2 - Verbesserte Methodik")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print(f"Analyse-Datum: {TODAY.strftime('%d.%m.%Y')}")
    print()

    # Historische Analyse
    print("Analysiere Zahlen-Historie (kann einige Sekunden dauern)...")
    number_history = analyze_number_history(df, window=50)

    # Aktuelle Daten
    current_freq = get_frequency_ranking(df, LAST_DRAW, 50)
    sorted_nums = sorted(current_freq.items(), key=lambda x: -x[1])
    current_ranks = {n: i+1 for i, (n, _) in enumerate(sorted_nums)}

    current_hz_w50 = get_hot_zone(df, LAST_DRAW, 50, 7)
    current_hz_w20 = get_hot_zone(df, LAST_DRAW, 20, 7)

    # Scores berechnen
    scores = {}

    for num in range(1, 71):
        hist = number_history[num]
        rank = current_ranks.get(num, 70)

        # 1. Aktueller Rang Score
        if rank <= 7:
            rank_score = 1.0 - (rank - 1) * 0.05
        elif rank <= 14:
            rank_score = 0.6
        elif rank <= 21:
            rank_score = 0.5
        elif rank <= 35:
            rank_score = 0.4  # Rang 29-35 hat kürzeren Median!
        else:
            rank_score = 0.2

        # 2. Historische Erfolgsrate wenn HOT
        if hist['total_hot_periods'] > 0:
            success_rate = hist['success_when_hot'] / hist['total_hot_periods']
        else:
            success_rate = 0

        # 3. Trend Score (negativer Trend = besser, Rang verbessert sich)
        trend = calculate_trend(hist['rank_history'])
        if trend < -5:
            trend_score = 1.0  # Stark aufsteigend
        elif trend < -2:
            trend_score = 0.8
        elif trend < 0:
            trend_score = 0.6
        elif trend < 2:
            trend_score = 0.4
        else:
            trend_score = 0.2  # Absteigend

        # 4. Recency Score - Wie lange seit letztem Jackpot-Hit?
        recency_score = 0.3
        if hist['jackpot_hits']:
            last_hit = max(hist['jackpot_hits'])
            days_since = (LAST_DRAW - last_hit).days
            if days_since < 30:
                recency_score = 0.3  # Zu kürzlich
            elif days_since < 60:
                recency_score = 0.7
            elif days_since < 120:
                recency_score = 1.0  # Optimal
            elif days_since < 200:
                recency_score = 0.8
            else:
                recency_score = 0.5

        # 5. Hot-Zone Stabilität (oft in Hot-Zone = stabil)
        stability = min(hist['total_hot_periods'] / 20, 1.0)

        # Gesamtscore
        total_score = (
            rank_score * 0.30 +       # Aktueller Rang wichtig
            success_rate * 0.25 +     # Historische Erfolge
            trend_score * 0.20 +      # Aufsteigender Trend
            recency_score * 0.15 +    # Nicht zu kürzlich getroffen
            stability * 0.10          # Stabile Hot-Zone Präsenz
        )

        scores[num] = {
            'total_score': total_score,
            'rank': rank,
            'rank_score': rank_score,
            'success_rate': success_rate,
            'trend': trend,
            'trend_score': trend_score,
            'recency_score': recency_score,
            'stability': stability,
            'hot_periods': hist['total_hot_periods'],
            'in_hz_w50': num in current_hz_w50,
            'in_hz_w20': num in current_hz_w20,
            'freq': current_freq.get(num, 0)
        }

    # Sortieren
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1]['total_score'])

    # =========================================================================
    # AKTUELLE HOT-ZONES
    # =========================================================================
    print()
    print("=" * 80)
    print("AKTUELLE HOT-ZONES")
    print("=" * 80)
    print()
    print(f"Hot-Zone W50 (Top 7 aus 50 Ziehungen): {sorted(current_hz_w50)}")
    print(f"Hot-Zone W20 (Top 7 aus 20 Ziehungen): {sorted(current_hz_w20)}")

    # =========================================================================
    # TOP 7 AUS AKTUELLER HOT-ZONE (MIT SCORES)
    # =========================================================================
    print()
    print("=" * 80)
    print("ANALYSE DER AKTUELLEN HOT-ZONE W50")
    print("=" * 80)
    print()

    hz_scores = [(num, scores[num]) for num in current_hz_w50]
    hz_scores.sort(key=lambda x: -x[1]['total_score'])

    print(f"{'Zahl':>6} {'Score':>8} {'Rang':>6} {'Erfolg%':>9} {'Trend':>8} {'Hot-Per':>10}")
    print("-" * 60)

    for num, s in hz_scores:
        trend_dir = "↑" if s['trend'] < 0 else "↓" if s['trend'] > 0 else "→"
        print(f"{num:>6} {s['total_score']:>8.3f} {s['rank']:>6} "
              f"{s['success_rate']*100:>8.1f}% {trend_dir}{abs(s['trend']):>6.1f} {s['hot_periods']:>10}")

    # =========================================================================
    # EMPFEHLUNG: BESTE ZAHLEN AUS HOT-ZONE
    # =========================================================================
    print()
    print("=" * 80)
    print("EMPFEHLUNG: Beste 7 Zahlen (Hot-Zone + Score)")
    print("=" * 80)
    print()

    # Kombiniere: Top aus W50 und Top aus W20, gewichtet nach Score
    combined_candidates = set(current_hz_w50) | set(current_hz_w20)
    candidate_scores = [(num, scores[num]) for num in combined_candidates]
    candidate_scores.sort(key=lambda x: -x[1]['total_score'])

    best7 = [num for num, _ in candidate_scores[:7]]
    print(f"Empfohlene Zahlen: {sorted(best7)}")
    print()

    print("Detail:")
    for num, s in candidate_scores[:7]:
        trend_dir = "↑" if s['trend'] < 0 else "↓"
        w50 = "W50" if s['in_hz_w50'] else "   "
        w20 = "W20" if s['in_hz_w20'] else "   "
        print(f"  {num:>2}: Score={s['total_score']:.3f}, Rang={s['rank']:>2}, "
              f"Erfolg={s['success_rate']*100:.0f}%, Trend={trend_dir}, [{w50}] [{w20}]")

    # =========================================================================
    # AUFSTEIGENDE ZAHLEN (POTENZIAL)
    # =========================================================================
    print()
    print("=" * 80)
    print("AUFSTEIGENDE ZAHLEN (Rang verbessert sich)")
    print("=" * 80)
    print()

    rising = [(num, s) for num, s in scores.items() if s['trend'] < -3 and s['rank'] <= 20]
    rising.sort(key=lambda x: x[1]['trend'])

    if rising:
        print("Diese Zahlen steigen im Rang und könnten bald in die Hot-Zone kommen:")
        for num, s in rising[:10]:
            in_hz = "★" if s['in_hz_w50'] else " "
            print(f"  {in_hz} {num:>2}: Rang={s['rank']:>2}, Trend={s['trend']:>+.1f}, Erfolg={s['success_rate']*100:.0f}%")
    else:
        print("Keine stark aufsteigenden Zahlen gefunden.")

    # =========================================================================
    # 7 KOMBINATIONEN
    # =========================================================================
    print()
    print("=" * 80)
    print("7 KOMBINATIONEN FÜR TYP-6 SPIEL")
    print("=" * 80)
    print()

    for i, exclude in enumerate(sorted(best7), 1):
        combo = sorted([n for n in best7 if n != exclude])
        print(f"Kombi {i}: {combo}")

    print()
    print("Einsatz: 7 x 1 EUR = 7 EUR")

    # =========================================================================
    # FINALE EMPFEHLUNG
    # =========================================================================
    print()
    print("=" * 80)
    print("FINALE EMPFEHLUNG")
    print("=" * 80)
    print()

    # Durchschnittlicher Score der empfohlenen Zahlen
    avg_score = sum(scores[n]['total_score'] for n in best7) / 7
    avg_success = sum(scores[n]['success_rate'] for n in best7) / 7

    print(f"Empfohlene Zahlen:     {sorted(best7)}")
    print(f"Durchschnittlicher Score: {avg_score:.3f}")
    print(f"Durchschnittl. Erfolg:    {avg_success*100:.1f}%")
    print()

    # Vergleich mit reiner Hot-Zone
    hz_avg_score = sum(scores[n]['total_score'] for n in current_hz_w50) / 7
    hz_avg_success = sum(scores[n]['success_rate'] for n in current_hz_w50) / 7

    print(f"Hot-Zone W50:          {sorted(current_hz_w50)}")
    print(f"Durchschnittlicher Score: {hz_avg_score:.3f}")
    print(f"Durchschnittl. Erfolg:    {hz_avg_success*100:.1f}%")

    if avg_score > hz_avg_score:
        print()
        print(f"→ Empfehlung ist {(avg_score/hz_avg_score - 1)*100:.1f}% besser als reine Hot-Zone!")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Hot-Zahlen Vorhersage V2

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {LAST_DRAW.strftime('%d.%m.%Y')}

---

## Aktuelle Hot-Zones

| Fenster | Zahlen |
|---------|--------|
| W50 (50 Ziehungen) | {sorted(current_hz_w50)} |
| W20 (20 Ziehungen) | {sorted(current_hz_w20)} |

---

## Empfohlene 7 Zahlen

### **{sorted(best7)}**

| Zahl | Score | Rang | Erfolg% | Trend | W50 | W20 |
|------|-------|------|---------|-------|-----|-----|
"""

    for num, s in candidate_scores[:7]:
        trend_dir = "↑" if s['trend'] < 0 else "↓"
        w50 = "✓" if s['in_hz_w50'] else ""
        w20 = "✓" if s['in_hz_w20'] else ""
        md += f"| {num} | {s['total_score']:.3f} | {s['rank']} | {s['success_rate']*100:.0f}% | {trend_dir} | {w50} | {w20} |\n"

    md += f"""

---

## 7 Kombinationen für Typ-6

| # | Kombination |
|---|-------------|
"""

    for i, exclude in enumerate(sorted(best7), 1):
        combo = sorted([n for n in best7 if n != exclude])
        md += f"| {i} | {combo} |\n"

    md += f"""

**Einsatz:** 7 EUR

---

## Vergleich: Empfehlung vs. Hot-Zone

| Methode | Score | Erfolg% |
|---------|-------|---------|
| **Empfehlung** | {avg_score:.3f} | {avg_success*100:.1f}% |
| Hot-Zone W50 | {hz_avg_score:.3f} | {hz_avg_success*100:.1f}% |

**Verbesserung:** {(avg_score/hz_avg_score - 1)*100:+.1f}%

---

## Scoring-Methodik V2

| Faktor | Gewicht | Beschreibung |
|--------|---------|--------------|
| Rang-Score | 30% | Aktueller Rang in Hot-Zone |
| Erfolgsrate | 25% | Jackpot-Rate wenn in Hot-Zone |
| Trend | 20% | Aufsteigend = besser |
| Recency | 15% | 60-120 Tage seit letztem Hit optimal |
| Stabilität | 10% | Häufigkeit in Hot-Zone |

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "hot_zahlen_vorhersage_v2.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
