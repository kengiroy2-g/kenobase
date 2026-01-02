#!/usr/bin/env python3
"""
INTER-JACKPOT ANALYSE: Was passiert ZWISCHEN Jackpots?

FRAGESTELLUNG:
1. Wie verteilen sich Gewinnklassen zwischen Jackpots?
2. Gibt es Signale/Muster VOR einem Jackpot?
3. Kann man den naechsten Jackpot "vorhersagen"?

HYPOTHESE (basierend auf Adversarial System):
- Nach einem Jackpot "entspannt" sich das System
- Vor dem naechsten Jackpot gibt es "Near-Miss" Ereignisse
- Das System zeigt Muster bevor es einen Jackpot "erlaubt"

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
import numpy as np
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kenobase.core.keno_quotes import get_fixed_quote


# Gewinnklassen fuer Typ 9
GK_THRESHOLDS = {
    0: "GK9_0 (Niete mit Trost)",
    1: "GK9_1 (Niete)",
    2: "GK9_2 (Niete)",
    3: "GK9_3 (Niete)",
    4: "GK9_4 (1 EUR)",
    5: "GK9_5 (2 EUR)",
    6: "GK9_6 (5 EUR)",
    7: "GK9_7 (20 EUR)",
    8: "GK9_8 (1000 EUR)",
    9: "GK9_9 (50000 EUR - JACKPOT)"
}


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots(df, base_path):
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return dates


def simulate_v21_ticket(draw_set):
    """Simuliere V2.1 Ticket gegen eine Ziehung."""
    V2_1 = [3, 7, 36, 43, 48, 51, 55, 58, 61]
    hits = len(set(V2_1) & draw_set)
    return hits


def get_inter_jackpot_periods(df, jackpot_dates):
    """Teile Daten in Perioden zwischen Jackpots auf."""
    df = df.copy()
    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)

    # Finde Jackpot-Indizes
    jackpot_indices = df[df["is_jackpot"]].index.tolist()

    periods = []

    for i in range(len(jackpot_indices)):
        jp_idx = jackpot_indices[i]
        jp_date = df.loc[jp_idx, "Datum"]

        # Naechster Jackpot (oder Ende der Daten)
        if i < len(jackpot_indices) - 1:
            next_jp_idx = jackpot_indices[i + 1]
            next_jp_date = df.loc[next_jp_idx, "Datum"]
        else:
            next_jp_idx = len(df) - 1
            next_jp_date = None

        # Ziehungen zwischen diesem und naechstem Jackpot
        period_df = df.loc[jp_idx + 1:next_jp_idx].copy()

        if len(period_df) > 0:
            periods.append({
                "start_jp_date": jp_date,
                "end_jp_date": next_jp_date,
                "draws": period_df,
                "n_draws": len(period_df),
                "has_next_jp": next_jp_date is not None
            })

    return periods


def analyze_period_progression(period_df):
    """Analysiere die Treffer-Progression innerhalb einer Periode."""
    hits_by_position = []

    for i, (_, row) in enumerate(period_df.iterrows()):
        hits = simulate_v21_ticket(row["numbers_set"])
        position_pct = (i + 1) / len(period_df) * 100  # Position in %
        hits_by_position.append({
            "position": i + 1,
            "position_pct": position_pct,
            "hits": hits,
            "date": row["Datum"]
        })

    return hits_by_position


def main():
    print("=" * 80)
    print("INTER-JACKPOT ANALYSE: Was passiert zwischen Jackpots?")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpots(df, base_path)

    # Filter auf 2025
    df_2025 = df[df["Datum"].dt.year == 2025].copy()

    print(f"\nDaten: {len(df_2025)} Ziehungen in 2025")
    print(f"Jackpots: {len([d for d in jackpot_dates if pd.to_datetime(d).year == 2025])}")

    # =========================================================================
    # 1. INTER-JACKPOT PERIODEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. INTER-JACKPOT PERIODEN (2025)")
    print("=" * 80)

    periods = get_inter_jackpot_periods(df_2025, jackpot_dates)

    print(f"\n{'Periode':>3} {'Nach JP':>12} {'Naechster JP':>12} {'Ziehungen':>10} {'Tage':>6}")
    print("-" * 50)

    for i, p in enumerate(periods):
        start = p["start_jp_date"].strftime("%d.%m.%Y")
        end = p["end_jp_date"].strftime("%d.%m.%Y") if p["end_jp_date"] else "OFFEN"
        days = (p["end_jp_date"] - p["start_jp_date"]).days if p["end_jp_date"] else "-"
        print(f"{i+1:>3} {start:>12} {end:>12} {p['n_draws']:>10} {days:>6}")

    # =========================================================================
    # 2. GEWINNKLASSEN-VERTEILUNG PRO PERIODE
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. GEWINNKLASSEN-VERTEILUNG (V2.1 Ticket)")
    print("=" * 80)

    print("\nWie viele Treffer hat V2.1 in jeder Periode?")
    print(f"\n{'Per.':>4} {'0-2':>6} {'3':>6} {'4':>6} {'5':>6} {'6':>6} {'7+':>6} {'Avg':>6} {'Max':>5}")
    print("-" * 60)

    period_stats = []

    for i, p in enumerate(periods):
        if not p["has_next_jp"]:
            continue  # Nur vollstaendige Perioden

        hits_list = [simulate_v21_ticket(row["numbers_set"])
                     for _, row in p["draws"].iterrows()]

        dist = Counter(hits_list)

        low = sum(dist.get(h, 0) for h in range(0, 3))
        h3 = dist.get(3, 0)
        h4 = dist.get(4, 0)
        h5 = dist.get(5, 0)
        h6 = dist.get(6, 0)
        h7plus = sum(dist.get(h, 0) for h in range(7, 10))

        avg = np.mean(hits_list)
        max_h = max(hits_list)

        period_stats.append({
            "period": i + 1,
            "n_draws": p["n_draws"],
            "hits_list": hits_list,
            "avg": avg,
            "max": max_h,
            "h5_plus": h5 + h6 + h7plus,
            "dist": dist
        })

        print(f"{i+1:>4} {low:>6} {h3:>6} {h4:>6} {h5:>6} {h6:>6} {h7plus:>6} {avg:>6.2f} {max_h:>5}")

    # =========================================================================
    # 3. PROGRESSION INNERHALB DER PERIODEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. TREFFER-PROGRESSION: Anfang vs. Ende der Periode")
    print("=" * 80)

    print("\nHypothese: Vor dem naechsten Jackpot steigen die Treffer (Near-Miss)?")

    # Teile jede Periode in 4 Quartile
    quartile_hits = defaultdict(list)

    for i, p in enumerate(periods):
        if not p["has_next_jp"] or p["n_draws"] < 4:
            continue

        hits_list = [simulate_v21_ticket(row["numbers_set"])
                     for _, row in p["draws"].iterrows()]

        n = len(hits_list)
        q_size = n // 4

        for q in range(4):
            start = q * q_size
            end = (q + 1) * q_size if q < 3 else n
            q_hits = hits_list[start:end]
            quartile_hits[q].extend(q_hits)

    print(f"\n{'Quartil':<15} {'Avg Hits':>10} {'5+ Treffer':>12} {'6+ Treffer':>12}")
    print("-" * 55)

    quartile_names = ["Q1 (direkt nach JP)", "Q2 (frueh)", "Q3 (mittel)", "Q4 (vor naechstem JP)"]

    for q in range(4):
        hits = quartile_hits[q]
        avg = np.mean(hits)
        h5_plus = sum(1 for h in hits if h >= 5) / len(hits) * 100
        h6_plus = sum(1 for h in hits if h >= 6) / len(hits) * 100
        print(f"{quartile_names[q]:<15} {avg:>10.2f} {h5_plus:>11.1f}% {h6_plus:>11.1f}%")

    # =========================================================================
    # 4. NEAR-MISS EVENTS VOR JACKPOTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. NEAR-MISS EVENTS: Hohe Treffer VOR Jackpots")
    print("=" * 80)

    print("\nWann erscheinen 5+, 6+, 7+ Treffer relativ zum naechsten Jackpot?")

    high_hit_positions = []

    for i, p in enumerate(periods):
        if not p["has_next_jp"]:
            continue

        for j, (_, row) in enumerate(p["draws"].iterrows()):
            hits = simulate_v21_ticket(row["numbers_set"])
            if hits >= 5:
                days_to_jp = (p["end_jp_date"] - row["Datum"]).days
                draws_to_jp = p["n_draws"] - j - 1
                high_hit_positions.append({
                    "hits": hits,
                    "days_to_jp": days_to_jp,
                    "draws_to_jp": draws_to_jp,
                    "date": row["Datum"]
                })

    print(f"\n{'Datum':<12} {'Treffer':>8} {'Tage bis JP':>12} {'Zieh. bis JP':>14}")
    print("-" * 50)

    for event in sorted(high_hit_positions, key=lambda x: -x["hits"])[:20]:
        print(f"{event['date'].strftime('%d.%m.%Y'):<12} {event['hits']:>8} "
              f"{event['days_to_jp']:>12} {event['draws_to_jp']:>14}")

    # =========================================================================
    # 5. SIGNALE VOR JACKPOTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. JACKPOT-SIGNAL-ANALYSE")
    print("=" * 80)

    # Analysiere die letzten N Ziehungen vor jedem Jackpot
    windows = [3, 5, 7, 10]

    print("\nDurchschnittliche Treffer in den letzten N Ziehungen VOR Jackpot:")
    print(f"\n{'Fenster':<15} {'Avg Hits':>10} {'Max Hits':>10} {'5+ Events':>12}")
    print("-" * 50)

    for window in windows:
        window_hits = []
        window_max = []
        window_5plus = []

        for p in periods:
            if not p["has_next_jp"] or p["n_draws"] < window:
                continue

            # Letzte N Ziehungen vor Jackpot
            last_n = p["draws"].tail(window)
            hits_list = [simulate_v21_ticket(row["numbers_set"])
                         for _, row in last_n.iterrows()]

            window_hits.append(np.mean(hits_list))
            window_max.append(max(hits_list))
            window_5plus.append(sum(1 for h in hits_list if h >= 5))

        if window_hits:
            print(f"Letzte {window:<2} Zieh. {np.mean(window_hits):>10.2f} "
                  f"{np.mean(window_max):>10.1f} {np.mean(window_5plus):>12.1f}")

    # =========================================================================
    # 6. JACKPOT-WARTEZEIT-MUSTER
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. JACKPOT-WARTEZEIT-MUSTER")
    print("=" * 80)

    wait_times = []
    for p in periods:
        if p["has_next_jp"]:
            days = (p["end_jp_date"] - p["start_jp_date"]).days
            wait_times.append({
                "days": days,
                "draws": p["n_draws"],
                "start": p["start_jp_date"],
                "end": p["end_jp_date"]
            })

    print(f"\nWartezeit zwischen Jackpots:")
    print(f"  Min:  {min(w['days'] for w in wait_times):>3} Tage")
    print(f"  Max:  {max(w['days'] for w in wait_times):>3} Tage")
    print(f"  Mean: {np.mean([w['days'] for w in wait_times]):>5.1f} Tage")
    print(f"  Median: {np.median([w['days'] for w in wait_times]):>3.0f} Tage")

    # =========================================================================
    # 7. JACKPOT-VORHERSAGE-INDIKATOREN
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. POTENZIELLE JACKPOT-INDIKATOREN")
    print("=" * 80)

    # Berechne Indikatoren fuer jede Periode
    indicators = []

    for p in periods:
        if not p["has_next_jp"] or p["n_draws"] < 5:
            continue

        # Letzte 5 Ziehungen
        last_5 = p["draws"].tail(5)
        hits_last_5 = [simulate_v21_ticket(row["numbers_set"])
                       for _, row in last_5.iterrows()]

        # Letzte 3 Ziehungen
        last_3 = p["draws"].tail(3)
        hits_last_3 = [simulate_v21_ticket(row["numbers_set"])
                       for _, row in last_3.iterrows()]

        indicators.append({
            "period_start": p["start_jp_date"],
            "period_end": p["end_jp_date"],
            "n_draws": p["n_draws"],
            "avg_last_5": np.mean(hits_last_5),
            "max_last_5": max(hits_last_5),
            "avg_last_3": np.mean(hits_last_3),
            "max_last_3": max(hits_last_3),
            "has_5plus_last_5": any(h >= 5 for h in hits_last_5),
            "has_6plus_last_5": any(h >= 6 for h in hits_last_5)
        })

    print("\nMuster VOR Jackpots (letzte 5 Ziehungen):")
    print(f"\n{'Nach JP':>12} {'Naechster JP':>12} {'Avg':>6} {'Max':>5} {'5+?':>5} {'6+?':>5}")
    print("-" * 55)

    for ind in indicators:
        has_5 = "JA" if ind["has_5plus_last_5"] else "NEIN"
        has_6 = "JA" if ind["has_6plus_last_5"] else "NEIN"
        print(f"{ind['period_start'].strftime('%d.%m.%Y'):>12} "
              f"{ind['period_end'].strftime('%d.%m.%Y'):>12} "
              f"{ind['avg_last_5']:>6.2f} {ind['max_last_5']:>5} {has_5:>5} {has_6:>5}")

    # Statistik
    pct_with_5plus = sum(1 for i in indicators if i["has_5plus_last_5"]) / len(indicators) * 100
    pct_with_6plus = sum(1 for i in indicators if i["has_6plus_last_5"]) / len(indicators) * 100

    print(f"\n{'='*55}")
    print(f"Vor {len(indicators)} Jackpots:")
    print(f"  - {pct_with_5plus:.0f}% hatten mindestens einen 5+ Treffer in letzten 5 Zieh.")
    print(f"  - {pct_with_6plus:.0f}% hatten mindestens einen 6+ Treffer in letzten 5 Zieh.")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: JACKPOT-SIGNAL-ERKENNTNISSE")
    print("=" * 80)

    # Q4 vs Q1 Vergleich
    q1_avg = np.mean(quartile_hits[0]) if quartile_hits[0] else 0
    q4_avg = np.mean(quartile_hits[3]) if quartile_hits[3] else 0

    print(f"""
ERKENNTNISSE:

1. WARTEZEIT:
   - Durchschnittlich {np.mean([w['days'] for w in wait_times]):.0f} Tage zwischen Jackpots
   - Min: {min(w['days'] for w in wait_times)} Tage, Max: {max(w['days'] for w in wait_times)} Tage

2. PROGRESSION (Q1 → Q4):
   - Direkt nach JP (Q1): {q1_avg:.2f} Avg Treffer
   - Vor naechstem JP (Q4): {q4_avg:.2f} Avg Treffer
   - Trend: {'STEIGEND' if q4_avg > q1_avg else 'FALLEND' if q4_avg < q1_avg else 'STABIL'}

3. NEAR-MISS SIGNAL:
   - {pct_with_5plus:.0f}% der Jackpots hatten 5+ Treffer in den letzten 5 Ziehungen
   - {pct_with_6plus:.0f}% der Jackpots hatten 6+ Treffer in den letzten 5 Ziehungen

STRATEGIE-EMPFEHLUNG:
   - Nach Jackpot: Ticket aktualisieren (Jackpot Follower)
   - Wenn 5+ oder 6+ Treffer erscheinen: WARNUNG - naechster JP koennte nah sein!
   - Bei langer Wartezeit (>{np.mean([w['days'] for w in wait_times]):.0f} Tage): Erhoehte JP-Wahrscheinlichkeit
""")

    # Speichere Ergebnisse
    output = {
        "analysis_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "periods_analyzed": len(indicators),
        "avg_wait_days": float(np.mean([w['days'] for w in wait_times])),
        "quartile_progression": {
            "Q1_avg": float(q1_avg),
            "Q4_avg": float(q4_avg),
            "trend": "STEIGEND" if q4_avg > q1_avg else "FALLEND"
        },
        "pre_jackpot_signals": {
            "pct_with_5plus": pct_with_5plus,
            "pct_with_6plus": pct_with_6plus
        },
        "indicators": [
            {
                "start": i["period_start"].strftime("%Y-%m-%d"),
                "end": i["period_end"].strftime("%Y-%m-%d"),
                "avg_last_5": float(i["avg_last_5"]),
                "max_last_5": int(i["max_last_5"])
            }
            for i in indicators
        ]
    }

    output_path = base_path / "results" / "inter_jackpot_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Analyse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
