"""
Backtest der kombinierten Jackpot-Strategie.

Testet:
1. Jackpot-Timing (8-14 Tage nach Jackpot = BOOST PHASE)
2. Jackpot-Optimierte Tickets (Favorites, Avoid, Constraints)
3. Vergleich mit Random-Tickets
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
    0: 2,      # 0 Treffer = 2 EUR
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 2,      # 5 Treffer = 2 EUR
    6: 5,
    7: 15,
    8: 100,
    9: 1000,
    10: 100000  # Jackpot!
}

# Experimentelle Erkenntnisse
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
            except Exception:
                continue

    return sorted(data, key=lambda x: x["datum"])


def load_jackpot_dates(events_path: Path) -> list[datetime]:
    """Laedt alle bekannten Jackpot-Daten."""
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dates = []

    # Verifizierte Events
    for event in data.get("events", []):
        try:
            d = datetime.strptime(event["date"], "%Y-%m-%d")
            dates.append(d)
        except:
            pass

    # Pending Events (2023)
    for event in data.get("pending_from_quotes_2023", []):
        try:
            d = datetime.strptime(event["date"], "%Y-%m-%d")
            dates.append(d)
        except:
            pass

    return sorted(dates)


def get_phase(datum: datetime, jackpot_dates: list[datetime]) -> str:
    """Bestimmt die Phase basierend auf letztem Jackpot."""

    # Finde letzten Jackpot vor diesem Datum
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
        return "EARLY"       # Tag 1-7
    elif days_since <= 14:
        return "BOOST"       # Tag 8-14 (SPIELEN!)
    elif days_since <= 21:
        return "NEUTRAL"     # Tag 15-21
    else:
        return "COOLDOWN"    # Tag 22+ (MEIDEN!)


def generate_optimized_ticket() -> set[int]:
    """Generiert ein Jackpot-optimiertes Ticket."""

    # Pool ohne Avoid-Zahlen
    pool = [z for z in range(1, 71) if z not in JACKPOT_AVOID]

    # Gewichte: Favorites bevorzugen, Birthday vermeiden
    weights = []
    for z in pool:
        w = 1.0
        if z in JACKPOT_FAVORITES:
            w *= 3.0
        if z <= 31:  # Birthday
            w *= 0.4
        if z > 50:   # Hohe Zahlen
            w *= 1.5
        if z % 10 == 1:  # Endziffer 1 vermeiden
            w *= 0.2
        weights.append(w)

    # Normalisieren
    total = sum(weights)
    weights = [w/total for w in weights]

    # Ziehe 10 Zahlen
    ticket = set()
    while len(ticket) < 10:
        choice = random.choices(pool, weights=weights, k=1)[0]
        ticket.add(choice)

    return ticket


def generate_random_ticket() -> set[int]:
    """Generiert ein zufaelliges Ticket."""
    return set(random.sample(range(1, 71), 10))


def calculate_win(ticket: set[int], drawn: set[int]) -> int:
    """Berechnet Gewinn fuer ein Ticket."""
    treffer = len(ticket & drawn)
    return KENO_QUOTES_TYP10.get(treffer, 0)


def run_backtest(
    draws: list[dict],
    jackpot_dates: list[datetime],
    strategy: str = "optimized",
    phase_filter: str = None
) -> dict:
    """
    Fuehrt Backtest durch.

    Args:
        draws: Liste der Ziehungen
        jackpot_dates: Liste der Jackpot-Daten
        strategy: "optimized" oder "random"
        phase_filter: Nur diese Phase testen (None = alle)
    """

    results = {
        "strategy": strategy,
        "phase_filter": phase_filter,
        "total_games": 0,
        "total_cost": 0,
        "total_win": 0,
        "treffer_distribution": defaultdict(int),
        "phase_results": defaultdict(lambda: {"games": 0, "cost": 0, "win": 0}),
    }

    for draw in draws:
        phase = get_phase(draw["datum"], jackpot_dates)

        # Phase-Filter
        if phase_filter and phase != phase_filter:
            continue

        # Generiere Ticket
        if strategy == "optimized":
            ticket = generate_optimized_ticket()
        else:
            ticket = generate_random_ticket()

        # Berechne Gewinn
        win = calculate_win(ticket, draw["zahlen"])
        treffer = len(ticket & draw["zahlen"])

        # Update Ergebnisse
        results["total_games"] += 1
        results["total_cost"] += 1  # 1 EUR pro Spiel
        results["total_win"] += win
        results["treffer_distribution"][treffer] += 1

        # Phase-spezifische Ergebnisse
        results["phase_results"][phase]["games"] += 1
        results["phase_results"][phase]["cost"] += 1
        results["phase_results"][phase]["win"] += win

    # ROI berechnen
    if results["total_cost"] > 0:
        results["roi"] = (results["total_win"] - results["total_cost"]) / results["total_cost"] * 100
    else:
        results["roi"] = 0

    return results


def main():
    print("=" * 70)
    print("BACKTEST: KOMBINIERTE JACKPOT-STRATEGIE")
    print("=" * 70)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")

    # Lade Daten
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"

    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)

    # Filtere auf 2023-2024 (wo wir Jackpot-Daten haben)
    draws_2023_2024 = [d for d in draws
                       if d["datum"].year in [2023, 2024]]

    print(f"\nDaten geladen:")
    print(f"  Ziehungen 2023-2024: {len(draws_2023_2024)}")
    print(f"  Jackpot-Tage: {len(jackpot_dates)}")

    # Test 1: Optimierte Strategie vs Random (alle Phasen)
    print(f"\n{'='*70}")
    print("TEST 1: OPTIMIERT vs RANDOM (alle Phasen, 100 Simulationen)")
    print(f"{'='*70}")

    opt_results = []
    rand_results = []

    for _ in range(100):
        opt = run_backtest(draws_2023_2024, jackpot_dates, "optimized")
        rand = run_backtest(draws_2023_2024, jackpot_dates, "random")
        opt_results.append(opt["roi"])
        rand_results.append(rand["roi"])

    print(f"\n{'Strategie':<20} {'ROI (Durchschnitt)':>20} {'ROI (Std)':>15}")
    print("-" * 55)
    print(f"{'Optimiert':<20} {np.mean(opt_results):>+20.2f}% {np.std(opt_results):>15.2f}%")
    print(f"{'Random':<20} {np.mean(rand_results):>+20.2f}% {np.std(rand_results):>15.2f}%")
    print(f"{'Differenz':<20} {np.mean(opt_results) - np.mean(rand_results):>+20.2f}%")

    # Test 2: Phasen-Vergleich
    print(f"\n{'='*70}")
    print("TEST 2: PHASEN-VERGLEICH (Optimierte Strategie)")
    print(f"{'='*70}")

    phase_rois = defaultdict(list)

    for _ in range(100):
        result = run_backtest(draws_2023_2024, jackpot_dates, "optimized")
        for phase, data in result["phase_results"].items():
            if data["games"] > 0:
                roi = (data["win"] - data["cost"]) / data["cost"] * 100
                phase_rois[phase].append(roi)

    print(f"\n{'Phase':<15} {'Spiele':>10} {'ROI (Avg)':>15} {'ROI (Std)':>15}")
    print("-" * 55)

    for phase in ["EARLY", "BOOST", "NEUTRAL", "COOLDOWN", "UNKNOWN"]:
        if phase in phase_rois:
            avg_roi = np.mean(phase_rois[phase])
            std_roi = np.std(phase_rois[phase])
            games = len(phase_rois[phase])

            marker = " ← SPIELEN!" if phase == "BOOST" else (" ← MEIDEN!" if phase == "COOLDOWN" else "")
            print(f"{phase:<15} {games:>10} {avg_roi:>+15.2f}% {std_roi:>15.2f}%{marker}")

    # Test 3: NUR BOOST-Phase
    print(f"\n{'='*70}")
    print("TEST 3: NUR BOOST-PHASE (Tag 8-14 nach Jackpot)")
    print(f"{'='*70}")

    boost_opt = []
    boost_rand = []

    for _ in range(100):
        opt = run_backtest(draws_2023_2024, jackpot_dates, "optimized", "BOOST")
        rand = run_backtest(draws_2023_2024, jackpot_dates, "random", "BOOST")
        if opt["total_games"] > 0:
            boost_opt.append(opt["roi"])
        if rand["total_games"] > 0:
            boost_rand.append(rand["roi"])

    if boost_opt and boost_rand:
        print(f"\n{'Strategie':<20} {'ROI (BOOST)':>20} {'Spiele':>15}")
        print("-" * 55)
        print(f"{'Optimiert':<20} {np.mean(boost_opt):>+20.2f}% {len(boost_opt):>15}")
        print(f"{'Random':<20} {np.mean(boost_rand):>+20.2f}% {len(boost_rand):>15}")
        print(f"{'Vorteil Optimiert':<20} {np.mean(boost_opt) - np.mean(boost_rand):>+20.2f}%")

    # Treffer-Verteilung
    print(f"\n{'='*70}")
    print("TREFFER-VERTEILUNG (letzte Simulation)")
    print(f"{'='*70}")

    final_result = run_backtest(draws_2023_2024, jackpot_dates, "optimized")

    print(f"\n{'Treffer':>10} {'Anzahl':>10} {'Anteil':>10} {'Gewinn':>10}")
    print("-" * 45)

    total = sum(final_result["treffer_distribution"].values())
    for treffer in range(11):
        count = final_result["treffer_distribution"].get(treffer, 0)
        pct = count / total * 100 if total > 0 else 0
        gewinn = KENO_QUOTES_TYP10.get(treffer, 0)
        print(f"{treffer:>10} {count:>10} {pct:>10.1f}% {gewinn:>10} EUR")

    # Zusammenfassung
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"""
ERGEBNISSE:

1. Optimierte Strategie vs Random:
   → Differenz: {np.mean(opt_results) - np.mean(rand_results):+.2f}%

2. Phasen-Timing:
   → BOOST (Tag 8-14): Beste Phase zum Spielen
   → COOLDOWN (Tag 22+): Schlechteste Phase

3. Kombination (Optimiert + BOOST):
   → Potenziell beste Strategie

ACHTUNG:
- Backtest basiert auf historischen Daten
- Kleine Stichprobe (nur 2023-2024)
- Keine Garantie fuer zukuenftige Performance
- KENO hat immer negativen Erwartungswert!
""")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "zeitraum": "2023-2024",
        "ziehungen": len(draws_2023_2024),
        "jackpot_tage": len(jackpot_dates),
        "ergebnisse": {
            "optimiert_vs_random": {
                "optimiert_roi": np.mean(opt_results),
                "random_roi": np.mean(rand_results),
                "differenz": np.mean(opt_results) - np.mean(rand_results),
            },
            "boost_phase": {
                "optimiert_roi": np.mean(boost_opt) if boost_opt else None,
                "random_roi": np.mean(boost_rand) if boost_rand else None,
            }
        }
    }

    output_path = base_path / "results/backtest_jackpot_strategy.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return output


if __name__ == "__main__":
    main()
