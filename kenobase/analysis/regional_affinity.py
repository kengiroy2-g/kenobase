"""Analyse regionale Zahlen-Affinitaet (Bundesland) vs. globale Baseline."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from kenobase.core.regions import normalize_region

try:
    from kenobase.core.data_loader import DrawResult
except Exception:  # pragma: no cover - used in type checking
    DrawResult = None  # type: ignore


@dataclass
class RegionalNumberStat:
    """Statistik fuer eine Zahl innerhalb einer Region."""

    number: int
    count: int
    draws: int
    relative_frequency: float
    global_relative_frequency: float
    lift: float
    z_score: float
    p_value: float
    is_significant: bool


@dataclass
class RegionalAffinityResult:
    """Ergebnis der regionalen Affinitaet fuer eine Region."""

    region: str
    n_draws: int
    numbers_per_draw: int
    stats: list[RegionalNumberStat]


@dataclass
class RegionalAffinityAnalysis:
    """Gesamtergebnis der regionalen Affinitaetsanalyse."""

    generated_at: datetime
    game: str
    number_range: tuple[int, int]
    numbers_per_draw: int
    n_draws_total: int
    global_relative_frequency: dict[int, float]
    regions: list[RegionalAffinityResult]
    skipped_regions: list[str]
    warnings: list[str]
    parameters: dict

    def to_dict(self) -> dict:
        """Serialisiert das Ergebnis fuer JSON-Ausgabe."""
        return {
            "analysis": "regional_affinity",
            "generated_at": self.generated_at.isoformat(),
            "game": self.game,
            "number_range": list(self.number_range),
            "numbers_per_draw": self.numbers_per_draw,
            "n_draws_total": self.n_draws_total,
            "parameters": self.parameters,
            "global_relative_frequency": {
                str(k): v for k, v in self.global_relative_frequency.items()
            },
            "regions": [
                {
                    "region": r.region,
                    "n_draws": r.n_draws,
                    "numbers_per_draw": r.numbers_per_draw,
                    "stats": [
                        {
                            "number": s.number,
                            "count": s.count,
                            "relative_frequency": s.relative_frequency,
                            "global_relative_frequency": s.global_relative_frequency,
                            "lift": s.lift,
                            "z_score": s.z_score,
                            "p_value": s.p_value,
                            "is_significant": s.is_significant,
                        }
                        for s in r.stats
                    ],
                }
                for r in self.regions
            ],
            "skipped_regions": self.skipped_regions,
            "warnings": self.warnings,
        }


def _get_region(draw: DrawResult) -> Optional[str]:
    """Extrahiert Region aus DrawResult-Metadaten."""
    for key in ("region", "bundesland", "state"):
        raw = draw.metadata.get(key)
        if raw:
            region = normalize_region(str(raw))
            if region:
                return region
    return None


def _calculate_p_value_from_z(z_score: float) -> float:
    """Berechnet zweiseitige p-Value aus z-Score."""
    return math.erfc(abs(z_score) / math.sqrt(2))


def analyze_regional_affinity(
    draws: list[DrawResult],
    *,
    number_range: tuple[int, int] = (1, 70),
    numbers_per_draw: Optional[int] = None,
    min_draws_per_region: int = 30,
    smoothing_alpha: float = 1.0,
    z_threshold: float = 2.0,
    game: str = "keno",
) -> RegionalAffinityAnalysis:
    """Berechnet regionale Zahlen-Affinitaeten je Bundesland.

    Args:
        draws: Liste von Ziehungen mit Region in metadata.
        number_range: Zahlenbereich (inklusive).
        numbers_per_draw: Override fuer Zahlen pro Ziehung (sonst aus Daten).
        min_draws_per_region: Mindestanzahl Ziehungen pro Region.
        smoothing_alpha: Laplace-Smoothing fuer seltene Regionen.
        z_threshold: Schwelle fuer Signifikanz (zweiseitig).
        game: Spielname fuer Metadaten.

    Returns:
        RegionalAffinityAnalysis mit Ergebnissen und Warnungen.
    """
    warnings: list[str] = []
    if not draws:
        warnings.append("No draws provided")
        return RegionalAffinityAnalysis(
            generated_at=datetime.now(),
            game=game,
            number_range=number_range,
            numbers_per_draw=numbers_per_draw or 0,
            n_draws_total=0,
            global_relative_frequency={},
            regions=[],
            skipped_regions=[],
            warnings=warnings,
            parameters={
                "min_draws_per_region": min_draws_per_region,
                "smoothing_alpha": smoothing_alpha,
                "z_threshold": z_threshold,
            },
        )

    inferred_numbers_per_draw = numbers_per_draw or len(draws[0].numbers)
    range_size = number_range[1] - number_range[0] + 1

    # Globale Frequenzen
    global_counter: Counter[int] = Counter()
    for draw in draws:
        global_counter.update(draw.numbers)
    global_total_draws = len(draws)
    global_total_picks = max(global_total_draws * inferred_numbers_per_draw, 1)

    global_relative = {
        n: (global_counter.get(n, 0) + smoothing_alpha)
        / (global_total_picks + smoothing_alpha * range_size)
        for n in range(number_range[0], number_range[1] + 1)
    }

    # Regionale Aufteilung
    region_draws: dict[str, list[DrawResult]] = defaultdict(list)
    for draw in draws:
        region = _get_region(draw)
        if region:
            region_draws[region].append(draw)

    if not region_draws:
        warnings.append("No region metadata found; skipping regional analysis")
        return RegionalAffinityAnalysis(
            generated_at=datetime.now(),
            game=game,
            number_range=number_range,
            numbers_per_draw=inferred_numbers_per_draw,
            n_draws_total=len(draws),
            global_relative_frequency=global_relative,
            regions=[],
            skipped_regions=[],
            warnings=warnings,
            parameters={
                "min_draws_per_region": min_draws_per_region,
                "smoothing_alpha": smoothing_alpha,
                "z_threshold": z_threshold,
            },
        )

    regions_results: list[RegionalAffinityResult] = []
    skipped_regions: list[str] = []

    for region, r_draws in region_draws.items():
        if len(r_draws) < min_draws_per_region:
            skipped_regions.append(region)
            continue

        region_counter: Counter[int] = Counter()
        for draw in r_draws:
            region_counter.update(draw.numbers)

        regional_total_picks = len(r_draws) * inferred_numbers_per_draw
        stats: list[RegionalNumberStat] = []

        for number in range(number_range[0], number_range[1] + 1):
            count = region_counter.get(number, 0)
            rel_freq = (count + smoothing_alpha) / (
                regional_total_picks + smoothing_alpha * range_size
            )
            global_freq = global_counter.get(number, 0) / global_total_picks
            lift = rel_freq / max(global_relative.get(number, 1e-12), 1e-12)

            expected = global_freq * regional_total_picks
            variance = expected * (1 - global_freq)
            if variance <= 0:
                z_score = 0.0
                p_value = 1.0
            else:
                z_score = (count - expected) / math.sqrt(variance)
                p_value = _calculate_p_value_from_z(z_score)

            stats.append(
                RegionalNumberStat(
                    number=number,
                    count=count,
                    draws=len(r_draws),
                    relative_frequency=rel_freq,
                    global_relative_frequency=global_relative.get(number, 0.0),
                    lift=lift,
                    z_score=z_score,
                    p_value=p_value,
                    is_significant=abs(z_score) >= z_threshold,
                )
            )

        regions_results.append(
            RegionalAffinityResult(
                region=region,
                n_draws=len(r_draws),
                numbers_per_draw=inferred_numbers_per_draw,
                stats=sorted(stats, key=lambda s: s.lift, reverse=True),
            )
        )

    if skipped_regions:
        warnings.append(
            f"Skipped regions with insufficient draws (<{min_draws_per_region}): "
            + ", ".join(sorted(skipped_regions))
        )

    return RegionalAffinityAnalysis(
        generated_at=datetime.now(),
        game=game,
        number_range=number_range,
        numbers_per_draw=inferred_numbers_per_draw,
        n_draws_total=len(draws),
        global_relative_frequency=global_relative,
        regions=regions_results,
        skipped_regions=skipped_regions,
        warnings=warnings,
        parameters={
            "min_draws_per_region": min_draws_per_region,
            "smoothing_alpha": smoothing_alpha,
            "z_threshold": z_threshold,
        },
    )


def get_top_affinities(
    analysis: RegionalAffinityAnalysis,
    *,
    region: Optional[str] = None,
    n: int = 5,
    significance_only: bool = False,
) -> list[RegionalNumberStat]:
    """Extrahiert Top-Lifts fuer eine Region oder global.

    Args:
        analysis: Ergebnis der Affinitaetsanalyse.
        region: Region-Name (None = erste Region).
        n: Anzahl Rueckgabewerte.
        significance_only: Nur signifikante Ergebnisse zurueckgeben.
    """
    if not analysis.regions:
        return []

    target_region = region or analysis.regions[0].region
    region_result = next((r for r in analysis.regions if r.region == target_region), None)
    if not region_result:
        return []

    stats = region_result.stats
    if significance_only:
        stats = [s for s in stats if s.is_significant]
    return stats[:n]


@dataclass
class RegionalDistributionResult:
    """Result of Chi-Quadrat test for winner distribution across regions."""

    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int
    is_significant: bool  # p < 0.05
    observed: dict[str, int]  # region -> winner count
    expected: dict[str, float]  # region -> expected count (by population)
    n_total: int
    deviations: dict[str, float]  # region -> (observed - expected) / expected

    def to_dict(self) -> dict:
        """Serialize for JSON output."""
        return {
            "chi2_statistic": self.chi2_statistic,
            "p_value": self.p_value,
            "degrees_of_freedom": self.degrees_of_freedom,
            "is_significant": self.is_significant,
            "n_total": self.n_total,
            "observed": self.observed,
            "expected": {k: round(v, 2) for k, v in self.expected.items()},
            "deviations": {k: round(v, 4) for k, v in self.deviations.items()},
        }


# German Bundesland population shares (2023, based on ~84 Mio total)
BUNDESLAND_POPULATION_SHARE = {
    "baden-wuerttemberg": 0.133,
    "bayern": 0.159,
    "berlin": 0.044,
    "brandenburg": 0.030,
    "bremen": 0.008,
    "hamburg": 0.022,
    "hessen": 0.076,
    "mecklenburg-vorpommern": 0.019,
    "niedersachsen": 0.096,
    "nordrhein-westfalen": 0.217,
    "rheinland-pfalz": 0.050,
    "saarland": 0.012,
    "sachsen": 0.049,
    "sachsen-anhalt": 0.026,
    "schleswig-holstein": 0.035,
    "thueringen": 0.025,
}


def calculate_distribution_chi2(
    draws: list[DrawResult],
    *,
    population_shares: Optional[dict[str, float]] = None,
    min_expected: float = 5.0,
) -> RegionalDistributionResult:
    """Calculate Chi-Quadrat test for regional winner distribution.

    Tests hypothesis: Winner distribution matches population distribution.
    HYP-003: If distribution deviates significantly, regional factors may exist.

    Args:
        draws: List of DrawResult objects with bundesland in metadata.
        population_shares: Expected shares per region (default: German population).
        min_expected: Minimum expected count per region (regions below are pooled).

    Returns:
        RegionalDistributionResult with Chi2 test results.
    """
    if population_shares is None:
        population_shares = BUNDESLAND_POPULATION_SHARE

    # Count winners per region
    observed: Counter[str] = Counter()
    for draw in draws:
        region = _get_region(draw)
        if region:
            observed[region] += 1

    n_total = sum(observed.values())

    if n_total == 0:
        return RegionalDistributionResult(
            chi2_statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
            observed={},
            expected={},
            n_total=0,
            deviations={},
        )

    # Calculate expected counts based on population shares
    # Only include regions that are in both observed and population_shares
    regions_to_test = [
        r for r in observed.keys() if r in population_shares
    ]

    if not regions_to_test:
        return RegionalDistributionResult(
            chi2_statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
            observed=dict(observed),
            expected={},
            n_total=n_total,
            deviations={},
        )

    # Renormalize population shares for observed regions
    share_sum = sum(population_shares.get(r, 0) for r in regions_to_test)
    if share_sum == 0:
        share_sum = 1.0

    normalized_shares = {
        r: population_shares.get(r, 0) / share_sum for r in regions_to_test
    }

    expected: dict[str, float] = {
        r: normalized_shares[r] * n_total for r in regions_to_test
    }

    # Pool regions with expected < min_expected into "other"
    regions_below_threshold = [r for r, e in expected.items() if e < min_expected]
    if regions_below_threshold:
        other_expected = sum(expected[r] for r in regions_below_threshold)
        other_observed = sum(observed[r] for r in regions_below_threshold)

        for r in regions_below_threshold:
            del expected[r]

        if other_expected >= min_expected:
            expected["other"] = other_expected
            observed["other"] = other_observed

    # Ensure we have degrees of freedom
    n_categories = len(expected)
    if n_categories < 2:
        return RegionalDistributionResult(
            chi2_statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
            observed=dict(observed),
            expected=expected,
            n_total=n_total,
            deviations={},
        )

    # Calculate Chi-Quadrat statistic
    chi2 = 0.0
    deviations: dict[str, float] = {}

    for region in expected:
        obs = observed.get(region, 0)
        exp = expected[region]
        if exp > 0:
            chi2 += ((obs - exp) ** 2) / exp
            deviations[region] = (obs - exp) / exp

    degrees_of_freedom = n_categories - 1

    # Calculate p-value using chi2 CDF approximation
    # For small df, use Wilson-Hilferty approximation
    p_value = _chi2_p_value(chi2, degrees_of_freedom)

    return RegionalDistributionResult(
        chi2_statistic=round(chi2, 4),
        p_value=round(p_value, 6),
        degrees_of_freedom=degrees_of_freedom,
        is_significant=p_value < 0.05,
        observed={r: observed.get(r, 0) for r in expected},
        expected=expected,
        n_total=n_total,
        deviations=deviations,
    )


def _chi2_p_value(chi2: float, df: int) -> float:
    """Approximate p-value for chi-squared distribution.

    Uses incomplete gamma function approximation.
    For df >= 1 and chi2 >= 0.
    """
    if df <= 0 or chi2 < 0:
        return 1.0

    if chi2 == 0:
        return 1.0

    # Use regularized incomplete gamma function
    # P(X > chi2) = 1 - gamma_inc(df/2, chi2/2)
    # Approximation using continued fraction for large values

    k = df / 2.0
    x = chi2 / 2.0

    # For small x, use series expansion
    if x < k + 1:
        return 1.0 - _gamma_inc_series(k, x)
    else:
        # For large x, use continued fraction
        return _gamma_inc_cf(k, x)


def _gamma_inc_series(a: float, x: float, max_iter: int = 100, eps: float = 1e-10) -> float:
    """Regularized incomplete gamma function via series expansion."""
    if x == 0:
        return 0.0

    # log(x^a * e^-x / Gamma(a))
    log_term = a * math.log(x) - x - math.lgamma(a)
    term = 1.0 / a
    sum_val = term

    for n in range(1, max_iter):
        term *= x / (a + n)
        sum_val += term
        if abs(term) < eps * abs(sum_val):
            break

    return sum_val * math.exp(log_term)


def _gamma_inc_cf(a: float, x: float, max_iter: int = 100, eps: float = 1e-10) -> float:
    """Regularized incomplete gamma function (upper) via continued fraction."""
    # Q(a,x) = Gamma(a,x) / Gamma(a)
    log_term = a * math.log(x) - x - math.lgamma(a)

    # Lentz's algorithm for continued fraction
    b = x + 1 - a
    c = 1e30
    d = 1.0 / b
    h = d

    for i in range(1, max_iter):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            break

    return h * math.exp(log_term)


__all__ = [
    "RegionalAffinityAnalysis",
    "RegionalAffinityResult",
    "RegionalNumberStat",
    "RegionalDistributionResult",
    "BUNDESLAND_POPULATION_SHARE",
    "analyze_regional_affinity",
    "get_top_affinities",
    "calculate_distribution_chi2",
]
