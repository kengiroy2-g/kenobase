"""Unit-Tests fuer das Backtest-Script.

Testet:
- Metriken-Berechnung (Precision, Recall, F1)
- BacktestEngine Periode-Split
- Edge Cases (wenig Daten, keine Hits)

Gemaess CLAUDE.md Phase 5 Test-Strategie.
"""

from datetime import datetime, timedelta

import pytest

from kenobase.core.config import KenobaseConfig
from kenobase.core.data_loader import DrawResult, GameType

# Import from backtest script
from scripts.backtest import (
    BacktestEngine,
    BacktestPeriodResult,
    BacktestResult,
    calculate_hits,
    calculate_metrics,
    format_result_json,
    format_result_markdown,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_draw() -> DrawResult:
    """Einzelne Beispiel-Ziehung."""
    return DrawResult(
        date=datetime(2023, 1, 1),
        numbers=[1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 66, 67, 68],
        game_type=GameType.KENO,
    )


@pytest.fixture
def sample_draws() -> list[DrawResult]:
    """Liste von Beispiel-Ziehungen (20 Draws)."""
    base_date = datetime(2023, 1, 1)
    draws = []
    for i in range(20):
        # Numbers shift slightly to create variance
        numbers = [(j + i) % 70 + 1 for j in range(20)]
        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=numbers,
                game_type=GameType.KENO,
            )
        )
    return draws


@pytest.fixture
def large_sample_draws() -> list[DrawResult]:
    """Groessere Liste von Beispiel-Ziehungen (120 Draws) fuer Backtest."""
    base_date = datetime(2023, 1, 1)
    draws = []
    for i in range(120):
        # Create varied numbers with some hot numbers (1-20 appear more often)
        if i % 2 == 0:
            numbers = list(range(1, 21))  # Hot numbers
        else:
            numbers = list(range(51, 71))  # Cold numbers
        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=numbers,
                game_type=GameType.KENO,
            )
        )
    return draws


@pytest.fixture
def default_config() -> KenobaseConfig:
    """Standard-Konfiguration fuer Tests."""
    return KenobaseConfig()


# =============================================================================
# Test calculate_hits
# =============================================================================


class TestCalculateHits:
    """Tests fuer calculate_hits Funktion."""

    def test_perfect_prediction(self, sample_draw: DrawResult) -> None:
        """100% Treffer wenn alle predicted in draw sind."""
        predicted = [1, 2, 3, 4, 5]
        test_draws = [sample_draw]
        hits = calculate_hits(predicted, test_draws)
        assert hits == 5

    def test_no_hits(self, sample_draw: DrawResult) -> None:
        """0 Treffer wenn nichts uebereinstimmt."""
        predicted = [71, 72, 73, 74, 75]  # Out of range
        test_draws = [sample_draw]
        hits = calculate_hits(predicted, test_draws)
        assert hits == 0

    def test_partial_hits(self, sample_draw: DrawResult) -> None:
        """Teilweise Treffer."""
        predicted = [1, 2, 100, 101, 102]  # 2 hits (1, 2)
        test_draws = [sample_draw]
        hits = calculate_hits(predicted, test_draws)
        assert hits == 2

    def test_multiple_draws(self) -> None:
        """Hits ueber mehrere Ziehungen summiert."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 1, 2),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
        ]
        predicted = [1, 2, 3]
        hits = calculate_hits(predicted, draws)
        assert hits == 6  # 3 per draw * 2 draws

    def test_empty_draws(self) -> None:
        """Keine Treffer bei leerer Liste."""
        hits = calculate_hits([1, 2, 3], [])
        assert hits == 0

    def test_empty_predicted(self, sample_draw: DrawResult) -> None:
        """Keine Treffer bei leerer Vorhersage."""
        hits = calculate_hits([], [sample_draw])
        assert hits == 0


# =============================================================================
# Test calculate_metrics
# =============================================================================


class TestCalculateMetrics:
    """Tests fuer calculate_metrics Funktion."""

    def test_perfect_prediction(self) -> None:
        """100% Precision wenn alle Vorhersagen korrekt."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
        ]
        predicted = [1, 2, 3, 4, 5]
        metrics = calculate_metrics(predicted, draws, numbers_per_draw=20)

        assert metrics["hits"] == 5
        assert metrics["precision"] == 1.0  # 5 / 5
        assert metrics["recall"] == 0.25  # 5 / 20
        assert metrics["f1_score"] == pytest.approx(0.4, rel=0.01)

    def test_no_hits(self) -> None:
        """0% Precision wenn keine Treffer."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
        ]
        predicted = [71, 72, 73, 74, 75]
        metrics = calculate_metrics(predicted, draws, numbers_per_draw=20)

        assert metrics["hits"] == 0
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1_score"] == 0.0

    def test_full_recall(self) -> None:
        """100% Recall wenn alle Zahlen vorhergesagt."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[1, 2, 3, 4, 5],
                game_type=GameType.LOTTO,
            ),
        ]
        # Vorhersage enthaelt alle und mehr
        predicted = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        metrics = calculate_metrics(predicted, draws, numbers_per_draw=5)

        assert metrics["hits"] == 5
        assert metrics["precision"] == 0.5  # 5 / 10
        assert metrics["recall"] == 1.0  # 5 / 5
        assert metrics["f1_score"] == pytest.approx(0.6667, rel=0.01)

    def test_empty_predictions(self) -> None:
        """Graceful bei leerer Vorhersage."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
        ]
        metrics = calculate_metrics([], draws, numbers_per_draw=20)

        assert metrics["hits"] == 0
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1_score"] == 0.0

    def test_empty_draws(self) -> None:
        """Graceful bei leeren Ziehungen."""
        metrics = calculate_metrics([1, 2, 3], [], numbers_per_draw=20)

        assert metrics["hits"] == 0
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1_score"] == 0.0


# =============================================================================
# Test BacktestEngine
# =============================================================================


class TestBacktestEngine:
    """Tests fuer BacktestEngine Klasse."""

    def test_minimum_draws_error(
        self,
        default_config: KenobaseConfig,
        sample_draws: list[DrawResult],
    ) -> None:
        """Fehler wenn zu wenig Ziehungen fuer Perioden."""
        engine = BacktestEngine(default_config)

        with pytest.raises(ValueError, match="Not enough draws"):
            engine.run(sample_draws, n_periods=100)  # 20 draws, need 1000

    def test_period_split(
        self,
        default_config: KenobaseConfig,
        large_sample_draws: list[DrawResult],
    ) -> None:
        """Perioden werden korrekt aufgeteilt."""
        engine = BacktestEngine(default_config)
        result = engine.run(large_sample_draws, n_periods=10, train_ratio=0.8)

        assert result.n_periods == 10
        assert len(result.period_results) == 10

        # Check period structure
        for period in result.period_results:
            assert period.train_draws > 0
            assert period.test_draws > 0
            assert period.train_start < period.train_end
            assert period.test_start < period.test_end
            assert period.train_end <= period.test_start

    def test_summary_generation(
        self,
        default_config: KenobaseConfig,
        large_sample_draws: list[DrawResult],
    ) -> None:
        """Summary enthaelt alle erforderlichen Metriken."""
        engine = BacktestEngine(default_config)
        result = engine.run(large_sample_draws, n_periods=6, train_ratio=0.8)

        required_keys = [
            "avg_precision",
            "avg_recall",
            "avg_f1",
            "std_f1",
            "avg_stability",
            "critical_periods",
            "best_period",
            "worst_period",
        ]

        for key in required_keys:
            assert key in result.summary, f"Missing key: {key}"

    def test_physics_integration(
        self,
        default_config: KenobaseConfig,
        large_sample_draws: list[DrawResult],
    ) -> None:
        """Physics Layer Metriken sind in Ergebnissen."""
        engine = BacktestEngine(default_config)
        result = engine.run(large_sample_draws, n_periods=6, train_ratio=0.8)

        for period in result.period_results:
            assert hasattr(period, "stability_score")
            assert hasattr(period, "criticality_level")
            # Values should be valid
            assert 0.0 <= period.stability_score <= 1.0
            assert period.criticality_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]


# =============================================================================
# Test Output Formatting
# =============================================================================


class TestOutputFormatting:
    """Tests fuer Output-Formatierung."""

    @pytest.fixture
    def sample_result(self) -> BacktestResult:
        """Beispiel BacktestResult fuer Formatierungstests."""
        period = BacktestPeriodResult(
            period_id=1,
            train_start=datetime(2023, 1, 1),
            train_end=datetime(2023, 3, 31),
            test_start=datetime(2023, 4, 1),
            test_end=datetime(2023, 4, 30),
            train_draws=100,
            test_draws=25,
            predicted_hot=[1, 2, 3, 4, 5],
            total_hits=50,
            total_predictions=125,
            precision=0.4,
            recall=0.25,
            f1_score=0.3077,
            stability_score=0.85,
            criticality_level="MEDIUM",
        )
        return BacktestResult(
            timestamp=datetime(2023, 5, 1, 12, 0, 0),
            config_name="2.0.0",
            total_draws=125,
            n_periods=1,
            period_results=[period],
            summary={
                "avg_precision": 0.4,
                "avg_recall": 0.25,
                "avg_f1": 0.3077,
                "std_f1": 0.0,
                "avg_stability": 0.85,
                "critical_periods": 0,
                "best_period": 1,
                "worst_period": 1,
                "best_f1": 0.3077,
                "worst_f1": 0.3077,
            },
        )

    def test_json_format_valid(self, sample_result: BacktestResult) -> None:
        """JSON-Output ist valides JSON."""
        import json

        output = format_result_json(sample_result)
        parsed = json.loads(output)

        assert "backtest_timestamp" in parsed
        assert "period_results" in parsed
        assert "summary" in parsed
        assert len(parsed["period_results"]) == 1

    def test_json_format_precision(self, sample_result: BacktestResult) -> None:
        """JSON-Werte haben korrekte Precision."""
        import json

        output = format_result_json(sample_result)
        parsed = json.loads(output)

        period = parsed["period_results"][0]
        assert period["precision"] == 0.4
        assert period["recall"] == 0.25

    def test_markdown_format_structure(self, sample_result: BacktestResult) -> None:
        """Markdown hat korrektes Format."""
        output = format_result_markdown(sample_result)

        assert "# Kenobase Backtest Report" in output
        assert "## Summary" in output
        assert "## Period Details" in output
        assert "| Period |" in output

    def test_markdown_contains_metrics(self, sample_result: BacktestResult) -> None:
        """Markdown enthaelt alle Metriken."""
        output = format_result_markdown(sample_result)

        assert "Avg Precision" in output
        assert "Avg Recall" in output
        assert "Avg F1" in output
        assert "0.4" in output


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests fuer Randfaelle."""

    def test_single_period(
        self,
        default_config: KenobaseConfig,
        large_sample_draws: list[DrawResult],
    ) -> None:
        """Funktioniert mit nur einer Periode."""
        engine = BacktestEngine(default_config)
        result = engine.run(large_sample_draws, n_periods=1, train_ratio=0.8)

        assert result.n_periods == 1
        assert len(result.period_results) == 1
        # std_f1 should be 0 with single period
        assert result.summary["std_f1"] == 0.0

    def test_extreme_train_ratio(
        self,
        default_config: KenobaseConfig,
        large_sample_draws: list[DrawResult],
    ) -> None:
        """Funktioniert mit extremen Train-Ratios."""
        engine = BacktestEngine(default_config)

        # High train ratio
        result = engine.run(large_sample_draws, n_periods=6, train_ratio=0.9)
        assert len(result.period_results) == 6

        # Low train ratio
        result = engine.run(large_sample_draws, n_periods=6, train_ratio=0.5)
        assert len(result.period_results) == 6

    def test_chronological_order(
        self,
        default_config: KenobaseConfig,
    ) -> None:
        """Ziehungen werden chronologisch sortiert."""
        # Create draws in random order
        draws = [
            DrawResult(
                date=datetime(2023, 3, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 2, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            ),
        ] * 40  # 120 draws

        engine = BacktestEngine(default_config)
        result = engine.run(draws, n_periods=6, train_ratio=0.8)

        # Verify first period starts with earliest date
        first_period = result.period_results[0]
        assert first_period.train_start == datetime(2023, 1, 1)
