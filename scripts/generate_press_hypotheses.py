#!/usr/bin/env python
# scripts/generate_press_hypotheses.py
"""CLI script to generate hypotheses from KENO press release data."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.press_hypotheses import (
    PressHypothesesGenerator,
    generate_hypotheses_markdown,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def find_latest_scrape_file(data_dir: Path) -> Path | None:
    """Find the most recent scrape results file."""
    pattern = "keno_winners_*.json"
    files = list(data_dir.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate hypotheses from KENO press release data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Generate from latest scrape results
  python scripts/generate_press_hypotheses.py

  # Generate from specific file
  python scripts/generate_press_hypotheses.py --input data/scraped/keno_winners_20251228.json

  # Output as markdown
  python scripts/generate_press_hypotheses.py --format markdown --output results/hypotheses.md

  # Combine with manual data (JSON format)
  python scripts/generate_press_hypotheses.py --input manual_data.json
        """,
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="Input JSON file from scrape_press.py (default: latest in data/scraped)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: results/press_hypotheses.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=3,
        help="Minimum records for hypothesis generation (default: 3)",
    )
    parser.add_argument(
        "--update-catalog",
        action="store_true",
        help="Update HYPOTHESES_CATALOG.md with new hypotheses",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Find input file
    if args.input:
        input_path = args.input
    else:
        data_dir = Path("data/scraped")
        input_path = find_latest_scrape_file(data_dir)
        if not input_path:
            print(f"Fehler: Keine Scrape-Dateien in {data_dir} gefunden.")
            print("Fuehre zuerst 'python scripts/scrape_press.py --all' aus.")
            return 1

    if not input_path.exists():
        print(f"Fehler: Datei nicht gefunden: {input_path}")
        return 1

    print("\n" + "=" * 60)
    print("KENO Press Hypotheses Generator")
    print("=" * 60)
    print(f"Input: {input_path}")
    print("-" * 60)

    # Load data
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Fehler: Ungueltige JSON-Datei: {e}")
        return 1

    records = data.get("records", [])
    print(f"Records geladen: {len(records)}")

    if not records:
        print("\nKeine Records gefunden. Hypothesengeneration nicht moeglich.")
        return 1

    # Generate hypotheses
    generator = PressHypothesesGenerator(min_records=args.min_records)
    result = generator.generate_from_file(input_path)

    print(f"Hypothesen generiert: {len(result.hypotheses)}")

    # Print warnings
    if result.warnings:
        print("\nWarnungen:")
        for warning in result.warnings:
            print(f"  - {warning}")

    # Print hypotheses summary
    print("\n" + "-" * 60)
    print("GENERIERTE HYPOTHESEN:")
    print()

    for hyp in result.hypotheses:
        print(f"  {hyp.id}: {hyp.name}")
        print(f"    Kategorie: {hyp.category} | Prioritaet: {hyp.priority}")
        print(f"    Konfidenz: {hyp.confidence:.0%} | Testbar: {'Ja' if hyp.testable else 'Nein'}")
        print()

    # Save outputs
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    output_base = args.output or results_dir / "press_hypotheses"

    saved_files: list[Path] = []

    if args.format in ("json", "both"):
        json_path = output_base.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        saved_files.append(json_path)

    if args.format in ("markdown", "both"):
        md_path = output_base.with_suffix(".md")
        md_content = generate_hypotheses_markdown(result)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        saved_files.append(md_path)

    print("-" * 60)
    print("GESPEICHERT:")
    for path in saved_files:
        print(f"  - {path}")

    # Update catalog if requested
    if args.update_catalog and result.hypotheses:
        catalog_path = Path("AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md")
        if catalog_path.exists():
            update_result = update_hypotheses_catalog(catalog_path, result)
            if update_result:
                print(f"  - {catalog_path} (aktualisiert)")
            else:
                print(f"  - {catalog_path} (keine Aenderungen)")
        else:
            print(f"  ! Katalog nicht gefunden: {catalog_path}")

    print("=" * 60 + "\n")

    return 0


def update_hypotheses_catalog(
    catalog_path: Path, result
) -> bool:
    """Append new hypotheses to HYPOTHESES_CATALOG.md.

    Args:
        catalog_path: Path to catalog markdown file
        result: PressHypothesesResult with new hypotheses

    Returns:
        True if catalog was updated
    """
    if not result.hypotheses:
        return False

    with open(catalog_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if press hypotheses section already exists
    if "## Hypothesen aus Pressemitteilungen" in content:
        # Don't duplicate - return False
        return False

    # Find the Changelog section
    changelog_marker = "## Changelog"
    if changelog_marker not in content:
        # Append at end
        insertion_point = len(content)
    else:
        insertion_point = content.index(changelog_marker)

    # Generate markdown for new hypotheses
    new_section = generate_hypotheses_markdown(result)
    new_section = "\n---\n\n" + new_section + "\n"

    # Insert before changelog
    updated_content = (
        content[:insertion_point] +
        new_section +
        content[insertion_point:]
    )

    # Add changelog entry
    today = datetime.now().strftime("%Y-%m-%d")
    hyp_ids = ", ".join([h.id for h in result.hypotheses])
    changelog_entry = (
        f"- {today}: **PRESS HYPOTHESES** - {len(result.hypotheses)} neue Hypothesen "
        f"aus Pressemitteilungen generiert ({hyp_ids})\n"
    )

    # Find position after "## Changelog"
    if changelog_marker in updated_content:
        changelog_pos = updated_content.index(changelog_marker) + len(changelog_marker)
        # Find end of line
        newline_pos = updated_content.index("\n", changelog_pos) + 1
        updated_content = (
            updated_content[:newline_pos] +
            "\n" + changelog_entry +
            updated_content[newline_pos:]
        )

    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return True


if __name__ == "__main__":
    sys.exit(main())
