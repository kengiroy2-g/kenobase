"""Feature Engineering Module - Kombiniert alle Analyse-Module zu per-number Features.

Dieses Package stellt eine unified Feature-Engineering-Pipeline bereit,
die alle verfuegbaren Analyse-Module zu einem Feature-Vektor pro Zahl kombiniert.

Hauptkomponenten:
- FeatureRegistry: Zentrale Registrierung aller Feature-Extraktoren
- FeatureExtractor: Extrahiert Features aus Rohdaten
- FeatureStore: Speichert und laedt Feature-Vektoren
- FeaturePipeline: Orchestriert den gesamten Feature-Engineering-Prozess

Verwendung:
    from kenobase.features import FeaturePipeline

    pipeline = FeaturePipeline(game="keno")
    features = pipeline.run(draws)
    # features: Dict[int, FeatureVector] mit Zahl 1-70 als Key
"""

from kenobase.features.extractor import (
    FeatureExtractor,
    FeatureVector,
    FeatureCategory,
)
from kenobase.features.registry import (
    FeatureRegistry,
    FeatureDefinition,
    register_feature,
)
from kenobase.features.store import (
    FeatureStore,
    StorageFormat,
)
from kenobase.features.pipeline import (
    FeaturePipeline,
    PipelineConfig,
    PipelineResult,
)

__all__ = [
    # Extractor
    "FeatureExtractor",
    "FeatureVector",
    "FeatureCategory",
    # Registry
    "FeatureRegistry",
    "FeatureDefinition",
    "register_feature",
    # Store
    "FeatureStore",
    "StorageFormat",
    # Pipeline
    "FeaturePipeline",
    "PipelineConfig",
    "PipelineResult",
]
