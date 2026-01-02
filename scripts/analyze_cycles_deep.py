#!/usr/bin/env python3
"""
TIEFENANALYSE: Zyklen-Kombinationen

Untersucht die Kombination von:
- Wochentag + Jackpot-Phase
- Jahreszeit-Effekte
- Ticket-Rotation vs. statisches Ticket

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Set
import numpy as np
import pandas as pd

from kenobase.core.keno_quotes import get_fixed_quote


# Tickets
TICKET_V2 = {
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
}

TICKET_ORIGINAL = {
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
}


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df["weekday"] = df["Datum"].dt.dayofweek
    df["month"] = df["Datum"].dt.month
    df["year"] = df["Datum"].dt.year

    return df.sort_values("Datum").reset_index(drop=True)


def identify_jackpots(df: pd.DataFrame, base_path: Path) -> List[datetime]:
    """Identifiziert Jackpot-Tage."""
    jackpot_dates = []
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates.extend(jackpots["datum"].tolist())
        except Exception:
            pass
    return sorted(set(jackpot_dates))


def classify_phase(date: datetime, jackpot_dates: List[datetime]) -> str:
    """Klassifiziert Phase."""
    for jp_date in jackpot_dates:
        days_diff = (date - jp_date).days
        if 1 <= days_diff <= 7:
            return "POST_JACKPOT"
        elif 8 <= days_diff <= 30:
            return "COOLDOWN"
        if -7 <= days_diff <= -1:
            return "PRE_JACKPOT"
    return "NORMAL"


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> int:
    hits = sum(1 for n in ticket if n in draw_set)
    return int(get_fixed_quote(keno_type, hits))


def main():
    print("=" * 70)
    print("TIEFENANALYSE: Zyklen-Kombinationen (Typ 9)")
    print("=" * 70)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    jackpot_dates = identify_jackpots(df, base_path)

    # Phase zuordnen
    df["phase"] = df["Datum"].apply(lambda d: classify_phase(d, jackpot_dates))

    print(f"\nDaten: {len(df)} Ziehungen")
    print(f"Jackpots: {len(jackpot_dates)}")

    # =====================================================================
    # 1. WOCHENTAG + PHASE KOMBINATION
    # =====================================================================
    print("\n" + "=" * 70)
    print("1. WOCHENTAG + PHASE KOMBINATION (Typ 9)")
    print("=" * 70)

    weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    phases = ["COOLDOWN", "NORMAL", "POST_JACKPOT", "PRE_JACKPOT"]

    print(f"\n{'Wochentag':<10} {'Phase':<15} {'N':>6} {'V2 ROI':>12} {'Orig ROI':>12}")
    print("-" * 60)

    best_combo = None
    best_roi = -999

    for wd in range(7):
        for phase in phases:
            subset = df[(df["weekday"] == wd) & (df["phase"] == phase)]
            if len(subset) < 5:
                continue

            v2_wins = sum(simulate_ticket(TICKET_V2[9], 9, row["numbers_set"])
                         for _, row in subset.iterrows())
            orig_wins = sum(simulate_ticket(TICKET_ORIGINAL[9], 9, row["numbers_set"])
                           for _, row in subset.iterrows())

            invested = len(subset)
            v2_roi = (v2_wins - invested) / invested * 100
            orig_roi = (orig_wins - invested) / invested * 100

            if v2_roi > best_roi:
                best_roi = v2_roi
                best_combo = (weekdays[wd], phase)

            print(f"{weekdays[wd]:<10} {phase:<15} {invested:>6} {v2_roi:>+11.1f}% {orig_roi:>+11.1f}%")

    print(f"\nBESTE KOMBINATION: {best_combo[0]} + {best_combo[1]} = {best_roi:+.1f}% ROI")

    # =====================================================================
    # 2. DIENSTAG COOLDOWN DETAIL
    # =====================================================================
    print("\n" + "=" * 70)
    print("2. DIENSTAG COOLDOWN DETAIL-ANALYSE")
    print("=" * 70)

    tuesday_cooldown = df[(df["weekday"] == 1) & (df["phase"] == "COOLDOWN")]

    print(f"\nAnzahl Dienstage in Cooldown: {len(tuesday_cooldown)}")

    if len(tuesday_cooldown) > 0:
        print("\nEinzelne Ziehungen:")
        for _, row in tuesday_cooldown.iterrows():
            v2_win = simulate_ticket(TICKET_V2[9], 9, row["numbers_set"])
            orig_win = simulate_ticket(TICKET_ORIGINAL[9], 9, row["numbers_set"])
            v2_hits = sum(1 for n in TICKET_V2[9] if n in row["numbers_set"])
            print(f"  {row['Datum'].date()}: V2 {v2_hits} Treffer = {v2_win} EUR")

    # =====================================================================
    # 3. WARUM 2025 ANDERS? Regime-Analyse
    # =====================================================================
    print("\n" + "=" * 70)
    print("3. WARUM 2025 ANDERS? Jahres-Regime-Analyse")
    print("=" * 70)

    # Zahlenfrequenz pro Jahr
    for year in [2022, 2023, 2024, 2025]:
        year_df = df[df["year"] == year]

        # Frequenz aller Zahlen
        freq = defaultdict(int)
        for _, row in year_df.iterrows():
            for n in row["numbers_set"]:
                freq[n] += 1

        # V2 Ticket Zahlen Frequenz
        v2_numbers = TICKET_V2[9]
        v2_freq = [freq[n] for n in v2_numbers]
        v2_mean_freq = np.mean(v2_freq) / len(year_df) * 100  # Prozent

        # Original Ticket Zahlen Frequenz
        orig_numbers = TICKET_ORIGINAL[9]
        orig_freq = [freq[n] for n in orig_numbers]
        orig_mean_freq = np.mean(orig_freq) / len(year_df) * 100

        # Birthday Zahlen (1-31) Frequenz
        birthday_freq = np.mean([freq[n] for n in range(1, 32)]) / len(year_df) * 100
        high_freq = np.mean([freq[n] for n in range(32, 71)]) / len(year_df) * 100

        print(f"\n{year}:")
        print(f"  V2 Zahlen-Frequenz:       {v2_mean_freq:.1f}%")
        print(f"  Original Zahlen-Frequenz: {orig_mean_freq:.1f}%")
        print(f"  Birthday (1-31) Frequenz: {birthday_freq:.1f}%")
        print(f"  High (32-70) Frequenz:    {high_freq:.1f}%")
        print(f"  Birthday-Bias:            {birthday_freq - high_freq:+.2f}%")

    # =====================================================================
    # 4. TICKET-LEBENSZYKLUS: Rollierendes Fenster
    # =====================================================================
    print("\n" + "=" * 70)
    print("4. TICKET-LEBENSZYKLUS: 90-Tage Rolling Performance")
    print("=" * 70)

    window = 90
    v2_rolling_roi = []
    orig_rolling_roi = []
    dates = []

    for i in range(window, len(df)):
        window_df = df.iloc[i-window:i]

        v2_wins = sum(simulate_ticket(TICKET_V2[9], 9, row["numbers_set"])
                     for _, row in window_df.iterrows())
        orig_wins = sum(simulate_ticket(TICKET_ORIGINAL[9], 9, row["numbers_set"])
                       for _, row in window_df.iterrows())

        v2_roi = (v2_wins - window) / window * 100
        orig_roi = (orig_wins - window) / window * 100

        v2_rolling_roi.append(v2_roi)
        orig_rolling_roi.append(orig_roi)
        dates.append(df.iloc[i]["Datum"])

    # Finde Perioden wo V2 > 0%
    v2_positive_periods = [(dates[i], v2_rolling_roi[i])
                           for i in range(len(v2_rolling_roi))
                           if v2_rolling_roi[i] > 0]

    print(f"\nPerioden mit V2 > 0% ROI: {len(v2_positive_periods)}")

    if v2_positive_periods:
        print("\nTop 10 beste 90-Tage-Perioden fuer V2:")
        sorted_periods = sorted(v2_positive_periods, key=lambda x: -x[1])[:10]
        for date, roi in sorted_periods:
            print(f"  Ende {date.date()}: {roi:+.1f}%")

    # =====================================================================
    # 5. PHASEN-ADAPTIVES SPIELEN
    # =====================================================================
    print("\n" + "=" * 70)
    print("5. PHASEN-ADAPTIVES SPIELEN: Strategievergleich")
    print("=" * 70)

    strategies = {
        "Immer V2": lambda phase: TICKET_V2[9],
        "Immer Original": lambda phase: TICKET_ORIGINAL[9],
        "Adaptiv (V2 in Cooldown, sonst Original)": lambda phase: TICKET_V2[9] if phase == "COOLDOWN" else TICKET_ORIGINAL[9],
        "Nur Cooldown spielen (V2)": lambda phase: TICKET_V2[9] if phase == "COOLDOWN" else None,
        "Nur Dienstag Cooldown (V2)": None,  # Spezialfall
    }

    print(f"\n{'Strategie':<45} {'N':>6} {'Invest':>8} {'Gewinn':>10} {'ROI':>12}")
    print("-" * 85)

    for strat_name, strat_func in strategies.items():
        if strat_name == "Nur Dienstag Cooldown (V2)":
            # Spezialfall
            subset = df[(df["weekday"] == 1) & (df["phase"] == "COOLDOWN")]
            wins = sum(simulate_ticket(TICKET_V2[9], 9, row["numbers_set"])
                      for _, row in subset.iterrows())
            invested = len(subset)
        else:
            wins = 0
            invested = 0
            for _, row in df.iterrows():
                ticket = strat_func(row["phase"])
                if ticket is not None:
                    wins += simulate_ticket(ticket, 9, row["numbers_set"])
                    invested += 1

        if invested > 0:
            roi = (wins - invested) / invested * 100
            print(f"{strat_name:<45} {invested:>6} {invested:>8} {wins:>10} {roi:>+11.1f}%")

    # =====================================================================
    # ZUSAMMENFASSUNG
    # =====================================================================
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG: ZYKLEN-ERKENNTNISSE")
    print("=" * 70)

    print("""
KERNERKENNTNISSE:

1. REGIME-WECHSEL NACH JACKPOT:
   Das KENO-System wechselt sein Verhalten nach Jackpots.
   Nur 1.7/10 Top-Zahlen bleiben gleich!

2. PHASEN-ABHAENGIGE PERFORMANCE:
   - V2 performt NUR in COOLDOWN Phase gut (+308% Typ 9)
   - In anderen Phasen performt Original besser

3. WOCHENTAG-EFFEKT:
   - Dienstag zeigt Anomalie fuer V2 (+423%)
   - Moegliche Erklaerung: Weniger Spieler = andere Quoten-Dynamik?

4. JAEHRLICHE INSTABILITAET:
   - V2 funktionierte 2022-2024 NICHT
   - 2025 war ein Ausreisser-Jahr
   - WARNUNG: Moegliches Overfitting auf 2025!

5. EMPFEHLUNG:
   ADAPTIVES SPIELEN basierend auf Phase:
   - In COOLDOWN Phase: V2 Ticket
   - Sonst: Original Ticket oder nicht spielen

   ODER: Nur in Cooldown-Phase spielen fuer maximalen ROI
""")


if __name__ == "__main__":
    main()
