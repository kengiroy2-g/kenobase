"""
Backtest: Anti-Momentum + Invariant-Constraints Strategie.

INVARIANTEN (aus Deep-Analyse von 3 Jackpot-Gewinnern):
- INV-01: Ziffernprodukt mod 9 = 0
- INV-02: Genau 1 einstellige Zahl (1-9)
- INV-03: 6 von 7 Dekaden besetzt
- INV-05: Alle 3 Drittel (1-23, 24-46, 47-70) besetzt

STRATEGIE:
- Anti-Momentum: Vermeide "heisse" Zahlen (Streak >= 2)
- Anti-Birthday: Vermeide populaere Birthday-Zahlen
- Timing: Boost-Phase (8-14 Tage nach Jackpot) + Tag 24-28/Mittwoch

TEST: Vergleich mit/ohne Invariant-Constraints
"""

import csv
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

# KENO Quoten
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 60, 7: 5000},
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 4, 6: 20, 7: 400, 8: 10000},
    9: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 10, 7: 50, 8: 1000, 9: 50000},
    10: {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000}
}

# Birthday-Zahlen die Spieler oft waehlen
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
                        "datum_str": datum_str,
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
    for event in data.get("pending_from_quotes_2023", []):
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
        else:
            break
    if last_jp is None:
        return 999
    return (datum - last_jp).days


def check_timing_rules(datum: datetime, jackpot_dates: list[datetime]) -> dict:
    """Prueft Timing-Regeln."""
    day_of_month = datum.day
    weekday = datum.weekday()
    days_since_jp = get_days_since_jackpot(datum, jackpot_dates)

    rules = {
        "tag_24_28": 24 <= day_of_month <= 28,
        "mittwoch": weekday == 2,
        "boost_phase": 8 <= days_since_jp <= 14,
        "days_since_jp": days_since_jp
    }
    rules["any_combo"] = (rules["tag_24_28"] or rules["mittwoch"]) and rules["boost_phase"]
    return rules


def get_recent_momentum(draws: list[dict], current_idx: int, lookback: int = 3) -> set[int]:
    """Holt Momentum-Zahlen basierend auf letzten X Ziehungen."""
    if current_idx < lookback:
        return set()

    number_counts = defaultdict(int)
    for i in range(current_idx - lookback, current_idx):
        for n in draws[i]["zahlen"]:
            number_counts[n] += 1

    return {n for n, c in number_counts.items() if c >= 2}


# === INVARIANT VALIDATION ===

def digit_product_mod9(numbers: list[int]) -> int:
    """Berechnet Ziffernprodukt mod 9."""
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
    decades = set(n // 10 for n in numbers)
    return len(decades)


def covers_all_thirds(numbers: list[int]) -> bool:
    """Prueft ob alle 3 Drittel abgedeckt sind."""
    has_low = any(1 <= n <= 23 for n in numbers)
    has_mid = any(24 <= n <= 46 for n in numbers)
    has_high = any(47 <= n <= 70 for n in numbers)
    return has_low and has_mid and has_high


def validate_invariants(numbers: list[int], strict: bool = True) -> tuple[bool, dict]:
    """
    Validiert ob Kombination die Invarianten erfuellt.

    Returns:
        (is_valid, details)
    """
    details = {
        "digit_product_mod9": digit_product_mod9(numbers),
        "single_digit_count": count_single_digit(numbers),
        "decades_count": count_decades(numbers),
        "covers_thirds": covers_all_thirds(numbers),
    }

    if strict:
        # Strikte Validierung: Alle Invarianten muessen erfuellt sein
        is_valid = (
            details["digit_product_mod9"] == 0 and
            details["single_digit_count"] == 1 and
            details["decades_count"] == 6 and
            details["covers_thirds"]
        )
    else:
        # Lockere Validierung: Mindestens 3 von 4 erfuellt
        score = 0
        if details["digit_product_mod9"] == 0:
            score += 1
        if details["single_digit_count"] >= 1:
            score += 1
        if details["decades_count"] >= 5:
            score += 1
        if details["covers_thirds"]:
            score += 1
        is_valid = score >= 3

    details["is_valid"] = is_valid
    return is_valid, details


# === TICKET GENERATORS ===

def generate_random_ticket(typ: int) -> set[int]:
    """Generiert zufaelliges Ticket."""
    return set(random.sample(range(1, 71), typ))


def generate_anti_momentum_ticket(typ: int, momentum_numbers: set[int]) -> set[int]:
    """
    Generiert Anti-Momentum Ticket.
    Vermeidet Momentum-Zahlen und populaere Birthday-Zahlen.
    """
    avoid = momentum_numbers | BIRTHDAY_POPULAR
    pool = [z for z in range(1, 71) if z not in avoid]

    if len(pool) < typ:
        pool = [z for z in range(1, 71) if z not in momentum_numbers]

    return set(random.sample(pool, min(typ, len(pool))))


def generate_invariant_ticket(
    typ: int,
    momentum_numbers: set[int],
    max_attempts: int = 100
) -> Optional[set[int]]:
    """
    Generiert Anti-Momentum Ticket das Invarianten erfuellt.

    Strategie:
    1. Starte mit einer einstelligen Zahl (INV-02)
    2. Fuelle aus verschiedenen Dekaden (INV-03)
    3. Stelle sicher dass alle Drittel abgedeckt (INV-05)
    4. Pruefe Ziffernprodukt mod 9 = 0 (INV-01)
    """
    avoid = momentum_numbers | BIRTHDAY_POPULAR

    for _ in range(max_attempts):
        ticket = set()

        # 1. Eine einstellige Zahl (1-9) die nicht gemieden wird
        single_digit_pool = [z for z in range(1, 10) if z not in avoid]
        if not single_digit_pool:
            single_digit_pool = list(range(1, 10))
        ticket.add(random.choice(single_digit_pool))

        # 2. Zahlen aus verschiedenen Dekaden waehlen
        # Drittel: 1-23, 24-46, 47-70

        # Low (10-23) - da 1-9 schon abgedeckt
        low_pool = [z for z in range(10, 24) if z not in avoid and z not in ticket]
        if low_pool:
            ticket.add(random.choice(low_pool))

        # Mid (24-46)
        mid_pool = [z for z in range(24, 47) if z not in avoid and z not in ticket]
        if mid_pool:
            for _ in range(min(3, typ // 3)):
                if mid_pool:
                    choice = random.choice(mid_pool)
                    ticket.add(choice)
                    mid_pool.remove(choice)

        # High (47-70)
        high_pool = [z for z in range(47, 71) if z not in avoid and z not in ticket]
        if high_pool:
            for _ in range(min(3, typ // 3)):
                if high_pool:
                    choice = random.choice(high_pool)
                    ticket.add(choice)
                    high_pool.remove(choice)

        # Auffuellen bis typ erreicht
        remaining_pool = [z for z in range(1, 71) if z not in avoid and z not in ticket]
        while len(ticket) < typ and remaining_pool:
            choice = random.choice(remaining_pool)
            ticket.add(choice)
            remaining_pool.remove(choice)

        # Fallback: Falls nicht genug Zahlen
        if len(ticket) < typ:
            fallback_pool = [z for z in range(1, 71) if z not in ticket]
            while len(ticket) < typ and fallback_pool:
                choice = random.choice(fallback_pool)
                ticket.add(choice)
                fallback_pool.remove(choice)

        # Validiere Invarianten
        is_valid, _ = validate_invariants(list(ticket), strict=False)

        if is_valid:
            return ticket

    # Fallback: Gib normales Anti-Momentum Ticket zurueck
    return generate_anti_momentum_ticket(typ, momentum_numbers)


def calculate_win(ticket: set[int], drawn: set[int], typ: int) -> int:
    """Berechnet Gewinn."""
    treffer = len(ticket & drawn)
    return KENO_QUOTES[typ].get(treffer, 0)


def run_backtest(
    draws: list[dict],
    jackpot_dates: list[datetime],
    typ: int,
    strategy: str,
    timing_filter: str,
    n_simulations: int = 100
) -> dict:
    """Fuehrt Backtest durch."""

    results = {
        "typ": typ,
        "strategy": strategy,
        "timing_filter": timing_filter,
        "games": 0,
        "cost": 0,
        "win": 0,
        "treffer_dist": defaultdict(int),
        "invariant_stats": defaultdict(int)
    }

    for _ in range(n_simulations):
        for idx, draw in enumerate(draws):
            datum = draw["datum"]

            # Timing-Regeln pruefen
            rules = check_timing_rules(datum, jackpot_dates)

            # Filter anwenden
            play = False
            if timing_filter == "none":
                play = True
            elif timing_filter == "boost_only":
                play = rules["boost_phase"]
            elif timing_filter == "any_combo":
                play = rules["any_combo"]

            if not play:
                continue

            # Momentum-Zahlen berechnen
            momentum_numbers = get_recent_momentum(draws, idx, lookback=3)

            # Ticket generieren basierend auf Strategie
            if strategy == "random":
                ticket = generate_random_ticket(typ)
            elif strategy == "anti_momentum":
                ticket = generate_anti_momentum_ticket(typ, momentum_numbers)
            elif strategy == "invariant":
                ticket = generate_invariant_ticket(typ, momentum_numbers)
            elif strategy == "invariant_strict":
                # Versuche strikt invariantes Ticket
                ticket = generate_invariant_ticket(typ, momentum_numbers, max_attempts=200)
                if ticket is None:
                    ticket = generate_anti_momentum_ticket(typ, momentum_numbers)
            else:
                ticket = generate_random_ticket(typ)

            if ticket is None:
                ticket = generate_random_ticket(typ)

            # Invariant-Stats tracken
            is_valid, details = validate_invariants(list(ticket), strict=False)
            if is_valid:
                results["invariant_stats"]["valid"] += 1
            else:
                results["invariant_stats"]["invalid"] += 1

            # Gewinn berechnen
            win = calculate_win(ticket, draw["zahlen"], typ)
            treffer = len(ticket & draw["zahlen"])

            results["games"] += 1
            results["cost"] += 1
            results["win"] += win
            results["treffer_dist"][treffer] += 1

    # ROI berechnen
    if results["cost"] > 0:
        results["roi"] = (results["win"] - results["cost"]) / results["cost"] * 100
    else:
        results["roi"] = 0

    # Invariant-Rate
    total_tickets = results["invariant_stats"]["valid"] + results["invariant_stats"]["invalid"]
    if total_tickets > 0:
        results["invariant_rate"] = results["invariant_stats"]["valid"] / total_tickets * 100
    else:
        results["invariant_rate"] = 0

    return results


def main():
    print("=" * 80)
    print("INVARIANT STRATEGIE BACKTEST")
    print("Anti-Momentum + Invariant-Constraints")
    print("=" * 80)

    N_SIMULATIONS = 500  # Fuer stabilitaet

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)

    # Filter auf 2023-2024
    draws_test = [d for d in draws if d["datum"].year in [2023, 2024]]

    print(f"Ziehungen: {len(draws_test)}")
    print(f"Jackpot-Tage: {len(jackpot_dates)}")
    print(f"Simulationen pro Strategie: {N_SIMULATIONS}")

    # === BACKTEST ===
    print(f"\n{'='*80}")
    print(f"BACKTEST ERGEBNISSE")
    print(f"{'='*80}")

    results_all = []

    # Strategien zu testen
    strategies = ["random", "anti_momentum", "invariant"]
    timing_filters = ["none", "boost_only", "any_combo"]
    types = [7, 8, 9, 10]

    print(f"\n{'Typ':<5} {'Timing':<15} {'Strategie':<18} {'Spiele':>8} {'ROI':>10} {'Inv-Rate':>10}")
    print("-" * 75)

    for typ in types:
        for timing_filter in timing_filters:
            for strategy in strategies:
                result = run_backtest(
                    draws_test, jackpot_dates,
                    typ=typ,
                    strategy=strategy,
                    timing_filter=timing_filter,
                    n_simulations=N_SIMULATIONS
                )

                games_per_sim = result["games"] // N_SIMULATIONS

                marker = ""
                if result["roi"] > 0:
                    marker = " *** POSITIV!"
                elif result["roi"] > -30:
                    marker = " **"

                print(f"{typ:<5} {timing_filter:<15} {strategy:<18} {games_per_sim:>8} "
                      f"{result['roi']:>+10.1f}% {result['invariant_rate']:>9.1f}%{marker}")

                results_all.append(result)

    # === VERGLEICH: Mit vs Ohne Invarianten ===
    print(f"\n{'='*80}")
    print("VERGLEICH: Anti-Momentum vs Anti-Momentum + Invarianten")
    print(f"{'='*80}")

    print(f"\n{'Typ':<5} {'Timing':<15} {'Anti-Mom ROI':>15} {'Invariant ROI':>15} {'Differenz':>12}")
    print("-" * 65)

    for typ in types:
        for timing_filter in timing_filters:
            # Finde die entsprechenden Ergebnisse
            am_result = next(
                (r for r in results_all
                 if r["typ"] == typ and r["timing_filter"] == timing_filter
                 and r["strategy"] == "anti_momentum"),
                None
            )
            inv_result = next(
                (r for r in results_all
                 if r["typ"] == typ and r["timing_filter"] == timing_filter
                 and r["strategy"] == "invariant"),
                None
            )

            if am_result and inv_result:
                diff = inv_result["roi"] - am_result["roi"]
                marker = " +" if diff > 0 else ""
                print(f"{typ:<5} {timing_filter:<15} {am_result['roi']:>+15.1f}% "
                      f"{inv_result['roi']:>+15.1f}% {diff:>+11.1f}%{marker}")

    # === BESTE STRATEGIEN ===
    print(f"\n{'='*80}")
    print("TOP 10 STRATEGIEN")
    print(f"{'='*80}")

    sorted_results = sorted(results_all, key=lambda x: -x["roi"])

    print(f"\n{'#':<3} {'Typ':<5} {'Timing':<15} {'Strategie':<18} {'ROI':>10} {'Inv-Rate':>10}")
    print("-" * 65)

    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:<3} {r['typ']:<5} {r['timing_filter']:<15} {r['strategy']:<18} "
              f"{r['roi']:>+10.1f}% {r['invariant_rate']:>9.1f}%")

    # === POSITIVE ROI STRATEGIEN ===
    positive = [r for r in results_all if r["roi"] > 0]

    print(f"\n{'='*80}")
    print(f"POSITIVE ROI STRATEGIEN: {len(positive)} gefunden")
    print(f"{'='*80}")

    if positive:
        for r in sorted(positive, key=lambda x: -x["roi"]):
            print(f"  Typ {r['typ']}, {r['timing_filter']}, {r['strategy']}: "
                  f"ROI {r['roi']:+.1f}% (Inv-Rate: {r['invariant_rate']:.1f}%)")
    else:
        print("  Keine positiven ROI Strategien gefunden.")

    # === ZUSAMMENFASSUNG ===
    print(f"\n{'='*80}")
    print("ZUSAMMENFASSUNG: Invariant-Strategie Effekt")
    print(f"{'='*80}")

    # Berechne durchschnittlichen Effekt
    improvements = []
    for typ in types:
        for timing_filter in timing_filters:
            am = next((r for r in results_all
                       if r["typ"] == typ and r["timing_filter"] == timing_filter
                       and r["strategy"] == "anti_momentum"), None)
            inv = next((r for r in results_all
                        if r["typ"] == typ and r["timing_filter"] == timing_filter
                        and r["strategy"] == "invariant"), None)
            if am and inv:
                improvements.append(inv["roi"] - am["roi"])

    if improvements:
        avg_improvement = sum(improvements) / len(improvements)
        positive_improvements = sum(1 for i in improvements if i > 0)

        print(f"\nDurchschnittlicher ROI-Unterschied: {avg_improvement:+.2f}%")
        print(f"Verbesserungen: {positive_improvements}/{len(improvements)} Faelle")

        if avg_improvement > 1:
            print("\n>>> FAZIT: Invariant-Constraints VERBESSERN die Strategie! <<<")
        elif avg_improvement < -1:
            print("\n>>> FAZIT: Invariant-Constraints VERSCHLECHTERN die Strategie! <<<")
        else:
            print("\n>>> FAZIT: Invariant-Constraints haben KEINEN signifikanten Effekt <<<")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "zeitraum": "2023-2024",
        "n_simulations": N_SIMULATIONS,
        "results": [
            {
                "typ": r["typ"],
                "timing_filter": r["timing_filter"],
                "strategy": r["strategy"],
                "games": r["games"],
                "roi": r["roi"],
                "invariant_rate": r["invariant_rate"]
            }
            for r in results_all
        ],
        "summary": {
            "avg_improvement": avg_improvement if improvements else 0,
            "positive_improvements": positive_improvements if improvements else 0,
            "total_comparisons": len(improvements) if improvements else 0
        }
    }

    output_path = base_path / "results/backtest_invariant_strategy.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
