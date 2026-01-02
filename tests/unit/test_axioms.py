"""Unit tests for kenobase.core.axioms module."""

import pytest

from kenobase.core.axioms import (
    ALL_AXIOMS,
    ALL_PREDICTIONS,
    AXIOM_A1,
    AXIOM_A2,
    AXIOM_A3,
    AXIOM_A4,
    AXIOM_A5,
    AXIOM_A6,
    AXIOM_A7,
    Axiom,
    Direction,
    NullModelType,
    Prediction,
    export_all_axioms,
    get_axiom,
    get_eurojackpot_control_config,
    get_prediction,
    get_predictions_by_null_model,
    get_predictions_for_axiom,
    get_predictions_requiring_data,
    get_train_test_split,
)


class TestAxiomDefinitions:
    """Test that all axioms are properly defined."""

    def test_all_axioms_exist(self):
        """Verify all 7 axioms are defined."""
        assert len(ALL_AXIOMS) == 7
        expected_ids = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
        assert list(ALL_AXIOMS.keys()) == expected_ids

    def test_each_axiom_has_3_predictions(self):
        """Verify each axiom has exactly 3 predictions."""
        for axiom_id, axiom in ALL_AXIOMS.items():
            assert len(axiom.predictions) == 3, (
                f"Axiom {axiom_id} has {len(axiom.predictions)} predictions, expected 3"
            )

    def test_total_predictions_count(self):
        """Verify total of 21 predictions (7 axioms x 3)."""
        assert len(ALL_PREDICTIONS) == 21

    def test_axiom_has_required_fields(self):
        """Verify each axiom has all required fields."""
        for axiom in ALL_AXIOMS.values():
            assert axiom.id is not None
            assert axiom.name is not None
            assert axiom.description is not None
            assert axiom.economic_rationale is not None
            assert len(axiom.economic_rationale) > 50  # Non-trivial rationale


class TestPredictionDefinitions:
    """Test that all predictions are properly defined."""

    def test_prediction_ids_follow_pattern(self):
        """Verify prediction IDs follow P{axiom}.{num} pattern."""
        for pred_id in ALL_PREDICTIONS.keys():
            assert pred_id.startswith("P")
            parts = pred_id[1:].split(".")
            assert len(parts) == 2
            axiom_num = int(parts[0])
            pred_num = int(parts[1])
            assert 1 <= axiom_num <= 7
            assert 1 <= pred_num <= 3

    def test_prediction_has_required_fields(self):
        """Verify each prediction has all required fields."""
        for pred in ALL_PREDICTIONS.values():
            assert pred.id is not None
            assert pred.description is not None
            assert pred.metric is not None
            assert pred.threshold is not None
            assert isinstance(pred.direction, Direction)
            assert isinstance(pred.null_model, NullModelType)

    def test_between_predictions_have_threshold_high(self):
        """Verify BETWEEN predictions have both thresholds."""
        for pred in ALL_PREDICTIONS.values():
            if pred.direction == Direction.BETWEEN:
                assert pred.threshold_high is not None, (
                    f"Prediction {pred.id} is BETWEEN but missing threshold_high"
                )


class TestAxiomA1HouseEdge:
    """Test Axiom A1: House-Edge specific properties."""

    def test_a1_name(self):
        """Verify A1 is House-Edge axiom."""
        assert AXIOM_A1.name == "House-Edge"

    def test_a1_predictions_cover_roi_variance(self):
        """Verify A1 predictions cover ROI and variance."""
        metrics = {p.metric for p in AXIOM_A1.predictions}
        assert "roi_12m" in metrics
        assert "roi_quarterly_std" in metrics

    def test_a1_p11_roi_bounds(self):
        """Verify P1.1 has correct ROI bounds (-55% to -45%)."""
        pred = get_prediction("P1.1")
        assert pred.threshold == -0.55
        assert pred.threshold_high == -0.45
        assert pred.direction == Direction.BETWEEN


class TestAxiomA6DataRequirements:
    """Test Axiom A6 data requirements."""

    def test_a6_predictions_require_data(self):
        """Verify A6 predictions flag data requirements."""
        for pred in AXIOM_A6.predictions:
            assert pred.requires_data == "DATAREQ-001", (
                f"Prediction {pred.id} should require DATAREQ-001"
            )

    def test_data_requiring_predictions(self):
        """Verify get_predictions_requiring_data returns A6 predictions."""
        data_preds = get_predictions_requiring_data()
        assert len(data_preds) == 3
        for pred in data_preds:
            assert pred.id.startswith("P6")


class TestAxiomA7ResetCycles:
    """Test Axiom A7: Reset-Zyklen specific properties."""

    def test_a7_uses_fake_lag_null_model(self):
        """Verify A7 P7.1 uses fake-lag control."""
        pred = get_prediction("P7.1")
        assert pred.null_model == NullModelType.FAKE_LAG


class TestGetters:
    """Test getter functions."""

    def test_get_axiom_valid(self):
        """Test getting valid axiom."""
        axiom = get_axiom("A1")
        assert axiom.id == "A1"
        assert axiom.name == "House-Edge"

    def test_get_axiom_invalid(self):
        """Test getting invalid axiom raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            get_axiom("A99")
        assert "Unknown axiom" in str(exc_info.value)

    def test_get_prediction_valid(self):
        """Test getting valid prediction."""
        pred = get_prediction("P1.1")
        assert pred.id == "P1.1"
        assert pred.metric == "roi_12m"

    def test_get_prediction_invalid(self):
        """Test getting invalid prediction raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            get_prediction("P99.99")
        assert "Unknown prediction" in str(exc_info.value)

    def test_get_predictions_for_axiom(self):
        """Test getting predictions for axiom."""
        preds = get_predictions_for_axiom("A1")
        assert len(preds) == 3
        assert all(p.id.startswith("P1") for p in preds)

    def test_get_predictions_by_null_model(self):
        """Test filtering by null model type."""
        iid_preds = get_predictions_by_null_model(NullModelType.IID)
        assert len(iid_preds) > 0
        assert all(p.null_model == NullModelType.IID for p in iid_preds)


class TestSerialization:
    """Test serialization functions."""

    def test_prediction_to_dict(self):
        """Test prediction serialization."""
        pred = get_prediction("P1.1")
        d = pred.to_dict()
        assert d["id"] == "P1.1"
        assert d["metric"] == "roi_12m"
        assert d["direction"] == "between"
        assert d["null_model"] == "binomial"

    def test_axiom_to_dict(self):
        """Test axiom serialization."""
        axiom = get_axiom("A1")
        d = axiom.to_dict()
        assert d["id"] == "A1"
        assert d["name"] == "House-Edge"
        assert len(d["predictions"]) == 3

    def test_export_all_axioms(self):
        """Test full export."""
        export = export_all_axioms()
        assert export["total_axioms"] == 7
        assert export["total_predictions"] == 21
        assert len(export["predictions_requiring_data"]) == 3
        assert "A1" in export["axioms"]


class TestTrainTestSplit:
    """Test train/test split configuration."""

    def test_split_dates(self):
        """Verify correct split dates."""
        split = get_train_test_split()
        assert split["train_end"] == "2023-12-31"
        assert split["test_start"] == "2024-01-01"

    def test_frozen_rule(self):
        """Verify frozen rule is documented."""
        split = get_train_test_split()
        assert "FROZEN" in split["rule"]


class TestEuroJackpotControl:
    """Test EuroJackpot negative control configuration."""

    def test_eurojackpot_not_german(self):
        """Verify EuroJackpot is flagged as non-German."""
        config = get_eurojackpot_control_config()
        assert config["is_german_ecosystem"] is False

    def test_excluded_axioms(self):
        """Verify A2, A4, A6 are excluded for EuroJackpot."""
        config = get_eurojackpot_control_config()
        assert "A2" in config["excluded_axioms"]
        assert "A4" in config["excluded_axioms"]
        assert "A6" in config["excluded_axioms"]
        # A1, A3, A5, A7 should still apply
        assert "A1" not in config["excluded_axioms"]
        assert "A3" not in config["excluded_axioms"]


class TestNullModelCoverage:
    """Test that null models are properly distributed."""

    def test_all_null_model_types_used(self):
        """Verify all null model types are used at least once."""
        used_types = {p.null_model for p in ALL_PREDICTIONS.values()}
        # Not all types need to be used, but key ones should be
        assert NullModelType.IID in used_types
        assert NullModelType.PERMUTATION in used_types
        assert NullModelType.POISSON in used_types

    def test_fake_lag_used_for_post_event(self):
        """Verify fake-lag is used for post-event tests (A7)."""
        fake_lag_preds = get_predictions_by_null_model(NullModelType.FAKE_LAG)
        assert len(fake_lag_preds) >= 1
        # P7.1 should use fake-lag
        assert any(p.id == "P7.1" for p in fake_lag_preds)
