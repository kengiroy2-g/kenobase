#!/usr/bin/env python3
"""
TEST: Alternative Vorhersage-Kriterien.

Testet verschiedene Regeln um unter/ueber-repraesentierte Zahlen vorherzusagen.
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import stdev
from typing import Dict, List, Set, Tuple, Callable

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}
BIRTHDAY_ALL = set(range(1, 32))


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
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """Holt Momentum-Zahlen."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()
    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def calculate_full_metrics(draws: List[Dict], stichtag_idx: int, pre_start_idx: int, zahl: int) -> Dict:
    """Berechnet erweiterte Metriken."""
    # Index (letzte 20 Tage)
    lookback_20 = draws[max(0, stichtag_idx-20):stichtag_idx]
    index = sum(1 if zahl in d["zahlen"] else -1 for d in lookback_20)
    count_20 = sum(1 for d in lookback_20 if zahl in d["zahlen"])

    # MCount (letzte 3 Tage)
    lookback_3 = draws[max(0, stichtag_idx-3):stichtag_idx]
    mcount = sum(1 for d in lookback_3 if zahl in d["zahlen"])

    # Gap
    gap = 0
    for i in range(stichtag_idx - 1, -1, -1):
        if zahl in draws[i]["zahlen"]:
            break
        gap += 1

    # Pre-Phase Indices (fuer Trend und Volatilitaet)
    pre_indices = []
    for idx in range(pre_start_idx, stichtag_idx):
        lb = draws[max(0, idx-20):idx]
        pre_idx = sum(1 if zahl in d["zahlen"] else -1 for d in lb)
        pre_indices.append(pre_idx)

    trend = pre_indices[-1] - pre_indices[0] if len(pre_indices) >= 2 else 0
    volatility = stdev(pre_indices) if len(pre_indices) >= 2 else 0

    # Count in Pre-Phase (wie oft gezogen?)
    pre_draws = draws[pre_start_idx:stichtag_idx]
    pre_count = sum(1 for d in pre_draws if zahl in d["zahlen"])

    return {
        "index": index,
        "count_20": count_20,
        "mcount": mcount,
        "gap": gap,
        "trend": trend,
        "volatility": volatility,
        "pre_count": pre_count,
        "is_birthday": zahl in BIRTHDAY_ALL,
        "is_birthday_popular": zahl in BIRTHDAY_POPULAR,
    }


# === VORHERSAGE-REGELN ===

def rule_original(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Original-Regel: Index + Trend."""
    under = {z for z in pool if metrics[z]["index"] > -5 and metrics[z]["trend"] > 2}
    over = {z for z in pool if metrics[z]["index"] < -8 and metrics[z]["trend"] <= 0}
    return under, over


def rule_inverse(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Inverse Regel: Umgekehrte Logik."""
    under = {z for z in pool if metrics[z]["index"] < -8 and metrics[z]["trend"] <= 0}
    over = {z for z in pool if metrics[z]["index"] > -5 and metrics[z]["trend"] > 2}
    return under, over


def rule_momentum_only(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Nur Momentum: HOT = unter, COLD = ueber."""
    under = {z for z in pool if metrics[z]["mcount"] >= 2}
    over = {z for z in pool if metrics[z]["gap"] >= 5}
    return under, over


def rule_momentum_inverse(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Inverse Momentum: HOT = ueber, COLD = unter."""
    over = {z for z in pool if metrics[z]["mcount"] >= 2}
    under = {z for z in pool if metrics[z]["gap"] >= 5}
    return under, over


def rule_birthday_split(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Birthday = unter, Non-Birthday = ueber."""
    under = {z for z in pool if metrics[z]["is_birthday_popular"]}
    over = {z for z in pool if not metrics[z]["is_birthday"]}
    return under, over


def rule_birthday_inverse(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Birthday = ueber, Non-Birthday = unter."""
    over = {z for z in pool if metrics[z]["is_birthday_popular"]}
    under = {z for z in pool if not metrics[z]["is_birthday"]}
    return under, over


def rule_volatility(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Hohe Volatilitaet = unter, niedrige = ueber."""
    avg_vol = sum(metrics[z]["volatility"] for z in pool) / len(pool)
    under = {z for z in pool if metrics[z]["volatility"] > avg_vol * 1.2}
    over = {z for z in pool if metrics[z]["volatility"] < avg_vol * 0.8}
    return under, over


def rule_extreme_index(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Extremer Index: Sehr niedrig = ueber (Regression), sehr hoch = unter."""
    indices = [metrics[z]["index"] for z in pool]
    q25 = sorted(indices)[len(indices) // 4]
    q75 = sorted(indices)[3 * len(indices) // 4]
    under = {z for z in pool if metrics[z]["index"] >= q75}
    over = {z for z in pool if metrics[z]["index"] <= q25}
    return under, over


def rule_pre_count(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Pre-Count basiert: Viel gezogen = unter, wenig = ueber."""
    avg_pre = sum(metrics[z]["pre_count"] for z in pool) / len(pool)
    under = {z for z in pool if metrics[z]["pre_count"] > avg_pre * 1.3}
    over = {z for z in pool if metrics[z]["pre_count"] < avg_pre * 0.7}
    return under, over


def rule_hot_birthday(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """HOT + Birthday = unter."""
    under = {z for z in pool if metrics[z]["mcount"] >= 2 and metrics[z]["is_birthday"]}
    over = {z for z in pool if metrics[z]["mcount"] < 2 and not metrics[z]["is_birthday"]}
    return under, over


def rule_cold_high_index(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """COLD + hoher Index = unter (Korrektur nach oben erwartet, aber wird unter)."""
    under = {z for z in pool if metrics[z]["gap"] >= 3 and metrics[z]["index"] > -6}
    over = {z for z in pool if metrics[z]["mcount"] >= 2 and metrics[z]["index"] < -8}
    return under, over


def rule_rising_momentum(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Steigender Trend + HOT = unter."""
    under = {z for z in pool if metrics[z]["trend"] > 4 and metrics[z]["mcount"] >= 2}
    over = {z for z in pool if metrics[z]["trend"] < -2 and metrics[z]["mcount"] < 2}
    return under, over


def rule_falling_cold(pool: Set[int], metrics: Dict) -> Tuple[Set[int], Set[int]]:
    """Fallender Trend + COLD = ueber (Regression)."""
    under = {z for z in pool if metrics[z]["trend"] > 4 and metrics[z]["gap"] >= 3}
    over = {z for z in pool if metrics[z]["trend"] < -2 and metrics[z]["mcount"] >= 1}
    return under, over


# Alle Regeln
RULES = {
    "Original (Idx+Trend)": rule_original,
    "Inverse (Idx+Trend)": rule_inverse,
    "Momentum Only": rule_momentum_only,
    "Momentum Inverse": rule_momentum_inverse,
    "Birthday Split": rule_birthday_split,
    "Birthday Inverse": rule_birthday_inverse,
    "Volatility": rule_volatility,
    "Extreme Index (Quartile)": rule_extreme_index,
    "Pre-Count": rule_pre_count,
    "HOT + Birthday": rule_hot_birthday,
    "COLD + High Index": rule_cold_high_index,
    "Rising + Momentum": rule_rising_momentum,
    "Falling + Cold": rule_falling_cold,
}


def evaluate_rule(
    rule_func: Callable,
    pool: Set[int],
    metrics: Dict,
    actual_under: Set[int],
    actual_over: Set[int]
) -> Dict:
    """Evaluiert eine Vorhersage-Regel."""
    pred_under, pred_over = rule_func(pool, metrics)

    # Precision und Recall
    tp_under = len(pred_under & actual_under)
    tp_over = len(pred_over & actual_over)

    precision_under = tp_under / len(pred_under) * 100 if pred_under else 0
    precision_over = tp_over / len(pred_over) * 100 if pred_over else 0

    recall_under = tp_under / len(actual_under) * 100 if actual_under else 0
    recall_over = tp_over / len(actual_over) * 100 if actual_over else 0

    # F1-Score
    f1_under = 2 * precision_under * recall_under / (precision_under + recall_under) if (precision_under + recall_under) > 0 else 0
    f1_over = 2 * precision_over * recall_over / (precision_over + recall_over) if (precision_over + recall_over) > 0 else 0

    return {
        "pred_under": pred_under,
        "pred_over": pred_over,
        "precision_under": precision_under,
        "precision_over": precision_over,
        "recall_under": recall_under,
        "recall_over": recall_over,
        "f1_under": f1_under,
        "f1_over": f1_over,
        "avg_f1": (f1_under + f1_over) / 2,
    }


def run_test(draws: List[Dict], stichtag: datetime, test_end: datetime) -> Dict:
    """Fuehrt Test fuer einen Stichtag durch."""
    # Indizes finden
    stichtag_idx = next(i for i, d in enumerate(draws) if d["datum"] >= stichtag)
    pre_start = stichtag - timedelta(days=14)
    pre_start_idx = next(i for i, d in enumerate(draws) if d["datum"] >= pre_start)

    # Pool
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum

    # Metriken
    metrics = {}
    for z in pool:
        metrics[z] = calculate_full_metrics(draws, stichtag_idx, pre_start_idx, z)

    # Tatsaechliche Unter/Ueber ermitteln
    test_draws = [d for d in draws if stichtag <= d["datum"] <= test_end]
    draw_counts = {z: sum(1 for d in test_draws if z in d["zahlen"]) for z in pool}
    expected = len(test_draws) * 20 / 70

    actual_under = {z for z in pool if draw_counts[z] < expected * 0.85}
    actual_over = {z for z in pool if draw_counts[z] > expected * 1.15}

    # Alle Regeln evaluieren
    results = {}
    for name, rule_func in RULES.items():
        results[name] = evaluate_rule(rule_func, pool, metrics, actual_under, actual_over)

    return {
        "stichtag": stichtag,
        "pool": pool,
        "metrics": metrics,
        "actual_under": actual_under,
        "actual_over": actual_over,
        "rule_results": results,
    }


def main():
    print("=" * 100)
    print("TEST: Alternative Vorhersage-Kriterien")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Teste mehrere Stichtage
    test_cases = [
        (datetime(2025, 2, 1), datetime(2025, 7, 31)),
        (datetime(2025, 3, 1), datetime(2025, 7, 31)),
        (datetime(2025, 4, 1), datetime(2025, 7, 31)),
        (datetime(2025, 5, 1), datetime(2025, 7, 31)),
    ]

    all_results = []

    for stichtag, test_end in test_cases:
        print(f"\n{'='*100}")
        print(f"STICHTAG: {stichtag.date()} bis {test_end.date()}")
        print(f"{'='*100}")

        result = run_test(draws, stichtag, test_end)
        all_results.append(result)

        print(f"\n  Pool: {sorted(result['pool'])}")
        print(f"  Tatsaechlich UNTER: {sorted(result['actual_under'])}")
        print(f"  Tatsaechlich UEBER: {sorted(result['actual_over'])}")

        print(f"\n  {'Regel':<30} {'Prec_U':<10} {'Prec_O':<10} {'Rec_U':<10} {'Rec_O':<10} {'Avg_F1':<10}")
        print("  " + "-" * 85)

        sorted_rules = sorted(result['rule_results'].items(), key=lambda x: x[1]['avg_f1'], reverse=True)

        for name, r in sorted_rules:
            print(f"  {name:<30} {r['precision_under']:<10.1f} {r['precision_over']:<10.1f} "
                  f"{r['recall_under']:<10.1f} {r['recall_over']:<10.1f} {r['avg_f1']:<10.1f}")

    # === AGGREGIERTE ERGEBNISSE ===
    print(f"\n\n{'='*100}")
    print("AGGREGIERTE ERGEBNISSE UEBER ALLE STICHTAGE")
    print(f"{'='*100}")

    # Durchschnitt ueber alle Stichtage
    avg_scores = {}
    for name in RULES.keys():
        scores = [r['rule_results'][name]['avg_f1'] for r in all_results]
        prec_u = [r['rule_results'][name]['precision_under'] for r in all_results]
        prec_o = [r['rule_results'][name]['precision_over'] for r in all_results]
        avg_scores[name] = {
            'avg_f1': sum(scores) / len(scores),
            'avg_prec_u': sum(prec_u) / len(prec_u),
            'avg_prec_o': sum(prec_o) / len(prec_o),
        }

    print(f"\n  {'Regel':<30} {'Avg Prec_U':<12} {'Avg Prec_O':<12} {'Avg F1':<12}")
    print("  " + "-" * 70)

    sorted_avg = sorted(avg_scores.items(), key=lambda x: x[1]['avg_f1'], reverse=True)
    for name, scores in sorted_avg:
        print(f"  {name:<30} {scores['avg_prec_u']:<12.1f} {scores['avg_prec_o']:<12.1f} {scores['avg_f1']:<12.1f}")

    # === BESTE REGEL DETAILS ===
    best_rule_name = sorted_avg[0][0]
    print(f"\n\n{'='*100}")
    print(f"BESTE REGEL: {best_rule_name}")
    print(f"{'='*100}")

    for result in all_results:
        r = result['rule_results'][best_rule_name]
        print(f"\n  Stichtag {result['stichtag'].date()}:")
        print(f"    Vorhergesagt UNTER: {sorted(r['pred_under'])}")
        print(f"    Tatsaechlich UNTER: {sorted(result['actual_under'])}")
        print(f"    Korrekt: {sorted(r['pred_under'] & result['actual_under'])}")
        print(f"    Vorhergesagt UEBER: {sorted(r['pred_over'])}")
        print(f"    Tatsaechlich UEBER: {sorted(result['actual_over'])}")
        print(f"    Korrekt: {sorted(r['pred_over'] & result['actual_over'])}")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
