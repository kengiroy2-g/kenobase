"""DIST-005: Distribution Pattern Synthesis.

Synthesizes results from DIST-001/002/003/004 into a unified report with
an overall evidence score for distribution pattern stability.

Hypothesis Mapping:
- DIST-001: Complete winner distribution analysis (CV, skewness, near-miss)
- DIST-002: Payout ratio consistency per Keno-Type/Matches
- DIST-003: Sum distribution windows and chi-square analysis
- DIST-004: Popularity proxy (birthday score vs winner correlation)

Overall Evidence Score: Weighted average of individual source indicators.
Verdict: STABLE / SUSPICIOUS / RANDOM
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default weights for each data source in the synthesis
DEFAULT_WEIGHTS = {
    "DIST-001": 0.30,  # Complete distribution (CV, near-miss, anomalies)
    "DIST-002": 0.25,  # Payout ratio consistency
    "DIST-003": 0.25,  # Sum distribution chi-square
    "DIST-004": 0.20,  # Popularity proxy (optional, may be NO_DATA)
}


@dataclass
class SourceResult:
    """Individual data source result for synthesis.

    Attributes:
        source_id: Unique identifier (DIST-001, DIST-002, etc.)
        description: Short description of the data source
        available: Whether the data source was available
        evidence_score: Normalized score 0.0-1.0 (higher = more evidence of stability)
        key_metrics: Dictionary of key metrics from the analysis
        source_file: Path to the source result file
    """

    source_id: str
    description: str
    available: bool
    evidence_score: float
    key_metrics: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""


@dataclass
class DistributionSynthesisReport:
    """Complete synthesis report of all distribution pattern sources.

    Attributes:
        sources: List of individual source results
        overall_evidence_score: Weighted average evidence score (0.0-1.0)
        distribution_verdict: Textual verdict based on score (STABLE/SUSPICIOUS/RANDOM)
        weights: Weights used for each source
        timestamp: When the synthesis was created
        n_available: Number of available data sources
        n_total: Total number of data sources
    """

    sources: list[SourceResult] = field(default_factory=list)
    overall_evidence_score: float = 0.0
    distribution_verdict: str = ""
    weights: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    n_available: int = 0
    n_total: int = 0


def load_dist001_result(filepath: Path) -> SourceResult | None:
    """Load and parse DIST-001 (complete distribution) result.

    Args:
        filepath: Path to hyp001_distribution_complete.json

    Returns:
        SourceResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"DIST-001 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load DIST-001: {e}")
        return None

    # Extract key metrics
    summary = data.get("summary_stats", {})
    hyp_eval = data.get("hypothesis_evaluation", {})

    # Calculate evidence score based on stability indicators
    avg_cv = summary.get("avg_cv", 1.0)
    near_miss_significant = summary.get("near_miss_significant", 0)
    anomaly_count = summary.get("total_anomalies", 0)

    # Lower CV = more stable = higher evidence score
    cv_score = max(0.0, 1.0 - min(avg_cv, 2.0) / 2.0)

    # Fewer anomalies = higher stability
    anomaly_score = max(0.0, 1.0 - min(anomaly_count, 20) / 20.0)

    # Fewer significant near-misses = more random (expected)
    near_miss_ratio = near_miss_significant / 9.0  # 9 Keno-Typen
    near_miss_score = 1.0 - near_miss_ratio  # High near-miss = suspicious

    # Weighted combination
    evidence_score = cv_score * 0.4 + anomaly_score * 0.3 + near_miss_score * 0.3

    return SourceResult(
        source_id="DIST-001",
        description="Complete winner distribution analysis",
        available=True,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "avg_cv": avg_cv,
            "max_cv": summary.get("max_cv"),
            "near_miss_significant": near_miss_significant,
            "anomaly_count": anomaly_count,
            "n_draws": data.get("n_draws"),
            "verdict": hyp_eval.get("verdict"),
            "confidence": hyp_eval.get("confidence"),
        },
        source_file=str(filepath),
    )


def load_dist002_result(filepath: Path) -> SourceResult | None:
    """Load and parse DIST-002 (payout ratio) result.

    Args:
        filepath: Path to dist002_payout_ratio.json

    Returns:
        SourceResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"DIST-002 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load DIST-002: {e}")
        return None

    summary = data.get("summary", {})

    # Extract metrics
    mean_cv = summary.get("mean_cv", 0.0)
    anomaly_count = summary.get("anomaly_count", 0)
    total_combinations = summary.get("total_combinations", 36)

    # CV = 0 means fixed payouts (expected for Keno) = high stability
    # Low CV = stable = high evidence score
    cv_score = max(0.0, 1.0 - min(mean_cv, 1.0))

    # Anomalies are zero-winner draws (expected for rare wins)
    # They indicate proper randomness, so not necessarily suspicious
    anomaly_ratio = anomaly_count / total_combinations
    # Moderate anomaly ratio is expected (4/36 ~ 0.11)
    if anomaly_ratio <= 0.15:
        anomaly_score = 0.9  # Normal
    elif anomaly_ratio <= 0.30:
        anomaly_score = 0.7  # Slightly unusual
    else:
        anomaly_score = 0.4  # Suspicious

    evidence_score = cv_score * 0.6 + anomaly_score * 0.4

    return SourceResult(
        source_id="DIST-002",
        description="Payout ratio consistency analysis",
        available=True,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "mean_cv": mean_cv,
            "anomaly_count": anomaly_count,
            "total_combinations": total_combinations,
            "period_rows": data.get("period", {}).get("total_rows"),
        },
        source_file=str(filepath),
    )


def load_dist003_result(filepath: Path) -> SourceResult | None:
    """Load and parse DIST-003 (sum distribution windows) result.

    Args:
        filepath: Path to sum_windows_analysis.json

    Returns:
        SourceResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"DIST-003 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load DIST-003: {e}")
        return None

    # Extract metrics
    sum_mean = data.get("sum_mean", 0)
    sum_std = data.get("sum_std", 0)
    expected_mean = data.get("expected_mean", 710)
    chi_square = data.get("chi_square", {})
    clusters = data.get("clusters", [])

    # Check if mean is close to expected (710 for 20 from 70)
    mean_deviation = abs(sum_mean - expected_mean) / expected_mean
    mean_score = max(0.0, 1.0 - mean_deviation * 10)  # 10% deviation = 0

    # CV calculation
    cv = sum_std / sum_mean if sum_mean > 0 else 1.0
    cv_score = max(0.0, 1.0 - min(cv, 0.5) * 2)  # CV > 0.5 = 0

    # Chi-square significance
    chi_p = chi_square.get("p_value", 1.0)
    is_significant = chi_square.get("is_significant", False)
    # Significant chi-square means non-uniform = suspicious
    chi_score = 0.3 if is_significant else 0.9

    # Cluster density (single dominant cluster = stable)
    if clusters:
        max_density = max(c.get("density", 0) for c in clusters)
        cluster_score = max_density
    else:
        cluster_score = 0.5

    evidence_score = (
        mean_score * 0.25 + cv_score * 0.25 + chi_score * 0.25 + cluster_score * 0.25
    )

    return SourceResult(
        source_id="DIST-003",
        description="Sum distribution windows analysis",
        available=True,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "sum_mean": round(sum_mean, 2),
            "sum_std": round(sum_std, 2),
            "expected_mean": expected_mean,
            "chi_p_value": chi_p,
            "chi_significant": is_significant,
            "cluster_density": round(clusters[0].get("density", 0), 4)
            if clusters
            else None,
            "total_draws": data.get("total_draws"),
        },
        source_file=str(filepath),
    )


def load_dist004_result(filepath: Path) -> SourceResult | None:
    """Load and parse DIST-004 (popularity proxy) result.

    Args:
        filepath: Path to popularity_proxy.json

    Returns:
        SourceResult or None if loading fails (graceful degradation)
    """
    if not filepath.exists():
        logger.warning(f"DIST-004 file not found: {filepath}")
        return SourceResult(
            source_id="DIST-004",
            description="Popularity proxy (birthday correlation)",
            available=False,
            evidence_score=0.0,
            key_metrics={"error": "File not found"},
            source_file=str(filepath),
        )

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load DIST-004: {e}")
        return SourceResult(
            source_id="DIST-004",
            description="Popularity proxy (birthday correlation)",
            available=False,
            evidence_score=0.0,
            key_metrics={"error": str(e)},
            source_file=str(filepath),
        )

    # Check for NO_DATA status
    status = data.get("status", "")
    if status == "NO_DATA":
        logger.info("DIST-004: NO_DATA - graceful degradation")
        return SourceResult(
            source_id="DIST-004",
            description="Popularity proxy (birthday correlation)",
            available=False,
            evidence_score=0.0,
            key_metrics={
                "status": status,
                "error": data.get("error"),
                "interpretation": data.get("summary", {}).get("interpretation"),
            },
            source_file=str(filepath),
        )

    # If data is available, extract metrics
    summary = data.get("summary", {})
    result = summary.get("result", "INCONCLUSIVE")

    # Score based on result
    if result == "SUPPORTED":
        evidence_score = 0.3  # Correlation found = suspicious
    elif result == "NOT_SUPPORTED":
        evidence_score = 0.9  # No correlation = random
    else:
        evidence_score = 0.5  # Inconclusive

    return SourceResult(
        source_id="DIST-004",
        description="Popularity proxy (birthday correlation)",
        available=True,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "result": result,
            "interpretation": summary.get("interpretation"),
        },
        source_file=str(filepath),
    )


def calculate_overall_score(
    sources: list[SourceResult],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate weighted average evidence score from available sources.

    Only considers sources where available=True.

    Args:
        sources: List of source results
        weights: Optional custom weights per source

    Returns:
        Overall evidence score 0.0-1.0
    """
    if not sources:
        return 0.0

    weights = weights or DEFAULT_WEIGHTS

    total_weight = 0.0
    weighted_sum = 0.0

    for src in sources:
        if not src.available:
            continue
        weight = weights.get(src.source_id, 0.25)
        weighted_sum += src.evidence_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 4)


def get_distribution_verdict(score: float) -> str:
    """Get textual verdict based on overall evidence score.

    Args:
        score: Overall evidence score (0.0-1.0)

    Returns:
        Verdict string (STABLE, SUSPICIOUS, or RANDOM)
    """
    if score >= 0.7:
        return "STABLE: Distribution patterns consistent with fair random draws"
    elif score >= 0.4:
        return "SUSPICIOUS: Some distribution anomalies detected, needs investigation"
    else:
        return "RANDOM: Significant deviations from expected distribution patterns"


def run_synthesis(
    results_dir: Path,
    weights: dict[str, float] | None = None,
) -> DistributionSynthesisReport:
    """Run the full synthesis of all distribution pattern sources.

    Args:
        results_dir: Path to results directory
        weights: Optional custom weights for sources

    Returns:
        DistributionSynthesisReport with all results
    """
    results_dir = Path(results_dir)
    weights = weights or DEFAULT_WEIGHTS

    sources: list[SourceResult] = []

    # Load each source result with graceful degradation
    loaders = [
        (results_dir / "hyp001_distribution_complete.json", load_dist001_result),
        (results_dir / "dist002_payout_ratio.json", load_dist002_result),
        (results_dir / "sum_windows_analysis.json", load_dist003_result),
        (results_dir / "popularity_proxy.json", load_dist004_result),
    ]

    for filepath, loader in loaders:
        result = loader(filepath)
        if result:
            sources.append(result)
            status = "available" if result.available else "NO_DATA"
            logger.info(
                f"{result.source_id}: {status}, score={result.evidence_score}"
            )
        else:
            logger.warning(f"Could not load result from {filepath}")

    # Calculate overall score (only from available sources)
    overall_score = calculate_overall_score(sources, weights)
    verdict = get_distribution_verdict(overall_score)

    n_available = sum(1 for s in sources if s.available)

    return DistributionSynthesisReport(
        sources=sources,
        overall_evidence_score=overall_score,
        distribution_verdict=verdict,
        weights=weights,
        timestamp=datetime.now(),
        n_available=n_available,
        n_total=len(sources),
    )


def source_to_dict(src: SourceResult) -> dict[str, Any]:
    """Convert SourceResult to dictionary.

    Args:
        src: SourceResult instance

    Returns:
        Dictionary representation
    """
    return {
        "source_id": src.source_id,
        "description": src.description,
        "available": src.available,
        "evidence_score": src.evidence_score,
        "key_metrics": src.key_metrics,
        "source_file": src.source_file,
    }


def report_to_dict(report: DistributionSynthesisReport) -> dict[str, Any]:
    """Convert DistributionSynthesisReport to dictionary for JSON export.

    Args:
        report: DistributionSynthesisReport instance

    Returns:
        Dictionary representation
    """
    return {
        "sources": [source_to_dict(s) for s in report.sources],
        "overall_evidence_score": report.overall_evidence_score,
        "distribution_verdict": report.distribution_verdict,
        "weights": report.weights,
        "timestamp": report.timestamp.isoformat(),
        "n_available": report.n_available,
        "n_total": report.n_total,
    }


def export_synthesis_report(
    report: DistributionSynthesisReport,
    output_path: Path,
) -> None:
    """Export synthesis report to JSON file.

    Args:
        report: DistributionSynthesisReport to export
        output_path: Path for output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "hypothesis": "DIST-005",
        "description": "Distribution Pattern Synthesis",
        "synthesis": report_to_dict(report),
        "methodology": {
            "aggregation": "Weighted average of available source evidence scores",
            "graceful_degradation": "Sources with NO_DATA are excluded from weighting",
            "weights_description": {
                "DIST-001": "Complete distribution analysis (30%)",
                "DIST-002": "Payout ratio consistency (25%)",
                "DIST-003": "Sum distribution windows (25%)",
                "DIST-004": "Popularity proxy correlation (20%)",
            },
            "verdict_thresholds": {
                "STABLE": ">= 0.70",
                "SUSPICIOUS": "0.40 - 0.69",
                "RANDOM": "< 0.40",
            },
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Synthesis report exported to {output_path}")


__all__ = [
    "SourceResult",
    "DistributionSynthesisReport",
    "DEFAULT_WEIGHTS",
    "load_dist001_result",
    "load_dist002_result",
    "load_dist003_result",
    "load_dist004_result",
    "calculate_overall_score",
    "get_distribution_verdict",
    "run_synthesis",
    "source_to_dict",
    "report_to_dict",
    "export_synthesis_report",
]
