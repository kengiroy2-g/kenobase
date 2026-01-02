#!/usr/bin/env python
"""
Kombiniert Loop-Erkenntnisse mit Hot-Zone Strategie

Loop-Erkenntnisse:
- HYP_CYC_001: FRÜH-Phase (Tag 1-14) = +364% ROI vs SPÄT -58%
- WL-003: 30 Tage Cooldown nach 10/10 Jackpot = -66% ROI
- Kern-Zahlen: 3, 9, 24, 49, 51, 64

HZ-Strategie (neu):
- HZ7: 48-60 Tage Wartezeit optimal
- HZ6: 0 Tage Wartezeit (sofort spielen)
- Auszahlungs-Korrelation: r=0.927
- Reife Hot-Zones: 1 JP + 2. erwartet

Ziel: Kombinierte Strategie mit Walk-Forward Backtest
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations
from datetime import datetime, timedelta
import statistics
import json

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
GQ_FILE_1 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
GQ_FILE_2 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)

TODAY = datetime.now()
LAST_DRAW = df['datum'].max()

# Loop Kern-Zahlen
LOOP_KERN = [3, 9, 24, 49, 51, 64]
LOOP_ERWEITERT = [2, 3, 9, 10, 20, 24, 33, 36, 49, 50, 51, 64]


def load_gq_data():
    """Laedt Gewinnquoten-Daten für Jackpot-Erkennung."""
    dfs = []
    for f in [GQ_FILE_1, GQ_FILE_2]:
        if f.exists():
            gq = pd.read_csv(f, sep=',', encoding='utf-8-sig')
            dfs.append(gq)
    if not dfs:
        return None
    gq_df = pd.concat(dfs, ignore_index=True)
    gq_df['datum'] = pd.to_datetime(gq_df['Datum'], format='%d.%m.%Y', errors='coerce')
    gq_df = gq_df.rename(columns={
        'Keno-Typ': 'Typ',
        'Anzahl richtiger Zahlen': 'GK',
        'Anzahl der Gewinner': 'Gewinner'
    })
    gq_df['Gewinner'] = pd.to_numeric(gq_df['Gewinner'], errors='coerce').fillna(0)
    return gq_df


def get_hot_zone(df, end_date, window, top_n):
    """Top-N häufigste Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(top_n)]


def find_jackpots_10_10(gq_df, start_date, end_date):
    """Findet 10/10 Jackpots im Zeitraum."""
    if gq_df is None:
        return []
    jp = gq_df[(gq_df['Typ'] == 10) & (gq_df['GK'] == 10) & (gq_df['Gewinner'] > 0)]
    jp = jp[(jp['datum'] >= start_date) & (jp['datum'] <= end_date)]
    return jp['datum'].tolist()


def get_cycle_phase(date):
    """Berechnet Zyklus-Phase (FRÜH = Tag 1-14, SPÄT = Tag 15-28)."""
    day = date.day
    return "FRÜH" if day <= 14 else "SPÄT"


def is_in_cooldown(date, jackpot_dates, cooldown_days=30):
    """Prüft ob Datum im Cooldown-Zeitraum ist."""
    for jp_date in jackpot_dates:
        if 0 < (date - jp_date).days <= cooldown_days:
            return True
    return False


def find_typ6_jackpots(df, numbers, start_date, end_date):
    """Findet Typ-6 Jackpots für eine Zahlenmenge."""
    numbers = sorted(numbers)[:7] if len(numbers) >= 7 else sorted(numbers)
    if len(numbers) < 6:
        return []

    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append(row['datum'])
                break
    return jackpots


def backtest_combined_strategy(df, gq_df, strategy_name, get_numbers_func,
                                use_frueh_phase=True, use_cooldown=True,
                                hz_delay=0, window=50):
    """
    Backtestet eine kombinierte Strategie.

    Args:
        strategy_name: Name der Strategie
        get_numbers_func: Funktion die (df, end_date, window) nimmt und Zahlen zurückgibt
        use_frueh_phase: Nur in FRÜH-Phase (Tag 1-14) spielen
        use_cooldown: 30 Tage nach 10/10 nicht spielen
        hz_delay: Tage Wartezeit nach Hot-Zone Ermittlung
    """
    results = {
        'strategy': strategy_name,
        'params': {
            'use_frueh_phase': use_frueh_phase,
            'use_cooldown': use_cooldown,
            'hz_delay': hz_delay,
            'window': window
        },
        'jackpots': 0,
        'jackpot_dates': [],
        'play_days': 0,
        'skip_cooldown': 0,
        'skip_spaet': 0,
        'unique_days': set()
    }

    # Alle 10/10 Jackpots für Cooldown
    jp_dates_10_10 = find_jackpots_10_10(gq_df, df['datum'].min(), LAST_DRAW) if gq_df is not None else []

    # Test-Monate generieren
    test_dates = pd.date_range(start='2022-06-01', end='2024-12-31', freq='MS')

    for test_date in test_dates:
        # Ermittlungs-Datum (Ende des Vormonats)
        ermittlung_date = test_date - timedelta(days=1)

        # Zahlen ermitteln
        numbers = get_numbers_func(df, ermittlung_date, window)
        if len(numbers) < 6:
            continue

        # Spielzeitraum
        play_start = test_date + timedelta(days=hz_delay)
        play_end = test_date + timedelta(days=hz_delay + 30)

        # Durch jeden Tag im Spielzeitraum
        current = play_start
        while current <= play_end and current <= LAST_DRAW:
            should_play = True

            # Check FRÜH-Phase
            if use_frueh_phase and get_cycle_phase(current) != "FRÜH":
                results['skip_spaet'] += 1
                should_play = False

            # Check Cooldown
            if use_cooldown and is_in_cooldown(current, jp_dates_10_10):
                results['skip_cooldown'] += 1
                should_play = False

            if should_play:
                results['play_days'] += 1

            current += timedelta(days=1)

        # Finde Jackpots im Spielzeitraum (unter Berücksichtigung der Regeln)
        jackpots = find_typ6_jackpots(df, numbers, play_start, play_end)

        for jp_date in jackpots:
            # Prüfe ob wir an diesem Tag gespielt hätten
            would_play = True
            if use_frueh_phase and get_cycle_phase(jp_date) != "FRÜH":
                would_play = False
            if use_cooldown and is_in_cooldown(jp_date, jp_dates_10_10):
                would_play = False

            if would_play:
                results['jackpots'] += 1
                results['jackpot_dates'].append(jp_date)
                results['unique_days'].add(jp_date)

    results['unique_days'] = len(results['unique_days'])
    return results


def main():
    print("=" * 80)
    print("KOMBINIERTE STRATEGIE: Loop-Erkenntnisse + Hot-Zone")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print()

    # GQ-Daten laden
    gq_df = load_gq_data()

    # =========================================================================
    # TEIL 1: Verschiedene Strategien backtesten
    # =========================================================================
    print("=" * 80)
    print("TEIL 1: STRATEGIE-VERGLEICH (Walk-Forward Backtest 2022-2024)")
    print("=" * 80)
    print()

    strategies = []

    # 1. Nur Hot-Zone 7 (Basis)
    def get_hz7(df, end_date, window):
        return get_hot_zone(df, end_date, window, 7)

    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 Basis (keine Regeln)",
        get_hz7, use_frueh_phase=False, use_cooldown=False, hz_delay=0
    ))

    # 2. HZ7 + 48 Tage Delay (unsere Erkenntnis)
    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 + 48d Delay",
        get_hz7, use_frueh_phase=False, use_cooldown=False, hz_delay=48
    ))

    # 3. HZ7 + FRÜH-Phase (Loop-Erkenntnis)
    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 + FRÜH-Phase",
        get_hz7, use_frueh_phase=True, use_cooldown=False, hz_delay=0
    ))

    # 4. HZ7 + Cooldown (Loop-Erkenntnis)
    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 + Cooldown",
        get_hz7, use_frueh_phase=False, use_cooldown=True, hz_delay=0
    ))

    # 5. HZ7 + FRÜH + Cooldown (Loop kombiniert)
    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 + FRÜH + Cooldown",
        get_hz7, use_frueh_phase=True, use_cooldown=True, hz_delay=0
    ))

    # 6. HZ7 + 48d Delay + FRÜH + Cooldown (KOMPLETT)
    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ7 KOMPLETT (alle Regeln)",
        get_hz7, use_frueh_phase=True, use_cooldown=True, hz_delay=48
    ))

    # 7. Loop Kern-Zahlen
    def get_loop_kern(df, end_date, window):
        return LOOP_KERN + [2]  # 7 Zahlen

    strategies.append(backtest_combined_strategy(
        df, gq_df, "Loop Kern-Zahlen + alle Regeln",
        get_loop_kern, use_frueh_phase=True, use_cooldown=True, hz_delay=0
    ))

    # 8. HZ6 (keine Wartezeit)
    def get_hz6(df, end_date, window):
        return get_hot_zone(df, end_date, window, 6)

    strategies.append(backtest_combined_strategy(
        df, gq_df, "HZ6 + FRÜH + Cooldown",
        get_hz6, use_frueh_phase=True, use_cooldown=True, hz_delay=0
    ))

    # Ergebnisse ausgeben
    print(f"{'Strategie':<35} {'JP':>6} {'Tage':>8} {'JP/Tag':>10} {'Skip CD':>10} {'Skip SP':>10}")
    print("-" * 85)

    for s in sorted(strategies, key=lambda x: -x['jackpots']):
        jp_per_day = s['jackpots'] / max(s['play_days'], 1) * 100
        print(f"{s['strategy']:<35} {s['jackpots']:>6} {s['unique_days']:>8} "
              f"{jp_per_day:>9.2f}% {s['skip_cooldown']:>10} {s['skip_spaet']:>10}")

    # =========================================================================
    # TEIL 2: Beste Strategie identifizieren
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 2: ANALYSE DER BESTEN STRATEGIE")
    print("=" * 80)
    print()

    # Sortiere nach Jackpots
    best = max(strategies, key=lambda x: x['jackpots'])
    print(f"Beste Strategie: {best['strategy']}")
    print(f"Jackpots: {best['jackpots']}")
    print(f"Unique Tage: {best['unique_days']}")
    print()

    # Vergleiche mit Basis
    basis = strategies[0]  # HZ7 Basis
    improvement = (best['jackpots'] - basis['jackpots']) / max(basis['jackpots'], 1) * 100
    print(f"Verbesserung vs Basis: {improvement:+.1f}%")

    # =========================================================================
    # TEIL 3: Synergie-Analyse
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 3: SYNERGIE-ANALYSE")
    print("=" * 80)
    print()

    print("Effekt einzelner Regeln:")
    print()

    basis_jp = strategies[0]['jackpots']
    for s in strategies[1:6]:
        diff = s['jackpots'] - basis_jp
        diff_pct = diff / max(basis_jp, 1) * 100
        print(f"  {s['strategy']:<35} {diff:+d} JP ({diff_pct:+.1f}%)")

    # =========================================================================
    # TEIL 4: Überlappung HZ vs Loop-Zahlen
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 4: ZAHLEN-ÜBERLAPPUNG")
    print("=" * 80)
    print()

    current_hz7 = get_hot_zone(df, LAST_DRAW, 50, 7)
    overlap = set(current_hz7) & set(LOOP_KERN)

    print(f"Aktuelle HZ7 (W50): {sorted(current_hz7)}")
    print(f"Loop Kern-Zahlen:   {sorted(LOOP_KERN)}")
    print(f"Überlappung:        {sorted(overlap)} ({len(overlap)} Zahlen)")
    print()

    # Kombinierte Empfehlung
    combined = list(set(current_hz7) | set(LOOP_KERN))[:7]
    print(f"Kombinierte Top-7:  {sorted(combined)}")

    # =========================================================================
    # TEIL 5: FINALE EMPFEHLUNG
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 5: FINALE KOMBINIERTE STRATEGIE")
    print("=" * 80)
    print()

    print("REGELN:")
    print("  1. Hot-Zone 7 (W50) als Basis")
    print("  2. 48-60 Tage Wartezeit nach Ermittlung")
    print("  3. Nur in FRÜH-Phase spielen (Tag 1-14)")
    print("  4. 30 Tage Cooldown nach 10/10 Jackpot")
    print()

    print("AKTUELLE EMPFEHLUNG:")
    print(f"  Zahlen: {sorted(current_hz7)}")
    print()

    # Check ob wir heute spielen sollten
    jp_dates_10_10 = find_jackpots_10_10(gq_df, df['datum'].min(), LAST_DRAW) if gq_df is not None else []
    last_jp = max(jp_dates_10_10) if jp_dates_10_10 else None

    print("STATUS-CHECK:")
    print(f"  - Zyklus-Phase: {get_cycle_phase(LAST_DRAW)}")
    if last_jp:
        days_since_jp = (LAST_DRAW - last_jp).days
        print(f"  - Tage seit 10/10 JP: {days_since_jp} (Cooldown: {'AKTIV' if days_since_jp < 30 else 'OK'})")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Kombinierte Strategie: Loop + Hot-Zone

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Backtest-Zeitraum:** 2022-2024

---

## Executive Summary

Die Kombination von Loop-Erkenntnissen (FRÜH-Phase, Cooldown) mit der Hot-Zone Strategie
(48-60 Tage Wartezeit) wurde getestet.

---

## Strategie-Vergleich

| Strategie | Jackpots | Tage | JP/Tag |
|-----------|----------|------|--------|
"""

    for s in sorted(strategies, key=lambda x: -x['jackpots']):
        jp_per_day = s['jackpots'] / max(s['play_days'], 1) * 100
        md += f"| {s['strategy']} | {s['jackpots']} | {s['unique_days']} | {jp_per_day:.2f}% |\n"

    md += f"""

---

## Beste Strategie

**{best['strategy']}**

- Jackpots: {best['jackpots']}
- Verbesserung vs Basis: {improvement:+.1f}%

---

## Finale kombinierte Regeln

1. **Hot-Zone 7 (W50)** als Zahlenbasis
2. **48-60 Tage Wartezeit** nach Ermittlung (HZ-Erkenntnis)
3. **FRÜH-Phase (Tag 1-14)** bevorzugen (Loop-Erkenntnis: +364% ROI)
4. **30 Tage Cooldown** nach 10/10 Jackpot (Loop-Erkenntnis: -66% ROI)

---

## Zahlen-Empfehlung

| Quelle | Zahlen |
|--------|--------|
| Aktuelle HZ7 | {sorted(current_hz7)} |
| Loop Kern | {sorted(LOOP_KERN)} |
| Überlappung | {sorted(overlap)} |
| **Kombiniert** | **{sorted(combined)}** |

---

## 7 Kombinationen

| # | Kombination |
|---|-------------|
"""

    final7 = sorted(combined)[:7]
    for i, exclude in enumerate(final7, 1):
        combo = sorted([n for n in final7 if n != exclude])
        md += f"| {i} | {combo} |\n"

    md += f"""

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "kombinierte_strategie_loop_hz.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")

    # JSON für weitere Analyse
    json_output = {
        'strategies': [{
            'name': s['strategy'],
            'jackpots': s['jackpots'],
            'unique_days': s['unique_days'],
            'params': s['params']
        } for s in strategies],
        'best_strategy': best['strategy'],
        'current_hz7': current_hz7,
        'loop_kern': LOOP_KERN,
        'combined_recommendation': combined[:7]
    }

    json_file = BASE_DIR / "results" / "kombinierte_strategie_loop_hz.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, default=str)

    print(f"JSON gespeichert: {json_file}")


if __name__ == "__main__":
    main()
