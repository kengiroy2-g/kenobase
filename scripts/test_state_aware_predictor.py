#!/usr/bin/env python
"""Validation script for StateAwarePredictor.

Repro command for TASK_004:
    python scripts/test_state_aware_predictor.py

Output:
    results/state_aware_validation.json

Validates:
    1. StateAwarePredictor fits on real KENO data
    2. State-aware F1 >= EnsemblePredictor baseline F1
    3. State labels match economic_state module
    4. Per-state metrics are computed
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.data_loader import DataLoader
from kenobase.core.economic_state import EconomicState
from kenobase.prediction.state_aware import (
    StateAwarePredictor,
    DEFAULT_STATE_ALPHAS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run StateAwarePredictor validation."""
    logger.info("=== StateAwarePredictor Validation ===")

    # Output path
    output_path = PROJECT_ROOT / "results" / "state_aware_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    validation_result = {
        "timestamp": datetime.now().isoformat(),
        "task": "TASK_004",
        "status": "PENDING",
        "checks": {},
        "metrics": {},
        "errors": [],
    }

    try:
        # 1. Load data
        logger.info("Loading KENO data...")
        loader = DataLoader()
        data_path = PROJECT_ROOT / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

        if not data_path.exists():
            # Fallback to alternative path
            data_path = PROJECT_ROOT / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

        if not data_path.exists():
            raise FileNotFoundError(f"KENO data not found at {data_path}")

        draws = loader.load(str(data_path))
        logger.info(f"Loaded {len(draws)} draws")

        validation_result["metrics"]["n_draws"] = len(draws)

        # 2. Initialize StateAwarePredictor
        logger.info("Initializing StateAwarePredictor...")
        predictor = StateAwarePredictor(
            state_alphas=DEFAULT_STATE_ALPHAS,
            numbers_range=(1, 70),
            numbers_to_draw=20,
            results_dir=str(PROJECT_ROOT / "results"),
        )

        validation_result["checks"]["predictor_init"] = True

        # 3. Fit predictor
        logger.info("Fitting StateAwarePredictor...")
        report = predictor.fit(draws, tune_hyperparameters=False, n_cv_folds=3)

        validation_result["checks"]["predictor_fit"] = True

        # 4. Extract metrics
        logger.info("Extracting metrics...")

        baseline_f1 = report.baseline_f1
        overall_f1 = report.overall_f1

        validation_result["metrics"]["baseline_f1"] = baseline_f1
        validation_result["metrics"]["overall_f1"] = overall_f1
        validation_result["metrics"]["f1_improvement"] = overall_f1 - baseline_f1

        # 5. Check acceptance criteria
        logger.info("Checking acceptance criteria...")

        # Criterion 1: F1 >= baseline
        f1_check = overall_f1 >= baseline_f1
        validation_result["checks"]["f1_geq_baseline"] = f1_check

        if not f1_check:
            logger.warning(
                f"F1 check FAILED: overall_f1={overall_f1:.4f} < baseline_f1={baseline_f1:.4f}"
            )

        # Criterion 2: State labels match economic_state
        valid_states = {"NORMAL", "COOLDOWN", "RECOVERY", "HOT"}
        states_valid = all(
            s.state_label in valid_states for s in predictor._economic_states
        )
        validation_result["checks"]["state_labels_valid"] = states_valid

        # 6. Per-state metrics
        validation_result["metrics"]["state_distribution"] = report.state_distribution
        validation_result["metrics"]["state_metrics"] = report.state_metrics
        validation_result["metrics"]["state_alphas"] = report.state_alphas

        # 7. Test predict
        logger.info("Testing predict...")
        predictions = predictor.predict(draws, top_n=10)

        validation_result["checks"]["predict_works"] = len(predictions) == 10
        validation_result["metrics"]["sample_predictions"] = [
            p.to_dict() for p in predictions[:3]
        ]

        # 8. Test predict with explicit state
        logger.info("Testing predict with explicit state...")
        cooldown_state = EconomicState(
            date=datetime.now(),
            spieleinsatz=500_000.0,
            jackpot=2_000_000.0,
            rolling_cv=0.6,
            state_label="COOLDOWN",
        )
        predictions_cooldown = predictor.predict(
            draws, top_n=10, current_state=cooldown_state
        )

        cooldown_check = all(p.state_label == "COOLDOWN" for p in predictions_cooldown)
        validation_result["checks"]["explicit_state_works"] = cooldown_check

        # 9. Overall status
        all_checks_passed = all(validation_result["checks"].values())
        validation_result["status"] = "PASS" if all_checks_passed else "FAIL"

        logger.info(f"Validation status: {validation_result['status']}")

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        validation_result["status"] = "ERROR"
        validation_result["errors"].append(str(e))

    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Results saved to {output_path}")

    # Return exit code
    if validation_result["status"] == "PASS":
        logger.info("=== VALIDATION PASSED ===")
        return 0
    else:
        logger.error("=== VALIDATION FAILED ===")
        return 1


if __name__ == "__main__":
    sys.exit(main())
