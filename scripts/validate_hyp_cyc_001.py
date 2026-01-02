#!/usr/bin/env python3
"""
AXIOM-FIRST VALIDIERUNG: HYP_CYC_001 (28-Tage-Zyklus FRUEH/SPAET)

Implementiert:
1. Train/Test Split (2022-2024 Train, 2025 Test)
2. Frozen Rules: FRUEH (Tag 1-14) vs SPAET (Tag 15-28)
3. Permutationstest (1000 Iterationen)
4. Out-of-Sample Validierung 2025

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# =============================================================================
# KONSTANTEN (FROZEN RULES - aus Training abgeleitet)
# =============================================================================

TICKET_V2 = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

DAUERSCHEIN_MAX_DAYS = 28  # Maximale Dauerschein-Laufzeit


# =============================================================================
# DATEN LADEN
# =============================================================================

def load_data(base_path: Path) -> Tuple[pd.DataFrame, List[datetime]]:
    """Laedt KENO-Daten und Jackpot-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Zahlen extrahieren
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
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

    return df, jackpot_dates


def add_cycle_info(df: pd.DataFrame, jackpot_dates: List[datetime]) -> pd.DataFrame:
    """
    Fuegt Zyklus-Informationen hinzu.

    Verwendet 28-Tage-Zyklus basierend auf:
    1. Jackpot-Daten (falls vorhanden)
    2. Fallback: 28-Tage-Zyklus ab Jahresbeginn (fuer historische Daten)
    """
    # Konvertiere jackpot_dates zu Set fuer schnellen Lookup
    jp_set = set(pd.to_datetime(d).date() for d in jackpot_dates) if jackpot_dates else set()

    def get_cycle_day(row_date, all_dates_df):
        """Bestimmt Tag im 28-Tage-Zyklus."""
        date = row_date.date() if hasattr(row_date, 'date') else row_date

        # Suche letzten Jackpot vor diesem Datum
        for jp in reversed(jackpot_dates):
            jp_date = pd.to_datetime(jp).date() if hasattr(jp, 'date') else jp
            diff = (date - jp_date).days
            if diff >= 0:
                return (diff % DAUERSCHEIN_MAX_DAYS) + 1

        # Fallback: 28-Tage-Zyklus ab Jahresbeginn des Datums
        year_start = pd.Timestamp(year=date.year, month=1, day=1).date()
        diff = (date - year_start).days
        return (diff % DAUERSCHEIN_MAX_DAYS) + 1

    df["cycle_day_28"] = df["Datum"].apply(lambda d: get_cycle_day(d, df))
    df["cycle_half"] = df["cycle_day_28"].apply(
        lambda d: "FRUEH" if 1 <= d <= 14 else ("SPAET" if 15 <= d <= 28 else "UNKNOWN")
    )
    df["year"] = df["Datum"].dt.year

    return df


def add_hits_and_wins(df: pd.DataFrame) -> pd.DataFrame:
    """Fuegt Treffer und Gewinn-Spalten hinzu."""
    for keno_type in [8, 9, 10]:
        ticket = TICKET_V2[keno_type]
        df[f"v2_hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket if n in s)
        )
        df[f"v2_win_t{keno_type}"] = df[f"v2_hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )
    return df


# =============================================================================
# ROI BERECHNUNG
# =============================================================================

def calculate_roi(df: pd.DataFrame, keno_type: int) -> float:
    """Berechnet ROI fuer gegebenen DataFrame."""
    n = len(df)
    if n == 0:
        return np.nan
    wins = df[f"v2_win_t{keno_type}"].sum()
    roi = (wins - n) / n * 100
    return roi


def calculate_roi_by_half(df: pd.DataFrame, keno_type: int) -> Dict:
    """Berechnet ROI fuer FRUEH und SPAET."""
    valid_df = df[df["cycle_half"].isin(["FRUEH", "SPAET"])]

    frueh_df = valid_df[valid_df["cycle_half"] == "FRUEH"]
    spaet_df = valid_df[valid_df["cycle_half"] == "SPAET"]

    frueh_roi = calculate_roi(frueh_df, keno_type)
    spaet_roi = calculate_roi(spaet_df, keno_type)
    diff = frueh_roi - spaet_roi if not np.isnan(frueh_roi) and not np.isnan(spaet_roi) else np.nan

    return {
        "frueh": {"n": len(frueh_df), "roi": frueh_roi},
        "spaet": {"n": len(spaet_df), "roi": spaet_roi},
        "diff": diff,
    }


# =============================================================================
# PERMUTATIONSTEST
# =============================================================================

def permutation_test(df: pd.DataFrame, keno_type: int, n_permutations: int = 1000) -> Dict:
    """
    Permutationstest: Ist der Unterschied FRUEH vs SPAET signifikant?

    Nullhypothese: Kein Unterschied zwischen FRUEH und SPAET
    Permutiert die cycle_half Labels und berechnet Verteilung der Differenzen.
    """
    valid_df = df[df["cycle_half"].isin(["FRUEH", "SPAET"])].copy()
    n = len(valid_df)

    if n < 50:
        return {"error": "Zu wenig Daten", "n": n}

    # Beobachtete Differenz
    observed = calculate_roi_by_half(valid_df, keno_type)
    observed_diff = observed["diff"]

    if np.isnan(observed_diff):
        return {"error": "NaN Differenz", "observed_diff": None}

    # Permutationen
    np.random.seed(42)
    perm_diffs = []

    for _ in range(n_permutations):
        # Permutiere Labels
        permuted_labels = np.random.permutation(valid_df["cycle_half"].values)
        valid_df["perm_half"] = permuted_labels

        frueh_wins = valid_df[valid_df["perm_half"] == "FRUEH"][f"v2_win_t{keno_type}"].sum()
        frueh_n = (valid_df["perm_half"] == "FRUEH").sum()
        spaet_wins = valid_df[valid_df["perm_half"] == "SPAET"][f"v2_win_t{keno_type}"].sum()
        spaet_n = (valid_df["perm_half"] == "SPAET").sum()

        if frueh_n > 0 and spaet_n > 0:
            frueh_roi = (frueh_wins - frueh_n) / frueh_n * 100
            spaet_roi = (spaet_wins - spaet_n) / spaet_n * 100
            perm_diffs.append(frueh_roi - spaet_roi)

    perm_diffs = np.array(perm_diffs)

    # p-Wert (zweiseitig)
    more_extreme = np.sum(np.abs(perm_diffs) >= np.abs(observed_diff))
    p_value = more_extreme / len(perm_diffs)

    return {
        "observed_diff": observed_diff,
        "n_permutations": n_permutations,
        "perm_mean": float(np.mean(perm_diffs)),
        "perm_std": float(np.std(perm_diffs)),
        "perm_5th": float(np.percentile(perm_diffs, 5)),
        "perm_95th": float(np.percentile(perm_diffs, 95)),
        "p_value": p_value,
        "significant_005": p_value < 0.05,
        "significant_001": p_value < 0.01,
    }


# =============================================================================
# TRAIN/TEST SPLIT
# =============================================================================

def train_test_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splittet in Train (2022-2024) und Test (2025)."""
    train_df = df[df["year"] < 2025].copy()
    test_df = df[df["year"] == 2025].copy()
    return train_df, test_df


# =============================================================================
# MAIN VALIDIERUNG
# =============================================================================

def validate_hyp_cyc_001() -> Dict:
    """
    Hauptvalidierung HYP_CYC_001:
    1. Train (2022-2024): Beobachtung + Permutationstest
    2. Test (2025): Frozen Rule Evaluation
    """
    print("=" * 70)
    print("AXIOM-FIRST VALIDIERUNG: HYP_CYC_001")
    print("28-Tage-Zyklus: FRUEH (Tag 1-14) vs SPAET (Tag 15-28)")
    print("=" * 70)

    base_path = Path(__file__).parent.parent
    results = {
        "hypothesis": "HYP_CYC_001",
        "description": "28-Tage-Zyklus FRUEH (Tag 1-14) vs SPAET (Tag 15-28)",
        "frozen_rule": "Investiere nur in FRUEH-Phase (Tag 1-14 nach Jackpot)",
        "validation_date": datetime.now().isoformat(),
    }

    # Daten laden
    print("\n[1] Daten laden...")
    df, jackpot_dates = load_data(base_path)
    df = add_cycle_info(df, jackpot_dates)
    df = add_hits_and_wins(df)

    print(f"    Total Ziehungen: {len(df)}")
    print(f"    Jackpots: {len(jackpot_dates)}")

    # Train/Test Split
    print("\n[2] Train/Test Split...")
    train_df, test_df = train_test_split(df)
    print(f"    Train (2022-2024): {len(train_df)}")
    print(f"    Test (2025): {len(test_df)}")

    results["data"] = {
        "total": len(df),
        "train": len(train_df),
        "test": len(test_df),
        "jackpots": len(jackpot_dates),
    }

    # Analyse pro Typ
    results["by_type"] = {}

    for keno_type in [8, 9, 10]:
        print(f"\n{'=' * 70}")
        print(f"TYP {keno_type}")
        print("=" * 70)

        type_result = {}

        # --- TRAIN: Beobachtete Unterschiede ---
        print("\n[3] TRAIN (2022-2024): Beobachtete Unterschiede")
        train_rois = calculate_roi_by_half(train_df, keno_type)
        type_result["train"] = train_rois

        print(f"    FRUEH: N={train_rois['frueh']['n']}, ROI={train_rois['frueh']['roi']:+.1f}%")
        print(f"    SPAET: N={train_rois['spaet']['n']}, ROI={train_rois['spaet']['roi']:+.1f}%")
        print(f"    Differenz: {train_rois['diff']:+.1f}%")

        # --- TRAIN: Permutationstest ---
        print("\n[4] TRAIN: Permutationstest (1000 Iterationen)")
        perm_result = permutation_test(train_df, keno_type, n_permutations=1000)
        type_result["permutation_test"] = perm_result

        if "error" not in perm_result:
            print(f"    Beobachtete Diff: {perm_result['observed_diff']:+.1f}%")
            print(f"    Permutierte Diff: Mean={perm_result['perm_mean']:.1f}%, Std={perm_result['perm_std']:.1f}%")
            print(f"    95% CI: [{perm_result['perm_5th']:.1f}%, {perm_result['perm_95th']:.1f}%]")
            print(f"    p-Wert: {perm_result['p_value']:.4f}")
            print(f"    Signifikant (p<0.05): {perm_result['significant_005']}")
            print(f"    Signifikant (p<0.01): {perm_result['significant_001']}")
        else:
            print(f"    ERROR: {perm_result['error']}")

        # --- TEST: Out-of-Sample (2025) ---
        print("\n[5] TEST (2025): Out-of-Sample Validierung mit FROZEN RULES")
        if len(test_df) > 0:
            test_rois = calculate_roi_by_half(test_df, keno_type)
            type_result["test_oos"] = test_rois

            print(f"    FRUEH: N={test_rois['frueh']['n']}, ROI={test_rois['frueh']['roi']:+.1f}%")
            print(f"    SPAET: N={test_rois['spaet']['n']}, ROI={test_rois['spaet']['roi']:+.1f}%")
            print(f"    Differenz: {test_rois['diff']:+.1f}%")

            # Konsistenzcheck
            train_direction = "FRUEH_BESSER" if train_rois["diff"] > 0 else "SPAET_BESSER"
            test_direction = "FRUEH_BESSER" if test_rois["diff"] > 0 else "SPAET_BESSER"
            consistent = train_direction == test_direction

            type_result["consistency"] = {
                "train_direction": train_direction,
                "test_direction": test_direction,
                "consistent": consistent,
            }

            print(f"\n    Konsistenz-Check:")
            print(f"      Train: {train_direction}")
            print(f"      Test:  {test_direction}")
            print(f"      Konsistent: {consistent}")
        else:
            type_result["test_oos"] = {"error": "Keine 2025 Daten verfuegbar"}

        # --- Strategie-Bewertung ---
        print("\n[6] STRATEGIE-BEWERTUNG")
        if "error" not in perm_result and test_rois["diff"] is not None:
            # Nur FRUEH spielen vs Random
            strategy_valid = (
                perm_result["significant_005"] and
                type_result.get("consistency", {}).get("consistent", False)
            )

            type_result["strategy_valid"] = strategy_valid

            if strategy_valid:
                print("    STRATEGIE VALIDIERT:")
                print("      - Signifikant im Train (Permutationstest)")
                print("      - Konsistent im OOS Test (2025)")
                print(f"      - Empfehlung: Nur FRUEH-Phase (Tag 1-14) spielen")
            else:
                print("    STRATEGIE NICHT VALIDIERT:")
                if not perm_result["significant_005"]:
                    print("      - Nicht signifikant im Permutationstest")
                if not type_result.get("consistency", {}).get("consistent", False):
                    print("      - Nicht konsistent zwischen Train und Test")

        results["by_type"][f"typ_{keno_type}"] = type_result

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    summary = {
        "validated_types": [],
        "not_validated_types": [],
    }

    for typ_key, typ_data in results["by_type"].items():
        if typ_data.get("strategy_valid", False):
            summary["validated_types"].append(typ_key)
        else:
            summary["not_validated_types"].append(typ_key)

    results["summary"] = summary

    print(f"\n  Validierte Typen: {summary['validated_types']}")
    print(f"  Nicht validiert: {summary['not_validated_types']}")

    # Speichern
    output_path = base_path / "results" / "hyp_cyc_001_validation.json"

    def json_serializer(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=json_serializer)

    print(f"\n  Ergebnis gespeichert: {output_path}")

    return results


if __name__ == "__main__":
    validate_hyp_cyc_001()
