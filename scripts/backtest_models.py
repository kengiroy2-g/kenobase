#!/usr/bin/env python
"""Backtest beider Zahlengruppen-Modelle gegen echte KENO Ziehungen.

Vergleicht:
- V1: group_recommendations.json (Jackpot/Near-Miss/Balanced Strategien)
- V2: all_class_groups.json (Pair-fokussiert, alle Gewinnklassen)

KENO Gewinnklassen:
- Typ 10: 10/10=GK1, 9/10=GK2, 8/10=GK3, 7/10=GK4, 6/10=GK5, 5/10=GK6, 0/10=GK7
- Typ 9:  9/9=GK1, 8/9=GK2, 7/9=GK3, 6/9=GK4, 5/9=GK5, 0/9=GK6
- ...usw.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE, get_fixed_quote

# Gewinnklassen-Labels aus dem offiziellen Fixed-Quote-Table ableiten.
_GK_LABELS_BY_TYPE: dict[int, dict[int, str]] = {}
for _keno_type, _hits_to_quote in KENO_FIXED_QUOTES_BY_TYPE.items():
    ordered = sorted(_hits_to_quote.keys(), reverse=True)
    _GK_LABELS_BY_TYPE[int(_keno_type)] = {int(h): f"GK{i+1}" for i, h in enumerate(ordered)}


@dataclass
class DrawResult:
    """Ergebnis einer einzelnen Ziehungs-Auswertung."""
    date: datetime
    drawn_numbers: set[int]
    group_numbers: set[int]
    hits: int
    keno_typ: int
    gewinnklasse: Optional[str]
    quote: int


@dataclass
class ModelStats:
    """Aggregierte Statistiken fuer ein Modell."""
    model_name: str
    strategy: str
    keno_typ: int
    total_draws: int = 0
    total_hits: int = 0
    avg_hits: float = 0.0
    hit_distribution: dict[int, int] = field(default_factory=dict)
    gewinnklassen: dict[str, int] = field(default_factory=dict)
    total_winnings: int = 0  # Bei 1 Euro Einsatz
    roi: float = 0.0


def load_keno_draws(data_path: Path) -> list[tuple[datetime, set[int]]]:
    """Laedt KENO Ziehungen aus CSV."""
    draws = []

    df = pd.read_csv(data_path, sep=";", encoding="utf-8")

    for _, row in df.iterrows():
        try:
            date_str = row["Datum"]
            date = datetime.strptime(date_str, "%d.%m.%Y")

            numbers = set()
            for i in range(1, 21):
                col = f"Keno_Z{i}"
                if col in row and pd.notna(row[col]):
                    numbers.add(int(row[col]))

            if len(numbers) == 20:
                draws.append((date, numbers))
        except (ValueError, KeyError):
            continue

    return draws


def load_v1_model(results_dir: Path) -> dict:
    """Laedt V1 Modell (group_recommendations.json)."""
    path = results_dir / "group_recommendations.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_v2_model(results_dir: Path) -> dict:
    """Laedt V2 Modell (all_class_groups.json)."""
    path = results_dir / "all_class_groups.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_hits(group: set[int], drawn: set[int]) -> int:
    """Berechnet Anzahl Treffer."""
    return len(group & drawn)


def get_gewinnklasse(keno_typ: int, hits: int) -> tuple[Optional[str], int]:
    """Bestimmt Gewinnklasse und Quote."""
    if int(keno_typ) not in _GK_LABELS_BY_TYPE:
        return None, 0

    quote = get_fixed_quote(keno_typ, hits)
    if quote <= 0:
        return None, 0

    gk = _GK_LABELS_BY_TYPE[int(keno_typ)].get(int(hits))
    if not gk:
        return None, 0

    return gk, int(quote)


def backtest_group(
    group: list[int],
    keno_typ: int,
    draws: list[tuple[datetime, set[int]]],
) -> ModelStats:
    """Fuehrt Backtest fuer eine Zahlengruppe durch."""
    group_set = set(group)
    stats = ModelStats(
        model_name="",
        strategy="",
        keno_typ=keno_typ,
        total_draws=len(draws),
    )

    for date, drawn in draws:
        hits = calculate_hits(group_set, drawn)
        stats.total_hits += hits
        stats.hit_distribution[hits] = stats.hit_distribution.get(hits, 0) + 1

        gk, quote = get_gewinnklasse(keno_typ, hits)
        if gk:
            stats.gewinnklassen[gk] = stats.gewinnklassen.get(gk, 0) + 1
            stats.total_winnings += quote

    stats.avg_hits = stats.total_hits / stats.total_draws if stats.total_draws > 0 else 0
    # ROI bei 1 Euro pro Ziehung
    stats.roi = (stats.total_winnings - stats.total_draws) / stats.total_draws * 100 if stats.total_draws > 0 else 0

    return stats


def backtest_v1(model: dict, draws: list[tuple[datetime, set[int]]]) -> dict[str, dict]:
    """Backtestet V1 Modell."""
    results = {}

    keno_types = model.get("keno_types", {})
    for typ_key, strategies in keno_types.items():
        keno_typ = int(typ_key.replace("typ_", ""))

        for strategy_name, strategy_data in strategies.items():
            numbers = strategy_data.get("numbers", [])
            if not numbers:
                continue

            stats = backtest_group(numbers, keno_typ, draws)
            stats.model_name = "V1"
            stats.strategy = strategy_name

            key = f"V1_typ{keno_typ}_{strategy_name}"
            results[key] = {
                "model": "V1",
                "keno_typ": keno_typ,
                "strategy": strategy_name,
                "numbers": numbers,
                "total_draws": stats.total_draws,
                "avg_hits": round(stats.avg_hits, 3),
                "hit_distribution": dict(sorted(stats.hit_distribution.items())),
                "gewinnklassen": stats.gewinnklassen,
                "total_winnings": stats.total_winnings,
                "roi_percent": round(stats.roi, 2),
            }

    return results


def backtest_v2(model: dict, draws: list[tuple[datetime, set[int]]]) -> dict[str, dict]:
    """Backtestet V2 Modell."""
    results = {}

    groups_by_type = model.get("groups_by_type", {})
    for typ_key, strategies in groups_by_type.items():
        keno_typ = int(typ_key.replace("typ_", ""))

        for strategy_name, strategy_data in strategies.items():
            numbers = strategy_data.get("numbers", [])
            if not numbers:
                continue

            stats = backtest_group(numbers, keno_typ, draws)
            stats.model_name = "V2"
            stats.strategy = strategy_name

            key = f"V2_typ{keno_typ}_{strategy_name}"
            results[key] = {
                "model": "V2",
                "keno_typ": keno_typ,
                "strategy": strategy_name,
                "numbers": numbers,
                "total_draws": stats.total_draws,
                "avg_hits": round(stats.avg_hits, 3),
                "hit_distribution": dict(sorted(stats.hit_distribution.items())),
                "gewinnklassen": stats.gewinnklassen,
                "total_winnings": stats.total_winnings,
                "roi_percent": round(stats.roi, 2),
            }

    return results


def print_comparison(v1_results: dict, v2_results: dict, keno_typ: int):
    """Gibt Vergleich fuer einen KENO-Typ aus."""
    print(f"\n{'='*70}")
    print(f"KENO TYP {keno_typ} - BACKTEST VERGLEICH")
    print(f"{'='*70}")

    # Header
    print(f"{'Modell':<8} {'Strategie':<15} {'Avg Hits':>9} {'GK1':>5} {'GK2':>5} {'GK3':>5} {'ROI%':>8}")
    print("-" * 70)

    # V1 Ergebnisse
    for key, data in sorted(v1_results.items()):
        if data["keno_typ"] != keno_typ:
            continue
        gk = data["gewinnklassen"]
        print(f"{'V1':<8} {data['strategy']:<15} {data['avg_hits']:>9.3f} "
              f"{gk.get('GK1', 0):>5} {gk.get('GK2', 0):>5} {gk.get('GK3', 0):>5} "
              f"{data['roi_percent']:>7.1f}%")

    print("-" * 70)

    # V2 Ergebnisse
    for key, data in sorted(v2_results.items()):
        if data["keno_typ"] != keno_typ:
            continue
        gk = data["gewinnklassen"]
        print(f"{'V2':<8} {data['strategy']:<15} {data['avg_hits']:>9.3f} "
              f"{gk.get('GK1', 0):>5} {gk.get('GK2', 0):>5} {gk.get('GK3', 0):>5} "
              f"{data['roi_percent']:>7.1f}%")


def calculate_expected_hits(keno_typ: int) -> float:
    """Berechnet erwartete Treffer bei Zufall."""
    # Bei KENO: 20 aus 70 gezogen
    # Wahrscheinlichkeit dass eine Zahl getroffen wird: 20/70 = 0.2857
    return keno_typ * (20 / 70)


def main():
    """Hauptfunktion."""
    data_path = Path("data/raw/keno/KENO_ab_2018.csv")
    results_dir = Path("results")

    print("=" * 70)
    print("KENOBASE - Modell Backtest V1 vs V2")
    print("=" * 70)

    # Lade Ziehungen
    print("\n[1] Lade KENO Ziehungen...")
    draws = load_keno_draws(data_path)
    print(f"    {len(draws)} Ziehungen geladen")
    print(f"    Zeitraum: {draws[0][0].date()} bis {draws[-1][0].date()}")

    # Lade Modelle
    print("\n[2] Lade Modelle...")
    v1_model = load_v1_model(results_dir)
    v2_model = load_v2_model(results_dir)
    print(f"    V1: {len(v1_model.get('keno_types', {}))} Typen")
    print(f"    V2: {len(v2_model.get('groups_by_type', {}))} Typen")

    # Backtest
    print("\n[3] Fuehre Backtest durch...")
    v1_results = backtest_v1(v1_model, draws)
    v2_results = backtest_v2(v2_model, draws)

    # Erwartungswerte
    print("\n[4] Erwartungswerte bei Zufall:")
    for typ in range(5, 11):
        expected = calculate_expected_hits(typ)
        print(f"    Typ {typ}: {expected:.3f} Treffer erwartet")

    # Vergleich ausgeben
    for keno_typ in range(10, 4, -1):
        print_comparison(v1_results, v2_results, keno_typ)

    # Beste Strategien
    print("\n" + "=" * 70)
    print("BESTE STRATEGIEN (nach ROI)")
    print("=" * 70)

    all_results = {**v1_results, **v2_results}
    sorted_by_roi = sorted(all_results.items(), key=lambda x: x[1]["roi_percent"], reverse=True)

    print(f"\n{'Rang':<5} {'Modell':<8} {'Typ':>4} {'Strategie':<15} {'ROI%':>8} {'GK1':>5} {'Zahlen'}")
    print("-" * 90)

    for i, (key, data) in enumerate(sorted_by_roi[:15], 1):
        gk1 = data["gewinnklassen"].get("GK1", 0)
        nums = ",".join(map(str, data["numbers"][:5])) + "..."
        print(f"{i:<5} {data['model']:<8} {data['keno_typ']:>4} {data['strategy']:<15} "
              f"{data['roi_percent']:>7.1f}% {gk1:>5} {nums}")

    # Speichere Ergebnisse
    output = {
        "backtest_date": datetime.now().isoformat(),
        "draws_count": len(draws),
        "date_range": {
            "start": draws[0][0].isoformat(),
            "end": draws[-1][0].isoformat(),
        },
        "v1_results": v1_results,
        "v2_results": v2_results,
        "best_by_roi": [
            {"rank": i+1, **data}
            for i, (_, data) in enumerate(sorted_by_roi[:20])
        ],
    }

    output_path = results_dir / "backtest_v1_v2_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[5] Ergebnisse gespeichert: {output_path}")

    # GK1 Treffer Zusammenfassung
    print("\n" + "=" * 70)
    print("GK1 TREFFER ZUSAMMENFASSUNG (Jackpots)")
    print("=" * 70)

    for keno_typ in range(10, 4, -1):
        v1_gk1 = sum(
            d["gewinnklassen"].get("GK1", 0)
            for d in v1_results.values()
            if d["keno_typ"] == keno_typ
        )
        v2_gk1 = sum(
            d["gewinnklassen"].get("GK1", 0)
            for d in v2_results.values()
            if d["keno_typ"] == keno_typ
        )
        print(f"Typ {keno_typ}: V1={v1_gk1} GK1, V2={v2_gk1} GK1")


if __name__ == "__main__":
    main()
