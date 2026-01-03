#!/usr/bin/env python3
"""
POOL DASHBOARD: Interaktives Multi-Pool Tracking mit visuellen Effekten

Features:
- Visuelle Reife-Anzeige mit Fortschrittsbalken
- Treffer-Analyse: Welche Pool-Zahlen kamen in der Ziehung?
- Letzte Ziehung mit Hervorhebung
- Online-Update via KENO API
- Uebersichtliche Sektionen

Verwendung:
    python scripts/pool_dashboard.py              # Dashboard anzeigen
    python scripts/pool_dashboard.py --update     # Daten aktualisieren
    python scripts/pool_dashboard.py --add        # Neuen Pool hinzufuegen
    python scripts/pool_dashboard.py --interactive # Interaktiver Modus

Autor: Kenobase V2.5
Datum: 2026-01-03
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

# ============================================================================
# KONSTANTEN & FARBEN
# ============================================================================

# ANSI Farben fuer Terminal
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Farben
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Hintergrund
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"


def supports_color():
    """Prueft ob Terminal Farben unterstuetzt."""
    if os.name == 'nt':
        os.system('')  # Enable ANSI on Windows
        return True
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


USE_COLORS = supports_color()


def c(text: str, color: str) -> str:
    """Faerbt Text wenn Terminal Farben unterstuetzt."""
    if USE_COLORS:
        return f"{color}{text}{Colors.RESET}"
    return text


# Pool-Reife Konfiguration
POOL_RIPENESS = {
    0: {"prob": 0.00, "status": "NEU", "color": Colors.DIM, "bar_char": "░"},
    1: {"prob": 0.31, "status": "UNREIF", "color": Colors.RED, "bar_char": "░"},
    2: {"prob": 0.45, "status": "FRUEH", "color": Colors.YELLOW, "bar_char": "▒"},
    3: {"prob": 0.61, "status": "REIF", "color": Colors.CYAN, "bar_char": "▓"},
    4: {"prob": 0.76, "status": "OPTIMAL", "color": Colors.GREEN, "bar_char": "█"},
    5: {"prob": 0.85, "status": "SEHR_REIF", "color": Colors.GREEN, "bar_char": "█"},
    6: {"prob": 0.91, "status": "SEHR_REIF", "color": Colors.GREEN, "bar_char": "█"},
    7: {"prob": 0.94, "status": "MAXIMAL", "color": Colors.MAGENTA, "bar_char": "█"},
}

RIPE_WINDOW = (4, 7)

# Dateipfade
MULTI_POOL_FILE = Path(__file__).parent.parent / "results" / "multi_pool_state.json"

# Pool-Generierung
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}
BAD_PATTERNS = {"0010010", "1000111", "0101011", "1010000", "0001101", "0001000", "0100100", "0001010", "0000111"}


# ============================================================================
# VISUELLE ELEMENTE
# ============================================================================

def clear_screen():
    """Loescht den Bildschirm."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Zeigt den Dashboard-Header."""
    print()
    print(c("╔" + "═" * 78 + "╗", Colors.CYAN))
    print(c("║", Colors.CYAN) + c("  KENO POOL DASHBOARD", Colors.BOLD + Colors.WHITE).center(86) + c("║", Colors.CYAN))
    print(c("║", Colors.CYAN) + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + c("║", Colors.CYAN))
    print(c("╚" + "═" * 78 + "╝", Colors.CYAN))


def print_section(title: str, color: str = Colors.YELLOW):
    """Zeigt eine Sektions-Ueberschrift."""
    print()
    print(c("┌" + "─" * 78 + "┐", color))
    print(c("│", color) + c(f"  {title}", Colors.BOLD).ljust(86) + c("│", color))
    print(c("└" + "─" * 78 + "┘", color))


def create_progress_bar(value: float, width: int = 30, filled_char: str = "█", empty_char: str = "░") -> str:
    """Erstellt einen visuellen Fortschrittsbalken."""
    filled = int(value * width)
    empty = width - filled
    return filled_char * filled + empty_char * empty


def create_ripeness_bar(age: int, width: int = 20) -> str:
    """Erstellt einen farbigen Reife-Balken."""
    ripeness = POOL_RIPENESS.get(age, POOL_RIPENESS[7])
    prob = ripeness["prob"]
    color = ripeness["color"]

    filled = int(prob * width)
    empty = width - filled

    bar = c("█" * filled, color) + c("░" * empty, Colors.DIM)
    return f"[{bar}]"


def format_number_with_hit(num: int, hit_numbers: Set[int], pool_numbers: Set[int]) -> str:
    """Formatiert eine Zahl mit Treffer-Hervorhebung."""
    if num in hit_numbers and num in pool_numbers:
        # Treffer! Zahl war im Pool UND in Ziehung
        return c(f"★{num:2d}", Colors.GREEN + Colors.BOLD)
    elif num in hit_numbers:
        # In Ziehung aber nicht im Pool
        return c(f" {num:2d}", Colors.YELLOW)
    elif num in pool_numbers:
        # Im Pool aber nicht in Ziehung
        return c(f" {num:2d}", Colors.CYAN)
    else:
        return c(f" {num:2d}", Colors.DIM)


# ============================================================================
# DATEN LADEN
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


def get_last_drawing(df: pd.DataFrame) -> Dict:
    """Holt die letzte Ziehung."""
    last = df.iloc[-1]
    return {
        "date": last["Datum"],
        "numbers": last["numbers_set"],
        "numbers_sorted": sorted(last["numbers_set"]),
    }


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


# ============================================================================
# POOL GENERIERUNG
# ============================================================================

def get_draws_until_date(df: pd.DataFrame, until_date: datetime) -> List[Dict]:
    """Holt Ziehungen bis zu einem Datum."""
    filtered = df[df["Datum"] <= until_date]
    return [{"datum": row["Datum"], "zahlen": row["numbers_set"]} for _, row in filtered.iterrows()]


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws: List[Dict], number: int) -> int:
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
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def get_index(draws: List[Dict], number: int) -> int:
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number(draws: List[Dict], number: int, hot: Set[int]) -> float:
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
    """Generiert Pool mit Metadaten."""
    if len(draws) < 10:
        return set(), {}

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    cold_bd_scored = [(z, get_count(draws, z), score_number(draws, z, hot)) for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

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
    }
    return pool, metadata


def add_pool_for_date(df: pd.DataFrame, pool_date: datetime) -> Dict:
    """Generiert und speichert Pool."""
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

    state = load_multi_pool_state()
    state["pools"][pool_date.strftime("%Y-%m-%d")] = entry
    save_multi_pool_state(state)
    return entry


# ============================================================================
# API UPDATE (Optional)
# ============================================================================

def update_keno_data_online(base_path: Path, auto_save: bool = True) -> bool:
    """
    Aktualisiert KENO-Daten automatisch via Lotto Hessen API.

    Args:
        base_path: Projekt-Basispfad
        auto_save: Wenn True, wird CSV automatisch aktualisiert

    Returns:
        True wenn erfolgreich, False sonst
    """
    try:
        import requests
    except ImportError:
        print(c("  [!] requests nicht installiert. Ueberspringe Online-Update.", Colors.YELLOW))
        return False

    print(c("  [*] Versuche Online-Update...", Colors.CYAN))

    # Offizielle Lotto Hessen API
    api_url = "https://services.lotto-hessen.de/spielinformationen/gewinnzahlen/keno"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(c(f"  [✓] API-Antwort erhalten", Colors.GREEN))

            # Parse die Ziehungsdaten (Lotto Hessen Format)
            if isinstance(data, dict):
                numbers = data.get("Zahl", data.get("gewinnzahlen", []))
                draw_date_raw = data.get("Datum", data.get("datum", ""))
                weekday = data.get("Ziehung", "")

                # Konvertiere Datum von DD.MM.YYYY zu YYYY-MM-DD
                if "." in draw_date_raw:
                    parts = draw_date_raw.split(".")
                    draw_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                else:
                    draw_date = draw_date_raw

                if numbers:
                    print(c(f"  [✓] Ziehung vom {draw_date} ({weekday})", Colors.GREEN))
                    print(c(f"      Zahlen: {sorted(numbers)}", Colors.CYAN))

                    # Lade CSV und pruefe ob Update noetig
                    csv_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
                    if csv_path.exists():
                        df = pd.read_csv(csv_path, sep=";", decimal=",")
                        # Datum im Format DD.MM.YYYY
                        last_date = pd.to_datetime(df["Datum"], format="%d.%m.%Y").max().strftime("%Y-%m-%d")
                        print(c(f"  [i] Letzte Ziehung in CSV: {last_date}", Colors.DIM))

                        if draw_date > last_date:
                            print(c(f"  [!] Neue Ziehung verfuegbar!", Colors.YELLOW))

                            if auto_save:
                                # Automatisch zur CSV hinzufuegen
                                success = append_drawing_to_csv(
                                    csv_path, draw_date_raw, numbers
                                )
                                if success:
                                    print(c(f"  [✓] CSV automatisch aktualisiert!", Colors.GREEN + Colors.BOLD))
                                    return True
                                else:
                                    print(c(f"  [!] CSV-Update fehlgeschlagen", Colors.RED))
                                    return False
                            else:
                                print(c(f"  [i] Manuelles Update: --update --save", Colors.DIM))
                        else:
                            print(c(f"  [✓] CSV ist aktuell.", Colors.GREEN))

                    return True
                else:
                    print(c(f"  [!] Keine Zahlen in API-Antwort", Colors.YELLOW))
                    return False
            else:
                print(c(f"  [!] Unerwartetes Datenformat", Colors.YELLOW))
                return False
        else:
            print(c(f"  [!] API Status: {response.status_code}", Colors.YELLOW))
            return False
    except requests.exceptions.Timeout:
        print(c(f"  [!] API-Timeout (15s)", Colors.YELLOW))
        return False
    except requests.exceptions.RequestException as e:
        print(c(f"  [!] Netzwerk-Fehler: {str(e)[:40]}", Colors.YELLOW))
        return False
    except Exception as e:
        print(c(f"  [!] API-Fehler: {str(e)[:50]}", Colors.YELLOW))
        return False


def append_drawing_to_csv(csv_path: Path, date_str: str, numbers: List[int]) -> bool:
    """
    Fuegt eine neue Ziehung zur CSV-Datei hinzu.

    Args:
        csv_path: Pfad zur CSV-Datei
        date_str: Datum im Format DD.MM.YYYY
        numbers: Liste der 20 gezogenen Zahlen

    Returns:
        True wenn erfolgreich
    """
    try:
        # Erstelle neue Zeile im CSV-Format
        # Format: Datum;Z1;Z2;...;Z20;Plus5;Spieleinsatz
        numbers_sorted = numbers  # Behalte Original-Reihenfolge (wie gezogen)

        # Plus5 und Spieleinsatz sind nicht in der API - Platzhalter
        plus5 = ""  # Nicht verfuegbar
        spieleinsatz = ""  # Nicht verfuegbar

        # CSV-Zeile erstellen
        row_values = [date_str] + [str(n) for n in numbers_sorted] + [plus5, spieleinsatz]
        new_row = ";".join(row_values)

        # Backup erstellen
        backup_path = csv_path.with_suffix(".csv.bak")
        import shutil
        shutil.copy(csv_path, backup_path)
        print(c(f"  [i] Backup: {backup_path.name}", Colors.DIM))

        # Zeile anfuegen
        with open(csv_path, "a", encoding="utf-8") as f:
            f.write("\n" + new_row)

        print(c(f"  [+] Neue Zeile hinzugefuegt: {date_str}", Colors.GREEN))
        print(c(f"      Zahlen: {numbers_sorted}", Colors.CYAN))

        return True

    except Exception as e:
        print(c(f"  [!] Fehler beim Schreiben: {e}", Colors.RED))
        return False


# ============================================================================
# DASHBOARD ANZEIGE
# ============================================================================

def show_last_drawing(df: pd.DataFrame):
    """Zeigt die letzte Ziehung."""
    print_section("LETZTE ZIEHUNG", Colors.MAGENTA)

    last = get_last_drawing(df)
    numbers = last["numbers_sorted"]

    print()
    print(f"  Datum: {c(last['date'].strftime('%Y-%m-%d (%A)'), Colors.WHITE + Colors.BOLD)}")
    print()

    # Zahlen in Gruppen anzeigen
    print("  Gezogene Zahlen:")
    print()

    # Zeile 1: 1-10
    row1 = "  "
    for n in range(1, 11):
        if n in last["numbers"]:
            row1 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row1 += c(f" {n:2d} ", Colors.DIM)
    print(row1)

    # Zeile 2: 11-20
    row2 = "  "
    for n in range(11, 21):
        if n in last["numbers"]:
            row2 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row2 += c(f" {n:2d} ", Colors.DIM)
    print(row2)

    # Zeile 3: 21-30
    row3 = "  "
    for n in range(21, 31):
        if n in last["numbers"]:
            row3 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row3 += c(f" {n:2d} ", Colors.DIM)
    print(row3)

    # Zeile 4: 31-40
    row4 = "  "
    for n in range(31, 41):
        if n in last["numbers"]:
            row4 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row4 += c(f" {n:2d} ", Colors.DIM)
    print(row4)

    # Zeile 5: 41-50
    row5 = "  "
    for n in range(41, 51):
        if n in last["numbers"]:
            row5 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row5 += c(f" {n:2d} ", Colors.DIM)
    print(row5)

    # Zeile 6: 51-60
    row6 = "  "
    for n in range(51, 61):
        if n in last["numbers"]:
            row6 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row6 += c(f" {n:2d} ", Colors.DIM)
    print(row6)

    # Zeile 7: 61-70
    row7 = "  "
    for n in range(61, 71):
        if n in last["numbers"]:
            row7 += c(f" {n:2d} ", Colors.BG_GREEN + Colors.WHITE + Colors.BOLD)
        else:
            row7 += c(f" {n:2d} ", Colors.DIM)
    print(row7)

    # Statistik
    birthday_count = len([n for n in numbers if n <= 31])
    high_count = len([n for n in numbers if n > 31])

    print()
    print(f"  Birthday (1-31): {c(str(birthday_count), Colors.CYAN)}  |  Hohe (32-70): {c(str(high_count), Colors.YELLOW)}")


def show_pool_with_hits(pool_entry: Dict, age: int, last_drawing: Set[int]):
    """Zeigt einen Pool mit Treffer-Hervorhebung."""
    ripeness = POOL_RIPENESS.get(age, POOL_RIPENESS.get(7, POOL_RIPENESS[7]))
    color = ripeness["color"]
    status = ripeness["status"]
    prob = ripeness["prob"]

    pool_numbers = set(pool_entry.get("numbers", []))
    hits = pool_numbers & last_drawing
    hit_count = len(hits)

    # Treffer-Farbe
    if hit_count >= 8:
        hit_color = Colors.GREEN + Colors.BOLD
        hit_text = "SUPER!"
    elif hit_count >= 6:
        hit_color = Colors.GREEN
        hit_text = "GUT!"
    elif hit_count >= 4:
        hit_color = Colors.YELLOW
        hit_text = "OK"
    else:
        hit_color = Colors.RED
        hit_text = "WENIG"

    # Pool-Header
    date_str = pool_entry.get("created_date", "?")
    bar = create_ripeness_bar(age)

    print()
    print(f"  {c('┌' + '─' * 74 + '┐', color)}")
    print(f"  {c('│', color)} Pool vom {c(date_str, Colors.WHITE + Colors.BOLD)}  "
          f"Tag {c(str(age), color + Colors.BOLD)}  {bar} {c(f'{prob*100:.0f}%', color)}  "
          f"{c(status, color + Colors.BOLD):<12}{c('│', color)}")
    print(f"  {c('├' + '─' * 74 + '┤', color)}")

    # Treffer-Zeile
    print(f"  {c('│', color)} Treffer: {c(f'{hit_count}/20', hit_color)} ({hit_text})  "
          f"Pool-Groesse: {len(pool_numbers)} Zahlen{' ' * 30}{c('│', color)}")
    print(f"  {c('├' + '─' * 74 + '┤', color)}")

    # Zahlen mit Treffer-Hervorhebung
    numbers_row = "  " + c("│", color) + " "
    for num in sorted(pool_numbers):
        if num in hits:
            numbers_row += c(f"★{num:2d}", Colors.GREEN + Colors.BOLD) + " "
        else:
            numbers_row += c(f" {num:2d}", Colors.CYAN) + " "

    # Padding
    padding_needed = 74 - (len(pool_numbers) * 4 + 1)
    numbers_row += " " * max(0, padding_needed) + c("│", color)
    print(numbers_row)

    # Treffer-Liste
    if hits:
        hits_str = ", ".join(str(h) for h in sorted(hits))
        print(f"  {c('│', color)} {c('TREFFER:', Colors.GREEN)} {hits_str:<60}{c('│', color)}")

    # Metadaten
    meta = pool_entry.get("metadata", {})
    if meta:
        print(f"  {c('├' + '─' * 74 + '┤', color)}")
        hot = meta.get("hot_numbers", [])
        cold_bd = meta.get("cold_birthday", [])
        cold_nbd = meta.get("cold_non_birthday", [])

        # Hot-Treffer
        hot_hits = [n for n in hot if n in last_drawing]
        print(f"  {c('│', color)} Hot ({len(hot_hits)}/{len(hot)}): {c(str(hot), Colors.RED):<50}{c('│', color)}")

        # Cold Birthday-Treffer
        bd_hits = [n for n in cold_bd if n in last_drawing]
        print(f"  {c('│', color)} Cold BD ({len(bd_hits)}/{len(cold_bd)}): {c(str(cold_bd), Colors.YELLOW):<46}{c('│', color)}")

        # Cold Non-BD-Treffer
        nbd_hits = [n for n in cold_nbd if n in last_drawing]
        print(f"  {c('│', color)} Cold Non-BD ({len(nbd_hits)}/{len(cold_nbd)}): {c(str(cold_nbd), Colors.BLUE):<42}{c('│', color)}")

    print(f"  {c('└' + '─' * 74 + '┘', color)}")


def show_ripe_pools(df: pd.DataFrame):
    """Zeigt alle reifen Pools mit Treffer-Analyse."""
    print_section("REIFE POOLS (Tag 4-7)", Colors.GREEN)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    state = load_multi_pool_state()
    last_drawing = get_last_drawing(df)["numbers"]

    ripe_pools = []

    for date_str, pool_entry in state.get("pools", {}).items():
        try:
            pool_date = datetime.strptime(date_str, "%Y-%m-%d")
            age = (today - pool_date).days

            if RIPE_WINDOW[0] <= age <= RIPE_WINDOW[1]:
                ripe_pools.append((age, pool_entry))
        except ValueError:
            continue

    if not ripe_pools:
        print()
        print(c("  Keine reifen Pools vorhanden!", Colors.YELLOW))
        print(c("  Generiere Pools mit: python pool_dashboard.py --init", Colors.DIM))
        return []

    # Sortieren nach Alter (aelteste zuerst = hoechste Reife)
    ripe_pools.sort(key=lambda x: x[0], reverse=True)

    for age, pool_entry in ripe_pools:
        show_pool_with_hits(pool_entry, age, last_drawing)

    return ripe_pools


def show_all_pools(df: pd.DataFrame):
    """Zeigt ALLE Pools (nicht nur reife)."""
    print_section("ALLE POOLS", Colors.CYAN)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    state = load_multi_pool_state()
    last_drawing = get_last_drawing(df)["numbers"]

    pools = []
    for date_str, pool_entry in state.get("pools", {}).items():
        try:
            pool_date = datetime.strptime(date_str, "%Y-%m-%d")
            age = (today - pool_date).days
            pools.append((age, pool_entry))
        except ValueError:
            continue

    if not pools:
        print()
        print(c("  Keine Pools vorhanden!", Colors.YELLOW))
        return

    pools.sort(key=lambda x: x[0])

    print()
    print(f"  {'Datum':<12} {'Tag':>4} {'Reife':<22} {'Prob':>6} {'Treffer':>8} {'Status':<10}")
    print(f"  {'-'*12} {'-'*4} {'-'*22} {'-'*6} {'-'*8} {'-'*10}")

    for age, pool_entry in pools:
        date_str = pool_entry.get("created_date", "?")
        ripeness = POOL_RIPENESS.get(age, POOL_RIPENESS.get(7, {"prob": 0.94, "status": "ALT", "color": Colors.DIM}))

        pool_numbers = set(pool_entry.get("numbers", []))
        hits = len(pool_numbers & last_drawing)

        bar = create_progress_bar(ripeness["prob"], width=15)

        is_ripe = RIPE_WINDOW[0] <= age <= RIPE_WINDOW[1]
        marker = c("★ REIF", Colors.GREEN) if is_ripe else ""

        color = ripeness["color"]
        status = ripeness["status"]

        print(f"  {date_str:<12} {age:>4} [{c(bar, color)}] {ripeness['prob']*100:>5.0f}% {hits:>8} {c(status, color):<10} {marker}")


def show_overlap_analysis(df: pd.DataFrame, ripe_pools: List):
    """Zeigt Ueberlappungs-Analyse."""
    print_section("POOL-UEBERLAPPUNG VS LETZTE ZIEHUNG", Colors.YELLOW)

    if not ripe_pools:
        print()
        print(c("  Keine reifen Pools fuer Analyse!", Colors.YELLOW))
        return

    last_drawing = get_last_drawing(df)["numbers"]

    # Zahlen sammeln
    all_pool_numbers = set()
    number_counts = defaultdict(int)

    for age, pool_entry in ripe_pools:
        pool_nums = set(pool_entry.get("numbers", []))
        all_pool_numbers.update(pool_nums)
        for n in pool_nums:
            number_counts[n] += 1

    # Zahlen in allen Pools
    common_all = [n for n, c in number_counts.items() if c == len(ripe_pools)]
    common_most = [n for n, c in number_counts.items() if c >= len(ripe_pools) - 1]

    # Treffer in gemeinsamen Zahlen
    common_hits = set(common_all) & last_drawing

    print()
    print(f"  Zahlen in {c('ALLEN', Colors.BOLD)} Pools ({len(common_all)}): {c(str(sorted(common_all)), Colors.CYAN)}")
    print(f"  Davon in letzter Ziehung: {c(str(sorted(common_hits)), Colors.GREEN + Colors.BOLD)}")
    print()

    if common_hits:
        hit_rate = len(common_hits) / len(common_all) * 100 if common_all else 0
        print(f"  >>> {c('TREFFER-QUOTE:', Colors.GREEN)} {len(common_hits)}/{len(common_all)} = {hit_rate:.1f}%")
    else:
        print(f"  >>> {c('Keine Treffer in gemeinsamen Zahlen', Colors.YELLOW)}")

    print()
    print(f"  Zahlen in {c('MEISTEN', Colors.BOLD)} Pools: {c(str(sorted(common_most)), Colors.YELLOW)}")

    # Matrix-Ansicht
    print()
    print(f"  {c('ZAHLEN-MATRIX:', Colors.BOLD)}")
    print()

    header = "  Zahl │"
    for age, _ in sorted(ripe_pools, key=lambda x: x[0]):
        header += f" T{age} │"
    header += " ZIEH │"
    print(header)
    print("  " + "─" * (7 + len(ripe_pools) * 5 + 7))

    for num in sorted(all_pool_numbers):
        row = f"  {num:4d} │"
        for age, pool_entry in sorted(ripe_pools, key=lambda x: x[0]):
            if num in pool_entry.get("numbers", []):
                row += c("  ● ", Colors.CYAN) + "│"
            else:
                row += "    │"

        # Ziehungs-Spalte
        if num in last_drawing:
            row += c("  ★ ", Colors.GREEN + Colors.BOLD) + "│"
        else:
            row += "    │"

        print(row)


def show_summary():
    """Zeigt Zusammenfassung und Empfehlungen."""
    print_section("EMPFEHLUNG", Colors.MAGENTA)

    print()
    print(f"  {c('POOL-REIFE GUIDE:', Colors.BOLD)}")
    print()

    for day in range(0, 8):
        rip = POOL_RIPENESS.get(day, POOL_RIPENESS[7])
        bar = create_ripeness_bar(day, 15)

        if day == 4:
            marker = c(" ← OPTIMAL!", Colors.GREEN + Colors.BOLD)
        elif 4 <= day <= 7:
            marker = c(" ← SPIELEN", Colors.GREEN)
        elif day <= 2:
            marker = c(" ← WARTEN", Colors.YELLOW)
        else:
            marker = ""

        print(f"    Tag {day}: {bar} {rip['prob']*100:5.1f}%  {c(rip['status'], rip['color']):<10}{marker}")

    print()
    print(f"  {c('LEGENDE:', Colors.BOLD)}")
    print(f"    {c('★', Colors.GREEN + Colors.BOLD)} = Treffer (Pool-Zahl in Ziehung)")
    print(f"    {c('●', Colors.CYAN)} = Im Pool")
    print(f"    {c('█', Colors.GREEN)} = Reife (je voller, desto reifer)")


# ============================================================================
# INTERAKTIVER MODUS
# ============================================================================

def interactive_mode(df: pd.DataFrame, base_path: Path):
    """Interaktiver Dashboard-Modus."""
    while True:
        clear_screen()
        print_header()

        print()
        print(f"  {c('MENU:', Colors.BOLD)}")
        print(f"    [1] Dashboard anzeigen")
        print(f"    [2] Neuen Pool hinzufuegen")
        print(f"    [3] Pools initialisieren (letzte 7 Tage)")
        print(f"    [4] Alle Pools anzeigen")
        print(f"    [5] Online-Update versuchen")
        print(f"    [q] Beenden")
        print()

        choice = input(f"  {c('Auswahl:', Colors.CYAN)} ").strip().lower()

        if choice == 'q':
            print()
            print(c("  Auf Wiedersehen!", Colors.GREEN))
            break
        elif choice == '1':
            clear_screen()
            print_header()
            show_last_drawing(df)
            ripe_pools = show_ripe_pools(df)
            show_overlap_analysis(df, ripe_pools)
            show_summary()
            input(f"\n  {c('Enter druecken zum Fortfahren...', Colors.DIM)}")
        elif choice == '2':
            print()
            entry = add_pool_for_date(df, datetime.now())
            if entry:
                print(c(f"  [✓] Pool hinzugefuegt: {entry['size']} Zahlen", Colors.GREEN))
            else:
                print(c("  [!] Fehler beim Hinzufuegen", Colors.RED))
            input(f"\n  {c('Enter druecken zum Fortfahren...', Colors.DIM)}")
        elif choice == '3':
            print()
            print(c("  Initialisiere Pools...", Colors.CYAN))
            today = datetime.now()
            for days_ago in range(7, -1, -1):
                pool_date = today - timedelta(days=days_ago)
                entry = add_pool_for_date(df, pool_date)
                status = c("OK", Colors.GREEN) if entry else c("FEHLER", Colors.RED)
                print(f"    {pool_date.strftime('%Y-%m-%d')}: {status}")
            input(f"\n  {c('Enter druecken zum Fortfahren...', Colors.DIM)}")
        elif choice == '4':
            clear_screen()
            print_header()
            show_all_pools(df)
            input(f"\n  {c('Enter druecken zum Fortfahren...', Colors.DIM)}")
        elif choice == '5':
            print()
            update_keno_data_online(base_path)
            input(f"\n  {c('Enter druecken zum Fortfahren...', Colors.DIM)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Pool Dashboard: Interaktives Multi-Pool Tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--show", action="store_true", help="Dashboard anzeigen")
    parser.add_argument("--add", action="store_true", help="Neuen Pool hinzufuegen")
    parser.add_argument("--init", action="store_true", help="Pools fuer letzte 7 Tage")
    parser.add_argument("--all", action="store_true", help="Alle Pools anzeigen")
    parser.add_argument("--update", action="store_true", help="Online-Update versuchen")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interaktiver Modus")

    args = parser.parse_args()

    base_path = Path(__file__).parent.parent

    # Daten laden
    print(c("Lade KENO-Daten...", Colors.DIM))
    df = load_keno_data(base_path)
    print(c(f"  {len(df)} Ziehungen geladen", Colors.DIM))

    # Interaktiver Modus
    if args.interactive:
        interactive_mode(df, base_path)
        return

    # Online-Update
    if args.update:
        update_keno_data_online(base_path)

    # Pool hinzufuegen
    if args.add:
        entry = add_pool_for_date(df, datetime.now())
        if entry:
            print(c(f"[✓] Pool hinzugefuegt: {entry['size']} Zahlen", Colors.GREEN))

    # Initialisieren
    if args.init:
        print(c("Initialisiere Pools...", Colors.CYAN))
        today = datetime.now()
        for days_ago in range(7, -1, -1):
            pool_date = today - timedelta(days=days_ago)
            entry = add_pool_for_date(df, pool_date)
            status = c("OK", Colors.GREEN) if entry else c("FEHLER", Colors.RED)
            print(f"  {pool_date.strftime('%Y-%m-%d')}: {status}")

    # Alle Pools
    if args.all:
        print_header()
        show_all_pools(df)
        return

    # Default: Dashboard
    if args.show or not any([args.add, args.init, args.all, args.update, args.interactive]):
        print_header()
        show_last_drawing(df)
        ripe_pools = show_ripe_pools(df)
        show_overlap_analysis(df, ripe_pools)
        show_summary()


if __name__ == "__main__":
    main()
