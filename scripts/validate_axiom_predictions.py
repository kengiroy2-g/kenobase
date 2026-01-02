#!/usr/bin/env python
"""
CLI Script for validating Axiom-First predictions.

Usage:
    python scripts/validate_axiom_predictions.py --help
    python scripts/validate_axiom_predictions.py --axiom A1
    python scripts/validate_axiom_predictions.py --all --output results/axiom_validation.json

Author: EXECUTOR (TASK AXIOM-001)
Date: 2025-12-30
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.core.axioms import (
    ALL_AXIOMS,
    ALL_PREDICTIONS,
    Axiom,
    Direction,
    NullModelType,
    Prediction,
    export_all_axioms,
    get_axiom,
    get_eurojackpot_control_config,
    get_predictions_for_axiom,
    get_predictions_requiring_data,
    get_train_test_split,
)


def validate_prediction(prediction: Prediction, data: Optional[dict] = None) -> dict:
    """
    Validate a single prediction against data.

    Args:
        prediction: The prediction to validate
        data: Optional data dict with observed values

    Returns:
        Validation result dict
    """
    result = {
        "prediction_id": prediction.id,
        "description": prediction.description,
        "metric": prediction.metric,
        "threshold": prediction.threshold,
        "threshold_high": prediction.threshold_high,
        "direction": prediction.direction.value,
        "null_model": prediction.null_model.value,
        "requires_data": prediction.requires_data,
        "status": "NOT_TESTED",
        "observed_value": None,
        "p_value": None,
        "is_falsified": None,
        "notes": [],
    }

    # Check for data requirements
    if prediction.requires_data is not None:
        result["status"] = "BLOCKED"
        result["notes"].append(f"Requires external data: {prediction.requires_data}")
        return result

    # If no data provided, mark as not tested
    if data is None:
        result["status"] = "NOT_TESTED"
        result["notes"].append("No data provided for validation")
        return result

    # Get observed value from data
    if prediction.metric not in data:
        result["status"] = "NOT_TESTED"
        result["notes"].append(f"Metric '{prediction.metric}' not found in data")
        return result

    observed = data[prediction.metric]
    result["observed_value"] = observed

    # Evaluate against threshold
    if prediction.direction == Direction.LESS:
        is_falsified = observed >= prediction.threshold
    elif prediction.direction == Direction.GREATER:
        is_falsified = observed <= prediction.threshold
    elif prediction.direction == Direction.BETWEEN:
        is_falsified = (
            observed < prediction.threshold or
            observed > prediction.threshold_high
        )
    elif prediction.direction == Direction.NOT_EQUAL:
        is_falsified = observed == prediction.threshold
    else:
        is_falsified = None
        result["notes"].append(f"Unknown direction: {prediction.direction}")

    result["is_falsified"] = is_falsified
    result["status"] = "FALSIFIED" if is_falsified else "SUPPORTED"

    return result


def validate_axiom(axiom: Axiom, data: Optional[dict] = None) -> dict:
    """
    Validate all predictions for an axiom.

    Args:
        axiom: The axiom to validate
        data: Optional data dict with observed values

    Returns:
        Validation results dict
    """
    results = {
        "axiom_id": axiom.id,
        "axiom_name": axiom.name,
        "description": axiom.description,
        "predictions": [],
        "summary": {
            "total": len(axiom.predictions),
            "supported": 0,
            "falsified": 0,
            "blocked": 0,
            "not_tested": 0,
        },
    }

    for pred in axiom.predictions:
        pred_result = validate_prediction(pred, data)
        results["predictions"].append(pred_result)

        if pred_result["status"] == "SUPPORTED":
            results["summary"]["supported"] += 1
        elif pred_result["status"] == "FALSIFIED":
            results["summary"]["falsified"] += 1
        elif pred_result["status"] == "BLOCKED":
            results["summary"]["blocked"] += 1
        else:
            results["summary"]["not_tested"] += 1

    return results


def run_validation(
    axiom_ids: Optional[list[str]] = None,
    data: Optional[dict] = None,
) -> dict:
    """
    Run validation for specified axioms or all axioms.

    Args:
        axiom_ids: List of axiom IDs to validate, or None for all
        data: Optional data dict with observed values

    Returns:
        Full validation report
    """
    if axiom_ids is None:
        axiom_ids = list(ALL_AXIOMS.keys())

    report = {
        "timestamp": datetime.now().isoformat(),
        "train_test_split": get_train_test_split(),
        "eurojackpot_control": get_eurojackpot_control_config(),
        "axioms_validated": axiom_ids,
        "results": [],
        "overall_summary": {
            "total_predictions": 0,
            "supported": 0,
            "falsified": 0,
            "blocked": 0,
            "not_tested": 0,
        },
    }

    for axiom_id in axiom_ids:
        axiom = get_axiom(axiom_id)
        axiom_result = validate_axiom(axiom, data)
        report["results"].append(axiom_result)

        # Update overall summary
        report["overall_summary"]["total_predictions"] += axiom_result["summary"]["total"]
        report["overall_summary"]["supported"] += axiom_result["summary"]["supported"]
        report["overall_summary"]["falsified"] += axiom_result["summary"]["falsified"]
        report["overall_summary"]["blocked"] += axiom_result["summary"]["blocked"]
        report["overall_summary"]["not_tested"] += axiom_result["summary"]["not_tested"]

    return report


def print_report(report: dict, verbose: bool = False) -> None:
    """Print validation report to console."""
    print("\n" + "=" * 60)
    print("AXIOM-FIRST FRAMEWORK VALIDATION REPORT")
    print("=" * 60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Train/Test Split: {report['train_test_split']['train_end']} | {report['train_test_split']['test_start']}")
    print()

    # Overall summary
    summary = report["overall_summary"]
    print("OVERALL SUMMARY:")
    print(f"  Total Predictions: {summary['total_predictions']}")
    print(f"  Supported:         {summary['supported']}")
    print(f"  Falsified:         {summary['falsified']}")
    print(f"  Blocked:           {summary['blocked']}")
    print(f"  Not Tested:        {summary['not_tested']}")
    print()

    # Per-axiom results
    for axiom_result in report["results"]:
        print("-" * 60)
        print(f"Axiom {axiom_result['axiom_id']}: {axiom_result['axiom_name']}")
        print(f"  {axiom_result['description']}")
        s = axiom_result["summary"]
        print(f"  Status: {s['supported']} supported, {s['falsified']} falsified, {s['blocked']} blocked, {s['not_tested']} not tested")

        if verbose:
            for pred in axiom_result["predictions"]:
                status_symbol = {
                    "SUPPORTED": "[OK]",
                    "FALSIFIED": "[FAIL]",
                    "BLOCKED": "[BLOCK]",
                    "NOT_TESTED": "[--]",
                }.get(pred["status"], "[?]")
                print(f"    {status_symbol} {pred['prediction_id']}: {pred['description'][:50]}...")
                if pred["observed_value"] is not None:
                    print(f"         Observed: {pred['observed_value']}, Threshold: {pred['threshold']}")
                if pred["notes"]:
                    for note in pred["notes"]:
                        print(f"         Note: {note}")
        print()

    # Data requirements
    data_preds = get_predictions_requiring_data()
    if data_preds:
        print("-" * 60)
        print("DATA REQUIREMENTS (DATAREQ-001):")
        for pred in data_preds:
            print(f"  {pred.id}: {pred.description[:60]}...")
    print()

    # EuroJackpot control
    ejc = report["eurojackpot_control"]
    print("-" * 60)
    print("EUROJACKPOT NEGATIVE CONTROL:")
    print(f"  Excluded Axioms: {', '.join(ejc['excluded_axioms'])}")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Axiom-First predictions for Kenobase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_axiom_predictions.py --list
  python scripts/validate_axiom_predictions.py --axiom A1
  python scripts/validate_axiom_predictions.py --axiom A1 A7 --verbose
  python scripts/validate_axiom_predictions.py --all --output results/axiom_validation.json
        """,
    )

    parser.add_argument(
        "--axiom",
        nargs="+",
        metavar="ID",
        help="Axiom ID(s) to validate (A1-A7)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all axioms",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all axioms and predictions",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file for results",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with prediction details",
    )
    parser.add_argument(
        "--export-definitions",
        type=Path,
        help="Export axiom/prediction definitions to JSON",
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        print("\nAXIOM-FIRST FRAMEWORK - Definitions")
        print("=" * 60)
        for axiom_id, axiom in ALL_AXIOMS.items():
            print(f"\n{axiom_id}: {axiom.name}")
            print(f"  {axiom.description}")
            for pred in axiom.predictions:
                print(f"    {pred.id}: {pred.description[:50]}...")
                print(f"         Metric: {pred.metric}, Threshold: {pred.threshold}, Null: {pred.null_model.value}")
        print(f"\nTotal: {len(ALL_AXIOMS)} axioms, {len(ALL_PREDICTIONS)} predictions")
        return 0

    # Handle --export-definitions
    if args.export_definitions:
        export = export_all_axioms()
        args.export_definitions.parent.mkdir(parents=True, exist_ok=True)
        with open(args.export_definitions, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)
        print(f"Definitions exported to: {args.export_definitions}")
        return 0

    # Determine which axioms to validate
    if args.all:
        axiom_ids = list(ALL_AXIOMS.keys())
    elif args.axiom:
        axiom_ids = args.axiom
        # Validate axiom IDs
        for aid in axiom_ids:
            if aid not in ALL_AXIOMS:
                print(f"Error: Unknown axiom '{aid}'. Valid: {list(ALL_AXIOMS.keys())}")
                return 1
    else:
        parser.print_help()
        return 0

    # Run validation (currently without data - placeholder for future implementation)
    report = run_validation(axiom_ids=axiom_ids, data=None)

    # Print report
    print_report(report, verbose=args.verbose)

    # Save to file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
