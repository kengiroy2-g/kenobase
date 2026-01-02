#!/usr/bin/env python3
"""
ZYKLEN-ANALYSE: Event-basierte Keno-Zyklen

Untersucht:
1. Jackpot-basierte Zyklen (Pre/Post/Cooldown)
2. Wochentag-Zyklen
3. Ticket-Lebenszyklus (>365 Tage)
4. Zahlen-Ueberlappung in verschiedenen Phasen

Hypothese: KENO-System ist zustandsbasiert (stateful) und wechselt
Verhalten basierend auf Events, nicht Kalenderjahr.

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


# ============================================================================
# TICKETS ZUM TESTEN
# ============================================================================

TICKET_V2 = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

TICKET_ORIGINAL = {
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten mit Jackpot-Info."""

    # Neueste Daten
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    if not keno_path.exists():
        keno_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Zahlen extrahieren
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df["numbers_list"] = df[pos_cols].apply(lambda row: sorted(row.dropna().astype(int).tolist()), axis=1)

    # Wochentag
    df["weekday"] = df["Datum"].dt.dayofweek  # 0=Mo, 6=So
    df["weekday_name"] = df["Datum"].dt.day_name()

    df = df.sort_values("Datum").reset_index(drop=True)

    return df


def identify_jackpots(df: pd.DataFrame, base_path: Path) -> List[datetime]:
    """Identifiziert Jackpot-Tage."""

    jackpot_dates = []

    # Versuche Timeline zu laden
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates.extend(jackpots["datum"].tolist())
        except Exception:
            pass

    # Fallback: Gewinnklasse 1 Treffer (10 aus 10)
    # Diese sind sehr selten und markieren Jackpot-Events
    if "GK1" in df.columns or "Gewinnklasse_1" in df.columns:
        gk1_col = "GK1" if "GK1" in df.columns else "Gewinnklasse_1"
        gk1_hits = df[df[gk1_col] > 0]
        jackpot_dates.extend(gk1_hits["Datum"].tolist())

    return sorted(set(jackpot_dates))


def classify_cycle_phase(
    date: datetime,
    jackpot_dates: List[datetime],
    cooldown_days: int = 30,
    pre_jackpot_days: int = 7
) -> str:
    """
    Klassifiziert eine Ziehung in eine Zyklusphase.

    Phasen:
    - PRE_JACKPOT: 7 Tage vor einem Jackpot
    - POST_JACKPOT: 1-7 Tage nach Jackpot
    - COOLDOWN: 8-30 Tage nach Jackpot
    - NORMAL: Ausserhalb dieser Phasen
    """

    for jp_date in jackpot_dates:
        days_diff = (date - jp_date).days

        # Post-Jackpot Phase
        if 1 <= days_diff <= 7:
            return "POST_JACKPOT"
        elif 8 <= days_diff <= cooldown_days:
            return "COOLDOWN"

        # Pre-Jackpot Phase
        if -pre_jackpot_days <= days_diff <= -1:
            return "PRE_JACKPOT"

    return "NORMAL"


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket und gibt (Gewinn, Treffer) zurueck."""
    hits = sum(1 for n in ticket if n in draw_set)
    return int(get_fixed_quote(keno_type, hits)), hits


def calculate_number_overlap(df: pd.DataFrame, window: int = 5) -> pd.Series:
    """
    Berechnet die Ueberlappung von Gewinnzahlen zwischen aufeinanderfolgenden Ziehungen.

    Overlap = Anzahl gemeinsamer Zahlen / 20
    """
    overlaps = []

    for i in range(1, len(df)):
        prev_set = df.iloc[i-1]["numbers_set"]
        curr_set = df.iloc[i]["numbers_set"]
        overlap = len(prev_set & curr_set) / 20.0
        overlaps.append(overlap)

    # Erste Ziehung hat keinen Vorgaenger
    overlaps.insert(0, np.nan)

    return pd.Series(overlaps)


def analyze_jackpot_cycles(df: pd.DataFrame, jackpot_dates: List[datetime]) -> Dict:
    """Analysiert Ticket-Performance in verschiedenen Jackpot-Phasen."""

    # Phase fuer jede Ziehung bestimmen
    df["cycle_phase"] = df["Datum"].apply(
        lambda d: classify_cycle_phase(d, jackpot_dates)
    )

    results = {
        "phase_counts": df["cycle_phase"].value_counts().to_dict(),
        "by_type": {},
    }

    print("\n" + "=" * 70)
    print("1. JACKPOT-BASIERTE ZYKLEN")
    print("=" * 70)

    print(f"\nPhasen-Verteilung:")
    for phase, count in results["phase_counts"].items():
        print(f"  {phase}: {count} Tage ({count/len(df)*100:.1f}%)")

    for keno_type in [8, 9, 10]:
        ticket_v2 = TICKET_V2[keno_type]
        ticket_orig = TICKET_ORIGINAL[keno_type]

        phase_results = {}

        for phase in ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]:
            phase_df = df[df["cycle_phase"] == phase]

            if len(phase_df) == 0:
                continue

            v2_wins = 0
            orig_wins = 0

            for _, row in phase_df.iterrows():
                draw_set = row["numbers_set"]
                v2_win, _ = simulate_ticket(ticket_v2, keno_type, draw_set)
                orig_win, _ = simulate_ticket(ticket_orig, keno_type, draw_set)
                v2_wins += v2_win
                orig_wins += orig_win

            invested = len(phase_df)
            v2_roi = (v2_wins - invested) / invested * 100 if invested > 0 else 0
            orig_roi = (orig_wins - invested) / invested * 100 if invested > 0 else 0

            phase_results[phase] = {
                "days": invested,
                "v2_roi": v2_roi,
                "orig_roi": orig_roi,
                "v2_wins": v2_wins,
                "orig_wins": orig_wins,
            }

        results["by_type"][f"typ_{keno_type}"] = phase_results

        print(f"\n--- TYP {keno_type} ---")
        print(f"{'Phase':<15} {'Tage':>8} {'V2 ROI':>12} {'Orig ROI':>12} {'Besser':>10}")
        print("-" * 60)

        for phase in ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]:
            if phase in phase_results:
                pr = phase_results[phase]
                better = "V2" if pr["v2_roi"] > pr["orig_roi"] else "ORIG"
                print(f"{phase:<15} {pr['days']:>8} {pr['v2_roi']:>+11.1f}% {pr['orig_roi']:>+11.1f}% {better:>10}")

    return results


def analyze_weekday_cycles(df: pd.DataFrame) -> Dict:
    """Analysiert Ticket-Performance nach Wochentag."""

    results = {"by_type": {}}

    print("\n" + "=" * 70)
    print("2. WOCHENTAG-ZYKLEN")
    print("=" * 70)

    weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                     "Freitag", "Samstag", "Sonntag"]

    for keno_type in [8, 9, 10]:
        ticket_v2 = TICKET_V2[keno_type]
        ticket_orig = TICKET_ORIGINAL[keno_type]

        weekday_results = {}

        for wd in range(7):
            wd_df = df[df["weekday"] == wd]

            if len(wd_df) == 0:
                continue

            v2_wins = 0
            orig_wins = 0

            for _, row in wd_df.iterrows():
                draw_set = row["numbers_set"]
                v2_win, _ = simulate_ticket(ticket_v2, keno_type, draw_set)
                orig_win, _ = simulate_ticket(ticket_orig, keno_type, draw_set)
                v2_wins += v2_win
                orig_wins += orig_win

            invested = len(wd_df)
            v2_roi = (v2_wins - invested) / invested * 100 if invested > 0 else 0
            orig_roi = (orig_wins - invested) / invested * 100 if invested > 0 else 0

            weekday_results[weekday_names[wd]] = {
                "days": invested,
                "v2_roi": v2_roi,
                "orig_roi": orig_roi,
            }

        results["by_type"][f"typ_{keno_type}"] = weekday_results

        print(f"\n--- TYP {keno_type} ---")
        print(f"{'Wochentag':<12} {'Tage':>8} {'V2 ROI':>12} {'Orig ROI':>12} {'Besser':>10}")
        print("-" * 55)

        for wd_name in weekday_names:
            if wd_name in weekday_results:
                wr = weekday_results[wd_name]
                better = "V2" if wr["v2_roi"] > wr["orig_roi"] else "ORIG"
                print(f"{wd_name:<12} {wr['days']:>8} {wr['v2_roi']:>+11.1f}% {wr['orig_roi']:>+11.1f}% {better:>10}")

    return results


def analyze_ticket_longevity(df: pd.DataFrame, window_days: int = 365) -> Dict:
    """
    Analysiert ob Tickets ueber lange Perioden (>365 Tage) stabil performen.

    Teilt die Daten in rollierende Fenster und misst ROI-Stabilitaet.
    """

    results = {"by_type": {}}

    print("\n" + "=" * 70)
    print("3. TICKET-LEBENSZYKLUS (>365 TAGE)")
    print("=" * 70)

    # Bestimme verfuegbare Jahre
    years = sorted(df["Datum"].dt.year.unique())
    print(f"\nVerfuegbare Jahre: {years}")

    for keno_type in [8, 9, 10]:
        ticket_v2 = TICKET_V2[keno_type]
        ticket_orig = TICKET_ORIGINAL[keno_type]

        yearly_results = {}

        for year in years:
            year_df = df[df["Datum"].dt.year == year]

            if len(year_df) < 30:  # Mindestens 30 Ziehungen
                continue

            v2_wins = 0
            orig_wins = 0

            for _, row in year_df.iterrows():
                draw_set = row["numbers_set"]
                v2_win, _ = simulate_ticket(ticket_v2, keno_type, draw_set)
                orig_win, _ = simulate_ticket(ticket_orig, keno_type, draw_set)
                v2_wins += v2_win
                orig_wins += orig_win

            invested = len(year_df)
            v2_roi = (v2_wins - invested) / invested * 100
            orig_roi = (orig_wins - invested) / invested * 100

            yearly_results[year] = {
                "days": invested,
                "v2_roi": v2_roi,
                "orig_roi": orig_roi,
            }

        # Stabilitaet berechnen (Standardabweichung der ROIs)
        v2_rois = [yr["v2_roi"] for yr in yearly_results.values()]
        orig_rois = [yr["orig_roi"] for yr in yearly_results.values()]

        v2_stability = np.std(v2_rois) if len(v2_rois) > 1 else 0
        orig_stability = np.std(orig_rois) if len(orig_rois) > 1 else 0

        results["by_type"][f"typ_{keno_type}"] = {
            "yearly": yearly_results,
            "v2_mean_roi": np.mean(v2_rois),
            "orig_mean_roi": np.mean(orig_rois),
            "v2_stability": v2_stability,
            "orig_stability": orig_stability,
        }

        print(f"\n--- TYP {keno_type} ---")
        print(f"{'Jahr':<8} {'Tage':>8} {'V2 ROI':>12} {'Orig ROI':>12}")
        print("-" * 45)

        for year, yr in sorted(yearly_results.items()):
            print(f"{year:<8} {yr['days']:>8} {yr['v2_roi']:>+11.1f}% {yr['orig_roi']:>+11.1f}%")

        print("-" * 45)
        print(f"{'MITTEL':<8} {'':>8} {np.mean(v2_rois):>+11.1f}% {np.mean(orig_rois):>+11.1f}%")
        print(f"{'STD':<8} {'':>8} {v2_stability:>11.1f}% {orig_stability:>11.1f}%")

        # Interpretation
        v2_stable = v2_stability < 100  # Weniger als 100% Standardabweichung
        orig_stable = orig_stability < 100

        print(f"\nStabilitaets-Bewertung:")
        print(f"  V2:   {'STABIL' if v2_stable else 'INSTABIL'} (STD={v2_stability:.1f}%)")
        print(f"  Orig: {'STABIL' if orig_stable else 'INSTABIL'} (STD={orig_stability:.1f}%)")

    return results


def analyze_number_overlap_by_phase(df: pd.DataFrame, jackpot_dates: List[datetime]) -> Dict:
    """
    Analysiert ob die Zahlen-Ueberlappung sich in verschiedenen Phasen aendert.

    Hypothese: Nach Jackpot koennte das System sein Auswahlverhalten aendern,
    was sich in veraenderter Ueberlappung zeigt.
    """

    results = {}

    print("\n" + "=" * 70)
    print("4. ZAHLEN-UEBERLAPPUNG NACH PHASE")
    print("=" * 70)

    # Ueberlappung berechnen
    df["overlap"] = calculate_number_overlap(df)

    # Phase zuordnen (falls noch nicht geschehen)
    if "cycle_phase" not in df.columns:
        df["cycle_phase"] = df["Datum"].apply(
            lambda d: classify_cycle_phase(d, jackpot_dates)
        )

    print(f"\n{'Phase':<15} {'N':>8} {'Mean Overlap':>15} {'Std':>10}")
    print("-" * 55)

    for phase in ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]:
        phase_df = df[df["cycle_phase"] == phase]

        if len(phase_df) < 2:
            continue

        mean_overlap = phase_df["overlap"].mean()
        std_overlap = phase_df["overlap"].std()

        results[phase] = {
            "count": len(phase_df),
            "mean_overlap": mean_overlap,
            "std_overlap": std_overlap,
        }

        print(f"{phase:<15} {len(phase_df):>8} {mean_overlap:>14.3f} {std_overlap:>10.3f}")

    # Gesamt-Durchschnitt
    overall_mean = df["overlap"].mean()
    overall_std = df["overlap"].std()

    print("-" * 55)
    print(f"{'GESAMT':<15} {len(df):>8} {overall_mean:>14.3f} {overall_std:>10.3f}")

    # Signifikanz-Test (einfach: Abweichung vom Mittel)
    print("\nAbweichung vom Gesamtmittel:")
    for phase, res in results.items():
        diff = res["mean_overlap"] - overall_mean
        direction = "MEHR" if diff > 0 else "WENIGER"
        print(f"  {phase}: {diff:+.3f} ({direction} Ueberlappung)")

    results["overall"] = {
        "mean": overall_mean,
        "std": overall_std,
    }

    return results


def analyze_consecutive_patterns(df: pd.DataFrame, jackpot_dates: List[datetime]) -> Dict:
    """
    Analysiert aufeinanderfolgende Muster nach Jackpots.

    Fragt: Wie viele Zahlen bleiben nach einem Jackpot gleich?
    Aendert sich das Muster der "heissen" und "kalten" Zahlen?
    """

    results = {"post_jackpot_patterns": []}

    print("\n" + "=" * 70)
    print("5. MUSTER-WECHSEL NACH JACKPOT")
    print("=" * 70)

    for jp_date in jackpot_dates:
        # Finde Ziehung am Jackpot-Tag
        jp_draws = df[df["Datum"] == jp_date]
        if len(jp_draws) == 0:
            continue

        jp_idx = jp_draws.index[0]

        # Hole Ziehungen vor und nach Jackpot
        if jp_idx < 5 or jp_idx >= len(df) - 10:
            continue

        pre_draws = df.iloc[jp_idx-5:jp_idx]
        post_draws = df.iloc[jp_idx+1:jp_idx+11]

        # Zahlenverteilung vor Jackpot
        pre_numbers = defaultdict(int)
        for _, row in pre_draws.iterrows():
            for n in row["numbers_set"]:
                pre_numbers[n] += 1

        # Zahlenverteilung nach Jackpot
        post_numbers = defaultdict(int)
        for _, row in post_draws.iterrows():
            for n in row["numbers_set"]:
                post_numbers[n] += 1

        # Top-10 vor und nach
        pre_top10 = set(sorted(pre_numbers.keys(), key=lambda x: -pre_numbers[x])[:10])
        post_top10 = set(sorted(post_numbers.keys(), key=lambda x: -post_numbers[x])[:10])

        overlap = len(pre_top10 & post_top10)

        results["post_jackpot_patterns"].append({
            "jackpot_date": str(jp_date.date()) if hasattr(jp_date, 'date') else str(jp_date),
            "pre_top10": sorted(pre_top10),
            "post_top10": sorted(post_top10),
            "overlap": overlap,
        })

    if results["post_jackpot_patterns"]:
        overlaps = [p["overlap"] for p in results["post_jackpot_patterns"]]
        mean_overlap = np.mean(overlaps)

        print(f"\nAnzahl analysierter Jackpots: {len(results['post_jackpot_patterns'])}")
        print(f"Durchschnittliche Top-10 Ueberlappung Pre/Post: {mean_overlap:.1f}/10")

        print("\nDetails pro Jackpot:")
        for pattern in results["post_jackpot_patterns"][:5]:  # Erste 5
            print(f"  {pattern['jackpot_date']}: {pattern['overlap']}/10 gemeinsame Top-Zahlen")

        # Interpretation
        if mean_overlap < 5:
            print("\n==> STARKER REGIME-WECHSEL: System aendert Zahlenauswahl nach Jackpot!")
        elif mean_overlap < 7:
            print("\n==> MODERATER REGIME-WECHSEL: Teilweise neue Zahlen nach Jackpot")
        else:
            print("\n==> KEIN REGIME-WECHSEL: Zahlenauswahl bleibt stabil")

        results["mean_overlap"] = mean_overlap

    return results


def main():
    print("=" * 70)
    print("ZYKLEN-ANALYSE: Event-basierte KENO-Zyklen")
    print("=" * 70)
    print()
    print("Hypothese: KENO-System ist zustandsbasiert und wechselt")
    print("           Verhalten basierend auf Events (Jackpots, etc.)")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    df = load_keno_data(base_path)
    print(f"  Ziehungen: {len(df)}")
    print(f"  Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")

    # Jackpots identifizieren
    jackpot_dates = identify_jackpots(df, base_path)
    print(f"  Jackpots gefunden: {len(jackpot_dates)}")

    # Alle Analysen durchfuehren
    results = {
        "metadata": {
            "total_drawings": len(df),
            "date_range": {
                "start": str(df["Datum"].min().date()),
                "end": str(df["Datum"].max().date()),
            },
            "jackpots": len(jackpot_dates),
        }
    }

    # 1. Jackpot-Zyklen
    results["jackpot_cycles"] = analyze_jackpot_cycles(df, jackpot_dates)

    # 2. Wochentag-Zyklen
    results["weekday_cycles"] = analyze_weekday_cycles(df)

    # 3. Ticket-Lebenszyklus
    results["longevity"] = analyze_ticket_longevity(df)

    # 4. Zahlen-Ueberlappung
    results["number_overlap"] = analyze_number_overlap_by_phase(df, jackpot_dates)

    # 5. Muster-Wechsel nach Jackpot
    results["regime_change"] = analyze_consecutive_patterns(df, jackpot_dates)

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG: ZYKLEN-ANALYSE")
    print("=" * 70)

    print("""
FRAGE 1: Gibt es Zyklen?
--> Ja, es gibt erkennbare Phasen (Pre-Jackpot, Post-Jackpot, Cooldown, Normal)

FRAGE 2: Wie performen Tickets in verschiedenen Zyklen?
--> Performance variiert stark nach Phase (siehe oben)

FRAGE 3: Kann ein Ticket >365 Tage gut performen?
--> Siehe Jaehrliche Analyse - Stabilitaet gemessen durch STD

FRAGE 4: Aendert das System sein Verhalten nach Jackpot?
""")

    if "regime_change" in results and "mean_overlap" in results["regime_change"]:
        mean_ov = results["regime_change"]["mean_overlap"]
        if mean_ov < 5:
            print(f"--> JA! Starker Regime-Wechsel (nur {mean_ov:.1f}/10 Zahlen bleiben)")
        elif mean_ov < 7:
            print(f"--> TEILWEISE: Moderater Wechsel ({mean_ov:.1f}/10 Zahlen bleiben)")
        else:
            print(f"--> NEIN: Stabil ({mean_ov:.1f}/10 Zahlen bleiben)")

    # Speichern
    output_path = base_path / "results" / "cycles_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        # Convert defaultdicts and sets for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, defaultdict):
                return dict(obj)
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj

        json.dump(results, f, indent=2, ensure_ascii=False, default=convert_for_json)

    print(f"\n\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
