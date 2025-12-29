#!/usr/bin/env python3
"""HYP-EVENT: KENO GK1-Events vs. Deutsche Events Korrelation.

Analysiert ob GK1-Jackpot-Events zeitlich mit wichtigen deutschen
nationalen/internationalen Events korrelieren.

Hypothese: Jackpots koennten zeitlich mit wichtigen Events korrelieren
um mediale Aufmerksamkeit zu maximieren.

Events zu pruefen:
- Feiertage (Neujahr, Ostern, Tag der Arbeit, Pfingsten, Einheit, Weihnachten)
- Sport-Events (WM 2022, EM 2024)
- Wirtschaft (Monatsanfang, Monatsende)

Usage:
    python scripts/analyze_event_correlation.py
    python scripts/analyze_event_correlation.py --gk1-data Keno_GPTs/10-9_KGDaten_gefiltert.csv
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class GermanEventsCalendar:
    """German events calendar for 2022-2024."""

    # Fixed holidays (month, day)
    fixed_holidays: dict[str, tuple[int, int]] = field(default_factory=lambda: {
        "neujahr": (1, 1),
        "tag_der_arbeit": (5, 1),
        "tag_der_einheit": (10, 3),
        "heiligabend": (12, 24),
        "weihnachten_1": (12, 25),
        "weihnachten_2": (12, 26),
        "silvester": (12, 31),
    })

    # Easter dates for 2022-2024 (variable)
    easter_dates: dict[int, date] = field(default_factory=lambda: {
        2022: date(2022, 4, 17),
        2023: date(2023, 4, 9),
        2024: date(2024, 3, 31),
    })

    # Major sport events
    wm_2022: tuple[date, date] = (date(2022, 11, 21), date(2022, 12, 18))
    em_2024: tuple[date, date] = (date(2024, 6, 14), date(2024, 7, 14))

    def get_all_holidays(self, start_date: date, end_date: date) -> list[date]:
        """Get all fixed holidays in date range."""
        holidays = []
        for year in range(start_date.year, end_date.year + 1):
            for name, (month, day) in self.fixed_holidays.items():
                try:
                    holiday = date(year, month, day)
                    if start_date <= holiday <= end_date:
                        holidays.append(holiday)
                except ValueError:
                    pass  # Invalid date
        return sorted(holidays)

    def get_easter_holidays(self, start_date: date, end_date: date) -> list[date]:
        """Get Easter-related holidays (Karfreitag, Ostern, Ostermontag, Pfingsten)."""
        holidays = []
        for year, easter in self.easter_dates.items():
            if start_date.year <= year <= end_date.year:
                # Karfreitag (Good Friday): 2 days before Easter
                karfreitag = easter - timedelta(days=2)
                # Ostersonntag (Easter Sunday)
                ostersonntag = easter
                # Ostermontag (Easter Monday)
                ostermontag = easter + timedelta(days=1)
                # Pfingstsonntag (Pentecost): 49 days after Easter
                pfingstsonntag = easter + timedelta(days=49)
                # Pfingstmontag
                pfingstmontag = easter + timedelta(days=50)

                for h in [karfreitag, ostersonntag, ostermontag, pfingstsonntag, pfingstmontag]:
                    if start_date <= h <= end_date:
                        holidays.append(h)
        return sorted(holidays)

    def is_near_holiday(self, check_date: date, window_days: int = 7) -> bool:
        """Check if date is within window_days of any holiday."""
        all_holidays = (
            self.get_all_holidays(
                check_date - timedelta(days=window_days),
                check_date + timedelta(days=window_days),
            )
            + self.get_easter_holidays(
                check_date - timedelta(days=window_days),
                check_date + timedelta(days=window_days),
            )
        )
        for holiday in all_holidays:
            if abs((check_date - holiday).days) <= window_days:
                return True
        return False

    def is_during_wm_2022(self, check_date: date) -> bool:
        """Check if date is during FIFA World Cup 2022."""
        return self.wm_2022[0] <= check_date <= self.wm_2022[1]

    def is_during_em_2024(self, check_date: date) -> bool:
        """Check if date is during UEFA Euro 2024."""
        return self.em_2024[0] <= check_date <= self.em_2024[1]

    def is_month_start(self, check_date: date) -> bool:
        """Check if date is in first 5 days of month (pay day period)."""
        return 1 <= check_date.day <= 5

    def is_month_end(self, check_date: date) -> bool:
        """Check if date is in last 7 days of month."""
        # Get last day of month
        if check_date.month == 12:
            last_day = date(check_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(check_date.year, check_date.month + 1, 1) - timedelta(days=1)
        return check_date.day >= 25 or check_date == last_day

    def is_quarter_end(self, check_date: date) -> bool:
        """Check if date is near quarter end (last 7 days of quarter)."""
        quarter_ends = [
            date(check_date.year, 3, 31),
            date(check_date.year, 6, 30),
            date(check_date.year, 9, 30),
            date(check_date.year, 12, 31),
        ]
        for qe in quarter_ends:
            if abs((check_date - qe).days) <= 7:
                return True
        return False


@dataclass
class EventCorrelationResult:
    """Result of event correlation analysis."""

    hypothesis_id: str
    hypothesis_name: str
    analysis_date: str
    data_period: dict[str, str]

    # Baseline
    total_draws: int
    total_gk1_events: int
    baseline_probability: float

    # Event-specific probabilities
    event_probabilities: dict[str, dict[str, Any]]

    # Chi-square test results
    chi_square_results: dict[str, dict[str, float]]

    # Conclusion
    significant_events: list[str]
    conclusion: str
    is_hypothesis_supported: bool


def load_gk1_data(gk1_path: Path) -> pd.DataFrame:
    """Load GK1 events data."""
    df = pd.read_csv(gk1_path, sep=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def load_all_draws(keno_path: Path) -> pd.DataFrame:
    """Load all KENO draws to establish baseline."""
    df = pd.read_csv(keno_path, sep=";")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def calculate_conditional_probability(
    gk1_dates: list[date],
    all_dates: list[date],
    condition_func,
) -> tuple[float, int, int]:
    """Calculate P(GK1 | condition).

    Returns:
        Tuple of (probability, gk1_count_in_condition, total_count_in_condition)
    """
    # Count draws meeting condition
    condition_dates = [d for d in all_dates if condition_func(d)]
    total_in_condition = len(condition_dates)

    if total_in_condition == 0:
        return 0.0, 0, 0

    # Count GK1 events meeting condition
    gk1_in_condition = sum(1 for d in gk1_dates if condition_func(d))

    probability = gk1_in_condition / total_in_condition
    return probability, gk1_in_condition, total_in_condition


def perform_chi_square_test(
    gk1_in_condition: int,
    gk1_not_in_condition: int,
    total_in_condition: int,
    total_not_in_condition: int,
) -> tuple[float, float, int]:
    """Perform Chi-Square test for independence.

    Returns:
        Tuple of (chi2_stat, p_value, degrees_of_freedom)
    """
    # Observed frequencies
    # Rows: GK1 / No GK1
    # Cols: In Condition / Not In Condition
    no_gk1_in_condition = total_in_condition - gk1_in_condition
    no_gk1_not_in_condition = total_not_in_condition - gk1_not_in_condition

    observed = np.array([
        [gk1_in_condition, gk1_not_in_condition],
        [no_gk1_in_condition, no_gk1_not_in_condition],
    ])

    # Check for valid contingency table
    if observed.min() < 0 or observed.sum() == 0:
        return 0.0, 1.0, 1

    try:
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        return chi2, p, dof
    except ValueError:
        return 0.0, 1.0, 1


def run_event_correlation_analysis(
    gk1_path: Path,
    keno_path: Path,
    window_days: int = 7,
) -> EventCorrelationResult:
    """Run full event correlation analysis."""
    calendar = GermanEventsCalendar()

    # Load data
    gk1_df = load_gk1_data(gk1_path)
    keno_df = load_all_draws(keno_path)

    # Filter to 2022-2024
    start_date = date(2022, 1, 1)
    end_date = date(2024, 12, 31)

    gk1_df = gk1_df[
        (gk1_df["Datum"].dt.date >= start_date) & (gk1_df["Datum"].dt.date <= end_date)
    ]
    keno_df = keno_df[
        (keno_df["Datum"].dt.date >= start_date) & (keno_df["Datum"].dt.date <= end_date)
    ]

    gk1_dates = [d.date() for d in gk1_df["Datum"]]
    all_dates = [d.date() for d in keno_df["Datum"]]

    logger.info(f"Analysis period: {start_date} to {end_date}")
    logger.info(f"Total draws: {len(all_dates)}")
    logger.info(f"GK1 events: {len(gk1_dates)}")

    # Baseline probability
    baseline_prob = len(gk1_dates) / len(all_dates)
    logger.info(f"Baseline P(GK1): {baseline_prob:.6f}")

    # Define conditions to test
    conditions = {
        "near_holiday_7d": lambda d: calendar.is_near_holiday(d, window_days=7),
        "wm_2022": lambda d: calendar.is_during_wm_2022(d),
        "em_2024": lambda d: calendar.is_during_em_2024(d),
        "month_start_1_5": lambda d: calendar.is_month_start(d),
        "month_end_25_31": lambda d: calendar.is_month_end(d),
        "quarter_end": lambda d: calendar.is_quarter_end(d),
    }

    event_probabilities = {}
    chi_square_results = {}
    significant_events = []

    total_gk1 = len(gk1_dates)

    for condition_name, condition_func in conditions.items():
        logger.info(f"\nAnalyzing: {condition_name}")

        # Calculate conditional probability
        prob, gk1_count, total_count = calculate_conditional_probability(
            gk1_dates, all_dates, condition_func
        )

        # Calculate inverse condition
        inv_total = len(all_dates) - total_count
        inv_gk1 = total_gk1 - gk1_count

        # Chi-square test
        chi2, p_value, dof = perform_chi_square_test(
            gk1_count, inv_gk1, total_count, inv_total
        )

        # Calculate odds ratio
        if inv_gk1 > 0 and (total_count - gk1_count) > 0:
            odds_in_condition = gk1_count / (total_count - gk1_count) if total_count > gk1_count else float('inf')
            odds_not_in_condition = inv_gk1 / (inv_total - inv_gk1) if inv_total > inv_gk1 else float('inf')
            if odds_not_in_condition > 0:
                odds_ratio = odds_in_condition / odds_not_in_condition
            else:
                odds_ratio = float('inf')
        else:
            odds_ratio = 0.0

        event_probabilities[condition_name] = {
            "probability": prob,
            "gk1_count": gk1_count,
            "total_draws_in_condition": total_count,
            "baseline_probability": baseline_prob,
            "probability_ratio": prob / baseline_prob if baseline_prob > 0 else 0,
            "odds_ratio": odds_ratio if odds_ratio != float('inf') else None,
        }

        chi_square_results[condition_name] = {
            "chi2_stat": chi2,
            "p_value": p_value,
            "degrees_of_freedom": dof,
            "is_significant": p_value < 0.05,
        }

        logger.info(f"  P(GK1|{condition_name}): {prob:.6f}")
        logger.info(f"  GK1 events: {gk1_count}/{total_count}")
        logger.info(f"  Ratio vs baseline: {prob / baseline_prob if baseline_prob > 0 else 0:.3f}x")
        logger.info(f"  Chi2: {chi2:.4f}, p={p_value:.4f}")

        if p_value < 0.05:
            significant_events.append(condition_name)
            logger.info(f"  ** SIGNIFICANT **")

    # Determine conclusion
    if significant_events:
        conclusion = (
            f"Signifikante Korrelation gefunden fuer: {', '.join(significant_events)}. "
            f"Diese Events zeigen ueberdurchschnittliche GK1-Wahrscheinlichkeiten "
            f"(Chi-Quadrat p < 0.05)."
        )
        is_supported = True
    else:
        conclusion = (
            "Keine signifikante Korrelation zwischen GK1-Events und "
            "deutschen nationalen/internationalen Events gefunden. "
            "Die zeitliche Verteilung der Jackpots erscheint zufaellig."
        )
        is_supported = False

    return EventCorrelationResult(
        hypothesis_id="HYP-EVENT",
        hypothesis_name="GK1-Events vs. Deutsche Events Korrelation",
        analysis_date=datetime.now().isoformat(),
        data_period={
            "start": str(start_date),
            "end": str(end_date),
        },
        total_draws=len(all_dates),
        total_gk1_events=len(gk1_dates),
        baseline_probability=baseline_prob,
        event_probabilities=event_probabilities,
        chi_square_results=chi_square_results,
        significant_events=significant_events,
        conclusion=conclusion,
        is_hypothesis_supported=is_supported,
    )


def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    return obj


def export_result_to_json(result: EventCorrelationResult, output_path: Path) -> None:
    """Export result to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "hypothesis_id": result.hypothesis_id,
        "hypothesis_name": result.hypothesis_name,
        "analysis_date": result.analysis_date,
        "data_period": result.data_period,
        "baseline": {
            "total_draws": result.total_draws,
            "total_gk1_events": result.total_gk1_events,
            "baseline_probability": result.baseline_probability,
        },
        "event_correlations": convert_to_serializable(result.event_probabilities),
        "chi_square_tests": convert_to_serializable(result.chi_square_results),
        "summary": {
            "significant_events": result.significant_events,
            "conclusion": result.conclusion,
            "is_hypothesis_supported": result.is_hypothesis_supported,
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results exported to {output_path}")


def main():
    """Run event correlation analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-EVENT: GK1-Events vs. Deutsche Events Korrelation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--gk1-data",
        type=Path,
        default=project_root / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv",
        help="Path to GK1 events CSV",
    )
    parser.add_argument(
        "--keno-data",
        type=Path,
        default=project_root / "data" / "raw" / "keno" / "KENO_ab_2018.csv",
        help="Path to all KENO draws CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "results" / "event_correlation.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=7,
        help="Window days for holiday proximity (default: 7)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input files
    if not args.gk1_data.exists():
        logger.error(f"GK1 data file not found: {args.gk1_data}")
        sys.exit(1)

    if not args.keno_data.exists():
        logger.error(f"KENO data file not found: {args.keno_data}")
        sys.exit(1)

    logger.info("=" * 70)
    logger.info("HYP-EVENT: GK1-Events vs. Deutsche Events Korrelation")
    logger.info("=" * 70)
    logger.info(f"GK1 data:    {args.gk1_data}")
    logger.info(f"KENO data:   {args.keno_data}")
    logger.info(f"Output:      {args.output}")
    logger.info(f"Window days: {args.window_days}")

    # Run analysis
    result = run_event_correlation_analysis(
        args.gk1_data,
        args.keno_data,
        args.window_days,
    )

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"\nBaseline P(GK1): {result.baseline_probability:.6f}")
    logger.info(f"({result.total_gk1_events} GK1 events / {result.total_draws} draws)")

    logger.info("\nEvent Correlations:")
    logger.info(f"{'Event':<25} {'P(GK1)':<12} {'Ratio':<10} {'Chi2':<10} {'p-value':<10} {'Sig?':<6}")
    logger.info("-" * 73)

    for event_name in result.event_probabilities:
        ep = result.event_probabilities[event_name]
        cs = result.chi_square_results[event_name]
        sig = "*" if cs["is_significant"] else ""
        logger.info(
            f"{event_name:<25} {ep['probability']:<12.6f} {ep['probability_ratio']:<10.3f} "
            f"{cs['chi2_stat']:<10.4f} {cs['p_value']:<10.4f} {sig:<6}"
        )

    logger.info("\n" + "=" * 70)
    logger.info("CONCLUSION")
    logger.info("=" * 70)
    logger.info(result.conclusion)

    # Export results
    export_result_to_json(result, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
