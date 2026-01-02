#!/usr/bin/env python3
"""
V1 vs V2 Model Comparison for all available KENO Typen.

Aggregates existing backtest data and creates per-Typ comparison
with ROI-Delta, hit-distribution, and best strategy per model.

Data source: results/backtest_v1_v2_comparison.json (2237 draws, 2018-2024)
Available types: 5-10 (Typ 2-4 not in source data)
Output: results/v1_v2_all_typen_comparison.json

Repro: python scripts/compare_v1_v2_all_typen.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_backtest_data(path: Path) -> dict[str, Any]:
    """Load existing V1/V2 backtest results."""
    with open(path) as f:
        return json.load(f)


def detect_available_typen(data: dict[str, Any]) -> list[int]:
    """Detect which Keno types are available in the backtest data."""
    typen_set: set[int] = set()
    for key in ["v1_results", "v2_results"]:
        for result in data.get(key, {}).values():
            if "keno_typ" in result:
                typen_set.add(result["keno_typ"])
    return sorted(typen_set)


def extract_typ_results(
    data: dict[str, Any], model: str, keno_typ: int
) -> list[dict[str, Any]]:
    """Extract all strategies for a given model and Keno typ."""
    key = f"{model.lower()}_results"
    results = []
    for name, result in data.get(key, {}).items():
        if result.get("keno_typ") == keno_typ:
            results.append(result)
    return results


def find_best_strategy(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the strategy with the highest ROI."""
    if not results:
        return None
    return max(results, key=lambda x: x.get("roi_percent", -999))


def calculate_avg_roi(results: list[dict[str, Any]]) -> float:
    """Calculate average ROI across strategies."""
    if not results:
        return 0.0
    rois = [r.get("roi_percent", 0) for r in results]
    return sum(rois) / len(rois)


def compare_models_for_typ(
    data: dict[str, Any], keno_typ: int
) -> dict[str, Any]:
    """Create comparison between V1 and V2 for a specific Keno typ."""
    v1_results = extract_typ_results(data, "V1", keno_typ)
    v2_results = extract_typ_results(data, "V2", keno_typ)

    v1_best = find_best_strategy(v1_results)
    v2_best = find_best_strategy(v2_results)

    v1_avg_roi = calculate_avg_roi(v1_results)
    v2_avg_roi = calculate_avg_roi(v2_results)

    v1_best_roi = v1_best.get("roi_percent", 0) if v1_best else 0
    v2_best_roi = v2_best.get("roi_percent", 0) if v2_best else 0

    # Handle edge case for v2_advantage_percent calculation
    if v1_best_roi == 0:
        v2_advantage_pct = 0.0 if v2_best_roi == 0 else float("inf")
    else:
        v2_advantage_pct = (v2_best_roi - v1_best_roi) / abs(v1_best_roi) * 100

    return {
        "keno_typ": keno_typ,
        "v1": {
            "strategies_count": len(v1_results),
            "avg_roi_percent": round(v1_avg_roi, 2),
            "best_strategy": v1_best.get("strategy") if v1_best else None,
            "best_roi_percent": round(v1_best_roi, 2),
            "best_numbers": v1_best.get("numbers") if v1_best else None,
            "best_avg_hits": v1_best.get("avg_hits") if v1_best else None,
            "best_hit_distribution": v1_best.get("hit_distribution") if v1_best else None,
            "best_gewinnklassen": v1_best.get("gewinnklassen") if v1_best else None,
        },
        "v2": {
            "strategies_count": len(v2_results),
            "avg_roi_percent": round(v2_avg_roi, 2),
            "best_strategy": v2_best.get("strategy") if v2_best else None,
            "best_roi_percent": round(v2_best_roi, 2),
            "best_numbers": v2_best.get("numbers") if v2_best else None,
            "best_avg_hits": v2_best.get("avg_hits") if v2_best else None,
            "best_hit_distribution": v2_best.get("hit_distribution") if v2_best else None,
            "best_gewinnklassen": v2_best.get("gewinnklassen") if v2_best else None,
        },
        "comparison": {
            "roi_delta_best": round(v2_best_roi - v1_best_roi, 2),
            "roi_delta_avg": round(v2_avg_roi - v1_avg_roi, 2),
            "winner_model": "V2" if v2_best_roi > v1_best_roi else ("V1" if v1_best_roi > v2_best_roi else "TIE"),
            "v2_advantage_percent": round(v2_advantage_pct, 2) if v2_advantage_pct != float("inf") else "inf",
        },
    }


def main() -> None:
    """Run V1 vs V2 comparison for all available Typen."""
    base_path = Path(__file__).parent.parent
    input_path = base_path / "results" / "backtest_v1_v2_comparison.json"
    output_path = base_path / "results" / "v1_v2_all_typen_comparison.json"

    print(f"Loading data from: {input_path}")
    data = load_backtest_data(input_path)

    draws_count = data.get("draws_count", 0)
    date_range = data.get("date_range", {})

    print(f"Data: {draws_count} draws ({date_range.get('start', '?')} to {date_range.get('end', '?')})")

    # Detect available types dynamically
    available_typen = detect_available_typen(data)
    print(f"Available Typen in data: {available_typen}")

    # Note missing types
    expected_typen = list(range(2, 11))  # Typ 2-10
    missing_typen = [t for t in expected_typen if t not in available_typen]
    if missing_typen:
        print(f"Note: Typ {missing_typen} not in source data (backtest not generated for these)")

    comparisons = []
    for typ in available_typen:
        print(f"\nAnalyzing Typ {typ}...")
        comparison = compare_models_for_typ(data, typ)
        comparisons.append(comparison)

        winner = comparison["comparison"]["winner_model"]
        delta = comparison["comparison"]["roi_delta_best"]
        print(f"  Winner: {winner} (ROI-Delta: {delta:+.2f}%)")

    # Summary statistics
    v2_wins = sum(1 for c in comparisons if c["comparison"]["winner_model"] == "V2")
    v1_wins = sum(1 for c in comparisons if c["comparison"]["winner_model"] == "V1")
    ties = len(comparisons) - v2_wins - v1_wins
    avg_delta = sum(c["comparison"]["roi_delta_best"] for c in comparisons) / len(comparisons) if comparisons else 0

    result = {
        "analysis_date": datetime.now().isoformat(),
        "source_file": str(input_path.name),
        "draws_count": draws_count,
        "date_range": date_range,
        "available_typen": available_typen,
        "missing_typen": missing_typen,
        "summary": {
            "total_typen_compared": len(comparisons),
            "v2_wins": v2_wins,
            "v1_wins": v1_wins,
            "ties": ties,
            "avg_roi_delta_best": round(avg_delta, 2),
            "conclusion": f"V2 wins {v2_wins}/{len(comparisons)} Typen with avg ROI-Delta of {avg_delta:+.2f}%",
        },
        "per_typ_comparison": comparisons,
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SUMMARY: V1 vs V2 for Typ {min(available_typen)}-{max(available_typen)}")
    print(f"{'='*60}")
    print(f"Typen analyzed: {len(comparisons)} (Typ {available_typen})")
    if missing_typen:
        print(f"Missing Typen: {missing_typen} (not in backtest source)")
    print(f"V2 Wins: {v2_wins}/{len(comparisons)} Typen")
    print(f"V1 Wins: {v1_wins}/{len(comparisons)} Typen")
    if ties:
        print(f"Ties: {ties}")
    print(f"Average ROI-Delta (best): {avg_delta:+.2f}%")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
