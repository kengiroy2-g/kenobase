"""Unit-Tests fuer kenobase.analysis.cluster_reset.

Diese Tests verifizieren die HYP-003 Implementierung:
- Cluster-Erkennung (>= threshold aufeinanderfolgende Erscheinungen)
- Reset-Wahrscheinlichkeit berechnen
- Trading-Signale generieren

Granularity: per-draw
Target Metric: reset-probability
"""

from datetime import datetime, timedelta

import pytest

from kenobase.analysis.cluster_reset import (
    ClusterEvent,
    ClusterResetResult,
    TradingSignal,
    analyze_reset_probability,
    detect_cluster_events,
    generate_cluster_reset_report,
    generate_trading_signals,
)
from kenobase.core.data_loader import DrawResult, GameType


# ============================================================================
# Test Fixtures
# ============================================================================


def make_draw(date: datetime, numbers: list[int]) -> DrawResult:
    """Helper to create DrawResult objects."""
    return DrawResult(
        date=date,
        numbers=numbers,
        game_type=GameType.KENO,
    )


@pytest.fixture
def draws_with_cluster() -> list[DrawResult]:
    """Draws where number 1 appears 5 times consecutively then disappears."""
    base_date = datetime(2024, 1, 1)
    draws = []

    # Number 1 appears in draws 0-4 (5 consecutive = cluster)
    for i in range(5):
        numbers = [1] + list(range(2 + i * 19, 21 + i * 19))  # 1 + 19 other numbers
        draws.append(make_draw(base_date + timedelta(days=i), numbers))

    # Number 1 does NOT appear in draws 5-7 (reset)
    for i in range(5, 8):
        numbers = list(range(2 + i * 20, 22 + i * 20))  # 20 numbers without 1
        numbers = [n for n in numbers if n <= 70][:20]  # Keep in range
        if len(numbers) < 20:
            numbers = list(range(2, 22))  # Fallback
        draws.append(make_draw(base_date + timedelta(days=i), numbers))

    return draws


@pytest.fixture
def draws_with_no_cluster() -> list[DrawResult]:
    """Draws where no number appears 5 times consecutively."""
    base_date = datetime(2024, 1, 1)
    draws = []

    # Each draw has completely different numbers
    for i in range(10):
        start = 1 + (i * 20) % 50
        numbers = [(start + j - 1) % 70 + 1 for j in range(20)]
        draws.append(make_draw(base_date + timedelta(days=i), numbers))

    return draws


@pytest.fixture
def draws_with_multiple_clusters() -> list[DrawResult]:
    """Draws where numbers 1 and 2 both form clusters."""
    base_date = datetime(2024, 1, 1)
    draws = []

    # Numbers 1 and 2 appear in draws 0-5 (6 consecutive)
    for i in range(6):
        numbers = [1, 2] + list(range(3 + i * 18, 21 + i * 18))
        numbers = [n for n in numbers if n <= 70][:20]
        draws.append(make_draw(base_date + timedelta(days=i), numbers))

    # Numbers 1 and 2 do NOT appear in draws 6-7 (reset)
    for i in range(6, 8):
        numbers = list(range(3 + i * 20, 23 + i * 20))
        numbers = [n for n in numbers if n <= 70][:20]
        if len(numbers) < 20:
            numbers = list(range(3, 23))
        draws.append(make_draw(base_date + timedelta(days=i), numbers))

    return draws


# ============================================================================
# Test: detect_cluster_events
# ============================================================================


class TestDetectClusterEvents:
    """Tests fuer detect_cluster_events Funktion."""

    def test_detects_cluster(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that a cluster is detected."""
        clusters = detect_cluster_events(draws_with_cluster, threshold=5)

        assert len(clusters) >= 1
        # Number 1 should have a cluster of length 5
        num1_clusters = [c for c in clusters if c.number == 1]
        assert len(num1_clusters) >= 1
        assert any(c.length >= 5 for c in num1_clusters)

    def test_no_cluster_below_threshold(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that short runs are not detected as clusters."""
        # With threshold 6, the 5-run should not be a cluster
        clusters = detect_cluster_events(draws_with_cluster, threshold=6)

        num1_clusters = [c for c in clusters if c.number == 1]
        assert len(num1_clusters) == 0 or all(c.length >= 6 for c in num1_clusters)

    def test_no_clusters_in_random_data(self, draws_with_no_cluster: list[DrawResult]) -> None:
        """Test that no clusters are found in random data."""
        clusters = detect_cluster_events(draws_with_no_cluster, threshold=5)

        # Should have no or very few clusters
        assert len(clusters) <= 2  # Allow some coincidental clusters

    def test_multiple_clusters(self, draws_with_multiple_clusters: list[DrawResult]) -> None:
        """Test detection of multiple clusters."""
        clusters = detect_cluster_events(draws_with_multiple_clusters, threshold=5)

        # Numbers 1 and 2 should both have clusters
        num1_clusters = [c for c in clusters if c.number == 1]
        num2_clusters = [c for c in clusters if c.number == 2]

        assert len(num1_clusters) >= 1
        assert len(num2_clusters) >= 1

    def test_cluster_event_attributes(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that ClusterEvent has correct attributes."""
        clusters = detect_cluster_events(draws_with_cluster, threshold=5)

        for cluster in clusters:
            assert isinstance(cluster, ClusterEvent)
            assert 1 <= cluster.number <= 70
            assert cluster.length >= 5
            assert cluster.start_date is not None
            assert cluster.end_date is not None
            assert cluster.start_date <= cluster.end_date

    def test_reset_detection(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that reset is detected after cluster."""
        clusters = detect_cluster_events(draws_with_cluster, threshold=5)

        # Find cluster for number 1
        num1_clusters = [c for c in clusters if c.number == 1]
        if num1_clusters:
            cluster = num1_clusters[0]
            # Reset should have occurred (number 1 disappears after cluster)
            assert cluster.reset_occurred is True or cluster.reset_occurred is None

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        clusters = detect_cluster_events([], threshold=5)
        assert clusters == []

    def test_insufficient_draws(self) -> None:
        """Test with fewer draws than threshold."""
        draws = [make_draw(datetime(2024, 1, 1), list(range(1, 21)))]
        clusters = detect_cluster_events(draws, threshold=5)
        assert clusters == []


# ============================================================================
# Test: analyze_reset_probability
# ============================================================================


class TestAnalyzeResetProbability:
    """Tests fuer analyze_reset_probability Funktion."""

    def test_basic_analysis(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test basic reset probability calculation."""
        result = analyze_reset_probability(draws_with_cluster, threshold=5)

        assert isinstance(result, ClusterResetResult)
        assert result.total_draws == len(draws_with_cluster)
        assert result.threshold == 5
        assert result.total_clusters >= 1

    def test_baseline_probability(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test baseline probability is correct for KENO."""
        result = analyze_reset_probability(draws_with_cluster, threshold=5)

        # P(not appearing) = 1 - 20/70 = 0.714
        expected_baseline = 1 - (20 / 70)
        assert abs(result.baseline_probability - expected_baseline) < 0.001

    def test_lift_calculation(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test lift is reset_prob / baseline_prob."""
        result = analyze_reset_probability(draws_with_cluster, threshold=5)

        if result.baseline_probability > 0:
            expected_lift = result.reset_probability / result.baseline_probability
            assert abs(result.lift - expected_lift) < 0.001

    def test_is_significant_property(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test is_significant property."""
        result = analyze_reset_probability(draws_with_cluster, threshold=5)

        # is_significant requires lift > 1.1 and >= 10 clusters
        expected_significant = result.lift > 1.1 and result.total_clusters >= 10
        assert result.is_significant == expected_significant

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        result = analyze_reset_probability([], threshold=5)

        assert result.total_draws == 0
        assert result.total_clusters == 0
        assert result.reset_probability == 0.0

    def test_clusters_with_known_reset(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that clusters_with_reset is counted correctly."""
        result = analyze_reset_probability(draws_with_cluster, threshold=5)

        # clusters_with_reset should be <= total_clusters
        assert result.clusters_with_reset <= result.total_clusters


# ============================================================================
# Test: generate_trading_signals
# ============================================================================


class TestGenerateTradingSignals:
    """Tests fuer generate_trading_signals Funktion."""

    def test_generates_signals_for_active_clusters(self) -> None:
        """Test that signals are generated for active clusters."""
        base_date = datetime(2024, 1, 1)
        draws = []

        # Number 1 appears in last 5 draws (active cluster)
        for i in range(5):
            numbers = [1] + list(range(2 + i * 19, 21 + i * 19))
            numbers = [n for n in numbers if n <= 70][:20]
            draws.append(make_draw(base_date + timedelta(days=i), numbers))

        signals = generate_trading_signals(draws, threshold=5)

        assert len(signals) >= 1
        # Number 1 should have a NO_BET signal
        num1_signals = [s for s in signals if s.number == 1]
        assert len(num1_signals) >= 1
        assert num1_signals[0].signal_type == "NO_BET"

    def test_no_signals_for_short_runs(self) -> None:
        """Test that no signals for runs below threshold."""
        base_date = datetime(2024, 1, 1)
        draws = []

        # Number 1 appears in only 3 draws (below threshold of 5)
        for i in range(3):
            numbers = [1] + list(range(2 + i * 19, 21 + i * 19))
            numbers = [n for n in numbers if n <= 70][:20]
            draws.append(make_draw(base_date + timedelta(days=i), numbers))

        signals = generate_trading_signals(draws, threshold=5)

        # No signal for number 1 (run too short)
        num1_signals = [s for s in signals if s.number == 1]
        assert len(num1_signals) == 0

    def test_signal_attributes(self) -> None:
        """Test that TradingSignal has correct attributes."""
        base_date = datetime(2024, 1, 1)
        draws = []

        for i in range(6):
            numbers = [1, 2] + list(range(3 + i * 18, 21 + i * 18))
            numbers = [n for n in numbers if n <= 70][:20]
            draws.append(make_draw(base_date + timedelta(days=i), numbers))

        signals = generate_trading_signals(draws, threshold=5)

        for signal in signals:
            assert isinstance(signal, TradingSignal)
            assert 1 <= signal.number <= 70
            assert signal.signal_type in ["NO_BET", "NEUTRAL"]
            assert signal.cluster_length >= 5
            assert 0.0 <= signal.expected_reset_prob <= 1.0
            assert signal.date is not None

    def test_signals_sorted_by_cluster_length(self) -> None:
        """Test that signals are sorted by cluster length descending."""
        base_date = datetime(2024, 1, 1)
        draws = []

        # Create draws where number 1 has longer run than number 2
        for i in range(8):
            if i < 6:
                numbers = [1, 2] + list(range(3 + i * 18, 21 + i * 18))
            else:
                numbers = [1] + list(range(3 + i * 19, 22 + i * 19))  # Only 1, not 2
            numbers = [n for n in numbers if n <= 70][:20]
            draws.append(make_draw(base_date + timedelta(days=i), numbers))

        signals = generate_trading_signals(draws, threshold=5)

        if len(signals) >= 2:
            # First signal should have longer or equal cluster_length
            assert signals[0].cluster_length >= signals[1].cluster_length

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        signals = generate_trading_signals([], threshold=5)
        assert signals == []


# ============================================================================
# Test: generate_cluster_reset_report
# ============================================================================


class TestGenerateClusterResetReport:
    """Tests fuer generate_cluster_reset_report Funktion."""

    def test_report_structure(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that report has expected structure."""
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5)

        assert "metadata" in report
        assert "cluster_analysis" in report
        assert "cluster_events" in report
        assert "trading_signals" in report
        assert "acceptance_criteria" in report
        assert "summary" in report

    def test_metadata_content(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test metadata section content."""
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5)

        assert report["metadata"]["hypothesis"] == "HYP-003"
        assert report["metadata"]["total_draws"] == len(draws_with_cluster)
        assert "generated_at" in report["metadata"]
        assert report["metadata"]["config"]["cluster_threshold"] == 5

    def test_cluster_analysis_content(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test cluster_analysis section content."""
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5)
        ca = report["cluster_analysis"]

        assert "threshold" in ca
        assert "total_clusters" in ca
        assert "clusters_with_reset" in ca
        assert "reset_probability" in ca
        assert "baseline_probability" in ca
        assert "lift" in ca
        assert "is_significant" in ca

    def test_acceptance_criteria_included(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that acceptance criteria are included."""
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5)
        ac = report["acceptance_criteria"]

        assert "AC1_clusters_detected" in ac
        assert "AC2_reset_probability_calculated" in ac
        assert "AC3_lift_computed" in ac
        assert "AC4_signals_generated" in ac
        assert "AC5_hypothesis_testable" in ac

    def test_summary_key_findings(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test that summary has key findings."""
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5)

        assert "hypothesis_supported" in report["summary"]
        assert "key_findings" in report["summary"]
        assert isinstance(report["summary"]["key_findings"], list)

    def test_custom_config(self, draws_with_cluster: list[DrawResult]) -> None:
        """Test report with custom config."""
        config = {"cluster_threshold": 4}
        report = generate_cluster_reset_report(draws_with_cluster, threshold=5, config=config)

        # Config should override threshold
        assert report["metadata"]["config"]["cluster_threshold"] == 4

    def test_empty_draws(self) -> None:
        """Test with empty draw list."""
        report = generate_cluster_reset_report([], threshold=5)

        assert report["metadata"]["total_draws"] == 0
        assert report["cluster_analysis"]["total_clusters"] == 0
        assert report["cluster_events"] == []
        assert report["trading_signals"] == []
