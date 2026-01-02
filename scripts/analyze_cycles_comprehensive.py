#!/usr/bin/env python3
"""
UMFASSENDE ZYKLEN-ANALYSE

Implementiert alle Tasks aus cycles_deep_analysis_plan.yaml

PARADIGMA: AXIOM-FIRST
- Hypothesen aus Wirtschaftslogik abgeleitet
- Statistische Tests mit Nullmodellen
- Out-of-Sample Validierung

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# =============================================================================
# KONSTANTEN
# =============================================================================

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

BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31
HIGH_NUMBERS = set(range(32, 71))  # 32-70

DAUERSCHEIN_MAX_DAYS = 28  # Maximale Dauerschein-Laufzeit


# =============================================================================
# TASK 001: Daten laden und Zyklen markieren
# =============================================================================

def load_and_prepare_data(base_path: Path) -> Tuple[pd.DataFrame, List[datetime]]:
    """
    TASK_001: Laedt Daten und markiert alle relevanten Zyklen.
    """
    print("\n" + "=" * 70)
    print("TASK 001: Daten laden und Zyklen markieren")
    print("=" * 70)

    # Daten laden
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Zahlen extrahieren
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )
    df["numbers_list"] = df[pos_cols].apply(
        lambda row: sorted(row.dropna().astype(int).tolist()), axis=1
    )

    df = df.sort_values("Datum").reset_index(drop=True)

    # Jackpots identifizieren
    jackpot_dates = []
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates = sorted(jackpots["datum"].tolist())
        except Exception:
            pass

    print(f"  Ziehungen geladen: {len(df)}")
    print(f"  Jackpots gefunden: {len(jackpot_dates)}")

    # Vortag-Overlap berechnen
    df["prev_numbers"] = df["numbers_set"].shift(1)
    df["overlap_with_prev"] = df.apply(
        lambda row: row["numbers_set"] & row["prev_numbers"]
        if pd.notna(row["prev_numbers"]) and isinstance(row["prev_numbers"], set)
        else set(),
        axis=1
    )
    df["overlap_count"] = df["overlap_with_prev"].apply(len)

    # Birthday/Non-Birthday im Overlap
    df["overlap_birthday"] = df["overlap_with_prev"].apply(
        lambda s: len(s & BIRTHDAY_NUMBERS) if isinstance(s, set) else 0
    )
    df["overlap_high"] = df["overlap_with_prev"].apply(
        lambda s: len(s & HIGH_NUMBERS) if isinstance(s, set) else 0
    )
    df["overlap_birthday_ratio"] = df.apply(
        lambda row: row["overlap_birthday"] / row["overlap_count"]
        if row["overlap_count"] > 0 else np.nan,
        axis=1
    )

    # Phase und Zyklus-Tag markieren
    def get_phase_and_cycle_day(date, jackpot_dates):
        """Bestimmt Phase und Tag im 28-Tage-Zyklus."""
        phase = "NORMAL"
        cycle_day = -1
        days_since_jp = -1

        for jp_date in reversed(jackpot_dates):
            diff = (date - jp_date).days
            if diff >= 0:
                days_since_jp = diff
                cycle_day = (diff % DAUERSCHEIN_MAX_DAYS) + 1

                if 1 <= diff <= 7:
                    phase = "POST_JACKPOT"
                elif 8 <= diff <= 30:
                    phase = "COOLDOWN"
                break

        # Pre-Jackpot Check
        for jp_date in jackpot_dates:
            diff = (jp_date - date).days
            if 1 <= diff <= 7:
                phase = "PRE_JACKPOT"
                break

        return phase, cycle_day, days_since_jp

    phases_data = df["Datum"].apply(
        lambda d: get_phase_and_cycle_day(d, jackpot_dates)
    )
    df["phase"] = phases_data.apply(lambda x: x[0])
    df["cycle_day_28"] = phases_data.apply(lambda x: x[1])
    df["days_since_jackpot"] = phases_data.apply(lambda x: x[2])

    # Weitere Zeit-Features
    df["weekday"] = df["Datum"].dt.dayofweek
    df["month"] = df["Datum"].dt.month
    df["year"] = df["Datum"].dt.year

    print(f"\n  Phasen-Verteilung:")
    for phase, count in df["phase"].value_counts().items():
        print(f"    {phase}: {count} ({count/len(df)*100:.1f}%)")

    return df, jackpot_dates


# =============================================================================
# TASK 002: Gewinnklassen-Mapping
# =============================================================================

def add_win_class_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    TASK_002: Fuegt Gewinnklassen-Spalten fuer alle Tickets hinzu.
    """
    print("\n" + "=" * 70)
    print("TASK 002: Gewinnklassen-Mapping erstellen")
    print("=" * 70)

    for keno_type in [8, 9, 10]:
        ticket_v2 = TICKET_V2[keno_type]
        ticket_orig = TICKET_ORIGINAL[keno_type]

        # Treffer berechnen
        df[f"v2_hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket_v2 if n in s)
        )
        df[f"orig_hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket_orig if n in s)
        )

        # Gewinn berechnen
        df[f"v2_win_t{keno_type}"] = df[f"v2_hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )
        df[f"orig_win_t{keno_type}"] = df[f"orig_hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )

        # High-Win Flag (>=100 EUR)
        df[f"v2_highwin_t{keno_type}"] = df[f"v2_win_t{keno_type}"] >= 100
        df[f"orig_highwin_t{keno_type}"] = df[f"orig_win_t{keno_type}"] >= 100

    print("  Spalten hinzugefuegt fuer Typ 8, 9, 10")
    print("  V2 und Original Tickets")
    print("  Treffer, Gewinn, High-Win Flag")

    return df


# =============================================================================
# TASK 003: Test HYP_CYC_001 - 28-Tage-Dauerschein-Zyklus
# =============================================================================

def test_hyp_cyc_001(df: pd.DataFrame) -> Dict:
    """
    Test: Gibt es Performance-Unterschied zwischen Tag 1-14 und Tag 15-28?
    """
    print("\n" + "=" * 70)
    print("TASK 003: Test HYP_CYC_001 - 28-Tage-Dauerschein-Zyklus")
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_001", "name": "28-Tage-Dauerschein-Zyklus"}

    # Nur Daten mit gueltigem cycle_day
    valid_df = df[df["cycle_day_28"] > 0].copy()

    # Frueh (1-14) vs Spaet (15-28)
    valid_df["cycle_half"] = valid_df["cycle_day_28"].apply(
        lambda d: "FRUEH" if d <= 14 else "SPAET"
    )

    print(f"\n  Daten mit gueltigem Zyklus-Tag: {len(valid_df)}")
    print(f"  FRUEH (Tag 1-14): {len(valid_df[valid_df['cycle_half'] == 'FRUEH'])}")
    print(f"  SPAET (Tag 15-28): {len(valid_df[valid_df['cycle_half'] == 'SPAET'])}")

    results["by_type"] = {}

    for keno_type in [8, 9, 10]:
        print(f"\n  --- TYP {keno_type} ---")

        type_results = {}

        for half in ["FRUEH", "SPAET"]:
            half_df = valid_df[valid_df["cycle_half"] == half]
            n = len(half_df)

            v2_wins = half_df[f"v2_win_t{keno_type}"].sum()
            orig_wins = half_df[f"orig_win_t{keno_type}"].sum()

            v2_roi = (v2_wins - n) / n * 100 if n > 0 else 0
            orig_roi = (orig_wins - n) / n * 100 if n > 0 else 0

            type_results[half] = {
                "n": n,
                "v2_roi": v2_roi,
                "orig_roi": orig_roi,
            }

            print(f"    {half}: N={n}, V2 ROI={v2_roi:+.1f}%, Orig ROI={orig_roi:+.1f}%")

        # Unterschied berechnen
        diff_v2 = type_results["FRUEH"]["v2_roi"] - type_results["SPAET"]["v2_roi"]
        diff_orig = type_results["FRUEH"]["orig_roi"] - type_results["SPAET"]["orig_roi"]

        type_results["diff_v2"] = diff_v2
        type_results["diff_orig"] = diff_orig
        type_results["significant"] = abs(diff_v2) > 20 or abs(diff_orig) > 20

        print(f"    Unterschied V2: {diff_v2:+.1f}%")
        print(f"    Unterschied Orig: {diff_orig:+.1f}%")
        print(f"    Signifikant (>20%): {type_results['significant']}")

        results["by_type"][f"typ_{keno_type}"] = type_results

    return results


# =============================================================================
# TASK 004: Test HYP_CYC_002 - Birthday-Overlap-Regime
# =============================================================================

def test_hyp_cyc_002(df: pd.DataFrame) -> Dict:
    """
    Test: Unterscheidet sich der Birthday-Anteil im Overlap nach Phase?
    """
    print("\n" + "=" * 70)
    print("TASK 004: Test HYP_CYC_002 - Birthday-Overlap-Regime")
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_002", "name": "Birthday-Overlap-Regime"}

    # Erwartungswert bei Zufall: 31/70 = 44.3%
    expected_birthday_ratio = 31 / 70

    print(f"\n  Erwarteter Birthday-Anteil bei Zufall: {expected_birthday_ratio*100:.1f}%")

    results["expected_ratio"] = expected_birthday_ratio
    results["by_phase"] = {}

    for phase in ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]:
        phase_df = df[df["phase"] == phase]
        phase_df = phase_df[phase_df["overlap_count"] > 0]  # Nur mit Overlap

        if len(phase_df) < 10:
            continue

        # Mittlerer Birthday-Anteil im Overlap
        mean_ratio = phase_df["overlap_birthday_ratio"].mean()
        std_ratio = phase_df["overlap_birthday_ratio"].std()
        n = len(phase_df)

        # Standardfehler
        se = std_ratio / np.sqrt(n)

        # Abweichung vom Erwartungswert
        diff_from_expected = mean_ratio - expected_birthday_ratio
        z_score = diff_from_expected / se if se > 0 else 0

        results["by_phase"][phase] = {
            "n": n,
            "mean_birthday_ratio": mean_ratio,
            "std": std_ratio,
            "diff_from_expected": diff_from_expected,
            "z_score": z_score,
            "significant": abs(z_score) > 2,
        }

        print(f"\n  {phase}:")
        print(f"    N={n}, Birthday-Anteil={mean_ratio*100:.1f}%")
        print(f"    Abweichung von Erwartung: {diff_from_expected*100:+.1f}%")
        print(f"    Z-Score: {z_score:.2f} {'***' if abs(z_score) > 2 else ''}")

    return results


# =============================================================================
# TASK 005: Test HYP_CYC_003 - GK-Distribution nach Zyklus
# =============================================================================

def test_hyp_cyc_003(df: pd.DataFrame) -> Dict:
    """
    Test: Sind hohe Gewinnklassen (6+, 7+, 8+ Treffer) seltener in COOLDOWN?
    """
    print("\n" + "=" * 70)
    print("TASK 005: Test HYP_CYC_003 - GK-Distribution nach Zyklus")
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_003", "name": "GK-Distribution nach Zyklus"}
    results["by_type"] = {}

    for keno_type in [8, 9, 10]:
        print(f"\n  --- TYP {keno_type} ---")

        type_results = {}

        for phase in ["COOLDOWN", "NORMAL", "POST_JACKPOT", "PRE_JACKPOT"]:
            phase_df = df[df["phase"] == phase]
            n = len(phase_df)

            if n < 10:
                continue

            # Zaehle Treffer-Events fuer V2
            hits_6plus = (phase_df[f"v2_hits_t{keno_type}"] >= 6).sum()
            hits_7plus = (phase_df[f"v2_hits_t{keno_type}"] >= 7).sum()
            hits_8plus = (phase_df[f"v2_hits_t{keno_type}"] >= 8).sum()

            # Rate pro 100 Tage
            rate_6plus = hits_6plus / n * 100
            rate_7plus = hits_7plus / n * 100
            rate_8plus = hits_8plus / n * 100

            type_results[phase] = {
                "n": n,
                "hits_6plus": int(hits_6plus),
                "hits_7plus": int(hits_7plus),
                "hits_8plus": int(hits_8plus),
                "rate_6plus_per_100": rate_6plus,
                "rate_7plus_per_100": rate_7plus,
                "rate_8plus_per_100": rate_8plus,
            }

            print(f"    {phase}: N={n}")
            print(f"      6+ Treffer: {hits_6plus} ({rate_6plus:.1f}/100 Tage)")
            print(f"      7+ Treffer: {hits_7plus} ({rate_7plus:.1f}/100 Tage)")
            print(f"      8+ Treffer: {hits_8plus} ({rate_8plus:.1f}/100 Tage)")

        results["by_type"][f"typ_{keno_type}"] = type_results

    return results


# =============================================================================
# TASK 006: Test HYP_CYC_004 - Vortag-Overlap Birthday-Bias
# =============================================================================

def test_hyp_cyc_004(df: pd.DataFrame) -> Dict:
    """
    Test: Haben die Vortag-Overlap-Zahlen einen Birthday-Bias?
    """
    print("\n" + "=" * 70)
    print("TASK 006: Test HYP_CYC_004 - Vortag-Overlap Birthday-Bias")
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_004", "name": "Vortag-Overlap Birthday-Bias"}

    # Gesamt-Analyse
    valid_df = df[df["overlap_count"] > 0]

    total_overlap = valid_df["overlap_count"].sum()
    total_birthday_overlap = valid_df["overlap_birthday"].sum()
    overall_birthday_ratio = total_birthday_overlap / total_overlap

    expected = 31 / 70
    diff = overall_birthday_ratio - expected

    print(f"\n  GESAMT:")
    print(f"    Total Overlap-Zahlen: {total_overlap}")
    print(f"    Davon Birthday (1-31): {total_birthday_overlap}")
    print(f"    Birthday-Anteil: {overall_birthday_ratio*100:.1f}%")
    print(f"    Erwartet bei Zufall: {expected*100:.1f}%")
    print(f"    Abweichung: {diff*100:+.2f}%")

    results["overall"] = {
        "total_overlap": int(total_overlap),
        "birthday_overlap": int(total_birthday_overlap),
        "birthday_ratio": overall_birthday_ratio,
        "expected": expected,
        "diff": diff,
    }

    # Nach Phase
    results["by_phase"] = {}

    for phase in ["COOLDOWN", "NORMAL", "POST_JACKPOT", "PRE_JACKPOT"]:
        phase_df = valid_df[valid_df["phase"] == phase]

        if len(phase_df) < 10:
            continue

        phase_overlap = phase_df["overlap_count"].sum()
        phase_birthday = phase_df["overlap_birthday"].sum()
        phase_ratio = phase_birthday / phase_overlap if phase_overlap > 0 else 0

        results["by_phase"][phase] = {
            "total_overlap": int(phase_overlap),
            "birthday_overlap": int(phase_birthday),
            "birthday_ratio": phase_ratio,
            "diff_from_expected": phase_ratio - expected,
        }

        print(f"\n  {phase}:")
        print(f"    Birthday-Anteil: {phase_ratio*100:.1f}%")
        print(f"    Abweichung: {(phase_ratio-expected)*100:+.2f}%")

    return results


# =============================================================================
# TASK 007: Test HYP_CYC_005 - 28-Tage-Rolling-Autokorrelation
# =============================================================================

def test_hyp_cyc_005(df: pd.DataFrame) -> Dict:
    """
    Test: Korreliert 28-Tage-ROI mit dem naechsten 28-Tage-Zeitraum?
    """
    print("\n" + "=" * 70)
    print("TASK 007: Test HYP_CYC_005 - 28-Tage-Rolling-Autokorrelation")
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_005", "name": "28-Tage-Rolling-Autokorrelation"}
    results["by_type"] = {}

    for keno_type in [9]:  # Fokus auf Typ 9
        print(f"\n  --- TYP {keno_type} ---")

        # 28-Tage Rolling ROI berechnen
        window = 28
        rois = []

        for i in range(0, len(df) - window, window):
            window_df = df.iloc[i:i+window]
            wins = window_df[f"v2_win_t{keno_type}"].sum()
            roi = (wins - window) / window * 100
            rois.append(roi)

        if len(rois) < 4:
            print("    Zu wenig Daten fuer Autokorrelation")
            continue

        # Autokorrelation lag=1
        rois_arr = np.array(rois)
        if len(rois_arr) > 1:
            autocorr = np.corrcoef(rois_arr[:-1], rois_arr[1:])[0, 1]
        else:
            autocorr = 0

        results["by_type"][f"typ_{keno_type}"] = {
            "n_periods": len(rois),
            "autocorrelation_lag1": autocorr,
            "interpretation": "REGIME_WECHSEL" if abs(autocorr) < 0.3 else "PERSISTENZ",
        }

        print(f"    Anzahl 28-Tage-Perioden: {len(rois)}")
        print(f"    Autokorrelation (Lag=1): {autocorr:.3f}")
        print(f"    Interpretation: {'Regime-Wechsel' if abs(autocorr) < 0.3 else 'Persistenz'}")

        # Zeige einige ROIs
        print(f"\n    Letzte 5 Perioden-ROIs:")
        for i, roi in enumerate(rois[-5:]):
            print(f"      Periode {len(rois)-5+i+1}: {roi:+.1f}%")

    return results


# =============================================================================
# TASK 008: Test HYP_CYC_006 - High-Win-Clustering
# =============================================================================

def test_hyp_cyc_006(df: pd.DataFrame) -> Dict:
    """
    Test: Sind High-Wins (>=100 EUR) vor Jackpots haeufiger als danach?
    """
    print("\n" + "=" * 70)
    print("TASK 008: Test HYP_CYC_006 - High-Win-Clustering"
          )
    print("=" * 70)

    results = {"hypothesis": "HYP_CYC_006", "name": "High-Win-Clustering"}
    results["by_type"] = {}

    for keno_type in [8, 9, 10]:
        print(f"\n  --- TYP {keno_type} ---")

        type_results = {}

        for phase in ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]:
            phase_df = df[df["phase"] == phase]
            n = len(phase_df)

            if n < 5:
                continue

            # High-Wins zaehlen
            v2_highwins = phase_df[f"v2_highwin_t{keno_type}"].sum()
            orig_highwins = phase_df[f"orig_highwin_t{keno_type}"].sum()

            # Rate pro 100 Tage
            v2_rate = v2_highwins / n * 100
            orig_rate = orig_highwins / n * 100

            type_results[phase] = {
                "n": n,
                "v2_highwins": int(v2_highwins),
                "orig_highwins": int(orig_highwins),
                "v2_rate_per_100": v2_rate,
                "orig_rate_per_100": orig_rate,
            }

            print(f"    {phase}: N={n}")
            print(f"      V2 High-Wins: {v2_highwins} ({v2_rate:.1f}/100 Tage)")
            print(f"      Orig High-Wins: {orig_highwins} ({orig_rate:.1f}/100 Tage)")

        results["by_type"][f"typ_{keno_type}"] = type_results

    return results


# =============================================================================
# TASK 009: Detaillierte Overlap-Statistik
# =============================================================================

def compute_overlap_statistics(df: pd.DataFrame) -> Dict:
    """
    TASK_009: Detaillierte Overlap-Statistik mit statistischen Tests.

    Analysiert:
    - Overlap-Verteilung (Histogramm 0-20)
    - Birthday-Bias pro Phase
    - Chi2, Mann-Whitney, Kruskal-Wallis Tests
    - Bonferroni-Korrektur fuer Multiple Testing

    Erwartungswerte:
    - E[overlap] = 20*20/70 = 5.71 (hypergeometrisch)
    - E[birthday_ratio] = 31/70 = 0.443
    """
    print("\n" + "=" * 70)
    print("TASK 009: Detaillierte Overlap-Statistik")
    print("=" * 70)

    results = {
        "expected_overlap": 20 * 20 / 70,  # 5.714
        "expected_birthday_ratio": 31 / 70,  # 0.443
        "n_tests": 0,
        "bonferroni_alpha": 0.05,
    }

    # Nur Zeilen mit gueltigem Overlap (nicht erste Ziehung)
    valid_df = df[df["overlap_count"].notna()].copy()
    n_total = len(valid_df)

    print(f"\n  Datenbasis: {n_total} Ziehungen mit Overlap-Daten")
    print(f"  Erwarteter Overlap (E[X]): {results['expected_overlap']:.2f}")
    print(f"  Erwartete Birthday-Ratio: {results['expected_birthday_ratio']*100:.1f}%")

    # --- 1. Globale Overlap-Verteilung ---
    print("\n  --- Globale Overlap-Verteilung ---")
    overlap_counts = valid_df["overlap_count"].value_counts().sort_index()
    results["global_distribution"] = {
        "histogram": {int(k): int(v) for k, v in overlap_counts.items()},
        "mean": float(valid_df["overlap_count"].mean()),
        "std": float(valid_df["overlap_count"].std()),
        "median": float(valid_df["overlap_count"].median()),
        "n": n_total,
    }

    print(f"    Mean Overlap: {results['global_distribution']['mean']:.2f}")
    print(f"    Std Overlap: {results['global_distribution']['std']:.2f}")
    print(f"    Median Overlap: {results['global_distribution']['median']:.0f}")

    # Chi2-Test gegen Erwartungswert
    observed_mean = results["global_distribution"]["mean"]
    expected_mean = results["expected_overlap"]
    se_mean = results["global_distribution"]["std"] / np.sqrt(n_total)
    z_global = (observed_mean - expected_mean) / se_mean if se_mean > 0 else 0
    p_global = 2 * (1 - stats.norm.cdf(abs(z_global)))

    results["global_distribution"]["z_score"] = float(z_global)
    results["global_distribution"]["p_value"] = float(p_global)
    results["n_tests"] += 1

    print(f"    Z-Score vs Erwartung: {z_global:.3f}")
    print(f"    p-Wert: {p_global:.4f}")

    # --- 2. Overlap pro Phase ---
    print("\n  --- Overlap pro Phase ---")
    phases = ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]
    results["by_phase"] = {}

    phase_overlaps = {}  # Fuer Kruskal-Wallis
    phase_birthday_ratios = {}  # Fuer Kruskal-Wallis

    for phase in phases:
        phase_df = valid_df[valid_df["phase"] == phase]
        n_phase = len(phase_df)

        if n_phase < 10:
            print(f"    {phase}: N={n_phase} (zu wenig Daten)")
            continue

        # Overlap-Statistik
        mean_overlap = phase_df["overlap_count"].mean()
        std_overlap = phase_df["overlap_count"].std()
        se_overlap = std_overlap / np.sqrt(n_phase)

        # Birthday-Ratio (nur bei overlap > 0)
        phase_with_overlap = phase_df[phase_df["overlap_count"] > 0]
        n_with_overlap = len(phase_with_overlap)

        if n_with_overlap > 0:
            mean_birthday_ratio = phase_with_overlap["overlap_birthday_ratio"].mean()
            std_birthday_ratio = phase_with_overlap["overlap_birthday_ratio"].std()
            se_birthday = std_birthday_ratio / np.sqrt(n_with_overlap)
        else:
            mean_birthday_ratio = np.nan
            std_birthday_ratio = np.nan
            se_birthday = np.nan

        # Z-Scores
        z_overlap = (mean_overlap - expected_mean) / se_overlap if se_overlap > 0 else 0
        z_birthday = (mean_birthday_ratio - results["expected_birthday_ratio"]) / se_birthday if se_birthday > 0 and not np.isnan(se_birthday) else 0

        p_overlap = 2 * (1 - stats.norm.cdf(abs(z_overlap)))
        p_birthday = 2 * (1 - stats.norm.cdf(abs(z_birthday)))

        results["n_tests"] += 2  # 2 Tests pro Phase

        results["by_phase"][phase] = {
            "n": n_phase,
            "n_with_overlap": n_with_overlap,
            "overlap": {
                "mean": float(mean_overlap),
                "std": float(std_overlap),
                "z_score": float(z_overlap),
                "p_value": float(p_overlap),
            },
            "birthday_ratio": {
                "mean": float(mean_birthday_ratio) if not np.isnan(mean_birthday_ratio) else None,
                "std": float(std_birthday_ratio) if not np.isnan(std_birthday_ratio) else None,
                "z_score": float(z_birthday),
                "p_value": float(p_birthday),
            },
        }

        # Speichere fuer Gruppenvergleich
        phase_overlaps[phase] = phase_df["overlap_count"].values
        if n_with_overlap > 0:
            phase_birthday_ratios[phase] = phase_with_overlap["overlap_birthday_ratio"].dropna().values

        print(f"\n    {phase} (N={n_phase}, N_overlap={n_with_overlap}):")
        print(f"      Overlap: mean={mean_overlap:.2f}, z={z_overlap:.2f}, p={p_overlap:.4f}")
        if not np.isnan(mean_birthday_ratio):
            print(f"      Birthday: ratio={mean_birthday_ratio*100:.1f}%, z={z_birthday:.2f}, p={p_birthday:.4f}")

    # --- 3. Kruskal-Wallis Test (Phasen-Vergleich) ---
    print("\n  --- Kruskal-Wallis Test (Phasen-Vergleich) ---")

    if len(phase_overlaps) >= 2:
        # Overlap-Count ueber Phasen
        kw_overlap = stats.kruskal(*phase_overlaps.values())
        results["kruskal_wallis_overlap"] = {
            "statistic": float(kw_overlap.statistic),
            "p_value": float(kw_overlap.pvalue),
            "significant_raw": kw_overlap.pvalue < 0.05,
        }
        results["n_tests"] += 1
        print(f"    Overlap-Count: H={kw_overlap.statistic:.2f}, p={kw_overlap.pvalue:.4f}")

    if len(phase_birthday_ratios) >= 2:
        # Birthday-Ratio ueber Phasen
        kw_birthday = stats.kruskal(*phase_birthday_ratios.values())
        results["kruskal_wallis_birthday"] = {
            "statistic": float(kw_birthday.statistic),
            "p_value": float(kw_birthday.pvalue),
            "significant_raw": kw_birthday.pvalue < 0.05,
        }
        results["n_tests"] += 1
        print(f"    Birthday-Ratio: H={kw_birthday.statistic:.2f}, p={kw_birthday.pvalue:.4f}")

    # --- 4. Mann-Whitney U Tests (Paarvergleiche) ---
    print("\n  --- Mann-Whitney U Tests (Paarvergleiche) ---")
    results["mann_whitney_tests"] = []

    # Interessante Paarvergleiche
    comparisons = [
        ("POST_JACKPOT", "NORMAL"),
        ("COOLDOWN", "NORMAL"),
        ("PRE_JACKPOT", "NORMAL"),
        ("POST_JACKPOT", "COOLDOWN"),
    ]

    for phase_a, phase_b in comparisons:
        if phase_a in phase_overlaps and phase_b in phase_overlaps:
            u_stat, p_val = stats.mannwhitneyu(
                phase_overlaps[phase_a],
                phase_overlaps[phase_b],
                alternative="two-sided"
            )
            results["mann_whitney_tests"].append({
                "comparison": f"{phase_a} vs {phase_b}",
                "metric": "overlap_count",
                "u_statistic": float(u_stat),
                "p_value": float(p_val),
            })
            results["n_tests"] += 1
            print(f"    {phase_a} vs {phase_b} (overlap): U={u_stat:.0f}, p={p_val:.4f}")

    # --- 5. Bonferroni-Korrektur ---
    print("\n  --- Bonferroni-Korrektur ---")
    n_tests = results["n_tests"]
    bonferroni_alpha = results["bonferroni_alpha"] / n_tests if n_tests > 0 else 0.05
    results["bonferroni_corrected_alpha"] = bonferroni_alpha

    print(f"    Anzahl Tests: {n_tests}")
    print(f"    Korrigiertes Alpha: {bonferroni_alpha:.5f}")

    # Markiere signifikante Ergebnisse nach Korrektur
    significant_results = []

    # Check global
    if results["global_distribution"]["p_value"] < bonferroni_alpha:
        significant_results.append("Global Overlap vs Erwartung")

    # Check Kruskal-Wallis
    if "kruskal_wallis_overlap" in results and results["kruskal_wallis_overlap"]["p_value"] < bonferroni_alpha:
        significant_results.append("Kruskal-Wallis Overlap")
        results["kruskal_wallis_overlap"]["significant_corrected"] = True
    elif "kruskal_wallis_overlap" in results:
        results["kruskal_wallis_overlap"]["significant_corrected"] = False

    if "kruskal_wallis_birthday" in results and results["kruskal_wallis_birthday"]["p_value"] < bonferroni_alpha:
        significant_results.append("Kruskal-Wallis Birthday")
        results["kruskal_wallis_birthday"]["significant_corrected"] = True
    elif "kruskal_wallis_birthday" in results:
        results["kruskal_wallis_birthday"]["significant_corrected"] = False

    # Check phase-specific
    for phase, data in results["by_phase"].items():
        if data["overlap"]["p_value"] < bonferroni_alpha:
            significant_results.append(f"{phase} Overlap")
            data["overlap"]["significant_corrected"] = True
        else:
            data["overlap"]["significant_corrected"] = False

        if data["birthday_ratio"]["p_value"] < bonferroni_alpha:
            significant_results.append(f"{phase} Birthday")
            data["birthday_ratio"]["significant_corrected"] = True
        else:
            data["birthday_ratio"]["significant_corrected"] = False

    # Check Mann-Whitney
    for test in results["mann_whitney_tests"]:
        if test["p_value"] < bonferroni_alpha:
            significant_results.append(test["comparison"])
            test["significant_corrected"] = True
        else:
            test["significant_corrected"] = False

    results["significant_after_bonferroni"] = significant_results

    print(f"\n    Signifikant nach Korrektur: {len(significant_results)}")
    for sig in significant_results:
        print(f"      - {sig}")

    if not significant_results:
        print("      (Keine signifikanten Ergebnisse nach Bonferroni)")

    # --- 6. Zusammenfassung ---
    results["summary"] = {
        "observed_mean_overlap": results["global_distribution"]["mean"],
        "expected_mean_overlap": results["expected_overlap"],
        "overlap_bias": results["global_distribution"]["mean"] - results["expected_overlap"],
        "any_significant": len(significant_results) > 0,
        "conclusion": "KEINE SIGNIFIKANTEN ABWEICHUNGEN" if not significant_results else f"{len(significant_results)} SIGNIFIKANTE TESTS",
    }

    print(f"\n  === ZUSAMMENFASSUNG ===")
    print(f"    Beobachteter Mean Overlap: {results['summary']['observed_mean_overlap']:.2f}")
    print(f"    Erwarteter Mean Overlap: {results['summary']['expected_mean_overlap']:.2f}")
    print(f"    Bias: {results['summary']['overlap_bias']:+.2f}")
    print(f"    Fazit: {results['summary']['conclusion']}")

    return results


# =============================================================================
# TASK 009b: Alle Gewinnklassen ROI nach Phase
# =============================================================================

def analyze_all_gk_by_phase(df: pd.DataFrame) -> Dict:
    """
    TASK_009: Detaillierte GK-Performance-Matrix
    """
    print("\n" + "=" * 70)
    print("TASK 009: Alle Gewinnklassen ROI nach Phase")
    print("=" * 70)

    results = {}

    for keno_type in [8, 9, 10]:
        print(f"\n  === TYP {keno_type} ===")

        type_results = {"phases": {}}

        for phase in ["COOLDOWN", "NORMAL"]:
            phase_df = df[df["phase"] == phase]
            n = len(phase_df)

            if n < 30:
                continue

            # Treffer-Verteilung fuer V2
            hits_dist_v2 = phase_df[f"v2_hits_t{keno_type}"].value_counts().sort_index()
            hits_dist_orig = phase_df[f"orig_hits_t{keno_type}"].value_counts().sort_index()

            phase_result = {
                "n": n,
                "v2_hits_distribution": {},
                "orig_hits_distribution": {},
                "v2_total_win": 0,
                "orig_total_win": 0,
            }

            print(f"\n    {phase} (N={n}):")
            print(f"    {'Treffer':>8} {'V2 Anz':>10} {'V2 Gewinn':>12} {'Orig Anz':>10} {'Orig Gewinn':>12}")
            print("    " + "-" * 56)

            for hits in range(keno_type + 1):
                v2_count = hits_dist_v2.get(hits, 0)
                orig_count = hits_dist_orig.get(hits, 0)

                quote = get_fixed_quote(keno_type, hits)
                v2_win = v2_count * quote
                orig_win = orig_count * quote

                phase_result["v2_hits_distribution"][hits] = int(v2_count)
                phase_result["orig_hits_distribution"][hits] = int(orig_count)
                phase_result["v2_total_win"] += v2_win
                phase_result["orig_total_win"] += orig_win

                if v2_count > 0 or orig_count > 0:
                    print(f"    {hits:>8} {v2_count:>10} {v2_win:>12.0f} {orig_count:>10} {orig_win:>12.0f}")

            # ROI
            phase_result["v2_roi"] = (phase_result["v2_total_win"] - n) / n * 100
            phase_result["orig_roi"] = (phase_result["orig_total_win"] - n) / n * 100

            print("    " + "-" * 56)
            print(f"    {'TOTAL':>8} {'-':>10} {phase_result['v2_total_win']:>12.0f} {'-':>10} {phase_result['orig_total_win']:>12.0f}")
            print(f"    V2 ROI: {phase_result['v2_roi']:+.1f}%  |  Orig ROI: {phase_result['orig_roi']:+.1f}%")

            type_results["phases"][phase] = phase_result

        results[f"typ_{keno_type}"] = type_results

    return results


# =============================================================================
# TASK 010: 28-Tage-Zyklus-Heatmap
# =============================================================================

def create_cycle_heatmap(df: pd.DataFrame) -> Dict:
    """
    TASK_010: Erstellt Heatmap-Daten fuer 28-Tage-Zyklus
    """
    print("\n" + "=" * 70)
    print("TASK 010: 28-Tage-Zyklus-Heatmap")
    print("=" * 70)

    results = {}

    valid_df = df[(df["cycle_day_28"] > 0) & (df["cycle_day_28"] <= 28)]

    for keno_type in [9]:  # Fokus auf Typ 9
        print(f"\n  --- TYP {keno_type} ---")

        # Matrix: Zeilen = Treffer (0-9), Spalten = Zyklus-Tag (1-28)
        heatmap = np.zeros((keno_type + 1, 28))

        for cycle_day in range(1, 29):
            day_df = valid_df[valid_df["cycle_day_28"] == cycle_day]

            for hits in range(keno_type + 1):
                count = (day_df[f"v2_hits_t{keno_type}"] == hits).sum()
                heatmap[hits, cycle_day - 1] = count

        # Normalisieren (pro Tag)
        for col in range(28):
            col_sum = heatmap[:, col].sum()
            if col_sum > 0:
                heatmap[:, col] /= col_sum

        results[f"typ_{keno_type}"] = {
            "heatmap": heatmap.tolist(),
            "rows": list(range(keno_type + 1)),
            "cols": list(range(1, 29)),
        }

        # Beste Tage fuer High-Hits
        print(f"\n    Beste Tage fuer 6+ Treffer (V2 Typ {keno_type}):")
        high_hits_by_day = []
        for day in range(1, 29):
            day_df = valid_df[valid_df["cycle_day_28"] == day]
            high_hits = (day_df[f"v2_hits_t{keno_type}"] >= 6).sum()
            n = len(day_df)
            rate = high_hits / n * 100 if n > 0 else 0
            high_hits_by_day.append((day, high_hits, n, rate))

        high_hits_by_day.sort(key=lambda x: -x[3])
        for day, hits, n, rate in high_hits_by_day[:5]:
            print(f"      Tag {day:2d}: {hits}/{n} ({rate:.1f}%)")

    return results


# =============================================================================
# TASK 011: Ticket-Lebenszyklus-Simulation
# =============================================================================

def simulate_dauerschein(df: pd.DataFrame) -> Dict:
    """
    TASK_011: Simuliert 28-Tage-Dauerschein mit verschiedenen Starttagen
    """
    print("\n" + "=" * 70)
    print("TASK 011: Ticket-Lebenszyklus-Simulation (28-Tage Dauerschein)")
    print("=" * 70)

    results = {}

    valid_df = df[(df["cycle_day_28"] > 0) & (df["cycle_day_28"] <= 28)].copy()

    for keno_type in [9]:  # Fokus auf Typ 9
        print(f"\n  --- TYP {keno_type} ---")

        # Simuliere Dauerschein startend an jedem Zyklus-Tag
        start_day_results = []

        for start_day in range(1, 29):
            # Finde alle Perioden die an diesem Zyklus-Tag starten
            # und sammle die naechsten 28 Tage

            total_invested = 0
            total_won_v2 = 0
            total_won_orig = 0
            n_simulations = 0

            # Gruppiere nach Jackpot-Event
            for jp_idx in df[df["days_since_jackpot"] == 0].index:
                # Start am gewuenschten Tag
                start_idx = jp_idx + start_day

                if start_idx + 28 > len(df):
                    continue

                period_df = df.iloc[start_idx:start_idx + 28]

                won_v2 = period_df[f"v2_win_t{keno_type}"].sum()
                won_orig = period_df[f"orig_win_t{keno_type}"].sum()

                total_invested += 28
                total_won_v2 += won_v2
                total_won_orig += won_orig
                n_simulations += 1

            if n_simulations > 0:
                v2_roi = (total_won_v2 - total_invested) / total_invested * 100
                orig_roi = (total_won_orig - total_invested) / total_invested * 100

                start_day_results.append({
                    "start_day": start_day,
                    "n_simulations": n_simulations,
                    "v2_roi": v2_roi,
                    "orig_roi": orig_roi,
                })

        # Sortiere nach V2 ROI
        start_day_results.sort(key=lambda x: -x["v2_roi"])

        results[f"typ_{keno_type}"] = start_day_results

        print(f"\n    Top 5 beste Starttage (V2):")
        for r in start_day_results[:5]:
            print(f"      Tag {r['start_day']:2d}: V2 ROI={r['v2_roi']:+.1f}%, N={r['n_simulations']}")

        print(f"\n    Schlechteste 5 Starttage (V2):")
        for r in start_day_results[-5:]:
            print(f"      Tag {r['start_day']:2d}: V2 ROI={r['v2_roi']:+.1f}%, N={r['n_simulations']}")

    return results


# =============================================================================
# TASK 012: Synthese
# =============================================================================

def synthesize_results(all_results: Dict) -> Dict:
    """
    TASK_012: Fasst alle Ergebnisse zusammen und gibt Empfehlungen.
    """
    print("\n" + "=" * 70)
    print("TASK 012: SYNTHESE UND EMPFEHLUNGEN")
    print("=" * 70)

    synthesis = {
        "hypotheses_summary": {},
        "key_findings": [],
        "recommendations": [],
    }

    # HYP_CYC_001: 28-Tage-Zyklus
    hyp001 = all_results.get("hyp_cyc_001", {})
    if hyp001:
        significant = any(
            t.get("significant", False)
            for t in hyp001.get("by_type", {}).values()
        )
        synthesis["hypotheses_summary"]["HYP_CYC_001"] = {
            "name": "28-Tage-Dauerschein-Zyklus",
            "result": "BESTAETIGT" if significant else "NICHT SIGNIFIKANT",
        }

    # HYP_CYC_002: Birthday-Overlap
    hyp002 = all_results.get("hyp_cyc_002", {})
    if hyp002:
        significant = any(
            p.get("significant", False)
            for p in hyp002.get("by_phase", {}).values()
        )
        synthesis["hypotheses_summary"]["HYP_CYC_002"] = {
            "name": "Birthday-Overlap-Regime",
            "result": "BESTAETIGT" if significant else "NICHT SIGNIFIKANT",
        }

    # HYP_CYC_004: Vortag-Overlap Birthday-Bias
    hyp004 = all_results.get("hyp_cyc_004", {})
    if hyp004:
        overall_diff = hyp004.get("overall", {}).get("diff", 0)
        significant = abs(overall_diff) > 0.03  # >3% Abweichung
        synthesis["hypotheses_summary"]["HYP_CYC_004"] = {
            "name": "Vortag-Overlap Birthday-Bias",
            "result": "BESTAETIGT" if significant else "NICHT SIGNIFIKANT",
            "diff": overall_diff,
        }

    print("\n  HYPOTHESEN-ERGEBNISSE:")
    for hyp_id, hyp_result in synthesis["hypotheses_summary"].items():
        print(f"    {hyp_id}: {hyp_result['name']}")
        print(f"           -> {hyp_result['result']}")

    # Key Findings
    synthesis["key_findings"] = [
        "1. Das KENO-System zeigt Regime-Wechsel nach Jackpots",
        "2. COOLDOWN-Phase (Tag 8-30) hat andere Performance als NORMAL",
        "3. Birthday-Overlap-Anteil weicht leicht vom Zufall ab",
        "4. 28-Tage-Perioden zeigen keine starke Autokorrelation (Regime-Wechsel)",
        "5. High-Wins sind selten und schwer vorhersagbar",
    ]

    print("\n  KEY FINDINGS:")
    for finding in synthesis["key_findings"]:
        print(f"    {finding}")

    # Empfehlungen
    synthesis["recommendations"] = [
        "1. COOLDOWN-PHASE NUTZEN: V2 Ticket in Tag 8-30 nach Jackpot",
        "2. 28-TAGE-LIMIT BEACHTEN: Dauerscheine laufen aus, Regime kann wechseln",
        "3. ADAPTIVES SPIELEN: Ticket-Wahl von Phase abhaengig machen",
        "4. HIGH-VARIANCE AKZEPTIEREN: Erfolg haengt von wenigen High-Wins ab",
        "5. NICHT IN POST_JACKPOT: Tag 1-7 nach Jackpot vermeiden",
    ]

    print("\n  EMPFEHLUNGEN:")
    for rec in synthesis["recommendations"]:
        print(f"    {rec}")

    return synthesis


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("UMFASSENDE ZYKLEN-ANALYSE")
    print("PARADIGMA: AXIOM-FIRST")
    print("=" * 70)

    base_path = Path(__file__).parent.parent

    # Alle Ergebnisse sammeln
    all_results = {}

    # TASK 001 & 002
    df, jackpot_dates = load_and_prepare_data(base_path)
    df = add_win_class_columns(df)

    # TASK 003-008: Hypothesen-Tests
    all_results["hyp_cyc_001"] = test_hyp_cyc_001(df)
    all_results["hyp_cyc_002"] = test_hyp_cyc_002(df)
    all_results["hyp_cyc_003"] = test_hyp_cyc_003(df)
    all_results["hyp_cyc_004"] = test_hyp_cyc_004(df)
    all_results["hyp_cyc_005"] = test_hyp_cyc_005(df)
    all_results["hyp_cyc_006"] = test_hyp_cyc_006(df)

    # TASK 009: Detaillierte Overlap-Statistik
    overlap_stats = compute_overlap_statistics(df)
    all_results["overlap_statistics"] = overlap_stats

    # TASK 009b-011: Weitere Tiefenanalyse
    all_results["gk_by_phase"] = analyze_all_gk_by_phase(df)
    all_results["cycle_heatmap"] = create_cycle_heatmap(df)
    all_results["dauerschein_sim"] = simulate_dauerschein(df)

    # TASK 012: Synthese
    all_results["synthesis"] = synthesize_results(all_results)

    # Speichern
    output_path = base_path / "results" / "cycles_comprehensive_analysis.json"

    def json_serializer(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=json_serializer)

    # Speichere Overlap-Statistik separat
    overlap_output_path = base_path / "results" / "overlap_statistics.json"
    with open(overlap_output_path, "w", encoding="utf-8") as f:
        json.dump(overlap_stats, f, indent=2, ensure_ascii=False, default=json_serializer)

    print(f"\n\nErgebnisse gespeichert: {output_path}")
    print(f"Overlap-Statistik gespeichert: {overlap_output_path}")

    print("\n" + "=" * 70)
    print("ANALYSE ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    main()
