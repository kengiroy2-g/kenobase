#!/usr/bin/env python3
"""
Kenobase V2.2 - Garantie-Modell Generator

Generiert optimale Zahlengruppen basierend auf allen bestaetigten Hypothesen:
- WL-001: Paar-Garantie (30/30 Paare >90%)
- WL-005: Paar-Gewinn-Frequenz (monatl. Gewinne, nicht automatisch profitabel)
- WL-006: Jackpot-Uniqueness (90.9% haben Score >= 0.5)
- WL-007: GK-spezifische Paare (verschiedene Staerken)

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Ensure project root is importable when running `python scripts/...`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.near_miss import KENO_PROBABILITIES
from kenobase.core.keno_quotes import get_fixed_quote

# Bestaetigte Kern-Zahlen aus Analyse
CORE_NUMBERS = {
    "absolute": [3, 24, 49],
    "extended": [2, 9, 36, 51, 64],
    "anti_birthday": [33, 35, 37, 41, 47, 51, 56, 65, 69],
    "hot": [49, 64, 3, 51, 24, 2, 9, 36, 41, 37]
}

# Top-Paare aus WL-001/WL-007 Analyse
TOP_PAIRS = [
    (9, 50), (20, 36), (9, 10), (32, 64), (33, 49),
    (33, 50), (24, 40), (2, 3), (53, 64), (39, 64),
    (36, 49), (3, 20), (9, 49), (21, 42), (21, 68)
]

# Jackpot-Indikatoren aus WL-007
JACKPOT_INDICATORS = [(3, 9), (3, 25)]


def calculate_pair_score(numbers: List[int], top_pairs: List[Tuple[int, int]]) -> int:
    """Zaehlt wie viele Top-Paare in der Gruppe enthalten sind."""
    count = 0
    for pair in top_pairs:
        if pair[0] in numbers and pair[1] in numbers:
            count += 1
    return count


def calculate_uniqueness_score(numbers: List[int]) -> float:
    """Berechnet Uniqueness-Score fuer Jackpot-Wuerdigkeit."""
    # Anti-Birthday Score
    above_31 = sum(1 for n in numbers if n > 31) / len(numbers)

    # Konsekutive Paare
    sorted_nums = sorted(numbers)
    consecutive = sum(1 for i in range(len(sorted_nums)-1)
                      if sorted_nums[i+1] - sorted_nums[i] == 1)
    consecutive_score = 1 - (consecutive / 10)

    # Dekaden-Verteilung
    decades = [0] * 7
    for n in numbers:
        decades[min((n-1) // 10, 6)] += 1
    variance = np.var(decades)
    decade_score = 1 - (variance / 20)

    # Sum-Extremitaet
    total = sum(numbers)
    expected = 35.5 * len(numbers)
    extremity = abs(total - expected) / 250

    return above_31 * 0.30 + consecutive_score * 0.20 + decade_score * 0.20 + extremity * 0.15


def _expected_return_per_draw(keno_type: int) -> float:
    """Theoretical EV (gross return) for 1 EUR Einsatz under fixed quotes."""
    probs = KENO_PROBABILITIES.get(int(keno_type))
    if not probs:
        raise ValueError(f"Unsupported keno_type: {keno_type}")
    return float(sum(float(p) * get_fixed_quote(keno_type, hits) for hits, p in probs.items()))


def _load_pair_guarantee_backtest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def _extract_best_pair_ticket(pair_backtest: dict, keno_type: int) -> dict | None:
    type_key = f"typ_{int(keno_type)}"
    type_data = (pair_backtest.get("by_type") or {}).get(type_key)
    if not type_data:
        return None
    pair_results = type_data.get("pair_results") or []
    if not pair_results:
        return None
    return pair_results[0]


def generate_best_pair_group(
    keno_type: int,
    *,
    pair_backtest: dict | None = None,
) -> Dict:
    """Bestes (ROI-max) Paar-Ticket aus `scripts/backtest_pair_guarantee.py`."""
    best = _extract_best_pair_ticket(pair_backtest, keno_type) if pair_backtest else None

    if best:
        numbers = list(best["ticket"])
        total_invested = float(best["total_invested"])
        total_won = float(best["total_won"])
        return_per_draw = total_won / total_invested if total_invested > 0 else 0.0
        roi = float(best["roi"])
        monthly_win_rate = float(best["win_rate_monthly"])
        months_with_win = int(best["months_with_win"])
        total_months = int(best["total_months"])
        source = f"pair_guarantee_backtest.json best_pair={best['pair']}"
    else:
        # Fallback: (legacy) previously recommended numbers
        if keno_type == 10:
            numbers = [2, 3, 9, 24, 33, 36, 49, 50, 51, 64]
        elif keno_type == 8:
            numbers = [2, 3, 20, 24, 36, 49, 51, 64]
        elif keno_type == 6:
            numbers = [3, 24, 36, 49, 51, 64]
        else:
            numbers = list(CORE_NUMBERS["absolute"]) + list(CORE_NUMBERS["extended"])[: max(0, keno_type - 3)]

        roi = None
        return_per_draw = None
        monthly_win_rate = None
        months_with_win = None
        total_months = None
        source = "fallback (no backtest results found)"

    expected_return = _expected_return_per_draw(keno_type)
    expected_roi = expected_return - 1.0

    payload: dict = {
        "type": "best_pair_backtest",
        "keno_type": int(keno_type),
        "numbers": sorted(numbers[: int(keno_type)]),
        "pairs_included": calculate_pair_score(numbers[: int(keno_type)], TOP_PAIRS),
        "expected_return_per_draw": round(expected_return, 6),
        "expected_roi": round(expected_roi, 6),
        "source": source,
        "note": "Bei festen Quoten ist der EV (theoretisch) unabhaengig von den konkreten Zahlen.",
    }

    if roi is not None and return_per_draw is not None:
        payload["backtest"] = {
            "roi": round(roi, 6),
            "return_per_draw": round(return_per_draw, 6),
            "profit_per_draw": round(return_per_draw - 1.0, 6),
            "months_with_win": months_with_win,
            "total_months": total_months,
            "monthly_win_rate": round(monthly_win_rate, 6) if monthly_win_rate is not None else None,
        }

    return payload


def generate_jackpot_candidate() -> Dict:
    """
    Generiert Jackpot-Kandidat mit hohem Uniqueness-Score.
    Basiert auf WL-006 Ergebnissen.
    """
    # Anti-Birthday optimiert + starke Paare
    candidate = [33, 35, 37, 41, 47, 49, 51, 56, 65, 69]

    return {
        "type": "jackpot_candidate",
        "keno_type": 10,
        "numbers": sorted(candidate),
        "uniqueness_score": calculate_uniqueness_score(candidate),
        "anti_birthday_ratio": sum(1 for n in candidate if n > 31) / len(candidate),
        "pairs_included": calculate_pair_score(candidate, TOP_PAIRS),
        "source": "WL-006 Uniqueness Model"
    }


def generate_guarantee_100_group() -> Dict:
    """
    Generiert Gruppe fuer haeufige kleine Gewinne (kein Profitversprechen).
    Typ-6: 5/6 = 15 EUR, 6/6 = 500 EUR (bei 1 EUR Einsatz).
    """
    # Kombiniere starke Paare mit Kern-Zahlen
    numbers = [3, 9, 24, 49, 50, 64]

    expected_return = _expected_return_per_draw(6)
    return {
        "type": "guarantee_100",
        "keno_type": 6,
        "numbers": sorted(numbers),
        "pairs_included": calculate_pair_score(numbers, TOP_PAIRS),
        "target_hits": "5/6 = 15 EUR oder 6/6 = 500 EUR",
        "expected_return_per_draw": round(expected_return, 6),
        "expected_roi": round(expected_return - 1.0, 6),
        "source": "WL-001 Paar-Garantie"
    }


def generate_guarantee_500_group() -> Dict:
    """
    Generiert Gruppe fuer seltenere Hoechstgewinne (kein Profitversprechen).
    Typ-8: 7/8 = 100 EUR, 8/8 = 10000 EUR (bei 1 EUR Einsatz).
    """
    numbers = [2, 3, 9, 20, 24, 36, 49, 64]

    expected_return = _expected_return_per_draw(8)
    return {
        "type": "guarantee_500",
        "keno_type": 8,
        "numbers": sorted(numbers),
        "pairs_included": calculate_pair_score(numbers, TOP_PAIRS),
        "target_hits": "6/8 = 15 EUR, 7/8 = 100 EUR, 8/8 = 10000 EUR",
        "expected_return_per_draw": round(expected_return, 6),
        "expected_roi": round(expected_return - 1.0, 6),
        "source": "WL-005 Backtest"
    }


def generate_all_recommendations() -> Dict:
    """Generiert alle Empfehlungen."""
    base_path = Path(__file__).parent.parent
    pair_backtest_path = base_path / "results" / "pair_guarantee_backtest.json"
    pair_backtest = _load_pair_guarantee_backtest(pair_backtest_path)

    recommendations = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "version": "2.2.2",
            "model": "Wirtschaftslogik-Garantie-Modell",
            "hypotheses_used": ["WL-001", "WL-005", "WL-006", "WL-007"],
            "pair_backtest_file": str(pair_backtest_path) if pair_backtest else None,
        },
        "summary": {
            "confirmed_hypotheses": 11,
            "payout_model": "fixed_quotes_1eur",
            "expected_return_per_draw": {
                f"typ_{k}": round(_expected_return_per_draw(k), 6) for k in [6, 8, 10]
            },
            "expected_roi": {f"typ_{k}": round(_expected_return_per_draw(k) - 1.0, 6) for k in [6, 8, 10]},
        },
        "core_numbers": CORE_NUMBERS,
        "top_pairs": [str(p) for p in TOP_PAIRS[:10]],
        "jackpot_indicators": [str(p) for p in JACKPOT_INDICATORS],
        "recommendations": {}
    }

    # Bestes Paar-Ticket pro Typ (Backtest)
    for keno_type in [6, 8, 10]:
        key = f"best_pair_typ_{keno_type}"
        recommendations["recommendations"][key] = generate_best_pair_group(
            keno_type, pair_backtest=pair_backtest
        )

    # Garantie-Gruppen
    recommendations["recommendations"]["guarantee_100"] = generate_guarantee_100_group()
    recommendations["recommendations"]["guarantee_500"] = generate_guarantee_500_group()

    # Jackpot-Kandidat
    recommendations["recommendations"]["jackpot_candidate"] = generate_jackpot_candidate()

    return recommendations


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("KENOBASE V2.2.2 - GARANTIE-MODELL GENERATOR")
    print("=" * 70)
    print()

    print("Bestaetigte Hypothesen: 11")
    print("  - WL-001: Paar-Garantie (30/30 Paare >90%)")
    print("  - WL-005: Paar-Gewinn-Frequenz (monatl. Gewinne, nicht automatisch profitabel)")
    print("  - WL-006: Jackpot-Uniqueness (90.9% >= 0.5)")
    print("  - WL-007: GK-spezifische Paare")
    print()

    # Generiere Empfehlungen
    recommendations = generate_all_recommendations()

    # Economics summary (fixed quotes)
    print("Quoten-Modell (1 EUR Einsatz, fixed):")
    for k, v in recommendations["summary"]["expected_return_per_draw"].items():
        roi = recommendations["summary"]["expected_roi"][k]
        print(f"  {k}: E[Return]={v:.3f} EUR  E[ROI]={roi*100:.1f}%")
    print()

    # Ausgabe
    print("=" * 70)
    print("EMPFEHLUNGEN")
    print("=" * 70)

    for key, rec in recommendations["recommendations"].items():
        print(f"\n--- {rec['type'].upper()} (Typ-{rec['keno_type']}) ---")
        print(f"  Zahlen: {rec['numbers']}")
        print(f"  Paare: {rec['pairs_included']}")

        if "expected_return_per_draw" in rec and "expected_roi" in rec:
            print(
                f"  Erwartung (Nullmodell): Return={rec['expected_return_per_draw']:.3f} EUR "
                f"ROI={rec['expected_roi']*100:.1f}%"
            )

        if "backtest" in rec:
            bt = rec["backtest"]
            print(
                f"  Backtest: Return={bt['return_per_draw']:.3f} EUR ROI={bt['roi']*100:.1f}% "
                f"Monate_mit_Gewinn={bt['months_with_win']}/{bt['total_months']}"
            )

        if "uniqueness_score" in rec:
            print(f"  Uniqueness: {rec['uniqueness_score']:.3f}")

    # Speichern
    output_path = Path(__file__).parent.parent / "results" / "guarantee_recommendations.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)

    print(f"\n\nEmpfehlungen gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG FUER SPIELER")
    print("=" * 70)

    print("Hinweis: Bei festen Quoten ist der Erwartungswert negativ; es gibt keine echte Profit-Garantie.")
    print("Bestes Paar-Ticket (Backtest, falls Datei vorhanden):")
    for k in [6, 8, 10]:
        key = f"best_pair_typ_{k}"
        rec = recommendations["recommendations"][key]
        nums = ", ".join(map(str, rec["numbers"]))
        bt = rec.get("backtest")
        if bt:
            print(f"  Typ-{k}: {nums} | ROI={bt['roi']*100:.1f}% | Return={bt['return_per_draw']:.3f} EUR")
        else:
            print(f"  Typ-{k}: {nums} | (kein Backtest geladen)")

    print("\nWICHTIG: Das sind statistische/heuristische Empfehlungen basierend auf historischen Daten.")
    print("Keine Gewinngarantie; bitte als Analyse-Tool, nicht als Versprechen verstehen.")
    print("=" * 70)


if __name__ == "__main__":
    main()
