"""
Analyse: Sind die "anderen 10" (Nicht-Gewinner) populaerer als die "Gewinner 10"?

HYPOTHESE (korrigiert):
Das KENO-System waehlt die 20 Zahlen fuer optimale Auszahlungs-Balance:
  - NICHT-GEWINNER 10 = POPULAERE Zahlen (Birthday 1-31, haeufige Muster)
    → Viele kleine Gewinne, haelt Spieler bei der Stange
  - GEWINNER 10 = SELTENE/SPEZIFISCHE Zahlen
    → Minimiert Jackpot-Auszahlungen, sichert House Edge

POPULARITAETS-PROXIES (da wir keine echten Spielerdaten haben):
1. Birthday-Zahlen (1-31) - werden ueberproportional gespielt
2. "Glueckszahlen" (7, 3, 9, 13)
3. Runde Zahlen (10, 20, 30, 40, 50, 60, 70)
4. Niedrige Zahlen generell (Spieler bevorzugen kleine Zahlen)
"""

from collections import Counter
import json
import random
import numpy as np
from pathlib import Path
from scipy import stats


# Popularitaets-Gewichte basierend auf Spielerverhalten
# (Proxy, da echte Daten nicht verfuegbar)
def get_popularity_score(zahl: int) -> float:
    """
    Berechnet einen Popularitaets-Score fuer eine Zahl (0-1).

    Basiert auf bekannten Spieler-Praeferenzen:
    - Birthday-Zahlen (1-31) werden haeufiger gespielt
    - Glueckszahlen (7, 3, 9) sind beliebt
    - Niedrige Zahlen werden bevorzugt
    - Runde Zahlen (10, 20, 30...) sind beliebt
    """
    score = 0.0

    # 1. Birthday-Zahlen (1-31): +0.4
    if 1 <= zahl <= 31:
        score += 0.4

    # 2. Sehr niedrige Zahlen (1-12 Monate): +0.2
    if 1 <= zahl <= 12:
        score += 0.2

    # 3. Glueckszahlen: +0.3
    if zahl in [7, 3, 9, 13, 21]:
        score += 0.3

    # 4. Runde Zahlen (Zehner): +0.15
    if zahl % 10 == 0:
        score += 0.15

    # 5. Generelle Praeferenz fuer niedrige Zahlen
    # Linear abnehmend von 1 (0.3) bis 70 (0.0)
    score += 0.3 * (70 - zahl) / 69

    # 6. "Unbeliebte" Zahlen: hohe Zahlen ohne Muster
    if zahl >= 60 and zahl not in [60, 66, 69, 70]:
        score -= 0.1

    return max(0.0, min(1.0, score))


def analyze_popularity_split(name: str, gewinner_10: list[int], other_10: list[int]) -> dict:
    """
    Analysiert ob die Nicht-Gewinner-Zahlen populaerer sind als die Gewinner-Zahlen.
    """
    print(f"\n{'='*70}")
    print(f"POPULARITAETS-ANALYSE: {name}")
    print(f"{'='*70}")

    # Berechne Popularitaets-Scores
    gewinner_scores = [get_popularity_score(z) for z in gewinner_10]
    other_scores = [get_popularity_score(z) for z in other_10]

    avg_gewinner = np.mean(gewinner_scores)
    avg_other = np.mean(other_scores)

    print(f"\n--- GEWINNER 10 (sollten WENIGER populaer sein) ---")
    print(f"Zahlen: {sorted(gewinner_10)}")
    print(f"Popularity-Scores:")
    for z in sorted(gewinner_10):
        score = get_popularity_score(z)
        bar = "█" * int(score * 20)
        birthday = "← Birthday" if z <= 31 else ""
        print(f"  {z:>2}: {score:.2f} {bar} {birthday}")
    print(f"Durchschnitt: {avg_gewinner:.3f}")

    print(f"\n--- ANDERE 10 (sollten MEHR populaer sein) ---")
    print(f"Zahlen: {sorted(other_10)}")
    print(f"Popularity-Scores:")
    for z in sorted(other_10):
        score = get_popularity_score(z)
        bar = "█" * int(score * 20)
        birthday = "← Birthday" if z <= 31 else ""
        print(f"  {z:>2}: {score:.2f} {bar} {birthday}")
    print(f"Durchschnitt: {avg_other:.3f}")

    # Vergleich
    print(f"\n--- VERGLEICH ---")
    diff = avg_other - avg_gewinner
    diff_pct = diff / max(avg_gewinner, 0.01) * 100

    print(f"Andere 10 Durchschnitt:  {avg_other:.3f}")
    print(f"Gewinner 10 Durchschnitt: {avg_gewinner:.3f}")
    print(f"Differenz: {diff:+.3f} ({diff_pct:+.1f}%)")

    # Statistische Signifikanz (t-Test)
    t_stat, p_value = stats.ttest_ind(other_scores, gewinner_scores)
    print(f"\nT-Test (einseitig: andere > gewinner):")
    print(f"  t-Statistik: {t_stat:.3f}")
    print(f"  p-Wert (einseitig): {p_value/2:.4f}")

    # Spezifische Metriken
    print(f"\n--- DETAILMETRIKEN ---")

    # Birthday-Zahlen
    birthday_gewinner = sum(1 for z in gewinner_10 if z <= 31)
    birthday_other = sum(1 for z in other_10 if z <= 31)
    print(f"Birthday-Zahlen (1-31):")
    print(f"  In Gewinner 10: {birthday_gewinner}/10")
    print(f"  In Andere 10:   {birthday_other}/10")

    # Niedrige Zahlen (1-35)
    low_gewinner = sum(1 for z in gewinner_10 if z <= 35)
    low_other = sum(1 for z in other_10 if z <= 35)
    print(f"Niedrige Zahlen (1-35):")
    print(f"  In Gewinner 10: {low_gewinner}/10")
    print(f"  In Andere 10:   {low_other}/10")

    # Hohe Zahlen (51-70)
    high_gewinner = sum(1 for z in gewinner_10 if z >= 51)
    high_other = sum(1 for z in other_10 if z >= 51)
    print(f"Hohe Zahlen (51-70):")
    print(f"  In Gewinner 10: {high_gewinner}/10")
    print(f"  In Andere 10:   {high_other}/10")

    # Interpretation
    print(f"\n--- INTERPRETATION ---")
    if diff > 0.05 and p_value/2 < 0.1:
        hypothesis_result = "CONFIRMED"
        print(f"  ✓ HYPOTHESE BESTAETIGT!")
        print(f"    Die 'Anderen 10' sind signifikant populaerer.")
        print(f"    → System waehlt populaere Zahlen als Nicht-Gewinner")
        print(f"    → Viele Spieler haben Teiltreffer (kleine Gewinne)")
    elif diff < -0.05:
        hypothesis_result = "REJECTED"
        print(f"  ✗ HYPOTHESE WIDERLEGT!")
        print(f"    Die 'Gewinner 10' sind populaerer als die 'Anderen 10'.")
        print(f"    → Das widerspricht der Auszahlungs-Optimierung")
    else:
        hypothesis_result = "INCONCLUSIVE"
        print(f"  ~ UNENTSCHIEDEN")
        print(f"    Kein klarer Unterschied in der Popularitaet.")

    return {
        "name": name,
        "gewinner_10": sorted(gewinner_10),
        "other_10": sorted(other_10),
        "gewinner_avg_popularity": round(avg_gewinner, 4),
        "other_avg_popularity": round(avg_other, 4),
        "popularity_diff": round(diff, 4),
        "t_statistic": round(t_stat, 4),
        "p_value_onesided": round(p_value/2, 4),
        "birthday_in_gewinner": birthday_gewinner,
        "birthday_in_other": birthday_other,
        "hypothesis_result": hypothesis_result,
    }


def run_null_model(gewinner_10: list[int], n_simulations: int = 1000) -> dict:
    """
    Nullmodell: Wie waere die Verteilung bei zufaelliger Aufteilung?
    """
    random.seed(42)
    diffs = []

    all_numbers = list(range(1, 71))

    for _ in range(n_simulations):
        # Zufaellige 20 Zahlen (die den Gewinner enthalten)
        other_candidates = [n for n in all_numbers if n not in gewinner_10]
        random_other_10 = random.sample(other_candidates, 10)

        gewinner_scores = [get_popularity_score(z) for z in gewinner_10]
        other_scores = [get_popularity_score(z) for z in random_other_10]

        diff = np.mean(other_scores) - np.mean(gewinner_scores)
        diffs.append(diff)

    return {
        "mean_diff": np.mean(diffs),
        "std_diff": np.std(diffs),
        "diffs": diffs,
    }


def main():
    """Teste die Popularitaets-Split Hypothese."""

    print("=" * 70)
    print("POPULARITAETS-SPLIT ANALYSE")
    print("Hypothese: Nicht-Gewinner-Zahlen sind populaerer als Gewinner-Zahlen")
    print("=" * 70)

    # Zeige Popularitaets-Verteilung
    print(f"\n--- POPULARITAETS-SKALA (Referenz) ---")
    print("Beispiel-Scores fuer verschiedene Zahlen:")
    examples = [1, 7, 12, 20, 31, 35, 50, 55, 63, 70]
    for z in examples:
        score = get_popularity_score(z)
        bar = "█" * int(score * 20)
        print(f"  {z:>2}: {score:.2f} {bar}")

    # Die 3 bekannten Jackpot-Faelle
    jackpots = [
        {
            "name": "Kyritz",
            "gewinner": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
            "other_10": [1, 7, 14, 23, 31, 39, 52, 58, 63, 70],
        },
        {
            "name": "Oberbayern",
            "gewinner": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
            "other_10": [2, 8, 11, 24, 32, 41, 49, 57, 62, 70],
        },
        {
            "name": "Nordsachsen",
            "gewinner": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
            "other_10": [3, 11, 22, 28, 35, 51, 54, 62, 66, 70],
        },
    ]

    all_results = []

    for jp in jackpots:
        result = analyze_popularity_split(jp["name"], jp["gewinner"], jp["other_10"])

        # Nullmodell fuer diesen Gewinner
        print(f"\n--- NULLMODELL (1000 zufaellige Aufteilungen) ---")
        null = run_null_model(jp["gewinner"], n_simulations=1000)

        z_score = (result["popularity_diff"] - null["mean_diff"]) / max(null["std_diff"], 0.001)
        percentile = sum(1 for d in null["diffs"] if d < result["popularity_diff"]) / len(null["diffs"]) * 100

        print(f"Nullmodell Durchschnitt: {null['mean_diff']:.4f} ± {null['std_diff']:.4f}")
        print(f"Echter Wert:             {result['popularity_diff']:.4f}")
        print(f"Z-Score:                 {z_score:+.2f}")
        print(f"Percentile:              {percentile:.1f}%")

        result["null_model"] = {
            "mean": round(null["mean_diff"], 4),
            "std": round(null["std_diff"], 4),
            "z_score": round(z_score, 3),
            "percentile": round(percentile, 1),
        }

        all_results.append(result)

    # Gesamtzusammenfassung
    print(f"\n{'='*70}")
    print("GESAMTZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"\n{'Jackpot':<15} {'Gew.Pop':>10} {'And.Pop':>10} {'Diff':>10} {'Z-Score':>10} {'Ergebnis':>12}")
    print("-" * 70)

    total_diff = 0
    confirmed = 0

    for r in all_results:
        result_symbol = "✓" if r["hypothesis_result"] == "CONFIRMED" else ("✗" if r["hypothesis_result"] == "REJECTED" else "~")
        print(f"{r['name']:<15} {r['gewinner_avg_popularity']:>10.3f} {r['other_avg_popularity']:>10.3f} {r['popularity_diff']:>+10.3f} {r['null_model']['z_score']:>+10.2f} {result_symbol:>12}")
        total_diff += r["popularity_diff"]
        if r["hypothesis_result"] == "CONFIRMED":
            confirmed += 1

    avg_diff = total_diff / len(all_results)

    print(f"\n--- AGGREGIERTE ANALYSE ---")
    print(f"Durchschnittliche Differenz: {avg_diff:+.4f}")

    # Birthday-Zahlen Aggregat
    total_birthday_gewinner = sum(r["birthday_in_gewinner"] for r in all_results)
    total_birthday_other = sum(r["birthday_in_other"] for r in all_results)

    print(f"\nBirthday-Zahlen (1-31) ueber alle 3 Jackpots:")
    print(f"  In Gewinner 10: {total_birthday_gewinner}/30 ({total_birthday_gewinner/30*100:.1f}%)")
    print(f"  In Andere 10:   {total_birthday_other}/30 ({total_birthday_other/30*100:.1f}%)")

    # Chi-Quadrat Test fuer Birthday-Verteilung
    # Erwartung: 31/70 = 44.3% Birthday-Zahlen bei Zufall
    expected_birthday = 30 * 31 / 70

    print(f"\n  Erwartet bei Zufall: {expected_birthday:.1f}/30 ({31/70*100:.1f}%)")

    # Interpretation
    print(f"\n{'='*70}")
    print("FAZIT")
    print(f"{'='*70}")

    if avg_diff > 0.02:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE TENDENZIELL BESTAETIGT                                         ║
║                                                                           ║
║  Die 'Anderen 10' (Nicht-Gewinner) sind durchschnittlich POPULAERER      ║
║  als die 'Gewinner 10'.                                                   ║
║                                                                           ║
║  Das unterstuetzt die Theorie:                                            ║
║  → System waehlt populaere Zahlen als "Koeder" (viele Teiltreffer)       ║
║  → Gewinner-Kombination ist spezifisch/selten (minimiert Jackpots)       ║
║                                                                           ║
║  Differenz: {avg_diff:+.4f} (Andere populaerer)                                  ║
║  Birthday in Andere: {total_birthday_other}/30 vs Gewinner: {total_birthday_gewinner}/30                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    elif avg_diff < -0.02:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE WIDERLEGT                                                      ║
║                                                                           ║
║  Die 'Gewinner 10' sind durchschnittlich POPULAERER als die              ║
║  'Anderen 10' - das Gegenteil der Erwartung!                             ║
║                                                                           ║
║  Moegliche Erklaerungen:                                                  ║
║  → Gewinner spielen bewusst populaere Zahlen (Birthday-Strategie)        ║
║  → Die Stichprobe ist zu klein (nur 3 Jackpots)                          ║
║  → Unsere Popularitaets-Proxies sind ungenau                             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ERGEBNIS UNENTSCHIEDEN                                                   ║
║                                                                           ║
║  Kein klarer Unterschied in der Popularitaet zwischen                    ║
║  Gewinner-Zahlen und Nicht-Gewinner-Zahlen.                              ║
║                                                                           ║
║  Naechste Schritte:                                                       ║
║  → Mehr Jackpot-Faelle analysieren                                       ║
║  → Echte Spielerdaten (Dauerscheine) einbeziehen                         ║
║  → Andere Popularitaets-Metriken testen                                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Speichern
    output = {
        "hypothese": "Nicht-Gewinner-Zahlen sind populaerer (Birthday, niedrig) als Gewinner-Zahlen",
        "methode": "Popularitaets-Score basierend auf Birthday/Glueckszahlen-Proxies",
        "ergebnisse": all_results,
        "aggregiert": {
            "avg_popularity_diff": round(avg_diff, 4),
            "birthday_in_gewinner_total": total_birthday_gewinner,
            "birthday_in_other_total": total_birthday_other,
            "confirmed_count": confirmed,
        }
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/popularity_split_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return output


if __name__ == "__main__":
    main()
