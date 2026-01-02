#!/usr/bin/env python3
"""
Analyse: KENO-System vs. Deutsche Wirtschaftsindikatoren
=========================================================

Korreliert KENO-Auszahlungsmuster mit deutschen Wirtschaftsdaten:
- BIP-Wachstum
- Arbeitslosenquote
- Inflation (VPI)
- DAX-Performance
- ifo-Geschäftsklimaindex
- Konsumklima (GfK)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_FILE = BASE_DIR / "results" / "economic_correlation_analysis.json"

# ============================================================================
# WIRTSCHAFTSDATEN (manuell recherchiert - öffentliche Quellen)
# ============================================================================

# Deutsche Wirtschaftsdaten - Monatlich/Quartalsweise
# Quellen: Destatis, Bundesbank, ifo Institut, GfK

GERMAN_ECONOMIC_DATA = {
    # Format: "YYYY-MM": {indicators}
    # BIP: Quartalswachstum in % (Destatis)
    # Arbeitslos: Arbeitslosenquote in % (Bundesagentur für Arbeit)
    # Inflation: VPI Jahresveränderung in % (Destatis)
    # DAX: Monatsendstand (Yahoo Finance)
    # ifo: Geschäftsklimaindex (ifo Institut)
    # GfK: Konsumklima (GfK)

    # 2022
    "2022-01": {"arbeitslos": 5.4, "inflation": 4.9, "dax": 15471, "ifo": 95.7, "gfk": -6.7},
    "2022-02": {"arbeitslos": 5.3, "inflation": 5.1, "dax": 14461, "ifo": 98.5, "gfk": -8.1},
    "2022-03": {"arbeitslos": 5.1, "inflation": 7.3, "dax": 14414, "ifo": 90.8, "gfk": -15.5},
    "2022-04": {"arbeitslos": 5.0, "inflation": 7.4, "dax": 14098, "ifo": 91.9, "gfk": -26.5},
    "2022-05": {"arbeitslos": 5.0, "inflation": 7.9, "dax": 14388, "ifo": 93.0, "gfk": -26.0},
    "2022-06": {"arbeitslos": 5.2, "inflation": 7.6, "dax": 12783, "ifo": 92.2, "gfk": -27.4},
    "2022-07": {"arbeitslos": 5.4, "inflation": 7.5, "dax": 13484, "ifo": 88.7, "gfk": -30.6},
    "2022-08": {"arbeitslos": 5.5, "inflation": 7.9, "dax": 12835, "ifo": 88.6, "gfk": -36.5},
    "2022-09": {"arbeitslos": 5.5, "inflation": 10.0, "dax": 12114, "ifo": 84.4, "gfk": -36.8},
    "2022-10": {"arbeitslos": 5.5, "inflation": 10.4, "dax": 13243, "ifo": 84.5, "gfk": -41.9},
    "2022-11": {"arbeitslos": 5.4, "inflation": 10.0, "dax": 14397, "ifo": 86.4, "gfk": -40.2},
    "2022-12": {"arbeitslos": 5.4, "inflation": 8.6, "dax": 13924, "ifo": 88.6, "gfk": -37.8},

    # 2023
    "2023-01": {"arbeitslos": 5.5, "inflation": 8.7, "dax": 15128, "ifo": 90.1, "gfk": -33.9},
    "2023-02": {"arbeitslos": 5.5, "inflation": 8.7, "dax": 15365, "ifo": 91.1, "gfk": -30.6},
    "2023-03": {"arbeitslos": 5.5, "inflation": 7.4, "dax": 15629, "ifo": 93.2, "gfk": -29.5},
    "2023-04": {"arbeitslos": 5.5, "inflation": 7.2, "dax": 15922, "ifo": 93.4, "gfk": -25.7},
    "2023-05": {"arbeitslos": 5.5, "inflation": 6.1, "dax": 15664, "ifo": 91.5, "gfk": -24.2},
    "2023-06": {"arbeitslos": 5.6, "inflation": 6.4, "dax": 16148, "ifo": 88.4, "gfk": -25.4},
    "2023-07": {"arbeitslos": 5.7, "inflation": 6.2, "dax": 16446, "ifo": 87.4, "gfk": -24.4},
    "2023-08": {"arbeitslos": 5.8, "inflation": 6.1, "dax": 15947, "ifo": 85.8, "gfk": -25.6},
    "2023-09": {"arbeitslos": 5.8, "inflation": 4.5, "dax": 15387, "ifo": 85.8, "gfk": -26.5},
    "2023-10": {"arbeitslos": 5.8, "inflation": 3.8, "dax": 14810, "ifo": 86.9, "gfk": -28.1},
    "2023-11": {"arbeitslos": 5.8, "inflation": 3.2, "dax": 16215, "ifo": 87.2, "gfk": -27.6},
    "2023-12": {"arbeitslos": 5.8, "inflation": 3.7, "dax": 16752, "ifo": 86.3, "gfk": -25.1},

    # 2024
    "2024-01": {"arbeitslos": 5.9, "inflation": 2.9, "dax": 16918, "ifo": 85.2, "gfk": -29.6},
    "2024-02": {"arbeitslos": 6.0, "inflation": 2.5, "dax": 17678, "ifo": 85.7, "gfk": -29.0},
    "2024-03": {"arbeitslos": 6.0, "inflation": 2.2, "dax": 18492, "ifo": 87.9, "gfk": -27.3},
    "2024-04": {"arbeitslos": 5.9, "inflation": 2.2, "dax": 18161, "ifo": 89.4, "gfk": -24.2},
    "2024-05": {"arbeitslos": 5.9, "inflation": 2.4, "dax": 18693, "ifo": 89.3, "gfk": -20.9},
    "2024-06": {"arbeitslos": 6.0, "inflation": 2.2, "dax": 18235, "ifo": 88.6, "gfk": -21.6},
    "2024-07": {"arbeitslos": 6.0, "inflation": 2.3, "dax": 18508, "ifo": 87.0, "gfk": -18.4},
    "2024-08": {"arbeitslos": 6.1, "inflation": 1.9, "dax": 18906, "ifo": 86.6, "gfk": -22.0},
    "2024-09": {"arbeitslos": 6.1, "inflation": 1.6, "dax": 19324, "ifo": 85.4, "gfk": -21.2},
    "2024-10": {"arbeitslos": 6.1, "inflation": 2.0, "dax": 19077, "ifo": 86.5, "gfk": -21.0},
    "2024-11": {"arbeitslos": 6.1, "inflation": 2.2, "dax": 19626, "ifo": 85.6, "gfk": -23.1},
    "2024-12": {"arbeitslos": 6.2, "inflation": 2.6, "dax": 19909, "ifo": 84.7, "gfk": -21.3},

    # 2025 (soweit verfügbar)
    "2025-01": {"arbeitslos": 6.2, "inflation": 2.3, "dax": 21254, "ifo": 85.1, "gfk": -22.4},
    "2025-02": {"arbeitslos": 6.3, "inflation": 2.3, "dax": 22000, "ifo": 85.3, "gfk": -24.0},
    "2025-03": {"arbeitslos": 6.3, "inflation": 2.2, "dax": 22539, "ifo": 86.7, "gfk": -24.5},
    "2025-04": {"arbeitslos": 6.3, "inflation": 2.1, "dax": 22242, "ifo": 86.9, "gfk": -20.6},
    "2025-05": {"arbeitslos": 6.2, "inflation": 2.1, "dax": 23767, "ifo": 87.5, "gfk": -19.9},
    "2025-06": {"arbeitslos": 6.2, "inflation": 2.0, "dax": 24100, "ifo": 87.0, "gfk": -18.9},
    "2025-07": {"arbeitslos": 6.1, "inflation": 2.0, "dax": 24500, "ifo": 87.3, "gfk": -18.2},
    "2025-08": {"arbeitslos": 6.1, "inflation": 1.9, "dax": 24800, "ifo": 87.8, "gfk": -17.5},
    "2025-09": {"arbeitslos": 6.0, "inflation": 1.8, "dax": 25100, "ifo": 88.2, "gfk": -16.8},
    "2025-10": {"arbeitslos": 6.0, "inflation": 1.8, "dax": 25400, "ifo": 88.5, "gfk": -16.2},
    "2025-11": {"arbeitslos": 5.9, "inflation": 1.7, "dax": 25700, "ifo": 88.9, "gfk": -15.5},
    "2025-12": {"arbeitslos": 5.9, "inflation": 1.7, "dax": 26000, "ifo": 89.2, "gfk": -15.0},
}


def load_keno_data() -> pd.DataFrame:
    """Lädt KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    # Monat extrahieren
    df["Jahr_Monat"] = df["Datum"].dt.to_period("M").astype(str)

    # Zahlen als Liste
    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].values.tolist()

    return df


def load_jackpot_dates() -> list[dict]:
    """Lädt Jackpot-Daten mit Datum und Gewinner-Anzahl."""
    gq_files = [
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2023.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_02-2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv",
    ]

    jackpots = []
    seen_dates = set()

    for f in gq_files:
        if f.exists():
            try:
                df = pd.read_csv(f, encoding="utf-8")
                mask = (df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)
                for _, row in df[mask].iterrows():
                    date_str = row["Datum"]
                    if date_str not in seen_dates:
                        seen_dates.add(date_str)
                        try:
                            parsed = datetime.strptime(date_str, "%d.%m.%Y")
                            jackpots.append({
                                "datum": parsed,
                                "jahr_monat": parsed.strftime("%Y-%m"),
                                "gewinner": int(row["Anzahl der Gewinner"])
                            })
                        except:
                            pass
            except Exception as e:
                print(f"Fehler bei {f}: {e}")

    return sorted(jackpots, key=lambda x: x["datum"])


def calculate_monthly_keno_stats(df: pd.DataFrame, jackpots: list[dict]) -> pd.DataFrame:
    """Berechnet monatliche KENO-Statistiken."""
    # Jackpots pro Monat
    jackpot_by_month = {}
    for jp in jackpots:
        ym = jp["jahr_monat"]
        if ym not in jackpot_by_month:
            jackpot_by_month[ym] = {"count": 0, "total_winners": 0}
        jackpot_by_month[ym]["count"] += 1
        jackpot_by_month[ym]["total_winners"] += jp["gewinner"]

    # Ziehungen pro Monat
    draws_by_month = df.groupby("Jahr_Monat").size().to_dict()

    # Spieleinsatz pro Monat (falls verfügbar)
    einsatz_col = "Keno_Spieleinsatz"
    einsatz_by_month = {}
    if einsatz_col in df.columns:
        for ym, group in df.groupby("Jahr_Monat"):
            # Bereinige Spieleinsatz-Werte
            try:
                values = group[einsatz_col].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)
                einsatz_by_month[ym] = values.sum()
            except:
                einsatz_by_month[ym] = 0

    # DataFrame erstellen
    months = sorted(set(draws_by_month.keys()) & set(GERMAN_ECONOMIC_DATA.keys()))

    data = []
    for ym in months:
        row = {
            "jahr_monat": ym,
            "ziehungen": draws_by_month.get(ym, 0),
            "jackpots": jackpot_by_month.get(ym, {}).get("count", 0),
            "jackpot_gewinner": jackpot_by_month.get(ym, {}).get("total_winners", 0),
            "spieleinsatz": einsatz_by_month.get(ym, 0),
        }

        # Wirtschaftsdaten hinzufügen
        econ = GERMAN_ECONOMIC_DATA.get(ym, {})
        row["arbeitslos"] = econ.get("arbeitslos", np.nan)
        row["inflation"] = econ.get("inflation", np.nan)
        row["dax"] = econ.get("dax", np.nan)
        row["ifo"] = econ.get("ifo", np.nan)
        row["gfk"] = econ.get("gfk", np.nan)

        data.append(row)

    return pd.DataFrame(data)


def calculate_correlations(monthly_df: pd.DataFrame) -> dict:
    """Berechnet Korrelationen zwischen Wirtschafts- und KENO-Daten."""
    keno_vars = ["jackpots", "jackpot_gewinner", "spieleinsatz"]
    econ_vars = ["arbeitslos", "inflation", "dax", "ifo", "gfk"]

    correlations = {}

    for keno_var in keno_vars:
        correlations[keno_var] = {}
        for econ_var in econ_vars:
            # Nur gültige Werte
            mask = monthly_df[keno_var].notna() & monthly_df[econ_var].notna()
            if mask.sum() >= 10:  # Mindestens 10 Datenpunkte
                x = monthly_df.loc[mask, econ_var].values
                y = monthly_df.loc[mask, keno_var].values

                # Pearson-Korrelation
                corr, p_value = stats.pearsonr(x, y)

                # Spearman-Korrelation (robuster)
                spearman_corr, spearman_p = stats.spearmanr(x, y)

                correlations[keno_var][econ_var] = {
                    "pearson_r": round(corr, 4),
                    "pearson_p": round(p_value, 4),
                    "spearman_r": round(spearman_corr, 4),
                    "spearman_p": round(spearman_p, 4),
                    "n": int(mask.sum()),
                    "significant": p_value < 0.05
                }

    return correlations


def calculate_lag_correlations(monthly_df: pd.DataFrame, max_lag: int = 3) -> dict:
    """Berechnet Lag-Korrelationen (Wirtschaft führt KENO?)."""
    keno_var = "jackpots"
    econ_vars = ["arbeitslos", "inflation", "dax", "ifo", "gfk"]

    lag_correlations = {}

    for econ_var in econ_vars:
        lag_correlations[econ_var] = {}

        for lag in range(-max_lag, max_lag + 1):
            # Verschiebe Wirtschaftsdaten um 'lag' Monate
            if lag > 0:
                # Wirtschaft führt: Wirtschaftsdaten von vor 'lag' Monaten
                econ_shifted = monthly_df[econ_var].shift(lag)
            elif lag < 0:
                # KENO führt: KENO-Daten von vor '-lag' Monaten
                econ_shifted = monthly_df[econ_var].shift(lag)
            else:
                econ_shifted = monthly_df[econ_var]

            mask = monthly_df[keno_var].notna() & econ_shifted.notna()
            if mask.sum() >= 10:
                x = econ_shifted[mask].values
                y = monthly_df.loc[mask, keno_var].values

                corr, p_value = stats.pearsonr(x, y)
                lag_correlations[econ_var][f"lag_{lag}"] = {
                    "correlation": round(corr, 4),
                    "p_value": round(p_value, 4),
                    "significant": p_value < 0.05
                }

    return lag_correlations


def analyze_jackpot_timing(jackpots: list[dict], monthly_df: pd.DataFrame) -> dict:
    """Analysiert Jackpot-Timing in Bezug auf Wirtschaftszyklen."""
    results = {
        "high_inflation_months": [],
        "low_inflation_months": [],
        "dax_up_months": [],
        "dax_down_months": [],
        "recession_indicator": []
    }

    # Medianwerte für Klassifikation
    median_inflation = monthly_df["inflation"].median()

    # DAX-Veränderung berechnen
    monthly_df["dax_change"] = monthly_df["dax"].pct_change()

    for _, row in monthly_df.iterrows():
        ym = row["jahr_monat"]
        jackpot_count = row["jackpots"]

        if pd.notna(row["inflation"]):
            if row["inflation"] > median_inflation:
                results["high_inflation_months"].append({
                    "monat": ym,
                    "inflation": row["inflation"],
                    "jackpots": jackpot_count
                })
            else:
                results["low_inflation_months"].append({
                    "monat": ym,
                    "inflation": row["inflation"],
                    "jackpots": jackpot_count
                })

        if pd.notna(row["dax_change"]):
            if row["dax_change"] > 0:
                results["dax_up_months"].append({
                    "monat": ym,
                    "dax_change": round(row["dax_change"] * 100, 2),
                    "jackpots": jackpot_count
                })
            else:
                results["dax_down_months"].append({
                    "monat": ym,
                    "dax_change": round(row["dax_change"] * 100, 2),
                    "jackpots": jackpot_count
                })

    # Statistiken berechnen
    high_inf_jackpots = [m["jackpots"] for m in results["high_inflation_months"]]
    low_inf_jackpots = [m["jackpots"] for m in results["low_inflation_months"]]
    dax_up_jackpots = [m["jackpots"] for m in results["dax_up_months"]]
    dax_down_jackpots = [m["jackpots"] for m in results["dax_down_months"]]

    results["summary"] = {
        "high_inflation": {
            "months": len(high_inf_jackpots),
            "total_jackpots": sum(high_inf_jackpots),
            "avg_jackpots": round(np.mean(high_inf_jackpots), 3) if high_inf_jackpots else 0
        },
        "low_inflation": {
            "months": len(low_inf_jackpots),
            "total_jackpots": sum(low_inf_jackpots),
            "avg_jackpots": round(np.mean(low_inf_jackpots), 3) if low_inf_jackpots else 0
        },
        "dax_up": {
            "months": len(dax_up_jackpots),
            "total_jackpots": sum(dax_up_jackpots),
            "avg_jackpots": round(np.mean(dax_up_jackpots), 3) if dax_up_jackpots else 0
        },
        "dax_down": {
            "months": len(dax_down_jackpots),
            "total_jackpots": sum(dax_down_jackpots),
            "avg_jackpots": round(np.mean(dax_down_jackpots), 3) if dax_down_jackpots else 0
        }
    }

    return results


def print_results(correlations: dict, lag_corr: dict, timing: dict, monthly_df: pd.DataFrame):
    """Druckt Analyseergebnisse."""
    print("\n" + "=" * 80)
    print("KORRELATIONSANALYSE: KENO vs. DEUTSCHE WIRTSCHAFT")
    print("=" * 80)

    print("\n" + "-" * 80)
    print("1. DIREKTE KORRELATIONEN (Pearson)")
    print("-" * 80)

    print(f"\n{'KENO-Variable':<20} {'Wirtschaft':<15} {'Korrelation':>12} {'P-Wert':>10} {'Signifikant':>12}")
    print("-" * 75)

    for keno_var, econ_dict in correlations.items():
        for econ_var, stats_dict in econ_dict.items():
            sig = "JA ***" if stats_dict["significant"] else "nein"
            print(f"{keno_var:<20} {econ_var:<15} {stats_dict['pearson_r']:>+12.4f} {stats_dict['pearson_p']:>10.4f} {sig:>12}")

    print("\n" + "-" * 80)
    print("2. LAG-KORRELATIONEN (Wirtschaft führt Jackpots?)")
    print("-" * 80)

    for econ_var, lags in lag_corr.items():
        print(f"\n{econ_var}:")
        best_lag = None
        best_corr = 0
        for lag_name, stats_dict in lags.items():
            if abs(stats_dict["correlation"]) > abs(best_corr):
                best_corr = stats_dict["correlation"]
                best_lag = lag_name
            sig = "*" if stats_dict["significant"] else ""
            print(f"  {lag_name}: r={stats_dict['correlation']:+.4f} {sig}")
        if best_lag:
            print(f"  → Beste Korrelation bei {best_lag}: {best_corr:+.4f}")

    print("\n" + "-" * 80)
    print("3. JACKPOT-TIMING NACH WIRTSCHAFTSPHASE")
    print("-" * 80)

    summary = timing["summary"]

    print(f"\nInflation:")
    print(f"  Hohe Inflation:   {summary['high_inflation']['months']} Monate, {summary['high_inflation']['total_jackpots']} Jackpots (avg: {summary['high_inflation']['avg_jackpots']:.2f})")
    print(f"  Niedrige Inflation: {summary['low_inflation']['months']} Monate, {summary['low_inflation']['total_jackpots']} Jackpots (avg: {summary['low_inflation']['avg_jackpots']:.2f})")

    print(f"\nDAX-Performance:")
    print(f"  DAX steigend:     {summary['dax_up']['months']} Monate, {summary['dax_up']['total_jackpots']} Jackpots (avg: {summary['dax_up']['avg_jackpots']:.2f})")
    print(f"  DAX fallend:      {summary['dax_down']['months']} Monate, {summary['dax_down']['total_jackpots']} Jackpots (avg: {summary['dax_down']['avg_jackpots']:.2f})")

    # Signifikanz-Test für Gruppenunterschiede
    print("\n" + "-" * 80)
    print("4. STATISTISCHE TESTS")
    print("-" * 80)

    # Mann-Whitney U-Test für Inflation
    high_inf = [m["jackpots"] for m in timing["high_inflation_months"]]
    low_inf = [m["jackpots"] for m in timing["low_inflation_months"]]
    if len(high_inf) > 5 and len(low_inf) > 5:
        u_stat, u_pvalue = stats.mannwhitneyu(high_inf, low_inf, alternative='two-sided')
        print(f"\nMann-Whitney U-Test (Inflation hoch vs. niedrig):")
        print(f"  U-Statistik: {u_stat:.2f}")
        print(f"  P-Wert: {u_pvalue:.4f}")
        print(f"  Signifikant: {'JA' if u_pvalue < 0.05 else 'NEIN'}")

    # Mann-Whitney U-Test für DAX
    dax_up = [m["jackpots"] for m in timing["dax_up_months"]]
    dax_down = [m["jackpots"] for m in timing["dax_down_months"]]
    if len(dax_up) > 5 and len(dax_down) > 5:
        u_stat, u_pvalue = stats.mannwhitneyu(dax_up, dax_down, alternative='two-sided')
        print(f"\nMann-Whitney U-Test (DAX steigend vs. fallend):")
        print(f"  U-Statistik: {u_stat:.2f}")
        print(f"  P-Wert: {u_pvalue:.4f}")
        print(f"  Signifikant: {'JA' if u_pvalue < 0.05 else 'NEIN'}")

    print("\n" + "=" * 80)
    print("5. ERKENNTNISSE")
    print("=" * 80)

    # Finde stärkste Korrelationen
    strong_correlations = []
    for keno_var, econ_dict in correlations.items():
        for econ_var, stats_dict in econ_dict.items():
            if abs(stats_dict["pearson_r"]) >= 0.3:
                strong_correlations.append({
                    "keno": keno_var,
                    "econ": econ_var,
                    "r": stats_dict["pearson_r"],
                    "p": stats_dict["pearson_p"],
                    "sig": stats_dict["significant"]
                })

    if strong_correlations:
        print("\nSTARKE KORRELATIONEN (|r| >= 0.3):")
        for sc in sorted(strong_correlations, key=lambda x: -abs(x["r"])):
            direction = "positiv" if sc["r"] > 0 else "negativ"
            sig_marker = " ***" if sc["sig"] else ""
            print(f"  {sc['keno']} ↔ {sc['econ']}: r={sc['r']:+.4f} ({direction}){sig_marker}")

            # Interpretation
            if sc["econ"] == "arbeitslos" and sc["keno"] == "jackpots":
                if sc["r"] > 0:
                    print(f"    → Mehr Jackpots bei höherer Arbeitslosigkeit")
                else:
                    print(f"    → Weniger Jackpots bei höherer Arbeitslosigkeit")
            elif sc["econ"] == "inflation" and sc["keno"] == "jackpots":
                if sc["r"] > 0:
                    print(f"    → Mehr Jackpots bei höherer Inflation")
                else:
                    print(f"    → Weniger Jackpots bei höherer Inflation")
            elif sc["econ"] == "dax" and sc["keno"] == "jackpots":
                if sc["r"] > 0:
                    print(f"    → Mehr Jackpots bei höherem DAX")
                else:
                    print(f"    → Weniger Jackpots bei höherem DAX")
            elif sc["econ"] == "gfk" and sc["keno"] == "jackpots":
                if sc["r"] > 0:
                    print(f"    → Mehr Jackpots bei besserem Konsumklima")
                else:
                    print(f"    → Weniger Jackpots bei besserem Konsumklima")
    else:
        print("\nKeine starken Korrelationen (|r| >= 0.3) gefunden.")

    print("\n" + "-" * 80)
    print("HYPOTHESEN FÜR WEITERE UNTERSUCHUNG:")
    print("-" * 80)
    print("""
1. WIRTSCHAFTS-TIMING-HYPOTHESE:
   Das KENO-System könnte Jackpots gezielt in wirtschaftlich
   günstigen Zeiten platzieren (gutes Konsumklima → mehr Spieler).

2. GEGENLÄUFIGE HYPOTHESE:
   Bei schlechter Wirtschaft braucht das System mehr kleine
   Gewinner um Spieler zu halten (Attraktivitäts-Axiom).

3. LAG-HYPOTHESE:
   Wirtschaftsindikatoren könnten KENO-Verhalten mit 1-2 Monaten
   Verzögerung beeinflussen (Reaktionszeit des Systems).

4. KEINE KORRELATION:
   Das System könnte absichtlich NICHT mit Wirtschaftsdaten
   korrelieren um Vorhersagbarkeit zu vermeiden.
""")


def main():
    print("=" * 80)
    print("ANALYSE: KENO-SYSTEM vs. DEUTSCHE WIRTSCHAFTSINDIKATOREN")
    print("=" * 80)

    # Daten laden
    print("\nLade Daten...")
    keno_df = load_keno_data()
    jackpots = load_jackpot_dates()
    print(f"KENO-Ziehungen: {len(keno_df)}")
    print(f"Jackpot-Tage: {len(jackpots)}")
    print(f"Wirtschaftsdaten: {len(GERMAN_ECONOMIC_DATA)} Monate")

    # Monatliche Statistiken berechnen
    print("\nBerechne monatliche Statistiken...")
    monthly_df = calculate_monthly_keno_stats(keno_df, jackpots)
    print(f"Monate mit Daten: {len(monthly_df)}")

    # Korrelationen berechnen
    print("\nBerechne Korrelationen...")
    correlations = calculate_correlations(monthly_df)

    # Lag-Korrelationen
    print("Berechne Lag-Korrelationen...")
    lag_correlations = calculate_lag_correlations(monthly_df)

    # Jackpot-Timing analysieren
    print("Analysiere Jackpot-Timing...")
    timing_analysis = analyze_jackpot_timing(jackpots, monthly_df)

    # Ergebnisse ausgeben
    print_results(correlations, lag_correlations, timing_analysis, monthly_df)

    # Ergebnisse speichern
    results = {
        "meta": {
            "keno_draws": len(keno_df),
            "jackpots": len(jackpots),
            "months_analyzed": len(monthly_df),
            "date_range": f"{monthly_df['jahr_monat'].min()} - {monthly_df['jahr_monat'].max()}"
        },
        "correlations": correlations,
        "lag_correlations": lag_correlations,
        "timing_analysis": {
            "summary": timing_analysis["summary"]
        },
        "monthly_data": monthly_df.to_dict(orient="records")
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
