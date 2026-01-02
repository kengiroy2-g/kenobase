#!/usr/bin/env python3
"""
JACKPOT TIMING INDIKATOR

Kombiniert alle Signale zu einem "Jackpot Readiness Score":
- Tage seit letztem Jackpot
- Aktuelle Treffer-Tendenz
- Near-Miss Events

Output: Score von 0-100 der anzeigt wie "reif" der naechste Jackpot ist.

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import deque
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kenobase.core.keno_quotes import get_fixed_quote


# Konfiguration basierend auf historischer Analyse
CONFIG = {
    "avg_wait_days": 20,
    "median_wait_days": 14,
    "max_wait_days": 51,
    "min_wait_days": 4,
    "q4_avg_hits": 2.85,  # Avg kurz vor JP
    "q1_avg_hits": 2.71,  # Avg direkt nach JP
}


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_last_jackpot(base_path):
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        jackpots = timeline[timeline["keno_jackpot"] == 1].sort_values("datum")
        if len(jackpots) > 0:
            return jackpots.iloc[-1]["datum"]
    return None


def simulate_v21_ticket(draw_set):
    V2_1 = [3, 7, 36, 43, 48, 51, 55, 58, 61]
    return len(set(V2_1) & draw_set)


def calculate_timing_score(days_since_jp):
    """
    Score basierend auf Tagen seit letztem Jackpot.
    0-100 scale.
    """
    if days_since_jp <= CONFIG["min_wait_days"]:
        return 10  # Sehr unwahrscheinlich direkt nach JP
    elif days_since_jp <= CONFIG["median_wait_days"]:
        # Linear von 10 auf 50
        progress = (days_since_jp - CONFIG["min_wait_days"]) / (CONFIG["median_wait_days"] - CONFIG["min_wait_days"])
        return 10 + progress * 40
    elif days_since_jp <= CONFIG["avg_wait_days"]:
        # Linear von 50 auf 70
        progress = (days_since_jp - CONFIG["median_wait_days"]) / (CONFIG["avg_wait_days"] - CONFIG["median_wait_days"])
        return 50 + progress * 20
    elif days_since_jp <= CONFIG["max_wait_days"]:
        # Linear von 70 auf 95
        progress = (days_since_jp - CONFIG["avg_wait_days"]) / (CONFIG["max_wait_days"] - CONFIG["avg_wait_days"])
        return 70 + progress * 25
    else:
        return 98  # Ueberfaellig!


def calculate_trend_score(recent_hits):
    """
    Score basierend auf aktueller Treffer-Tendenz.
    Hohe Treffer = hoehere JP-Wahrscheinlichkeit.
    """
    if len(recent_hits) < 3:
        return 50  # Neutral

    avg = np.mean(recent_hits)
    max_recent = max(recent_hits)

    # Basis-Score aus Durchschnitt
    if avg >= CONFIG["q4_avg_hits"]:
        base_score = 70
    elif avg >= CONFIG["q1_avg_hits"]:
        progress = (avg - CONFIG["q1_avg_hits"]) / (CONFIG["q4_avg_hits"] - CONFIG["q1_avg_hits"])
        base_score = 40 + progress * 30
    else:
        base_score = 30

    # Bonus fuer High-Hits
    bonus = 0
    if max_recent >= 7:
        bonus = 20
    elif max_recent >= 6:
        bonus = 15
    elif max_recent >= 5:
        bonus = 10

    return min(95, base_score + bonus)


def calculate_near_miss_score(recent_hits):
    """
    Score basierend auf Near-Miss Events (5+, 6+ Treffer).
    """
    if len(recent_hits) < 5:
        return 50

    h5_count = sum(1 for h in recent_hits if h >= 5)
    h6_count = sum(1 for h in recent_hits if h >= 6)
    h7_count = sum(1 for h in recent_hits if h >= 7)

    score = 30  # Basis

    # Near-Miss Bonus
    score += h5_count * 10
    score += h6_count * 15
    score += h7_count * 20

    return min(95, score)


def calculate_combined_score(timing_score, trend_score, near_miss_score):
    """
    Kombiniere alle Scores mit Gewichtung.
    """
    weights = {
        "timing": 0.50,    # Wartezeit ist wichtigster Faktor
        "trend": 0.25,     # Trend zeigt System-Verhalten
        "near_miss": 0.25  # Near-Miss sind starke Signale
    }

    combined = (
        timing_score * weights["timing"] +
        trend_score * weights["trend"] +
        near_miss_score * weights["near_miss"]
    )

    return combined


def get_status_level(score):
    """Bestimme Status-Level basierend auf Score."""
    if score >= 80:
        return "KRITISCH", "🔴", "Jackpot sehr wahrscheinlich! Maximale Aufmerksamkeit!"
    elif score >= 65:
        return "HOCH", "🟠", "Erhoehte Jackpot-Wahrscheinlichkeit. Wachsam bleiben!"
    elif score >= 50:
        return "MITTEL", "🟡", "Normale Phase. Ticket spielen und beobachten."
    elif score >= 35:
        return "NIEDRIG", "🟢", "Fruehe Phase nach Jackpot. Geduld haben."
    else:
        return "SEHR NIEDRIG", "⚪", "Direkt nach Jackpot. Neues Ticket generieren."


def main():
    print("=" * 80)
    print("JACKPOT TIMING INDIKATOR")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)

    # Letzter Jackpot
    last_jp = get_last_jackpot(base_path)
    today = pd.Timestamp.now().normalize()

    if last_jp is None:
        print("FEHLER: Kein Jackpot gefunden!")
        return

    days_since_jp = (today - last_jp).days

    print(f"\nLetzter Jackpot:     {last_jp.strftime('%d.%m.%Y')}")
    print(f"Heute:               {today.strftime('%d.%m.%Y')}")
    print(f"Tage seit Jackpot:   {days_since_jp}")
    print(f"Durchschnitt:        {CONFIG['avg_wait_days']} Tage")

    # Letzte Ziehungen nach dem Jackpot
    df_since_jp = df[df["Datum"] > last_jp].sort_values("Datum")
    recent_hits = [simulate_v21_ticket(row["numbers_set"])
                   for _, row in df_since_jp.tail(10).iterrows()]

    print(f"\nLetzte 10 Treffer:   {recent_hits}")
    print(f"Avg letzte 10:       {np.mean(recent_hits):.2f}")
    print(f"Max letzte 10:       {max(recent_hits) if recent_hits else 0}")

    # =========================================================================
    # SCORE-BERECHNUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("SCORE-BERECHNUNG")
    print("=" * 80)

    timing_score = calculate_timing_score(days_since_jp)
    trend_score = calculate_trend_score(recent_hits)
    near_miss_score = calculate_near_miss_score(recent_hits)
    combined_score = calculate_combined_score(timing_score, trend_score, near_miss_score)

    print(f"""
EINZELNE SCORES:
  Timing Score:     {timing_score:>5.1f} / 100  (Gewicht: 50%)
  Trend Score:      {trend_score:>5.1f} / 100  (Gewicht: 25%)
  Near-Miss Score:  {near_miss_score:>5.1f} / 100  (Gewicht: 25%)

KOMBINIERTER SCORE:
""")

    status, emoji, message = get_status_level(combined_score)

    # Visualisierung
    bar_length = int(combined_score / 2)
    bar = "█" * bar_length + "░" * (50 - bar_length)

    print(f"  {emoji} {combined_score:.1f} / 100 [{bar}] {status}")
    print(f"\n  {message}")

    # =========================================================================
    # DETAIL-ANALYSE
    # =========================================================================
    print("\n" + "=" * 80)
    print("DETAIL-ANALYSE")
    print("=" * 80)

    # Timing
    print(f"\n1. TIMING ({timing_score:.0f}/100):")
    if days_since_jp > CONFIG["avg_wait_days"]:
        print(f"   ⚠️  {days_since_jp - CONFIG['avg_wait_days']} Tage UEBER Durchschnitt!")
    elif days_since_jp > CONFIG["median_wait_days"]:
        print(f"   📊  {CONFIG['avg_wait_days'] - days_since_jp} Tage bis Durchschnitt")
    else:
        print(f"   ✓  Noch in normaler Frühphase")

    # Trend
    print(f"\n2. TREND ({trend_score:.0f}/100):")
    if len(recent_hits) >= 3:
        avg = np.mean(recent_hits)
        if avg >= CONFIG["q4_avg_hits"]:
            print(f"   📈 Treffer-Durchschnitt ({avg:.2f}) auf Q4-Niveau!")
        else:
            print(f"   📊 Treffer-Durchschnitt: {avg:.2f}")

    # Near-Miss
    print(f"\n3. NEAR-MISS ({near_miss_score:.0f}/100):")
    h5_count = sum(1 for h in recent_hits if h >= 5)
    h6_count = sum(1 for h in recent_hits if h >= 6)
    if h6_count > 0:
        print(f"   🎯 {h6_count}x 6+ Treffer in letzten 10 Ziehungen!")
    elif h5_count > 0:
        print(f"   📍 {h5_count}x 5+ Treffer in letzten 10 Ziehungen")
    else:
        print(f"   ✓  Keine Near-Miss Events")

    # =========================================================================
    # EMPFEHLUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("EMPFEHLUNG")
    print("=" * 80)

    # Lade das empfohlene Ticket
    ticket_path = base_path / "results" / "jackpot_follower_ticket.json"
    if ticket_path.exists():
        with open(ticket_path, "r") as f:
            ticket_data = json.load(f)
        recommended_ticket = ticket_data.get("recommended_ticket", [])
    else:
        recommended_ticket = [1, 2, 4, 12, 34, 43, 49, 54, 55]

    print(f"""
AKTUELLES TICKET (Jackpot Follower):
  {recommended_ticket}

STRATEGIE basierend auf Score ({combined_score:.0f}):
""")

    if combined_score >= 80:
        print("""  🔴 KRITISCH - Maximaler Einsatz empfohlen!
     - Ticket JEDEN TAG spielen
     - Eventuell Typ 10 statt Typ 9 (hoeherer Jackpot)
     - System ist "ueberfaellig" - Jackpot wahrscheinlich BALD""")
    elif combined_score >= 65:
        print("""  🟠 HOCH - Erhoehte Aufmerksamkeit!
     - Ticket regelmaessig spielen
     - Bei weiteren Near-Miss Events: Einsatz erhoehen
     - Auf 5+ oder 6+ Treffer achten als finales Signal""")
    elif combined_score >= 50:
        print("""  🟡 MITTEL - Normale Spielphase
     - Ticket wie gewohnt spielen
     - Treffer-Entwicklung beobachten
     - Noch kein Grund fuer erhoehten Einsatz""")
    elif combined_score >= 35:
        print("""  🟢 NIEDRIG - Geduld-Phase
     - Ticket mit minimalem Einsatz spielen
     - System ist noch in Erholungsphase nach letztem JP
     - Fokus auf Daten-Sammlung""")
    else:
        print("""  ⚪ SEHR NIEDRIG - Direkt nach Jackpot
     - Neues Ticket aus Jackpot Follower generieren
     - Minimaler Einsatz
     - Abwarten bis Wartezeit steigt""")

    # =========================================================================
    # OUTPUT
    # =========================================================================
    output = {
        "timestamp": datetime.now().isoformat(),
        "last_jackpot": last_jp.strftime("%Y-%m-%d"),
        "days_since_jackpot": days_since_jp,
        "scores": {
            "timing": round(timing_score, 1),
            "trend": round(trend_score, 1),
            "near_miss": round(near_miss_score, 1),
            "combined": round(combined_score, 1)
        },
        "status": status,
        "recent_hits": recent_hits,
        "recommended_ticket": recommended_ticket
    }

    output_path = base_path / "results" / "jackpot_timing_indicator.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nIndikator gespeichert: {output_path}")


if __name__ == "__main__":
    main()
