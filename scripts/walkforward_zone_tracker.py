#!/usr/bin/env python
"""
Walk-Forward Zone Tracker

WICHTIG: KENO wurde von Top-Ingenieuren und Mathematikern entworfen.
Dieser Test ist EHRLICH - kein Zukunftswissen!

Ablauf:
1. Starte am 01.01.2024
2. Berechne aktive Zone NUR mit historischen Daten
3. Erstelle Ticket aus der Zone
4. Tracke das Ticket bis die Zone sich ändert
5. Wiederhole bis Ende 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import json

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"

WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].apply(
        lambda row: [int(x) for x in row if pd.notna(x)], axis=1
    )

    df = df.dropna(subset=["datum"])
    df = df.sort_values("datum").reset_index(drop=True)
    df["weekday"] = df["datum"].dt.dayofweek
    return df


def get_keno_quote(hits):
    """KENO Typ 9 Quoten."""
    quotes = {0: 2, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000}
    return quotes.get(hits, 0)


def calculate_active_zone(hist_df, target_weekday, long_window=50, short_window=5):
    """
    Berechne aktive Zone NUR mit historischen Daten.

    Kombiniert:
    - Wochentag-spezifische Frequenz (70%)
    - Kurzfristiges Momentum (30%)
    """
    # Langzeit: Wochentag-spezifisch
    wd_data = hist_df[hist_df["weekday"] == target_weekday].tail(long_window)

    freq_long = defaultdict(int)
    for zahlen in wd_data["zahlen"]:
        for num in zahlen:
            freq_long[num] += 1

    # Kurzzeit: Letzte N Ziehungen (alle Wochentage)
    recent = hist_df.tail(short_window)

    freq_short = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq_short[num] += 1

    # Kombinierter Score
    scores = {}
    for num in range(1, 71):
        long_score = freq_long[num] / max(len(wd_data), 1)
        short_score = freq_short[num] / max(len(recent), 1)

        # 70% Langzeit, 30% Kurzzeit
        combined = 0.7 * long_score + 0.3 * short_score

        # Momentum Bonus
        if short_score > long_score * 1.5 and long_score > 0:
            combined *= 1.2

        scores[num] = combined

    # Top 23 = Aktive Zone (1/3 von 70)
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    zone = [n for n, _ in sorted_scores[:23]]

    return zone, scores


def zone_similarity(zone1, zone2):
    """Berechne Ähnlichkeit zwischen zwei Zonen (0-100%)."""
    set1, set2 = set(zone1), set(zone2)
    overlap = len(set1 & set2)
    return overlap / 23 * 100


def run_walkforward_test(df, start_date="2024-01-01", zone_change_threshold=30):
    """
    Walk-Forward Test ab start_date.

    Erstellt neue Zone wenn sich >30% der Zahlen ändern.
    Trackt jedes Ticket bis zum Zonen-Wechsel.
    """
    start_dt = pd.Timestamp(start_date)

    # Finde Start-Index
    start_idx = df[df["datum"] >= start_dt].index[0]

    print(f"Start: {start_date}")
    print(f"Ziehungen ab Start: {len(df) - start_idx}")
    print(f"Zonen-Wechsel Schwelle: {zone_change_threshold}% Änderung")
    print("=" * 80)

    all_zones = []  # Alle erstellten Zonen
    all_results = []  # Alle Ziehungs-Ergebnisse

    current_zone = None
    current_ticket = None
    zone_start_date = None
    zone_id = 0

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_weekday = current["weekday"]
        current_numbers = set(current["zahlen"])

        # Historische Daten BIS GESTERN (kein Zukunftswissen!)
        hist = df.iloc[:i]

        # Berechne neue Zone
        new_zone, scores = calculate_active_zone(
            hist, current_weekday,
            long_window=50, short_window=5
        )

        # Prüfe ob Zone-Wechsel nötig
        need_new_zone = False
        if current_zone is None:
            need_new_zone = True
            reason = "START"
        else:
            similarity = zone_similarity(current_zone, new_zone)
            if similarity < (100 - zone_change_threshold):
                need_new_zone = True
                reason = f"ÄNDERUNG ({100-similarity:.0f}% neu)"

        # Neue Zone erstellen
        if need_new_zone:
            # Alte Zone abschließen
            if current_zone is not None:
                zone_results = [r for r in all_results if r["zone_id"] == zone_id]
                if zone_results:
                    total_hits = sum(r["hits"] for r in zone_results)
                    total_draws = len(zone_results)
                    avg_hits = total_hits / total_draws

                    all_zones[-1]["end_date"] = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
                    all_zones[-1]["total_draws"] = total_draws
                    all_zones[-1]["avg_hits"] = avg_hits
                    all_zones[-1]["total_win"] = sum(r["win"] for r in zone_results)

            # Neue Zone starten
            zone_id += 1
            current_zone = new_zone
            current_ticket = new_zone[:9]
            zone_start_date = current_date

            all_zones.append({
                "zone_id": zone_id,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "weekday": WEEKDAYS[current_weekday],
                "reason": reason,
                "zone": current_zone,
                "ticket": current_ticket,
                "end_date": None,
                "total_draws": 0,
                "avg_hits": 0,
                "total_win": 0,
            })

        # Ticket testen
        ticket_set = set(current_ticket)
        hits = len(current_numbers & ticket_set)
        win = get_keno_quote(hits)

        # Zone-Hits (23 Zahlen)
        zone_set = set(current_zone)
        zone_hits = len(current_numbers & zone_set)

        all_results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "weekday": WEEKDAYS[current_weekday],
            "zone_id": zone_id,
            "ticket": current_ticket,
            "drawn": list(current_numbers),
            "hits": hits,
            "zone_hits": zone_hits,
            "win": win,
            "stake": 1,
        })

    # Letzte Zone abschließen
    if all_zones:
        zone_results = [r for r in all_results if r["zone_id"] == zone_id]
        if zone_results:
            all_zones[-1]["end_date"] = df.iloc[-1]["datum"].strftime("%Y-%m-%d")
            all_zones[-1]["total_draws"] = len(zone_results)
            all_zones[-1]["avg_hits"] = sum(r["hits"] for r in zone_results) / len(zone_results)
            all_zones[-1]["total_win"] = sum(r["win"] for r in zone_results)

    return all_zones, all_results


def print_zone_summary(zones):
    """Drucke Zusammenfassung aller Zonen."""
    print("\n" + "=" * 80)
    print("ALLE ERSTELLTEN ZONEN")
    print("=" * 80)

    print(f"\n{'ID':>3} {'Start':<12} {'Ende':<12} {'Tage':>5} {'Avg Hits':>9} {'Gewinn':>8} {'Ticket'}")
    print("-" * 90)

    for z in zones:
        print(f"{z['zone_id']:>3} {z['start_date']:<12} {z['end_date'] or 'läuft':<12} "
              f"{z['total_draws']:>5} {z['avg_hits']:>9.2f} {z['total_win']:>7.0f}€ "
              f"{z['ticket']}")


def print_monthly_summary(results):
    """Drucke monatliche Zusammenfassung."""
    print("\n" + "=" * 80)
    print("MONATLICHE ZUSAMMENFASSUNG")
    print("=" * 80)

    df = pd.DataFrame(results)
    df["datum"] = pd.to_datetime(df["datum"])
    df["month"] = df["datum"].dt.to_period("M")

    monthly = df.groupby("month").agg({
        "hits": ["sum", "mean", "count"],
        "zone_hits": "mean",
        "win": "sum",
        "stake": "sum",
    })

    print(f"\n{'Monat':<10} {'Zieh':>5} {'Avg Hits':>9} {'Zone Hits':>10} {'Einsatz':>8} {'Gewinn':>8} {'Netto':>8} {'ROI':>8}")
    print("-" * 80)

    total_stake = 0
    total_win = 0

    for month, row in monthly.iterrows():
        draws = row[("hits", "count")]
        avg_hits = row[("hits", "mean")]
        zone_hits = row[("zone_hits", "mean")]
        stake = row[("stake", "sum")]
        win = row[("win", "sum")]
        netto = win - stake
        roi = (win / stake - 1) * 100 if stake > 0 else 0

        total_stake += stake
        total_win += win

        print(f"{str(month):<10} {draws:>5} {avg_hits:>9.2f} {zone_hits:>10.2f} "
              f"{stake:>7.0f}€ {win:>7.0f}€ {netto:>+7.0f}€ {roi:>+7.1f}%")

    print("-" * 80)
    total_netto = total_win - total_stake
    total_roi = (total_win / total_stake - 1) * 100 if total_stake > 0 else 0
    print(f"{'GESAMT':<10} {len(df):>5} {df['hits'].mean():>9.2f} {df['zone_hits'].mean():>10.2f} "
          f"{total_stake:>7.0f}€ {total_win:>7.0f}€ {total_netto:>+7.0f}€ {total_roi:>+7.1f}%")


def print_hit_distribution(results):
    """Drucke Treffer-Verteilung."""
    print("\n" + "=" * 80)
    print("TREFFER-VERTEILUNG (Ticket = 9 Zahlen)")
    print("=" * 80)

    df = pd.DataFrame(results)

    print(f"\n{'Treffer':>8} {'Anzahl':>8} {'Prozent':>8} {'Quote':>8} {'Gesamt':>10}")
    print("-" * 50)

    for hits in range(10):
        count = len(df[df["hits"] == hits])
        pct = count / len(df) * 100
        quote = get_keno_quote(hits)
        total = count * quote

        bar = "#" * int(pct / 2)
        print(f"{hits:>8} {count:>8} {pct:>7.1f}% {quote:>7}€ {total:>9}€  {bar}")


def print_zone_hit_distribution(results):
    """Drucke Zone-Treffer-Verteilung (23 Zahlen)."""
    print("\n" + "=" * 80)
    print("ZONE-TREFFER-VERTEILUNG (Zone = 23 Zahlen)")
    print("=" * 80)

    df = pd.DataFrame(results)
    expected = 20 * 23 / 70  # 6.57

    print(f"\nErwartung bei Zufall: {expected:.2f} Treffer")
    print(f"Tatsächlich: {df['zone_hits'].mean():.2f} Treffer")
    print(f"Lift: {df['zone_hits'].mean() / expected:.3f}x")

    print(f"\n{'Treffer':>8} {'Anzahl':>8} {'Prozent':>8}")
    print("-" * 30)

    for hits in range(0, 16):
        count = len(df[df["zone_hits"] == hits])
        if count > 0:
            pct = count / len(df) * 100
            bar = "#" * int(pct / 2)
            print(f"{hits:>8} {count:>8} {pct:>7.1f}%  {bar}")


def print_high_wins(results, min_hits=6):
    """Drucke alle hohen Gewinne."""
    print("\n" + "=" * 80)
    print(f"HOHE GEWINNE ({min_hits}+ Treffer)")
    print("=" * 80)

    high = [r for r in results if r["hits"] >= min_hits]

    if not high:
        print("\nKeine hohen Gewinne.")
        return

    print(f"\n{'Datum':<12} {'Treffer':>8} {'Gewinn':>8} {'Ticket'}")
    print("-" * 70)

    for r in sorted(high, key=lambda x: -x["hits"]):
        print(f"{r['datum']:<12} {r['hits']:>8} {r['win']:>7}€  {r['ticket']}")


def main():
    print("=" * 80)
    print("WALK-FORWARD ZONE TRACKER")
    print("Ehrlicher Test ab 01.01.2024 - KEIN Zukunftswissen!")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().date()} bis {df['datum'].max().date()}")

    # Walk-Forward Test
    zones, results = run_walkforward_test(
        df,
        start_date="2024-01-01",
        zone_change_threshold=30  # Neue Zone wenn >30% Änderung
    )

    # Zusammenfassungen
    print_zone_summary(zones)
    print_monthly_summary(results)
    print_hit_distribution(results)
    print_zone_hit_distribution(results)
    print_high_wins(results)

    # Finale Statistik
    print("\n" + "=" * 80)
    print("FINALE STATISTIK")
    print("=" * 80)

    total_stake = len(results)
    total_win = sum(r["win"] for r in results)
    total_netto = total_win - total_stake
    roi = (total_win / total_stake - 1) * 100

    avg_hits = sum(r["hits"] for r in results) / len(results)
    avg_zone_hits = sum(r["zone_hits"] for r in results) / len(results)
    expected_zone = 20 * 23 / 70

    print(f"\nZeitraum: 01.01.2024 - {results[-1]['datum']}")
    print(f"Anzahl Ziehungen: {len(results)}")
    print(f"Anzahl Zonen erstellt: {len(zones)}")
    print(f"\nTicket Performance (9 Zahlen):")
    print(f"  Avg Hits: {avg_hits:.2f}")
    print(f"  Einsatz: {total_stake} EUR")
    print(f"  Gewinn: {total_win} EUR")
    print(f"  Netto: {total_netto:+} EUR")
    print(f"  ROI: {roi:+.1f}%")

    print(f"\nZone Performance (23 Zahlen = 'Das richtige Drittel'):")
    print(f"  Avg Zone Hits: {avg_zone_hits:.2f}")
    print(f"  Erwartung Zufall: {expected_zone:.2f}")
    print(f"  Lift: {avg_zone_hits / expected_zone:.3f}x")

    # Vergleich 2024 vs 2025
    results_2024 = [r for r in results if r["datum"].startswith("2024")]
    results_2025 = [r for r in results if r["datum"].startswith("2025")]

    if results_2024 and results_2025:
        print(f"\nJahresvergleich:")

        avg_2024 = sum(r["zone_hits"] for r in results_2024) / len(results_2024)
        avg_2025 = sum(r["zone_hits"] for r in results_2025) / len(results_2025)

        win_2024 = sum(r["win"] for r in results_2024)
        win_2025 = sum(r["win"] for r in results_2025)

        roi_2024 = (win_2024 / len(results_2024) - 1) * 100
        roi_2025 = (win_2025 / len(results_2025) - 1) * 100

        print(f"  2024: Zone Hits {avg_2024:.2f}, ROI {roi_2024:+.1f}%")
        print(f"  2025: Zone Hits {avg_2025:.2f}, ROI {roi_2025:+.1f}%")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)

    output = {
        "timestamp": datetime.now().isoformat(),
        "test_period": f"2024-01-01 bis {results[-1]['datum']}",
        "total_draws": len(results),
        "total_zones": len(zones),
        "total_stake": total_stake,
        "total_win": total_win,
        "total_netto": total_netto,
        "roi_percent": roi,
        "avg_ticket_hits": avg_hits,
        "avg_zone_hits": avg_zone_hits,
        "zone_lift": avg_zone_hits / expected_zone,
        "zones": zones,
        "monthly_summary": None,  # Zu groß für JSON
    }

    with open(RESULTS_DIR / "walkforward_zone_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Detaillierte Ergebnisse separat speichern
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "walkforward_zone_details.csv", index=False)

    print(f"\nErgebnisse gespeichert:")
    print(f"  {RESULTS_DIR / 'walkforward_zone_results.json'}")
    print(f"  {RESULTS_DIR / 'walkforward_zone_details.csv'}")


if __name__ == "__main__":
    main()
