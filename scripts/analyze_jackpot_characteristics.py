"""
KENO Jackpot Charakteristik-Analyse

Ziel: Verstehen welche Charakteristiken das KENO-System bei der
Zahlenauswahl an Jackpot-Auszahltagen bevorzugt/vermeidet.

Kernhypothese: Das System wählt "unbeliebte" Kombinationen um
House-Edge zu wahren und Gewinner auf 1-10 zu begrenzen.
"""

import json
from pathlib import Path
from typing import NamedTuple

# Konfiguration
LUCKY_NUMBERS = {7, 3, 9, 11, 19}  # Beliebte Glückszahlen
BIRTHDAY_RANGE = range(1, 32)      # 1-31 (Tage im Monat)
HIGH_RANGE = range(50, 71)         # 50-70 (unbeliebt)


class Sample(NamedTuple):
    """Ein Jackpot-Sample mit Gewinner und Nicht-Gewinner Zahlen."""
    id: str
    date: str
    winner_10: list[int]
    not_chosen_10: list[int]
    total_winners: int


def load_samples() -> list[Sample]:
    """Lade alle Jackpot-Samples aus jackpot_events.json."""
    path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    samples = []
    for event in data["events"]:
        total_winners = event.get("quoten_data", {}).get("total_winners_typ10", 1)
        samples.append(Sample(
            id=event["id"],
            date=event["date"],
            winner_10=event["winner_10"],
            not_chosen_10=event["not_chosen_10"],
            total_winners=total_winners,
        ))
    return samples


def calculate_characteristics(numbers: list[int]) -> dict:
    """
    Berechne alle Charakteristiken für eine 10er-Kombination.

    Kategorien:
    - Beliebtheit: birthday_count, lucky_count, high_count
    - Strukturell: even_count, consecutive_pairs, decades_used
    - Numerisch: sum, mean
    """
    nums = sorted(numbers)

    # Beliebtheit
    birthday_count = sum(1 for n in nums if n in BIRTHDAY_RANGE)
    lucky_count = sum(1 for n in nums if n in LUCKY_NUMBERS)
    high_count = sum(1 for n in nums if n in HIGH_RANGE)

    # Strukturell
    even_count = sum(1 for n in nums if n % 2 == 0)
    odd_count = 10 - even_count

    # Konsekutive Paare (Abstand = 1)
    gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    consecutive_pairs = sum(1 for g in gaps if g == 1)

    # Dekaden-Verteilung
    decades = {}
    for n in nums:
        decade = ((n - 1) // 10) + 1  # 1-10=1, 11-20=2, ..., 61-70=7
        decades[decade] = decades.get(decade, 0) + 1
    decades_used = len(decades)
    max_per_decade = max(decades.values())

    # Numerisch
    total_sum = sum(nums)
    mean = total_sum / 10

    return {
        # Beliebtheit (höher = beliebter bei Spielern)
        "birthday_count": birthday_count,
        "birthday_pct": birthday_count / 10 * 100,
        "lucky_count": lucky_count,
        "high_count": high_count,  # höher = UNbeliebter

        # Strukturell
        "even_count": even_count,
        "odd_count": odd_count,
        "consecutive_pairs": consecutive_pairs,
        "decades_used": decades_used,
        "max_per_decade": max_per_decade,

        # Numerisch
        "sum": total_sum,
        "mean": mean,
    }


def analyze_sample(sample: Sample) -> dict:
    """Analysiere einen Sample: Gewinner vs. Nicht-Gewinner."""
    winner_chars = calculate_characteristics(sample.winner_10)
    not_chosen_chars = calculate_characteristics(sample.not_chosen_10)

    # Delta berechnen (Gewinner - Nicht-Gewinner)
    deltas = {}
    for key in winner_chars:
        deltas[key] = winner_chars[key] - not_chosen_chars[key]

    return {
        "id": sample.id,
        "date": sample.date,
        "total_winners": sample.total_winners,
        "winner": winner_chars,
        "not_chosen": not_chosen_chars,
        "delta": deltas,
    }


def check_consistency(analyses: list[dict]) -> dict:
    """
    Prüfe welche Charakteristiken bei ALLEN Samples konsistent sind.

    Konsistent = alle Deltas haben gleiches Vorzeichen (alle > 0 oder alle < 0)
    """
    if not analyses:
        return {}

    keys = list(analyses[0]["delta"].keys())
    consistency = {}

    for key in keys:
        deltas = [a["delta"][key] for a in analyses]

        # Alle positiv?
        all_positive = all(d > 0 for d in deltas)
        # Alle negativ?
        all_negative = all(d < 0 for d in deltas)
        # Alle null?
        all_zero = all(d == 0 for d in deltas)

        if all_positive:
            consistency[key] = {
                "consistent": True,
                "direction": "GEWINNER_HÖHER",
                "deltas": deltas,
                "interpretation": f"Gewinner haben MEHR {key}",
            }
        elif all_negative:
            consistency[key] = {
                "consistent": True,
                "direction": "GEWINNER_NIEDRIGER",
                "deltas": deltas,
                "interpretation": f"Gewinner haben WENIGER {key}",
            }
        elif all_zero:
            consistency[key] = {
                "consistent": True,
                "direction": "GLEICH",
                "deltas": deltas,
                "interpretation": f"{key} ist identisch",
            }
        else:
            consistency[key] = {
                "consistent": False,
                "direction": "MIXED",
                "deltas": deltas,
                "interpretation": f"{key} ist NICHT konsistent",
            }

    return consistency


def print_report(samples: list[Sample], analyses: list[dict], consistency: dict):
    """Drucke den vollständigen Analysebericht."""
    print("=" * 80)
    print("KENO JACKPOT CHARAKTERISTIK-ANALYSE")
    print("=" * 80)
    print()
    print("KERNHYPOTHESE: Das System wählt 'unbeliebte' Kombinationen")
    print("               um House-Edge zu wahren.")
    print()

    # Sample-Übersicht
    print("-" * 80)
    print("SAMPLES:")
    print("-" * 80)
    for s in samples:
        print(f"  {s.id}")
        print(f"    Datum: {s.date}")
        print(f"    Gewinner: {sorted(s.winner_10)}")
        print(f"    Nicht-Gew: {sorted(s.not_chosen_10)}")
        print(f"    Anz. Gewinner: {s.total_winners}")
        print()

    # Einzelanalysen
    print("-" * 80)
    print("EINZELANALYSEN (Gewinner vs. Nicht-Gewinner):")
    print("-" * 80)

    for a in analyses:
        print(f"\n{a['id']} ({a['date']}):")
        print(f"{'Charakteristik':<25} {'Gewinner':>10} {'Nicht-Gew':>10} {'Delta':>10}")
        print("-" * 55)

        for key in a["winner"]:
            w = a["winner"][key]
            n = a["not_chosen"][key]
            d = a["delta"][key]

            # Formatierung
            if isinstance(w, float):
                w_str = f"{w:.1f}"
                n_str = f"{n:.1f}"
                d_str = f"{d:+.1f}"
            else:
                w_str = str(w)
                n_str = str(n)
                d_str = f"{d:+d}" if isinstance(d, int) else f"{d:+.1f}"

            print(f"{key:<25} {w_str:>10} {n_str:>10} {d_str:>10}")

    # Konsistenz-Matrix
    print()
    print("=" * 80)
    print("KONSISTENZ-MATRIX (alle 3 Samples):")
    print("=" * 80)
    print()
    print(f"{'Charakteristik':<25} {'Konsistent?':>12} {'Richtung':>20} {'Deltas'}")
    print("-" * 80)

    # Sortiere: Konsistente zuerst
    sorted_keys = sorted(consistency.keys(),
                        key=lambda k: (not consistency[k]["consistent"], k))

    for key in sorted_keys:
        c = consistency[key]
        cons_str = "JA" if c["consistent"] else "NEIN"
        direction = c["direction"]
        deltas = c["deltas"]

        # Formatiere Deltas
        if all(isinstance(d, int) for d in deltas):
            delta_str = str([f"{d:+d}" for d in deltas])
        else:
            delta_str = str([f"{d:+.1f}" for d in deltas])

        print(f"{key:<25} {cons_str:>12} {direction:>20} {delta_str}")

    # Zusammenfassung: Konsistente Muster
    print()
    print("=" * 80)
    print("KONSISTENTE MUSTER (Unbeliebtheits-Profil):")
    print("=" * 80)

    consistent_patterns = {k: v for k, v in consistency.items() if v["consistent"]}

    if consistent_patterns:
        print()
        for key, c in consistent_patterns.items():
            if c["direction"] != "GLEICH":
                print(f"  - {c['interpretation']}")

        # Beliebtheit-Interpretation
        print()
        print("INTERPRETATION:")

        if consistency.get("birthday_count", {}).get("direction") == "GEWINNER_NIEDRIGER":
            print("  -> Gewinner haben WENIGER Birthday-Zahlen (1-31)")
            print("     = System vermeidet beliebte Kombinationen")

        if consistency.get("high_count", {}).get("direction") == "GEWINNER_HÖHER":
            print("  -> Gewinner haben MEHR hohe Zahlen (50-70)")
            print("     = System bevorzugt unbeliebte Zahlen")

        if consistency.get("lucky_count", {}).get("direction") == "GEWINNER_NIEDRIGER":
            print("  -> Gewinner haben WENIGER Glückszahlen (3,7,9,11,19)")
            print("     = System vermeidet populäre Zahlen")

    else:
        print()
        print("  KEINE konsistenten Muster gefunden!")
        print("  Möglicherweise sind mehr Samples nötig.")

    # Nicht-konsistente Muster
    print()
    print("-" * 80)
    print("NICHT-KONSISTENTE MUSTER:")
    print("-" * 80)

    inconsistent = {k: v for k, v in consistency.items()
                    if not v["consistent"]}

    for key, c in inconsistent.items():
        print(f"  - {key}: {c['deltas']}")


def check_absolute_patterns(analyses: list[dict]) -> dict:
    """
    Prüfe ABSOLUTE Muster der Gewinner-Kombinationen.

    Nicht: Gewinner vs. Nicht-Gewinner
    Sondern: Haben ALLE Gewinner bestimmte absolute Eigenschaften?
    """
    results = {}

    # Sammle alle Gewinner-Charakteristiken
    keys = list(analyses[0]["winner"].keys())

    for key in keys:
        winner_values = [a["winner"][key] for a in analyses]
        not_chosen_values = [a["not_chosen"][key] for a in analyses]

        results[key] = {
            "winner_values": winner_values,
            "winner_min": min(winner_values),
            "winner_max": max(winner_values),
            "winner_mean": sum(winner_values) / len(winner_values),
            "not_chosen_values": not_chosen_values,
            "not_chosen_min": min(not_chosen_values),
            "not_chosen_max": max(not_chosen_values),
            "not_chosen_mean": sum(not_chosen_values) / len(not_chosen_values),
        }

    return results


def print_absolute_analysis(absolute: dict):
    """Drucke die absolute Muster-Analyse."""
    print()
    print("=" * 80)
    print("ABSOLUTE MUSTER-ANALYSE (Gewinner-Kombinationen)")
    print("=" * 80)
    print()
    print("Frage: Haben ALLE Gewinner bestimmte absolute Eigenschaften?")
    print()
    print(f"{'Charakteristik':<25} {'Gewinner':<30} {'Nicht-Gew':<30}")
    print(f"{'':<25} {'Min/Max/Mean':<30} {'Min/Max/Mean':<30}")
    print("-" * 85)

    for key, data in absolute.items():
        w_min, w_max, w_mean = data["winner_min"], data["winner_max"], data["winner_mean"]
        n_min, n_max, n_mean = data["not_chosen_min"], data["not_chosen_max"], data["not_chosen_mean"]

        if isinstance(w_mean, float):
            w_str = f"{w_min:.0f} / {w_max:.0f} / {w_mean:.1f}"
            n_str = f"{n_min:.0f} / {n_max:.0f} / {n_mean:.1f}"
        else:
            w_str = f"{w_min} / {w_max} / {w_mean:.1f}"
            n_str = f"{n_min} / {n_max} / {n_mean:.1f}"

        print(f"{key:<25} {w_str:<30} {n_str:<30}")

    # Potentielle Regeln
    print()
    print("-" * 80)
    print("POTENTIELLE ABSOLUTE REGELN:")
    print("-" * 80)

    # Birthday
    bd = absolute["birthday_pct"]
    print(f"\n1. BIRTHDAY-REGEL:")
    print(f"   Gewinner: {bd['winner_values']} -> Max: {bd['winner_max']:.0f}%")
    print(f"   Nicht-Gew: {bd['not_chosen_values']} -> Max: {bd['not_chosen_max']:.0f}%")
    if bd["winner_max"] <= 44:
        print(f"   -> MUSTER: Alle Gewinner haben <= 44% Birthday-Zahlen!")

    # High count
    hc = absolute["high_count"]
    print(f"\n2. HOHE-ZAHLEN-REGEL:")
    print(f"   Gewinner: {hc['winner_values']} -> Min: {hc['winner_min']}")
    print(f"   Nicht-Gew: {hc['not_chosen_values']} -> Min: {hc['not_chosen_min']}")
    if hc["winner_min"] >= 1:
        print(f"   -> MUSTER: Alle Gewinner haben mindestens {hc['winner_min']} hohe Zahlen (50-70)")

    # Sum
    sm = absolute["sum"]
    print(f"\n3. SUMMEN-REGEL:")
    print(f"   Gewinner: {sm['winner_values']} -> Range: {sm['winner_min']}-{sm['winner_max']}")
    print(f"   Nicht-Gew: {sm['not_chosen_values']} -> Range: {sm['not_chosen_min']}-{sm['not_chosen_max']}")


def main():
    """Hauptfunktion."""
    # Samples laden
    samples = load_samples()
    print(f"Geladene Samples: {len(samples)}")

    # Einzelanalysen
    analyses = [analyze_sample(s) for s in samples]

    # Konsistenz prüfen (relativ)
    consistency = check_consistency(analyses)

    # Absolute Muster prüfen
    absolute = check_absolute_patterns(analyses)

    # Bericht ausgeben
    print_report(samples, analyses, consistency)

    # Absolute Analyse
    print_absolute_analysis(absolute)

    # Pool-Analyse: Wie viel Birthday im 20er-Pool?
    print()
    print("=" * 80)
    print("POOL-ANALYSE: Birthday im 20er-Pool vs. Gewinner-Auswahl")
    print("=" * 80)

    for s, a in zip(samples, analyses):
        # Lade drawn_20 aus jackpot_events.json
        path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for event in data["events"]:
            if event["id"] == s.id:
                drawn_20 = event["drawn_20"]
                break

        pool_birthday = sum(1 for n in drawn_20 if n in BIRTHDAY_RANGE)
        pool_birthday_pct = pool_birthday / 20 * 100

        winner_birthday = a["winner"]["birthday_count"]
        winner_birthday_pct = a["winner"]["birthday_pct"]

        # Erwartung: Wenn zufällig aus Pool gewählt
        expected_winner_birthday = pool_birthday / 2  # 10 von 20

        print(f"\n{s.id}:")
        print(f"  20er-Pool Birthday: {pool_birthday}/20 = {pool_birthday_pct:.0f}%")
        print(f"  Erwartete Gewinner-Birthday (zufällig): {expected_winner_birthday:.1f}/10")
        print(f"  Tatsächliche Gewinner-Birthday: {winner_birthday}/10 = {winner_birthday_pct:.0f}%")

        if winner_birthday < expected_winner_birthday:
            print(f"  -> System hat WENIGER Birthday gewählt als erwartet!")
            print(f"     Delta: {winner_birthday - expected_winner_birthday:.1f}")
        elif winner_birthday > expected_winner_birthday:
            print(f"  -> System hat MEHR Birthday gewählt als erwartet!")
            print(f"     Delta: +{winner_birthday - expected_winner_birthday:.1f}")
        else:
            print(f"  -> Wie erwartet (zufällig)")

    # Ergebnisse speichern
    output = {
        "samples": [
            {
                "id": s.id,
                "date": s.date,
                "winner_10": s.winner_10,
                "not_chosen_10": s.not_chosen_10,
                "total_winners": s.total_winners,
            }
            for s in samples
        ],
        "analyses": analyses,
        "consistency": consistency,
    }

    output_path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/results/characteristics_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
