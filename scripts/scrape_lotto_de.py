#!/usr/bin/env python
# scripts/scrape_lotto_de.py
"""CLI script for scraping KENO archive from lotto.de (DLTB)."""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.scraper.lotto_de import (
    LottoDeScraper,
    analyze_birthday_correlation,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def print_progress(current_date: datetime, days_done: int, total_days: int) -> None:
    """Print progress update."""
    pct = (days_done / total_days) * 100
    print(
        f"\r  [{days_done}/{total_days}] {current_date.strftime('%Y-%m-%d')} "
        f"({pct:.1f}%)",
        end="",
        flush=True,
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape KENO archive from lotto.de (DLTB central source)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Letzte 30 Tage scrapen
  python scripts/scrape_lotto_de.py --recent 30

  # Bestimmten Zeitraum scrapen
  python scripts/scrape_lotto_de.py --start 2024-01-01 --end 2024-12-31

  # Nur ein bestimmtes Datum
  python scripts/scrape_lotto_de.py --date 2024-06-15

  # Mit Birthday-Korrelationsanalyse
  python scripts/scrape_lotto_de.py --recent 365 --analyze
        """,
    )

    # Date selection
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "--recent",
        type=int,
        metavar="DAYS",
        help="Scrape letzte N Tage",
    )
    date_group.add_argument(
        "--date",
        type=str,
        metavar="YYYY-MM-DD",
        help="Scrape einzelnes Datum",
    )
    date_group.add_argument(
        "--start",
        type=str,
        metavar="YYYY-MM-DD",
        help="Startdatum (erfordert --end)",
    )

    parser.add_argument(
        "--end",
        type=str,
        metavar="YYYY-MM-DD",
        help="Enddatum (erfordert --start)",
    )

    # Options
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data/lotto_de"),
        help="Output-Verzeichnis (default: data/lotto_de)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Verzoegerung zwischen Requests in Sekunden (default: 1.0)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Birthday-Korrelationsanalyse durchfuehren",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ausfuehrliche Ausgabe",
    )

    args = parser.parse_args()

    # Validate date range
    if args.start and not args.end:
        print("Fehler: --start erfordert --end")
        return 1
    if args.end and not args.start:
        print("Fehler: --end erfordert --start")
        return 1

    # Setup logging
    setup_logging(args.verbose)

    # Parse dates
    if args.date:
        start_date = datetime.strptime(args.date, "%Y-%m-%d")
        end_date = start_date
    elif args.recent:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.recent)
    else:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")

    # Create scraper
    scraper = LottoDeScraper(delay_between_requests=args.delay)

    # Print header
    print("\n" + "=" * 60)
    print("LOTTO.de KENO Archive Scraper")
    print("=" * 60)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Zeitraum: {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}")
    print(f"Output: {args.output}")
    print("-" * 60)

    # Scrape
    print("\nScraping...\n")
    results = scraper.fetch_date_range(
        start_date,
        end_date,
        progress_callback=print_progress,
    )
    print()  # Newline after progress

    # Summary
    print("\n" + "-" * 60)
    print("ERGEBNIS:")
    print(f"  Ziehungen geladen:  {len(results)}")

    if results:
        draws_with_winners = [r for r in results if r.total_winners is not None]
        print(f"  Mit Gewinnerzahlen: {len(draws_with_winners)}")

        # Show sample
        print("\n  Beispiel-Ziehungen:")
        for r in results[:3]:
            print(f"    {r.date.strftime('%Y-%m-%d')}: {r.numbers[:5]}... "
                  f"(Birthday: {r.birthday_score:.0%})")

    # Analyze if requested
    if args.analyze and results:
        print("\n" + "-" * 60)
        print("BIRTHDAY-KORRELATIONSANALYSE:")

        analysis = analyze_birthday_correlation(results)

        if "error" in analysis:
            print(f"  Fehler: {analysis['error']}")
        else:
            print(f"  Ziehungen analysiert: {analysis['total_draws_analyzed']}")
            print(f"  Korrelation: {analysis['correlation_birthday_vs_winners']:.4f}")
            print(f"  Interpretation: {analysis['interpretation']}")
            print()
            print(f"  High-Birthday Ziehungen (>50%): {analysis['high_birthday_draws']}")
            print(f"    Durchschnittl. Gewinner: {analysis['avg_winners_high_birthday']:.0f}")
            print(f"  Low-Birthday Ziehungen (<35%): {analysis['low_birthday_draws']}")
            print(f"    Durchschnittl. Gewinner: {analysis['avg_winners_low_birthday']:.0f}")

            if analysis['winner_ratio']:
                print(f"  Verhaeltnis High/Low: {analysis['winner_ratio']:.2f}x")

    # Save results
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output / f"keno_archive_{timestamp}.json"
        scraper.save_results(results, output_file)
        print("\n" + "-" * 60)
        print(f"Ergebnisse gespeichert: {output_file}")

    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
