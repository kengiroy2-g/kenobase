"""HYP-014: Mehrwochenschein Jackpot-Timing Analyse.

Analysiert ob Jackpot-Hits bevorzugt am Anfang oder Ende von
Abo-Perioden (Mehrwochenscheine) auftreten. Verwendet Monte-Carlo
Simulation da keine echten Abo-Daten verfuegbar sind.

Hypothese: Falls RNG durch Tippscheine beeinflusst wird, koennten
Jackpot-Treffer systematisch zu bestimmten Zeitpunkten innerhalb
von Abo-Perioden auftreten (z.B. Ende, um Verlaengerung zu motivieren).

Acceptance Criteria:
- Chi-Quadrat Uniformitaetstest p > 0.05 -> keine Manipulation
- p < 0.05 -> signifikante Abweichung von Zufallsverteilung
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

# Standard-Abo-Laengen (Tage)
ABO_LENGTHS = [7, 14, 28]

# Position-Bins fuer Histogramm (quartile-basiert)
N_POSITION_BINS = 4


@dataclass
class SimulationConfig:
    """Konfiguration fuer Monte-Carlo Simulation.

    Attributes:
        n_simulations: Anzahl Simulationen (default 10000)
        random_seed: Seed fuer Reproduzierbarkeit (default 42)
        abo_lengths: Liste der Abo-Laengen in Tagen
    """

    n_simulations: int = 10000
    random_seed: int = 42
    abo_lengths: list[int] = field(default_factory=lambda: [7, 14, 28])


@dataclass
class PositionDistribution:
    """Verteilung der Jackpot-Positionen innerhalb Abo-Perioden.

    Attributes:
        abo_length: Abo-Laenge in Tagen
        n_jackpots: Anzahl analysierter Jackpots
        position_counts: Anzahl pro Position-Bin (0-3 fuer Quartile)
        position_labels: Labels fuer Bins (z.B. "Tag 1-7" fuer 28-Tage-Abo)
        mean_position_ratio: Mittlere relative Position (0.0-1.0)
        std_position_ratio: Standardabweichung der relativen Position
    """

    abo_length: int
    n_jackpots: int
    position_counts: list[int]
    position_labels: list[str]
    mean_position_ratio: float
    std_position_ratio: float


@dataclass
class ChiSquareResult:
    """Ergebnis des Chi-Quadrat Uniformitaetstests.

    Attributes:
        abo_length: Abo-Laenge in Tagen
        chi2_statistic: Chi-Quadrat Teststatistik
        p_value: p-Wert des Tests
        df: Freiheitsgrade
        is_uniform: True wenn p > 0.05 (keine signifikante Abweichung)
        interpretation: Textuelle Interpretation
    """

    abo_length: int
    chi2_statistic: float
    p_value: float
    df: int
    is_uniform: bool
    interpretation: str


@dataclass
class MonteCarloComparison:
    """Vergleich mit Monte-Carlo Baseline.

    Attributes:
        abo_length: Abo-Laenge in Tagen
        observed_mean_ratio: Beobachtete mittlere Position-Ratio
        simulated_mean_ratio: Mittlere Position-Ratio aus MC Simulation
        simulated_std_ratio: Std der Position-Ratio aus MC Simulation
        z_score: Z-Score des beobachteten Wertes
        p_value_mc: p-Wert (zweiseitig) aus MC-Vergleich
        is_significant: True wenn p < 0.05
    """

    abo_length: int
    observed_mean_ratio: float
    simulated_mean_ratio: float
    simulated_std_ratio: float
    z_score: float
    p_value_mc: float
    is_significant: bool


@dataclass
class MultiweekTimingResult:
    """Gesamtergebnis der HYP-014 Analyse.

    Attributes:
        hypothesis_id: HYP-014
        analysis_date: Datum der Analyse
        data_source: Beschreibung der Datenquelle
        n_jackpots: Anzahl analysierter Jackpot-Ereignisse
        date_range_start: Startdatum des Analysezeitraums
        date_range_end: Enddatum des Analysezeitraums
        simulation_config: Monte-Carlo Konfiguration
        distributions: Position-Verteilungen pro Abo-Laenge
        chi2_results: Chi-Quadrat Testergebnisse pro Abo-Laenge
        mc_comparisons: Monte-Carlo Vergleiche pro Abo-Laenge
        verdict: Gesamtergebnis (BESTAETIGT/NICHT_BESTAETIGT/UNKLAR)
        confidence: Konfidenz des Verdicts (0.0-1.0)
        acceptance_criteria_met: True wenn keine Manipulation erkannt
    """

    hypothesis_id: str = "HYP-014"
    analysis_date: str = ""
    data_source: str = ""
    n_jackpots: int = 0
    date_range_start: str = ""
    date_range_end: str = ""
    simulation_config: SimulationConfig = field(default_factory=SimulationConfig)
    distributions: list[PositionDistribution] = field(default_factory=list)
    chi2_results: list[ChiSquareResult] = field(default_factory=list)
    mc_comparisons: list[MonteCarloComparison] = field(default_factory=list)
    verdict: str = ""
    confidence: float = 0.0
    acceptance_criteria_met: bool = True


def simulate_random_abo_starts(
    jackpot_dates: list[datetime],
    date_range: tuple[datetime, datetime],
    abo_length: int,
    n_simulations: int = 10000,
    random_seed: int = 42,
) -> np.ndarray:
    """Simuliert zufaellige Abo-Starts und berechnet Position-Ratios.

    Da wir keine echten Abo-Daten haben, simulieren wir:
    1. Fuer jede Simulation: zufaelliger Abo-Start
    2. Berechne relative Position jedes Jackpots im Abo

    Args:
        jackpot_dates: Liste der Jackpot-Daten
        date_range: (start, end) des gesamten Zeitraums
        abo_length: Abo-Laenge in Tagen
        n_simulations: Anzahl Simulationen
        random_seed: Random Seed

    Returns:
        Array der mittleren Position-Ratios pro Simulation
    """
    rng = np.random.default_rng(random_seed)
    start_date, end_date = date_range
    total_days = (end_date - start_date).days

    if total_days <= 0 or not jackpot_dates:
        return np.array([0.5] * n_simulations)

    # Konvertiere Jackpot-Daten zu Day-Offsets
    jackpot_offsets = np.array([(d - start_date).days for d in jackpot_dates])

    mean_ratios = []
    for _ in range(n_simulations):
        # Zufaelliger Abo-Start (0 bis abo_length-1)
        abo_start_offset = rng.integers(0, abo_length)

        # Berechne Position jedes Jackpots im Abo
        positions = (jackpot_offsets - abo_start_offset) % abo_length
        ratios = positions / (abo_length - 1) if abo_length > 1 else np.zeros_like(positions)
        mean_ratios.append(float(np.mean(ratios)))

    return np.array(mean_ratios)


def calculate_position_distribution(
    jackpot_dates: list[datetime],
    date_range: tuple[datetime, datetime],
    abo_length: int,
    n_bins: int = N_POSITION_BINS,
) -> PositionDistribution:
    """Berechnet die Verteilung der Jackpot-Positionen.

    Nimmt einen festen Abo-Start am Anfang des Zeitraums an.

    Args:
        jackpot_dates: Liste der Jackpot-Daten
        date_range: (start, end) des Zeitraums
        abo_length: Abo-Laenge in Tagen
        n_bins: Anzahl Bins fuer Histogramm

    Returns:
        PositionDistribution Objekt
    """
    start_date, _ = date_range

    if not jackpot_dates:
        return PositionDistribution(
            abo_length=abo_length,
            n_jackpots=0,
            position_counts=[0] * n_bins,
            position_labels=_create_position_labels(abo_length, n_bins),
            mean_position_ratio=0.5,
            std_position_ratio=0.0,
        )

    # Berechne Position jedes Jackpots im Abo (0-indexed)
    positions = [(d - start_date).days % abo_length for d in jackpot_dates]
    ratios = [p / (abo_length - 1) if abo_length > 1 else 0.0 for p in positions]

    # Erstelle Histogramm
    bin_edges = np.linspace(0, abo_length, n_bins + 1)
    counts, _ = np.histogram(positions, bins=bin_edges)

    labels = _create_position_labels(abo_length, n_bins)

    return PositionDistribution(
        abo_length=abo_length,
        n_jackpots=len(jackpot_dates),
        position_counts=[int(c) for c in counts],
        position_labels=labels,
        mean_position_ratio=round(float(np.mean(ratios)), 4),
        std_position_ratio=round(float(np.std(ratios)), 4),
    )


def _create_position_labels(abo_length: int, n_bins: int) -> list[str]:
    """Erstellt Labels fuer Position-Bins."""
    bin_size = abo_length // n_bins
    labels = []
    for i in range(n_bins):
        start = i * bin_size + 1
        end = (i + 1) * bin_size if i < n_bins - 1 else abo_length
        if start == end:
            labels.append(f"Tag {start}")
        else:
            labels.append(f"Tag {start}-{end}")
    return labels


def chi_square_uniformity_test(
    distribution: PositionDistribution,
    alpha: float = 0.05,
) -> ChiSquareResult:
    """Fuehrt Chi-Quadrat Uniformitaetstest durch.

    H0: Jackpot-Positionen sind gleichverteilt ueber Abo-Periode
    H1: Jackpot-Positionen sind nicht gleichverteilt

    Args:
        distribution: PositionDistribution Objekt
        alpha: Signifikanzniveau (default 0.05)

    Returns:
        ChiSquareResult Objekt
    """
    observed = np.array(distribution.position_counts)
    n_bins = len(observed)
    total = observed.sum()

    if total < 20:
        return ChiSquareResult(
            abo_length=distribution.abo_length,
            chi2_statistic=0.0,
            p_value=1.0,
            df=n_bins - 1,
            is_uniform=True,
            interpretation=f"Zu wenige Daten fuer Chi-Quadrat Test ({total} < 20)",
        )

    # Erwartete Gleichverteilung
    expected = np.full(n_bins, total / n_bins)

    # Chi-Quadrat Test
    chi2_stat, p_value = stats.chisquare(observed, f_exp=expected)

    is_uniform = p_value > alpha

    if is_uniform:
        interpretation = (
            f"p-Wert {p_value:.4f} > {alpha}: "
            f"Keine signifikante Abweichung von Gleichverteilung. "
            f"Jackpot-Positionen erscheinen zufaellig."
        )
    else:
        interpretation = (
            f"p-Wert {p_value:.4f} <= {alpha}: "
            f"Signifikante Abweichung von Gleichverteilung! "
            f"Jackpot-Positionen folgen nicht dem erwarteten Zufallsmuster."
        )

    return ChiSquareResult(
        abo_length=distribution.abo_length,
        chi2_statistic=round(float(chi2_stat), 4),
        p_value=round(float(p_value), 6),
        df=n_bins - 1,
        is_uniform=is_uniform,
        interpretation=interpretation,
    )


def compare_to_monte_carlo(
    distribution: PositionDistribution,
    simulated_ratios: np.ndarray,
    alpha: float = 0.05,
) -> MonteCarloComparison:
    """Vergleicht beobachtete Verteilung mit Monte-Carlo Simulation.

    Args:
        distribution: Beobachtete PositionDistribution
        simulated_ratios: Array der simulierten mittleren Position-Ratios
        alpha: Signifikanzniveau

    Returns:
        MonteCarloComparison Objekt
    """
    observed_mean = distribution.mean_position_ratio
    sim_mean = float(np.mean(simulated_ratios))
    sim_std = float(np.std(simulated_ratios))

    # Z-Score
    if sim_std > 1e-10:
        z_score = (observed_mean - sim_mean) / sim_std
        # Zweiseitiger p-Wert
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    else:
        z_score = 0.0
        p_value = 1.0

    is_significant = p_value < alpha

    return MonteCarloComparison(
        abo_length=distribution.abo_length,
        observed_mean_ratio=round(observed_mean, 4),
        simulated_mean_ratio=round(sim_mean, 4),
        simulated_std_ratio=round(sim_std, 4),
        z_score=round(z_score, 4),
        p_value_mc=round(p_value, 6),
        is_significant=is_significant,
    )


def analyze_multiweek_timing(
    jackpot_dates: list[datetime],
    simulation_config: SimulationConfig | None = None,
    alpha: float = 0.05,
) -> MultiweekTimingResult:
    """Fuehrt vollstaendige HYP-014 Analyse durch.

    Args:
        jackpot_dates: Liste der Jackpot-Daten (datetime)
        simulation_config: Monte-Carlo Konfiguration (optional)
        alpha: Signifikanzniveau

    Returns:
        MultiweekTimingResult mit allen Analyseergebnissen
    """
    if simulation_config is None:
        simulation_config = SimulationConfig()

    if not jackpot_dates:
        return MultiweekTimingResult(
            analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_source="keine",
            verdict="INSUFFICIENT_DATA",
            confidence=0.0,
            acceptance_criteria_met=True,
        )

    # Sortiere Daten
    sorted_dates = sorted(jackpot_dates)
    date_range = (sorted_dates[0], sorted_dates[-1])

    result = MultiweekTimingResult(
        analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        n_jackpots=len(sorted_dates),
        date_range_start=sorted_dates[0].strftime("%d.%m.%Y"),
        date_range_end=sorted_dates[-1].strftime("%d.%m.%Y"),
        simulation_config=simulation_config,
    )

    # Analysiere fuer jede Abo-Laenge
    sig_chi2_count = 0
    sig_mc_count = 0

    for abo_length in simulation_config.abo_lengths:
        # Position-Verteilung
        dist = calculate_position_distribution(sorted_dates, date_range, abo_length)
        result.distributions.append(dist)

        # Chi-Quadrat Test
        chi2_res = chi_square_uniformity_test(dist, alpha)
        result.chi2_results.append(chi2_res)
        if not chi2_res.is_uniform:
            sig_chi2_count += 1

        # Monte-Carlo Vergleich
        sim_ratios = simulate_random_abo_starts(
            sorted_dates,
            date_range,
            abo_length,
            simulation_config.n_simulations,
            simulation_config.random_seed,
        )
        mc_comp = compare_to_monte_carlo(dist, sim_ratios, alpha)
        result.mc_comparisons.append(mc_comp)
        if mc_comp.is_significant:
            sig_mc_count += 1

    # Bestimme Gesamtergebnis
    total_tests = len(simulation_config.abo_lengths) * 2  # chi2 + MC pro Abo-Laenge
    sig_total = sig_chi2_count + sig_mc_count

    if sig_total == 0:
        result.verdict = "NICHT_BESTAETIGT"
        result.confidence = 0.95
        result.acceptance_criteria_met = True
    elif sig_total >= 3:  # Mindestens 3 von 6 Tests signifikant
        result.verdict = "BESTAETIGT"
        result.confidence = 0.80
        result.acceptance_criteria_met = False
    else:
        result.verdict = "UNKLAR"
        result.confidence = 0.50
        result.acceptance_criteria_met = True

    return result


def to_dict(result: MultiweekTimingResult) -> dict[str, Any]:
    """Konvertiert MultiweekTimingResult zu JSON-serialisierbarem Dict."""

    def to_native(val: Any) -> Any:
        """Convert numpy types to native Python types."""
        if isinstance(val, (np.bool_, np.integer)):
            return int(val) if isinstance(val, np.integer) else bool(val)
        if isinstance(val, np.floating):
            return float(val)
        return val

    def dataclass_to_dict(obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, list):
            return [dataclass_to_dict(item) for item in obj]
        if hasattr(obj, "__dataclass_fields__"):
            d = asdict(obj)
            # Recursively convert numpy types
            return {k: to_native(v) if not isinstance(v, (dict, list)) else dataclass_to_dict(v) for k, v in d.items()}
        return to_native(obj)

    return {
        "hypothesis_id": result.hypothesis_id,
        "analysis_date": result.analysis_date,
        "data_source": result.data_source,
        "n_jackpots": result.n_jackpots,
        "date_range": {
            "start": result.date_range_start,
            "end": result.date_range_end,
        },
        "simulation_config": dataclass_to_dict(result.simulation_config),
        "distributions": dataclass_to_dict(result.distributions),
        "chi2_results": dataclass_to_dict(result.chi2_results),
        "mc_comparisons": dataclass_to_dict(result.mc_comparisons),
        "verdict": result.verdict,
        "confidence": to_native(result.confidence),
        "acceptance_criteria_met": to_native(result.acceptance_criteria_met),
    }


def export_result_to_json(
    result: MultiweekTimingResult,
    output_path: str | Path,
) -> None:
    """Exportiert Analyseergebnis als JSON.

    Args:
        result: MultiweekTimingResult Objekt
        output_path: Pfad zur Ausgabedatei
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = to_dict(result)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported result to {output_path}")


def run_hyp014_analysis(
    jackpot_dates: list[datetime],
    output_path: str | Path | None = None,
    n_simulations: int = 10000,
    random_seed: int = 42,
) -> MultiweekTimingResult:
    """Convenience-Funktion fuer HYP-014 Analyse.

    Args:
        jackpot_dates: Liste der Jackpot-Daten
        output_path: Optional, Pfad zur JSON-Ausgabedatei
        n_simulations: Anzahl Monte-Carlo Simulationen
        random_seed: Random Seed fuer Reproduzierbarkeit

    Returns:
        MultiweekTimingResult
    """
    config = SimulationConfig(
        n_simulations=n_simulations,
        random_seed=random_seed,
    )

    result = analyze_multiweek_timing(jackpot_dates, config)

    if output_path:
        export_result_to_json(result, output_path)

    return result


__all__ = [
    "SimulationConfig",
    "PositionDistribution",
    "ChiSquareResult",
    "MonteCarloComparison",
    "MultiweekTimingResult",
    "ABO_LENGTHS",
    "N_POSITION_BINS",
    "simulate_random_abo_starts",
    "calculate_position_distribution",
    "chi_square_uniformity_test",
    "compare_to_monte_carlo",
    "analyze_multiweek_timing",
    "to_dict",
    "export_result_to_json",
    "run_hyp014_analysis",
]
