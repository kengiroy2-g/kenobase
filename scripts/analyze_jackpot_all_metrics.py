"""
Analysiert ALLE Metriken aus number_index für Jackpot-Gewinner vs. Andere.

Metriken:
- Index (Streak)
- Mcount (Monat)
- Count (JP-Reset)
- JCount (JP-Total)
- JCountY (JP-Jahr)
- TCount (Total)
"""

import re
from pathlib import Path
from collections import defaultdict

# Verifizierte Jackpot-Gewinner (10 Zahlen = Winner, 10 = Other)
JACKPOTS = {
    "25.10.2025": {
        "name": "Kyritz",
        "winner": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
        "other": [2, 9, 19, 35, 39, 49, 54, 55, 62, 64]
    },
    "28.06.2023": {
        "name": "Oberbayern",
        "winner": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
        "other": [6, 13, 24, 36, 38, 40, 43, 51, 56, 63]
    },
    "24.01.2024": {
        "name": "Nordsachsen",
        "winner": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
        "other": [3, 7, 12, 13, 16, 17, 21, 36, 52, 54]
    }
}


def parse_number_index(filepath: Path) -> dict:
    """Parst die number_index Datei und extrahiert alle Metriken pro Tag."""

    data = {}
    current_date = None
    current_entry = {}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Datum erkennen (z.B. "25.10.2025 (Saturday)")
        date_match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+\(", line)
        if date_match:
            if current_date and current_entry:
                data[current_date] = current_entry
            current_date = date_match.group(1)
            current_entry = {"zahlen": [], "metrics": {}}
            i += 1
            continue

        # Zahlen-Zeile
        if line.startswith("Zahlen:") and current_date:
            parts = line.replace("Zahlen:", "").split()
            current_entry["zahlen"] = [int(x) for x in parts if x.isdigit()]
            i += 1
            continue

        # Metrik-Zeilen
        for metric in ["Index:", "Mcount:", "Count:", "JCount:", "JCountY:", "TCount:"]:
            if line.startswith(metric) and current_date:
                name = metric.replace(":", "")
                parts = line.replace(metric, "").split()
                values = [int(x) for x in parts if x.lstrip("-").isdigit()]
                current_entry["metrics"][name] = values
                break

        i += 1

    # Letzten Eintrag speichern
    if current_date and current_entry:
        data[current_date] = current_entry

    return data


def analyze_jackpot(data: dict, date: str, jackpot_info: dict) -> dict:
    """Analysiert einen Jackpot mit allen Metriken."""

    if date not in data:
        print(f"WARNUNG: {date} nicht in Daten gefunden!")
        return None

    entry = data[date]
    zahlen = entry["zahlen"]
    metrics = entry["metrics"]

    winner = set(jackpot_info["winner"])
    other = set(jackpot_info["other"])

    # Mapping: Zahl -> Position in der Ziehung
    zahl_to_pos = {z: i for i, z in enumerate(zahlen)}

    results = {
        "name": jackpot_info["name"],
        "date": date,
        "winner": {},
        "other": {}
    }

    for metric_name, values in metrics.items():
        winner_values = []
        other_values = []

        for zahl in zahlen:
            pos = zahl_to_pos.get(zahl)
            if pos is not None and pos < len(values):
                val = values[pos]
                if zahl in winner:
                    winner_values.append(val)
                elif zahl in other:
                    other_values.append(val)

        if winner_values and other_values:
            results["winner"][metric_name] = {
                "values": winner_values,
                "avg": sum(winner_values) / len(winner_values),
                "min": min(winner_values),
                "max": max(winner_values)
            }
            results["other"][metric_name] = {
                "values": other_values,
                "avg": sum(other_values) / len(other_values),
                "min": min(other_values),
                "max": max(other_values)
            }

    return results


def main():
    print("=" * 80)
    print("JACKPOT ANALYSE - ALLE METRIKEN")
    print("=" * 80)

    filepath = Path("C:/Users/kenfu/Documents/keno_base/results/number_index_2022_2025.txt")

    print(f"\nLade {filepath}...")
    data = parse_number_index(filepath)
    print(f"Gefunden: {len(data)} Tage")

    # Alle Jackpots analysieren
    all_results = []

    for date, jackpot_info in JACKPOTS.items():
        print(f"\n{'='*80}")
        print(f"JACKPOT: {jackpot_info['name']} ({date})")
        print(f"{'='*80}")

        result = analyze_jackpot(data, date, jackpot_info)
        if result:
            all_results.append(result)

            print(f"\nWinner: {jackpot_info['winner']}")
            print(f"Other:  {jackpot_info['other']}")

            print(f"\n{'Metrik':<12} {'Winner Avg':>12} {'Other Avg':>12} {'Ratio':>10} {'Differenz':>12}")
            print("-" * 60)

            for metric in ["Index", "Mcount", "Count", "JCount", "JCountY", "TCount"]:
                if metric in result["winner"] and metric in result["other"]:
                    w_avg = result["winner"][metric]["avg"]
                    o_avg = result["other"][metric]["avg"]
                    ratio = w_avg / o_avg if o_avg > 0 else float('inf')
                    diff = w_avg - o_avg

                    marker = ""
                    if ratio > 1.2:
                        marker = " ★ WINNER HOEHER"
                    elif ratio < 0.8:
                        marker = " ★ OTHER HOEHER"

                    print(f"{metric:<12} {w_avg:>12.2f} {o_avg:>12.2f} {ratio:>10.2f}x {diff:>+12.2f}{marker}")

            # Detail-Ausgabe
            print(f"\n--- Detail Winner (Index) ---")
            if "Index" in result["winner"]:
                print(f"Werte: {result['winner']['Index']['values']}")

            print(f"\n--- Detail Other (Index) ---")
            if "Index" in result["other"]:
                print(f"Werte: {result['other']['Index']['values']}")

    # Zusammenfassung
    if all_results:
        print(f"\n{'='*80}")
        print("ZUSAMMENFASSUNG ALLER JACKPOTS")
        print(f"{'='*80}")

        # Aggregiere über alle Jackpots
        agg_winner = defaultdict(list)
        agg_other = defaultdict(list)

        for result in all_results:
            for metric in ["Index", "Mcount", "Count", "JCount", "JCountY", "TCount"]:
                if metric in result["winner"]:
                    agg_winner[metric].extend(result["winner"][metric]["values"])
                if metric in result["other"]:
                    agg_other[metric].extend(result["other"][metric]["values"])

        print(f"\n{'Metrik':<12} {'Winner Avg':>12} {'Other Avg':>12} {'Ratio':>10} {'Signifikant?':>15}")
        print("-" * 65)

        significant_metrics = []

        for metric in ["Index", "Mcount", "Count", "JCount", "JCountY", "TCount"]:
            if agg_winner[metric] and agg_other[metric]:
                w_avg = sum(agg_winner[metric]) / len(agg_winner[metric])
                o_avg = sum(agg_other[metric]) / len(agg_other[metric])
                ratio = w_avg / o_avg if o_avg > 0 else float('inf')

                # Einfacher Signifikanz-Check
                sig = ""
                if ratio > 1.3 or ratio < 0.7:
                    sig = "★★★ JA"
                    significant_metrics.append((metric, ratio, w_avg, o_avg))
                elif ratio > 1.15 or ratio < 0.85:
                    sig = "★★ MOEGLICH"
                elif ratio > 1.05 or ratio < 0.95:
                    sig = "★ SCHWACH"
                else:
                    sig = "NEIN"

                print(f"{metric:<12} {w_avg:>12.2f} {o_avg:>12.2f} {ratio:>10.2f}x {sig:>15}")

        if significant_metrics:
            print(f"\n{'='*80}")
            print("POTENTIELLE SIGNALE GEFUNDEN:")
            print(f"{'='*80}")
            for metric, ratio, w, o in significant_metrics:
                direction = "WINNER HOEHER" if ratio > 1 else "OTHER HOEHER"
                print(f"  → {metric}: {direction} (Ratio {ratio:.2f}x)")
                print(f"     Winner avg: {w:.2f}, Other avg: {o:.2f}")


if __name__ == "__main__":
    main()
