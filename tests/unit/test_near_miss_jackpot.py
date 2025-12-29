"""Unit tests for kenobase.analysis.near_miss_jackpot module (HOUSE-004)."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from kenobase.analysis.near_miss_jackpot import (
    House004AnalysisSummary,
    MIN_SIGNIFICANT_TYPES,
    NearMissJackpotResult,
    P_VALUE_THRESHOLD,
    analyze_all_near_miss_jackpot,
    analyze_near_miss_jackpot,
    result_to_dict,
    split_by_jackpot_dates,
    summary_to_dict,
)


class TestSplitByJackpotDates:
    """Tests for split_by_jackpot_dates function."""

    @pytest.fixture
    def sample_gq_data(self) -> pd.DataFrame:
        """Create sample GQ data."""
        return pd.DataFrame({
            "Datum": [
                "01.01.2024",
                "02.01.2024",
                "03.01.2024",
                "04.01.2024",
                "05.01.2024",
            ],
            "Keno-Typ": [5, 5, 5, 5, 5],
            "Anzahl richtiger Zahlen": [5, 5, 5, 5, 5],
            "Anzahl der Gewinner": [10, 20, 15, 25, 30],
        })

    def test_split_basic(self, sample_gq_data):
        """Should split data correctly by jackpot dates."""
        jackpot_dates = {
            datetime(2024, 1, 1),
            datetime(2024, 1, 3),
        }

        jackpot_df, normal_df = split_by_jackpot_dates(sample_gq_data, jackpot_dates)

        assert len(jackpot_df) == 2
        assert len(normal_df) == 3

    def test_all_jackpot(self, sample_gq_data):
        """Should handle all dates being jackpot dates."""
        jackpot_dates = {
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3),
            datetime(2024, 1, 4),
            datetime(2024, 1, 5),
        }

        jackpot_df, normal_df = split_by_jackpot_dates(sample_gq_data, jackpot_dates)

        assert len(jackpot_df) == 5
        assert len(normal_df) == 0

    def test_no_jackpot(self, sample_gq_data):
        """Should handle no jackpot dates."""
        jackpot_dates: set[datetime] = set()

        jackpot_df, normal_df = split_by_jackpot_dates(sample_gq_data, jackpot_dates)

        assert len(jackpot_df) == 0
        assert len(normal_df) == 5

    def test_missing_datum_column(self):
        """Should handle DataFrame without Datum column."""
        df = pd.DataFrame({
            "Keno-Typ": [5],
            "Anzahl richtiger Zahlen": [5],
        })
        jackpot_dates = {datetime(2024, 1, 1)}

        jackpot_df, normal_df = split_by_jackpot_dates(df, jackpot_dates)

        assert len(jackpot_df) == 0
        assert len(normal_df) == 1


class TestNearMissJackpotResult:
    """Tests for NearMissJackpotResult dataclass."""

    def test_dataclass_creation(self):
        """Should create NearMissJackpotResult correctly."""
        result = NearMissJackpotResult(
            keno_type=5,
            jackpot_near_miss_ratio=7.5,
            normal_near_miss_ratio=6.0,
            expected_ratio=6.2,
            ratio_difference=1.5,
            chi2_stat=5.5,
            p_value=0.019,
            is_significant=True,
            n_jackpot_draws=50,
            n_normal_draws=500,
            jackpot_max_winners=100,
            jackpot_near_winners=750,
            normal_max_winners=1000,
            normal_near_winners=6000,
        )

        assert result.keno_type == 5
        assert result.jackpot_near_miss_ratio == 7.5
        assert result.normal_near_miss_ratio == 6.0
        assert result.ratio_difference == 1.5
        assert result.is_significant is True

    def test_result_to_dict(self):
        """Should convert result to dictionary."""
        result = NearMissJackpotResult(
            keno_type=5,
            jackpot_near_miss_ratio=7.5,
            normal_near_miss_ratio=6.0,
            expected_ratio=6.2,
            ratio_difference=1.5,
            chi2_stat=5.5,
            p_value=0.019,
            is_significant=True,
            n_jackpot_draws=50,
            n_normal_draws=500,
            jackpot_max_winners=100,
            jackpot_near_winners=750,
            normal_max_winners=1000,
            normal_near_winners=6000,
        )

        d = result_to_dict(result)

        assert d["keno_type"] == 5
        assert d["jackpot_near_miss_ratio"] == 7.5
        assert d["is_significant"] is True
        assert "chi2_stat" in d


class TestAnalyzeNearMissJackpot:
    """Tests for analyze_near_miss_jackpot function."""

    @pytest.fixture
    def sample_gq_data(self) -> pd.DataFrame:
        """Create comprehensive GQ data for testing."""
        data = []

        # Jackpot dates: 1st, 5th, 10th, 15th of January
        jackpot_days = [1, 5, 10, 15]

        for day in range(1, 29):
            date = f"{day:02d}.01.2024"

            # Keno-Typ 5: max=5, near_miss=4
            # Create different ratios for jackpot vs normal
            if day in jackpot_days:
                # Higher near-miss during jackpot
                max_winners = 10
                near_winners = 80  # ratio = 8.0
            else:
                # Normal ratio
                max_winners = 10
                near_winners = 60  # ratio = 6.0

            data.append({
                "Datum": date,
                "Keno-Typ": 5,
                "Anzahl richtiger Zahlen": 5,
                "Anzahl der Gewinner": max_winners,
            })
            data.append({
                "Datum": date,
                "Keno-Typ": 5,
                "Anzahl richtiger Zahlen": 4,
                "Anzahl der Gewinner": near_winners,
            })

        return pd.DataFrame(data)

    @pytest.fixture
    def jackpot_dates(self) -> set[datetime]:
        """Create jackpot dates for testing."""
        return {
            datetime(2024, 1, 1),
            datetime(2024, 1, 5),
            datetime(2024, 1, 10),
            datetime(2024, 1, 15),
        }

    def test_analyze_basic(self, sample_gq_data, jackpot_dates):
        """Should analyze near-miss for jackpot vs normal periods."""
        result = analyze_near_miss_jackpot(sample_gq_data, jackpot_dates, keno_type=5)

        assert isinstance(result, NearMissJackpotResult)
        assert result.keno_type == 5
        assert result.n_jackpot_draws == 4  # 4 jackpot days
        assert result.n_normal_draws == 24  # 28 - 4 = 24 normal days

    def test_ratio_calculation(self, sample_gq_data, jackpot_dates):
        """Should calculate ratios correctly."""
        result = analyze_near_miss_jackpot(sample_gq_data, jackpot_dates, keno_type=5)

        # Jackpot: 4 days * 10 max = 40, 4 days * 80 near = 320 -> ratio = 8.0
        # Normal: 24 days * 10 max = 240, 24 days * 60 near = 1440 -> ratio = 6.0
        assert result.jackpot_near_miss_ratio == pytest.approx(8.0, rel=0.01)
        assert result.normal_near_miss_ratio == pytest.approx(6.0, rel=0.01)
        assert result.ratio_difference == pytest.approx(2.0, rel=0.01)

    def test_winner_counts(self, sample_gq_data, jackpot_dates):
        """Should count winners correctly."""
        result = analyze_near_miss_jackpot(sample_gq_data, jackpot_dates, keno_type=5)

        # Jackpot: 4 * 10 = 40 max, 4 * 80 = 320 near
        assert result.jackpot_max_winners == 40
        assert result.jackpot_near_winners == 320

        # Normal: 24 * 10 = 240 max, 24 * 60 = 1440 near
        assert result.normal_max_winners == 240
        assert result.normal_near_winners == 1440

    def test_p_value_in_range(self, sample_gq_data, jackpot_dates):
        """p_value should be between 0 and 1."""
        result = analyze_near_miss_jackpot(sample_gq_data, jackpot_dates, keno_type=5)

        assert 0 <= result.p_value <= 1

    def test_empty_keno_type(self, sample_gq_data, jackpot_dates):
        """Should handle missing Keno-Typ gracefully."""
        result = analyze_near_miss_jackpot(sample_gq_data, jackpot_dates, keno_type=10)

        # Should return zero counts
        assert result.n_jackpot_draws == 0
        assert result.n_normal_draws == 0
        assert result.p_value == 1.0

    def test_no_jackpot_dates(self, sample_gq_data):
        """Should handle empty jackpot dates."""
        result = analyze_near_miss_jackpot(sample_gq_data, set(), keno_type=5)

        assert result.n_jackpot_draws == 0
        assert result.n_normal_draws == 28
        assert result.jackpot_near_miss_ratio == 0.0


class TestAnalyzeAllNearMissJackpot:
    """Tests for analyze_all_near_miss_jackpot function."""

    @pytest.fixture
    def multi_keno_data(self) -> pd.DataFrame:
        """Create multi-Keno-Typ data."""
        data = []
        jackpot_days = [1, 5, 10]

        for day in range(1, 15):
            date = f"{day:02d}.01.2024"

            for keno_type in range(2, 11):
                max_matches = keno_type
                near_matches = keno_type - 1

                if day in jackpot_days:
                    max_winners = 10
                    near_winners = 100  # Higher ratio
                else:
                    max_winners = 10
                    near_winners = 60  # Normal ratio

                data.append({
                    "Datum": date,
                    "Keno-Typ": keno_type,
                    "Anzahl richtiger Zahlen": max_matches,
                    "Anzahl der Gewinner": max_winners,
                })
                data.append({
                    "Datum": date,
                    "Keno-Typ": keno_type,
                    "Anzahl richtiger Zahlen": near_matches,
                    "Anzahl der Gewinner": near_winners,
                })

        return pd.DataFrame(data)

    @pytest.fixture
    def jackpot_dates(self) -> set[datetime]:
        """Create jackpot dates."""
        return {
            datetime(2024, 1, 1),
            datetime(2024, 1, 5),
            datetime(2024, 1, 10),
        }

    def test_returns_list(self, multi_keno_data, jackpot_dates):
        """Should return list of NearMissJackpotResult."""
        results = analyze_all_near_miss_jackpot(multi_keno_data, jackpot_dates)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, NearMissJackpotResult) for r in results)

    def test_all_keno_types_analyzed(self, multi_keno_data, jackpot_dates):
        """Should analyze all available Keno-Typen."""
        results = analyze_all_near_miss_jackpot(multi_keno_data, jackpot_dates)

        keno_types_analyzed = {r.keno_type for r in results}
        expected_types = set(range(2, 11))
        assert keno_types_analyzed == expected_types


class TestHouse004AnalysisSummary:
    """Tests for House004AnalysisSummary dataclass."""

    def test_dataclass_creation(self):
        """Should create summary correctly."""
        results = [
            NearMissJackpotResult(
                keno_type=5,
                jackpot_near_miss_ratio=8.0,
                normal_near_miss_ratio=6.0,
                expected_ratio=6.2,
                ratio_difference=2.0,
                chi2_stat=10.0,
                p_value=0.001,
                is_significant=True,
                n_jackpot_draws=50,
                n_normal_draws=500,
                jackpot_max_winners=100,
                jackpot_near_winners=800,
                normal_max_winners=1000,
                normal_near_winners=6000,
            )
        ]

        summary = House004AnalysisSummary(
            results=results,
            n_significant=1,
            hypothesis_supported=False,
            n_gk1_events=10,
            date_range_start=datetime(2024, 1, 1),
            date_range_end=datetime(2024, 12, 31),
            gk1_source="test_gk1.csv",
            gq_source="test_gq.csv",
        )

        assert len(summary.results) == 1
        assert summary.n_significant == 1
        assert summary.hypothesis_supported is False

    def test_summary_to_dict(self):
        """Should convert summary to dictionary."""
        results = [
            NearMissJackpotResult(
                keno_type=5,
                jackpot_near_miss_ratio=8.0,
                normal_near_miss_ratio=6.0,
                expected_ratio=6.2,
                ratio_difference=2.0,
                chi2_stat=10.0,
                p_value=0.001,
                is_significant=True,
                n_jackpot_draws=50,
                n_normal_draws=500,
                jackpot_max_winners=100,
                jackpot_near_winners=800,
                normal_max_winners=1000,
                normal_near_winners=6000,
            )
        ]

        summary = House004AnalysisSummary(
            results=results,
            n_significant=1,
            hypothesis_supported=False,
            n_gk1_events=10,
            date_range_start=datetime(2024, 1, 1),
            date_range_end=datetime(2024, 12, 31),
            gk1_source="test_gk1.csv",
            gq_source="test_gq.csv",
        )

        d = summary_to_dict(summary)

        assert "results" in d
        assert len(d["results"]) == 1
        assert d["n_significant"] == 1
        assert d["hypothesis_supported"] is False
        assert d["n_gk1_events"] == 10


class TestHypothesisSupportedLogic:
    """Tests for hypothesis support determination."""

    def test_supported_when_min_significant(self):
        """Hypothesis supported when >= MIN_SIGNIFICANT_TYPES are significant."""
        results = [
            NearMissJackpotResult(
                keno_type=i,
                jackpot_near_miss_ratio=8.0,
                normal_near_miss_ratio=6.0,
                expected_ratio=6.2,
                ratio_difference=2.0,
                chi2_stat=10.0,
                p_value=0.001,  # Significant
                is_significant=True,
                n_jackpot_draws=50,
                n_normal_draws=500,
                jackpot_max_winners=100,
                jackpot_near_winners=800,
                normal_max_winners=1000,
                normal_near_winners=6000,
            )
            for i in range(2, 2 + MIN_SIGNIFICANT_TYPES)
        ]

        n_significant = sum(1 for r in results if r.is_significant)
        hypothesis_supported = n_significant >= MIN_SIGNIFICANT_TYPES

        assert n_significant == MIN_SIGNIFICANT_TYPES
        assert hypothesis_supported is True

    def test_not_supported_when_below_min(self):
        """Hypothesis not supported when < MIN_SIGNIFICANT_TYPES are significant."""
        results = [
            NearMissJackpotResult(
                keno_type=5,
                jackpot_near_miss_ratio=6.5,
                normal_near_miss_ratio=6.0,
                expected_ratio=6.2,
                ratio_difference=0.5,
                chi2_stat=1.0,
                p_value=0.3,  # Not significant
                is_significant=False,
                n_jackpot_draws=50,
                n_normal_draws=500,
                jackpot_max_winners=100,
                jackpot_near_winners=650,
                normal_max_winners=1000,
                normal_near_winners=6000,
            )
        ]

        n_significant = sum(1 for r in results if r.is_significant)
        hypothesis_supported = n_significant >= MIN_SIGNIFICANT_TYPES

        assert n_significant == 0
        assert hypothesis_supported is False


class TestConstants:
    """Tests for module constants."""

    def test_p_value_threshold(self):
        """P_VALUE_THRESHOLD should be standard significance level."""
        assert P_VALUE_THRESHOLD == 0.05

    def test_min_significant_types(self):
        """MIN_SIGNIFICANT_TYPES should be reasonable value."""
        assert MIN_SIGNIFICANT_TYPES >= 1
        assert MIN_SIGNIFICANT_TYPES <= 9  # Max possible Keno-Typen (2-10)
