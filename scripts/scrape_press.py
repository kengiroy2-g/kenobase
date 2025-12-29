#!/usr/bin/env python
# scripts/scrape_press.py
"""CLI script for scraping KENO winner press releases from Landeslotterien."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.scraper import (
    LANDESLOTTERIEN,
    PressReleaseScraper,
    get_scraper_config,
)
from kenobase.scraper.base import ScraperConfig


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def print_progress(code: str, status: str) -> None:
    """Print progress update."""
    config = LANDESLOTTERIEN.get(code)
    name = config.name if config else code
    print(f"  [{code}] {name}: {status}")


def list_lotterien() -> None:
    """Print list of all available Landeslotterien."""
    print("\nVerfuegbare Landeslotterien:")
    print("-" * 60)
    for code, config in sorted(LANDESLOTTERIEN.items()):
        print(f"  {code:15} {config.name:30} ({config.bundesland})")
    print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape KENO winner press releases from Landeslotterien",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Alle Landeslotterien scrapen
  python scripts/scrape_press.py --all

  # Nur bestimmte Lotterien
  python scripts/scrape_press.py --sites bayern nrw sachsen

  # Liste aller verfuegbaren Lotterien
  python scripts/scrape_press.py --list

  # Mit angepasster Verzoegerung (Rate Limiting)
  python scripts/scrape_press.py --sites bayern --delay 3.0

  # Output in bestimmtes Verzeichnis
  python scripts/scrape_press.py --all --output results/scraped
        """,
    )

    # Action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--all",
        action="store_true",
        help="Scrape alle 16 Landeslotterien",
    )
    action_group.add_argument(
        "--sites",
        nargs="+",
        metavar="CODE",
        help="Nur bestimmte Lotterien scrapen (z.B. bayern nrw)",
    )
    action_group.add_argument(
        "--list",
        action="store_true",
        help="Liste aller verfuegbaren Landeslotterien anzeigen",
    )

    # Configuration arguments
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data/scraped"),
        help="Output-Verzeichnis (default: data/scraped)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Verzoegerung zwischen Requests in Sekunden (default: 2.0)",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=50,
        help="Maximale Artikel pro Seite (default: 50)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimale Extraktions-Konfidenz 0.0-1.0 (default: 0.3)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ausfuehrliche Ausgabe",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle --list
    if args.list:
        list_lotterien()
        return 0

    # Validate site codes
    if args.sites:
        invalid = [s for s in args.sites if s not in LANDESLOTTERIEN]
        if invalid:
            print(f"Fehler: Unbekannte Lotterie-Codes: {', '.join(invalid)}")
            print("Verwende --list fuer eine Liste aller verfuegbaren Codes.")
            return 1

    # Create scraper config
    config = ScraperConfig(
        delay_between_requests=args.delay,
        delay_between_sites=args.delay * 2,
        max_articles_per_site=args.max_articles,
        min_confidence=args.min_confidence,
        output_dir=args.output,
    )

    # Create scraper
    scraper = PressReleaseScraper(config)

    # Determine sites to scrape
    codes = args.sites if args.sites else None

    # Print header
    print("\n" + "=" * 60)
    print("KENO Winner Press Release Scraper")
    print("=" * 60)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sites: {len(codes) if codes else 16}")
    print(f"Output: {args.output}")
    print("-" * 60)

    # Run scraper
    print("\nScraping...\n")
    result = scraper.scrape_all(codes=codes, progress_callback=print_progress)

    # Print summary
    print("\n" + "-" * 60)
    print("ERGEBNIS:")
    print(f"  Sites gescraped:     {result.sites_scraped}")
    print(f"  Artikel gefunden:    {result.articles_found}")
    print(f"  Artikel geparst:     {result.articles_parsed}")
    print(f"  Records extrahiert:  {len(result.records)}")
    print(f"  Fehler:              {len(result.errors)}")
    print(f"  Dauer:               {result.duration_seconds:.1f}s")

    # Print extracted records
    if result.records:
        print("\n" + "-" * 60)
        print("EXTRAHIERTE GEWINNER:")
        print()
        for i, record in enumerate(result.records, 1):
            location = record.city or record.region or "Unbekannt"
            numbers_str = ",".join(map(str, record.numbers)) if record.numbers else "-"
            amount_str = f"{record.amount_eur:,.0f} EUR" if record.amount_eur else "-"

            print(f"  {i}. {record.bundesland} / {location}")
            print(f"     Zahlen: {numbers_str}")
            print(f"     Typ: {record.keno_type or '-'} | Betrag: {amount_str}")
            print(f"     Konfidenz: {record.extraction_confidence:.0%}")
            print()

    # Print errors if any
    if result.errors and args.verbose:
        print("-" * 60)
        print("FEHLER:")
        for error in result.errors:
            print(f"  - {error}")

    # Save results
    output_path = scraper.save_results(result)
    print("-" * 60)
    print(f"Ergebnisse gespeichert: {output_path}")
    print("=" * 60 + "\n")

    return 0 if not result.errors else 1


if __name__ == "__main__":
    sys.exit(main())
