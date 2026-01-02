"""
Analyse der "Nah-dran-Illusion" bei Jackpot-Ziehungen.

HYPOTHESE:
Die 20 Jackpot-Zahlen werden so gewaehlt, dass:
1. Maximale "Nah-dran-Verteilung" (viele Spieler mit 5-7/10 Treffern)
2. Minimale echte Gewinner (genau 1 bei 10/10)

TEST:
- Vergleiche echte Jackpot-Ziehungen mit zufaelligen 20er-Sets
- Echte Ziehung sollte MEHR "5-7 Treffer" Kombinationen erzeugen
- Echte Ziehung sollte WENIGER "9-10 Treffer" Kombinationen haben

Das wuerde beweisen, dass die Ziehung auf "Illusions-Maximierung" optimiert ist.
"""

from itertools import combinations
from collections import Counter
import json
import random
import numpy as np
from pathlib import Path


def count_overlap_distribution(jackpot_20: list[int], gewinner_10: list[int]) -> dict[int, int]:
    """
    Zaehlt fuer alle C(20,10) Kombinationen, wie viele Treffer sie mit dem Gewinner haben.

    Returns:
        Dict mit {anzahl_treffer: anzahl_kombinationen}
    """
    gewinner_set = set(gewinner_10)
    overlap_counts = Counter()

    for combo in combinations(sorted(jackpot_20), 10):
        overlap = len(set(combo).intersection(gewinner_set))
        overlap_counts[overlap] += 1

    return dict(overlap_counts)


def generate_random_jackpot(gewinner_10: list[int], all_numbers: range = range(1, 71)) -> list[int]:
    """
    Generiert ein zufaelliges 20er-Set das den Gewinner enthaelt.

    Args:
        gewinner_10: Die 10 Gewinner-Zahlen (muessen enthalten sein)
        all_numbers: Alle moeglichen Zahlen (1-70)

    Returns:
        20 Zahlen (10 Gewinner + 10 zufaellige andere)
    """
    other_numbers = [n for n in all_numbers if n not in gewinner_10]
    random_10 = random.sample(other_numbers, 10)
    return sorted(gewinner_10 + random_10)


def calculate_illusion_score(distribution: dict[int, int]) -> dict:
    """
    Berechnet den "Illusions-Score" einer Verteilung.

    Hoher Score = Viele "fast Gewinner" (5-7), wenige "echte Gewinner" (9-10)
    """
    total = sum(distribution.values())

    # "Nah-dran" Zone: 5-7 Treffer
    near_miss = sum(distribution.get(i, 0) for i in [5, 6, 7])
    near_miss_pct = near_miss / total * 100

    # "Sehr nah" Zone: 8-9 Treffer
    very_close = sum(distribution.get(i, 0) for i in [8, 9])
    very_close_pct = very_close / total * 100

    # "Gewinner" Zone: 10 Treffer
    winners = distribution.get(10, 0)
    winners_pct = winners / total * 100

    # Illusion Score: Maximiere near_miss, minimiere winners
    # Score = (near_miss%) / (very_close% + 1) * (1 / (winners + 1))
    illusion_score = (near_miss_pct / (very_close_pct + 1)) * (100 / (winners + 1))

    return {
        "near_miss_5_7": near_miss,
        "near_miss_5_7_pct": round(near_miss_pct, 2),
        "very_close_8_9": very_close,
        "very_close_8_9_pct": round(very_close_pct, 2),
        "winners_10": winners,
        "winners_10_pct": round(winners_pct, 4),
        "illusion_score": round(illusion_score, 2),
    }


def analyze_single_jackpot(name: str, jackpot_20: list[int], gewinner_10: list[int],
                           n_random_simulations: int = 100) -> dict:
    """
    Analysiert einen einzelnen Jackpot-Fall und vergleicht mit Zufalls-Nullmodell.
    """
    print(f"\n{'='*70}")
    print(f"ANALYSE: {name}")
    print(f"{'='*70}")
    print(f"Jackpot-Zahlen (20): {sorted(jackpot_20)}")
    print(f"Gewinner (10):       {sorted(gewinner_10)}")

    # 1. Echte Verteilung
    print(f"\n--- ECHTE ZIEHUNG ---")
    real_dist = count_overlap_distribution(jackpot_20, gewinner_10)
    real_scores = calculate_illusion_score(real_dist)

    print(f"\nTreffer-Verteilung (von {sum(real_dist.values()):,} Kombinationen):")
    print(f"{'Treffer':>8} {'Anzahl':>10} {'Prozent':>10}")
    print("-" * 30)
    for treffer in sorted(real_dist.keys(), reverse=True):
        count = real_dist[treffer]
        pct = count / sum(real_dist.values()) * 100
        marker = " ← NEAR MISS" if treffer in [5, 6, 7] else (" ← GEWINNER" if treffer == 10 else "")
        print(f"{treffer:>8} {count:>10,} {pct:>9.2f}%{marker}")

    print(f"\nIllusions-Metriken:")
    print(f"  Near-Miss (5-7 Treffer): {real_scores['near_miss_5_7']:,} ({real_scores['near_miss_5_7_pct']:.1f}%)")
    print(f"  Sehr nah (8-9 Treffer):  {real_scores['very_close_8_9']:,} ({real_scores['very_close_8_9_pct']:.1f}%)")
    print(f"  Gewinner (10 Treffer):   {real_scores['winners_10']:,}")
    print(f"  ILLUSION-SCORE:          {real_scores['illusion_score']:.2f}")

    # 2. Zufalls-Nullmodell
    print(f"\n--- ZUFALLS-NULLMODELL ({n_random_simulations} Simulationen) ---")

    random_scores = []
    random_near_miss = []
    random_very_close = []
    random_illusion = []

    random.seed(42)  # Reproduzierbarkeit

    for i in range(n_random_simulations):
        # Generiere zufaelliges 20er-Set mit dem gleichen Gewinner
        random_20 = generate_random_jackpot(gewinner_10)
        random_dist = count_overlap_distribution(random_20, gewinner_10)
        scores = calculate_illusion_score(random_dist)

        random_scores.append(scores)
        random_near_miss.append(scores['near_miss_5_7_pct'])
        random_very_close.append(scores['very_close_8_9_pct'])
        random_illusion.append(scores['illusion_score'])

    # Statistiken
    avg_near_miss = np.mean(random_near_miss)
    std_near_miss = np.std(random_near_miss)
    avg_very_close = np.mean(random_very_close)
    std_very_close = np.std(random_very_close)
    avg_illusion = np.mean(random_illusion)
    std_illusion = np.std(random_illusion)

    print(f"\nNullmodell-Statistiken:")
    print(f"  Near-Miss (5-7):  {avg_near_miss:.1f}% ± {std_near_miss:.1f}%")
    print(f"  Sehr nah (8-9):   {avg_very_close:.1f}% ± {std_very_close:.1f}%")
    print(f"  Illusion-Score:   {avg_illusion:.2f} ± {std_illusion:.2f}")

    # 3. Vergleich: Z-Scores
    print(f"\n--- VERGLEICH: ECHT vs ZUFALL ---")

    z_near_miss = (real_scores['near_miss_5_7_pct'] - avg_near_miss) / max(std_near_miss, 0.01)
    z_very_close = (real_scores['very_close_8_9_pct'] - avg_very_close) / max(std_very_close, 0.01)
    z_illusion = (real_scores['illusion_score'] - avg_illusion) / max(std_illusion, 0.01)

    # Percentile
    pct_near_miss = sum(1 for x in random_near_miss if x < real_scores['near_miss_5_7_pct']) / len(random_near_miss) * 100
    pct_illusion = sum(1 for x in random_illusion if x < real_scores['illusion_score']) / len(random_illusion) * 100

    print(f"\n{'Metrik':<20} {'Echt':>10} {'Zufall':>12} {'Z-Score':>10} {'Percentile':>12}")
    print("-" * 66)
    print(f"{'Near-Miss (5-7)':<20} {real_scores['near_miss_5_7_pct']:>9.1f}% {avg_near_miss:>10.1f}% {z_near_miss:>+10.2f} {pct_near_miss:>11.0f}%")
    print(f"{'Sehr nah (8-9)':<20} {real_scores['very_close_8_9_pct']:>9.1f}% {avg_very_close:>10.1f}% {z_very_close:>+10.2f}")
    print(f"{'Illusion-Score':<20} {real_scores['illusion_score']:>10.2f} {avg_illusion:>11.2f} {z_illusion:>+10.2f} {pct_illusion:>11.0f}%")

    # Interpretation
    print(f"\n--- INTERPRETATION ---")
    if z_illusion > 1.0:
        print(f"  ✓ HYPOTHESE BESTAETIGT: Illusion-Score ist {z_illusion:.1f}σ UEBER Zufall!")
        print(f"    → Die echte Ziehung erzeugt MEHR 'Nah-dran-Gefuehl' als zufaellig.")
    elif z_illusion < -1.0:
        print(f"  ✗ HYPOTHESE WIDERLEGT: Illusion-Score ist {abs(z_illusion):.1f}σ UNTER Zufall!")
        print(f"    → Die echte Ziehung ist WENIGER 'illusionsoptimiert' als zufaellig.")
    else:
        print(f"  ~ UNENTSCHIEDEN: Illusion-Score liegt im Zufallsbereich (|z| < 1).")
        print(f"    → Keine signifikante Abweichung vom Zufall erkennbar.")

    return {
        "name": name,
        "jackpot_zahlen": sorted(jackpot_20),
        "gewinner": sorted(gewinner_10),
        "real_distribution": real_dist,
        "real_scores": real_scores,
        "nullmodel": {
            "n_simulations": n_random_simulations,
            "avg_near_miss_pct": round(avg_near_miss, 2),
            "std_near_miss_pct": round(std_near_miss, 2),
            "avg_illusion_score": round(avg_illusion, 2),
            "std_illusion_score": round(std_illusion, 2),
        },
        "comparison": {
            "z_near_miss": round(z_near_miss, 3),
            "z_illusion": round(z_illusion, 3),
            "percentile_near_miss": round(pct_near_miss, 1),
            "percentile_illusion": round(pct_illusion, 1),
        },
        "hypothesis_result": "CONFIRMED" if z_illusion > 1.0 else ("REJECTED" if z_illusion < -1.0 else "INCONCLUSIVE"),
    }


def main():
    """Teste die Nah-dran-Illusion Hypothese mit bekannten Jackpot-Daten."""

    print("=" * 70)
    print("NAH-DRAN-ILLUSION ANALYSE")
    print("Hypothese: Jackpot-Ziehungen maximieren 'Fast gewonnen!'-Gefuehl")
    print("=" * 70)

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
        jackpot_20 = jp["gewinner"] + jp["other_10"]
        result = analyze_single_jackpot(
            jp["name"],
            jackpot_20,
            jp["gewinner"],
            n_random_simulations=500  # Mehr Simulationen fuer bessere Statistik
        )
        all_results.append(result)

    # Gesamtzusammenfassung
    print(f"\n{'='*70}")
    print("GESAMTZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"\n{'Jackpot':<15} {'Illusion-Score':>15} {'Z-Score':>10} {'Percentile':>12} {'Ergebnis':>15}")
    print("-" * 70)

    confirmed = 0
    rejected = 0
    inconclusive = 0

    for r in all_results:
        result_symbol = "✓" if r["hypothesis_result"] == "CONFIRMED" else ("✗" if r["hypothesis_result"] == "REJECTED" else "~")
        print(f"{r['name']:<15} {r['real_scores']['illusion_score']:>15.2f} {r['comparison']['z_illusion']:>+10.2f} {r['comparison']['percentile_illusion']:>11.0f}% {result_symbol:>15}")

        if r["hypothesis_result"] == "CONFIRMED":
            confirmed += 1
        elif r["hypothesis_result"] == "REJECTED":
            rejected += 1
        else:
            inconclusive += 1

    print(f"\n{'='*70}")
    print("FAZIT")
    print(f"{'='*70}")
    print(f"\n  Bestaetigt:    {confirmed}/3 Jackpots")
    print(f"  Widerlegt:     {rejected}/3 Jackpots")
    print(f"  Unentschieden: {inconclusive}/3 Jackpots")

    if confirmed >= 2:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE BESTAETIGT!                                                    ║
║                                                                           ║
║  Die echten Jackpot-Ziehungen erzeugen MEHR "Nah-dran-Gefuehl"           ║
║  als zufaellige Ziehungen. Das System ist auf ILLUSIONS-MAXIMIERUNG      ║
║  optimiert:                                                               ║
║                                                                           ║
║  → Viele Spieler mit 5-7 Treffern denken "Ich war so nah dran!"          ║
║  → Das haelt sie bei der Stange (Axiom A3: Attraktivitaet)               ║
║  → Gleichzeitig gibt es nur 1 echten 10/10 Gewinner (House Edge)         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    elif rejected >= 2:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE WIDERLEGT!                                                     ║
║                                                                           ║
║  Die echten Jackpot-Ziehungen zeigen KEINE erhoehte Illusions-           ║
║  Optimierung gegenueber zufaelligen Ziehungen.                           ║
║                                                                           ║
║  Moegliche Erklaerungen:                                                  ║
║  → Die 20 Zahlen werden tatsaechlich zufaellig gezogen                   ║
║  → Die Illusions-Metrik ist nicht sensitiv genug                         ║
║  → Die Stichprobe (3 Jackpots) ist zu klein                              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ERGEBNIS UNENTSCHIEDEN                                                   ║
║                                                                           ║
║  Die Daten zeigen keine klare Tendenz. Moegliche Gruende:                ║
║  → Zu wenige Jackpot-Faelle (nur 3)                                      ║
║  → Die Illusions-Optimierung ist subtiler als erwartet                   ║
║  → Weitere Constraints/Metriken noetig                                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Speichern
    output = {
        "hypothese": "Jackpot-Ziehungen maximieren Nah-dran-Illusion",
        "methode": "Vergleich mit 500 zufaelligen 20er-Sets pro Jackpot",
        "ergebnisse": all_results,
        "zusammenfassung": {
            "bestaetigt": confirmed,
            "widerlegt": rejected,
            "unentschieden": inconclusive,
        }
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/near_miss_illusion_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return output


if __name__ == "__main__":
    main()
