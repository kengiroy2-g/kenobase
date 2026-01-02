#!/usr/bin/env python3
"""
TEST HYP_007: Regime-Wechsel (28-Tage-Rolling-Autokorrelation)

HYPOTHESE (aus HYP_CYC_005):
    ROI in 28-Tage-Block A korreliert NICHT mit Block A+1
    Vorhersage: |autocorrelation(lag=1)| < 0.3

NULLMODELL:
    Block-Permutation: 28-Tage-Bloecke werden permutiert,
    Autokorrelation wird neu berechnet.
    p-value = Anteil der Permutationen mit |autocorr| >= |observed|

ACCEPTANCE:
    - autocorrelation(lag=1) < 0.3 => HYP_007 BESTAETIGT (Regime-Wechsel)
    - p-value fuer Signifikanz gegen Zufall

OUTPUT: results/hyp007_regime_switch.json

Autor: Kenobase V2.2
Datum: 2025-12-30
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
# KONSTANTEN
# =============================================================================

TICKET_V2 = {
    6: [36, 43, 51, 58, 61, 64],
    7: [3, 36, 43, 51, 58, 61, 64],
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

BLOCK_SIZE = 28  # 28-Tage-Perioden (Dauerschein-Zyklus)
N_PERMUTATIONS = 1000  # Anzahl Permutationen fuer Nullmodell


# =============================================================================
# DATA LOADING
# =============================================================================

def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten und bereitet sie vor."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Zahlen extrahieren
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )

    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def add_win_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Fuegt Gewinn-Spalten fuer alle Ticket-Typen hinzu."""
    for keno_type in [6, 7, 8, 9, 10]:
        ticket = TICKET_V2[keno_type]

        # Treffer berechnen
        df[f"hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket if n in s)
        )

        # Gewinn berechnen
        df[f"win_t{keno_type}"] = df[f"hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )

    return df


# =============================================================================
# ROI BERECHNUNG
# =============================================================================

def compute_block_rois(df: pd.DataFrame, keno_type: int) -> List[float]:
    """Berechnet ROI fuer jeden 28-Tage-Block."""
    rois = []
    win_col = f"win_t{keno_type}"

    for i in range(0, len(df) - BLOCK_SIZE + 1, BLOCK_SIZE):
        block_df = df.iloc[i:i + BLOCK_SIZE]
        wins = block_df[win_col].sum()
        cost = BLOCK_SIZE  # 1 EUR pro Ziehung
        roi = (wins - cost) / cost * 100 if cost > 0 else 0
        rois.append(roi)

    return rois


def compute_autocorrelation_lag1(rois: List[float]) -> float:
    """Berechnet Autokorrelation mit Lag=1."""
    if len(rois) < 2:
        return np.nan

    rois_arr = np.array(rois)
    return float(np.corrcoef(rois_arr[:-1], rois_arr[1:])[0, 1])


# =============================================================================
# NULLMODELL: Block-Permutation
# =============================================================================

def block_permutation_test(
    df: pd.DataFrame,
    keno_type: int,
    observed_autocorr: float,
    n_permutations: int = N_PERMUTATIONS,
) -> Tuple[float, List[float]]:
    """
    Fuehrt Block-Permutation-Test durch.

    Permutiert die 28-Tage-Bloecke und berechnet jeweils die Autokorrelation.
    p-value = Anteil der Permutationen mit |autocorr| >= |observed|.

    Returns:
        (p_value, permuted_autocorrs)
    """
    win_col = f"win_t{keno_type}"

    # Bloecke extrahieren
    blocks = []
    for i in range(0, len(df) - BLOCK_SIZE + 1, BLOCK_SIZE):
        block_wins = df.iloc[i:i + BLOCK_SIZE][win_col].values
        blocks.append(block_wins)

    if len(blocks) < 4:
        return np.nan, []

    # Permutationen durchfuehren
    permuted_autocorrs = []
    rng = np.random.default_rng(42)  # Fuer Reproduzierbarkeit

    for _ in range(n_permutations):
        # Bloecke permutieren (Reihenfolge aendern)
        perm_indices = rng.permutation(len(blocks))
        perm_rois = []

        for idx in perm_indices:
            block_wins = blocks[idx]
            roi = (block_wins.sum() - BLOCK_SIZE) / BLOCK_SIZE * 100
            perm_rois.append(roi)

        # Autokorrelation berechnen
        autocorr = compute_autocorrelation_lag1(perm_rois)
        if not np.isnan(autocorr):
            permuted_autocorrs.append(autocorr)

    # p-value berechnen (two-tailed)
    if len(permuted_autocorrs) == 0:
        return np.nan, []

    observed_abs = abs(observed_autocorr)
    count_extreme = sum(1 for ac in permuted_autocorrs if abs(ac) >= observed_abs)
    p_value = count_extreme / len(permuted_autocorrs)

    return p_value, permuted_autocorrs


# =============================================================================
# HAUPTTEST
# =============================================================================

def test_hyp007_regime_switch(base_path: Path) -> Dict:
    """
    Haupttest fuer HYP_007: Regime-Wechsel.

    Tests:
    1. Berechne 28-Tage-Rolling-ROI pro Typ
    2. Berechne Autokorrelation (Lag=1)
    3. Block-Permutation Nullmodell fuer p-value
    4. Bewertung: |autocorr| < 0.3 => REGIME_WECHSEL
    """
    print("\n" + "=" * 70)
    print("HYP_007: Regime-Wechsel (28-Tage-Rolling-Autokorrelation)")
    print("=" * 70)

    # Daten laden
    print("\n[1] Daten laden...")
    df = load_keno_data(base_path)
    df = add_win_columns(df)
    print(f"    Ziehungen: {len(df)}")

    # Ergebnis-Container
    results = {
        "hypothesis": "HYP_007",
        "name": "Regime-Wechsel (28-Tage-Rolling-Autokorrelation)",
        "prediction": "|autocorrelation(lag=1)| < 0.3 => REGIME_WECHSEL",
        "nullmodel": "Block-Permutation (28-Tage-Bloecke)",
        "n_permutations": N_PERMUTATIONS,
        "block_size_days": BLOCK_SIZE,
        "data_source": "data/raw/keno/KENO_ab_2022_bereinigt.csv",
        "n_draws": len(df),
        "run_timestamp": datetime.now().isoformat(),
        "by_type": {},
    }

    # Test fuer jeden Typ
    print("\n[2] Tests pro Typ durchfuehren...")

    all_confirmed = True

    for keno_type in [6, 7, 8, 9, 10]:
        print(f"\n  --- TYP {keno_type} ---")

        # ROIs berechnen
        rois = compute_block_rois(df, keno_type)
        n_periods = len(rois)

        if n_periods < 4:
            print(f"    SKIP: Zu wenig Perioden ({n_periods})")
            results["by_type"][f"typ_{keno_type}"] = {
                "status": "SKIPPED",
                "reason": f"Zu wenig Perioden ({n_periods} < 4)",
            }
            continue

        # Autokorrelation berechnen
        autocorr = compute_autocorrelation_lag1(rois)
        print(f"    Anzahl 28-Tage-Perioden: {n_periods}")
        print(f"    Autokorrelation (Lag=1): {autocorr:.4f}")

        # Nullmodell
        print(f"    Block-Permutation Test ({N_PERMUTATIONS}x)...")
        p_value, perm_autocorrs = block_permutation_test(
            df, keno_type, autocorr, N_PERMUTATIONS
        )

        if np.isnan(p_value):
            print("    SKIP: Nullmodell konnte nicht berechnet werden")
            results["by_type"][f"typ_{keno_type}"] = {
                "status": "SKIPPED",
                "reason": "Nullmodell fehlgeschlagen",
            }
            continue

        # Statistiken der Permutationen
        perm_mean = np.mean(perm_autocorrs)
        perm_std = np.std(perm_autocorrs)

        # Bewertung
        is_regime_switch = abs(autocorr) < 0.3
        interpretation = "REGIME_WECHSEL" if is_regime_switch else "PERSISTENZ"

        if not is_regime_switch:
            all_confirmed = False

        print(f"    p-value: {p_value:.4f}")
        print(f"    Permutation Mean: {perm_mean:.4f}, Std: {perm_std:.4f}")
        print(f"    Interpretation: {interpretation}")

        # ROI-Statistiken
        roi_mean = np.mean(rois)
        roi_std = np.std(rois)
        roi_min = np.min(rois)
        roi_max = np.max(rois)

        results["by_type"][f"typ_{keno_type}"] = {
            "n_periods": n_periods,
            "autocorrelation_lag1": round(autocorr, 6),
            "p_value": round(p_value, 4),
            "nullmodel_mean": round(perm_mean, 6),
            "nullmodel_std": round(perm_std, 6),
            "interpretation": interpretation,
            "confirmed": is_regime_switch,
            "roi_stats": {
                "mean": round(roi_mean, 2),
                "std": round(roi_std, 2),
                "min": round(roi_min, 2),
                "max": round(roi_max, 2),
            },
        }

    # Gesamt-Bewertung
    confirmed_types = [
        k for k, v in results["by_type"].items()
        if v.get("confirmed", False)
    ]
    tested_types = [
        k for k, v in results["by_type"].items()
        if v.get("status") != "SKIPPED"
    ]

    results["summary"] = {
        "tested_types": tested_types,
        "confirmed_types": confirmed_types,
        "confirmation_rate": len(confirmed_types) / len(tested_types) if tested_types else 0,
        "overall_status": "BESTAETIGT" if all_confirmed and tested_types else "NICHT_BESTAETIGT",
    }

    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"  Getestete Typen: {len(tested_types)}")
    print(f"  Bestaetigt (|autocorr| < 0.3): {len(confirmed_types)}")
    print(f"  Bestaetigungsrate: {results['summary']['confirmation_rate']*100:.1f}%")
    print(f"  Gesamtstatus: {results['summary']['overall_status']}")

    return results


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent.parent
    results = test_hyp007_regime_switch(base_path)

    # Speichern
    output_path = base_path / "results" / "hyp007_regime_switch.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {output_path}")


if __name__ == "__main__":
    main()
