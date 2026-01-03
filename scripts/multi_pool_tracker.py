#!/usr/bin/env python3
"""
MULTI-POOL TRACKER: Mehrere Pools gleichzeitig verwalten

Konzept:
- Jeden Tag wird ein neuer Pool generiert und gespeichert
- Pools im "reifen" Fenster (Tag 4-7) werden angezeigt
- An jedem Tag gibt es bis zu 4 "reife" Pools zur Auswahl

Beispiel:
  Heute ist Tag X. Folgende Pools sind "reif":
  - Pool von Tag X-4: jetzt Tag 4 (OPTIMAL - 76%)
  - Pool von Tag X-5: jetzt Tag 5 (SEHR_REIF - 85%)
  - Pool von Tag X-6: jetzt Tag 6 (SEHR_REIF - 91%)
  - Pool von Tag X-7: jetzt Tag 7 (MAXIMAL - 94%)

Verwendung:
    # Neuen Pool fuer heute generieren und speichern
    python scripts/multi_pool_tracker.py --add

    # Alle reifen Pools anzeigen
    python scripts/multi_pool_tracker.py --show

    # Vergleich aller reifen Pools
    python scripts/multi_pool_tracker.py --compare

    # Alte Pools bereinigen (aelter als 7 Tage)
    python scripts/multi_pool_tracker.py --cleanup

Autor: Kenobase V2.5
Datum: 2026-01-03
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

# ============================================================================
# KONSTANTEN
# ============================================================================

MULTI_POOL_FILE = Path(__file__).parent.parent / "results" / "multi_pool_state.json"

# Pool-Reife Wahrscheinlichkeiten (kumulativ)
POOL_RIPENESS = {
    1: {"probability": 0.31, "status": "UNREIF", "recommendation": "Nicht spielen"},
    2: {"probability": 0.45, "status": "FRUEH", "recommendation": "Noch warten"},
    3: {"probability": 0.61, "status": "REIF", "recommendation": "Spielbereit"},
    4: {"probability": 0.76, "status": "OPTIMAL", "recommendation": "Beste Zeit!"},
    5: {"probability": 0.85, "status": "SEHR_REIF", "recommendation": "Sehr gut"},
    6: {"probability": 0.91, "status": "SEHR_REIF", "recommendation": "Sehr gut"},
    7: {"probability": 0.94, "status": "MAXIMAL", "recommendation": "Letzte Chance"},
}

# Reifes Fenster
RIPE_WINDOW = (4, 7)  # Tag 4 bis Tag 7

# Pool-Generierung Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}
BAD_PATTERNS = {"0010010", "1000111", "0101011", "1010000", "0001101", "0001000", "0100100", "0001010", "0000111"}


# ============================================================================
# POOL GENERIERUNG (aus daily_recommendation.py)
# ============================================================================

def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    if not keno_path.exists():
        keno_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8-sig")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_draws_until_date(df: pd.DataFrame, until_date: datetime) -> List[Dict]:
    """Konvertiert DataFrame bis zu einem bestimmten Datum in Liste von Dicts."""
    filtered = df[df["Datum"] <= until_date]
    draws = []
    for _, row in filtered.iterrows():
        draws.append({
            "datum": row["Datum"],
            "zahlen": row["numbers_set"]
        })
    return draws


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    """Ermittelt 'heisse' Zahlen."""
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    """Zaehlt Erscheinungen."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws: List[Dict], number: int) -> int:
    """Berechnet Streak."""
    if not draws:
        return 0
    streak = 0
    in_last = number in draws[-1]["zahlen"]
    for draw in reversed(draws):
        if (number in draw["zahlen"]) == in_last:
            streak += 1
        else:
            break
    return streak if in_last else -streak


def get_pattern_7(draws: List[Dict], number: int) -> str:
    """7-Tage Pattern."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    """Durchschnittlicher Abstand."""
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def get_index(draws: List[Dict], number: int) -> int:
    """Index (Tage seit letztem Erscheinen)."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number(draws: List[Dict], number: int, hot: Set[int]) -> float:
    """Score fuer Pool-Aufnahme."""
    score = 50.0
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    streak = get_streak(draws, number)
    if streak >= 3:
        score -= 10
    elif 0 < streak <= 2:
        score += 5
    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5
    index = get_index(draws, number)
    if 3 <= index <= 6:
        score += 5
    return score


def build_pool(draws: List[Dict]) -> Tuple[Set[int], Dict]:
    """
    Generiert Pool mit Metadaten.

    Returns:
        (pool_numbers, metadata)
    """
    if len(draws) < 10:
        return set(), {}

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # Hot-Zahlen
    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    # Kalte Birthday-Zahlen
    cold_bd_scored = [(z, get_count(draws, z), score_number(draws, z, hot)) for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    # Kalte Non-Birthday-Zahlen
    cold_nbd_scored = [(z, get_count(draws, z), score_number(draws, z, hot)) for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    pool = hot_keep | cold_bd_keep | cold_nbd_keep

    metadata = {
        "hot_numbers": sorted(hot_keep),
        "cold_birthday": sorted(cold_bd_keep),
        "cold_non_birthday": sorted(cold_nbd_keep),
        "total_hot_available": len(hot_filtered),
        "draws_used": len(draws),
        "last_draw_date": draws[-1]["datum"].strftime("%Y-%m-%d") if draws else None,
    }

    return pool, metadata


# ============================================================================
# MULTI-POOL STORAGE
# ============================================================================

def load_multi_pool_state() -> Dict:
    """Laedt gespeicherte Pools."""
    if not MULTI_POOL_FILE.exists():
        return {"pools": {}}

    try:
        with open(MULTI_POOL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"pools": {}}


def save_multi_pool_state(state: Dict):
    """Speichert Pool-State."""
    MULTI_POOL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MULTI_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False, default=str)


def add_pool_for_date(df: pd.DataFrame, pool_date: datetime) -> Dict:
    """
    Generiert und speichert einen Pool fuer ein bestimmtes Datum.

    Args:
        df: KENO DataFrame
        pool_date: Datum fuer den Pool

    Returns:
        Pool-Eintrag mit Metadaten
    """
    # Ziehungen bis zum Pool-Datum
    draws = get_draws_until_date(df, pool_date)

    if not draws:
        return None

    pool, metadata = build_pool(draws)

    if not pool:
        return None

    entry = {
        "created_date": pool_date.strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(),
        "numbers": sorted(pool),
        "size": len(pool),
        "metadata": metadata,
    }

    # State laden und aktualisieren
    state = load_multi_pool_state()
    state["pools"][pool_date.strftime("%Y-%m-%d")] = entry
    save_multi_pool_state(state)

    return entry


def get_ripe_pools(today: datetime = None) -> List[Dict]:
    """
    Gibt alle Pools zurueck die im reifen Fenster (Tag 4-7) liegen.

    Returns:
        Liste von Pool-Eintraegen mit Alter und Reife-Info
    """
    if today is None:
        today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)

    state = load_multi_pool_state()
    ripe_pools = []

    for date_str, pool_entry in state.get("pools", {}).items():
        try:
            pool_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        age = (today - pool_date).days

        # Nur Pools im reifen Fenster
        if RIPE_WINDOW[0] <= age <= RIPE_WINDOW[1]:
            ripeness = POOL_RIPENESS.get(age, POOL_RIPENESS[7])

            ripe_pools.append({
                "date": date_str,
                "age_days": age,
                "numbers": pool_entry.get("numbers", []),
                "size": pool_entry.get("size", 0),
                "probability": ripeness["probability"],
                "status": ripeness["status"],
                "recommendation": ripeness["recommendation"],
                "metadata": pool_entry.get("metadata", {}),
            })

    # Nach Alter sortieren (aelteste = hoechste Reife zuerst)
    ripe_pools.sort(key=lambda x: x["age_days"], reverse=True)

    return ripe_pools


def cleanup_old_pools(max_age: int = 10):
    """Entfernt Pools die aelter als max_age Tage sind."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    state = load_multi_pool_state()

    removed = []
    new_pools = {}

    for date_str, pool_entry in state.get("pools", {}).items():
        try:
            pool_date = datetime.strptime(date_str, "%Y-%m-%d")
            age = (today - pool_date).days

            if age <= max_age:
                new_pools[date_str] = pool_entry
            else:
                removed.append(date_str)
        except ValueError:
            continue

    state["pools"] = new_pools
    save_multi_pool_state(state)

    return removed


def get_pool_overlap(pools: List[Dict]) -> Dict:
    """Berechnet Ueberlappungen zwischen Pools."""
    if len(pools) < 2:
        return {}

    all_numbers = set()
    for p in pools:
        all_numbers.update(p["numbers"])

    # Zahlen die in mehreren Pools vorkommen
    number_counts = defaultdict(int)
    for p in pools:
        for n in p["numbers"]:
            number_counts[n] += 1

    common_all = [n for n, c in number_counts.items() if c == len(pools)]
    common_most = [n for n, c in number_counts.items() if c >= len(pools) - 1]

    return {
        "total_unique": len(all_numbers),
        "common_in_all": sorted(common_all),
        "common_in_most": sorted(common_most),
        "number_frequency": dict(number_counts),
    }


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def print_ripe_pools(ripe_pools: List[Dict], show_overlap: bool = True):
    """Zeigt alle reifen Pools an."""

    print("\n" + "=" * 80)
    print("  MULTI-POOL TRACKER: Reife Pools (Tag 4-7)")
    print("=" * 80)

    if not ripe_pools:
        print("\n  Keine reifen Pools vorhanden!")
        print("  Generiere Pools mit: python multi_pool_tracker.py --add")
        print("=" * 80)
        return

    print(f"\n  Heute: {datetime.now().strftime('%Y-%m-%d (%A)')}")
    print(f"  Reife Pools: {len(ripe_pools)}")

    print("\n" + "-" * 80)

    for pool in ripe_pools:
        age = pool["age_days"]
        prob = pool["probability"]
        status = pool["status"]

        # Fortschrittsbalken
        bar_filled = int(prob * 20)
        bar_empty = 20 - bar_filled
        bar = "█" * bar_filled + "░" * bar_empty

        print(f"\n  POOL vom {pool['date']} (Tag {age})")
        print(f"  ┌{'─' * 50}┐")
        print(f"  │ Reife: [{bar}] {prob*100:.0f}%{' ' * (50 - 30)}│")
        print(f"  │ Status: {status:<15} {pool['recommendation']:<23}│")
        print(f"  │ Zahlen ({pool['size']}): {str(pool['numbers'][:10])[:40]:<40}│")
        if pool['size'] > 10:
            print(f"  │          {str(pool['numbers'][10:]):<48}│")
        print(f"  └{'─' * 50}┘")

        # Metadaten
        meta = pool.get("metadata", {})
        if meta:
            print(f"    Hot: {meta.get('hot_numbers', [])}")
            print(f"    Cold Birthday: {meta.get('cold_birthday', [])}")
            print(f"    Cold Non-BD: {meta.get('cold_non_birthday', [])}")

    # Ueberlappung
    if show_overlap and len(ripe_pools) > 1:
        print("\n" + "-" * 80)
        print("  POOL-UEBERLAPPUNG:")
        overlap = get_pool_overlap(ripe_pools)

        print(f"\n  Zahlen in ALLEN Pools ({len(overlap['common_in_all'])}): {overlap['common_in_all']}")
        print(f"  Zahlen in MEISTEN Pools: {overlap['common_in_most']}")

        # Empfehlung basierend auf Ueberlappung
        if overlap['common_in_all']:
            print(f"\n  >>> EMPFEHLUNG: Diese Zahlen erscheinen in allen reifen Pools!")
            print(f"  >>> Hoechste Konsistenz: {overlap['common_in_all']}")

    print("\n" + "=" * 80)


def print_pool_comparison(ripe_pools: List[Dict]):
    """Vergleicht alle reifen Pools nebeneinander."""

    print("\n" + "=" * 80)
    print("  POOL-VERGLEICH: Alle reifen Pools")
    print("=" * 80)

    if not ripe_pools:
        print("\n  Keine reifen Pools zum Vergleichen!")
        return

    # Alle Zahlen sammeln
    all_numbers = set()
    for p in ripe_pools:
        all_numbers.update(p["numbers"])

    # Header
    header = "  Zahl │"
    for p in ripe_pools:
        header += f" Tag {p['age_days']} │"
    print("\n" + header)
    print("  " + "─" * (6 + len(ripe_pools) * 7))

    # Zahlen-Matrix
    for num in sorted(all_numbers):
        row = f"  {num:4d} │"
        for p in ripe_pools:
            if num in p["numbers"]:
                row += "   ●  │"
            else:
                row += "      │"
        print(row)

    print("  " + "─" * (6 + len(ripe_pools) * 7))

    # Legende
    print(f"\n  Legende:")
    for p in ripe_pools:
        print(f"    Tag {p['age_days']}: Pool vom {p['date']} ({p['status']}, {p['probability']*100:.0f}%)")

    print("\n" + "=" * 80)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Pool Tracker: Mehrere Pools gleichzeitig verwalten",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
KONZEPT:
  Jeden Tag wird ein neuer Pool generiert.
  An jedem Tag sind bis zu 4 Pools im "reifen" Fenster (Tag 4-7):

  - Pool von vor 4 Tagen: Tag 4 (OPTIMAL - 76%)
  - Pool von vor 5 Tagen: Tag 5 (SEHR_REIF - 85%)
  - Pool von vor 6 Tagen: Tag 6 (SEHR_REIF - 91%)
  - Pool von vor 7 Tagen: Tag 7 (MAXIMAL - 94%)

BEISPIELE:
  # Neuen Pool fuer heute generieren
  python multi_pool_tracker.py --add

  # Pool fuer bestimmtes Datum generieren
  python multi_pool_tracker.py --add --date 2025-12-30

  # Pools fuer die letzten 7 Tage generieren
  python multi_pool_tracker.py --init

  # Alle reifen Pools anzeigen
  python multi_pool_tracker.py --show

  # Pools vergleichen
  python multi_pool_tracker.py --compare

  # Alte Pools bereinigen
  python multi_pool_tracker.py --cleanup
        """
    )

    parser.add_argument("--add", action="store_true",
                        help="Neuen Pool fuer heute (oder --date) generieren")
    parser.add_argument("--date", type=str, default=None,
                        help="Datum fuer Pool (YYYY-MM-DD)")
    parser.add_argument("--init", action="store_true",
                        help="Pools fuer die letzten 7 Tage generieren")
    parser.add_argument("--show", action="store_true",
                        help="Alle reifen Pools anzeigen")
    parser.add_argument("--compare", action="store_true",
                        help="Pools nebeneinander vergleichen")
    parser.add_argument("--cleanup", action="store_true",
                        help="Alte Pools entfernen (aelter als 10 Tage)")
    parser.add_argument("--list", action="store_true",
                        help="Alle gespeicherten Pools auflisten")

    args = parser.parse_args()

    base_path = Path(__file__).parent.parent

    # Default: --show wenn keine Aktion angegeben
    if not any([args.add, args.init, args.show, args.compare, args.cleanup, args.list]):
        args.show = True

    # Daten laden
    print("Lade KENO-Daten...")
    df = load_keno_data(base_path)
    print(f"  Ziehungen: {len(df)}")
    print(f"  Letzte: {df['Datum'].max().date()}")

    # Aktionen
    if args.add:
        if args.date:
            try:
                pool_date = datetime.strptime(args.date, "%Y-%m-%d")
            except ValueError:
                print("Fehler: --date muss im Format YYYY-MM-DD sein")
                return
        else:
            pool_date = datetime.now()

        print(f"\nGeneriere Pool fuer {pool_date.strftime('%Y-%m-%d')}...")
        entry = add_pool_for_date(df, pool_date)

        if entry:
            print(f"  Pool gespeichert: {entry['size']} Zahlen")
            print(f"  Zahlen: {entry['numbers']}")
        else:
            print("  Fehler beim Generieren des Pools")

    if args.init:
        print("\nGeneriere Pools fuer die letzten 7 Tage...")
        today = datetime.now()

        for days_ago in range(7, -1, -1):
            pool_date = today - timedelta(days=days_ago)
            print(f"  {pool_date.strftime('%Y-%m-%d')}...", end=" ")
            entry = add_pool_for_date(df, pool_date)
            if entry:
                print(f"OK ({entry['size']} Zahlen)")
            else:
                print("Fehler")

    if args.cleanup:
        print("\nBereinige alte Pools...")
        removed = cleanup_old_pools(max_age=10)
        if removed:
            print(f"  Entfernt: {removed}")
        else:
            print("  Keine alten Pools gefunden")

    if args.list:
        state = load_multi_pool_state()
        pools = state.get("pools", {})

        print(f"\n{'=' * 60}")
        print(f"  ALLE GESPEICHERTEN POOLS ({len(pools)})")
        print(f"{'=' * 60}")

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for date_str in sorted(pools.keys(), reverse=True):
            pool = pools[date_str]
            try:
                pool_date = datetime.strptime(date_str, "%Y-%m-%d")
                age = (today - pool_date).days
            except ValueError:
                age = "?"

            ripeness = POOL_RIPENESS.get(age, {"status": "?", "probability": 0})
            status = ripeness.get("status", "?")
            prob = ripeness.get("probability", 0)

            ripe_marker = " ★ REIF" if RIPE_WINDOW[0] <= age <= RIPE_WINDOW[1] else ""

            print(f"  {date_str} | Tag {age:2} | {status:<10} | {prob*100:5.1f}% | {pool.get('size', 0)} Zahlen{ripe_marker}")

    if args.show:
        ripe_pools = get_ripe_pools()
        print_ripe_pools(ripe_pools)

    if args.compare:
        ripe_pools = get_ripe_pools()
        print_pool_comparison(ripe_pools)


if __name__ == "__main__":
    main()
