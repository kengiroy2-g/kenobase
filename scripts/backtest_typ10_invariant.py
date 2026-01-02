"""
Fokussierter Backtest: Typ 10 mit Invariant-Constraints.

Die Invarianten stammen von Typ-10-Jackpot-Gewinnern, daher
testen wir hier spezifisch Typ 10 mit mehr Simulationen.

HYPOTHESE: Invarianten sollten bei Typ 10 am besten funktionieren.
"""

import csv
import json
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# KENO Quoten Typ 10
KENO_QUOTES_10 = {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000}

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}


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
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def load_jackpot_dates(events_path: Path) -> list[datetime]:
    """Laedt Jackpot-Daten."""
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    dates = []
    for event in data.get("events", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except Exception:
            pass
    return sorted(dates)


def get_days_since_jackpot(datum: datetime, jackpot_dates: list[datetime]) -> int:
    """Berechnet Tage seit letztem Jackpot."""
    last_jp = None
    for jp in jackpot_dates:
        if jp < datum:
            last_jp = jp
    return (datum - last_jp).days if last_jp else 999


def get_recent_momentum(draws: list[dict], current_idx: int, lookback: int = 3) -> set[int]:
    """Holt Momentum-Zahlen."""
    if current_idx < lookback:
        return set()
    number_counts = defaultdict(int)
    for i in range(current_idx - lookback, current_idx):
        for n in draws[i]["zahlen"]:
            number_counts[n] += 1
    return {n for n, c in number_counts.items() if c >= 2}


# === INVARIANT CHECKS ===

def digit_product_mod9(numbers: list[int]) -> int:
    """Ziffernprodukt mod 9."""
    prod = 1
    for n in numbers:
        for d in str(n):
            if d != '0':
                prod *= int(d)
    return prod % 9


def count_single_digit(numbers: list[int]) -> int:
    """Zaehlt einstellige Zahlen (1-9)."""
    return sum(1 for n in numbers if 1 <= n <= 9)


def count_decades(numbers: list[int]) -> int:
    """Zaehlt besetzte Dekaden."""
    return len(set(n // 10 for n in numbers))


def covers_all_thirds(numbers: list[int]) -> bool:
    """Prueft ob alle 3 Drittel abgedeckt."""
    return (any(1 <= n <= 23 for n in numbers) and
            any(24 <= n <= 46 for n in numbers) and
            any(47 <= n <= 70 for n in numbers))


def validate_invariants(numbers: list[int]) -> tuple[bool, int]:
    """
    Validiert Invarianten und gibt Score zurueck.

    Returns:
        (is_valid, score) - score ist 0-4
    """
    score = 0

    if digit_product_mod9(numbers) == 0:
        score += 1
    if count_single_digit(numbers) == 1:
        score += 1
    if count_decades(numbers) >= 6:
        score += 1
    if covers_all_thirds(numbers):
        score += 1

    is_valid = score >= 3  # Mindestens 3 von 4
    return is_valid, score


# === TICKET GENERATORS ===

def generate_random_ticket() -> set[int]:
    """Zufaelliges Typ-10 Ticket."""
    return set(random.sample(range(1, 71), 10))


def generate_anti_momentum_ticket(momentum_numbers: set[int]) -> set[int]:
    """Anti-Momentum Ticket."""
    avoid = momentum_numbers | BIRTHDAY_POPULAR
    pool = [z for z in range(1, 71) if z not in avoid]
    if len(pool) < 10:
        pool = [z for z in range(1, 71) if z not in momentum_numbers]
    return set(random.sample(pool, 10))


def generate_invariant_ticket(momentum_numbers: set[int], max_attempts: int = 200) -> set[int]:
    """
    Generiert Ticket das Invarianten erfuellt.

    Strategie:
    1. Waehle genau 1 einstellige Zahl (1-9)
    2. Verteile auf 6 Dekaden
    3. Decke alle 3 Drittel ab
    4. Pruefe Ziffernprodukt mod 9 = 0
    """
    avoid = momentum_numbers | BIRTHDAY_POPULAR

    for _ in range(max_attempts):
        ticket = set()

        # 1. Eine einstellige Zahl (1-9)
        single_pool = [z for z in range(1, 10) if z not in avoid]
        if not single_pool:
            single_pool = list(range(1, 10))
        ticket.add(random.choice(single_pool))

        # 2. Aus Low (10-23)
        low_pool = [z for z in range(10, 24) if z not in avoid]
        if low_pool:
            ticket.add(random.choice(low_pool))

        # 3. Aus Mid (24-46) - 3 Zahlen
        mid_pool = [z for z in range(24, 47) if z not in avoid]
        random.shuffle(mid_pool)
        for z in mid_pool[:3]:
            ticket.add(z)

        # 4. Aus High (47-70) - 3 Zahlen
        high_pool = [z for z in range(47, 71) if z not in avoid]
        random.shuffle(high_pool)
        for z in high_pool[:3]:
            ticket.add(z)

        # 5. Auffuellen bis 10
        remaining = [z for z in range(1, 71) if z not in avoid and z not in ticket]
        random.shuffle(remaining)
        while len(ticket) < 10 and remaining:
            ticket.add(remaining.pop())

        # Fallback
        if len(ticket) < 10:
            fallback = [z for z in range(1, 71) if z not in ticket]
            random.shuffle(fallback)
            while len(ticket) < 10:
                ticket.add(fallback.pop())

        # Validiere
        is_valid, score = validate_invariants(list(ticket))
        if is_valid:
            return ticket

    # Fallback: Gib Anti-Momentum zurueck
    return generate_anti_momentum_ticket(momentum_numbers)


def calculate_win(ticket: set[int], drawn: set[int]) -> int:
    """Berechnet Gewinn fuer Typ 10."""
    treffer = len(ticket & drawn)
    return KENO_QUOTES_10.get(treffer, 0)


def run_focused_backtest(draws: list[dict], jackpot_dates: list[datetime], n_sims: int = 1000):
    """Fokussierter Backtest fuer Typ 10."""

    results = {
        "random": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
        "anti_momentum": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
        "invariant": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
    }

    for sim in range(n_sims):
        if sim % 100 == 0:
            print(f"  Simulation {sim}/{n_sims}...")

        for idx, draw in enumerate(draws):
            datum = draw["datum"]
            days_since = get_days_since_jackpot(datum, jackpot_dates)

            # Nur in Boost-Phase spielen (beste Timing-Regel)
            if not (8 <= days_since <= 14):
                continue

            momentum = get_recent_momentum(draws, idx)

            # Random
            ticket_r = generate_random_ticket()
            win_r = calculate_win(ticket_r, draw["zahlen"])
            results["random"]["cost"] += 1
            results["random"]["win"] += win_r
            results["random"]["treffer"][len(ticket_r & draw["zahlen"])] += 1

            # Anti-Momentum
            ticket_am = generate_anti_momentum_ticket(momentum)
            win_am = calculate_win(ticket_am, draw["zahlen"])
            results["anti_momentum"]["cost"] += 1
            results["anti_momentum"]["win"] += win_am
            results["anti_momentum"]["treffer"][len(ticket_am & draw["zahlen"])] += 1

            # Invariant
            ticket_inv = generate_invariant_ticket(momentum)
            win_inv = calculate_win(ticket_inv, draw["zahlen"])
            results["invariant"]["cost"] += 1
            results["invariant"]["win"] += win_inv
            results["invariant"]["treffer"][len(ticket_inv & draw["zahlen"])] += 1

    return results


def main():
    print("=" * 80)
    print("TYP 10 FOKUSSIERTER INVARIANT-TEST")
    print("=" * 80)

    N_SIMS = 1000

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)

    # Filter 2023-2024
    draws_test = [d for d in draws if d["datum"].year in [2023, 2024]]

    print(f"Ziehungen: {len(draws_test)}")
    print(f"Jackpots: {len(jackpot_dates)}")
    print(f"Simulationen: {N_SIMS}")
    print(f"\nTiming: Nur Boost-Phase (Tag 8-14 nach Jackpot)")

    print("\nStarte Backtest...")
    results = run_focused_backtest(draws_test, jackpot_dates, N_SIMS)

    print("\n" + "=" * 80)
    print("ERGEBNISSE TYP 10 + BOOST PHASE")
    print("=" * 80)

    print(f"\n{'Strategie':<20} {'Spiele':>10} {'Gewinn':>12} {'ROI':>12}")
    print("-" * 56)

    for strategy, data in results.items():
        if data["cost"] > 0:
            roi = (data["win"] - data["cost"]) / data["cost"] * 100
            games = data["cost"] // N_SIMS
            print(f"{strategy:<20} {games:>10} {data['win']:>12,} {roi:>+11.2f}%")

    print("\n--- Treffer-Verteilung (pro 1000 Simulationen) ---")
    print(f"\n{'Treffer':<10} {'Random':>12} {'Anti-Mom':>12} {'Invariant':>12}")
    print("-" * 48)

    for t in range(11):
        r_count = results["random"]["treffer"].get(t, 0) // N_SIMS
        am_count = results["anti_momentum"]["treffer"].get(t, 0) // N_SIMS
        inv_count = results["invariant"]["treffer"].get(t, 0) // N_SIMS
        if r_count > 0 or am_count > 0 or inv_count > 0:
            print(f"{t:<10} {r_count:>12} {am_count:>12} {inv_count:>12}")

    # High-Win Analyse
    print("\n--- High-Win Analyse (7+ Treffer) ---")
    for strategy, data in results.items():
        high_wins = sum(data["treffer"].get(t, 0) for t in range(7, 11))
        print(f"  {strategy}: {high_wins} High-Wins in {N_SIMS} Sims = {high_wins/N_SIMS:.3f} pro Sim")

    # Vergleich
    print("\n" + "=" * 80)
    print("VERGLEICH")
    print("=" * 80)

    if results["anti_momentum"]["cost"] > 0 and results["invariant"]["cost"] > 0:
        roi_am = (results["anti_momentum"]["win"] - results["anti_momentum"]["cost"]) / results["anti_momentum"]["cost"] * 100
        roi_inv = (results["invariant"]["win"] - results["invariant"]["cost"]) / results["invariant"]["cost"] * 100
        diff = roi_inv - roi_am

        print(f"\nAnti-Momentum ROI: {roi_am:+.2f}%")
        print(f"Invariant ROI:     {roi_inv:+.2f}%")
        print(f"Differenz:         {diff:+.2f}%")

        if diff > 5:
            print("\n>>> FAZIT: Invarianten VERBESSERN Typ-10 Performance! <<<")
        elif diff < -5:
            print("\n>>> FAZIT: Invarianten VERSCHLECHTERN Typ-10 Performance! <<<")
        else:
            print("\n>>> FAZIT: Kein signifikanter Unterschied <<<")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "typ": 10,
        "timing": "boost_phase",
        "n_simulations": N_SIMS,
        "results": {
            strategy: {
                "cost": data["cost"],
                "win": data["win"],
                "roi": (data["win"] - data["cost"]) / data["cost"] * 100 if data["cost"] > 0 else 0
            }
            for strategy, data in results.items()
        }
    }

    output_path = base_path / "results/backtest_typ10_invariant.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
