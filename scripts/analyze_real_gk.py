#!/usr/bin/env python
"""
Analyse der echten KENO Gewinnklassen-Auszahlungen 2025
=======================================================

Analysiert wie oft die Top-Gewinnklassen (Jackpots, GK2, GK3)
tatsächlich ausgezahlt wurden - pro Monat und Typ.

Autor: Think Tank
Datum: 2025-12-31
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

BASE_DIR = Path(__file__).parent.parent
GQ_2025 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"
GQ_2024 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2024.csv"


def parse_date(date_str):
    """Parst das Datum aus dem Format 'So, 28.12.' """
    # Extrahiere Tag und Monat
    match = re.search(r'(\d+)\.(\d+)\.', date_str)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        return day, month
    return None, None


def load_gq_data(filepath):
    """Lädt und bereinigt die GQ-Daten."""
    df = pd.read_csv(filepath, encoding='utf-8')

    # Bereinige Spalten
    df.columns = ['Datum', 'Keno_Typ', 'Richtige', 'Anzahl_Gewinner', 'Gewinn']

    # Filtere nur die Hauptgewinnzeilen (nicht die Plus5 Zeilen)
    df = df[~df['Richtige'].astype(str).str.contains('Gewinnklasse')]

    # Konvertiere Typen
    df['Keno_Typ'] = pd.to_numeric(df['Keno_Typ'], errors='coerce')
    df['Richtige'] = pd.to_numeric(df['Richtige'], errors='coerce')

    # Parse Anzahl Gewinner (kann "1.647" sein)
    df['Anzahl_Gewinner'] = df['Anzahl_Gewinner'].astype(str).str.replace('.', '', regex=False)
    df['Anzahl_Gewinner'] = pd.to_numeric(df['Anzahl_Gewinner'], errors='coerce').fillna(0).astype(int)

    # Parse Datum
    df['Tag'], df['Monat'] = zip(*df['Datum'].apply(parse_date))

    # Filtere ungültige Zeilen
    df = df.dropna(subset=['Keno_Typ', 'Richtige', 'Tag', 'Monat'])

    return df


def analyze_top_gk(df, year):
    """Analysiert die Top-Gewinnklassen pro Monat."""

    print(f"\n{'='*80}")
    print(f"ECHTE KENO GEWINNKLASSEN-AUSZAHLUNGEN {year}")
    print(f"{'='*80}")

    # Gewinnklassen-Definition
    gk_definitions = {
        6: {6: "GK1 (6/6)", 5: "GK2 (5/6)", 4: "GK3 (4/6)"},
        7: {7: "GK1 (7/7)", 6: "GK2 (6/7)", 5: "GK3 (5/7)"},
        8: {8: "GK1 (8/8)", 7: "GK2 (7/8)", 6: "GK3 (6/8)"},
        9: {9: "GK1 (9/9)", 8: "GK2 (8/9)", 7: "GK3 (7/9)"},
        10: {10: "GK1 (10/10)", 9: "GK2 (9/10)", 8: "GK3 (8/10)"},
    }

    # Quoten
    quotes = {
        6: {6: 500, 5: 15, 4: 2},
        7: {7: 5000, 6: 100, 5: 12},
        8: {8: 10000, 7: 100, 6: 15},
        9: {9: 50000, 8: 1000, 7: 20},
        10: {10: 100000, 9: 1000, 8: 100},
    }

    for keno_typ in [6, 7, 8, 9, 10]:
        print(f"\n{'#'*80}")
        print(f"# TYP {keno_typ} - ECHTE AUSZAHLUNGEN {year}")
        print(f"{'#'*80}")

        df_typ = df[df['Keno_Typ'] == keno_typ].copy()

        if len(df_typ) == 0:
            print("  Keine Daten verfügbar")
            continue

        # Monatliche Zusammenfassung
        monthly_data = defaultdict(lambda: defaultdict(int))

        for _, row in df_typ.iterrows():
            monat = int(row['Monat'])
            richtige = int(row['Richtige'])
            gewinner = int(row['Anzahl_Gewinner'])

            if richtige in gk_definitions[keno_typ]:
                monthly_data[monat][richtige] += gewinner

        # Header
        gk_cols = sorted(gk_definitions[keno_typ].keys(), reverse=True)
        header = f"{'Monat':<8}"
        for gk in gk_cols:
            gk_name = gk_definitions[keno_typ][gk]
            quote = quotes[keno_typ][gk]
            header += f" {gk_name} ({quote}€)"
            header = header.ljust(len(header) + 5)
        print(f"\n{header}")
        print("-" * len(header))

        # Monate
        monatsnamen = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

        yearly_totals = {gk: 0 for gk in gk_cols}

        for monat in range(1, 13):
            if monat not in monthly_data:
                continue

            row_str = f"{monatsnamen[monat]:<8}"
            for gk in gk_cols:
                count = monthly_data[monat].get(gk, 0)
                yearly_totals[gk] += count
                row_str += f" {count:>8}"
                row_str = row_str.ljust(len(row_str) + 12)

            print(row_str)

        # Summe
        print("-" * len(header))
        sum_row = f"{'SUMME':<8}"
        for gk in gk_cols:
            sum_row += f" {yearly_totals[gk]:>8}"
            sum_row = sum_row.ljust(len(sum_row) + 12)
        print(sum_row)

        # Durchschnitt pro Monat
        n_months = len(monthly_data)
        if n_months > 0:
            print(f"\nDurchschnitt pro Monat (bei {n_months} Monaten Daten):")
            for gk in gk_cols:
                avg = yearly_totals[gk] / n_months
                gk_name = gk_definitions[keno_typ][gk]
                quote = quotes[keno_typ][gk]
                if avg >= 1:
                    print(f"  {gk_name}: {avg:.1f} Gewinner/Monat × {quote}€ = {avg * quote:,.0f}€/Monat")
                else:
                    interval = 1/avg if avg > 0 else float('inf')
                    print(f"  {gk_name}: 1 Gewinner alle {interval:.1f} Monate × {quote}€")


def compare_gk8(df_2024, df_2025):
    """Vergleicht GK8 (Typ 8) zwischen 2024 und 2025."""

    print(f"\n\n{'='*80}")
    print(f"FOKUS: TYP 8 - Vergleich der echten Gewinner")
    print(f"{'='*80}")

    for year, df in [("2024", df_2024), ("2025", df_2025)]:
        print(f"\n--- {year} ---")

        df_typ8 = df[(df['Keno_Typ'] == 8)].copy()

        if len(df_typ8) == 0:
            print("  Keine Daten")
            continue

        # Zähle Gewinner pro Gewinnklasse
        for richtige in [8, 7, 6]:
            df_gk = df_typ8[df_typ8['Richtige'] == richtige]
            total_winners = df_gk['Anzahl_Gewinner'].sum()

            n_days = df_gk['Datum'].nunique()
            days_with_winners = (df_gk['Anzahl_Gewinner'] > 0).sum()

            quote = {8: 10000, 7: 100, 6: 15}[richtige]

            print(f"\n  GK{9-richtige} ({richtige}/8 = {quote}€):")
            print(f"    Gesamt Gewinner: {total_winners:,}")
            print(f"    Ziehungen: {n_days}")
            print(f"    Gewinner/Ziehung: {total_winners/n_days:.2f}" if n_days > 0 else "    N/A")
            print(f"    Auszahlungssumme: {total_winners * quote:,}€")


def main():
    print("=" * 80)
    print("ANALYSE DER ECHTEN KENO GEWINNKLASSEN")
    print("Wie oft wurden die Top-GK tatsächlich ausgezahlt?")
    print("=" * 80)

    # Lade 2025 Daten
    print("\nLade Keno_GQ_2025.csv...")
    df_2025 = load_gq_data(GQ_2025)
    print(f"  Geladene Zeilen: {len(df_2025)}")

    # Lade 2024 Daten falls vorhanden
    df_2024 = None
    if GQ_2024.exists():
        print("\nLade Keno_GQ_2024.csv...")
        df_2024 = load_gq_data(GQ_2024)
        print(f"  Geladene Zeilen: {len(df_2024)}")

    # Analysiere 2025
    analyze_top_gk(df_2025, 2025)

    # Analysiere 2024 falls vorhanden
    if df_2024 is not None:
        analyze_top_gk(df_2024, 2024)

    # Vergleich TYP 8
    if df_2024 is not None:
        compare_gk8(df_2024, df_2025)

    # ZUSAMMENFASSUNG für Typ 8
    print(f"\n\n{'='*80}")
    print("ZUSAMMENFASSUNG: TYP 8 - Was kann man realistisch erwarten?")
    print("=" * 80)

    df_typ8 = df_2025[df_2025['Keno_Typ'] == 8]

    for richtige, quote, name in [(8, 10000, "JACKPOT"), (7, 100, "GK2"), (6, 15, "GK3")]:
        df_gk = df_typ8[df_typ8['Richtige'] == richtige]
        total = df_gk['Anzahl_Gewinner'].sum()
        n_draws = df_gk['Datum'].nunique()

        if n_draws > 0:
            per_draw = total / n_draws
            per_month = per_draw * 30

            print(f"\n{name} ({richtige}/8 = {quote}€):")
            print(f"  In {n_draws} Ziehungen: {total:,} Gewinner gesamt")
            print(f"  Pro Ziehung: {per_draw:.2f} Gewinner")
            print(f"  Pro Monat (~30 Ziehungen): {per_month:.1f} Gewinner")

            if per_draw > 0:
                # Wahrscheinlichkeit dass EIN Ticket gewinnt
                # Annahme: ~50.000 Typ-8 Tickets pro Ziehung
                tickets_per_draw = 50000  # Schätzung
                win_prob = per_draw / tickets_per_draw
                print(f"  Geschätzte Gewinnchance: 1:{1/win_prob:,.0f}")


if __name__ == "__main__":
    main()
