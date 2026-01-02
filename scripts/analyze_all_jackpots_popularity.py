"""
Analyse ALLER bekannten Jackpot-Tage mit der Popularity-Split-Methode.

Verwendet die ECHTEN dokumentierten Jackpot-Events aus:
AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json

Ziel: Ermitteln ob die "anderen 10" (nicht vom Gewinner gewaehlt)
systematisch populaerer sind als die "Gewinner 10".
"""

import json
from collections import Counter
from pathlib import Path
import numpy as np
from scipy import stats


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


def analyze_jackpot_event(event: dict) -> dict:
    """Analysiert ein einzelnes Jackpot-Event."""

    name = event.get("city", event.get("id", "Unknown"))
    date = event.get("date", "Unknown")
    region = event.get("region", "Unknown")
    winner_10 = event["winner_10"]
    other_10 = event["not_chosen_10"]
    drawn_20 = event["drawn_20"]

    print(f"\n{'='*70}")
    print(f"JACKPOT: {name} ({region})")
    print(f"Datum: {date}")
    print(f"{'='*70}")

    # Berechne Popularitaets-Scores
    winner_scores = [get_popularity_score(z) for z in winner_10]
    other_scores = [get_popularity_score(z) for z in other_10]

    avg_winner = np.mean(winner_scores)
    avg_other = np.mean(other_scores)
    diff = avg_other - avg_winner
    diff_pct = diff / max(avg_winner, 0.01) * 100

    print(f"\n--- GEWINNER 10 ---")
    print(f"Zahlen: {sorted(winner_10)}")
    for z in sorted(winner_10):
        score = get_popularity_score(z)
        bar = "█" * int(score * 20)
        birthday = "← Birthday" if z <= 31 else ""
        print(f"  {z:>2}: {score:.2f} {bar} {birthday}")
    print(f"Durchschnitt: {avg_winner:.3f}")

    print(f"\n--- ANDERE 10 (nicht gewaehlt) ---")
    print(f"Zahlen: {sorted(other_10)}")
    for z in sorted(other_10):
        score = get_popularity_score(z)
        bar = "█" * int(score * 20)
        birthday = "← Birthday" if z <= 31 else ""
        print(f"  {z:>2}: {score:.2f} {bar} {birthday}")
    print(f"Durchschnitt: {avg_other:.3f}")

    print(f"\n--- VERGLEICH ---")
    print(f"Andere 10:   {avg_other:.3f}")
    print(f"Gewinner 10: {avg_winner:.3f}")
    print(f"Differenz:   {diff:+.3f} ({diff_pct:+.1f}%)")

    # T-Test
    t_stat, p_value = stats.ttest_ind(other_scores, winner_scores)
    print(f"T-Test p-Wert: {p_value:.4f}")

    # Birthday-Analyse
    birthday_winner = sum(1 for z in winner_10 if z <= 31)
    birthday_other = sum(1 for z in other_10 if z <= 31)

    print(f"\n--- BIRTHDAY-ZAHLEN (1-31) ---")
    print(f"In Gewinner 10: {birthday_winner}/10 ({birthday_winner*10}%)")
    print(f"In Andere 10:   {birthday_other}/10 ({birthday_other*10}%)")
    print(f"Erwartet:       4.4/10 (44.3%)")

    # Interpretation
    if diff > 0.02:
        result = "BESTAETIGT"
        symbol = "✓"
        print(f"\n  {symbol} Andere 10 sind POPULAERER als Gewinner 10")
    elif diff < -0.02:
        result = "WIDERLEGT"
        symbol = "✗"
        print(f"\n  {symbol} Gewinner 10 sind POPULAERER als Andere 10!")
    else:
        result = "NEUTRAL"
        symbol = "~"
        print(f"\n  {symbol} Kein signifikanter Unterschied")

    return {
        "id": event.get("id"),
        "name": name,
        "date": date,
        "region": region,
        "winner_10": sorted(winner_10),
        "other_10": sorted(other_10),
        "winner_avg_popularity": round(avg_winner, 4),
        "other_avg_popularity": round(avg_other, 4),
        "popularity_diff": round(diff, 4),
        "popularity_diff_pct": round(diff_pct, 2),
        "t_statistic": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "birthday_in_winner": birthday_winner,
        "birthday_in_other": birthday_other,
        "hypothesis_result": result,
    }


def main():
    """Analysiere alle dokumentierten Jackpot-Events."""

    print("=" * 70)
    print("POPULARITY-SPLIT ANALYSE ALLER JACKPOT-EVENTS")
    print("=" * 70)

    # Lade Jackpot-Events
    events_path = Path("C:/Users/kenfu/Documents/keno_base/AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")

    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = data["events"]
    print(f"\nGeladene Jackpot-Events: {len(events)}")

    # Analysiere jedes Event
    results = []
    for event in events:
        if "winner_10" in event and "not_chosen_10" in event:
            result = analyze_jackpot_event(event)
            results.append(result)

    # Zusammenfassung
    print(f"\n{'='*70}")
    print("GESAMTZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"\n{'Jackpot':<20} {'Region':<15} {'Gew.Pop':>8} {'And.Pop':>8} {'Diff':>8} {'Result':>10}")
    print("-" * 75)

    total_diff = 0
    total_birthday_winner = 0
    total_birthday_other = 0
    confirmed = 0

    for r in results:
        symbol = "✓" if r["hypothesis_result"] == "BESTAETIGT" else ("✗" if r["hypothesis_result"] == "WIDERLEGT" else "~")
        print(f"{r['name']:<20} {r['region']:<15} {r['winner_avg_popularity']:>8.3f} {r['other_avg_popularity']:>8.3f} {r['popularity_diff']:>+8.3f} {symbol:>10}")

        total_diff += r["popularity_diff"]
        total_birthday_winner += r["birthday_in_winner"]
        total_birthday_other += r["birthday_in_other"]

        if r["hypothesis_result"] == "BESTAETIGT":
            confirmed += 1

    avg_diff = total_diff / len(results)
    n_events = len(results)

    print(f"\n{'='*70}")
    print("AGGREGIERTE STATISTIK")
    print(f"{'='*70}")

    print(f"\nAnzahl analysierte Jackpots: {n_events}")
    print(f"Durchschnittliche Popularitaets-Differenz: {avg_diff:+.4f}")
    print(f"Hypothese bestaetigt: {confirmed}/{n_events}")

    print(f"\n--- BIRTHDAY-ZAHLEN GESAMT ---")
    print(f"In Gewinner 10: {total_birthday_winner}/{n_events*10} ({total_birthday_winner/(n_events*10)*100:.1f}%)")
    print(f"In Andere 10:   {total_birthday_other}/{n_events*10} ({total_birthday_other/(n_events*10)*100:.1f}%)")
    print(f"Bei Zufall erwartet: {n_events*10*31/70:.1f}/{n_events*10} (44.3%)")

    # Regionale Analyse
    print(f"\n{'='*70}")
    print("REGIONALE ANALYSE")
    print(f"{'='*70}")

    regions = {}
    for r in results:
        region = r["region"]
        if region not in regions:
            regions[region] = []
        regions[region].append(r)

    for region, region_results in regions.items():
        avg_winner_pop = np.mean([r["winner_avg_popularity"] for r in region_results])
        avg_other_pop = np.mean([r["other_avg_popularity"] for r in region_results])
        regional_diff = avg_other_pop - avg_winner_pop

        print(f"\n{region}:")
        print(f"  Anzahl Jackpots: {len(region_results)}")
        print(f"  Gewinner Popularitaet: {avg_winner_pop:.3f}")
        print(f"  Andere Popularitaet:   {avg_other_pop:.3f}")
        print(f"  Differenz: {regional_diff:+.3f}")

    # Fazit
    print(f"\n{'='*70}")
    print("FAZIT")
    print(f"{'='*70}")

    if avg_diff > 0.02 and confirmed >= n_events * 0.6:
        conclusion = "BESTAETIGT"
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE BESTAETIGT ({confirmed}/{n_events} Jackpots)                                     ║
║                                                                           ║
║  Die 'Anderen 10' (nicht vom Gewinner gewaehlt) sind systematisch        ║
║  POPULAERER als die 'Gewinner 10'.                                        ║
║                                                                           ║
║  Durchschnittliche Differenz: {avg_diff:+.4f}                                     ║
║  Birthday-Zahlen: {total_birthday_other}/{n_events*10} (Andere) vs {total_birthday_winner}/{n_events*10} (Gewinner)                  ║
║                                                                           ║
║  INTERPRETATION:                                                          ║
║  → Das System waehlt 20 Zahlen mit optimaler Auszahlungs-Balance         ║
║  → Populaere Zahlen (Birthday) landen bei den "Anderen 10"               ║
║  → Viele Spieler haben Teiltreffer → kleine Auszahlungen                 ║
║  → Gewinner-Kombination ist spezifisch → wenige Jackpots                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    elif avg_diff < -0.02:
        conclusion = "WIDERLEGT"
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  HYPOTHESE WIDERLEGT                                                      ║
║                                                                           ║
║  Die 'Gewinner 10' sind populaerer als die 'Anderen 10' - das            ║
║  Gegenteil der Erwartung!                                                 ║
║                                                                           ║
║  Moegliche Erklaerungen:                                                  ║
║  → Gewinner spielen bewusst populaere Zahlen                             ║
║  → Unsere Popularitaets-Proxies sind ungenau                             ║
║  → Mehr Daten benoetigt                                                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    else:
        conclusion = "UNENTSCHIEDEN"
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ERGEBNIS UNENTSCHIEDEN                                                   ║
║                                                                           ║
║  Kein klarer systematischer Unterschied erkennbar.                        ║
║  Mehr Jackpot-Daten benoetigt fuer signifikante Aussage.                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Speichern
    output = {
        "analyse_typ": "Popularity-Split alle Jackpots",
        "anzahl_events": n_events,
        "hypothese": "Andere 10 sind populaerer als Gewinner 10",
        "ergebnisse": results,
        "aggregiert": {
            "avg_popularity_diff": round(avg_diff, 4),
            "birthday_in_winner_total": total_birthday_winner,
            "birthday_in_other_total": total_birthday_other,
            "confirmed_count": confirmed,
        },
        "fazit": conclusion,
        "regionale_analyse": {
            region: {
                "count": len(rr),
                "avg_winner_pop": round(np.mean([r["winner_avg_popularity"] for r in rr]), 4),
                "avg_other_pop": round(np.mean([r["other_avg_popularity"] for r in rr]), 4),
            }
            for region, rr in regions.items()
        }
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/all_jackpots_popularity_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    # Hinweis auf fehlende Daten
    print(f"\n{'='*70}")
    print("NAECHSTE SCHRITTE")
    print(f"{'='*70}")
    print(f"""
Aktuell nur {n_events} Jackpot-Events mit vollstaendigen Daten verfuegbar.

Um mehr Jackpots zu finden:
1. Quoten-Daten durchsuchen (Anzahl Gewinner bei Typ 10)
2. Pressemitteilungen der 16 Landeslotterien recherchieren
3. lotto.de Archiv nach 10/10 Gewinnern durchsuchen
4. Regionale Lotto-Webseiten scrapen

Mit mehr Daten koennen wir:
- Regionale Popularitaets-Profile erstellen
- Zeitliche Muster identifizieren
- Die Hypothese statistisch absichern
""")

    return output


if __name__ == "__main__":
    main()
