"""Wiederkehrende Gewinnzahlen (WGZ) Analyse fuer Kenobase V2.0.

Dieses Modul analysiert wiederkehrende Muster in Lottoziehungen:
- Wiederholungsrate: Wie oft wiederholen sich Zahlen zwischen Ziehungen?
- GK1-Korrelation: Korrelieren Wiederholungen mit Gewinnklasse-1-Ereignissen?
- Paar-Stabilitaet: Welche Zahlenpaare treten stabil gemeinsam auf?

HYP-006: Pattern-Analyse und Kombinatorik
Kernfrage: Wiederholen sich Zahlen in identifizierbaren Mustern?

Usage:
    from kenobase.analysis.recurrence import (
        RecurrenceResult,
        analyze_recurrence,
        calculate_gk1_correlation,
        analyze_pair_stability,
    )

    # Einzelne Analyse
    result = analyze_recurrence(draws, window=1)

    # GK1-Korrelation
    corr = calculate_gk1_correlation(draws, gk1_events)

    # Paar-Stabilitaet
    stability = analyze_pair_stability(draws, min_occurrences=3)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass
class RecurrenceResult:
    """Ergebnis der Wiederholungsanalyse.

    Attributes:
        total_draws: Gesamtanzahl analysierter Ziehungen
        draws_with_recurrence: Anzahl Ziehungen mit mind. einer Wiederholung
        recurrence_rate: Anteil Ziehungen mit Wiederholungen (0.0-1.0)
        avg_recurrence_count: Durchschnittliche Anzahl Wiederholungen pro Ziehung
        max_recurrence_count: Maximale Wiederholungen in einer Ziehung
        recurrence_by_number: Dict[Zahl, Anzahl Wiederholungen]
        consecutive_pairs: Liste von (Zahl, Anzahl aufeinanderfolgender Erscheinungen)
    """

    total_draws: int
    draws_with_recurrence: int
    recurrence_rate: float
    avg_recurrence_count: float
    max_recurrence_count: int
    recurrence_by_number: dict[int, int] = field(default_factory=dict)
    consecutive_pairs: list[tuple[int, int]] = field(default_factory=list)

    @property
    def recurrence_percentage(self) -> float:
        """Wiederholungsrate als Prozent."""
        return self.recurrence_rate * 100.0


@dataclass
class PairStabilityResult:
    """Ergebnis der Paar-Stabilitaetsanalyse.

    Attributes:
        total_pairs_analyzed: Gesamtanzahl analysierter Paare
        stable_pairs: Paare die >= min_occurrences erscheinen
        stability_score: Anteil stabiler Paare (0.0-1.0)
        top_pairs: Top N Paare nach Haeufigkeit
        pair_frequencies: Dict[(a,b), count]
    """

    total_pairs_analyzed: int
    stable_pairs: list[tuple[tuple[int, int], int]]
    stability_score: float
    top_pairs: list[tuple[tuple[int, int], int]]
    pair_frequencies: dict[tuple[int, int], int] = field(default_factory=dict)


@dataclass
class GK1CorrelationResult:
    """Ergebnis der GK1-Korrelationsanalyse.

    Attributes:
        total_gk1_events: Anzahl GK1-Ereignisse
        gk1_with_prior_recurrence: GK1-Events mit Wiederholung in vorheriger Ziehung
        correlation_rate: Korrelationsrate (0.0-1.0)
        gk1_recurrence_numbers: Zahlen die bei GK1 wiederholt erschienen
        baseline_recurrence_rate: Basis-Wiederholungsrate ohne GK1-Filter
    """

    total_gk1_events: int
    gk1_with_prior_recurrence: int
    correlation_rate: float
    gk1_recurrence_numbers: list[int]
    baseline_recurrence_rate: float


@dataclass
class WeeklyCycleResult:
    """Ergebnis der Wochentagsverteilung-Analyse.

    Attributes:
        total_draws: Gesamtanzahl analysierter Ziehungen
        draws_by_weekday: Dict[Wochentag (0-6), Anzahl Ziehungen]
        recurrence_by_weekday: Dict[Wochentag, Wiederholungsrate]
        best_weekday: Wochentag mit hoechster Wiederholungsrate
        worst_weekday: Wochentag mit niedrigster Wiederholungsrate
        weekday_names: Mapping von Wochentag-Index zu Namen
    """

    total_draws: int
    draws_by_weekday: dict[int, int] = field(default_factory=dict)
    recurrence_by_weekday: dict[int, float] = field(default_factory=dict)
    best_weekday: int | None = None
    worst_weekday: int | None = None
    weekday_names: dict[int, str] = field(default_factory=lambda: {
        0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag",
        4: "Freitag", 5: "Samstag", 6: "Sonntag"
    })


@dataclass
class RecurrenceDaysResult:
    """Ergebnis der tagesbasierten Wiederholungsanalyse.

    Attributes:
        days: Anzahl Tage fuer Lookback
        total_draws: Gesamtanzahl analysierter Ziehungen
        draws_with_recurrence: Anzahl Ziehungen mit mind. einer Wiederholung
        recurrence_rate: Anteil Ziehungen mit Wiederholungen (0.0-1.0)
        avg_recurrence_count: Durchschnittliche Anzahl Wiederholungen
        max_recurrence_count: Maximale Wiederholungen
        recurrence_by_number: Dict[Zahl, Anzahl Wiederholungen]
    """

    days: int
    total_draws: int
    draws_with_recurrence: int
    recurrence_rate: float
    avg_recurrence_count: float
    max_recurrence_count: int
    recurrence_by_number: dict[int, int] = field(default_factory=dict)


def analyze_recurrence(
    draws: list[DrawResult],
    window: int = 1,
) -> RecurrenceResult:
    """Analysiert Wiederholungen zwischen aufeinanderfolgenden Ziehungen.

    Eine Wiederholung tritt auf, wenn eine Zahl in Ziehung N auch in
    Ziehung N-window erscheint.

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)
        window: Lookback-Fenster (1 = nur vorherige Ziehung)

    Returns:
        RecurrenceResult mit Wiederholungsstatistiken

    Example:
        >>> from kenobase.core.data_loader import DataLoader
        >>> loader = DataLoader()
        >>> draws = loader.load("data/KENO_Stats.csv")
        >>> result = analyze_recurrence(draws, window=1)
        >>> print(f"Wiederholungsrate: {result.recurrence_percentage:.1f}%")
        Wiederholungsrate: 42.3%
    """
    if len(draws) <= window:
        return RecurrenceResult(
            total_draws=0,
            draws_with_recurrence=0,
            recurrence_rate=0.0,
            avg_recurrence_count=0.0,
            max_recurrence_count=0,
        )

    # Sort by date ascending
    sorted_draws = sorted(draws, key=lambda d: d.date)

    recurrence_counts: list[int] = []
    recurrence_by_number: Counter[int] = Counter()
    consecutive_count: dict[int, int] = {}  # Track consecutive appearances

    for i in range(window, len(sorted_draws)):
        current_numbers = set(sorted_draws[i].numbers)

        # Collect all numbers from previous window draws
        previous_numbers: set[int] = set()
        for j in range(1, window + 1):
            previous_numbers.update(sorted_draws[i - j].numbers)

        # Find recurring numbers
        recurring = current_numbers.intersection(previous_numbers)
        recurrence_counts.append(len(recurring))

        # Track which numbers recur
        for num in recurring:
            recurrence_by_number[num] += 1
            consecutive_count[num] = consecutive_count.get(num, 0) + 1

        # Reset consecutive count for non-recurring numbers
        for num in current_numbers - recurring:
            if num in consecutive_count and consecutive_count[num] > 1:
                consecutive_count[num] = 0

    draws_with_recurrence = sum(1 for c in recurrence_counts if c > 0)
    total_analyzed = len(recurrence_counts)

    # Find numbers with longest consecutive runs
    consecutive_pairs = sorted(
        [(num, count) for num, count in consecutive_count.items() if count >= 2],
        key=lambda x: x[1],
        reverse=True,
    )[:20]  # Top 20

    return RecurrenceResult(
        total_draws=total_analyzed,
        draws_with_recurrence=draws_with_recurrence,
        recurrence_rate=draws_with_recurrence / total_analyzed if total_analyzed > 0 else 0.0,
        avg_recurrence_count=sum(recurrence_counts) / total_analyzed if total_analyzed > 0 else 0.0,
        max_recurrence_count=max(recurrence_counts) if recurrence_counts else 0,
        recurrence_by_number=dict(recurrence_by_number),
        consecutive_pairs=consecutive_pairs,
    )


def analyze_pair_stability(
    draws: list[DrawResult],
    min_occurrences: int = 3,
    top_n: int = 50,
) -> PairStabilityResult:
    """Analysiert die Stabilitaet von Zahlenpaaren ueber Ziehungen.

    Ein Paar gilt als stabil, wenn es mindestens min_occurrences mal
    gemeinsam in einer Ziehung erscheint.

    Args:
        draws: Liste von DrawResult-Objekten
        min_occurrences: Mindest-Haeufigkeit fuer stabile Paare
        top_n: Anzahl Top-Paare im Ergebnis

    Returns:
        PairStabilityResult mit Paar-Statistiken

    Example:
        >>> result = analyze_pair_stability(draws, min_occurrences=5)
        >>> print(f"Stabile Paare: {len(result.stable_pairs)}")
        >>> for pair, count in result.top_pairs[:5]:
        ...     print(f"  {pair}: {count}x")
    """
    pair_counter: Counter[tuple[int, int]] = Counter()

    for draw in draws:
        # Generate all pairs from this draw
        for pair in combinations(sorted(draw.numbers), 2):
            pair_counter[pair] += 1

    total_pairs = len(pair_counter)

    # Filter stable pairs
    stable_pairs = [
        (pair, count)
        for pair, count in pair_counter.items()
        if count >= min_occurrences
    ]
    stable_pairs.sort(key=lambda x: x[1], reverse=True)

    # Top N pairs
    top_pairs = stable_pairs[:top_n]

    stability_score = len(stable_pairs) / total_pairs if total_pairs > 0 else 0.0

    return PairStabilityResult(
        total_pairs_analyzed=total_pairs,
        stable_pairs=stable_pairs,
        stability_score=stability_score,
        top_pairs=top_pairs,
        pair_frequencies=dict(pair_counter),
    )


def calculate_gk1_correlation(
    draws: list[DrawResult],
    gk1_dates: list[datetime],
    window: int = 1,
) -> GK1CorrelationResult:
    """Berechnet Korrelation zwischen Wiederholungen und GK1-Ereignissen.

    Untersucht ob Wiederholungen in der Ziehung vor einem GK1-Ereignis
    haeufiger auftreten als im Durchschnitt.

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)
        gk1_dates: Liste von Daten mit GK1-Treffern
        window: Lookback-Fenster fuer Wiederholungs-Check

    Returns:
        GK1CorrelationResult mit Korrelationsstatistiken

    Example:
        >>> gk1_dates = [datetime(2024, 1, 15), datetime(2024, 2, 20)]
        >>> corr = calculate_gk1_correlation(draws, gk1_dates)
        >>> print(f"GK1-Korrelation: {corr.correlation_rate:.2%}")
    """
    if len(draws) <= window:
        return GK1CorrelationResult(
            total_gk1_events=0,
            gk1_with_prior_recurrence=0,
            correlation_rate=0.0,
            gk1_recurrence_numbers=[],
            baseline_recurrence_rate=0.0,
        )

    # Sort draws by date
    sorted_draws = sorted(draws, key=lambda d: d.date)
    gk1_date_set = set(gk1_dates)

    # Build date-to-draw index
    date_to_idx: dict[datetime, int] = {}
    for idx, draw in enumerate(sorted_draws):
        # Normalize date to date-only for comparison
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_to_idx[draw_date] = idx

    # Calculate baseline recurrence rate
    baseline_result = analyze_recurrence(sorted_draws, window=window)
    baseline_rate = baseline_result.recurrence_rate

    # Analyze recurrence before GK1 events
    gk1_with_recurrence = 0
    gk1_recurrence_numbers: list[int] = []
    total_gk1_found = 0

    for gk1_date in gk1_dates:
        # Normalize GK1 date
        normalized_gk1 = gk1_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if normalized_gk1 not in date_to_idx:
            continue

        gk1_idx = date_to_idx[normalized_gk1]
        if gk1_idx < window:
            continue

        total_gk1_found += 1

        # Get current and previous draws
        current_numbers = set(sorted_draws[gk1_idx].numbers)
        previous_numbers: set[int] = set()
        for j in range(1, window + 1):
            previous_numbers.update(sorted_draws[gk1_idx - j].numbers)

        recurring = current_numbers.intersection(previous_numbers)

        if len(recurring) > 0:
            gk1_with_recurrence += 1
            gk1_recurrence_numbers.extend(recurring)

    correlation_rate = (
        gk1_with_recurrence / total_gk1_found if total_gk1_found > 0 else 0.0
    )

    return GK1CorrelationResult(
        total_gk1_events=total_gk1_found,
        gk1_with_prior_recurrence=gk1_with_recurrence,
        correlation_rate=correlation_rate,
        gk1_recurrence_numbers=gk1_recurrence_numbers,
        baseline_recurrence_rate=baseline_rate,
    )


def analyze_number_streaks(
    draws: list[DrawResult],
    min_streak: int = 3,
) -> dict[int, list[tuple[datetime, datetime, int]]]:
    """Analysiert Serien (Streaks) einzelner Zahlen.

    Eine Serie ist eine Folge von Ziehungen in denen eine Zahl
    kontinuierlich erscheint.

    Args:
        draws: Liste von DrawResult-Objekten
        min_streak: Mindest-Laenge einer Serie

    Returns:
        Dict[Zahl, Liste von (start_date, end_date, length)]

    Example:
        >>> streaks = analyze_number_streaks(draws, min_streak=4)
        >>> for num, series in streaks.items():
        ...     print(f"Zahl {num}: {len(series)} Serien")
    """
    sorted_draws = sorted(draws, key=lambda d: d.date)

    # Track current streaks for each number
    current_streak: dict[int, tuple[datetime, int]] = {}  # num -> (start_date, length)
    completed_streaks: dict[int, list[tuple[datetime, datetime, int]]] = {}

    for draw in sorted_draws:
        current_numbers = set(draw.numbers)
        draw_date = draw.date

        # Check all numbers 1-70 (KENO range)
        for num in range(1, 71):
            if num in current_numbers:
                if num in current_streak:
                    # Continue streak
                    start, length = current_streak[num]
                    current_streak[num] = (start, length + 1)
                else:
                    # Start new streak
                    current_streak[num] = (draw_date, 1)
            else:
                # Number not in this draw - end streak if exists
                if num in current_streak:
                    start, length = current_streak[num]
                    if length >= min_streak:
                        if num not in completed_streaks:
                            completed_streaks[num] = []
                        completed_streaks[num].append((start, draw_date, length))
                    del current_streak[num]

    # Finalize remaining streaks
    if sorted_draws:
        last_date = sorted_draws[-1].date
        for num, (start, length) in current_streak.items():
            if length >= min_streak:
                if num not in completed_streaks:
                    completed_streaks[num] = []
                completed_streaks[num].append((start, last_date, length))

    return completed_streaks


def analyze_weekly_cycle(
    draws: list[DrawResult],
) -> WeeklyCycleResult:
    """Analysiert die Wiederholungsrate nach Wochentagen.

    Untersucht ob bestimmte Wochentage hoehere Wiederholungsraten aufweisen.
    Dies ist relevant fuer HYP-006 7-Tage-Zyklus-Analyse.

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)

    Returns:
        WeeklyCycleResult mit Wochentags-Statistiken

    Example:
        >>> result = analyze_weekly_cycle(draws)
        >>> print(f"Bester Tag: {result.weekday_names[result.best_weekday]}")
        >>> for day, rate in result.recurrence_by_weekday.items():
        ...     print(f"  {result.weekday_names[day]}: {rate:.1%}")
    """
    if len(draws) < 2:
        return WeeklyCycleResult(total_draws=len(draws))

    sorted_draws = sorted(draws, key=lambda d: d.date)

    # Track draws and recurrences by weekday
    draws_by_weekday: dict[int, int] = {i: 0 for i in range(7)}
    recurrence_counts_by_weekday: dict[int, list[int]] = {i: [] for i in range(7)}

    for i in range(1, len(sorted_draws)):
        current_draw = sorted_draws[i]
        previous_draw = sorted_draws[i - 1]

        weekday = current_draw.date.weekday()
        draws_by_weekday[weekday] += 1

        # Calculate recurrence from previous draw
        current_numbers = set(current_draw.numbers)
        previous_numbers = set(previous_draw.numbers)
        recurring_count = len(current_numbers.intersection(previous_numbers))
        recurrence_counts_by_weekday[weekday].append(recurring_count)

    # Calculate recurrence rate per weekday (rate = draws with any recurrence / total)
    recurrence_by_weekday: dict[int, float] = {}
    for day in range(7):
        counts = recurrence_counts_by_weekday[day]
        if counts:
            # Rate = proportion of draws with at least one recurrence
            recurrence_by_weekday[day] = sum(1 for c in counts if c > 0) / len(counts)
        else:
            recurrence_by_weekday[day] = 0.0

    # Find best and worst weekdays (only among days with data)
    active_days = {d: r for d, r in recurrence_by_weekday.items() if draws_by_weekday[d] > 0}
    best_weekday = max(active_days, key=active_days.get) if active_days else None
    worst_weekday = min(active_days, key=active_days.get) if active_days else None

    return WeeklyCycleResult(
        total_draws=len(draws) - 1,
        draws_by_weekday=draws_by_weekday,
        recurrence_by_weekday=recurrence_by_weekday,
        best_weekday=best_weekday,
        worst_weekday=worst_weekday,
    )


def analyze_recurrence_days(
    draws: list[DrawResult],
    days: int = 7,
) -> RecurrenceDaysResult:
    """Analysiert Wiederholungen ueber einen bestimmten Zeitraum in Tagen.

    Im Gegensatz zu analyze_recurrence (window = Anzahl Ziehungen) basiert
    diese Funktion auf echten Kalendertagen. Relevant fuer 7-Tage-Zyklus.

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)
        days: Lookback-Zeitraum in Kalendertagen (default: 7 fuer Wochen-Zyklus)

    Returns:
        RecurrenceDaysResult mit tagesbasierter Wiederholungsstatistik

    Example:
        >>> result = analyze_recurrence_days(draws, days=7)
        >>> print(f"7-Tage-Wiederholungsrate: {result.recurrence_rate:.1%}")
    """
    if len(draws) < 2:
        return RecurrenceDaysResult(
            days=days,
            total_draws=0,
            draws_with_recurrence=0,
            recurrence_rate=0.0,
            avg_recurrence_count=0.0,
            max_recurrence_count=0,
        )

    from datetime import timedelta

    sorted_draws = sorted(draws, key=lambda d: d.date)

    recurrence_counts: list[int] = []
    recurrence_by_number: Counter[int] = Counter()
    analyzable_draws = 0

    for i, current_draw in enumerate(sorted_draws):
        # Collect all numbers from draws within the last 'days' calendar days
        cutoff_date = current_draw.date - timedelta(days=days)
        previous_numbers: set[int] = set()

        for j in range(i - 1, -1, -1):
            prev_draw = sorted_draws[j]
            if prev_draw.date < cutoff_date:
                break
            previous_numbers.update(prev_draw.numbers)

        # Skip first draws that don't have enough history
        if not previous_numbers:
            continue

        analyzable_draws += 1
        current_numbers = set(current_draw.numbers)
        recurring = current_numbers.intersection(previous_numbers)
        recurrence_counts.append(len(recurring))

        for num in recurring:
            recurrence_by_number[num] += 1

    if analyzable_draws == 0:
        return RecurrenceDaysResult(
            days=days,
            total_draws=0,
            draws_with_recurrence=0,
            recurrence_rate=0.0,
            avg_recurrence_count=0.0,
            max_recurrence_count=0,
        )

    draws_with_recurrence = sum(1 for c in recurrence_counts if c > 0)

    return RecurrenceDaysResult(
        days=days,
        total_draws=analyzable_draws,
        draws_with_recurrence=draws_with_recurrence,
        recurrence_rate=draws_with_recurrence / analyzable_draws,
        avg_recurrence_count=sum(recurrence_counts) / analyzable_draws,
        max_recurrence_count=max(recurrence_counts) if recurrence_counts else 0,
        recurrence_by_number=dict(recurrence_by_number),
    )


def generate_recurrence_report(
    draws: list[DrawResult],
    gk1_dates: list[datetime] | None = None,
    config: dict | None = None,
) -> dict:
    """Generiert einen vollstaendigen WGZ-Report.

    Kombiniert alle Analysen in einen Report fuer HYP-006.

    Args:
        draws: Liste von DrawResult-Objekten
        gk1_dates: Optionale Liste von GK1-Daten
        config: Optionale Konfiguration mit Schwellwerten

    Returns:
        Dict mit Report-Daten fuer JSON-Export

    Example:
        >>> report = generate_recurrence_report(draws, gk1_dates)
        >>> import json
        >>> with open("wgz_report.json", "w") as f:
        ...     json.dump(report, f, indent=2, default=str)
    """
    config = config or {}
    window = config.get("window", 1)
    min_occurrences = config.get("min_occurrences", 3)
    min_streak = config.get("min_streak", 3)
    top_n = config.get("top_n", 50)
    recurrence_days = config.get("recurrence_days", 7)

    # Run all analyses
    recurrence = analyze_recurrence(draws, window=window)
    pair_stability = analyze_pair_stability(draws, min_occurrences=min_occurrences, top_n=top_n)
    streaks = analyze_number_streaks(draws, min_streak=min_streak)
    weekly_cycle = analyze_weekly_cycle(draws)
    recurrence_7d = analyze_recurrence_days(draws, days=recurrence_days)

    # GK1 correlation if dates provided
    gk1_correlation = None
    if gk1_dates:
        gk1_correlation = calculate_gk1_correlation(draws, gk1_dates, window=window)

    # Build report
    report = {
        "metadata": {
            "hypothesis": "HYP-006",
            "description": "Wiederkehrende Gewinnzahlen (WGZ) Analyse",
            "generated_at": datetime.now().isoformat(),
            "total_draws": len(draws),
            "config": {
                "window": window,
                "min_occurrences": min_occurrences,
                "min_streak": min_streak,
                "top_n": top_n,
                "recurrence_days": recurrence_days,
            },
        },
        "recurrence": {
            "total_draws": recurrence.total_draws,
            "draws_with_recurrence": recurrence.draws_with_recurrence,
            "recurrence_rate": recurrence.recurrence_rate,
            "recurrence_percentage": recurrence.recurrence_percentage,
            "avg_recurrence_count": recurrence.avg_recurrence_count,
            "max_recurrence_count": recurrence.max_recurrence_count,
            "top_recurring_numbers": sorted(
                recurrence.recurrence_by_number.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:20],
            "consecutive_pairs": recurrence.consecutive_pairs,
        },
        "pair_stability": {
            "total_pairs_analyzed": pair_stability.total_pairs_analyzed,
            "stable_pairs_count": len(pair_stability.stable_pairs),
            "stability_score": pair_stability.stability_score,
            "top_pairs": [
                {"pair": list(pair), "count": count}
                for pair, count in pair_stability.top_pairs
            ],
        },
        "streaks": {
            "numbers_with_streaks": len(streaks),
            "total_streaks": sum(len(s) for s in streaks.values()),
            "top_streaks": sorted(
                [
                    {"number": num, "streak_count": len(series), "max_length": max(s[2] for s in series)}
                    for num, series in streaks.items()
                ],
                key=lambda x: x["max_length"],
                reverse=True,
            )[:20],
        },
        "weekly_cycle": {
            "total_draws": weekly_cycle.total_draws,
            "draws_by_weekday": {
                weekly_cycle.weekday_names.get(d, str(d)): count
                for d, count in weekly_cycle.draws_by_weekday.items()
            },
            "recurrence_by_weekday": {
                weekly_cycle.weekday_names.get(d, str(d)): rate
                for d, rate in weekly_cycle.recurrence_by_weekday.items()
            },
            "best_weekday": weekly_cycle.weekday_names.get(weekly_cycle.best_weekday, None)
            if weekly_cycle.best_weekday is not None else None,
            "worst_weekday": weekly_cycle.weekday_names.get(weekly_cycle.worst_weekday, None)
            if weekly_cycle.worst_weekday is not None else None,
        },
        "recurrence_7d": {
            "days": recurrence_7d.days,
            "total_draws": recurrence_7d.total_draws,
            "draws_with_recurrence": recurrence_7d.draws_with_recurrence,
            "recurrence_rate": recurrence_7d.recurrence_rate,
            "avg_recurrence_count": recurrence_7d.avg_recurrence_count,
            "max_recurrence_count": recurrence_7d.max_recurrence_count,
            "top_recurring_numbers": sorted(
                recurrence_7d.recurrence_by_number.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:20],
        },
    }

    if gk1_correlation:
        report["gk1_correlation"] = {
            "total_gk1_events": gk1_correlation.total_gk1_events,
            "gk1_with_prior_recurrence": gk1_correlation.gk1_with_prior_recurrence,
            "correlation_rate": gk1_correlation.correlation_rate,
            "baseline_recurrence_rate": gk1_correlation.baseline_recurrence_rate,
            "correlation_vs_baseline": (
                gk1_correlation.correlation_rate - gk1_correlation.baseline_recurrence_rate
            ),
            "is_significant": (
                gk1_correlation.correlation_rate > gk1_correlation.baseline_recurrence_rate * 1.1
            ),
        }

    # Acceptance Criteria Check
    report["acceptance_criteria"] = {
        "AC1_recurrence_rate_calculated": recurrence.recurrence_rate > 0,
        "AC2_pair_stability_measured": pair_stability.total_pairs_analyzed > 0,
        "AC3_gk1_correlation_computed": gk1_correlation is not None,
        "AC4_streaks_identified": len(streaks) > 0,
        "AC5_7day_recurrence_calculated": recurrence_7d.total_draws > 0,
        "AC6_weekly_cycle_analyzed": weekly_cycle.total_draws > 0,
    }

    return report


__all__ = [
    "RecurrenceResult",
    "PairStabilityResult",
    "GK1CorrelationResult",
    "WeeklyCycleResult",
    "RecurrenceDaysResult",
    "analyze_recurrence",
    "analyze_pair_stability",
    "calculate_gk1_correlation",
    "analyze_number_streaks",
    "analyze_weekly_cycle",
    "analyze_recurrence_days",
    "generate_recurrence_report",
]
