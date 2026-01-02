#!/usr/bin/env python
"""
Analyse der Kyritz KENO-Gewinner Zahlen gegen alle Ziehungen 2022-2025.

Gewinnzahlen vom 27.10.2025: [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lade KENO-Daten aus CSV."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df.sort_values("Datum").reset_index(drop=True)


def analyze_winner_numbers(df: pd.DataFrame, winner_numbers: list, start_date: datetime, end_date: datetime):
    """
    Analysiere wie oft die Gewinnzahlen in jeder Ziehung vorkamen.

    Returns:
        List of dicts with analysis results
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    winner_set = set(winner_numbers)

    # Filter auf Zeitraum
    mask = (df["Datum"] >= start_date) & (df["Datum"] <= end_date)
    period_df = df[mask].copy()

    # Kumulative Treffer pro Zahl tracken
    cumulative_hits = {num: 0 for num in winner_numbers}

    results = []

    for _, row in period_df.iterrows():
        date = row["Datum"]
        drawn = set(int(row[col]) for col in pos_cols)

        # Treffer finden
        hits = winner_set & drawn
        hit_count = len(hits)
        hit_numbers = sorted(list(hits))

        # Kumulative Hits aktualisieren
        for num in hits:
            cumulative_hits[num] += 1

        # Kumulative Hits String erstellen
        cum_str = " ".join([f"[{num}:{cumulative_hits[num]}]" for num in winner_numbers])

        result = {
            "Datum": date.strftime("%d.%m.%Y"),
            "Wochentag": date.strftime("%a"),
            "Treffer": hit_count,
            "Treffer_Zahlen": hit_numbers,
            "Kumulativ": cum_str,
        }
        results.append(result)

    return results, cumulative_hits


def write_markdown(results: list, winner_numbers: list, cumulative_hits: dict, output_path: Path):
    """Schreibe Ergebnisse als Markdown-Datei."""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# KENO Gewinner-Zahlen Analyse: Kyritz (Brandenburg)\n\n")
        f.write("## Gewinnzahlen vom 27.10.2025\n\n")
        f.write(f"**Zahlen:** `{winner_numbers}`\n\n")
        f.write("**Gewinn:** 100.000 EUR (Typ 10 - 10/10)\n\n")
        f.write("---\n\n")

        # Zusammenfassung
        f.write("## Zusammenfassung\n\n")
        f.write("### Kumulative Treffer pro Zahl (2022-2025)\n\n")
        f.write("| Zahl | Treffer | Anteil |\n")
        f.write("|------|---------|--------|\n")
        total_draws = len(results)
        for num in winner_numbers:
            hits = cumulative_hits[num]
            pct = (hits / total_draws) * 100
            f.write(f"| {num} | {hits} | {pct:.1f}% |\n")
        f.write(f"\n**Gesamt Ziehungen:** {total_draws}\n\n")

        # Treffer-Verteilung
        f.write("### Treffer-Verteilung\n\n")
        hit_counts = {}
        for r in results:
            cnt = r["Treffer"]
            hit_counts[cnt] = hit_counts.get(cnt, 0) + 1

        f.write("| Treffer | Anzahl Tage | Anteil |\n")
        f.write("|---------|-------------|--------|\n")
        for cnt in sorted(hit_counts.keys(), reverse=True):
            days = hit_counts[cnt]
            pct = (days / total_draws) * 100
            f.write(f"| {cnt}/10 | {days} | {pct:.1f}% |\n")

        # Highlight: Tage mit 6+ Treffern
        f.write("\n---\n\n")
        f.write("## Tage mit 6+ Treffern\n\n")
        f.write("| Datum | Wochentag | Treffer | Treffer-Zahlen | Kumulativ |\n")
        f.write("|-------|-----------|---------|----------------|----------|\n")
        for r in results:
            if r["Treffer"] >= 6:
                zahlen_str = ", ".join(map(str, r["Treffer_Zahlen"]))
                f.write(f"| {r['Datum']} | {r['Wochentag']} | **{r['Treffer']}** | {zahlen_str} | {r['Kumulativ']} |\n")

        # Alle Ergebnisse
        f.write("\n---\n\n")
        f.write("## Alle Ziehungen (2022-2025)\n\n")
        f.write("| Datum | Tag | Treffer | Treffer-Zahlen | Kumulativ |\n")
        f.write("|-------|-----|---------|----------------|----------|\n")

        for r in results:
            zahlen_str = ", ".join(map(str, r["Treffer_Zahlen"])) if r["Treffer_Zahlen"] else "-"
            treffer_display = f"**{r['Treffer']}**" if r["Treffer"] >= 5 else str(r["Treffer"])
            f.write(f"| {r['Datum']} | {r['Wochentag']} | {treffer_display} | {zahlen_str} | {r['Kumulativ']} |\n")

        f.write("\n---\n\n")
        f.write(f"*Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n")


def main():
    base_path = Path(__file__).parent.parent

    # Kyritz Gewinnzahlen
    winner_numbers = [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]

    print("Lade KENO-Daten...")
    df = load_keno_data(base_path)

    print("Analysiere Gewinnzahlen gegen alle Ziehungen...")
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 12, 31)

    results, cumulative_hits = analyze_winner_numbers(df, winner_numbers, start_date, end_date)

    # Statistiken
    print(f"\nZiehungen analysiert: {len(results)}")
    print(f"\nKumulative Treffer pro Zahl:")
    for num in winner_numbers:
        print(f"  {num:2d}: {cumulative_hits[num]} Treffer")

    # Treffer-Verteilung
    hit_counts = {}
    for r in results:
        cnt = r["Treffer"]
        hit_counts[cnt] = hit_counts.get(cnt, 0) + 1

    print(f"\nTreffer-Verteilung:")
    for cnt in sorted(hit_counts.keys(), reverse=True):
        print(f"  {cnt}/10: {hit_counts[cnt]} Tage")

    # Markdown schreiben
    output_path = base_path / "results" / "kyritz_winner_analysis.md"
    print(f"\nSchreibe Ergebnisse nach: {output_path}")
    write_markdown(results, winner_numbers, cumulative_hits, output_path)

    print("\nFertig!")


if __name__ == "__main__":
    main()
