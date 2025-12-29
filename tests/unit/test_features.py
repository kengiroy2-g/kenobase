"""Unit Tests fuer Feature Engineering Module.

Testet:
- FeatureRegistry: Registrierung und Abruf von Features
- FeatureExtractor: Feature-Extraktion aus Ziehungsdaten
- FeatureStore: Speichern und Laden von Features
- FeaturePipeline: End-to-End Pipeline

Acceptance Criteria:
- Features >= 18 (PASS wenn >= 18 Features registriert)
- Coverage >= 80% (via pytest-cov)
- Performance < 5s/1000 draws
"""

from datetime import datetime
import tempfile
import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.features.registry import (
    FeatureRegistry,
    FeatureDefinition,
    FeatureCategory,
    register_feature,
)
from kenobase.features.extractor import FeatureExtractor, FeatureVector
from kenobase.features.store import FeatureStore, StorageFormat
from kenobase.features.pipeline import FeaturePipeline, PipelineConfig, PipelineResult


# ====================
# Test Fixtures
# ====================


@pytest.fixture
def sample_draws() -> list[DrawResult]:
    """Erstellt Sample-Ziehungsdaten fuer Tests."""
    from datetime import timedelta
    draws = []
    base_date = datetime(2024, 1, 1)

    # 100 simulierte Ziehungen
    for i in range(100):
        # Simulate somewhat realistic number distribution
        import random
        random.seed(i)  # Reproducible
        numbers = sorted(random.sample(range(1, 71), 20))

        draw_date = base_date + timedelta(days=i)

        draws.append(
            DrawResult(
                date=draw_date,
                numbers=numbers,
                bonus=[random.randint(0, 99999)],
                game_type=GameType.KENO,
                metadata={"index": i},
            )
        )

    return draws


@pytest.fixture
def temp_dir():
    """Erstellt temporaeres Verzeichnis fuer Tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ====================
# FeatureRegistry Tests
# ====================


class TestFeatureRegistry:
    """Tests fuer FeatureRegistry."""

    def test_singleton(self):
        """Registry ist ein Singleton."""
        reg1 = FeatureRegistry()
        reg2 = FeatureRegistry()
        assert reg1 is reg2

    def test_default_features_registered(self):
        """Mindestens 18 Features sind registriert."""
        registry = FeatureRegistry()
        assert registry.count() >= 18, f"Expected >= 18 features, got {registry.count()}"

    def test_get_feature(self):
        """Feature kann abgerufen werden."""
        registry = FeatureRegistry()
        freq_raw = registry.get("freq_raw")
        assert freq_raw is not None
        assert freq_raw.category == FeatureCategory.FREQUENCY

    def test_get_by_category(self):
        """Features nach Kategorie abrufen."""
        registry = FeatureRegistry()
        freq_features = registry.get_by_category(FeatureCategory.FREQUENCY)
        assert len(freq_features) >= 4  # freq_raw, freq_rolling, freq_hot, freq_cold

    def test_register_custom_feature(self):
        """Benutzerdefiniertes Feature kann registriert werden."""
        registry = FeatureRegistry()
        initial_count = registry.count()

        registry.register(
            FeatureDefinition(
                name="test_custom_feature",
                category=FeatureCategory.FREQUENCY,
                description="Test feature",
                weight=1.0,
            )
        )

        assert registry.count() == initial_count + 1
        assert registry.get("test_custom_feature") is not None

    def test_feature_names(self):
        """Alle Feature-Namen abrufen."""
        registry = FeatureRegistry()
        names = registry.feature_names
        assert "freq_raw" in names
        assert "duo_score" in names
        assert "law_a_score" in names


# ====================
# FeatureExtractor Tests
# ====================


class TestFeatureExtractor:
    """Tests fuer FeatureExtractor."""

    def test_extract_empty_draws(self):
        """Leere Draws geben leere Features."""
        extractor = FeatureExtractor()
        features = extractor.extract([])

        assert len(features) == 70  # Alle Zahlen
        for num, vec in features.items():
            assert vec.number == num
            assert vec.combined_score == 0.5  # Default

    def test_extract_features_count(self, sample_draws):
        """Extrahiert mindestens 18 Features."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        first_vec = features[1]
        assert len(first_vec.features) >= 18, f"Expected >= 18 features, got {len(first_vec.features)}"

    def test_feature_normalization(self, sample_draws):
        """Features sind auf 0-1 normalisiert."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num, vec in features.items():
            for name, value in vec.features.items():
                # Cluster signal kann -1 bis 1 sein
                if name == "cluster_signal":
                    assert -1.0 <= value <= 1.0, f"{name}={value} out of range"
                else:
                    assert 0.0 <= value <= 1.0, f"{name}={value} out of range"

    def test_tier_classification(self, sample_draws):
        """Tiers werden korrekt klassifiziert."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num, vec in features.items():
            assert vec.tier in ("A", "B", "C")

            if vec.combined_score >= 0.7:
                assert vec.tier == "A"
            elif vec.combined_score >= 0.5:
                assert vec.tier == "B"
            else:
                assert vec.tier == "C"

    def test_frequency_features(self, sample_draws):
        """Frequency-Features werden berechnet."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num in range(1, 71):
            vec = features[num]
            assert "freq_raw" in vec.features
            assert "freq_rolling" in vec.features
            assert "freq_hot" in vec.features
            assert "freq_cold" in vec.features

    def test_pattern_features(self, sample_draws):
        """Pattern-Features werden berechnet."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num in range(1, 71):
            vec = features[num]
            assert "duo_score" in vec.features
            assert "trio_score" in vec.features
            assert "quatro_score" in vec.features

    def test_temporal_features(self, sample_draws):
        """Temporal-Features werden berechnet."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num in range(1, 71):
            vec = features[num]
            assert "weekday_bias" in vec.features
            assert "month_bias" in vec.features
            assert "holiday_proximity" in vec.features

    def test_popularity_features(self, sample_draws):
        """Popularity-Features werden berechnet."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        # Birthday numbers (1-31)
        assert features[15].features["is_birthday"] == 1.0
        assert features[50].features["is_birthday"] == 0.0

        # Schoene Zahlen
        assert features[7].features["is_schoene"] == 1.0
        assert features[8].features["is_schoene"] == 0.0

    def test_stability_features(self, sample_draws):
        """Stability-Features (Model Law A) werden berechnet."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        for num in range(1, 71):
            vec = features[num]
            assert "law_a_score" in vec.features

    def test_performance(self, sample_draws):
        """Performance: < 5s fuer 100 Draws."""
        import time

        extractor = FeatureExtractor()

        start = time.time()
        features = extractor.extract(sample_draws)
        duration = time.time() - start

        # Scale to 1000 draws
        estimated_1000 = duration * 10
        assert estimated_1000 < 5.0, f"Estimated {estimated_1000:.2f}s for 1000 draws, expected < 5s"


# ====================
# FeatureStore Tests
# ====================


class TestFeatureStore:
    """Tests fuer FeatureStore."""

    def test_save_json(self, sample_draws, temp_dir):
        """Features koennen als JSON gespeichert werden."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        path = store.save(features, "test_features", format=StorageFormat.JSON)

        assert path.exists()
        assert path.suffix == ".json"

    def test_save_load_roundtrip(self, sample_draws, temp_dir):
        """Features koennen gespeichert und geladen werden."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        store.save(features, "roundtrip_test")

        loaded = store.load("roundtrip_test")

        assert len(loaded) == len(features)
        for num in range(1, 71):
            assert loaded[num].number == features[num].number
            assert abs(loaded[num].combined_score - features[num].combined_score) < 0.001

    def test_list_features(self, sample_draws, temp_dir):
        """Gespeicherte Feature-Sets koennen aufgelistet werden."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        store.save(features, "list_test_1")
        store.save(features, "list_test_2")

        names = store.list()
        assert "list_test_1" in names
        assert "list_test_2" in names

    def test_exists(self, sample_draws, temp_dir):
        """Existenz-Check funktioniert."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        store.save(features, "exists_test")

        assert store.exists("exists_test")
        assert not store.exists("nonexistent")

    def test_delete(self, sample_draws, temp_dir):
        """Feature-Sets koennen geloescht werden."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        store.save(features, "delete_test")

        assert store.exists("delete_test")
        store.delete("delete_test")
        assert not store.exists("delete_test")

    def test_to_dataframe(self, sample_draws, temp_dir):
        """Features koennen zu DataFrame konvertiert werden."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        store = FeatureStore(base_dir=temp_dir)
        df = store.to_dataframe(features)

        assert len(df) == 70
        assert "combined_score" in df.columns
        assert "tier" in df.columns


# ====================
# FeaturePipeline Tests
# ====================


class TestFeaturePipeline:
    """Tests fuer FeaturePipeline."""

    def test_config_defaults(self):
        """Pipeline hat sinnvolle Defaults."""
        pipeline = FeaturePipeline(game="keno")

        assert pipeline.config.game == "keno"
        assert pipeline.config.numbers_range == (1, 70)
        assert pipeline.config.numbers_to_draw == 20

    def test_run_with_draws(self, sample_draws, temp_dir):
        """Pipeline kann mit vorgeladenen Draws laufen."""
        config = PipelineConfig(
            game="keno",
            output_dir=temp_dir,
        )
        pipeline = FeaturePipeline(config=config)

        result = pipeline.run(draws=sample_draws, save=False)

        assert result.success
        assert result.draw_count == 100
        assert result.feature_count >= 18
        assert len(result.top_numbers) == 10

    def test_tier_distribution(self, sample_draws, temp_dir):
        """Tier-Distribution wird berechnet."""
        config = PipelineConfig(
            game="keno",
            output_dir=temp_dir,
        )
        pipeline = FeaturePipeline(config=config)

        result = pipeline.run(draws=sample_draws, save=False)

        assert "A" in result.tier_distribution
        assert "B" in result.tier_distribution
        assert "C" in result.tier_distribution

        total = sum(result.tier_distribution.values())
        assert total == 70

    def test_save_output(self, sample_draws, temp_dir):
        """Pipeline speichert Output."""
        config = PipelineConfig(
            game="keno",
            output_dir=temp_dir,
        )
        pipeline = FeaturePipeline(config=config)

        result = pipeline.run(draws=sample_draws, save=True, name="save_test")

        assert result.output_path is not None
        from pathlib import Path
        assert Path(result.output_path).exists()

    def test_result_to_dict(self, sample_draws, temp_dir):
        """PipelineResult kann zu Dict konvertiert werden."""
        config = PipelineConfig(
            game="keno",
            output_dir=temp_dir,
        )
        pipeline = FeaturePipeline(config=config)

        result = pipeline.run(draws=sample_draws, save=False)
        result_dict = result.to_dict()

        assert "success" in result_dict
        assert "feature_count" in result_dict
        assert "top_numbers" in result_dict


# ====================
# Integration Tests
# ====================


class TestIntegration:
    """Integration Tests fuer Feature Engineering."""

    def test_full_pipeline(self, sample_draws, temp_dir):
        """Voller Pipeline-Durchlauf."""
        # Configure
        config = PipelineConfig(
            game="keno",
            output_dir=temp_dir,
        )

        # Run pipeline
        pipeline = FeaturePipeline(config=config)
        result = pipeline.run(draws=sample_draws, save=True, name="integration_test")

        # Verify
        assert result.success
        assert result.feature_count >= 18

        # Load and verify
        store = FeatureStore(base_dir=temp_dir)
        loaded = store.load("integration_test")

        assert len(loaded) == 70
        assert all(vec.tier in ("A", "B", "C") for vec in loaded.values())

    def test_acceptance_criteria_features_count(self, sample_draws):
        """Acceptance Criteria: >= 18 Features."""
        extractor = FeatureExtractor()
        features = extractor.extract(sample_draws)

        first_vec = features[1]
        assert len(first_vec.features) >= 18, (
            f"FAIL: Expected >= 18 features, got {len(first_vec.features)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
