"""
Backtest ZWEI GETRENNTE Strategien:

STRATEGIE 1: Jackpot-Optimierte Zahlen
  - Ziel: Jackpot (10/10) gewinnen
  - Test: Wie oft treffen wir 8+, 9+, 10/10?

STRATEGIE 2: Timing nach Jackpot
  - Ziel: Maximiere regulaere Gewinne
  - Test: ROI in BOOST vs COOLDOWN Phase (mit RANDOM Tickets)
"""

import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import random
import numpy as np

# KENO Quoten (Typ 10, pro 1 EUR Einsatz)
KENO_QUOTES_TYP10 = {
    0: 2, 1: 0, 2: 0, 3: 0, 4: 0,
    5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000
}

# Strategie 1: Jackpot-Optimierte Zahlen
JACKPOT_FAVORITES = {43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45}
JACKPOT_AVOID = {1, 16, 21, 27, 29, 37, 67, 25, 68, 28}


def load_keno_data(filepath: Path) -> list[dict]:
    """Laedt KENO-Ziehungsdaten."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                datum_str = row.get("Datum", "").strip()
                if not datum_str:
                    continue
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                numbers = []
                for i in range(1, 21):
                    col = f"Keno_Z{i}"
                    if col in row and row[col]:
                        numbers.append(int(row[col]))
                if len(numbers) == 20:
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers)
                    })
            except:
                continue
    return sorted(data, key=lambda x: x["datum"])


def load_jackpot_dates(events_path: Path) -> list[datetime]:
    """Laedt alle bekannten Jackpot-Daten."""
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    dates = []
    for event in data.get("events", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except:
            pass
    for event in data.get("pending_from_quotes_2023", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except:
            pass
    return sorted(dates)


def get_phase(datum: datetime, jackpot_dates: list[datetime]) -> str:
    """Bestimmt die Phase basierend auf letztem Jackpot."""
    last_jackpot = None
    for jp in jackpot_dates:
        if jp < datum:
            last_jackpot = jp
        else:
            break
    if last_jackpot is None:
        return "UNKNOWN"
    days_since = (datum - last_jackpot).days
    if days_since <= 7:
        return "EARLY"
    elif days_since <= 14:
        return "BOOST"
    elif days_since <= 21:
        return "NEUTRAL"
    else:
        return "COOLDOWN"


def generate_jackpot_optimized_ticket() -> set[int]:
    """Strategie 1: Ticket optimiert fuer Jackpot."""
    pool = [z for z in range(1, 71) if z not in JACKPOT_AVOID]
    weights = []
    for z in pool:
        w = 1.0
        if z in JACKPOT_FAVORITES:
            w *= 3.0
        if z <= 31:
            w *= 0.4
        if z > 50:
            w *= 1.5
        if z % 10 == 1:
            w *= 0.2
        weights.append(w)
    total = sum(weights)
    weights = [w/total for w in weights]

    ticket = set()
    while len(ticket) < 10:
        choice = random.choices(pool, weights=weights, k=1)[0]
        ticket.add(choice)
    return ticket


def generate_random_ticket() -> set[int]:
    """Zufaelliges Ticket."""
    return set(random.sample(range(1, 71), 10))


def main():
    print("=" * 70)
    print("BACKTEST: ZWEI GETRENNTE STRATEGIEN")
    print("=" * 70)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"

    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)

    draws_2023_2024 = [d for d in draws if d["datum"].year in [2023, 2024]]

    print(f"\nDaten: {len(draws_2023_2024)} Ziehungen, {len(jackpot_dates)} Jackpot-Tage")

    # ================================================================
    # STRATEGIE 1: JACKPOT-OPTIMIERTE ZAHLEN
    # ================================================================
    print(f"\n{'='*70}")
    print("STRATEGIE 1: JACKPOT-OPTIMIERTE ZAHLEN")
    print("Ziel: Jackpot (10/10) oder hohe Treffer (8+, 9+)")
    print(f"{'='*70}")

    n_simulations = 1000

    # Zaehle hohe Treffer
    opt_high = {"8+": 0, "9+": 0, "10": 0, "total": 0}
    rand_high = {"8+": 0, "9+": 0, "10": 0, "total": 0}

    opt_treffer_sum = 0
    rand_treffer_sum = 0

    for _ in range(n_simulations):
        for draw in draws_2023_2024:
            opt_ticket = generate_jackpot_optimized_ticket()
            rand_ticket = generate_random_ticket()

            opt_treffer = len(opt_ticket & draw["zahlen"])
            rand_treffer = len(rand_ticket & draw["zahlen"])

            opt_treffer_sum += opt_treffer
            rand_treffer_sum += rand_treffer
            opt_high["total"] += 1
            rand_high["total"] += 1

            if opt_treffer >= 8:
                opt_high["8+"] += 1
            if opt_treffer >= 9:
                opt_high["9+"] += 1
            if opt_treffer == 10:
                opt_high["10"] += 1

            if rand_treffer >= 8:
                rand_high["8+"] += 1
            if rand_treffer >= 9:
                rand_high["9+"] += 1
            if rand_treffer == 10:
                rand_high["10"] += 1

    print(f"\n{n_simulations} Simulationen x {len(draws_2023_2024)} Ziehungen = {opt_high['total']:,} Spiele")

    print(f"\n{'Metrik':<20} {'Optimiert':>15} {'Random':>15} {'Vorteil':>15}")
    print("-" * 65)

    print(f"{'Avg Treffer':<20} {opt_treffer_sum/opt_high['total']:>15.3f} "
          f"{rand_treffer_sum/rand_high['total']:>15.3f} "
          f"{(opt_treffer_sum-rand_treffer_sum)/opt_high['total']:>+15.3f}")

    print(f"{'8+ Treffer':<20} {opt_high['8+']/n_simulations:>15.1f} "
          f"{rand_high['8+']/n_simulations:>15.1f} "
          f"{(opt_high['8+']-rand_high['8+'])/n_simulations:>+15.1f}")

    print(f"{'9+ Treffer':<20} {opt_high['9+']/n_simulations:>15.1f} "
          f"{rand_high['9+']/n_simulations:>15.1f} "
          f"{(opt_high['9+']-rand_high['9+'])/n_simulations:>+15.1f}")

    print(f"{'10/10 JACKPOT':<20} {opt_high['10']/n_simulations:>15.2f} "
          f"{rand_high['10']/n_simulations:>15.2f} "
          f"{(opt_high['10']-rand_high['10'])/n_simulations:>+15.2f}")

    # Prozentual
    print(f"\n{'Rate pro 1000 Spiele:'}")
    print(f"  8+ Treffer: Optimiert {opt_high['8+']/opt_high['total']*1000:.2f} vs Random {rand_high['8+']/rand_high['total']*1000:.2f}")
    print(f"  9+ Treffer: Optimiert {opt_high['9+']/opt_high['total']*1000:.4f} vs Random {rand_high['9+']/rand_high['total']*1000:.4f}")

    # ================================================================
    # STRATEGIE 2: TIMING NACH JACKPOT
    # ================================================================
    print(f"\n{'='*70}")
    print("STRATEGIE 2: TIMING NACH JACKPOT")
    print("Ziel: Maximiere Gewinne durch Timing (mit RANDOM Tickets)")
    print(f"{'='*70}")

    phase_results = defaultdict(lambda: {"games": 0, "cost": 0, "win": 0})

    for _ in range(100):  # 100 Simulationen
        for draw in draws_2023_2024:
            phase = get_phase(draw["datum"], jackpot_dates)
            ticket = generate_random_ticket()  # NUR RANDOM!
            treffer = len(ticket & draw["zahlen"])
            win = KENO_QUOTES_TYP10.get(treffer, 0)

            phase_results[phase]["games"] += 1
            phase_results[phase]["cost"] += 1
            phase_results[phase]["win"] += win

    print(f"\n{'Phase':<15} {'Spiele':>10} {'Kosten':>12} {'Gewinn':>12} {'ROI':>12}")
    print("-" * 65)

    for phase in ["EARLY", "BOOST", "NEUTRAL", "COOLDOWN", "UNKNOWN"]:
        if phase in phase_results:
            data = phase_results[phase]
            roi = (data["win"] - data["cost"]) / data["cost"] * 100 if data["cost"] > 0 else 0

            marker = ""
            if phase == "BOOST":
                marker = " ← ERWARTUNG: GUT"
            elif phase == "COOLDOWN":
                marker = " ← ERWARTUNG: SCHLECHT"

            print(f"{phase:<15} {data['games']:>10,} {data['cost']:>12,} EUR "
                  f"{data['win']:>12,} EUR {roi:>+11.1f}%{marker}")

    # ================================================================
    # FAZIT
    # ================================================================
    print(f"\n{'='*70}")
    print("FAZIT")
    print(f"{'='*70}")

    print("""
STRATEGIE 1 (Jackpot-Optimierte Zahlen):
  → Testet: Haben unsere Zahlen hoehere Jackpot-Chance?
  → Ergebnis: Siehe oben (8+, 9+, 10/10 Vergleich)

STRATEGIE 2 (Timing nach Jackpot):
  → Testet: Ist ROI in BOOST besser als in COOLDOWN?
  → Ergebnis: Siehe oben (Phasen-ROI)

WICHTIG:
  - Strategie 1 = WELCHE Zahlen
  - Strategie 2 = WANN spielen
  - Beide sind UNABHAENGIG voneinander!
""")

    # Speichern
    results = {
        "datum": datetime.now().isoformat(),
        "strategie_1_jackpot_zahlen": {
            "simulationen": n_simulations,
            "spiele_total": opt_high["total"],
            "optimiert_8plus": opt_high["8+"],
            "random_8plus": rand_high["8+"],
            "optimiert_9plus": opt_high["9+"],
            "random_9plus": rand_high["9+"],
            "optimiert_10": opt_high["10"],
            "random_10": rand_high["10"],
        },
        "strategie_2_timing": {
            phase: {
                "games": data["games"],
                "roi": (data["win"] - data["cost"]) / data["cost"] * 100 if data["cost"] > 0 else 0
            }
            for phase, data in phase_results.items()
        }
    }

    output_path = base_path / "results/backtest_two_strategies.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
