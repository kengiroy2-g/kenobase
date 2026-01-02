"""
Analyse der regionalen Praeferenzen aus Jackpot-Daten.

Methode:
1. Fuer bekannte Jackpots: Analysiere "Andere 10" (= populaere Zahlen der Region)
2. Fuer alle Jackpot-Tage: Analysiere 20 gezogene Zahlen
3. Vergleiche mit Nicht-Jackpot-Tagen
4. Leite regionale Praeferenzen ab
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import numpy as np


def load_keno_data(filepath: Path) -> list[dict]:
    """Laedt KENO-Ziehungsdaten."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                datum = row.get("Datum", "").strip()
                if not datum:
                    continue

                numbers = []
                for i in range(1, 21):
                    col = f"Keno_Z{i}"
                    if col in row and row[col]:
                        numbers.append(int(row[col]))

                if len(numbers) == 20:
                    data.append({
                        "datum": datum,
                        "zahlen": sorted(numbers)
                    })
            except Exception:
                continue
    return data


def analyze_numbers(numbers: list[int]) -> dict:
    """Analysiert eine Liste von Zahlen nach verschiedenen Metriken."""
    return {
        "birthday": sum(1 for z in numbers if z <= 31),
        "gerade": sum(1 for z in numbers if z % 2 == 0),
        "niedrig": sum(1 for z in numbers if z <= 35),
        "hoch": sum(1 for z in numbers if z > 50),
        "summe": sum(numbers),
        "avg": np.mean(numbers),
        "einstellig": sum(1 for z in numbers if z <= 9),
        "endziffer_7": sum(1 for z in numbers if z % 10 == 7),
        "endziffer_3": sum(1 for z in numbers if z % 10 == 3),
        "dekade_0": sum(1 for z in numbers if z < 10),
        "dekade_1": sum(1 for z in numbers if 10 <= z < 20),
        "dekade_2": sum(1 for z in numbers if 20 <= z < 30),
        "dekade_3": sum(1 for z in numbers if 30 <= z < 40),
        "dekade_4": sum(1 for z in numbers if 40 <= z < 50),
        "dekade_5": sum(1 for z in numbers if 50 <= z < 60),
        "dekade_6": sum(1 for z in numbers if 60 <= z < 70),
        "dekade_7": sum(1 for z in numbers if z == 70),
    }


def main():
    print("=" * 70)
    print("ANALYSE REGIONALER PRAEFERENZEN AUS JACKPOT-DATEN")
    print("=" * 70)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")

    # 1. Lade bekannte Jackpots
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        jackpot_data = json.load(f)

    verified_events = jackpot_data["events"]
    pending_events = jackpot_data.get("pending_from_quotes_2023", [])

    print(f"\nVerifizierte Jackpots: {len(verified_events)}")
    print(f"Pending Jackpots (2023): {len(pending_events)}")

    # 2. Lade alle KENO-Daten 2023-2024
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    all_draws = load_keno_data(keno_path)

    # Filtere nach Jahr
    draws_2023 = [d for d in all_draws if "2023" in d["datum"]]
    draws_2024 = [d for d in all_draws if "2024" in d["datum"]]

    print(f"Ziehungen 2023: {len(draws_2023)}")
    print(f"Ziehungen 2024: {len(draws_2024)}")

    # 3. Analysiere "Andere 10" der verifizierten Jackpots
    print(f"\n{'='*70}")
    print("TEIL 1: ANALYSE DER 'ANDERE 10' (Verifizierte Jackpots)")
    print(f"{'='*70}")

    for event in verified_events:
        city = event.get("city", event["id"])
        region = event.get("region", "Unknown")
        winner = set(event["winner_10"])
        drawn = set(event["drawn_20"])
        other = list(drawn - winner)

        metrics = analyze_numbers(other)

        print(f"\n{city} ({region}):")
        print(f"  Andere 10: {sorted(other)}")
        print(f"  Birthday (1-31):  {metrics['birthday']}/10 ({metrics['birthday']*10}%)")
        print(f"  Gerade:           {metrics['gerade']}/10 ({metrics['gerade']*10}%)")
        print(f"  Niedrig (<=35):   {metrics['niedrig']}/10 ({metrics['niedrig']*10}%)")
        print(f"  Hoch (>50):       {metrics['hoch']}/10 ({metrics['hoch']*10}%)")
        print(f"  Durchschnitt:     {metrics['avg']:.1f}")

    # 4. Analysiere alle Jackpot-Tage (20 gezogene)
    print(f"\n{'='*70}")
    print("TEIL 2: ANALYSE ALLER JACKPOT-TAGE 2023 (20 gezogene Zahlen)")
    print(f"{'='*70}")

    # Sammle Jackpot-Daten
    jackpot_dates_2023 = set()
    for event in verified_events:
        if "2023" in event["date"]:
            # Konvertiere YYYY-MM-DD zu DD.MM.YYYY
            d = datetime.strptime(event["date"], "%Y-%m-%d")
            jackpot_dates_2023.add(d.strftime("%d.%m.%Y"))

    for event in pending_events:
        # Pending events haben "date" im Format YYYY-MM-DD
        if "date" in event:
            d = datetime.strptime(event["date"], "%Y-%m-%d")
            jackpot_dates_2023.add(d.strftime("%d.%m.%Y"))

    print(f"\nJackpot-Tage 2023: {len(jackpot_dates_2023)}")

    # Analysiere Jackpot-Tage vs Nicht-Jackpot-Tage
    jackpot_draws = []
    normal_draws = []

    for draw in draws_2023:
        if draw["datum"] in jackpot_dates_2023:
            jackpot_draws.append(draw)
        else:
            normal_draws.append(draw)

    print(f"Gefundene Jackpot-Ziehungen: {len(jackpot_draws)}")
    print(f"Normale Ziehungen: {len(normal_draws)}")

    # Berechne Durchschnitte
    if jackpot_draws and normal_draws:
        print(f"\n{'Metrik':<25} {'Jackpot-Tage':>15} {'Normale Tage':>15} {'Differenz':>12}")
        print("-" * 70)

        metrics_to_compare = [
            ("Birthday (1-31)", "birthday", 20),
            ("Gerade", "gerade", 20),
            ("Niedrig (<=35)", "niedrig", 20),
            ("Hoch (>50)", "hoch", 20),
            ("Durchschnitt", "avg", None),
            ("Summe", "summe", None),
        ]

        for label, key, max_val in metrics_to_compare:
            jp_values = [analyze_numbers(d["zahlen"])[key] for d in jackpot_draws]
            nm_values = [analyze_numbers(d["zahlen"])[key] for d in normal_draws]

            jp_avg = np.mean(jp_values)
            nm_avg = np.mean(nm_values)
            diff = jp_avg - nm_avg
            diff_pct = (diff / nm_avg * 100) if nm_avg != 0 else 0

            if max_val:
                print(f"{label:<25} {jp_avg:>12.1f}/20 {nm_avg:>12.1f}/20 {diff:>+10.2f} ({diff_pct:+.1f}%)")
            else:
                print(f"{label:<25} {jp_avg:>15.1f} {nm_avg:>15.1f} {diff:>+12.1f}")

    # 5. Analysiere Zahlen-Haeufigkeit an Jackpot-Tagen
    print(f"\n{'='*70}")
    print("TEIL 3: ZAHLEN-HAEUFIGKEIT AN JACKPOT-TAGEN 2023")
    print(f"{'='*70}")

    # Zaehle Zahlen an Jackpot-Tagen
    jp_counter = Counter()
    for draw in jackpot_draws:
        jp_counter.update(draw["zahlen"])

    # Zaehle Zahlen an normalen Tagen (normalisiert)
    nm_counter = Counter()
    for draw in normal_draws:
        nm_counter.update(draw["zahlen"])

    # Normalisiere
    jp_total = len(jackpot_draws)
    nm_total = len(normal_draws)

    print(f"\nTop 20 Zahlen an Jackpot-Tagen (vs Erwartung):")
    print(f"{'Zahl':>6} {'JP-Freq':>10} {'Normal-Freq':>12} {'Ratio':>8}")
    print("-" * 40)

    ratios = []
    for zahl in range(1, 71):
        jp_freq = jp_counter[zahl] / jp_total if jp_total > 0 else 0
        nm_freq = nm_counter[zahl] / nm_total if nm_total > 0 else 0
        ratio = jp_freq / nm_freq if nm_freq > 0 else 1.0
        ratios.append((zahl, jp_freq, nm_freq, ratio))

    # Sortiere nach Ratio (hoeher = ueberrepraesentiert an Jackpot-Tagen)
    ratios.sort(key=lambda x: x[3], reverse=True)

    for zahl, jp_freq, nm_freq, ratio in ratios[:20]:
        birthday = "BD" if zahl <= 31 else ""
        print(f"{zahl:>6} {jp_freq:>10.1%} {nm_freq:>12.1%} {ratio:>8.2f}x  {birthday}")

    print(f"\nUnterrepraesentiert an Jackpot-Tagen:")
    for zahl, jp_freq, nm_freq, ratio in ratios[-10:]:
        birthday = "BD" if zahl <= 31 else ""
        print(f"{zahl:>6} {jp_freq:>10.1%} {nm_freq:>12.1%} {ratio:>8.2f}x  {birthday}")

    # 6. Regionale Praeferenz-Ableitung aus "Andere 10"
    print(f"\n{'='*70}")
    print("TEIL 4: ABGELEITETE REGIONALE PRAEFERENZEN")
    print(f"{'='*70}")

    print("""
Basierend auf den "Andere 10" der verifizierten Jackpots:

BRANDENBURG (Kyritz):
  Andere 10: [2, 9, 19, 35, 39, 49, 54, 55, 62, 64]
  - 3/10 Birthday → Brandenburg-Spieler bevorzugen NICHT Birthday
  - 4/10 Gerade → Spieler bevorzugen UNGERADE (deshalb 8/10 gerade im Gewinner)
  - Durchschnitt 38.8 → Spieler bevorzugen MITTLERE Zahlen

BAYERN (Oberbayern):
  Andere 10: [6, 13, 24, 36, 38, 40, 43, 51, 56, 63]
  - 3/10 Birthday → Bayern-Spieler bevorzugen NICHT Birthday
  - 6/10 Gerade → Spieler bevorzugen GERADE (deshalb 4/10 gerade im Gewinner)
  - Durchschnitt 37.0 → Spieler bevorzugen MITTLERE Zahlen

SACHSEN (Nordsachsen):
  Andere 10: [3, 7, 12, 13, 16, 17, 21, 36, 52, 54]
  - 7/10 Birthday → Sachsen-Spieler bevorzugen STARK Birthday!
  - 5/10 Gerade → Ausgeglichen
  - Durchschnitt 23.1 → Spieler bevorzugen NIEDRIGE Zahlen
""")

    # 7. Speichere Ergebnisse
    results = {
        "analyse": "Regionale Praeferenzen aus Jackpot-Daten",
        "datum": datetime.now().isoformat(),
        "verifizierte_jackpots": {
            event.get("city", event["id"]): {
                "region": event.get("region"),
                "andere_10": sorted(list(set(event["drawn_20"]) - set(event["winner_10"]))),
                "metriken": analyze_numbers(
                    list(set(event["drawn_20"]) - set(event["winner_10"]))
                )
            }
            for event in verified_events
        },
        "jackpot_tage_2023": {
            "anzahl": len(jackpot_draws),
            "normale_tage": len(normal_draws),
        },
        "abgeleitete_praeferenzen": {
            "Brandenburg": {
                "birthday_praeferenz": "NIEDRIG",
                "gerade_praeferenz": "UNGERADE",
                "zahlen_niveau": "MITTEL",
            },
            "Bayern": {
                "birthday_praeferenz": "NIEDRIG",
                "gerade_praeferenz": "GERADE",
                "zahlen_niveau": "MITTEL",
            },
            "Sachsen": {
                "birthday_praeferenz": "HOCH",
                "gerade_praeferenz": "AUSGEGLICHEN",
                "zahlen_niveau": "NIEDRIG",
            },
        }
    }

    output_path = base_path / "results/regional_preferences_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    # 8. 2024 Analyse
    print(f"\n{'='*70}")
    print("TEIL 5: ANALYSE 2024")
    print(f"{'='*70}")

    # Finde 2024 Jackpots
    jackpot_dates_2024 = set()
    for event in verified_events:
        if "2024" in event["date"]:
            d = datetime.strptime(event["date"], "%Y-%m-%d")
            jackpot_dates_2024.add(d.strftime("%d.%m.%Y"))

    print(f"\nVerifizierte Jackpots 2024: {len(jackpot_dates_2024)}")

    if jackpot_dates_2024:
        for event in verified_events:
            if "2024" in event["date"]:
                city = event.get("city", event["id"])
                region = event.get("region", "Unknown")
                winner = set(event["winner_10"])
                drawn = set(event["drawn_20"])
                other = list(drawn - winner)

                metrics = analyze_numbers(other)

                print(f"\n{city} ({region}):")
                print(f"  Andere 10: {sorted(other)}")
                print(f"  Birthday:  {metrics['birthday']}/10")
                print(f"  Gerade:    {metrics['gerade']}/10")
                print(f"  Durchschn: {metrics['avg']:.1f}")
    else:
        print("Keine verifizierten 2024 Jackpots mit Gewinner-Zahlen gefunden.")
        print("Nur Nordsachsen (24.01.2024) ist verifiziert.")

    return results


if __name__ == "__main__":
    main()
