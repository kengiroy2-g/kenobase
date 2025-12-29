"""Near-Miss Zahlen-Analyse.

Analysiert welche Zahlen haeufiger in Near-Miss Situationen erscheinen.

Grundannahme: Das System erzeugt Near-Misses um Spieler zu motivieren.
Die Zahlen die Near-Misses erzeugen sind vorhersagbarer.
"""

import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pfade
BASE_DIR = Path(__file__).parent.parent
KENO_DATA_PATH = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
GQ_DATA_PATH = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
OUTPUT_PATH = BASE_DIR / "results" / "near_miss_numbers.json"


def load_keno_drawings(path: Path) -> pd.DataFrame:
    """Lade KENO Ziehungsdaten."""
    logger.info(f"Lade Ziehungsdaten von {path}")

    df = pd.read_csv(path, sep=';', encoding='utf-8')

    # Parse Datum
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Extrahiere gezogene Zahlen als Liste
    number_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['numbers'] = df[number_cols].values.tolist()

    logger.info(f"Geladen: {len(df)} Ziehungen von {df['Datum'].min()} bis {df['Datum'].max()}")

    return df


def load_winning_quotes(path: Path) -> pd.DataFrame:
    """Lade Gewinnquoten-Daten."""
    logger.info(f"Lade Gewinnquoten von {path}")

    df = pd.read_csv(path, encoding='utf-8-sig')

    # Parse Datum
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Parse Gewinner-Anzahl (deutsche Zahlenformat: 1.234 -> 1234)
    df['Anzahl der Gewinner'] = df['Anzahl der Gewinner'].astype(str).str.replace('.', '', regex=False)
    df['Anzahl der Gewinner'] = pd.to_numeric(df['Anzahl der Gewinner'], errors='coerce').fillna(0).astype(int)

    logger.info(f"Geladen: {len(df)} Eintraege")

    return df


def extract_near_miss_data(gq_df: pd.DataFrame) -> pd.DataFrame:
    """Extrahiere Near-Miss Daten (GK2 = 9 von 10 richtig fuer Typ 10).

    Near-Miss Definition:
    - Typ 10: 9 von 10 richtig (Gewinnklasse 2)
    - Typ 9: 8 von 9 richtig
    - Typ 8: 7 von 8 richtig
    usw.
    """
    # Fokus auf Typ 10, GK2 (9 richtige) - das ist der "Near-Miss zum Jackpot"
    near_miss_typ10 = gq_df[
        (gq_df['Keno-Typ'] == 10) &
        (gq_df['Anzahl richtiger Zahlen'] == 9)
    ].copy()

    # Aggregiere nach Datum
    near_miss_per_day = near_miss_typ10.groupby('Datum')['Anzahl der Gewinner'].sum().reset_index()
    near_miss_per_day.columns = ['Datum', 'near_miss_winners']

    logger.info(f"Near-Miss Daten fuer {len(near_miss_per_day)} Tage extrahiert")

    return near_miss_per_day


def classify_days(near_miss_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """Klassifiziere Tage in HIGH und LOW Near-Miss basierend auf Median."""
    median_winners = near_miss_df['near_miss_winners'].median()

    high_nm_days = near_miss_df[near_miss_df['near_miss_winners'] > median_winners].copy()
    low_nm_days = near_miss_df[near_miss_df['near_miss_winners'] <= median_winners].copy()

    logger.info(f"Median Near-Miss Gewinner: {median_winners}")
    logger.info(f"HIGH Near-Miss Tage: {len(high_nm_days)} (>{median_winners} Gewinner)")
    logger.info(f"LOW Near-Miss Tage: {len(low_nm_days)} (<={median_winners} Gewinner)")

    return high_nm_days, low_nm_days, median_winners


def calculate_number_frequencies(keno_df: pd.DataFrame, dates: pd.Series) -> dict[int, int]:
    """Berechne Haeufigkeit jeder Zahl an gegebenen Tagen."""
    # Filtere auf relevante Tage
    filtered = keno_df[keno_df['Datum'].isin(dates)]

    # Zaehle jede Zahl
    freq = {i: 0 for i in range(1, 71)}

    for _, row in filtered.iterrows():
        for num in row['numbers']:
            if 1 <= num <= 70:
                freq[num] += 1

    return freq


def analyze_near_miss_numbers(
    keno_df: pd.DataFrame,
    high_nm_days: pd.DataFrame,
    low_nm_days: pd.DataFrame
) -> dict:
    """Hauptanalyse: Welche Zahlen erscheinen haeufiger an Near-Miss Tagen."""

    # Frequenzen berechnen
    high_freq = calculate_number_frequencies(keno_df, high_nm_days['Datum'])
    low_freq = calculate_number_frequencies(keno_df, low_nm_days['Datum'])

    n_high_days = len(high_nm_days)
    n_low_days = len(low_nm_days)

    logger.info(f"Analysiere {n_high_days} HIGH-Tage und {n_low_days} LOW-Tage")

    # Normalisierte Frequenzen (pro Tag)
    results = []

    for num in range(1, 71):
        # Absolute Frequenzen
        high_count = high_freq[num]
        low_count = low_freq[num]

        # Normalisierte Frequenzen (Erscheinungen pro Tag)
        high_rate = high_count / n_high_days if n_high_days > 0 else 0
        low_rate = low_count / n_low_days if n_low_days > 0 else 0

        # Near-Miss Score: Differenz zwischen HIGH und LOW
        # Positiv = erscheint haeufiger an Near-Miss Tagen
        # Negativ = erscheint seltener an Near-Miss Tagen (Jackpot-Indikator)
        near_miss_score = high_rate - low_rate

        # Ratio (wenn moeglich)
        ratio = high_rate / low_rate if low_rate > 0 else float('inf') if high_rate > 0 else 1.0

        results.append({
            'number': num,
            'high_nm_count': high_count,
            'low_nm_count': low_count,
            'high_nm_rate': round(high_rate, 4),
            'low_nm_rate': round(low_rate, 4),
            'near_miss_score': round(near_miss_score, 4),
            'ratio': round(ratio, 4) if ratio != float('inf') else 999.0
        })

    # Sortiere nach Near-Miss Score
    results_sorted = sorted(results, key=lambda x: x['near_miss_score'], reverse=True)

    return results_sorted


def create_output(
    all_results: list[dict],
    median_winners: float,
    n_high_days: int,
    n_low_days: int
) -> dict:
    """Erstelle finales JSON Output."""

    # Top 20 Near-Miss Indikatoren (hoechste Scores)
    top_near_miss = all_results[:20]

    # Bottom 20 Jackpot Indikatoren (niedrigste Scores)
    bottom_jackpot = all_results[-20:][::-1]  # Umkehren fuer aufsteigende Reihenfolge

    output = {
        "metadata": {
            "analysis": "Near-Miss Number Frequency Analysis",
            "description": "Welche Zahlen erscheinen haeufiger an Tagen mit vielen Near-Miss Gewinnern",
            "median_near_miss_winners": median_winners,
            "high_nm_days_count": n_high_days,
            "low_nm_days_count": n_low_days,
            "scoring": {
                "near_miss_score": "Differenz: Erscheinungsrate(High-NM-Tage) - Erscheinungsrate(Low-NM-Tage)",
                "positive_score": "Zahl erscheint haeufiger an Near-Miss Tagen",
                "negative_score": "Zahl erscheint seltener an Near-Miss Tagen (Jackpot-Indikator)"
            }
        },
        "all_numbers_by_near_miss_score": all_results,
        "top_20_near_miss_indicators": top_near_miss,
        "top_20_jackpot_indicators": bottom_jackpot,
        "summary": {
            "strongest_near_miss_numbers": [r['number'] for r in top_near_miss[:5]],
            "strongest_jackpot_numbers": [r['number'] for r in bottom_jackpot[:5]],
            "interpretation": (
                "Zahlen mit positivem Score erscheinen haeufiger an Tagen mit vielen Near-Miss Gewinnern. "
                "Hypothese: Diese Zahlen werden vom System bevorzugt um Near-Misses zu generieren. "
                "Zahlen mit negativem Score erscheinen haeufiger an Tagen mit wenigen Near-Misses (Jackpot-Tage)."
            )
        }
    }

    return output


def main():
    """Hauptfunktion."""
    logger.info("=== NEAR-MISS ZAHLEN-ANALYSE ===")

    # 1. Daten laden
    keno_df = load_keno_drawings(KENO_DATA_PATH)
    gq_df = load_winning_quotes(GQ_DATA_PATH)

    # 2. Near-Miss Daten extrahieren (Typ 10, 9 richtige)
    near_miss_df = extract_near_miss_data(gq_df)

    # 3. Tage klassifizieren (HIGH vs LOW Near-Miss)
    high_nm_days, low_nm_days, median_winners = classify_days(near_miss_df)

    # 4. Nur Tage verwenden die in beiden Datensaetzen existieren
    common_dates_high = set(high_nm_days['Datum']).intersection(set(keno_df['Datum']))
    common_dates_low = set(low_nm_days['Datum']).intersection(set(keno_df['Datum']))

    high_nm_days = high_nm_days[high_nm_days['Datum'].isin(common_dates_high)]
    low_nm_days = low_nm_days[low_nm_days['Datum'].isin(common_dates_low)]

    logger.info(f"Gemeinsame Tage: {len(common_dates_high)} HIGH, {len(common_dates_low)} LOW")

    # 5. Analyse durchfuehren
    results = analyze_near_miss_numbers(keno_df, high_nm_days, low_nm_days)

    # 6. Output erstellen
    output = create_output(
        results,
        median_winners,
        len(high_nm_days),
        len(low_nm_days)
    )

    # 7. Speichern
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Ergebnis gespeichert: {OUTPUT_PATH}")

    # 8. Zusammenfassung ausgeben
    print("\n" + "="*60)
    print("NEAR-MISS ZAHLEN-ANALYSE - ERGEBNIS")
    print("="*60)
    print(f"\nMedian Near-Miss Gewinner pro Tag: {median_winners}")
    print(f"HIGH Near-Miss Tage analysiert: {len(high_nm_days)}")
    print(f"LOW Near-Miss Tage analysiert: {len(low_nm_days)}")

    print("\n--- TOP 10 NEAR-MISS INDIKATOREN ---")
    print("(Zahlen die haeufiger an Near-Miss Tagen erscheinen)")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i:2d}. Zahl {r['number']:2d}: Score={r['near_miss_score']:+.4f} (High:{r['high_nm_rate']:.3f} vs Low:{r['low_nm_rate']:.3f})")

    print("\n--- TOP 10 JACKPOT INDIKATOREN ---")
    print("(Zahlen die seltener an Near-Miss Tagen erscheinen)")
    for i, r in enumerate(results[-10:][::-1], 1):
        print(f"  {i:2d}. Zahl {r['number']:2d}: Score={r['near_miss_score']:+.4f} (High:{r['high_nm_rate']:.3f} vs Low:{r['low_nm_rate']:.3f})")

    return output


if __name__ == "__main__":
    main()
