#!/usr/bin/env python3
"""
SMART TICKET GENERATOR

Nutzt KDI/KVS-Metriken fuer intelligente Zahlenauswahl.

STRATEGIE:
- Berechne Metriken fuer alle 70 Zahlen
- Ranke nach "Favorabilitaet" (niedriger KDI, hoher Gap, niedrige Popularitaet)
- Generiere Tickets aus den besten Zahlen

METRIKEN:
- KDI: Korrektur-Druck-Index (VERMEIDEN wenn hoch)
- GAS: Gap-Alert-Score (BEVORZUGEN wenn hoch)
- POP: Popularitaets-Schaetzung (VERMEIDEN wenn hoch)
- DBS: Dekaden-Balance-Score

Autor: Kenobase V2.5
"""

import csv
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# === KONSTANTEN ===

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}
MUSTER_POPULAR = {7, 11, 13, 17, 21, 23}  # "Glueckszahlen"

# KENO Quoten
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 60, 7: 5000},
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 4, 6: 15, 7: 100, 8: 10000},
    9: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 6, 7: 25, 8: 500, 9: 50000},
    10: {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000},
}


@dataclass
class NumberScore:
    """Score fuer eine einzelne Zahl."""
    zahl: int
    kdi: float  # Korrektur-Druck-Index (niedrig = gut)
    gas: float  # Gap-Alert-Score (hoch = gut)
    pop: float  # Popularitaet (niedrig = gut)
    dbs: float  # Dekaden-Balance

    # Composite Scores
    favorability: float  # Gesamt-Favorabilitaet (hoch = gut)
    risk_level: str  # "LOW", "MEDIUM", "HIGH"

    # Context
    gap: int
    index: int
    is_birthday: bool
    is_muster: bool


def load_keno_data(filepath: Path) -> List[Dict]:
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
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def load_jackpot_dates(events_path: Path) -> List[datetime]:
    """Laedt Jackpot-Daten (verified + pending)."""
    if not events_path.exists():
        return []
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    dates = []
    # Verified events
    for event in data.get("events", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except Exception:
            pass
    # Pending events (auch nuetzlich fuer Timing)
    for event in data.get("pending_from_quotes_2023", []):
        try:
            dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
        except Exception:
            pass
    return sorted(set(dates))  # Unique dates


def get_days_since_jackpot(datum: datetime, jackpot_dates: List[datetime]) -> int:
    """Berechnet Tage seit letztem Jackpot."""
    past = [jp for jp in jackpot_dates if jp < datum]
    if not past:
        return 999
    return (datum - max(past)).days


def calculate_number_history(draws: List[Dict], lookback: int = 30) -> Dict:
    """
    Berechnet historische Statistiken fuer alle 70 Zahlen.

    Returns:
        Dict mit: frequency, last_seen, momentum_count, gaps
    """
    recent = draws[-lookback:] if len(draws) >= lookback else draws

    stats = {
        z: {
            "frequency": 0,
            "last_seen": -1,
            "momentum_3": 0,  # Count in last 3 days
            "appearances": []
        }
        for z in range(1, 71)
    }

    for idx, draw in enumerate(recent):
        for z in draw["zahlen"]:
            stats[z]["frequency"] += 1
            stats[z]["appearances"].append(idx)

    # Last seen und Gap berechnen
    for z in range(1, 71):
        if stats[z]["appearances"]:
            stats[z]["last_seen"] = max(stats[z]["appearances"])
            stats[z]["gap"] = len(recent) - 1 - stats[z]["last_seen"]
        else:
            stats[z]["gap"] = lookback  # Nie erschienen = maximaler Gap

    # Momentum (letzte 3 Tage)
    last_3 = draws[-3:] if len(draws) >= 3 else draws
    for draw in last_3:
        for z in draw["zahlen"]:
            stats[z]["momentum_3"] += 1

    return stats


def calculate_kdi(
    zahl: int,
    index: int,
    is_birthday: bool,
    is_muster: bool,
    momentum_count: int,
    gap: int
) -> float:
    """
    Korrektur-Druck-Index (KDI).

    Hoher KDI = System wird diese Zahl wahrscheinlich KORRIGIEREN (nicht ziehen).

    Faktoren die KDI erhoehen:
    - Hoher Index (oft gezogen)
    - Birthday-Zahl (populaer)
    - Muster-Zahl (7, 11, 13...)
    - Hohes Momentum (kuerzlich oft gezogen)
    - Niedriger Gap (gerade erst gezogen)
    """
    druck = 0.0

    # Index-Druck (stark!)
    if index >= 2:
        druck += 0.20 + (index - 2) * 0.10
    if index >= 4:
        druck += 0.20  # Extra Penalty

    # Birthday-Druck
    if is_birthday:
        druck += 0.15
        if index >= 1:  # Birthday + aktiv = sehr riskant
            druck += 0.15

    # Muster-Druck
    if is_muster:
        druck += 0.10

    # Momentum-Druck (stark!)
    if momentum_count >= 2:
        druck += 0.25  # Hohes Momentum = hohes Risiko
    elif momentum_count == 1:
        druck += 0.10

    # Gap-Druck (invers - niedriger Gap = hoeher Druck)
    if gap <= 1:
        druck += 0.20
    elif gap <= 3:
        druck += 0.10

    return min(druck, 1.0)


def calculate_gas(gap: int, max_gap: int = 30) -> float:
    """
    Gap-Alert-Score (GAS).

    Hoher GAS = Zahl lange nicht gezogen = koennnte "faellig" sein.

    Nach Korrektur-Theorie: System muss Pseudo-Zufall garantieren,
    also werden Zahlen mit langem Gap irgendwann gezogen.
    """
    if gap >= 10:
        return 0.8 + min((gap - 10) * 0.02, 0.2)  # Max 1.0
    elif gap >= 7:
        return 0.6
    elif gap >= 5:
        return 0.4
    elif gap >= 3:
        return 0.2
    else:
        return 0.0


def calculate_pop(zahl: int, is_birthday: bool, is_muster: bool) -> float:
    """
    Popularitaets-Schaetzung (POP).

    Hohe POP = viele Spieler waehlen diese Zahl = zu vermeiden.
    """
    pop = 0.0

    if is_birthday:
        pop += 0.40  # Birthday sehr populaer

    if is_muster:
        pop += 0.30  # Glueckszahlen populaer

    # Runde Zahlen
    if zahl % 10 == 0:
        pop += 0.15

    # Sehr niedrige Zahlen
    if zahl <= 10:
        pop += 0.10

    return min(pop, 1.0)


def calculate_dbs(zahl: int, selected: Set[int]) -> float:
    """
    Dekaden-Balance-Score (DBS).

    Prueft wie gut die Dekade dieser Zahl zur bisherigen Auswahl passt.
    """
    if not selected:
        return 0.5  # Neutral

    dekade = zahl // 10
    dekaden_count = defaultdict(int)
    for s in selected:
        dekaden_count[s // 10] += 1

    # Wenn diese Dekade schon oft vertreten ist = niedrigerer Score
    current_in_dekade = dekaden_count.get(dekade, 0)

    if current_in_dekade >= 2:
        return 0.1  # Schlechte Balance
    elif current_in_dekade == 1:
        return 0.4
    else:
        return 0.8  # Gute Diversifikation


def calculate_favorability(kdi: float, gas: float, pop: float) -> float:
    """
    Gesamt-Favorabilitaet einer Zahl.

    Hohe Favorabilitaet = gute Wahl fuer Ticket.

    Formel:
    - KDI negativ gewichtet (hohes KDI = schlecht)
    - GAS positiv gewichtet (hoher Gap = gut)
    - POP negativ gewichtet (hohe Popularitaet = schlecht)
    """
    score = (
        -kdi * 0.50 +      # Korrektur-Druck stark vermeiden
        gas * 0.30 +       # Gap-Alert moderat positiv
        -pop * 0.35 +      # Popularitaet vermeiden
        0.5                # Basis-Offset
    )
    return max(0.0, min(1.0, score))


def get_risk_level(kdi: float, pop: float, momentum: int) -> str:
    """Bestimmt Risiko-Level einer Zahl."""
    risk_score = kdi * 0.5 + pop * 0.3 + (momentum / 3) * 0.2

    if risk_score >= 0.6:
        return "HIGH"
    elif risk_score >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"


def score_all_numbers(
    draws: List[Dict],
    jackpot_dates: List[datetime],
    current_date: datetime = None
) -> List[NumberScore]:
    """
    Berechnet Scores fuer alle 70 Zahlen.

    Returns:
        Liste von NumberScore, sortiert nach Favorabilitaet (beste zuerst)
    """
    if current_date is None:
        current_date = datetime.now()

    # Historische Stats berechnen
    stats = calculate_number_history(draws, lookback=30)

    # Index aus letzten 20 Tagen
    recent_20 = draws[-20:] if len(draws) >= 20 else draws
    index_counts = defaultdict(int)
    for draw in recent_20:
        for z in draw["zahlen"]:
            index_counts[z] += 1

    scores = []

    for zahl in range(1, 71):
        is_birthday = zahl in BIRTHDAY_POPULAR
        is_muster = zahl in MUSTER_POPULAR
        gap = stats[zahl]["gap"]
        momentum = stats[zahl]["momentum_3"]
        index = index_counts.get(zahl, 0)

        # Metriken berechnen
        kdi = calculate_kdi(zahl, index, is_birthday, is_muster, momentum, gap)
        gas = calculate_gas(gap)
        pop = calculate_pop(zahl, is_birthday, is_muster)
        dbs = 0.5  # Wird spaeter bei Selektion berechnet

        favorability = calculate_favorability(kdi, gas, pop)
        risk_level = get_risk_level(kdi, pop, momentum)

        scores.append(NumberScore(
            zahl=zahl,
            kdi=kdi,
            gas=gas,
            pop=pop,
            dbs=dbs,
            favorability=favorability,
            risk_level=risk_level,
            gap=gap,
            index=index,
            is_birthday=is_birthday,
            is_muster=is_muster
        ))

    # Sortiere nach Favorabilitaet (beste zuerst)
    scores.sort(key=lambda x: -x.favorability)

    return scores


def generate_smart_ticket(
    scores: List[NumberScore],
    typ: int,
    strategy: str = "balanced"
) -> Tuple[List[int], Dict]:
    """
    Generiert ein intelligentes Ticket basierend auf Scores.

    Strategien:
    - "balanced": Balancierte Auswahl mit Dekaden-Check
    - "aggressive": Top Favorabilitaet, ignoriert Dekaden
    - "conservative": Nur LOW-Risk Zahlen

    Returns:
        (ticket, meta_info)
    """
    selected = set()
    meta = {
        "strategy": strategy,
        "avg_favorability": 0.0,
        "avg_kdi": 0.0,
        "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    }

    if strategy == "conservative":
        # Nur LOW-Risk Zahlen
        candidates = [s for s in scores if s.risk_level == "LOW"]
    elif strategy == "aggressive":
        # Top 20 Favorabilitaet
        candidates = scores[:20]
    else:  # balanced
        # LOW und MEDIUM Risk, aber nicht HIGH
        candidates = [s for s in scores if s.risk_level != "HIGH"]

    # Fallback wenn nicht genug Kandidaten
    if len(candidates) < typ:
        candidates = scores[:typ * 3]

    # Auswahl mit Dekaden-Balance
    for score in candidates:
        if len(selected) >= typ:
            break

        # Dekaden-Check
        dekade = score.zahl // 10
        dekaden_in_selected = sum(1 for s in selected if s // 10 == dekade)

        if dekaden_in_selected >= 2:
            continue  # Max 2 pro Dekade

        selected.add(score.zahl)

    # Falls noch nicht genug: mit Zufall auffuellen
    if len(selected) < typ:
        remaining = [s.zahl for s in candidates if s.zahl not in selected]
        random.shuffle(remaining)
        while len(selected) < typ and remaining:
            selected.add(remaining.pop())

    # Meta-Info berechnen
    selected_scores = [s for s in scores if s.zahl in selected]
    if selected_scores:
        meta["avg_favorability"] = sum(s.favorability for s in selected_scores) / len(selected_scores)
        meta["avg_kdi"] = sum(s.kdi for s in selected_scores) / len(selected_scores)
        for s in selected_scores:
            meta["risk_distribution"][s.risk_level] += 1

    ticket = sorted(selected)
    return ticket, meta


def generate_multiple_tickets(
    scores: List[NumberScore],
    typ: int,
    n_tickets: int = 5
) -> List[Tuple[List[int], Dict]]:
    """
    Generiert mehrere verschiedene Tickets.

    Variiert die Auswahl leicht, um Diversifikation zu ermoeglichen.
    """
    tickets = []
    used_numbers = set()

    for i in range(n_tickets):
        # Strategie variieren
        if i == 0:
            strategy = "balanced"
        elif i == 1:
            strategy = "conservative"
        elif i == 2:
            strategy = "aggressive"
        else:
            strategy = "balanced"

        # Scores leicht shuffeln fuer Variation
        shuffled_scores = scores.copy()
        if i > 0:
            # Leichte Randomisierung innerhalb aehnlicher Favorabilitaet
            for j in range(len(shuffled_scores) - 1):
                if abs(shuffled_scores[j].favorability - shuffled_scores[j+1].favorability) < 0.05:
                    if random.random() < 0.3:
                        shuffled_scores[j], shuffled_scores[j+1] = shuffled_scores[j+1], shuffled_scores[j]

        ticket, meta = generate_smart_ticket(shuffled_scores, typ, strategy)
        meta["ticket_index"] = i + 1
        tickets.append((ticket, meta))

    return tickets


def print_analysis(scores: List[NumberScore], top_n: int = 20):
    """Gibt Analyse der Zahlen-Scores aus."""

    print("\n" + "=" * 80)
    print("ZAHLEN-ANALYSE (Smart Ticket Generator)")
    print("=" * 80)

    print(f"\n{'Rang':<5} {'Zahl':<6} {'Favor':<8} {'KDI':<8} {'GAS':<8} {'POP':<8} {'Risk':<8} {'Gap':<5}")
    print("-" * 70)

    for i, s in enumerate(scores[:top_n]):
        bd = "B" if s.is_birthday else " "
        mu = "M" if s.is_muster else " "
        flags = bd + mu
        print(f"{i+1:<5} {s.zahl:<4}{flags} {s.favorability:<8.3f} {s.kdi:<8.3f} "
              f"{s.gas:<8.3f} {s.pop:<8.3f} {s.risk_level:<8} {s.gap:<5}")

    # Statistik
    low_risk = [s for s in scores if s.risk_level == "LOW"]
    high_risk = [s for s in scores if s.risk_level == "HIGH"]

    print(f"\n--- Statistik ---")
    print(f"LOW Risk Zahlen: {len(low_risk)}")
    print(f"HIGH Risk Zahlen: {len(high_risk)}")
    print(f"Beste 10: {[s.zahl for s in scores[:10]]}")
    print(f"Schlechteste 10: {[s.zahl for s in scores[-10:]]}")


def print_tickets(tickets: List[Tuple[List[int], Dict]]):
    """Gibt generierte Tickets formatiert aus."""

    print("\n" + "=" * 80)
    print("GENERIERTE SMART TICKETS")
    print("=" * 80)

    for ticket, meta in tickets:
        strategy = meta.get("strategy", "?")
        avg_fav = meta.get("avg_favorability", 0)
        avg_kdi = meta.get("avg_kdi", 0)
        risk_dist = meta.get("risk_distribution", {})

        print(f"\n  Ticket #{meta.get('ticket_index', '?')} ({strategy.upper()})")
        print(f"  +-----------------------------------------------+")
        print(f"  | {' '.join(f'{n:2d}' for n in ticket):43s} |")
        print(f"  +-----------------------------------------------+")
        print(f"  Favorabilitaet: {avg_fav:.3f} | KDI: {avg_kdi:.3f}")
        print(f"  Risiko: LOW={risk_dist.get('LOW', 0)}, MED={risk_dist.get('MEDIUM', 0)}, HIGH={risk_dist.get('HIGH', 0)}")


def check_timing(datum: datetime, jackpot_dates: List[datetime]) -> Dict:
    """Prueft Timing-Regeln."""
    # Tage seit Jackpot
    past = [jp for jp in jackpot_dates if jp < datum]
    days_since_jp = (datum - max(past)).days if past else 999

    day_of_month = datum.day
    weekday = datum.weekday()  # 0=Mo, 2=Mi

    boost_phase = 8 <= days_since_jp <= 14
    tag_24_28 = 24 <= day_of_month <= 28
    mittwoch = weekday == 2

    # Kombinierte Regeln (BESTE STRATEGIE!)
    any_combo = boost_phase and (tag_24_28 or mittwoch)

    return {
        "days_since_jp": days_since_jp,
        "boost_phase": boost_phase,
        "tag_24_28": tag_24_28,
        "mittwoch": mittwoch,
        "any_combo": any_combo,  # +36.3% ROI Bedingung!
    }


def run_comparison_backtest(
    draws: List[Dict],
    jackpot_dates: List[datetime],
    typ: int = 7,
    n_tests: int = 100,
    n_sims: int = 100
) -> Dict:
    """
    Vergleicht Smart-Generator mit Random-Generator.

    Returns:
        Backtest-Ergebnisse
    """
    print(f"\n{'='*80}")
    print(f"BACKTEST: Smart vs Random (Typ {typ}, {n_tests} Ziehungen, {n_sims} Sims)")
    print(f"{'='*80}")

    results = {
        "smart_balanced": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
        "smart_conservative": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
        "random": {"cost": 0, "win": 0, "treffer": defaultdict(int)},
    }

    test_draws = draws[-n_tests-30:-30] if len(draws) > n_tests + 30 else draws[:-30]

    for sim in range(n_sims):
        if sim % 20 == 0:
            print(f"  Simulation {sim}/{n_sims}...")

        for idx in range(30, len(test_draws)):
            draw = test_draws[idx]
            history = test_draws[:idx]

            # Scores berechnen (basierend auf Historie VOR der Ziehung)
            scores = score_all_numbers(history, jackpot_dates, draw["datum"])

            # Smart Balanced Ticket
            ticket_sb, _ = generate_smart_ticket(scores, typ, "balanced")
            treffer_sb = len(set(ticket_sb) & draw["zahlen"])
            win_sb = KENO_QUOTES[typ].get(treffer_sb, 0)
            results["smart_balanced"]["cost"] += 1
            results["smart_balanced"]["win"] += win_sb
            results["smart_balanced"]["treffer"][treffer_sb] += 1

            # Smart Conservative Ticket
            ticket_sc, _ = generate_smart_ticket(scores, typ, "conservative")
            treffer_sc = len(set(ticket_sc) & draw["zahlen"])
            win_sc = KENO_QUOTES[typ].get(treffer_sc, 0)
            results["smart_conservative"]["cost"] += 1
            results["smart_conservative"]["win"] += win_sc
            results["smart_conservative"]["treffer"][treffer_sc] += 1

            # Random Ticket
            ticket_r = set(random.sample(range(1, 71), typ))
            treffer_r = len(ticket_r & draw["zahlen"])
            win_r = KENO_QUOTES[typ].get(treffer_r, 0)
            results["random"]["cost"] += 1
            results["random"]["win"] += win_r
            results["random"]["treffer"][treffer_r] += 1

    # ROI berechnen
    print(f"\n{'Strategy':<25} {'Games':>10} {'Win':>12} {'ROI':>12}")
    print("-" * 60)

    for strategy, data in results.items():
        if data["cost"] > 0:
            roi = (data["win"] - data["cost"]) / data["cost"] * 100
            data["roi"] = roi
            print(f"{strategy:<25} {data['cost']:>10} {data['win']:>12,} {roi:>+11.2f}%")

    return results


def run_timing_backtest(
    draws: List[Dict],
    jackpot_dates: List[datetime],
    typ: int = 7,
    n_sims: int = 500
) -> Dict:
    """
    Backtest MIT Timing-Regeln (Boost-Phase).

    Das ist der richtige Test - kombiniert Timing + Zahlenauswahl.
    """
    print(f"\n{'='*80}")
    print(f"TIMING-BACKTEST: Smart vs Random vs Anti-Momentum")
    print(f"Timing: NUR Boost-Phase (8-14 Tage nach Jackpot)")
    print(f"{'='*80}")

    results = {
        "smart_boost": {"cost": 0, "win": 0, "plays": 0},
        "random_boost": {"cost": 0, "win": 0, "plays": 0},
        "anti_momentum_boost": {"cost": 0, "win": 0, "plays": 0},
        "random_immer": {"cost": 0, "win": 0, "plays": 0},
    }

    # Test auf 2023-2024 Daten
    test_draws = [d for d in draws if d["datum"].year in [2023, 2024]]
    print(f"Jackpots geladen: {len(jackpot_dates)}")
    print(f"Test-Ziehungen: {len(test_draws)}")

    boost_days = 0
    combo_days = 0
    for draw in test_draws:
        timing = check_timing(draw["datum"], jackpot_dates)
        if timing["boost_phase"]:
            boost_days += 1
        if timing["any_combo"]:
            combo_days += 1
    print(f"Tage in Boost-Phase: {boost_days}")
    print(f"Tage mit optimalen Timing (Boost + Mi/24-28): {combo_days}")

    for sim in range(n_sims):
        if sim % 100 == 0:
            print(f"  Simulation {sim}/{n_sims}...")

        for idx, draw in enumerate(test_draws):
            if idx < 30:
                continue

            history = test_draws[:idx]
            timing = check_timing(draw["datum"], jackpot_dates)

            # Random IMMER spielen (Baseline)
            ticket_ri = set(random.sample(range(1, 71), typ))
            treffer_ri = len(ticket_ri & draw["zahlen"])
            win_ri = KENO_QUOTES[typ].get(treffer_ri, 0)
            results["random_immer"]["cost"] += 1
            results["random_immer"]["win"] += win_ri

            # NUR bei Boost-Phase spielen
            if timing["boost_phase"]:
                results["random_boost"]["plays"] += 1
                results["smart_boost"]["plays"] += 1
                results["anti_momentum_boost"]["plays"] += 1

                # 1. Random mit Timing
                ticket_rt = set(random.sample(range(1, 71), typ))
                treffer_rt = len(ticket_rt & draw["zahlen"])
                win_rt = KENO_QUOTES[typ].get(treffer_rt, 0)
                results["random_boost"]["cost"] += 1
                results["random_boost"]["win"] += win_rt

                # 2. Smart mit Timing
                scores = score_all_numbers(history, jackpot_dates, draw["datum"])
                ticket_st, _ = generate_smart_ticket(scores, typ, "balanced")
                treffer_st = len(set(ticket_st) & draw["zahlen"])
                win_st = KENO_QUOTES[typ].get(treffer_st, 0)
                results["smart_boost"]["cost"] += 1
                results["smart_boost"]["win"] += win_st

                # 3. Anti-Momentum mit Timing (klassisch)
                # Momentum = Zahlen die 2+ mal in letzten 3 Tagen erschienen
                momentum = set()
                for h in history[-3:]:
                    for z in h["zahlen"]:
                        momentum.add(z)
                pool = [z for z in range(1, 71) if z not in (momentum | BIRTHDAY_POPULAR)]
                if len(pool) < typ:
                    pool = [z for z in range(1, 71) if z not in momentum]
                ticket_am = set(random.sample(pool, min(typ, len(pool))))
                while len(ticket_am) < typ:
                    ticket_am.add(random.randint(1, 70))
                treffer_am = len(ticket_am & draw["zahlen"])
                win_am = KENO_QUOTES[typ].get(treffer_am, 0)
                results["anti_momentum_boost"]["cost"] += 1
                results["anti_momentum_boost"]["win"] += win_am

    # ROI berechnen
    print(f"\n{'Strategy':<30} {'Plays':>8} {'Games':>10} {'Win':>12} {'ROI':>12}")
    print("-" * 75)

    for strategy, data in results.items():
        if data["cost"] > 0:
            roi = (data["win"] - data["cost"]) / data["cost"] * 100
            data["roi"] = roi
            plays = data.get("plays", data["cost"]) // n_sims
            print(f"{strategy:<30} {plays:>8} {data['cost']:>10} {data['win']:>12,} {roi:>+11.2f}%")

    # Vergleich
    print(f"\n--- VERGLEICH ---")
    if results["random_immer"]["cost"] > 0:
        baseline = results["random_immer"]["roi"]
        print(f"Baseline (Random immer):       {baseline:+.2f}%")

        if results["random_boost"]["cost"] > 0:
            rt_roi = results["random_boost"]["roi"]
            print(f"Random + Boost:                {rt_roi:+.2f}% (vs Baseline: {rt_roi - baseline:+.2f}%)")

        if results["anti_momentum_boost"]["cost"] > 0:
            am_roi = results["anti_momentum_boost"]["roi"]
            print(f"Anti-Momentum + Boost:         {am_roi:+.2f}% (vs Baseline: {am_roi - baseline:+.2f}%)")

        if results["smart_boost"]["cost"] > 0:
            st_roi = results["smart_boost"]["roi"]
            print(f"Smart + Boost:                 {st_roi:+.2f}% (vs Baseline: {st_roi - baseline:+.2f}%)")

    return results


def main():
    print("=" * 80)
    print("SMART TICKET GENERATOR")
    print("Nutzt KDI/KVS-Metriken fuer intelligente Zahlenauswahl")
    print("=" * 80)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"

    print("\nLade Daten...")
    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(events_path)

    print(f"  Ziehungen: {len(draws)}")
    print(f"  Letzte: {draws[-1]['datum'].date()}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # === AKTUELLE ANALYSE ===
    print("\nBerechne Scores fuer alle 70 Zahlen...")
    scores = score_all_numbers(draws, jackpot_dates)

    # Analyse ausgeben
    print_analysis(scores, top_n=25)

    # === TICKETS GENERIEREN ===
    for typ in [7, 8, 9, 10]:
        print(f"\n{'='*80}")
        print(f"TYP {typ} TICKETS")
        print(f"{'='*80}")

        tickets = generate_multiple_tickets(scores, typ, n_tickets=3)
        print_tickets(tickets)

    # === TIMING BACKTEST (der wichtige Test!) ===
    print("\n\nStarte Timing-Backtest (Boost-Phase + Mittwoch/Tag24-28)...")
    timing_results = run_timing_backtest(
        draws, jackpot_dates,
        typ=7,
        n_sims=500
    )

    # === SIMPLE BACKTEST (zum Vergleich) ===
    print("\n\nStarte Vergleichs-Backtest (ohne Timing)...")
    backtest_results = run_comparison_backtest(
        draws, jackpot_dates,
        typ=7,
        n_tests=100,
        n_sims=100
    )

    # === FAZIT ===
    print("\n" + "=" * 80)
    print("FAZIT")
    print("=" * 80)

    # Timing-Ergebnisse (wichtiger!)
    print("\n--- MIT BOOST-PHASE (8-14 Tage nach Jackpot) ---")
    if timing_results.get("random_immer", {}).get("roi"):
        baseline = timing_results["random_immer"]["roi"]
        print(f"Baseline (Random immer):  {baseline:+.2f}%")

    if timing_results.get("random_boost", {}).get("roi"):
        rt = timing_results["random_boost"]["roi"]
        print(f"Random + Boost:           {rt:+.2f}%")

    if timing_results.get("anti_momentum_boost", {}).get("roi"):
        am = timing_results["anti_momentum_boost"]["roi"]
        print(f"Anti-Momentum + Boost:    {am:+.2f}%")

    if timing_results.get("smart_boost", {}).get("roi"):
        st = timing_results["smart_boost"]["roi"]
        print(f"Smart + Boost:            {st:+.2f}%")

    # Vergleich Anti-Momentum vs Smart
    if timing_results.get("anti_momentum_boost", {}).get("roi") and timing_results.get("smart_boost", {}).get("roi"):
        am = timing_results["anti_momentum_boost"]["roi"]
        st = timing_results["smart_boost"]["roi"]
        diff = st - am
        print(f"\nSmart vs Anti-Momentum:   {diff:+.2f}%")

        if diff > 5:
            print("\n>>> Smart Generator verbessert Anti-Momentum! <<<")
        elif diff < -5:
            print("\n>>> Anti-Momentum ist besser als Smart! <<<")
        else:
            print("\n>>> Kein signifikanter Unterschied - beide Strategien funktionieren <<<")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "top_20_zahlen": [
            {"zahl": s.zahl, "favorability": s.favorability, "kdi": s.kdi,
             "gas": s.gas, "pop": s.pop, "risk": s.risk_level}
            for s in scores[:20]
        ],
        "vermeiden_zahlen": [
            {"zahl": s.zahl, "kdi": s.kdi, "risk": s.risk_level}
            for s in scores[-15:]
        ],
        "timing_backtest": {
            strategy: {"roi": data.get("roi", 0), "games": data["cost"]}
            for strategy, data in timing_results.items()
        },
        "simple_backtest": {
            strategy: {"roi": data.get("roi", 0), "games": data["cost"]}
            for strategy, data in backtest_results.items()
        }
    }

    output_path = base_path / "results/smart_ticket_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
