"""Feature Pipeline - Orchestriert den Feature-Engineering-Prozess.

Dieses Modul stellt die FeaturePipeline bereit, die:
1. Daten laedt (via DataLoader)
2. Features extrahiert (via FeatureExtractor)
3. Features speichert (via FeatureStore)
4. Mit HypothesisSynthesizer integriert

Verwendung:
    from kenobase.features import FeaturePipeline

    pipeline = FeaturePipeline(game="keno")
    result = pipeline.run()
    print(result.feature_count)  # 18
    print(result.top_numbers)    # [45, 23, ...]
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.features.extractor import FeatureExtractor, FeatureVector
from kenobase.features.store import FeatureStore, StorageFormat

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Konfiguration fuer die Feature-Pipeline.

    Attributes:
        game: Spieltyp (keno, eurojackpot, lotto)
        data_path: Pfad zur Datendatei
        results_dir: Verzeichnis fuer Hypothesen-Ergebnisse
        output_dir: Verzeichnis fuer Feature-Output
        numbers_range: Zahlenbereich (min, max)
        numbers_to_draw: Anzahl gezogener Zahlen
        hot_threshold: Schwelle fuer "hot" Klassifikation
        cold_threshold: Schwelle fuer "cold" Klassifikation
        rolling_window: Fenstergroesse fuer Rolling-Features
        stability_threshold: Schwelle fuer Model Law A
        storage_format: Format fuer Feature-Speicherung
    """

    game: str = "keno"
    data_path: Optional[str] = None
    results_dir: str = "results"
    output_dir: str = "data/features"
    numbers_range: tuple[int, int] = (1, 70)
    numbers_to_draw: int = 20
    hot_threshold: float = 0.37
    cold_threshold: float = 0.20
    rolling_window: int = 50
    stability_threshold: float = 0.90
    storage_format: StorageFormat = StorageFormat.JSON


@dataclass
class PipelineResult:
    """Ergebnis eines Pipeline-Durchlaufs.

    Attributes:
        success: Ob Pipeline erfolgreich war
        features: Dict mit Zahl -> FeatureVector
        feature_count: Anzahl extrahierter Features pro Zahl
        draw_count: Anzahl verarbeiteter Ziehungen
        duration_seconds: Laufzeit in Sekunden
        top_numbers: Top-10 Zahlen nach combined_score
        tier_distribution: Verteilung der Tiers (A/B/C)
        output_path: Pfad zur gespeicherten Datei
        errors: Aufgetretene Fehler
    """

    success: bool = True
    features: dict[int, FeatureVector] = field(default_factory=dict)
    feature_count: int = 0
    draw_count: int = 0
    duration_seconds: float = 0.0
    top_numbers: list[int] = field(default_factory=list)
    tier_distribution: dict[str, int] = field(default_factory=dict)
    output_path: Optional[str] = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary (ohne features fuer Summary)."""
        return {
            "success": self.success,
            "feature_count": self.feature_count,
            "draw_count": self.draw_count,
            "duration_seconds": round(self.duration_seconds, 3),
            "top_numbers": self.top_numbers,
            "tier_distribution": self.tier_distribution,
            "output_path": self.output_path,
            "errors": self.errors,
        }


class FeaturePipeline:
    """Orchestriert den Feature-Engineering-Prozess.

    Diese Klasse:
    1. Laedt Ziehungsdaten via DataLoader
    2. Laedt Hypothesen-Ergebnisse (wenn vorhanden)
    3. Extrahiert Features via FeatureExtractor
    4. Speichert Features via FeatureStore
    5. Integriert mit HypothesisSynthesizer

    Verwendung:
        pipeline = FeaturePipeline(game="keno")
        result = pipeline.run()
    """

    # Game-specific configurations
    GAME_CONFIGS = {
        "keno": {
            "numbers_range": (1, 70),
            "numbers_to_draw": 20,
            "hot_threshold": 0.37,
            "cold_threshold": 0.20,
            "data_file": "data/raw/keno/KENO_ab_2018.csv",
        },
        "eurojackpot": {
            "numbers_range": (1, 50),
            "numbers_to_draw": 5,
            "hot_threshold": 0.13,
            "cold_threshold": 0.07,
            "data_file": "data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv",
        },
        "lotto": {
            "numbers_range": (1, 49),
            "numbers_to_draw": 6,
            "hot_threshold": 0.16,
            "cold_threshold": 0.09,
            "data_file": "data/raw/lotto/Lotto_archiv_bereinigt.csv",
        },
    }

    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        game: str = "keno",
    ):
        """Initialisiert die Pipeline.

        Args:
            config: Pipeline-Konfiguration (optional)
            game: Spieltyp wenn keine Config angegeben
        """
        if config:
            self.config = config
        else:
            # Create config from game defaults
            game_cfg = self.GAME_CONFIGS.get(game, self.GAME_CONFIGS["keno"])
            self.config = PipelineConfig(
                game=game,
                data_path=game_cfg["data_file"],
                numbers_range=game_cfg["numbers_range"],
                numbers_to_draw=game_cfg["numbers_to_draw"],
                hot_threshold=game_cfg["hot_threshold"],
                cold_threshold=game_cfg["cold_threshold"],
            )

        self._loader = DataLoader()
        self._extractor = FeatureExtractor(
            numbers_range=self.config.numbers_range,
            numbers_to_draw=self.config.numbers_to_draw,
            hot_threshold=self.config.hot_threshold,
            cold_threshold=self.config.cold_threshold,
            rolling_window=self.config.rolling_window,
            stability_threshold=self.config.stability_threshold,
        )
        self._store = FeatureStore(
            base_dir=self.config.output_dir,
            default_format=self.config.storage_format,
        )

    def run(
        self,
        draws: Optional[list[DrawResult]] = None,
        save: bool = True,
        name: Optional[str] = None,
    ) -> PipelineResult:
        """Fuehrt die Feature-Pipeline aus.

        Args:
            draws: Optional vorgeladene Ziehungsdaten
            save: Ob Features gespeichert werden sollen
            name: Name fuer gespeicherte Features

        Returns:
            PipelineResult mit Features und Metriken
        """
        start_time = time.time()
        result = PipelineResult()

        try:
            # Step 1: Load data
            if draws is None:
                draws = self._load_draws()
            result.draw_count = len(draws)
            logger.info(f"Loaded {result.draw_count} draws")

            # Step 2: Load hypothesis results
            hyp_results = self._load_hypothesis_results()
            logger.info(f"Loaded {len(hyp_results)} hypothesis results")

            # Step 3: Extract features
            features = self._extractor.extract(draws, hyp_results)
            result.features = features

            # Step 4: Calculate metrics
            if features:
                first_vec = next(iter(features.values()))
                result.feature_count = len(first_vec.features)

            # Top numbers
            sorted_nums = sorted(
                features.items(),
                key=lambda x: x[1].combined_score,
                reverse=True,
            )
            result.top_numbers = [num for num, _ in sorted_nums[:10]]

            # Tier distribution
            tier_counts = {"A": 0, "B": 0, "C": 0}
            for vec in features.values():
                tier_counts[vec.tier] = tier_counts.get(vec.tier, 0) + 1
            result.tier_distribution = tier_counts

            # Step 5: Save features
            if save:
                feature_name = name or f"{self.config.game}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                output_path = self._store.save(
                    features,
                    feature_name,
                    metadata={
                        "game": self.config.game,
                        "draw_count": result.draw_count,
                        "feature_count": result.feature_count,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                result.output_path = str(output_path)
                logger.info(f"Saved features to {output_path}")

            result.success = True

        except FileNotFoundError as e:
            result.success = False
            result.errors.append(f"Data file not found: {e}")
            logger.error(f"Pipeline failed: {e}")

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Pipeline failed: {e}")

        result.duration_seconds = time.time() - start_time
        logger.info(
            f"Pipeline completed in {result.duration_seconds:.2f}s "
            f"(features={result.feature_count}, draws={result.draw_count})"
        )

        return result

    def _load_draws(self) -> list[DrawResult]:
        """Laedt Ziehungsdaten."""
        if not self.config.data_path:
            raise FileNotFoundError("No data path configured")

        path = Path(self.config.data_path)
        if not path.exists():
            # Try relative paths
            for base in [".", "data/raw"]:
                alt_path = Path(base) / path.name
                if alt_path.exists():
                    path = alt_path
                    break

        game_type = GameType(self.config.game)
        return self._loader.load(path, game_type=game_type)

    def _load_hypothesis_results(self) -> dict[str, dict]:
        """Laedt Hypothesen-Ergebnisse aus results/."""
        results = {}
        results_dir = Path(self.config.results_dir)

        if not results_dir.exists():
            logger.warning(f"Results directory not found: {results_dir}")
            return results

        for json_file in results_dir.glob("hyp*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    hyp_id = data.get("hypothesis", data.get("hypothesis_id", ""))
                    if hyp_id:
                        results[hyp_id] = data
                        logger.debug(f"Loaded {hyp_id} from {json_file.name}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load {json_file}: {e}")

        return results

    def get_synthesized_scores(self) -> dict[int, float]:
        """Gibt kombinierte Scores aus HypothesisSynthesizer zurueck.

        Returns:
            Dict mit Zahl -> combined_score
        """
        try:
            from kenobase.prediction.synthesizer import HypothesisSynthesizer

            synthesizer = HypothesisSynthesizer(
                results_dir=self.config.results_dir,
                numbers_range=self.config.numbers_range,
            )
            scores = synthesizer.synthesize()
            return {num: ns.combined_score for num, ns in scores.items()}
        except ImportError:
            logger.warning("HypothesisSynthesizer not available")
            return {}


__all__ = [
    "FeaturePipeline",
    "PipelineConfig",
    "PipelineResult",
]
