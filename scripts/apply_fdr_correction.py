"""
Apply FDR (Benjamini-Hochberg) correction across all hypothesis tests in results/.

This script:
1. Scans all JSON files in results/ for p_value keys (nested or top-level)
2. Extracts hypothesis/test identifiers with their p_values
3. Applies global FDR correction using kenobase.analysis.null_models.benjamini_hochberg_fdr()
4. Outputs fdr_corrected_hypotheses.json with q_values and significance flags
5. Generates a Markdown report

Implements TASK_031: Multiple Testing Korrektur
ADR constraint: max 21 primary tests (7 Axiome x 3 Predictions) with alpha=0.05

Author: EXECUTOR (TASK_031)
Date: 2025-12-30
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class PValueEntry:
    """A single p-value entry extracted from results."""

    source_file: str
    hypothesis_id: str
    test_name: str
    p_value: float
    json_path: str  # e.g., "by_type.typ_6.p_value"
    context: dict[str, Any] = field(default_factory=dict)


def extract_p_values_recursive(
    data: Any,
    path: str = "",
    source_file: str = "",
    entries: list[PValueEntry] | None = None,
) -> list[PValueEntry]:
    """
    Recursively extract all p_value fields from a nested JSON structure.

    Args:
        data: JSON data (dict, list, or primitive)
        path: Current JSON path for debugging
        source_file: Source file name
        entries: Accumulator for entries

    Returns:
        List of PValueEntry objects
    """
    if entries is None:
        entries = []

    if isinstance(data, dict):
        # Check for p_value keys (various naming conventions)
        p_value_keys = [k for k in data.keys() if re.match(r"^p[_-]?value", k, re.I)]

        for p_key in p_value_keys:
            val = data[p_key]
            if isinstance(val, (int, float)) and val is not None:
                # Infer hypothesis_id and test_name from context
                hypothesis_id = _infer_hypothesis_id(data, path, source_file)
                test_name = _infer_test_name(data, path)

                context = {}
                for ctx_key in [
                    "observed_value",
                    "observed_statistic",
                    "threshold",
                    "direction",
                    "null_model",
                    "n",
                    "n_permutations",
                ]:
                    if ctx_key in data:
                        context[ctx_key] = data[ctx_key]

                entries.append(
                    PValueEntry(
                        source_file=source_file,
                        hypothesis_id=hypothesis_id,
                        test_name=test_name,
                        p_value=float(val),
                        json_path=f"{path}.{p_key}" if path else p_key,
                        context=context,
                    )
                )

        # Recurse into nested dicts
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            extract_p_values_recursive(value, new_path, source_file, entries)

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            new_path = f"{path}[{idx}]"
            extract_p_values_recursive(item, new_path, source_file, entries)

    return entries


def _infer_hypothesis_id(data: dict, path: str, source_file: str) -> str:
    """Infer hypothesis ID from data or file name."""
    # Check for explicit fields
    for key in ["hypothesis_id", "hypothesis", "axiom_id", "prediction_id", "id"]:
        if key in data and data[key]:
            return str(data[key])

    # Check parent path for HYP/PRED patterns
    match = re.search(r"(HYP[_-]?\d+|P\d+\.\d+|A\d+)", path, re.I)
    if match:
        return match.group(1).upper()

    # Extract from filename
    fname = Path(source_file).stem
    match = re.search(r"(hyp\d+|axiom|a6|cross|cycles|house)", fname, re.I)
    if match:
        return match.group(1).upper()

    return fname.upper()


def _infer_test_name(data: dict, path: str) -> str:
    """Infer test name from data or path."""
    # Check for explicit test name fields
    for key in ["test_name", "name", "description", "comparison", "signal_name"]:
        if key in data and data[key]:
            return str(data[key])[:50]

    # Use last path segment
    parts = path.split(".")
    if parts:
        return parts[-1] if parts[-1] != "p_value" else parts[-2] if len(parts) > 1 else "unknown"

    return "unknown"


def scan_results_directory(results_dir: Path) -> list[PValueEntry]:
    """
    Scan all JSON files in results/ and extract p_values.

    Args:
        results_dir: Path to results directory

    Returns:
        List of all PValueEntry objects found
    """
    all_entries: list[PValueEntry] = []

    # Use set to avoid duplicates from overlapping glob patterns
    json_files = set(results_dir.glob("**/*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            relative_path = json_file.relative_to(results_dir)
            entries = extract_p_values_recursive(
                data,
                path="",
                source_file=str(relative_path),
            )
            all_entries.extend(entries)

        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not read {json_file}: {e}")

    return all_entries


def apply_fdr_correction(
    entries: list[PValueEntry], alpha: float = 0.05
) -> dict[str, Any]:
    """
    Apply Benjamini-Hochberg FDR correction to all p-values.

    Args:
        entries: List of PValueEntry objects
        alpha: Significance level (default 0.05)

    Returns:
        Dict with FDR results and corrected entries
    """
    from kenobase.analysis.null_models import benjamini_hochberg_fdr

    p_values = [e.p_value for e in entries]
    fdr_result = benjamini_hochberg_fdr(p_values, alpha=alpha)

    corrected_entries = []
    for idx, entry in enumerate(entries):
        corrected_entries.append(
            {
                "source_file": entry.source_file,
                "hypothesis_id": entry.hypothesis_id,
                "test_name": entry.test_name,
                "json_path": entry.json_path,
                "original_p_value": entry.p_value,
                "q_value": fdr_result.q_values[idx],
                "is_significant_after_fdr": idx in fdr_result.significant_indices,
                "context": entry.context,
            }
        )

    return {
        "timestamp": datetime.now().isoformat(),
        "alpha": alpha,
        "n_tests": fdr_result.n_tests,
        "n_significant_before_correction": sum(1 for p in p_values if p < alpha),
        "n_significant_after_fdr": fdr_result.n_significant,
        "significant_indices": fdr_result.significant_indices,
        "entries": corrected_entries,
        "summary": {
            "files_scanned": len(set(e.source_file for e in entries)),
            "unique_hypotheses": len(set(e.hypothesis_id for e in entries)),
            "p_values_extracted": len(entries),
            "min_p_value": min(p_values) if p_values else None,
            "max_p_value": max(p_values) if p_values else None,
            "median_p_value": sorted(p_values)[len(p_values) // 2] if p_values else None,
        },
    }


def generate_markdown_report(fdr_results: dict[str, Any], output_path: Path) -> None:
    """
    Generate a Markdown report of FDR correction results.

    Args:
        fdr_results: Output from apply_fdr_correction()
        output_path: Path to write Markdown report
    """
    lines = [
        "# FDR Correction Report",
        "",
        f"**Generated:** {fdr_results['timestamp']}",
        f"**Alpha:** {fdr_results['alpha']}",
        "",
        "## Summary",
        "",
        f"- **Total p-values extracted:** {fdr_results['n_tests']}",
        f"- **Files scanned:** {fdr_results['summary']['files_scanned']}",
        f"- **Unique hypotheses:** {fdr_results['summary']['unique_hypotheses']}",
        f"- **Significant before correction (p < {fdr_results['alpha']}):** {fdr_results['n_significant_before_correction']}",
        f"- **Significant after FDR correction:** {fdr_results['n_significant_after_fdr']}",
        "",
        "## Significant Results After FDR Correction",
        "",
    ]

    significant_entries = [
        e for e in fdr_results["entries"] if e["is_significant_after_fdr"]
    ]

    if significant_entries:
        lines.append("| Hypothesis | Test | p-value | q-value | File |")
        lines.append("|------------|------|---------|---------|------|")
        for entry in sorted(significant_entries, key=lambda x: x["q_value"]):
            lines.append(
                f"| {entry['hypothesis_id']} | {entry['test_name'][:30]} | "
                f"{entry['original_p_value']:.4f} | {entry['q_value']:.4f} | "
                f"{entry['source_file']} |"
            )
    else:
        lines.append("*No tests remain significant after FDR correction.*")

    lines.extend(
        [
            "",
            "## All Tests (sorted by q-value)",
            "",
            "| # | Hypothesis | Test | p-value | q-value | Sig. | File |",
            "|---|------------|------|---------|---------|------|------|",
        ]
    )

    for idx, entry in enumerate(
        sorted(fdr_results["entries"], key=lambda x: x["q_value"]), 1
    ):
        sig = "Yes" if entry["is_significant_after_fdr"] else "No"
        lines.append(
            f"| {idx} | {entry['hypothesis_id']} | {entry['test_name'][:25]} | "
            f"{entry['original_p_value']:.4f} | {entry['q_value']:.4f} | "
            f"{sig} | {entry['source_file'][:25]} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- FDR correction uses Benjamini-Hochberg procedure",
            "- q-value represents adjusted p-value controlling False Discovery Rate",
            f"- ADR constraint: max 21 primary tests (7 Axiome x 3 Predictions) at alpha={fdr_results['alpha']}",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Apply FDR correction to all p-values in results/"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results"),
        help="Path to results directory (default: results/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/fdr_corrected_hypotheses.json"),
        help="Output JSON file (default: results/fdr_corrected_hypotheses.json)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/fdr_correction_report.md"),
        help="Output Markdown report (default: results/fdr_correction_report.md)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level for FDR (default: 0.05)",
    )

    args = parser.parse_args()

    print(f"Scanning {args.results_dir} for p-values...")
    entries = scan_results_directory(args.results_dir)
    print(f"Found {len(entries)} p-values in {len(set(e.source_file for e in entries))} files")

    if not entries:
        print("No p-values found. Exiting.")
        return

    print(f"Applying FDR correction with alpha={args.alpha}...")
    fdr_results = apply_fdr_correction(entries, alpha=args.alpha)

    print(f"Writing results to {args.output}...")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(fdr_results, f, indent=2)

    print(f"Writing report to {args.report}...")
    generate_markdown_report(fdr_results, args.report)

    print("\nSummary:")
    print(f"  - Tests before correction (p < {args.alpha}): {fdr_results['n_significant_before_correction']}")
    print(f"  - Tests after FDR correction: {fdr_results['n_significant_after_fdr']}")

    if fdr_results["n_significant_after_fdr"] > 0:
        print("\n  Significant after FDR:")
        for entry in fdr_results["entries"]:
            if entry["is_significant_after_fdr"]:
                print(f"    - {entry['hypothesis_id']}: {entry['test_name']} (q={entry['q_value']:.4f})")


if __name__ == "__main__":
    main()
