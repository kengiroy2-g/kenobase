#!/usr/bin/env python3
"""
Jackknife Leave-One-Out Varianzschaetzung fuer V1 vs V2 ROI-Differenz.

TASK_039e: Berechnet robuste Konfidenzintervalle fuer die V2-V1 Delta.

Methode:
- Jackknife LOO: Fuer jeden Zyklus i, berechne Mean-Delta auf 67 anderen Zyklen
- Standard Error (SE) via Jackknife-Formel
- 95% CI = Mean +/- 1.96 * SE
- Signifikanz: 0 ausserhalb des CI?

Input: results/v1_v2_cycle_comparison.json (68 Zyklen)
Output: results/jackknife_v1_v2_loo.json

Repro: python scripts/jackknife_v1_v2_loo.py
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def jackknife_standard_error(deltas: List[float]) -> Tuple[float, float, float, bool]:
    """
    Berechnet Jackknife Standard Error und 95% Konfidenzintervall.

    Args:
        deltas: Liste der ROI-Differenzen (V2 - V1) pro Zyklus

    Returns:
        Tuple: (se, ci_lower, ci_upper, significant)
        - se: Jackknife Standard Error
        - ci_lower: 95% CI untere Grenze
        - ci_upper: 95% CI obere Grenze
        - significant: True wenn 0 ausserhalb des CI
    """
    n = len(deltas)
    if n < 2:
        return 0.0, 0.0, 0.0, False

    # Original-Mittelwert
    mean_delta = sum(deltas) / n

    # Jackknife LOO: Fuer jeden i, berechne Mean auf n-1 Samples
    theta_i = []
    for i in range(n):
        loo_deltas = deltas[:i] + deltas[i+1:]
        theta_i.append(sum(loo_deltas) / len(loo_deltas))

    # Jackknife Standard Error
    # SE = sqrt( ((n-1)/n) * sum((theta_i - theta_bar)^2) )
    theta_bar = sum(theta_i) / n
    sum_sq = sum((t - theta_bar) ** 2 for t in theta_i)
    jackknife_variance = ((n - 1) / n) * sum_sq
    se = math.sqrt(jackknife_variance)

    # 95% CI (z = 1.96 fuer alpha = 0.05)
    ci_lower = mean_delta - 1.96 * se
    ci_upper = mean_delta + 1.96 * se

    # Signifikanz: 0 ausserhalb des CI?
    significant = not (ci_lower <= 0 <= ci_upper)

    return se, ci_lower, ci_upper, significant


def run_jackknife_analysis(input_path: Path) -> Dict:
    """
    Fuehrt Jackknife LOO Analyse auf v1_v2_cycle_comparison.json durch.

    Args:
        input_path: Pfad zur Eingabe-JSON

    Returns:
        Dict mit Jackknife-Ergebnissen
    """
    # Lade existierende Vergleichsdaten
    with open(input_path, "r", encoding="utf-8") as f:
        comparison_data = json.load(f)

    n_cycles = comparison_data["cycle_semantics"]["total_cycles"]

    results = {
        "analysis_date": datetime.now().isoformat(),
        "method": "jackknife_leave_one_out",
        "input_file": str(input_path),
        "n_cycles": n_cycles,
        "per_type": {},
        "combined": {},
        "interpretation": "",
    }

    all_deltas = []
    type_summaries = []

    # Pro KENO-Typ (8, 9, 10)
    for keno_type in [8, 9, 10]:
        type_key = f"typ_{keno_type}"
        per_cycle = comparison_data["per_cycle_detail"][type_key]

        # Extrahiere Deltas (V2_ROI - V1_ROI)
        deltas = [cycle["delta"] for cycle in per_cycle]
        all_deltas.extend(deltas)

        mean_delta = sum(deltas) / len(deltas)
        se, ci_lower, ci_upper, significant = jackknife_standard_error(deltas)

        results["per_type"][type_key] = {
            "mean_delta": round(mean_delta, 4),
            "jackknife_se": round(se, 4),
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4),
            "significant_at_005": significant,
            "n_loo_samples": len(deltas),
        }

        type_summaries.append({
            "type": keno_type,
            "mean": mean_delta,
            "se": se,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "significant": significant,
        })

        print(f"\n{type_key.upper()}:")
        print(f"  Mean Delta: {mean_delta:+.2f}%")
        print(f"  Jackknife SE: {se:.2f}%")
        print(f"  95% CI: [{ci_lower:.2f}%, {ci_upper:.2f}%]")
        print(f"  Signifikant (alpha=0.05): {'JA' if significant else 'NEIN'}")

    # Combined (alle 3 Typen, 68*3 = 204 Zyklen)
    combined_mean = sum(all_deltas) / len(all_deltas)
    combined_se, combined_ci_lower, combined_ci_upper, combined_significant = jackknife_standard_error(all_deltas)

    results["combined"] = {
        "mean_delta": round(combined_mean, 4),
        "jackknife_se": round(combined_se, 4),
        "ci_95_lower": round(combined_ci_lower, 4),
        "ci_95_upper": round(combined_ci_upper, 4),
        "significant_at_005": combined_significant,
        "n_loo_samples": len(all_deltas),
    }

    print(f"\nCOMBINED (alle Typen, N={len(all_deltas)}):")
    print(f"  Mean Delta: {combined_mean:+.2f}%")
    print(f"  Jackknife SE: {combined_se:.2f}%")
    print(f"  95% CI: [{combined_ci_lower:.2f}%, {combined_ci_upper:.2f}%]")
    print(f"  Signifikant (alpha=0.05): {'JA' if combined_significant else 'NEIN'}")

    # Robustheit-Check: Sind alle 3 Typen konsistent?
    all_positive = all(s["mean"] > 0 for s in type_summaries)
    all_negative = all(s["mean"] < 0 for s in type_summaries)
    any_significant = any(s["significant"] for s in type_summaries)

    results["robustness_check"] = {
        "all_types_positive_delta": all_positive,
        "all_types_negative_delta": all_negative,
        "any_type_significant": any_significant,
        "consistency": "CONSISTENT" if (all_positive or all_negative) else "MIXED",
    }

    # Interpretation
    if combined_significant:
        if combined_mean > 0:
            interpretation = f"V2 zeigt signifikant bessere Performance als V1 (+{combined_mean:.2f}%, p<0.05)"
        else:
            interpretation = f"V1 zeigt signifikant bessere Performance als V2 ({combined_mean:.2f}%, p<0.05)"
    else:
        interpretation = f"V2 zeigt positive Delta (+{combined_mean:.2f}%), aber NICHT signifikant bei alpha=0.05. " \
                         f"95% CI umfasst 0 -> Differenz kann Zufall sein."

    results["interpretation"] = interpretation

    return results


def main():
    """Hauptfunktion: Jackknife LOO Analyse."""
    print("=" * 70)
    print("JACKKNIFE LEAVE-ONE-OUT: V1 vs V2 VARIANZSCHAETZUNG")
    print("=" * 70)
    print()
    print("Methode:")
    print("  - Jackknife LOO fuer robuste SE-Schaetzung")
    print("  - 95% CI via +-1.96*SE")
    print("  - Signifikanz: 0 ausserhalb des CI?")
    print()

    base_path = Path(__file__).parent.parent
    input_path = base_path / "results" / "v1_v2_cycle_comparison.json"
    output_path = base_path / "results" / "jackknife_v1_v2_loo.json"

    if not input_path.exists():
        print(f"ERROR: Input-Datei nicht gefunden: {input_path}")
        print("Bitte zuerst compare_v1_v2_cycles.py ausfuehren.")
        return

    print(f"Input: {input_path}")
    print()

    # Analyse durchfuehren
    results = run_jackknife_analysis(input_path)

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print(f"\n{results['interpretation']}")

    print("\n" + "=" * 70)
    print("ROBUSTHEIT")
    print("=" * 70)
    rob = results["robustness_check"]
    print(f"\n  Alle Typen positive Delta: {'JA' if rob['all_types_positive_delta'] else 'NEIN'}")
    print(f"  Irgendein Typ signifikant: {'JA' if rob['any_type_significant'] else 'NEIN'}")
    print(f"  Konsistenz: {rob['consistency']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
