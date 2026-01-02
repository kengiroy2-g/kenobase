"""
Post-Jackpot Momentum Strategie mit kombinierten Timing-Regeln.

TIMING-REGELN (KOMBINIERT):
- Tag 24-28 des Monats (2.02x)
- Mittwoch (1.46x)
- Juni (2.28x)
- 8-14 Tage nach Jackpot

ZAHLEN-STRATEGIE:
- Momentum-Zahlen: Index >= 2 am Jackpot-Tag
- Mix mit Top-Frequenz-Zahlen

TEST: Typ 6 und Typ 7
"""

import csv
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import random

# KENO Quoten
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 60, 7: 5000},
    10: {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000}
}


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
                        "zahlen_list": numbers
                    })
            except:
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
        except:
            pass
    for event in data.get("pending_from_quotes_2023", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except:
            pass
    return sorted(dates)


def parse_number_index(filepath: Path) -> dict:
    """Parst die number_index Datei fuer Index-Werte."""
    data = {}
    current_date = None
    current_entry = {}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        date_match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+\(", line)
        if date_match:
            if current_date and current_entry:
                data[current_date] = current_entry
            current_date = date_match.group(1)
            current_entry = {"zahlen": [], "index": []}
            continue

        if line.startswith("Zahlen:") and current_date:
            parts = line.replace("Zahlen:", "").split()
            current_entry["zahlen"] = [int(x) for x in parts if x.isdigit()]
            continue

        if line.startswith("Index:") and current_date:
            parts = line.replace("Index:", "").split()
            current_entry["index"] = [int(x) for x in parts if x.lstrip("-").isdigit()]

    if current_date and current_entry:
        data[current_date] = current_entry

    return data


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
    """Prueft welche Timing-Regeln erfuellt sind."""
    day_of_month = datum.day
    weekday = datum.weekday()  # 0=Mo, 1=Di, 2=Mi, ...
    month = datum.month
    days_since_jp = get_days_since_jackpot(datum, jackpot_dates)

    rules = {
        "tag_24_28": 24 <= day_of_month <= 28,
        "mittwoch": weekday == 2,
        "juni": month == 6,
        "boost_phase": 8 <= days_since_jp <= 14,
        "days_since_jp": days_since_jp
    }

    # Kombinierte Regeln
    rules["tag_24_28_AND_boost"] = rules["tag_24_28"] and rules["boost_phase"]
    rules["mittwoch_AND_boost"] = rules["mittwoch"] and rules["boost_phase"]
    rules["any_combo"] = rules["tag_24_28_AND_boost"] or rules["mittwoch_AND_boost"]

    return rules


def get_momentum_numbers(index_data: dict, jp_date_str: str) -> list[int]:
    """Holt Momentum-Zahlen (Index >= 2) vom Jackpot-Tag."""
    if jp_date_str not in index_data:
        return []

    entry = index_data[jp_date_str]
    zahlen = entry.get("zahlen", [])
    indices = entry.get("index", [])

    momentum = []
    for i, z in enumerate(zahlen):
        if i < len(indices) and indices[i] >= 2:
            momentum.append(z)

    return momentum


def generate_momentum_ticket(momentum_numbers: list[int], typ: int) -> set[int]:
    """Generiert Ticket mit Momentum-Zahlen."""
    ticket = set()

    # Zuerst Momentum-Zahlen (max 60% des Tickets)
    max_momentum = int(typ * 0.6)
    if momentum_numbers:
        selected = random.sample(momentum_numbers, min(len(momentum_numbers), max_momentum))
        ticket.update(selected)

    # Rest mit zufaelligen Zahlen auffuellen
    pool = [z for z in range(1, 71) if z not in ticket]
    while len(ticket) < typ:
        ticket.add(random.choice(pool))
        pool = [z for z in range(1, 71) if z not in ticket]

    return ticket


def generate_random_ticket(typ: int) -> set[int]:
    """Generiert zufaelliges Ticket."""
    return set(random.sample(range(1, 71), typ))


def generate_anti_momentum_ticket(typ: int, momentum_numbers: set[int]) -> set[int]:
    """
    Generiert Ticket das Momentum-Zahlen AKTIV vermeidet.

    Das ist der Kern der Strategie:
    - Andere Spieler waehlen "heisse" Zahlen
    - Wir vermeiden sie explizit
    """
    # Auch populaere Birthday-Zahlen vermeiden
    birthday_popular = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}
    avoid = momentum_numbers | birthday_popular

    # Pool ohne zu vermeidende Zahlen
    pool = [z for z in range(1, 71) if z not in avoid]

    if len(pool) < typ:
        pool = [z for z in range(1, 71) if z not in momentum_numbers]

    return set(random.sample(pool, min(typ, len(pool))))


def calculate_win(ticket: set[int], drawn: set[int], typ: int) -> int:
    """Berechnet Gewinn."""
    treffer = len(ticket & drawn)
    return KENO_QUOTES[typ].get(treffer, 0)


def get_recent_momentum(draws: list[dict], current_idx: int, lookback: int = 3) -> set[int]:
    """Holt Momentum-Zahlen basierend auf den letzten X Ziehungen."""
    if current_idx < lookback:
        return set()

    number_counts = defaultdict(int)
    for i in range(current_idx - lookback, current_idx):
        for n in draws[i]["zahlen"]:
            number_counts[n] += 1

    # Zahlen die 2+ mal erschienen = Momentum
    return {n for n, c in number_counts.items() if c >= 2}


def run_backtest(
    draws: list[dict],
    jackpot_dates: list[datetime],
    index_data: dict,
    typ: int,
    strategy: str,  # "random", "momentum", "anti_momentum"
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
        "treffer_dist": defaultdict(int)
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
            elif timing_filter == "tag_24_28_AND_boost":
                play = rules["tag_24_28_AND_boost"]
            elif timing_filter == "mittwoch_AND_boost":
                play = rules["mittwoch_AND_boost"]
            elif timing_filter == "any_combo":
                play = rules["any_combo"]

            if not play:
                continue

            # Momentum-Zahlen aus letzten 3 Ziehungen
            momentum_numbers = get_recent_momentum(draws, idx, lookback=3)

            # Ticket generieren basierend auf Strategie
            if strategy == "momentum" and momentum_numbers:
                ticket = generate_momentum_ticket(list(momentum_numbers), typ)
            elif strategy == "anti_momentum":
                ticket = generate_anti_momentum_ticket(typ, momentum_numbers)
            else:  # random
                ticket = generate_random_ticket(typ)

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

    return results


def main():
    print("=" * 80)
    print("POST-JACKPOT MOMENTUM STRATEGIE - BACKTEST")
    print("=" * 80)

    N_SIMULATIONS = 1000  # Mehr Simulationen fuer Stabilitaet

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"
    index_path = base_path / "results/number_index_2022_2025.txt"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)
    index_data = parse_number_index(index_path)

    # Filter auf 2023-2024 (wo wir Jackpot-Daten haben)
    draws_test = [d for d in draws if d["datum"].year in [2023, 2024]]

    print(f"Ziehungen: {len(draws_test)}")
    print(f"Jackpot-Tage: {len(jackpot_dates)}")
    print(f"Index-Tage: {len(index_data)}")

    # Zaehle Spieltage pro Filter
    filter_counts = defaultdict(int)
    for draw in draws_test:
        rules = check_timing_rules(draw["datum"], jackpot_dates)
        if rules["boost_phase"]:
            filter_counts["boost_only"] += 1
        if rules["tag_24_28_AND_boost"]:
            filter_counts["tag_24_28_AND_boost"] += 1
        if rules["mittwoch_AND_boost"]:
            filter_counts["mittwoch_AND_boost"] += 1
        if rules["any_combo"]:
            filter_counts["any_combo"] += 1

    print(f"\n--- Spieltage pro Filter (von {len(draws_test)} total) ---")
    for f, c in sorted(filter_counts.items()):
        pct = c / len(draws_test) * 100
        print(f"  {f}: {c} Tage ({pct:.1f}%)")

    # === BACKTEST ===
    print(f"\n{'='*80}")
    print(f"BACKTEST ERGEBNISSE ({N_SIMULATIONS} Simulationen)")
    print(f"{'='*80}")

    results_all = []

    for typ in [6, 7]:
        print(f"\n--- TYP {typ} ---")
        print(f"{'Filter':<25} {'Strategie':<15} {'Spiele':>8} {'ROI':>10} {'Gewinn':>12}")
        print("-" * 75)

        for timing_filter in ["none", "boost_only", "tag_24_28_AND_boost", "any_combo"]:
            for strategy in ["random", "momentum", "anti_momentum"]:
                result = run_backtest(
                    draws_test, jackpot_dates, index_data,
                    typ=typ,
                    strategy=strategy,
                    timing_filter=timing_filter,
                    n_simulations=N_SIMULATIONS
                )

                games_per_sim = result["games"] // N_SIMULATIONS

                marker = ""
                if result["roi"] > 0:
                    marker = " ★★★ POSITIV!"
                elif result["roi"] > -30:
                    marker = " ★★"

                print(f"{timing_filter:<25} {strategy:<15} {games_per_sim:>8} "
                      f"{result['roi']:>+10.1f}% {result['win']:>12,}{marker}")

                results_all.append(result)

    # Beste Ergebnisse
    print(f"\n{'='*80}")
    print("BESTE STRATEGIEN")
    print(f"{'='*80}")

    positive = [r for r in results_all if r["roi"] > 0]
    if positive:
        print("\nPositive ROI Strategien:")
        for r in sorted(positive, key=lambda x: -x["roi"])[:10]:
            print(f"  Typ {r['typ']}, {r['timing_filter']}, {r['strategy']}: ROI {r['roi']:+.1f}%")
    else:
        print("\nKeine positiven ROI Strategien gefunden.")
        print("Beste Strategien (geringster Verlust):")
        for r in sorted(results_all, key=lambda x: -x["roi"])[:5]:
            print(f"  Typ {r['typ']}, {r['timing_filter']}, {r['strategy']}: ROI {r['roi']:+.1f}%")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "zeitraum": "2023-2024",
        "filter_counts": dict(filter_counts),
        "results": [
            {
                "typ": r["typ"],
                "timing_filter": r["timing_filter"],
                "strategy": r["strategy"],
                "games": r["games"],
                "roi": r["roi"]
            }
            for r in results_all
        ]
    }

    output_path = base_path / "results/backtest_postjp_momentum.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
