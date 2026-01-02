#!/usr/bin/env python3
"""
Validiere JACKPOT_FAVORITES und JACKPOT_AVOID über 2022-2025.

Prüft ob die Zahlen-Präferenzen an Jackpot-Tagen über alle Jahre stabil sind.
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
JACKPOT_2023_FILE = BASE_DIR / "results" / "jackpot_days_from_quotes.json"
RESULTS_FILE = BASE_DIR / "results" / "jackpot_favorites_validation.json"


def load_keno_data():
    """Lade KENO-Ziehungsdaten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")

    # Datum parsen
    if "Datum" in df.columns:
        df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Zahlen extrahieren
    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].values.tolist()

    return df


def load_jackpot_days():
    """Lade alle bekannten Jackpot-Tage."""
    jackpot_days = {}

    # 2023 Jackpot-Tage aus Quoten
    if JACKPOT_2023_FILE.exists():
        with open(JACKPOT_2023_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for jp in data.get("jackpot_tage", []):
                date_str = jp["datum"]
                date = datetime.strptime(date_str, "%d.%m.%Y")
                jackpot_days[date] = {
                    "drawn_20": jp["drawn_20"],
                    "winners": jp["anzahl_gewinner"],
                    "year": date.year
                }

    # Zusätzliche verifizierte Jackpots hinzufügen
    # Kyritz 2025
    kyritz_date = datetime(2025, 10, 26)
    jackpot_days[kyritz_date] = {
        "drawn_20": [2, 5, 9, 12, 19, 20, 26, 34, 35, 36, 39, 42, 45, 48, 49, 54, 55, 62, 64, 66],
        "winners": 1,
        "year": 2025
    }

    # Nordsachsen 2024
    nord_date = datetime(2024, 1, 24)
    jackpot_days[nord_date] = {
        "drawn_20": [3, 7, 9, 12, 13, 16, 17, 19, 21, 36, 37, 38, 43, 45, 48, 52, 54, 57, 59, 67],
        "winners": 1,
        "year": 2024
    }

    return jackpot_days


def analyze_number_frequency(jackpot_days: dict, all_draws: pd.DataFrame):
    """Analysiere Zahlenfrequenz an Jackpot-Tagen vs. normale Tage."""

    # Alle Jackpot-Zahlen sammeln
    jackpot_numbers = Counter()
    jackpot_count = 0

    for date, jp_data in jackpot_days.items():
        for num in jp_data["drawn_20"]:
            jackpot_numbers[num] += 1
        jackpot_count += 1

    # Alle normalen Tage
    normal_numbers = Counter()
    normal_count = 0

    for _, row in all_draws.iterrows():
        date = row["Datum"]
        if date not in jackpot_days:
            for num in row["zahlen"]:
                if pd.notna(num):
                    normal_numbers[int(num)] += 1
            normal_count += 1

    # Frequenz berechnen
    results = []
    for num in range(1, 71):
        jp_freq = jackpot_numbers[num] / jackpot_count if jackpot_count > 0 else 0
        normal_freq = normal_numbers[num] / normal_count if normal_count > 0 else 0

        # Ratio: >1 = häufiger an Jackpot-Tagen
        ratio = jp_freq / normal_freq if normal_freq > 0 else 0

        results.append({
            "number": num,
            "jackpot_freq": round(jp_freq, 4),
            "normal_freq": round(normal_freq, 4),
            "ratio": round(ratio, 3),
            "jackpot_count": jackpot_numbers[num],
            "is_birthday": num <= 31
        })

    return results, jackpot_count, normal_count


def analyze_by_year(jackpot_days: dict, all_draws: pd.DataFrame):
    """Analysiere Stabilität pro Jahr."""
    years = sorted(set(jp["year"] for jp in jackpot_days.values()))

    yearly_favorites = {}
    yearly_avoid = {}

    for year in years:
        year_jps = {d: jp for d, jp in jackpot_days.items() if jp["year"] == year}

        if len(year_jps) < 3:
            continue  # Zu wenig Daten

        # Zahlen zählen für dieses Jahr
        year_numbers = Counter()
        for jp_data in year_jps.values():
            for num in jp_data["drawn_20"]:
                year_numbers[num] += 1

        # Top 15 und Bottom 10 für das Jahr
        sorted_nums = sorted(range(1, 71), key=lambda x: year_numbers[x], reverse=True)
        yearly_favorites[year] = sorted_nums[:15]
        yearly_avoid[year] = sorted_nums[-10:]

    return yearly_favorites, yearly_avoid


def check_stability(yearly_favorites: dict, yearly_avoid: dict):
    """Prüfe ob Favorites/Avoid über Jahre stabil sind (Law A)."""

    if len(yearly_favorites) < 2:
        return None, None, "Nicht genug Jahre für Stabilitätstest"

    years = sorted(yearly_favorites.keys())

    # Überlappung zwischen Jahren berechnen
    overlap_matrix = {}
    for i, y1 in enumerate(years):
        for y2 in years[i+1:]:
            fav_overlap = len(set(yearly_favorites[y1]) & set(yearly_favorites[y2]))
            avoid_overlap = len(set(yearly_avoid[y1]) & set(yearly_avoid[y2]))
            overlap_matrix[f"{y1}-{y2}"] = {
                "favorites_overlap": fav_overlap,
                "favorites_pct": round(fav_overlap / 15 * 100, 1),
                "avoid_overlap": avoid_overlap,
                "avoid_pct": round(avoid_overlap / 10 * 100, 1)
            }

    # Konsistente Zahlen (in ALLEN Jahren)
    all_fav_sets = [set(f) for f in yearly_favorites.values()]
    all_avoid_sets = [set(a) for a in yearly_avoid.values()]

    consistent_favorites = set.intersection(*all_fav_sets) if all_fav_sets else set()
    consistent_avoid = set.intersection(*all_avoid_sets) if all_avoid_sets else set()

    return consistent_favorites, consistent_avoid, overlap_matrix


def main():
    print("=" * 60)
    print("JACKPOT_FAVORITES/AVOID VALIDATION (2022-2025)")
    print("=" * 60)

    # Daten laden
    print("\n[1] Lade Daten...")
    df = load_keno_data()
    jackpot_days = load_jackpot_days()

    print(f"    Ziehungen gesamt: {len(df)}")
    print(f"    Jackpot-Tage: {len(jackpot_days)}")

    # Jahre zählen
    years_count = Counter(jp["year"] for jp in jackpot_days.values())
    for year, count in sorted(years_count.items()):
        print(f"      {year}: {count} Jackpots")

    # Gesamtanalyse
    print("\n[2] Analysiere Zahlenfrequenz...")
    freq_results, jp_count, normal_count = analyze_number_frequency(jackpot_days, df)

    # Sortieren nach Ratio
    sorted_by_ratio = sorted(freq_results, key=lambda x: x["ratio"], reverse=True)

    print(f"\n    JACKPOT_FAVORITES (häufiger an Jackpot-Tagen):")
    favorites_all = []
    for item in sorted_by_ratio[:15]:
        print(f"      {item['number']:2d}: ratio={item['ratio']:.2f}x ({item['jackpot_count']} JP-Erscheinungen)")
        favorites_all.append(item["number"])

    print(f"\n    JACKPOT_AVOID (seltener an Jackpot-Tagen):")
    avoid_all = []
    for item in sorted_by_ratio[-10:]:
        print(f"      {item['number']:2d}: ratio={item['ratio']:.2f}x ({item['jackpot_count']} JP-Erscheinungen)")
        avoid_all.append(item["number"])

    # Jahresanalyse
    print("\n[3] Analysiere Stabilität pro Jahr...")
    yearly_fav, yearly_avoid = analyze_by_year(jackpot_days, df)

    for year in sorted(yearly_fav.keys()):
        print(f"\n    {year} Favorites: {yearly_fav[year][:10]}")
        print(f"    {year} Avoid:     {yearly_avoid[year]}")

    # Stabilitätstest
    print("\n[4] Law A Stabilitätstest...")
    consistent_fav, consistent_avoid, overlap = check_stability(yearly_fav, yearly_avoid)

    if isinstance(overlap, dict):
        print(f"\n    Überlappung zwischen Jahren:")
        for pair, data in overlap.items():
            print(f"      {pair}: Favorites {data['favorites_pct']}%, Avoid {data['avoid_pct']}%")

        print(f"\n    KONSISTENT über ALLE Jahre:")
        print(f"      Favorites: {sorted(consistent_fav) if consistent_fav else 'KEINE'}")
        print(f"      Avoid:     {sorted(consistent_avoid) if consistent_avoid else 'KEINE'}")
    else:
        print(f"\n    {overlap}")

    # Vergleich mit Original 2023-Liste
    print("\n[5] Vergleich mit Original 2023-Liste...")
    original_favorites = [43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45]
    original_avoid = [1, 16, 21, 27, 29, 37, 67, 25, 68, 28]

    fav_still_valid = [n for n in original_favorites if n in favorites_all]
    fav_no_longer = [n for n in original_favorites if n not in favorites_all]
    avoid_still_valid = [n for n in original_avoid if n in avoid_all]
    avoid_no_longer = [n for n in original_avoid if n not in avoid_all]

    print(f"\n    Original Favorites (2023): {original_favorites}")
    print(f"    Noch gültig (2022-2025):   {fav_still_valid}")
    print(f"    Nicht mehr gültig:         {fav_no_longer}")

    print(f"\n    Original Avoid (2023): {original_avoid}")
    print(f"    Noch gültig (2022-2025):   {avoid_still_valid}")
    print(f"    Nicht mehr gültig:         {avoid_no_longer}")

    # Bewertung
    stability_score = len(fav_still_valid) / len(original_favorites)
    print(f"\n    STABILITÄTS-SCORE: {stability_score:.1%}")

    if stability_score >= 0.7:
        print("    → STABIL: Muster gilt auch für 2022-2025")
    elif stability_score >= 0.5:
        print("    → TEILWEISE STABIL: Einige Zahlen ändern sich")
    else:
        print("    → INSTABIL: Muster ist nicht über Jahre stabil")

    # Ergebnisse speichern
    results = {
        "datum": datetime.now().isoformat(),
        "datenbasis": {
            "jackpot_tage": len(jackpot_days),
            "normale_tage": normal_count,
            "jahre": dict(years_count)
        },
        "original_2023": {
            "favorites": original_favorites,
            "avoid": original_avoid
        },
        "aktualisiert_2022_2025": {
            "favorites": favorites_all,
            "avoid": avoid_all,
            "stability_score": round(stability_score, 3)
        },
        "validierung": {
            "favorites_noch_gueltig": fav_still_valid,
            "favorites_nicht_mehr": fav_no_longer,
            "avoid_noch_gueltig": avoid_still_valid,
            "avoid_nicht_mehr": avoid_no_longer
        },
        "jahres_analyse": {
            "yearly_favorites": {str(k): v for k, v in yearly_fav.items()},
            "yearly_avoid": {str(k): v for k, v in yearly_avoid.items()},
            "konsistent_favorites": sorted(consistent_fav) if consistent_fav else [],
            "konsistent_avoid": sorted(consistent_avoid) if consistent_avoid else []
        },
        "empfehlung": "STABIL" if stability_score >= 0.7 else ("TEILWEISE" if stability_score >= 0.5 else "INSTABIL")
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[6] Ergebnisse gespeichert: {RESULTS_FILE}")

    return results


if __name__ == "__main__":
    main()
