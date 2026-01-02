#!/usr/bin/env python3
"""
BACKTEST: Optimierte Tickets ueber X Tage

Testet die optimierte Ticket-Strategie rueckwirkend.
"""

import csv
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

# Quoten
QUOTES_6 = {0: 0, 1: 0, 2: 0, 3: 1, 4: 7, 5: 70, 6: 5000}
QUOTES_5 = {0: 0, 1: 0, 2: 0, 3: 2, 4: 15, 5: 500}


def load_data(filepath):
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
                    data.append({"datum": datum, "zahlen": set(numbers)})
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_hot_numbers(draws, lookback=3):
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_index(draws, number):
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws, number, lookback=30):
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def build_pool(draws):
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_sorted = sorted(hot_filtered, key=lambda z: get_index(draws, z))
    hot_keep = set(hot_sorted[:5]) if len(hot_sorted) >= 5 else set(hot_sorted)

    cold_bd_sorted = sorted(cold_birthday, key=lambda z: get_count(draws, z))
    cold_bd_keep = set(cold_bd_sorted[:6])

    cold_nbd_sorted = sorted(cold_nonbd, key=lambda z: get_count(draws, z))
    cold_nbd_keep = set(cold_nbd_sorted[:6])

    return hot_keep | cold_bd_keep | cold_nbd_keep, hot


def get_decades(numbers):
    return len(set((n - 1) // 10 for n in numbers))


def get_non_birthday_ratio(numbers):
    nbd = len([n for n in numbers if n > 31])
    return nbd / len(numbers)


def has_consecutive(numbers):
    nums = sorted(numbers)
    for i in range(len(nums) - 1):
        if nums[i + 1] - nums[i] == 1:
            return True
    return False


def get_hot_count(numbers, hot_set):
    return len([n for n in numbers if n in hot_set])


def score_combo(combo):
    score = 0
    decades = get_decades(combo)
    score += min(decades, 6) * 10
    nbd_ratio = get_non_birthday_ratio(combo)
    score += (1 - abs(nbd_ratio - 0.5) * 2) * 20
    total = sum(combo)
    if 150 <= total <= 250:
        score += 15
    spread = max(combo) - min(combo)
    if spread >= 50:
        score += 15
    return score


def generate_best_ticket(draws):
    pool, hot = build_pool(draws)
    all_combos = list(combinations(sorted(pool), 6))

    # Strenge Filter
    filtered = all_combos
    filtered = [c for c in filtered if get_decades(c) >= 5]
    filtered = [c for c in filtered if 0.45 <= get_non_birthday_ratio(c) <= 0.55]
    filtered = [c for c in filtered if not has_consecutive(c)]
    filtered = [c for c in filtered if get_hot_count(c, hot) == 2]
    filtered = [c for c in filtered if 150 <= sum(c) <= 250]

    if filtered:
        ranked = sorted(filtered, key=score_combo, reverse=True)
        return set(ranked[0]), pool, hot, len(filtered)
    else:
        # Fallback
        filtered = [c for c in all_combos if get_decades(c) >= 4]
        filtered = [c for c in filtered if not has_consecutive(c)]
        if filtered:
            ranked = sorted(filtered, key=score_combo, reverse=True)
            return set(ranked[0]), pool, hot, len(filtered)
        else:
            return set(sorted(pool)[:6]), pool, hot, 1


def main():
    filepath = Path("data/raw/keno/KENO_ab_2022_bereinigt.csv")
    data = load_data(filepath)

    print("=" * 80)
    print("BACKTEST: Optimierte Tickets ueber 60 Tage")
    print("=" * 80)
    print()
    print(f"Gesamt Ziehungen: {len(data)}")
    print(f"Letzte Ziehung:   {data[-1]['datum'].strftime('%d.%m.%Y')}")
    print()

    # Gehe 60 Tage zurueck
    backtest_start_idx = len(data) - 60
    train_data = data[:backtest_start_idx]
    test_draws = data[backtest_start_idx:]

    start_date = test_draws[0]["datum"]
    end_date = test_draws[-1]["datum"]

    print(f"Backtest-Zeitraum: {start_date.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}")
    print(f"Anzahl Tage:       {len(test_draws)}")
    print()

    # Generiere Ticket
    print("=" * 80)
    print(f"TICKET-GENERIERUNG (Stand: {train_data[-1]['datum'].strftime('%d.%m.%Y')})")
    print("=" * 80)
    print()

    best_ticket, pool, hot, num_filtered = generate_best_ticket(train_data)
    typ5_ticket = set(sorted(best_ticket)[:5])

    print(f"Pool (17 Zahlen): {sorted(pool)}")
    print(f"HOT Zahlen:       {sorted(hot)}")
    print(f"Gefilterte Kombis: {num_filtered}")
    print()
    print(f">>> Ticket Typ 6: {sorted(best_ticket)}")
    print(f">>> Ticket Typ 5: {sorted(typ5_ticket)}")
    print()

    # Backtest
    print("=" * 80)
    print("BACKTEST-ERGEBNISSE")
    print("=" * 80)
    print()

    typ6_hits = []
    typ5_hits = []
    jackpot_days_6 = []
    jackpot_days_5 = []

    print(f"{'Datum':<12} {'T6':<4} {'T5':<4} {'Treffer aus Ticket'}")
    print("-" * 60)

    for draw in test_draws:
        drawn = draw["zahlen"]
        hits_6 = len(best_ticket & drawn)
        hits_5 = len(typ5_ticket & drawn)

        typ6_hits.append(hits_6)
        typ5_hits.append(hits_5)

        if hits_6 == 6:
            jackpot_days_6.append(draw["datum"])
        if hits_5 == 5:
            jackpot_days_5.append(draw["datum"])

        # Zeige Tage mit >= 3 Treffer
        if hits_6 >= 3:
            matches = sorted(best_ticket & drawn)
            print(f"{draw['datum'].strftime('%d.%m.%Y'):<12} {hits_6:<4} {hits_5:<4} {matches}")

    print()
    print("=" * 80)
    print("STATISTIK")
    print("=" * 80)
    print()

    print("TREFFER-VERTEILUNG TYP 6:")
    for h in range(7):
        count = typ6_hits.count(h)
        pct = count / len(typ6_hits) * 100
        bar = "#" * int(pct / 2)
        print(f"  {h}/6: {count:>3}x ({pct:>5.1f}%) {bar}")

    print()
    print("TREFFER-VERTEILUNG TYP 5:")
    for h in range(6):
        count = typ5_hits.count(h)
        pct = count / len(typ5_hits) * 100
        bar = "#" * int(pct / 2)
        print(f"  {h}/5: {count:>3}x ({pct:>5.1f}%) {bar}")

    print()
    avg_hits_6 = sum(typ6_hits) / len(typ6_hits)
    avg_hits_5 = sum(typ5_hits) / len(typ5_hits)
    expected_6 = 6 * 20 / 70
    expected_5 = 5 * 20 / 70

    print(f"DURCHSCHNITTLICHE TREFFER:")
    print(f"  Typ 6: {avg_hits_6:.2f} (Erwartung: {expected_6:.2f})")
    print(f"  Typ 5: {avg_hits_5:.2f} (Erwartung: {expected_5:.2f})")
    print()

    # ROI
    total_cost = len(test_draws) * 1
    total_win_6 = sum(QUOTES_6.get(h, 0) for h in typ6_hits)
    total_win_5 = sum(QUOTES_5.get(h, 0) for h in typ5_hits)
    roi_6 = (total_win_6 - total_cost) / total_cost * 100
    roi_5 = (total_win_5 - total_cost) / total_cost * 100

    print("ROI-BERECHNUNG (1 EUR/Tag):")
    print(f"  Typ 6: Einsatz {total_cost} EUR, Gewinn {total_win_6} EUR, ROI: {roi_6:+.1f}%")
    print(f"  Typ 5: Einsatz {total_cost} EUR, Gewinn {total_win_5} EUR, ROI: {roi_5:+.1f}%")
    print()

    # Jackpots
    print("=" * 80)
    print("JACKPOTS")
    print("=" * 80)
    print()

    if jackpot_days_6:
        days_to_jp = (jackpot_days_6[0] - start_date).days + 1
        print(f"  TYP 6 (6/6): {len(jackpot_days_6)}x JACKPOT!")
        for d in jackpot_days_6:
            print(f"    -> {d.strftime('%d.%m.%Y')}")
        print(f"    Erster Jackpot nach {days_to_jp} Tagen")
    else:
        max_h = max(typ6_hits)
        print(f"  TYP 6 (6/6): Kein Jackpot (max: {max_h}/6)")

    print()

    if jackpot_days_5:
        days_to_jp = (jackpot_days_5[0] - start_date).days + 1
        print(f"  TYP 5 (5/5): {len(jackpot_days_5)}x JACKPOT!")
        for d in jackpot_days_5:
            print(f"    -> {d.strftime('%d.%m.%Y')}")
        print(f"    Erster Jackpot nach {days_to_jp} Tagen")
    else:
        max_h = max(typ5_hits)
        print(f"  TYP 5 (5/5): Kein Jackpot (max: {max_h}/5)")

    print()
    print("=" * 80)
    print("FAZIT")
    print("=" * 80)
    print()

    if jackpot_days_6:
        print(f"  ERFOLG: 6/6 Jackpot erreicht!")
    elif max(typ6_hits) >= 5:
        print(f"  KNAPP: 5/6 erreicht - nur 1 Zahl fehlte!")
    else:
        print(f"  Maximale Treffer: {max(typ6_hits)}/6")

    print()


if __name__ == "__main__":
    main()
