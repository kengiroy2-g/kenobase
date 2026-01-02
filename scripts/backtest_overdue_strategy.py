#!/usr/bin/env python3
"""
Backtest: Überfällige-Zahlen-Strategie
======================================

Generiert Tickets aus überfälligen Zahlen (Z-Score basiert) und testet
die Performance nach Tagestypen:
- Normale Tage
- Tage VOR Jackpot (1-3 Tage)
- Tage NACH Jackpot (1-7 Tage, 8-30 Tage)
- Jackpot-Tage selbst
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_FILE = BASE_DIR / "results" / "overdue_strategy_backtest.json"

# KENO Gewinnquoten (Typ 10)
KENO_QUOTES_TYP10 = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
    5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000
}

# Einsatz pro Ticket
EINSATZ = 10  # Euro


def load_data() -> pd.DataFrame:
    """Lädt KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    # Zahlen als Liste extrahieren
    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].values.tolist()

    return df


def load_jackpot_dates() -> set:
    """Lädt alle Jackpot-Tage aus GQ-Daten."""
    gq_files = [
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2023.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_02-2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv",
    ]

    jackpot_days = set()
    for f in gq_files:
        if f.exists():
            try:
                df = pd.read_csv(f, encoding="utf-8")
                mask = (df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)
                jackpots = df[mask]["Datum"]
                for date_str in jackpots:
                    try:
                        parsed = datetime.strptime(date_str, "%d.%m.%Y").date()
                        jackpot_days.add(parsed)
                    except:
                        pass
            except Exception as e:
                print(f"Fehler beim Laden von {f}: {e}")

    return jackpot_days


def calculate_overdue_at_date(df: pd.DataFrame, target_idx: int, z_threshold: float = 1.0) -> list[int]:
    """
    Berechnet überfällige Zahlen zum Zeitpunkt vor einer Ziehung.

    Args:
        df: DataFrame mit historischen Daten
        target_idx: Index der Ziel-Ziehung
        z_threshold: Z-Score Schwelle für "überfällig"

    Returns:
        Liste der überfälligen Zahlen, sortiert nach Z-Score
    """
    if target_idx < 100:  # Mindestens 100 Ziehungen Historie
        return []

    # Nur Daten VOR der Ziel-Ziehung verwenden
    history = df.iloc[:target_idx]

    # Letzte Erscheinung jeder Zahl berechnen
    last_seen = {i: -1 for i in range(1, 71)}
    gap_history = {i: [] for i in range(1, 71)}

    for idx, row in history.iterrows():
        zahlen = row["zahlen"]
        for z in range(1, 71):
            if z in zahlen:
                if last_seen[z] >= 0:
                    gap = idx - last_seen[z]
                    gap_history[z].append(gap)
                last_seen[z] = idx

    # Aktuelle Lücke und Z-Score berechnen
    current_idx = target_idx - 1
    overdue = []

    for z in range(1, 71):
        if last_seen[z] < 0 or len(gap_history[z]) < 10:
            continue

        current_gap = current_idx - last_seen[z]
        avg_gap = np.mean(gap_history[z])
        std_gap = np.std(gap_history[z])

        if std_gap > 0:
            z_score = (current_gap - avg_gap) / std_gap
            if z_score >= z_threshold:
                overdue.append((z, z_score, current_gap))

    # Nach Z-Score sortieren (höchste zuerst)
    overdue.sort(key=lambda x: -x[1])

    return overdue


def generate_ticket_from_overdue(
    overdue: list,
    ticket_size: int = 10,
    min_overdue: int = 3,
    fill_with_rare: bool = True,
    rare_numbers: list[int] = None
) -> list[int]:
    """
    Generiert ein Ticket aus überfälligen Zahlen.

    Args:
        overdue: Liste von (zahl, z_score, gap) Tupeln
        ticket_size: Anzahl Zahlen im Ticket
        min_overdue: Minimum überfällige Zahlen erforderlich
        fill_with_rare: Fülle auf mit seltenen Zahlen
        rare_numbers: Fallback-Zahlen

    Returns:
        Liste der Ticket-Zahlen
    """
    if len(overdue) < min_overdue:
        return []

    # Überfällige Zahlen nehmen
    ticket = [z[0] for z in overdue[:ticket_size]]

    # Auffüllen wenn nötig
    if fill_with_rare and len(ticket) < ticket_size and rare_numbers:
        for num in rare_numbers:
            if num not in ticket:
                ticket.append(num)
                if len(ticket) >= ticket_size:
                    break

    if len(ticket) < ticket_size:
        return []

    return sorted(ticket[:ticket_size])


def calculate_hits(ticket: list[int], drawn: list[int]) -> int:
    """Berechnet Treffer zwischen Ticket und Ziehung."""
    return len(set(ticket) & set(drawn))


def calculate_payout(hits: int, ticket_type: int = 10) -> float:
    """Berechnet Auszahlung basierend auf Treffern."""
    if ticket_type == 10:
        return KENO_QUOTES_TYP10.get(hits, 0)
    return 0


def classify_day(
    date: datetime,
    jackpot_days: set,
    df: pd.DataFrame
) -> str:
    """
    Klassifiziert einen Tag nach seiner Beziehung zu Jackpots.

    Returns:
        "jackpot": Jackpot-Tag selbst
        "pre_jackpot_1": 1 Tag vor Jackpot
        "pre_jackpot_2_3": 2-3 Tage vor Jackpot
        "post_jackpot_1_7": 1-7 Tage nach Jackpot
        "post_jackpot_8_30": 8-30 Tage nach Jackpot
        "normal": Normaler Tag
    """
    current_date = date.date() if hasattr(date, 'date') else date

    # Ist es ein Jackpot-Tag?
    if current_date in jackpot_days:
        return "jackpot"

    # Prüfe Tage vor Jackpot
    for days_ahead in range(1, 4):
        future_date = current_date + timedelta(days=days_ahead)
        if future_date in jackpot_days:
            if days_ahead == 1:
                return "pre_jackpot_1"
            else:
                return "pre_jackpot_2_3"

    # Prüfe Tage nach Jackpot
    for days_back in range(1, 31):
        past_date = current_date - timedelta(days=days_back)
        if past_date in jackpot_days:
            if days_back <= 7:
                return "post_jackpot_1_7"
            else:
                return "post_jackpot_8_30"

    return "normal"


def run_backtest(
    df: pd.DataFrame,
    jackpot_days: set,
    z_threshold: float = 0.5,
    ticket_size: int = 10,
    start_idx: int = 200,
    min_overdue: int = 3
) -> dict:
    """
    Führt Backtest der Überfällige-Zahlen-Strategie durch.

    Args:
        df: DataFrame mit Ziehungsdaten
        jackpot_days: Set der Jackpot-Tage
        z_threshold: Z-Score Schwelle
        ticket_size: Ticket-Größe
        start_idx: Start-Index (für genug Historie)
        min_overdue: Minimum überfällige Zahlen

    Returns:
        Dictionary mit Backtest-Ergebnissen
    """
    # Seltene Zahlen aus System-Perspektive (Fallback)
    RARE_NUMBERS = [22, 7, 60, 41, 69, 70, 18, 24, 29, 19, 21, 32, 11, 13, 30]

    results = {
        "normal": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
        "jackpot": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
        "pre_jackpot_1": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
        "pre_jackpot_2_3": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
        "post_jackpot_1_7": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
        "post_jackpot_8_30": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "tickets": []},
    }

    skipped = 0

    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        date = row["Datum"]
        drawn = row["zahlen"]

        # Überfällige Zahlen berechnen (mit Daten VOR dieser Ziehung)
        overdue = calculate_overdue_at_date(df, idx, z_threshold)

        # Ticket generieren mit Fallback auf seltene Zahlen
        ticket = generate_ticket_from_overdue(
            overdue, ticket_size, min_overdue=min_overdue,
            fill_with_rare=True, rare_numbers=RARE_NUMBERS
        )

        if not ticket:
            skipped += 1
            continue

        # Tag klassifizieren
        day_type = classify_day(date, jackpot_days, df)

        # Treffer berechnen
        hits = calculate_hits(ticket, drawn)
        payout = calculate_payout(hits, ticket_size)

        # Ergebnisse speichern
        results[day_type]["plays"] += 1
        results[day_type]["cost"] += EINSATZ
        results[day_type]["payout"] += payout

        hits_key = str(hits)
        results[day_type]["hits_dist"][hits_key] = results[day_type]["hits_dist"].get(hits_key, 0) + 1

        # Beispiel-Tickets speichern (max 5 pro Kategorie)
        if len(results[day_type]["tickets"]) < 5:
            results[day_type]["tickets"].append({
                "date": str(date.date()),
                "ticket": ticket,
                "drawn": drawn[:10],  # Erste 10 der Ziehung
                "hits": hits,
                "payout": payout
            })

    # Statistiken berechnen
    for day_type in results:
        r = results[day_type]
        if r["plays"] > 0:
            r["roi"] = round((r["payout"] - r["cost"]) / r["cost"] * 100, 2)
            r["avg_hits"] = round(sum(int(k) * v for k, v in r["hits_dist"].items()) / r["plays"], 3)
            r["profit"] = r["payout"] - r["cost"]
        else:
            r["roi"] = 0
            r["avg_hits"] = 0
            r["profit"] = 0

    return {
        "results_by_day_type": results,
        "parameters": {
            "z_threshold": z_threshold,
            "ticket_size": ticket_size,
            "start_idx": start_idx,
            "skipped_days": skipped
        }
    }


def print_results(backtest_results: dict):
    """Druckt Backtest-Ergebnisse."""
    print("\n" + "=" * 80)
    print("BACKTEST: ÜBERFÄLLIGE-ZAHLEN-STRATEGIE")
    print("=" * 80)

    params = backtest_results["parameters"]
    print(f"\nParameter:")
    print(f"  Z-Score Schwelle: >= {params['z_threshold']}")
    print(f"  Ticket-Größe: Typ {params['ticket_size']}")
    print(f"  Übersprungene Tage: {params['skipped_days']}")

    print("\n" + "-" * 80)
    print("ERGEBNISSE NACH TAGESTYP")
    print("-" * 80)

    results = backtest_results["results_by_day_type"]

    # Sortierung für Ausgabe
    order = ["normal", "jackpot", "pre_jackpot_1", "pre_jackpot_2_3",
             "post_jackpot_1_7", "post_jackpot_8_30"]

    labels = {
        "normal": "Normale Tage",
        "jackpot": "JACKPOT-TAGE",
        "pre_jackpot_1": "1 Tag VOR Jackpot",
        "pre_jackpot_2_3": "2-3 Tage VOR Jackpot",
        "post_jackpot_1_7": "1-7 Tage NACH Jackpot",
        "post_jackpot_8_30": "8-30 Tage NACH Jackpot"
    }

    print(f"\n{'Tagestyp':<25} {'Spiele':>8} {'Kosten':>10} {'Auszahl.':>10} {'Profit':>10} {'ROI':>10} {'Avg Hits':>10}")
    print("-" * 85)

    for day_type in order:
        r = results[day_type]
        label = labels[day_type]
        print(f"{label:<25} {r['plays']:>8} {r['cost']:>10.0f}€ {r['payout']:>10.0f}€ {r['profit']:>+10.0f}€ {r['roi']:>+9.1f}% {r['avg_hits']:>10.3f}")

    # Gesamt
    print("-" * 85)
    total_plays = sum(r["plays"] for r in results.values())
    total_cost = sum(r["cost"] for r in results.values())
    total_payout = sum(r["payout"] for r in results.values())
    total_profit = total_payout - total_cost
    total_roi = (total_profit / total_cost * 100) if total_cost > 0 else 0
    print(f"{'GESAMT':<25} {total_plays:>8} {total_cost:>10.0f}€ {total_payout:>10.0f}€ {total_profit:>+10.0f}€ {total_roi:>+9.1f}%")

    # Treffer-Verteilung
    print("\n" + "-" * 80)
    print("TREFFER-VERTEILUNG")
    print("-" * 80)

    print(f"\n{'Tagestyp':<25}", end="")
    for i in range(11):
        print(f"{i:>6}", end="")
    print()
    print("-" * 90)

    for day_type in order:
        r = results[day_type]
        label = labels[day_type][:24]
        print(f"{label:<25}", end="")
        for i in range(11):
            count = r["hits_dist"].get(str(i), 0)
            print(f"{count:>6}", end="")
        print()

    # Beispiel-Tickets für Jackpot-Tage
    print("\n" + "-" * 80)
    print("BEISPIEL-TICKETS AN JACKPOT-TAGEN")
    print("-" * 80)

    for ticket_info in results["jackpot"]["tickets"]:
        print(f"\n  Datum: {ticket_info['date']}")
        print(f"  Ticket: {ticket_info['ticket']}")
        print(f"  Gezogen: {ticket_info['drawn']}")
        print(f"  Treffer: {ticket_info['hits']}, Auszahlung: {ticket_info['payout']}€")

    # Analyse
    print("\n" + "=" * 80)
    print("ANALYSE")
    print("=" * 80)

    jackpot_roi = results["jackpot"]["roi"]
    normal_roi = results["normal"]["roi"]
    pre1_roi = results["pre_jackpot_1"]["roi"]
    post1_7_roi = results["post_jackpot_1_7"]["roi"]

    print(f"""
ERKENNTNISSE:

1. JACKPOT-TAGE vs. NORMALE TAGE:
   - Jackpot-Tage ROI: {jackpot_roi:+.1f}%
   - Normale Tage ROI: {normal_roi:+.1f}%
   - Differenz: {jackpot_roi - normal_roi:+.1f}%

2. VOR JACKPOT (1 Tag):
   - ROI: {pre1_roi:+.1f}%
   - Interpretation: {"BESSER" if pre1_roi > normal_roi else "SCHLECHTER"} als normale Tage

3. NACH JACKPOT (1-7 Tage):
   - ROI: {post1_7_roi:+.1f}%
   - Interpretation: {"Cooldown-Effekt bestätigt" if post1_7_roi < normal_roi else "Kein Cooldown-Effekt"}

4. STRATEGIE-EMPFEHLUNG:
""")

    # Beste Tagestypen finden
    sorted_types = sorted(
        [(day_type, results[day_type]["roi"]) for day_type in order if results[day_type]["plays"] > 10],
        key=lambda x: -x[1]
    )

    print("   BESTE Tagestypen für Überfällige-Zahlen-Strategie:")
    for i, (day_type, roi) in enumerate(sorted_types[:3], 1):
        print(f"   {i}. {labels[day_type]}: {roi:+.1f}%")

    print("\n   SCHLECHTESTE Tagestypen:")
    for i, (day_type, roi) in enumerate(sorted_types[-2:], 1):
        print(f"   {i}. {labels[day_type]}: {roi:+.1f}%")


def main():
    print("=" * 80)
    print("BACKTEST: ÜBERFÄLLIGE-ZAHLEN-STRATEGIE NACH TAGESTYPEN")
    print("=" * 80)

    # Daten laden
    print("\nLade Daten...")
    df = load_data()
    print(f"Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['Datum'].min()} - {df['Datum'].max()}")

    # Jackpot-Tage identifizieren
    jackpot_days = load_jackpot_dates()
    print(f"Jackpot-Tage: {len(jackpot_days)}")

    # Backtest durchführen
    print("\nFühre Backtest durch...")
    results = run_backtest(
        df=df,
        jackpot_days=jackpot_days,
        z_threshold=0.5,
        ticket_size=10,
        start_idx=200,
        min_overdue=3
    )

    # Ergebnisse ausgeben
    print_results(results)

    # Ergebnisse speichern
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        # Tickets für JSON serialisierbar machen
        for day_type in results["results_by_day_type"]:
            for ticket in results["results_by_day_type"][day_type]["tickets"]:
                ticket["drawn"] = [int(x) for x in ticket["drawn"]]
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
