#!/usr/bin/env python3
"""
TASK-RE02: Popularity Reverse Engineering

Schliesse aus den Gewinnquoten-Daten (Anzahl der Gewinner) auf die
POPULARITAET der gezogenen Zahlen zurueck.

Kernidee:
- Viele Gewinner bei 8/10 richtig -> Gezogene Zahlen waren BELIEBT
- Wenige Gewinner bei 8/10 richtig -> Gezogene Zahlen waren UNBELIEBT
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class PopularityResult:
    """Ergebnis der Popularitaetsanalyse."""

    number: int
    popularity_score: float  # Negativ = unpopulaer, Positiv = populaer
    times_in_popular: int
    times_in_unpopular: int
    times_in_neutral: int
    total_draws: int
    draw_frequency: float  # Wie oft gezogen (relativ)


@dataclass
class DayClassification:
    """Klassifikation eines Ziehungstages."""

    date: str
    drawn_numbers: list[int]
    winners_8of10: float
    normalized_winners: float
    classification: str  # POPULAR, NEUTRAL, UNPOPULAR
    stake: Optional[float] = None


def parse_german_number(value: str) -> float:
    """Parst deutsche Zahlenformate (1.234,56 -> 1234.56)."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # Entferne Waehrungssymbole und Leerzeichen
    value = str(value).replace("€", "").replace(" ", "").strip()
    # Deutsche Notation: 1.234,56 -> 1234.56
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0


def load_gq_files(gq_paths: list[Path]) -> pd.DataFrame:
    """Laedt und kombiniert alle Gewinnquoten-Dateien."""
    all_data = []

    for path in gq_paths:
        if not path.exists():
            print(f"  [WARN] Datei nicht gefunden: {path}")
            continue

        print(f"  Lade: {path.name}")

        # Versuche verschiedene Trennzeichen
        for sep in [",", ";"]:
            try:
                df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
                if len(df.columns) >= 4:
                    break
            except Exception:
                continue

        # Spalten normalisieren
        df.columns = [c.strip() for c in df.columns]

        # Datum-Spalte finden und normalisieren
        date_col = None
        for col in df.columns:
            if "datum" in col.lower() or "date" in col.lower():
                date_col = col
                break

        if date_col is None:
            print(f"    [WARN] Keine Datum-Spalte gefunden in {path.name}")
            continue

        # Relevante Spalten extrahieren
        result = pd.DataFrame()
        result["Datum"] = df[date_col]

        # Keno-Typ finden
        for col in df.columns:
            if "typ" in col.lower():
                result["Keno_Typ"] = pd.to_numeric(df[col], errors="coerce")
                break

        # Anzahl richtiger Zahlen
        for col in df.columns:
            if "richtig" in col.lower():
                result["Richtige"] = pd.to_numeric(df[col], errors="coerce")
                break

        # Anzahl der Gewinner
        for col in df.columns:
            if "gewinner" in col.lower() and "anzahl" in col.lower():
                result["Gewinner"] = df[col].apply(parse_german_number)
                break
            elif "gewinner" in col.lower():
                result["Gewinner"] = df[col].apply(parse_german_number)
                break

        if "Gewinner" not in result.columns:
            print(f"    [WARN] Keine Gewinner-Spalte gefunden in {path.name}")
            continue

        result["Quelle"] = path.name
        all_data.append(result)
        print(f"    -> {len(result)} Zeilen geladen")

    if not all_data:
        raise ValueError("Keine GQ-Daten geladen!")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"\nGesamt GQ-Daten: {len(combined)} Zeilen")

    return combined


def load_draw_data(draw_path: Path) -> pd.DataFrame:
    """Laedt die Ziehungsdaten."""
    print(f"\nLade Ziehungsdaten: {draw_path.name}")

    # Versuche verschiedene Trennzeichen
    for sep in [";", ","]:
        try:
            df = pd.read_csv(draw_path, sep=sep, encoding="utf-8-sig")
            if len(df.columns) >= 21:
                break
        except Exception:
            continue

    # Spalten normalisieren
    df.columns = [c.strip() for c in df.columns]

    # Datum-Spalte
    date_col = df.columns[0]  # Erste Spalte ist Datum

    # Zahlen-Spalten (Z1-Z20 oder Keno_Z1-Keno_Z20)
    number_cols = []
    for col in df.columns:
        if "z" in col.lower() and any(c.isdigit() for c in col):
            # Pruefe ob es eine Zahl zwischen 1-20 ist
            num_part = "".join(c for c in col if c.isdigit())
            if num_part and 1 <= int(num_part) <= 20:
                number_cols.append(col)

    number_cols = sorted(number_cols, key=lambda x: int("".join(c for c in x if c.isdigit())))[:20]

    if len(number_cols) < 20:
        print(f"  [WARN] Nur {len(number_cols)} Zahlen-Spalten gefunden")

    # Spieleinsatz-Spalte
    stake_col = None
    for col in df.columns:
        if "einsatz" in col.lower() or "spieleinsatz" in col.lower():
            stake_col = col
            break

    result = pd.DataFrame()
    result["Datum"] = df[date_col]

    # Zahlen als Liste speichern
    def get_numbers(row):
        numbers = []
        for col in number_cols:
            val = row[col]
            if pd.notna(val):
                try:
                    numbers.append(int(val))
                except (ValueError, TypeError):
                    pass
        return numbers

    result["Zahlen"] = df.apply(get_numbers, axis=1)

    if stake_col:
        result["Spieleinsatz"] = df[stake_col].apply(parse_german_number)
    else:
        result["Spieleinsatz"] = None

    print(f"  -> {len(result)} Ziehungen geladen")

    return result


def classify_days(
    gq_data: pd.DataFrame, draw_data: pd.DataFrame, verbose: bool = False
) -> list[DayClassification]:
    """Klassifiziert jeden Tag als POPULAR, NEUTRAL oder UNPOPULAR."""
    print("\nKlassifiziere Tage...")

    # Filtere GQ-Daten auf Typ 10, 8 Richtige (bester Indikator)
    gq_filtered = gq_data[
        (gq_data["Keno_Typ"] == 10) & (gq_data["Richtige"] == 8)
    ].copy()

    if len(gq_filtered) == 0:
        # Fallback: Typ 10, 7 Richtige
        print("  [INFO] Keine 8/10 Daten, verwende 7/10")
        gq_filtered = gq_data[
            (gq_data["Keno_Typ"] == 10) & (gq_data["Richtige"] == 7)
        ].copy()

    # Gruppiere nach Datum (falls mehrere Eintraege pro Tag)
    gq_by_date = gq_filtered.groupby("Datum").agg({"Gewinner": "sum"}).reset_index()

    # Merge mit Ziehungsdaten
    merged = pd.merge(
        gq_by_date, draw_data, on="Datum", how="inner"
    )

    if len(merged) == 0:
        print("  [WARN] Kein Datum-Match gefunden, versuche Datumsformat-Konvertierung")
        # Versuche Datumsformate anzupassen
        gq_by_date["Datum_parsed"] = pd.to_datetime(
            gq_by_date["Datum"], format="%d.%m.%Y", errors="coerce"
        )
        draw_data["Datum_parsed"] = pd.to_datetime(
            draw_data["Datum"], format="%d.%m.%Y", errors="coerce"
        )
        merged = pd.merge(
            gq_by_date, draw_data, on="Datum_parsed", how="inner"
        )

    print(f"  Gematchte Tage: {len(merged)}")

    if len(merged) == 0:
        return []

    # Normalisiere Gewinner nach Spieleinsatz (falls vorhanden)
    if "Spieleinsatz" in merged.columns and merged["Spieleinsatz"].notna().any():
        merged["Normalized"] = merged["Gewinner"] / (
            merged["Spieleinsatz"] / 10000
        )  # Pro 10k Einsatz
    else:
        merged["Normalized"] = merged["Gewinner"]

    # Berechne Schwellwerte (Perzentile)
    p25 = merged["Normalized"].quantile(0.25)
    p75 = merged["Normalized"].quantile(0.75)

    print(f"  Schwellwerte: UNPOPULAR < {p25:.1f} < NEUTRAL < {p75:.1f} < POPULAR")

    classifications = []
    for _, row in merged.iterrows():
        norm = row["Normalized"]
        if norm < p25:
            classification = "UNPOPULAR"
        elif norm > p75:
            classification = "POPULAR"
        else:
            classification = "NEUTRAL"

        # Datum extrahieren (kann Datum_x oder Datum sein)
        date_str = row.get("Datum_x", row.get("Datum", ""))
        if pd.isna(date_str):
            date_str = str(row.get("Datum_parsed", ""))

        classifications.append(
            DayClassification(
                date=str(date_str),
                drawn_numbers=row["Zahlen"] if isinstance(row["Zahlen"], list) else [],
                winners_8of10=row["Gewinner"],
                normalized_winners=norm,
                classification=classification,
                stake=row.get("Spieleinsatz"),
            )
        )

    # Statistik
    pop_count = sum(1 for c in classifications if c.classification == "POPULAR")
    unpop_count = sum(1 for c in classifications if c.classification == "UNPOPULAR")
    neut_count = sum(1 for c in classifications if c.classification == "NEUTRAL")

    print(f"  Klassifikation: POPULAR={pop_count}, NEUTRAL={neut_count}, UNPOPULAR={unpop_count}")

    return classifications


def calculate_popularity_scores(
    classifications: list[DayClassification],
) -> list[PopularityResult]:
    """Berechnet Popularitaets-Score fuer jede Zahl 1-70."""
    print("\nBerechne Popularitaets-Scores...")

    # Zaehler fuer jede Zahl
    popular_count = defaultdict(int)
    unpopular_count = defaultdict(int)
    neutral_count = defaultdict(int)
    total_count = defaultdict(int)

    for day in classifications:
        for number in day.drawn_numbers:
            if 1 <= number <= 70:
                total_count[number] += 1
                if day.classification == "POPULAR":
                    popular_count[number] += 1
                elif day.classification == "UNPOPULAR":
                    unpopular_count[number] += 1
                else:
                    neutral_count[number] += 1

    # Berechne Scores
    total_draws = len(classifications)
    results = []

    for number in range(1, 71):
        pop = popular_count[number]
        unpop = unpopular_count[number]
        neut = neutral_count[number]
        total = total_count[number]

        # Popularity Score: (popular - unpopular) / total
        # Positiv = wird bei populaeren Ziehungen gezogen
        # Negativ = wird bei unpopulaeren Ziehungen gezogen
        if total > 0:
            score = (pop - unpop) / total
        else:
            score = 0.0

        # Ziehungshaeufigkeit relativ zum Durchschnitt
        expected = total_draws * 20 / 70  # Erwartete Anzahl
        if expected > 0:
            frequency = total / expected
        else:
            frequency = 0.0

        results.append(
            PopularityResult(
                number=number,
                popularity_score=score,
                times_in_popular=pop,
                times_in_unpopular=unpop,
                times_in_neutral=neut,
                total_draws=total,
                draw_frequency=frequency,
            )
        )

    return results


def analyze_correlation(results: list[PopularityResult]) -> dict:
    """Analysiert Korrelation zwischen Popularitaet und Ziehungshaeufigkeit."""
    print("\nAnalysiere Korrelation...")

    popularity = [r.popularity_score for r in results]
    frequency = [r.draw_frequency for r in results]

    # Pearson Korrelation
    pearson_r, pearson_p = stats.pearsonr(popularity, frequency)

    # Spearman Korrelation
    spearman_r, spearman_p = stats.spearmanr(popularity, frequency)

    print(f"  Pearson:  r={pearson_r:.4f}, p={pearson_p:.4f}")
    print(f"  Spearman: r={spearman_r:.4f}, p={spearman_p:.4f}")

    # Interpretation
    if pearson_p < 0.05:
        if pearson_r < 0:
            interpretation = "BESTAETIGT: Unpopulaere Zahlen werden HAEUFIGER gezogen!"
        else:
            interpretation = "WIDERLEGT: Populaere Zahlen werden HAEUFIGER gezogen"
    else:
        interpretation = "NICHT SIGNIFIKANT: Keine Korrelation gefunden"

    print(f"\n  >>> {interpretation}")

    return {
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_r": spearman_r,
        "spearman_p": spearman_p,
        "interpretation": interpretation,
        "hypothesis_confirmed": bool(pearson_p < 0.05 and pearson_r < 0),
    }


def main():
    parser = argparse.ArgumentParser(description="TASK-RE02: Popularity Reverse Engineering")
    parser.add_argument(
        "--gq-dir",
        type=Path,
        default=Path("Keno_GPTs"),
        help="Verzeichnis mit GQ-Dateien",
    )
    parser.add_argument(
        "--draws",
        type=Path,
        default=Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv"),
        help="Pfad zu Ziehungsdaten",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/popularity_reverse_engineering.json"),
        help="Output-Datei",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose Output")

    args = parser.parse_args()

    print("=" * 60)
    print("TASK-RE02: Popularity Reverse Engineering")
    print("=" * 60)

    # Finde alle GQ-Dateien
    gq_patterns = [
        "Keno_GQ_*.csv",
        "KENO_Quote_details_*.csv",
    ]

    gq_files = []
    for pattern in gq_patterns:
        gq_files.extend(args.gq_dir.glob(pattern))

    # Spezifische Dateien hinzufuegen
    specific_files = [
        args.gq_dir / "Keno_GQ_2022_2023-2024.csv",
        args.gq_dir / "Keno_GQ_2023-2024.csv",
        args.gq_dir / "Keno_GQ_2023.csv",
        args.gq_dir / "Keno_GQ_2024.csv",
        args.gq_dir / "Keno_GQ_02-2024.csv",
        args.gq_dir / "KENO_Quote_details_2023.csv",
    ]
    for f in specific_files:
        if f.exists() and f not in gq_files:
            gq_files.append(f)

    gq_files = list(set(gq_files))  # Deduplizieren
    print(f"\nGefundene GQ-Dateien: {len(gq_files)}")

    # Lade Daten
    gq_data = load_gq_files(gq_files)
    draw_data = load_draw_data(args.draws)

    # Klassifiziere Tage
    classifications = classify_days(gq_data, draw_data, verbose=args.verbose)

    if len(classifications) == 0:
        print("\n[ERROR] Keine Daten fuer Analyse verfuegbar!")
        sys.exit(1)

    # Berechne Scores
    results = calculate_popularity_scores(classifications)

    # Analysiere Korrelation
    correlation = analyze_correlation(results)

    # Sortiere nach Popularity Score
    results_sorted = sorted(results, key=lambda x: x.popularity_score)

    # Ausgabe: Top 10 unpopulaere und populaere Zahlen
    print("\n" + "=" * 60)
    print("ERGEBNISSE")
    print("=" * 60)

    print("\nTop 10 UNPOPULAERE Zahlen (niedrigster Score):")
    print("-" * 50)
    for r in results_sorted[:10]:
        print(
            f"  Zahl {r.number:2d}: Score={r.popularity_score:+.3f}, "
            f"Freq={r.draw_frequency:.3f}, Pop/Unpop={r.times_in_popular}/{r.times_in_unpopular}"
        )

    print("\nTop 10 POPULAERE Zahlen (hoechster Score):")
    print("-" * 50)
    for r in results_sorted[-10:][::-1]:
        print(
            f"  Zahl {r.number:2d}: Score={r.popularity_score:+.3f}, "
            f"Freq={r.draw_frequency:.3f}, Pop/Unpop={r.times_in_popular}/{r.times_in_unpopular}"
        )

    # Speichere Ergebnisse
    args.output.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "gq_files": [str(f) for f in gq_files],
            "draws_file": str(args.draws),
            "days_analyzed": len(classifications),
        },
        "correlation": correlation,
        "popularity_ranking": [
            {
                "number": r.number,
                "popularity_score": r.popularity_score,
                "times_in_popular": r.times_in_popular,
                "times_in_unpopular": r.times_in_unpopular,
                "times_in_neutral": r.times_in_neutral,
                "total_draws": r.total_draws,
                "draw_frequency": r.draw_frequency,
            }
            for r in results_sorted
        ],
        "unpopular_numbers": [r.number for r in results_sorted[:10]],
        "popular_numbers": [r.number for r in results_sorted[-10:][::-1]],
        "day_classifications": [
            {
                "date": c.date,
                "classification": c.classification,
                "winners": c.winners_8of10,
                "normalized": c.normalized_winners,
            }
            for c in classifications[:100]  # Nur erste 100 zur Dokumentation
        ],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {args.output}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Analysierte Tage: {len(classifications)}")
    print(f"Korrelation (Pearson): r={correlation['pearson_r']:.4f}, p={correlation['pearson_p']:.4f}")
    print(f"\n>>> {correlation['interpretation']}")

    if correlation["hypothesis_confirmed"]:
        print("\n[!] WICHTIG: Die Hypothese HYP-004 wird durch diese Daten UNTERSTUETZT!")
        print("    Unpopulaere Zahlen (wenige Spieler tippen sie) werden haeufiger gezogen.")
    else:
        print("\n[i] Die Daten zeigen keine signifikante Praeferenz fuer unpopulaere Zahlen.")


if __name__ == "__main__":
    main()
