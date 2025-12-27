#!/usr/bin/env python
"""Smoke Tests fuer Kenobase V2.0.

Schnelle Tests um kritische Pfade zu verifizieren.
Diese Tests sollten in unter 30 Sekunden durchlaufen.

Usage:
    python tests/smoke_test.py
    pytest tests/smoke_test.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def smoke_test_imports() -> bool:
    """Test: Alle kritischen Module koennen importiert werden."""
    try:
        from kenobase import __version__
        from kenobase.core.config import KenobaseConfig, load_config
        from kenobase.core.data_loader import DataLoader, DrawResult, GameType
        from kenobase.core.number_pool import NumberPoolGenerator
        from kenobase.core.combination_engine import CombinationEngine
        from kenobase.analysis.frequency import (
            FrequencyResult,
            calculate_frequency,
            calculate_pair_frequency,
        )
        from kenobase.analysis.pattern import (
            PatternResult,
            extract_patterns,
            extract_patterns_from_draws,
        )
        from kenobase.physics.model_laws import is_law, calculate_criticality
        from kenobase.physics.avalanche import (
            calculate_theta,
            get_avalanche_state,
            is_profitable,
        )
        from kenobase.physics.metrics import calculate_hurst_exponent
        from kenobase.pipeline.runner import PipelineRunner, run_pipeline
        from kenobase.pipeline.output_formats import OutputFormatter

        print(f"[OK] All imports successful (version: {__version__})")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def smoke_test_config() -> bool:
    """Test: Config-System funktioniert."""
    try:
        from kenobase.core.config import KenobaseConfig

        config = KenobaseConfig()

        assert config.version == "2.0.0"
        assert config.physics.enable_model_laws is True
        assert config.physics.enable_avalanche is True
        assert config.analysis.min_frequency_threshold >= 0

        print("[OK] Config system works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Config error: {e}")
        return False


def smoke_test_physics_stability() -> bool:
    """Test: Physics Law A (Stability) funktioniert."""
    try:
        from kenobase.physics.model_laws import is_law

        # Stabile Relation (konstante Ausgabe)
        def stable_fn(**kwargs) -> float:
            return 1.0

        variations = [{"x": i} for i in range(5)]
        stability, is_stable = is_law(stable_fn, variations, threshold=0.9)

        assert stability >= 0.99  # Perfekt stabil
        assert is_stable == True  # Use == for numpy compatibility

        # Instabile Relation
        def unstable_fn(**kwargs) -> float:
            return kwargs.get("x", 0) * 0.5

        stability_bad, is_stable_bad = is_law(unstable_fn, variations, threshold=0.9)
        assert is_stable_bad == False  # Use == for numpy compatibility

        print("[OK] Physics stability (Law A) works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Physics stability error: {e}")
        return False


def smoke_test_physics_criticality() -> bool:
    """Test: Physics Law C (Criticality) funktioniert."""
    try:
        from kenobase.physics.model_laws import calculate_criticality

        # Niedrige Criticality (weit von 0.5 entfernt)
        score_low, level_low = calculate_criticality(0.1, regime_complexity=1)
        assert level_low == "LOW"

        # Hohe Criticality (nahe 0.5, hohe Komplexitaet)
        score_high, level_high = calculate_criticality(0.5, regime_complexity=3)
        assert score_high > score_low

        print("[OK] Physics criticality (Law C) works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Physics criticality error: {e}")
        return False


def smoke_test_physics_avalanche() -> bool:
    """Test: Physics Avalanche-Berechnung funktioniert."""
    try:
        from kenobase.physics.avalanche import (
            calculate_theta,
            get_avalanche_state,
            is_profitable,
        )

        # SAFE: 2 Picks mit 80% Precision
        theta_safe = calculate_theta(0.8, 2)
        state_safe = get_avalanche_state(theta_safe)
        assert state_safe == "SAFE"

        # CRITICAL: 6 Picks mit 70% Precision
        theta_crit = calculate_theta(0.7, 6)
        state_crit = get_avalanche_state(theta_crit)
        assert state_crit == "CRITICAL"

        # Profitabilitaet
        assert is_profitable(0.5, 2.5) is True  # 0.5 * 2.5 = 1.25 > 1
        assert is_profitable(0.3, 2.0) is False  # 0.3 * 2.0 = 0.6 < 1

        print("[OK] Physics avalanche works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Physics avalanche error: {e}")
        return False


def smoke_test_physics_hurst() -> bool:
    """Test: Hurst-Exponent Berechnung funktioniert."""
    try:
        from kenobase.physics.metrics import calculate_hurst_exponent
        import random

        # Random walk should have H ~ 0.5
        random.seed(42)
        data = [random.gauss(0, 1) for _ in range(100)]

        hurst = calculate_hurst_exponent(data)
        assert 0.0 <= hurst <= 1.0

        print(f"[OK] Hurst exponent calculation works (H={hurst:.3f})")
        return True
    except Exception as e:
        print(f"[FAIL] Hurst calculation error: {e}")
        return False


def smoke_test_combination_engine() -> bool:
    """Test: Kombinations-Engine funktioniert."""
    try:
        from kenobase.core.combination_engine import CombinationEngine

        pool = {1, 5, 12, 23, 34, 45, 56, 67, 8, 15}  # Must be a set
        engine = CombinationEngine(
            pool=pool,
            combination_size=6,
            max_per_decade=3,
            min_sum=100,
        )

        combinations = list(engine.generate())

        # Should generate combinations
        assert len(combinations) > 0

        # Each should have 6 numbers
        for combo in combinations:
            assert len(combo.numbers) == 6

        print(f"[OK] Combination engine works ({len(combinations)} combos from pool of {len(pool)})")
        return True
    except Exception as e:
        print(f"[FAIL] Combination engine error: {e}")
        return False


def smoke_test_number_pool() -> bool:
    """Test: Number Pool Generator funktioniert."""
    try:
        from datetime import timedelta
        from kenobase.core.number_pool import NumberPoolGenerator
        from kenobase.core.data_loader import DrawResult, GameType

        # Sample draws (need 30 for 3 periods of 10)
        base_date = datetime(2024, 1, 1)
        draws = []
        for i in range(30):
            base = (i * 3) % 50
            numbers = [(base + j) % 70 + 1 for j in range(20)]
            draws.append(
                DrawResult(
                    date=base_date + timedelta(days=i),
                    numbers=numbers,
                    bonus=[],
                    game_type=GameType.KENO,
                )
            )

        generator = NumberPoolGenerator(
            n_periods=3,
            draws_per_period=10,
            top_n_per_period=11,
            top_n_total=20,
        )
        pool = generator.generate(draws)

        assert len(pool) > 0
        assert all(isinstance(n, int) for n in pool)

        print(f"[OK] Number pool generation works (pool size: {len(pool)})")
        return True
    except Exception as e:
        print(f"[FAIL] Number pool error: {e}")
        return False


def smoke_test_frequency_analysis() -> bool:
    """Test: Frequency Analysis funktioniert."""
    try:
        from datetime import datetime, timedelta
        from kenobase.analysis.frequency import calculate_frequency
        from kenobase.core.data_loader import DrawResult, GameType

        # Create DrawResult objects
        base_date = datetime(2024, 1, 1)
        draws = [
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=[1, 2, 3, 4, 5] if i == 0 else [1, 2, 3, 6, 7] if i == 1 else [1, 2, 8, 9, 10],
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(3)
        ]

        results = calculate_frequency(draws)

        # Number 1 should appear 3 times
        freq_1 = next((r for r in results if r.number == 1), None)
        assert freq_1 is not None
        assert freq_1.absolute_frequency == 3

        print("[OK] Frequency analysis works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Frequency analysis error: {e}")
        return False


def smoke_test_pipeline() -> bool:
    """Test: Pipeline Runner funktioniert End-to-End."""
    try:
        from datetime import timedelta
        from kenobase.core.config import KenobaseConfig
        from kenobase.core.data_loader import DrawResult, GameType
        from kenobase.pipeline.runner import PipelineRunner

        config = KenobaseConfig()
        base_date = datetime(2024, 1, 1)

        # Erstelle Test-Ziehungen
        draws = [
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=[(i + j) % 70 + 1 for j in range(20)],
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(20)
        ]

        runner = PipelineRunner(config)
        result = runner.run(draws)

        assert result.draws_count == 20
        assert result.timestamp is not None
        assert len(result.frequency_results) > 0
        assert result.physics_result is not None

        print("[OK] Pipeline end-to-end works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Pipeline error: {e}")
        return False


def smoke_test_cli_help() -> bool:
    """Test: CLI --help funktioniert."""
    try:
        import subprocess

        scripts_dir = PROJECT_ROOT / "scripts"
        analyze_script = scripts_dir / "analyze.py"

        if not analyze_script.exists():
            print("[SKIP] analyze.py not found")
            return True

        result = subprocess.run(
            [sys.executable, str(analyze_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Usage" in result.stdout or "usage" in result.stdout.lower()

        print("[OK] CLI --help works correctly")
        return True
    except subprocess.TimeoutExpired:
        print("[FAIL] CLI --help timed out")
        return False
    except Exception as e:
        print(f"[FAIL] CLI error: {e}")
        return False


def run_all_smoke_tests() -> tuple[int, int]:
    """Fuehrt alle Smoke Tests aus.

    Returns:
        Tuple aus (passed, failed)
    """
    tests = [
        ("Imports", smoke_test_imports),
        ("Config", smoke_test_config),
        ("Physics Stability", smoke_test_physics_stability),
        ("Physics Criticality", smoke_test_physics_criticality),
        ("Physics Avalanche", smoke_test_physics_avalanche),
        ("Physics Hurst", smoke_test_physics_hurst),
        ("Combination Engine", smoke_test_combination_engine),
        ("Number Pool", smoke_test_number_pool),
        ("Frequency Analysis", smoke_test_frequency_analysis),
        ("Pipeline E2E", smoke_test_pipeline),
        ("CLI Help", smoke_test_cli_help),
    ]

    print("=" * 60)
    print("KENOBASE V2.0 SMOKE TESTS")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"Running: {name}...")
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] Unexpected error in {name}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return passed, failed


# Pytest-kompatible Tests
import pytest


class TestSmokeTests:
    """Pytest-Wrapper fuer Smoke Tests."""

    def test_imports(self) -> None:
        """Test: Alle kritischen Module importierbar."""
        assert smoke_test_imports()

    def test_config(self) -> None:
        """Test: Config-System."""
        assert smoke_test_config()

    def test_physics_stability(self) -> None:
        """Test: Physics Law A."""
        assert smoke_test_physics_stability()

    def test_physics_criticality(self) -> None:
        """Test: Physics Law C."""
        assert smoke_test_physics_criticality()

    def test_physics_avalanche(self) -> None:
        """Test: Avalanche Berechnung."""
        assert smoke_test_physics_avalanche()

    def test_physics_hurst(self) -> None:
        """Test: Hurst Exponent."""
        assert smoke_test_physics_hurst()

    def test_combination_engine(self) -> None:
        """Test: Kombinations-Engine."""
        assert smoke_test_combination_engine()

    def test_number_pool(self) -> None:
        """Test: Number Pool Generator."""
        assert smoke_test_number_pool()

    def test_frequency_analysis(self) -> None:
        """Test: Frequency Analysis."""
        assert smoke_test_frequency_analysis()

    def test_pipeline_e2e(self) -> None:
        """Test: Pipeline End-to-End."""
        assert smoke_test_pipeline()

    def test_cli_help(self) -> None:
        """Test: CLI --help."""
        assert smoke_test_cli_help()


if __name__ == "__main__":
    passed, failed = run_all_smoke_tests()
    sys.exit(0 if failed == 0 else 1)
