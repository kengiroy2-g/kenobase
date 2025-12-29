"""Feature Store - Speichert und laedt Feature-Vektoren.

Dieses Modul stellt den FeatureStore bereit, der Feature-Vektoren
persistent speichert und laedt. Unterstuetzte Formate:
- JSON: Menschenlesbar, gut fuer Debugging
- Pickle: Schnell, gut fuer Produktion
- Parquet: Effizient fuer grosse Datensaetze
"""

from __future__ import annotations

import json
import logging
import pickle
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from kenobase.features.extractor import FeatureVector

logger = logging.getLogger(__name__)


class StorageFormat(str, Enum):
    """Unterstuetzte Speicherformate."""

    JSON = "json"
    PICKLE = "pickle"
    PARQUET = "parquet"


class FeatureStore:
    """Persistenter Speicher fuer Feature-Vektoren.

    Verwendung:
        store = FeatureStore("data/features")
        store.save(features, "keno_2024")
        loaded = store.load("keno_2024")
    """

    def __init__(
        self,
        base_dir: str = "data/features",
        default_format: StorageFormat = StorageFormat.JSON,
    ):
        """Initialisiert den FeatureStore.

        Args:
            base_dir: Basis-Verzeichnis fuer Feature-Dateien
            default_format: Standard-Speicherformat
        """
        self.base_dir = Path(base_dir)
        self.default_format = default_format
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        features: dict[int, FeatureVector],
        name: str,
        format: Optional[StorageFormat] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Path:
        """Speichert Feature-Vektoren.

        Args:
            features: Dict mit Zahl -> FeatureVector
            name: Name fuer die Speicherdatei (ohne Extension)
            format: Speicherformat (default: self.default_format)
            metadata: Zusaetzliche Metadaten

        Returns:
            Pfad zur gespeicherten Datei
        """
        fmt = format or self.default_format
        timestamp = datetime.now().isoformat()

        data = {
            "name": name,
            "timestamp": timestamp,
            "format_version": "1.0",
            "count": len(features),
            "metadata": metadata or {},
            "features": {
                str(num): vec.to_dict() for num, vec in features.items()
            },
        }

        if fmt == StorageFormat.JSON:
            return self._save_json(data, name)
        elif fmt == StorageFormat.PICKLE:
            return self._save_pickle(data, name)
        elif fmt == StorageFormat.PARQUET:
            return self._save_parquet(features, name, metadata)
        else:
            raise ValueError(f"Unknown format: {fmt}")

    def _save_json(self, data: dict, name: str) -> Path:
        """Speichert als JSON."""
        path = self.base_dir / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved features to {path}")
        return path

    def _save_pickle(self, data: dict, name: str) -> Path:
        """Speichert als Pickle."""
        path = self.base_dir / f"{name}.pkl"
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Saved features to {path}")
        return path

    def _save_parquet(
        self,
        features: dict[int, FeatureVector],
        name: str,
        metadata: Optional[dict] = None,
    ) -> Path:
        """Speichert als Parquet."""
        # Convert to DataFrame
        rows = []
        for num, vec in features.items():
            row = {"number": num, "combined_score": vec.combined_score, "tier": vec.tier}
            row.update(vec.features)
            rows.append(row)

        df = pd.DataFrame(rows)
        path = self.base_dir / f"{name}.parquet"
        df.to_parquet(path, index=False)

        # Save metadata separately
        if metadata:
            meta_path = self.base_dir / f"{name}_meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

        logger.info(f"Saved features to {path}")
        return path

    def load(
        self,
        name: str,
        format: Optional[StorageFormat] = None,
    ) -> dict[int, FeatureVector]:
        """Laedt Feature-Vektoren.

        Args:
            name: Name der Speicherdatei (ohne Extension)
            format: Speicherformat (wird automatisch erkannt wenn None)

        Returns:
            Dict mit Zahl -> FeatureVector
        """
        # Auto-detect format
        if format is None:
            for fmt in StorageFormat:
                ext = fmt.value if fmt != StorageFormat.PICKLE else "pkl"
                path = self.base_dir / f"{name}.{ext}"
                if path.exists():
                    format = fmt
                    break

        if format is None:
            raise FileNotFoundError(f"No feature file found for: {name}")

        if format == StorageFormat.JSON:
            return self._load_json(name)
        elif format == StorageFormat.PICKLE:
            return self._load_pickle(name)
        elif format == StorageFormat.PARQUET:
            return self._load_parquet(name)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _load_json(self, name: str) -> dict[int, FeatureVector]:
        """Laedt aus JSON."""
        path = self.base_dir / f"{name}.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        features: dict[int, FeatureVector] = {}
        for num_str, vec_dict in data.get("features", {}).items():
            num = int(num_str)
            features[num] = FeatureVector(
                number=vec_dict["number"],
                features=vec_dict.get("features", {}),
                combined_score=vec_dict.get("combined_score", 0.5),
                tier=vec_dict.get("tier", "C"),
                metadata=vec_dict.get("metadata", {}),
            )

        logger.info(f"Loaded {len(features)} features from {path}")
        return features

    def _load_pickle(self, name: str) -> dict[int, FeatureVector]:
        """Laedt aus Pickle."""
        path = self.base_dir / f"{name}.pkl"
        with open(path, "rb") as f:
            data = pickle.load(f)

        features: dict[int, FeatureVector] = {}
        for num_str, vec_dict in data.get("features", {}).items():
            num = int(num_str)
            features[num] = FeatureVector(
                number=vec_dict["number"],
                features=vec_dict.get("features", {}),
                combined_score=vec_dict.get("combined_score", 0.5),
                tier=vec_dict.get("tier", "C"),
                metadata=vec_dict.get("metadata", {}),
            )

        logger.info(f"Loaded {len(features)} features from {path}")
        return features

    def _load_parquet(self, name: str) -> dict[int, FeatureVector]:
        """Laedt aus Parquet."""
        path = self.base_dir / f"{name}.parquet"
        df = pd.read_parquet(path)

        # Identify feature columns (not number, combined_score, tier)
        meta_cols = {"number", "combined_score", "tier"}
        feature_cols = [c for c in df.columns if c not in meta_cols]

        features: dict[int, FeatureVector] = {}
        for _, row in df.iterrows():
            num = int(row["number"])
            feature_dict = {col: float(row[col]) for col in feature_cols}
            features[num] = FeatureVector(
                number=num,
                features=feature_dict,
                combined_score=float(row["combined_score"]),
                tier=str(row["tier"]),
            )

        logger.info(f"Loaded {len(features)} features from {path}")
        return features

    def list(self) -> list[str]:
        """Listet alle gespeicherten Feature-Sets.

        Returns:
            Liste von Namen (ohne Extension)
        """
        names = set()
        for ext in ["json", "pkl", "parquet"]:
            for path in self.base_dir.glob(f"*.{ext}"):
                names.add(path.stem)
        return sorted(names)

    def exists(self, name: str) -> bool:
        """Prueft ob ein Feature-Set existiert.

        Args:
            name: Name des Feature-Sets

        Returns:
            True wenn vorhanden
        """
        for ext in ["json", "pkl", "parquet"]:
            if (self.base_dir / f"{name}.{ext}").exists():
                return True
        return False

    def delete(self, name: str) -> bool:
        """Loescht ein Feature-Set.

        Args:
            name: Name des Feature-Sets

        Returns:
            True wenn geloescht
        """
        deleted = False
        for ext in ["json", "pkl", "parquet"]:
            path = self.base_dir / f"{name}.{ext}"
            if path.exists():
                path.unlink()
                deleted = True
                logger.info(f"Deleted {path}")

        # Also delete metadata file if exists
        meta_path = self.base_dir / f"{name}_meta.json"
        if meta_path.exists():
            meta_path.unlink()

        return deleted

    def to_dataframe(self, features: dict[int, FeatureVector]) -> pd.DataFrame:
        """Konvertiert Features zu DataFrame.

        Args:
            features: Dict mit Zahl -> FeatureVector

        Returns:
            DataFrame mit Zahlen als Index
        """
        rows = []
        for num, vec in sorted(features.items()):
            row = {
                "number": num,
                "combined_score": vec.combined_score,
                "tier": vec.tier,
            }
            row.update(vec.features)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.set_index("number", inplace=True)
        return df


__all__ = [
    "FeatureStore",
    "StorageFormat",
]
