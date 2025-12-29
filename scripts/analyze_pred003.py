#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PRED-003: Jackpot-Korrelation mit Near-Miss Ratio

Hypothese: Wenn der akkumulierte Jackpot hoch ist, sinkt die Near-Miss Ratio
(weil mehr Max-Gewinne "erlaubt" werden).

Analyse:
- Near-Miss Ratio fuer Typ 9: Gewinner GK2 (8 Richtige) / Gewinner GK1 (9 Richtige)
- Jackpot-Proxy: Tage seit letztem GK1-Gewinner (9 Richtige bei Typ 9)
- Korrelation: Pearson und Spearman
"""

import json
import os
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from pathlib import Path


def load_gewinnquoten(filepath: str) -> pd.DataFrame:
    """Lade Gewinnquoten-Daten."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')

    # Parse Datum
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Konvertiere Anzahl der Gewinner (kann Punkt als Tausendertrennzeichen haben)
    df['Anzahl der Gewinner'] = df['Anzahl der Gewinner'].apply(
        lambda x: float(str(x).replace('.', '').replace(',', '.')) if pd.notna(x) else 0
    )

    return df


def load_restbetrag(filepath: str) -> pd.DataFrame:
    """Lade Restbetrag-Daten als zusaetzliche Quelle."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig')

    # Parse Datum
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    return df


def calculate_near_miss_ratio_type9(gq_df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechne Near-Miss Ratio fuer Keno Typ 9.

    Near-Miss Ratio = Gewinner mit 8 Richtigen / Gewinner mit 9 Richtigen

    Bei 0 Gewinnern mit 9 Richtigen setzen wir den Wert auf NaN.
    """
    # Filtere nur Typ 9
    typ9 = gq_df[gq_df['Keno-Typ'] == 9].copy()

    # Pivot: Datum x Anzahl richtiger Zahlen
    pivot = typ9.pivot_table(
        index='Datum',
        columns='Anzahl richtiger Zahlen',
        values='Anzahl der Gewinner',
        aggfunc='first'
    ).reset_index()

    # Near-Miss Ratio: 8 Richtige / 9 Richtige
    pivot['gk1_winners'] = pivot[9] if 9 in pivot.columns else 0  # 9 Richtige (Max)
    pivot['gk2_winners'] = pivot[8] if 8 in pivot.columns else 0  # 8 Richtige (Near-Miss)

    # Near-Miss Ratio berechnen
    # Wenn GK1 = 0, dann ist Jackpot-Effekt aktiv (kein Max-Gewinner)
    pivot['near_miss_ratio'] = pivot.apply(
        lambda row: row['gk2_winners'] / row['gk1_winners'] if row['gk1_winners'] > 0 else np.nan,
        axis=1
    )

    # Markiere ob GK1-Gewinner vorhanden
    pivot['has_gk1_winner'] = pivot['gk1_winners'] > 0

    return pivot[['Datum', 'gk1_winners', 'gk2_winners', 'near_miss_ratio', 'has_gk1_winner']]


def calculate_jackpot_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechne Jackpot-Proxy: Tage seit letztem GK1-Gewinner.

    Je mehr Tage ohne GK1-Gewinner, desto hoeher der akkumulierte Jackpot.
    """
    df = df.sort_values('Datum').copy()

    # Berechne Tage seit letztem GK1-Gewinner
    days_since_gk1 = []
    last_gk1_date = None

    for idx, row in df.iterrows():
        if last_gk1_date is None:
            days_since_gk1.append(0)
        else:
            days_since_gk1.append((row['Datum'] - last_gk1_date).days)

        if row['has_gk1_winner']:
            last_gk1_date = row['Datum']

    df['days_since_gk1'] = days_since_gk1

    # Berechne auch rollende Summe von GK1-losen Tagen als alternativen Proxy
    df['cumulative_no_gk1'] = (~df['has_gk1_winner']).cumsum()

    return df


def calculate_restbetrag_proxy(gq_df: pd.DataFrame, rest_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Restbetrag-Daten als alternativen Jackpot-Proxy.

    Restbetrag_nach_Auszahlung repraesentiert den akkumulierten Pool.
    """
    # Merge auf Datum
    merged = gq_df.merge(
        rest_df[['Datum', 'Restbetrag_nach_Auszahlung', 'Kasse']],
        on='Datum',
        how='left'
    )

    return merged


def analyze_pred003(
    gq_path: str,
    rest_path: str,
    output_path: str
) -> dict:
    """
    Hauptanalyse fuer PRED-003.
    """
    print("=" * 60)
    print("PRED-003: Jackpot-Korrelation mit Near-Miss Ratio")
    print("=" * 60)

    # Lade Daten
    print("\n[1] Lade Gewinnquoten-Daten...")
    gq_df = load_gewinnquoten(gq_path)
    print(f"    Geladen: {len(gq_df)} Zeilen, Datum-Range: {gq_df['Datum'].min()} bis {gq_df['Datum'].max()}")

    print("\n[2] Lade Restbetrag-Daten...")
    rest_df = load_restbetrag(rest_path)
    print(f"    Geladen: {len(rest_df)} Zeilen, Datum-Range: {rest_df['Datum'].min()} bis {rest_df['Datum'].max()}")

    # Berechne Near-Miss Ratio
    print("\n[3] Berechne Near-Miss Ratio fuer Typ 9...")
    nm_df = calculate_near_miss_ratio_type9(gq_df)
    print(f"    Ziehungen mit GK1-Gewinnern: {nm_df['has_gk1_winner'].sum()} von {len(nm_df)}")
    print(f"    Ziehungen ohne GK1-Gewinner: {(~nm_df['has_gk1_winner']).sum()}")

    # Berechne Jackpot-Proxy
    print("\n[4] Berechne Jackpot-Proxy (Tage seit GK1)...")
    nm_df = calculate_jackpot_proxy(nm_df)

    # Merge mit Restbetrag
    print("\n[5] Merge mit Restbetrag-Daten...")
    nm_df = calculate_restbetrag_proxy(nm_df, rest_df)

    # Analysiere Korrelation
    print("\n[6] Berechne Korrelationen...")

    results = {
        "hypothesis": "PRED-003",
        "description": "Hoher Jackpot korreliert mit niedriger Near-Miss Ratio",
        "expected_correlation": "negative",
        "analysis_date": datetime.now().isoformat(),
        "data_sources": {
            "gewinnquoten": gq_path,
            "restbetrag": rest_path
        },
        "sample_sizes": {},
        "correlations": {},
        "conclusion": {}
    }

    # Korrelation 1: days_since_gk1 vs near_miss_ratio
    # Nur Zeilen wo beide Werte vorhanden sind
    valid_days = nm_df[['days_since_gk1', 'near_miss_ratio']].dropna()

    if len(valid_days) >= 10:
        pearson_days, p_pearson_days = stats.pearsonr(
            valid_days['days_since_gk1'],
            valid_days['near_miss_ratio']
        )
        spearman_days, p_spearman_days = stats.spearmanr(
            valid_days['days_since_gk1'],
            valid_days['near_miss_ratio']
        )

        results["correlations"]["days_since_gk1_vs_near_miss"] = {
            "pearson_r": round(pearson_days, 4),
            "pearson_p": round(p_pearson_days, 6),
            "spearman_rho": round(spearman_days, 4),
            "spearman_p": round(p_spearman_days, 6),
            "sample_size": len(valid_days),
            "significant_p05": p_spearman_days < 0.05
        }
        results["sample_sizes"]["days_since_gk1"] = len(valid_days)

        print(f"\n    [days_since_gk1 vs near_miss_ratio]")
        print(f"    Pearson r = {pearson_days:.4f}, p = {p_pearson_days:.6f}")
        print(f"    Spearman rho = {spearman_days:.4f}, p = {p_spearman_days:.6f}")
        print(f"    N = {len(valid_days)}")

    # Korrelation 2: Restbetrag vs near_miss_ratio (wenn vorhanden)
    valid_rest = nm_df[['Restbetrag_nach_Auszahlung', 'near_miss_ratio']].dropna()

    if len(valid_rest) >= 10:
        pearson_rest, p_pearson_rest = stats.pearsonr(
            valid_rest['Restbetrag_nach_Auszahlung'],
            valid_rest['near_miss_ratio']
        )
        spearman_rest, p_spearman_rest = stats.spearmanr(
            valid_rest['Restbetrag_nach_Auszahlung'],
            valid_rest['near_miss_ratio']
        )

        results["correlations"]["restbetrag_vs_near_miss"] = {
            "pearson_r": round(pearson_rest, 4),
            "pearson_p": round(p_pearson_rest, 6),
            "spearman_rho": round(spearman_rest, 4),
            "spearman_p": round(p_spearman_rest, 6),
            "sample_size": len(valid_rest),
            "significant_p05": p_spearman_rest < 0.05
        }
        results["sample_sizes"]["restbetrag"] = len(valid_rest)

        print(f"\n    [Restbetrag vs near_miss_ratio]")
        print(f"    Pearson r = {pearson_rest:.4f}, p = {p_pearson_rest:.6f}")
        print(f"    Spearman rho = {spearman_rest:.4f}, p = {p_spearman_rest:.6f}")
        print(f"    N = {len(valid_rest)}")

    # Korrelation 3: Kasse (kumulierter Pool) vs near_miss_ratio
    valid_kasse = nm_df[['Kasse', 'near_miss_ratio']].dropna()

    if len(valid_kasse) >= 10:
        pearson_kasse, p_pearson_kasse = stats.pearsonr(
            valid_kasse['Kasse'],
            valid_kasse['near_miss_ratio']
        )
        spearman_kasse, p_spearman_kasse = stats.spearmanr(
            valid_kasse['Kasse'],
            valid_kasse['near_miss_ratio']
        )

        results["correlations"]["kasse_vs_near_miss"] = {
            "pearson_r": round(pearson_kasse, 4),
            "pearson_p": round(p_pearson_kasse, 6),
            "spearman_rho": round(spearman_kasse, 4),
            "spearman_p": round(p_spearman_kasse, 6),
            "sample_size": len(valid_kasse),
            "significant_p05": p_spearman_kasse < 0.05
        }
        results["sample_sizes"]["kasse"] = len(valid_kasse)

        print(f"\n    [Kasse (kumuliert) vs near_miss_ratio]")
        print(f"    Pearson r = {pearson_kasse:.4f}, p = {p_pearson_kasse:.6f}")
        print(f"    Spearman rho = {spearman_kasse:.4f}, p = {p_spearman_kasse:.6f}")
        print(f"    N = {len(valid_kasse)}")

    # Zusatzanalyse: Vergleiche Near-Miss Ratio bei hohem vs niedrigem Jackpot
    print("\n[7] Gruppenvergleich: Hoher vs niedriger Jackpot...")

    if len(valid_days) >= 20:
        median_days = valid_days['days_since_gk1'].median()
        high_jackpot = valid_days[valid_days['days_since_gk1'] >= median_days]['near_miss_ratio']
        low_jackpot = valid_days[valid_days['days_since_gk1'] < median_days]['near_miss_ratio']

        # Mann-Whitney U Test
        if len(high_jackpot) >= 5 and len(low_jackpot) >= 5:
            u_stat, u_pvalue = stats.mannwhitneyu(high_jackpot, low_jackpot, alternative='two-sided')

            results["group_comparison"] = {
                "high_jackpot_n": len(high_jackpot),
                "high_jackpot_mean_nmr": round(high_jackpot.mean(), 4),
                "high_jackpot_median_nmr": round(high_jackpot.median(), 4),
                "low_jackpot_n": len(low_jackpot),
                "low_jackpot_mean_nmr": round(low_jackpot.mean(), 4),
                "low_jackpot_median_nmr": round(low_jackpot.median(), 4),
                "median_split_days": round(median_days, 1),
                "mann_whitney_u": round(u_stat, 2),
                "mann_whitney_p": round(u_pvalue, 6),
                "significant_p05": u_pvalue < 0.05
            }

            print(f"    Median-Split bei {median_days:.0f} Tagen")
            print(f"    Hoher Jackpot (>= Median): N={len(high_jackpot)}, Mean NMR={high_jackpot.mean():.2f}")
            print(f"    Niedriger Jackpot (< Median): N={len(low_jackpot)}, Mean NMR={low_jackpot.mean():.2f}")
            print(f"    Mann-Whitney U = {u_stat:.2f}, p = {u_pvalue:.6f}")

    # Fazit
    print("\n" + "=" * 60)
    print("FAZIT")
    print("=" * 60)

    # Bestimme ob Hypothese bestaetigt wird
    hypothesis_confirmed = False
    primary_correlation = None
    primary_p_value = None

    if "days_since_gk1_vs_near_miss" in results["correlations"]:
        corr_data = results["correlations"]["days_since_gk1_vs_near_miss"]
        primary_correlation = corr_data["spearman_rho"]
        primary_p_value = corr_data["spearman_p"]

        # Hypothese bestaetigt wenn:
        # 1. Korrelation signifikant negativ (p < 0.05, r < 0)
        if primary_p_value < 0.05 and primary_correlation < 0:
            hypothesis_confirmed = True
            conclusion_text = (
                f"BESTAETIGT: Signifikante negative Korrelation gefunden. "
                f"Spearman rho = {primary_correlation:.4f}, p = {primary_p_value:.6f}. "
                f"Hoeherer Jackpot-Proxy korreliert mit niedrigerer Near-Miss Ratio."
            )
        elif primary_p_value >= 0.05:
            conclusion_text = (
                f"FALSIFIZIERT: Keine signifikante Korrelation gefunden. "
                f"Spearman rho = {primary_correlation:.4f}, p = {primary_p_value:.6f}. "
                f"Der Zusammenhang ist statistisch nicht nachweisbar."
            )
        else:
            conclusion_text = (
                f"FALSIFIZIERT: Korrelation ist positiv statt negativ. "
                f"Spearman rho = {primary_correlation:.4f}, p = {primary_p_value:.6f}. "
                f"Dies widerspricht der Hypothese."
            )
    else:
        conclusion_text = "NICHT TESTBAR: Nicht genuegend Daten fuer Korrelationsanalyse."

    results["conclusion"] = {
        "hypothesis_confirmed": hypothesis_confirmed,
        "primary_metric": "spearman_rho",
        "primary_correlation": primary_correlation,
        "primary_p_value": primary_p_value,
        "significance_level": 0.05,
        "interpretation": conclusion_text
    }

    print(f"\n{conclusion_text}")

    # Deskriptive Statistiken hinzufuegen
    results["descriptive_stats"] = {
        "total_draws_analyzed": len(nm_df),
        "draws_with_gk1_winner": int(nm_df['has_gk1_winner'].sum()),
        "draws_without_gk1_winner": int((~nm_df['has_gk1_winner']).sum()),
        "near_miss_ratio_mean": round(nm_df['near_miss_ratio'].mean(), 4) if nm_df['near_miss_ratio'].notna().any() else None,
        "near_miss_ratio_std": round(nm_df['near_miss_ratio'].std(), 4) if nm_df['near_miss_ratio'].notna().any() else None,
        "near_miss_ratio_min": round(nm_df['near_miss_ratio'].min(), 4) if nm_df['near_miss_ratio'].notna().any() else None,
        "near_miss_ratio_max": round(nm_df['near_miss_ratio'].max(), 4) if nm_df['near_miss_ratio'].notna().any() else None,
        "days_since_gk1_mean": round(nm_df['days_since_gk1'].mean(), 2),
        "days_since_gk1_max": int(nm_df['days_since_gk1'].max())
    }

    # Speichere Ergebnisse
    print(f"\n[8] Speichere Ergebnisse nach: {output_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n    Ergebnisse gespeichert!")

    return results


if __name__ == "__main__":
    # Pfade
    base_path = Path(__file__).parent.parent
    gq_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    rest_path = base_path / "Keno_GPTs" / "Keno_Ziehung2023_+_Restbetrag_v2.CSV"
    output_path = base_path / "results" / "pred003_jackpot_correlation.json"

    results = analyze_pred003(
        str(gq_path),
        str(rest_path),
        str(output_path)
    )
