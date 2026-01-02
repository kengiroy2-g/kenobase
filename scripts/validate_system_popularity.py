"""
Validiere: Enthalten Jackpot-Gewinner mehr "System-unbeliebte" Zahlen?

System-Beliebtheit = Durchschnittliche Gewinner-Anzahl wenn diese Zahl gezogen wird
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np


def load_system_popularity():
    """Lade die berechnete System-Beliebtheit pro Zahl."""
    path = Path("results/system_reality_analysis.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["number_winner_correlation"]


def load_jackpot_events():
    """Lade Jackpot-Events."""
    path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["events"]


def analyze_jackpot_popularity(events, popularity):
    """
    Analysiere die System-Beliebtheit der Jackpot-Gewinner Zahlen
    vs. die nicht-gewaehlten Zahlen.
    """
    print("="*70)
    print("SYSTEM-BELIEBTHEIT DER JACKPOT-GEWINNER")
    print("="*70)

    # Global statistics
    all_pop = [popularity[str(n)]["mean_winners"] for n in range(1, 71)]
    global_mean = np.mean(all_pop)
    global_std = np.std(all_pop)

    print(f"\nGlobale Statistik:")
    print(f"  Durchschnitt ueber alle Zahlen: {global_mean:.1f} Gewinner/Tag")
    print(f"  Standardabweichung: {global_std:.1f}")
    print(f"  Min (unbeliebteste): {min(all_pop):.1f}")
    print(f"  Max (beliebteste): {max(all_pop):.1f}")

    results = []

    for event in events:
        print(f"\n{'='*70}")
        print(f"{event['id']} ({event['date']})")
        print("="*70)

        winner_10 = event["winner_10"]
        not_chosen_10 = event["not_chosen_10"]
        drawn_20 = event["drawn_20"]

        # Berechne durchschnittliche System-Beliebtheit
        winner_pop = [popularity[str(n)]["mean_winners"] for n in winner_10]
        not_chosen_pop = [popularity[str(n)]["mean_winners"] for n in not_chosen_10]
        drawn_pop = [popularity[str(n)]["mean_winners"] for n in drawn_20]

        winner_mean = np.mean(winner_pop)
        not_chosen_mean = np.mean(not_chosen_pop)
        drawn_mean = np.mean(drawn_pop)

        print(f"\nGewinner-10 System-Beliebtheit:")
        for n in sorted(winner_10):
            pop = popularity[str(n)]["mean_winners"]
            z_score = (pop - global_mean) / global_std
            marker = "UNBELIEBT" if z_score < -0.5 else ("BELIEBT" if z_score > 0.5 else "")
            print(f"  Zahl {n:2}: {pop:.0f} Gewinner/Tag (z={z_score:+.2f}) {marker}")

        print(f"\n  MITTELWERT Gewinner: {winner_mean:.1f}")
        print(f"  vs. Global-Durchschnitt: {winner_mean - global_mean:+.1f}")

        print(f"\nNicht-Gewaehlte-10 System-Beliebtheit:")
        for n in sorted(not_chosen_10):
            pop = popularity[str(n)]["mean_winners"]
            z_score = (pop - global_mean) / global_std
            marker = "UNBELIEBT" if z_score < -0.5 else ("BELIEBT" if z_score > 0.5 else "")
            print(f"  Zahl {n:2}: {pop:.0f} Gewinner/Tag (z={z_score:+.2f}) {marker}")

        print(f"\n  MITTELWERT Nicht-Gewaehlt: {not_chosen_mean:.1f}")
        print(f"  vs. Global-Durchschnitt: {not_chosen_mean - global_mean:+.1f}")

        print(f"\nVERGLEICH:")
        delta = winner_mean - not_chosen_mean
        print(f"  Gewinner - Nicht-Gewaehlt = {delta:+.1f}")

        if delta < 0:
            print(f"  → GEWINNER sind UNBELIEBTER (= weniger Dauerscheine)")
        else:
            print(f"  → GEWINNER sind BELIEBTER (= mehr Dauerscheine)")

        results.append({
            "id": event["id"],
            "winner_mean_pop": winner_mean,
            "not_chosen_mean_pop": not_chosen_mean,
            "delta": delta,
            "winner_has_lower_pop": delta < 0
        })

    # Konsistenz-Check
    print("\n" + "="*70)
    print("KONSISTENZ-ANALYSE")
    print("="*70)

    all_lower = all(r["winner_has_lower_pop"] for r in results)
    deltas = [r["delta"] for r in results]

    print(f"\nGewinner haben niedrigere Beliebtheit in {sum(r['winner_has_lower_pop'] for r in results)}/3 Faellen")
    print(f"Durchschnittliches Delta: {np.mean(deltas):+.1f}")

    if all_lower:
        print("\n✓ KONSISTENT: Gewinner haben IMMER niedrigere System-Beliebtheit!")
        print("  → Das System waehlt Kombinationen mit weniger Dauerscheinen")
    else:
        print("\n✗ NICHT KONSISTENT: Muster ist gemischt")

    return results


def main():
    print("Lade Daten...")
    popularity = load_system_popularity()
    events = load_jackpot_events()

    print(f"Anzahl Jackpot-Events: {len(events)}")

    results = analyze_jackpot_popularity(events, popularity)

    # Speichere
    output = {
        "hypothesis": "Jackpot-Gewinner enthalten Zahlen mit niedrigerer System-Beliebtheit",
        "results": results,
        "consistent": all(r["winner_has_lower_pop"] for r in results)
    }

    output_path = Path("results/system_popularity_jackpot_validation.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
