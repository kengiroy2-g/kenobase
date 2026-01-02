#!/usr/bin/env python3
"""
V1 vs V2 Model Comparison for KENO Typ 6-10.

Aggregates existing backtest data and creates per-Typ comparison
with ROI-Delta, hit-distribution, and best strategy per model.

Data source: results/backtest_v1_v2_comparison.json (2237 draws, 2018-2024)
Output: results/v1_v2_typ6_10_comparison.json

Repro: python scripts/compare_v1_v2_typ6_10.py
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
            "winner_model": "V2" if v2_best_roi > v1_best_roi else "V1",
            "v2_advantage_percent": round(
                ((v2_best_roi - v1_best_roi) / abs(v1_best_roi) * 100)
                if v1_best_roi != 0 else 0, 2
            ),
        },
    }


def main() -> None:
    """Run V1 vs V2 comparison for Typ 6-10."""
    base_path = Path(__file__).parent.parent
    input_path = base_path / "results" / "backtest_v1_v2_comparison.json"
    output_path = base_path / "results" / "v1_v2_typ6_10_comparison.json"

    print(f"Loading data from: {input_path}")
    data = load_backtest_data(input_path)

    draws_count = data.get("draws_count", 0)
    date_range = data.get("date_range", {})

    print(f"Data: {draws_count} draws ({date_range.get('start', '?')} to {date_range.get('end', '?')})")

    comparisons = []
    for typ in [6, 7, 8, 9, 10]:
        print(f"\nAnalyzing Typ {typ}...")
        comparison = compare_models_for_typ(data, typ)
        comparisons.append(comparison)

        winner = comparison["comparison"]["winner_model"]
        delta = comparison["comparison"]["roi_delta_best"]
        print(f"  Winner: {winner} (ROI-Delta: {delta:+.2f}%)")

    # Summary statistics
    v2_wins = sum(1 for c in comparisons if c["comparison"]["winner_model"] == "V2")
    v1_wins = len(comparisons) - v2_wins
    avg_delta = sum(c["comparison"]["roi_delta_best"] for c in comparisons) / len(comparisons)

    result = {
        "analysis_date": datetime.now().isoformat(),
        "source_file": str(input_path.name),
        "draws_count": draws_count,
        "date_range": date_range,
        "typ_range": [6, 7, 8, 9, 10],
        "summary": {
            "v2_wins": v2_wins,
            "v1_wins": v1_wins,
            "avg_roi_delta_best": round(avg_delta, 2),
            "conclusion": f"V2 wins {v2_wins}/5 Typen with avg ROI-Delta of {avg_delta:+.2f}%",
        },
        "per_typ_comparison": comparisons,
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SUMMARY: V1 vs V2 for Typ 6-10")
    print(f"{'='*60}")
    print(f"V2 Wins: {v2_wins}/5 Typen")
    print(f"V1 Wins: {v1_wins}/5 Typen")
    print(f"Average ROI-Delta (best): {avg_delta:+.2f}%")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
