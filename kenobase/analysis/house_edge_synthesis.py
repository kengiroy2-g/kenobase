"""HOUSE-005: House-Edge Manipulation Synthesis.

Synthesizes results from HOUSE-001/002/003/004 into a unified report with
an overall evidence score for house-edge manipulation.

Hypothesis Mapping:
- HOUSE-001 (HYP-015): Jackpot-Hoehe vs. Zahlentyp Korrelation
- HOUSE-002: High-stake draws favor unpopular numbers
- HOUSE-003: Rolling House-Edge Stability (CV analysis)
- HOUSE-004: Near-Miss bei hohem Jackpot

Overall Evidence Score: Weighted average of individual hypothesis support indicators.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default weights for each hypothesis in the synthesis
DEFAULT_WEIGHTS = {
    "HOUSE-001": 0.20,  # Jackpot correlation
    "HOUSE-002": 0.25,  # Stake-popularity correlation
    "HOUSE-003": 0.25,  # Rolling stability
    "HOUSE-004": 0.30,  # Near-miss jackpot (most direct evidence)
}


@dataclass
class HypothesisResult:
    """Individual hypothesis result for synthesis.

    Attributes:
        hypothesis_id: Unique identifier (HOUSE-001, HOUSE-002, etc.)
        description: Short description of the hypothesis
        supported: Whether the hypothesis was supported by data
        evidence_score: Normalized score 0.0-1.0 (higher = more evidence)
        key_metrics: Dictionary of key metrics from the analysis
        source_file: Path to the source result file
    """

    hypothesis_id: str
    description: str
    supported: bool
    evidence_score: float
    key_metrics: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""


@dataclass
class SynthesisReport:
    """Complete synthesis report of all house-edge hypotheses.

    Attributes:
        hypotheses: List of individual hypothesis results
        overall_evidence_score: Weighted average evidence score (0.0-1.0)
        manipulation_verdict: Textual verdict based on score
        weights: Weights used for each hypothesis
        timestamp: When the synthesis was created
        n_supported: Number of supported hypotheses
        n_total: Total number of hypotheses
    """

    hypotheses: list[HypothesisResult] = field(default_factory=list)
    overall_evidence_score: float = 0.0
    manipulation_verdict: str = ""
    weights: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    n_supported: int = 0
    n_total: int = 0


def load_house001_result(filepath: Path) -> HypothesisResult | None:
    """Load and parse HOUSE-001 (HYP-015) result.

    Args:
        filepath: Path to hyp015_jackpot_correlation.json

    Returns:
        HypothesisResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"HOUSE-001 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load HOUSE-001: {e}")
        return None

    # Extract key metrics
    correlation = data.get("correlation", {})
    supported = correlation.get("is_significant", False)

    # Evidence score based on correlation strength and p-value
    pearson_r = abs(correlation.get("pearson_r", 0))
    pearson_p = correlation.get("pearson_p", 1.0)

    # Score: higher r and lower p = higher evidence
    if pearson_p < 0.05:
        evidence_score = min(pearson_r * 5, 1.0)  # Scale r to 0-1
    else:
        evidence_score = 0.0

    return HypothesisResult(
        hypothesis_id="HOUSE-001",
        description="Jackpot-Hoehe vs. Zahlentyp Korrelation",
        supported=supported,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "pearson_r": correlation.get("pearson_r"),
            "pearson_p": correlation.get("pearson_p"),
            "chi_square_p": correlation.get("chi_square_p"),
            "n_jackpot_draws": correlation.get("n_jackpot_draws"),
            "n_total_draws": correlation.get("n_total_draws"),
        },
        source_file=str(filepath),
    )


def load_house002_result(filepath: Path) -> HypothesisResult | None:
    """Load and parse HOUSE-002 result.

    Args:
        filepath: Path to house002_stake_popularity.json

    Returns:
        HypothesisResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"HOUSE-002 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load HOUSE-002: {e}")
        return None

    result = data.get("result", {})
    supported = result.get("supports_hypothesis", False)

    # Evidence score based on correlation and significance
    spearman_r = abs(result.get("spearman_r", 0))
    spearman_p = result.get("spearman_p", 1.0)

    if spearman_p < 0.05 and spearman_r > 0.15:
        evidence_score = min(spearman_r * 3, 1.0)
    else:
        evidence_score = 0.0

    return HypothesisResult(
        hypothesis_id="HOUSE-002",
        description="High-stake draws favor unpopular numbers",
        supported=supported,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "spearman_r": result.get("spearman_r"),
            "spearman_p": result.get("spearman_p"),
            "n_draws": result.get("n_draws"),
            "mean_unpopular_ratio_high": result.get("mean_unpopular_ratio_high"),
            "mean_unpopular_ratio_low": result.get("mean_unpopular_ratio_low"),
        },
        source_file=str(filepath),
    )


def load_house003_result(filepath: Path) -> HypothesisResult | None:
    """Load and parse HOUSE-003 result.

    Args:
        filepath: Path to house003_rolling_stability.json

    Returns:
        HypothesisResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"HOUSE-003 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load HOUSE-003: {e}")
        return None

    result = data.get("result", {})
    supported = result.get("hypothesis_supported", False)

    # Evidence score: if CV is suspiciously LOW, that's evidence of manipulation
    # (too stable = controlled)
    stable_count = result.get("stable_count", 0)
    total_windows = result.get("total_windows", 3)

    if stable_count >= 2:
        evidence_score = stable_count / total_windows
    else:
        evidence_score = 0.0

    windows = result.get("windows", {})
    cv_values = {k: v.get("cv_mean", 0) for k, v in windows.items()}

    return HypothesisResult(
        hypothesis_id="HOUSE-003",
        description="Rolling House-Edge Stability",
        supported=supported,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "stable_count": stable_count,
            "total_windows": total_windows,
            "cv_values": cv_values,
            "cv_threshold": result.get("cv_threshold"),
        },
        source_file=str(filepath),
    )


def load_house004_result(filepath: Path) -> HypothesisResult | None:
    """Load and parse HOUSE-004 result.

    Args:
        filepath: Path to house004_near_miss_jackpot.json

    Returns:
        HypothesisResult or None if loading fails
    """
    if not filepath.exists():
        logger.warning(f"HOUSE-004 file not found: {filepath}")
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load HOUSE-004: {e}")
        return None

    summary = data.get("summary", {})
    verdict = data.get("verdict", {})
    supported = verdict.get("hypothesis_supported", False)

    # Evidence score based on number of significant Keno-Typen
    n_significant = summary.get("n_significant", 0)
    total_types = verdict.get("total_types", 9)

    if n_significant >= 3:
        evidence_score = min(n_significant / total_types * 1.5, 1.0)
    else:
        evidence_score = n_significant / total_types * 0.5

    return HypothesisResult(
        hypothesis_id="HOUSE-004",
        description="Near-Miss bei hohem Jackpot",
        supported=supported,
        evidence_score=round(evidence_score, 4),
        key_metrics={
            "n_significant": n_significant,
            "total_types": total_types,
            "n_gk1_events": summary.get("n_gk1_events"),
            "date_range_start": summary.get("date_range_start"),
            "date_range_end": summary.get("date_range_end"),
        },
        source_file=str(filepath),
    )


def calculate_overall_score(
    hypotheses: list[HypothesisResult],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate weighted average evidence score.

    Args:
        hypotheses: List of hypothesis results
        weights: Optional custom weights per hypothesis

    Returns:
        Overall evidence score 0.0-1.0
    """
    if not hypotheses:
        return 0.0

    weights = weights or DEFAULT_WEIGHTS

    total_weight = 0.0
    weighted_sum = 0.0

    for hyp in hypotheses:
        weight = weights.get(hyp.hypothesis_id, 0.25)
        weighted_sum += hyp.evidence_score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 4)


def get_manipulation_verdict(score: float) -> str:
    """Get textual verdict based on overall evidence score.

    Args:
        score: Overall evidence score (0.0-1.0)

    Returns:
        Verdict string
    """
    if score >= 0.7:
        return "STRONG_EVIDENCE: Multiple indicators suggest systematic manipulation"
    elif score >= 0.5:
        return "MODERATE_EVIDENCE: Some indicators suggest possible manipulation"
    elif score >= 0.3:
        return "WEAK_EVIDENCE: Limited indicators, inconclusive"
    else:
        return "NO_EVIDENCE: Data consistent with fair random draws"


def run_synthesis(
    results_dir: Path,
    weights: dict[str, float] | None = None,
) -> SynthesisReport:
    """Run the full synthesis of all house-edge hypothesis results.

    Args:
        results_dir: Path to results directory
        weights: Optional custom weights for hypotheses

    Returns:
        SynthesisReport with all results
    """
    results_dir = Path(results_dir)
    weights = weights or DEFAULT_WEIGHTS

    hypotheses: list[HypothesisResult] = []

    # Load each hypothesis result
    loaders = [
        (results_dir / "hyp015_jackpot_correlation.json", load_house001_result),
        (results_dir / "house002_stake_popularity.json", load_house002_result),
        (results_dir / "house003_rolling_stability.json", load_house003_result),
        (results_dir / "house004_near_miss_jackpot.json", load_house004_result),
    ]

    for filepath, loader in loaders:
        result = loader(filepath)
        if result:
            hypotheses.append(result)
            status = "SUPPORTED" if result.supported else "not supported"
            logger.info(
                f"{result.hypothesis_id}: {status}, score={result.evidence_score}"
            )
        else:
            logger.warning(f"Could not load result from {filepath}")

    # Calculate overall score
    overall_score = calculate_overall_score(hypotheses, weights)
    verdict = get_manipulation_verdict(overall_score)

    n_supported = sum(1 for h in hypotheses if h.supported)

    return SynthesisReport(
        hypotheses=hypotheses,
        overall_evidence_score=overall_score,
        manipulation_verdict=verdict,
        weights=weights,
        timestamp=datetime.now(),
        n_supported=n_supported,
        n_total=len(hypotheses),
    )


def hypothesis_to_dict(hyp: HypothesisResult) -> dict[str, Any]:
    """Convert HypothesisResult to dictionary.

    Args:
        hyp: HypothesisResult instance

    Returns:
        Dictionary representation
    """
    return {
        "hypothesis_id": hyp.hypothesis_id,
        "description": hyp.description,
        "supported": hyp.supported,
        "evidence_score": hyp.evidence_score,
        "key_metrics": hyp.key_metrics,
        "source_file": hyp.source_file,
    }


def report_to_dict(report: SynthesisReport) -> dict[str, Any]:
    """Convert SynthesisReport to dictionary for JSON export.

    Args:
        report: SynthesisReport instance

    Returns:
        Dictionary representation
    """
    return {
        "hypotheses": [hypothesis_to_dict(h) for h in report.hypotheses],
        "overall_evidence_score": report.overall_evidence_score,
        "manipulation_verdict": report.manipulation_verdict,
        "weights": report.weights,
        "timestamp": report.timestamp.isoformat(),
        "n_supported": report.n_supported,
        "n_total": report.n_total,
    }


def export_synthesis_report(
    report: SynthesisReport,
    output_path: Path,
) -> None:
    """Export synthesis report to JSON file.

    Args:
        report: SynthesisReport to export
        output_path: Path for output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "hypothesis": "HOUSE-005",
        "description": "House-Edge Manipulation Synthesis",
        "synthesis": report_to_dict(report),
        "methodology": {
            "aggregation": "Weighted average of individual hypothesis evidence scores",
            "weights_description": {
                "HOUSE-001": "Jackpot-Zahlentyp correlation (20%)",
                "HOUSE-002": "Stake-popularity correlation (25%)",
                "HOUSE-003": "Rolling stability CV analysis (25%)",
                "HOUSE-004": "Near-miss jackpot analysis (30%)",
            },
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Synthesis report exported to {output_path}")


__all__ = [
    "HypothesisResult",
    "SynthesisReport",
    "DEFAULT_WEIGHTS",
    "load_house001_result",
    "load_house002_result",
    "load_house003_result",
    "load_house004_result",
    "calculate_overall_score",
    "get_manipulation_verdict",
    "run_synthesis",
    "hypothesis_to_dict",
    "report_to_dict",
    "export_synthesis_report",
]
