"""
KENO System-Realitaet Analyse

Die "Beliebtheit" einer Zahl aus SYSTEM-Sicht:
1. Korrelation mit Gewinner-Anzahl (viele Gewinner = beliebte Zahl gezogen)
2. Position in Original-Reihenfolge (Position 1-20 koennte Bedeutung haben)
3. Count-Kurven-Entwicklung (wie veraendert sich die Haeufigkeit ueber Zeit)

Diese Analyse entlarvt die ILLUSION der Spieler-Statistik.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json
from scipy import stats


def load_keno_data():
    """Lade KENO-Daten mit Original-Reihenfolge."""
    path = Path("data/raw/keno/KENO_ab_2022_bereinigt.csv")
    df = pd.read_csv(path, sep=";", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def load_quoten_data():
    """Lade Quoten-Daten mit Gewinner-Anzahl fuer Typ 10 (10/10)."""
    # Versuche verschiedene Dateien
    paths = [
        Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2025.csv"),
        Path("Keno_GPTs/Keno_GQ_2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2023.csv"),
        Path("Keno_GPTs/Keno_GQ_2022.csv"),
    ]

    all_dfs = []
    for path in paths:
        if path.exists():
            try:
                df = pd.read_csv(path, encoding="utf-8-sig")
                all_dfs.append(df)
                print(f"  Geladen: {path.name} ({len(df)} Zeilen)")
            except Exception as e:
                print(f"  Fehler bei {path.name}: {e}")

    if not all_dfs:
        raise FileNotFoundError("Keine Quoten-Dateien gefunden")

    df = pd.concat(all_dfs, ignore_index=True)

    # Parse Datum - versuche verschiedene Formate
    def parse_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        date_str = str(date_str).strip()
        # Entferne Wochentag-Prefix wie "So, " oder "Mo, "
        if ", " in date_str and len(date_str.split(", ")[0]) <= 3:
            date_str = date_str.split(", ")[1]
        # Fuege Jahr hinzu wenn fehlt
        if date_str.count(".") == 2 and len(date_str.split(".")[-1]) == 4:
            try:
                return pd.to_datetime(date_str, format="%d.%m.%Y")
            except:
                pass
        return pd.NaT

    df["Datum"] = df["Datum"].apply(parse_date)
    df = df.dropna(subset=["Datum"])

    # Filtere auf Typ 10, 10 Richtige (Jackpot)
    # Oder summiere alle Gewinner pro Tag fuer Typ 10
    typ10_mask = df["Keno-Typ"] == 10

    # Gruppiere nach Datum und summiere Gewinner (oder nimm nur 10/10)
    typ10_df = df[typ10_mask].copy()

    # Konvertiere Gewinner-Anzahl
    typ10_df["Anzahl der Gewinner"] = typ10_df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".")
    typ10_df["Anzahl der Gewinner"] = pd.to_numeric(typ10_df["Anzahl der Gewinner"], errors="coerce").fillna(0).astype(int)

    # Gruppiere: Summe aller Gewinner bei Typ 10 pro Tag
    daily = typ10_df.groupby("Datum")["Anzahl der Gewinner"].sum().reset_index()
    daily.columns = ["Datum", "Typ10_Anz"]

    print(f"  Typ 10 Daten: {len(daily)} Tage")

    return daily


def analyze_position_winner_correlation(keno_df, quoten_df):
    """
    Analysiere: Korreliert die POSITION einer Zahl mit der Gewinner-Anzahl?

    Hypothese: Zahlen an bestimmten Positionen fuehren zu mehr/weniger Gewinnern
    weil das System "unbeliebte" Zahlen an bestimmte Positionen setzt.
    """
    print("\n" + "="*70)
    print("ANALYSE 1: Position vs. Gewinner-Anzahl")
    print("="*70)

    # Merge auf Datum
    merged = keno_df.merge(quoten_df[["Datum", "Typ10_Anz"]], on="Datum", how="inner")
    merged = merged.dropna(subset=["Typ10_Anz"])
    merged["Typ10_Anz"] = merged["Typ10_Anz"].astype(int)

    print(f"Anzahl Ziehungen mit Quoten-Daten: {len(merged)}")

    # Fuer jede Position: Welche Zahlen erscheinen dort wenn viele/wenige Gewinner?
    position_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Korrelation: Position -> durchschnittliche Gewinner-Anzahl
    position_winner_corr = {}

    for pos_idx, col in enumerate(position_cols, 1):
        # Gruppiere nach Zahl an dieser Position
        pos_data = merged.groupby(col)["Typ10_Anz"].agg(["mean", "count", "sum"])

        # Durchschnittliche Gewinner wenn Zahl X an Position pos_idx
        position_winner_corr[pos_idx] = {
            "mean_winners": merged["Typ10_Anz"].mean(),
            "std_winners": merged["Typ10_Anz"].std(),
        }

    # Analysiere: Gibt es Positionen die konsistent mit weniger Gewinnern korrelieren?
    print("\nMittelwert Gewinner pro Tag:", merged["Typ10_Anz"].mean())
    print("Standardabweichung:", merged["Typ10_Anz"].std())

    # Tage mit VIELEN Gewinnern (>= 5) vs. WENIGEN (< 2)
    many_winners = merged[merged["Typ10_Anz"] >= 5]
    few_winners = merged[merged["Typ10_Anz"] < 2]

    print(f"\nTage mit >= 5 Gewinnern: {len(many_winners)}")
    print(f"Tage mit < 2 Gewinnern: {len(few_winners)}")

    # Fuer jede Position: Zahlen-Verteilung bei vielen vs. wenigen Gewinnern
    position_analysis = {}

    for pos_idx, col in enumerate(position_cols, 1):
        many_numbers = many_winners[col].tolist()
        few_numbers = few_winners[col].tolist()

        # Durchschnittliche Zahl an Position
        many_mean = np.mean(many_numbers) if many_numbers else 0
        few_mean = np.mean(few_numbers) if few_numbers else 0

        # Anteil Birthday-Zahlen (1-31)
        many_birthday = sum(1 for n in many_numbers if n <= 31) / max(len(many_numbers), 1)
        few_birthday = sum(1 for n in few_numbers if n <= 31) / max(len(few_numbers), 1)

        position_analysis[pos_idx] = {
            "many_winners_mean_number": round(many_mean, 1),
            "few_winners_mean_number": round(few_mean, 1),
            "delta": round(few_mean - many_mean, 1),
            "many_winners_birthday_pct": round(many_birthday * 100, 1),
            "few_winners_birthday_pct": round(few_birthday * 100, 1),
        }

    print("\nPosition | Viele Gew. | Wenige Gew. | Delta | Birthday% (viel/wenig)")
    print("-" * 70)

    for pos, data in position_analysis.items():
        print(f"  {pos:2}     | {data['many_winners_mean_number']:5.1f}      | "
              f"{data['few_winners_mean_number']:5.1f}       | {data['delta']:+5.1f} | "
              f"{data['many_winners_birthday_pct']:4.1f}% / {data['few_winners_birthday_pct']:4.1f}%")

    return position_analysis


def analyze_number_winner_correlation(keno_df, quoten_df):
    """
    Analysiere: Welche ZAHLEN korrelieren mit vielen/wenigen Gewinnern?

    Das ist die SYSTEM-Sicht auf "Beliebtheit" - nicht Haeufigkeit!
    """
    print("\n" + "="*70)
    print("ANALYSE 2: Zahl -> Gewinner-Korrelation (SYSTEM-BELIEBTHEIT)")
    print("="*70)

    # Merge auf Datum
    merged = keno_df.merge(quoten_df[["Datum", "Typ10_Anz"]], on="Datum", how="inner")
    merged = merged.dropna(subset=["Typ10_Anz"])
    merged["Typ10_Anz"] = merged["Typ10_Anz"].astype(int)

    position_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Fuer jede Zahl 1-70: Durchschnittliche Gewinner wenn diese Zahl gezogen
    number_winner_stats = {}

    for number in range(1, 71):
        # Finde alle Tage wo diese Zahl gezogen wurde
        mask = merged[position_cols].apply(lambda row: number in row.values, axis=1)
        days_with_number = merged[mask]

        if len(days_with_number) > 0:
            mean_winners = days_with_number["Typ10_Anz"].mean()
            count = len(days_with_number)

            number_winner_stats[number] = {
                "mean_winners": round(mean_winners, 3),
                "count": count,
            }

    # Sortiere nach mean_winners
    sorted_numbers = sorted(number_winner_stats.items(),
                           key=lambda x: x[1]["mean_winners"])

    print("\nZahlen mit WENIGSTEN Gewinnern (= unbeliebt beim Spieler):")
    print("-" * 50)
    for num, data in sorted_numbers[:15]:
        birthday = "Birthday" if num <= 31 else "Hoch"
        print(f"  Zahl {num:2}: {data['mean_winners']:.3f} Gewinner/Tag "
              f"({data['count']} Tage) [{birthday}]")

    print("\nZahlen mit MEISTEN Gewinnern (= beliebt beim Spieler):")
    print("-" * 50)
    for num, data in sorted_numbers[-15:]:
        birthday = "Birthday" if num <= 31 else "Hoch"
        print(f"  Zahl {num:2}: {data['mean_winners']:.3f} Gewinner/Tag "
              f"({data['count']} Tage) [{birthday}]")

    # Korrelation: Birthday-Zahlen vs. Hohe Zahlen
    birthday_numbers = [n for n in range(1, 32)]
    high_numbers = [n for n in range(50, 71)]

    birthday_mean = np.mean([number_winner_stats[n]["mean_winners"]
                            for n in birthday_numbers if n in number_winner_stats])
    high_mean = np.mean([number_winner_stats[n]["mean_winners"]
                        for n in high_numbers if n in number_winner_stats])

    print("\n" + "="*70)
    print("SYSTEM-SICHT auf Beliebtheit:")
    print(f"  Birthday-Zahlen (1-31): {birthday_mean:.3f} Gewinner/Tag im Schnitt")
    print(f"  Hohe Zahlen (50-70):    {high_mean:.3f} Gewinner/Tag im Schnitt")
    print(f"  Delta:                  {birthday_mean - high_mean:+.3f}")
    print("="*70)

    return number_winner_stats


def analyze_count_curves(keno_df):
    """
    Analysiere die COUNT-KURVEN der Zahlen ueber Zeit.

    Hypothese: Das System steuert Zahlen so, dass ihre Haeufigkeit
    in einem bestimmten Korridor bleibt - aber die FORM der Kurve
    koennte ein Signal sein.
    """
    print("\n" + "="*70)
    print("ANALYSE 3: Count-Kurven als System-Signal")
    print("="*70)

    position_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Rolling Count fuer jede Zahl (letzte 30 Tage)
    window = 30

    # Zaehle Vorkommen pro Tag pro Zahl
    number_daily = {n: [] for n in range(1, 71)}

    for _, row in keno_df.iterrows():
        drawn = set(row[position_cols].values)
        for n in range(1, 71):
            number_daily[n].append(1 if n in drawn else 0)

    # Rolling Sum
    number_rolling = {}
    for n in range(1, 71):
        series = pd.Series(number_daily[n])
        rolling = series.rolling(window=window).sum()
        number_rolling[n] = rolling.dropna().tolist()

    # Analysiere Kurvenformen
    print(f"\nRolling {window}-Tage Count Statistiken:")
    print("-" * 60)

    curve_stats = {}
    for n in range(1, 71):
        if len(number_rolling[n]) > 100:
            curve = number_rolling[n]
            curve_stats[n] = {
                "mean": np.mean(curve),
                "std": np.std(curve),
                "min": min(curve),
                "max": max(curve),
                "range": max(curve) - min(curve),
                "trend": curve[-1] - curve[0],  # Gesamttrend
                "volatility": np.std(np.diff(curve)),  # Wie stark schwankt sie
            }

    # Finde Zahlen mit extremen Kurvenformen
    # Hohe Volatilitaet = System "spielt" mit der Zahl
    sorted_by_volatility = sorted(curve_stats.items(),
                                  key=lambda x: x[1]["volatility"], reverse=True)

    print("\nZahlen mit HOECHSTER Volatilitaet (System manipuliert aktiv?):")
    for num, data in sorted_by_volatility[:10]:
        birthday = "B" if num <= 31 else "H"
        print(f"  Zahl {num:2} [{birthday}]: Volatilitaet={data['volatility']:.2f}, "
              f"Range={data['range']:.0f}, Trend={data['trend']:+.1f}")

    print("\nZahlen mit NIEDRIGSTER Volatilitaet (stabil gehalten?):")
    for num, data in sorted_by_volatility[-10:]:
        birthday = "B" if num <= 31 else "H"
        print(f"  Zahl {num:2} [{birthday}]: Volatilitaet={data['volatility']:.2f}, "
              f"Range={data['range']:.0f}, Trend={data['trend']:+.1f}")

    return curve_stats


def analyze_jackpot_positions(keno_df, quoten_df):
    """
    Analysiere die POSITIONEN der Gewinner-Zahlen an Jackpot-Tagen.

    Hypothese: An Jackpot-Tagen platziert das System die "unbeliebten"
    Zahlen an bestimmten Positionen.
    """
    print("\n" + "="*70)
    print("ANALYSE 4: Positionen an Jackpot-Tagen")
    print("="*70)

    # Merge
    merged = keno_df.merge(quoten_df[["Datum", "Typ10_Anz"]], on="Datum", how="inner")
    merged = merged.dropna(subset=["Typ10_Anz"])
    merged["Typ10_Anz"] = merged["Typ10_Anz"].astype(int)

    # Jackpot-Tage (Typ10_Anz > 0)
    jackpot_days = merged[merged["Typ10_Anz"] > 0]
    non_jackpot_days = merged[merged["Typ10_Anz"] == 0]

    print(f"Jackpot-Tage: {len(jackpot_days)}")
    print(f"Nicht-Jackpot-Tage: {len(non_jackpot_days)}")

    position_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Vergleiche Durchschnittszahl pro Position
    print("\nDurchschnittliche Zahl pro Position:")
    print("Position | Jackpot-Tag | Normal-Tag | Delta")
    print("-" * 50)

    position_comparison = {}
    for pos_idx, col in enumerate(position_cols, 1):
        jackpot_mean = jackpot_days[col].mean()
        normal_mean = non_jackpot_days[col].mean() if len(non_jackpot_days) > 0 else 0
        delta = jackpot_mean - normal_mean

        position_comparison[pos_idx] = {
            "jackpot_mean": jackpot_mean,
            "normal_mean": normal_mean,
            "delta": delta,
        }

        print(f"  {pos_idx:2}      | {jackpot_mean:5.1f}       | {normal_mean:5.1f}      | {delta:+5.2f}")

    # Statistischer Test: Unterscheiden sich die Positionen signifikant?
    print("\nStatistischer Test (Mann-Whitney U):")
    significant_positions = []

    for pos_idx, col in enumerate(position_cols, 1):
        jackpot_values = jackpot_days[col].values
        normal_values = non_jackpot_days[col].values

        if len(normal_values) > 0:
            stat, p_value = stats.mannwhitneyu(jackpot_values, normal_values,
                                               alternative='two-sided')
            if p_value < 0.05:
                significant_positions.append((pos_idx, p_value))
                print(f"  Position {pos_idx}: p={p_value:.4f} SIGNIFIKANT")

    if not significant_positions:
        print("  Keine signifikanten Unterschiede gefunden.")

    return position_comparison


def main():
    """Hauptfunktion."""
    print("="*70)
    print("KENO SYSTEM-REALITAET ANALYSE")
    print("Entlarvung der Spieler-Illusion")
    print("="*70)

    # Lade Daten
    keno_df = load_keno_data()
    print(f"\nKENO-Daten geladen: {len(keno_df)} Ziehungen")
    print(f"Zeitraum: {keno_df['Datum'].min()} bis {keno_df['Datum'].max()}")

    try:
        quoten_df = load_quoten_data()
        print(f"Quoten-Daten geladen: {len(quoten_df)} Eintraege")
        has_quoten = True
    except Exception as e:
        print(f"Keine Quoten-Daten gefunden: {e}")
        has_quoten = False

    results = {}

    # Analyse 1: Position vs. Gewinner
    if has_quoten:
        results["position_analysis"] = analyze_position_winner_correlation(keno_df, quoten_df)

        # Analyse 2: Zahl -> Gewinner Korrelation
        results["number_winner_correlation"] = analyze_number_winner_correlation(keno_df, quoten_df)

        # Analyse 4: Jackpot-Positionen
        results["jackpot_positions"] = analyze_jackpot_positions(keno_df, quoten_df)

    # Analyse 3: Count-Kurven (benoetigt keine Quoten)
    results["count_curves"] = analyze_count_curves(keno_df)

    # Speichere Ergebnisse
    output_path = Path("results/system_reality_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Konvertiere numpy types fuer JSON
    def convert_for_json(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(i) for i in obj]
        return obj

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(convert_for_json(results), f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG: Was das System WIRKLICH tut")
    print("="*70)
    print("""
Die Spieler sehen: "Zahl X wurde haeufig gezogen"
Das System sieht:  "Wenn Zahl X gezogen wird, wie viele Gewinner gibt es?"

SPIELER-ILLUSION:
  - Haeufige Zahlen = "heisse" Zahlen
  - Seltene Zahlen = "kalte" Zahlen

SYSTEM-REALITAET:
  - Zahlen mit VIELEN Gewinnern = beliebt bei Spielern (Dauerscheine)
  - Zahlen mit WENIGEN Gewinnern = unbeliebt
  - Das System kann Haeufigkeit steuern ohne Beliebtheit zu aendern!
    """)


if __name__ == "__main__":
    main()
