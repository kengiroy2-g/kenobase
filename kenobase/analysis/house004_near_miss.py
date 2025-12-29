"""HOUSE-004: Near-Miss Analyse (Jackpot-Kontext vs. Normal).

Ziel
----
Untersucht, ob sich das Verhältnis von Near-Miss Gewinnern (k-1 Treffer) zu
Jackpot-Gewinnern (k Treffer) zwischen zwei Kontexten unterscheidet.

Wichtiger Punkt: Je nach Kontext-Definition entstehen starke Selektions-/Trunkierungs-
effekte. Daher enthält das Modul optional ein einfaches Erklärmodell:

- **Poisson-Gamma (shared intensity)** für (Near-Miss, Jackpot) pro Keno-Typ, das
  heterogene Beteiligung (Ticket-Volumen) über einen latenten Tagesfaktor abbildet.

Kontext-Definitionen
--------------------
`context="self"` (Default):
    "Jackpot-Tage" sind Tage, an denen es mindestens einen k/k Gewinner für diesen
    Keno-Typ gibt. Das ist für seltene Jackpots stark zero-inflated (viele 0‑Tage).

`context="gk1"`:
    "Jackpot-Tage" sind Tage, an denen es mindestens einen GK1 Winner gibt
    (hier pragmatisch: 9/9 oder 10/10 Gewinner).

Beide Kontexte werden unterstützt, weil sie in Diskussionen oft vermischt werden.
"""

from __future__ import annotations

import math
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from kenobase.analysis.distribution import load_gq_data


@dataclass
class RatioStats:
    """Aggregierte Ratio-Statistik für eine Gruppe von Tagen."""

    days: int
    near_winners_total: int
    jackpot_winners_total: int
    ratio: Optional[float]


@dataclass
class ModelFit:
    """Fit/Simulationsergebnis des Erklärmodells (Poisson-Gamma)."""

    gamma_shape_r: Optional[float]
    mu_jackpot_per_day: float
    mu_near_per_day: float
    p0_jackpot: float
    expected_ratio_on_jackpot_days: Optional[float]
    simulated_p_value_two_sided: Optional[float]


@dataclass
class House004TypeResult:
    keno_type: int
    date_min: str
    date_max: str
    context: str
    overall: RatioStats
    in_context: RatioStats
    out_context: RatioStats
    diff_in_minus_out: Optional[float]
    model: Optional[ModelFit] = None


def _safe_ratio(numer: int, denom: int) -> Optional[float]:
    if denom <= 0:
        return None
    return float(numer) / float(denom)


def _solve_nb_shape_from_p0(mu: float, p0: float) -> Optional[float]:
    """Solve r from p0 = (r/(r+mu))^r for a Poisson-Gamma/NB mixture.

    Returns None if no solution is needed/possible (e.g. p0 <= exp(-mu)).
    """
    if mu <= 0:
        return None

    # For pure Poisson: p0 = exp(-mu). If observed p0 is <= that, heterogeneity not required.
    if p0 <= math.exp(-mu) + 1e-12:
        return None

    def f(r: float) -> float:
        return (r / (r + mu)) ** r - p0

    lo, hi = 1e-6, 1e6
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None

    for _ in range(80):
        mid = (lo + hi) / 2
        fmid = f(mid)
        if abs(fmid) < 1e-12:
            return mid
        if flo * fmid > 0:
            lo, flo = mid, fmid
        else:
            hi = mid
    return (lo + hi) / 2


def _fit_poisson_gamma_and_simulate(
    *,
    jackpot: np.ndarray,
    near: np.ndarray,
    n_sim: int,
    seed: int,
) -> ModelFit:
    """Fit a shared-intensity Poisson-Gamma model and simulate the ratio gap.

    Assumption:
      S ~ Gamma(r, scale=1)
      J | S ~ Poisson(S * a_j)
      N | S ~ Poisson(S * a_n)
    """
    n_days = int(jackpot.shape[0])
    mu_j = float(np.mean(jackpot))
    mu_n = float(np.mean(near))
    p0 = float(np.mean(jackpot == 0))

    r = _solve_nb_shape_from_p0(mu_j, p0)

    obs_overall = _safe_ratio(int(near.sum()), int(jackpot.sum()))
    mask = jackpot > 0
    obs_on = _safe_ratio(int(near[mask].sum()), int(jackpot[mask].sum()))

    if r is None or n_sim <= 0 or obs_overall is None or obs_on is None:
        expected = None
        p_value = None
        if r is not None:
            # still provide a point expectation via conditional mean identity
            expected = mu_n / (mu_j / (1 - p0)) if (1 - p0) > 0 and mu_j > 0 else None
        return ModelFit(
            gamma_shape_r=r,
            mu_jackpot_per_day=mu_j,
            mu_near_per_day=mu_n,
            p0_jackpot=p0,
            expected_ratio_on_jackpot_days=expected,
            simulated_p_value_two_sided=p_value,
        )

    # Rates given S ~ Gamma(r, 1): E[S]=r
    a_j = mu_j / r
    a_n = mu_n / r

    rng = np.random.default_rng(seed)

    # Vectorized simulation: (n_sim, n_days)
    # Note: Gamma(shape=r) allows non-integer r.
    s = rng.gamma(shape=r, scale=1.0, size=(n_sim, n_days))
    j = rng.poisson(lam=s * a_j)
    n = rng.poisson(lam=s * a_n)

    j_sum = j.sum(axis=1)
    n_sum = n.sum(axis=1)

    valid_total = j_sum > 0
    ratio_total = np.full(n_sim, np.nan, dtype=float)
    ratio_total[valid_total] = n_sum[valid_total] / j_sum[valid_total]

    # Jackpot-days ratio
    j_pos = j > 0
    j_on_sum = (j * j_pos).sum(axis=1)
    n_on_sum = (n * j_pos).sum(axis=1)

    valid_on = j_on_sum > 0
    ratio_on = np.full(n_sim, np.nan, dtype=float)
    ratio_on[valid_on] = n_on_sum[valid_on] / j_on_sum[valid_on]

    valid = np.isfinite(ratio_total) & np.isfinite(ratio_on)
    if not np.any(valid):
        return ModelFit(
            gamma_shape_r=r,
            mu_jackpot_per_day=mu_j,
            mu_near_per_day=mu_n,
            p0_jackpot=p0,
            expected_ratio_on_jackpot_days=float(np.nan),
            simulated_p_value_two_sided=None,
        )

    diff_sim = ratio_on[valid] - ratio_total[valid]
    diff_obs = (obs_on - obs_overall)

    # Two-sided Monte Carlo p-value for the "ratio gap"
    p_value = (np.sum(np.abs(diff_sim) >= abs(diff_obs)) + 1) / (diff_sim.size + 1)

    expected = float(np.nanmean(ratio_on[valid]))

    return ModelFit(
        gamma_shape_r=float(r),
        mu_jackpot_per_day=mu_j,
        mu_near_per_day=mu_n,
        p0_jackpot=p0,
        expected_ratio_on_jackpot_days=expected,
        simulated_p_value_two_sided=float(p_value),
    )


def analyze_house004(
    df: pd.DataFrame,
    *,
    keno_type: int,
    context: str = "self",
    n_sim: int = 20000,
    seed: int = 42,
) -> House004TypeResult:
    """Run HOUSE-004 for a single keno_type."""
    if context not in ("self", "gk1"):
        raise ValueError(f"Unsupported context: {context}")

    data = df.copy()
    data["Datum"] = pd.to_datetime(data["Datum"])

    date_min = data["Datum"].min()
    date_max = data["Datum"].max()

    pivot = data.pivot_table(
        index="Datum",
        columns=["Keno-Typ", "Anzahl richtiger Zahlen"],
        values="Anzahl der Gewinner",
        aggfunc="sum",
        fill_value=0,
    )

    def series(k: int, m: int) -> pd.Series:
        key = (k, m)
        if key in pivot.columns:
            return pivot[key].astype(int)
        return pd.Series(0, index=pivot.index, dtype=int)

    jackpot = series(keno_type, keno_type).to_numpy(dtype=int)
    near = series(keno_type, keno_type - 1).to_numpy(dtype=int)

    if context == "self":
        in_mask = jackpot > 0
    else:
        # GK1 day: at least one 9/9 or 10/10 winner
        gk1 = (series(9, 9) > 0) | (series(10, 10) > 0)
        in_mask = gk1.to_numpy(dtype=bool)

    out_mask = ~in_mask

    overall = RatioStats(
        days=int(jackpot.shape[0]),
        near_winners_total=int(near.sum()),
        jackpot_winners_total=int(jackpot.sum()),
        ratio=_safe_ratio(int(near.sum()), int(jackpot.sum())),
    )

    in_context = RatioStats(
        days=int(in_mask.sum()),
        near_winners_total=int(near[in_mask].sum()),
        jackpot_winners_total=int(jackpot[in_mask].sum()),
        ratio=_safe_ratio(int(near[in_mask].sum()), int(jackpot[in_mask].sum())),
    )

    out_context = RatioStats(
        days=int(out_mask.sum()),
        near_winners_total=int(near[out_mask].sum()),
        jackpot_winners_total=int(jackpot[out_mask].sum()),
        ratio=_safe_ratio(int(near[out_mask].sum()), int(jackpot[out_mask].sum())),
    )

    diff = None
    if in_context.ratio is not None and out_context.ratio is not None:
        diff = float(in_context.ratio - out_context.ratio)

    model: Optional[ModelFit] = None
    if context == "self":
        model = _fit_poisson_gamma_and_simulate(
            jackpot=jackpot.astype(int),
            near=near.astype(int),
            n_sim=n_sim,
            seed=seed,
        )

    return House004TypeResult(
        keno_type=int(keno_type),
        date_min=pd.to_datetime(date_min).date().isoformat(),
        date_max=pd.to_datetime(date_max).date().isoformat(),
        context=context,
        overall=overall,
        in_context=in_context,
        out_context=out_context,
        diff_in_minus_out=diff,
        model=model,
    )


def run_house004_from_file(
    gq_file: str | Path,
    *,
    context: str = "self",
    keno_types: Optional[list[int]] = None,
    n_sim: int = 20000,
    seed: int = 42,
    output_json: Optional[str | Path] = None,
) -> list[House004TypeResult]:
    """Load a GQ file and run HOUSE-004 for the selected types."""
    gq_file = Path(gq_file)
    df = load_gq_data(str(gq_file))

    types = keno_types or sorted(int(x) for x in df["Keno-Typ"].dropna().unique().tolist())
    results = [
        analyze_house004(df, keno_type=k, context=context, n_sim=n_sim, seed=seed) for k in types
    ]

    if output_json:
        payload = {
            "analysis": "HOUSE-004",
            "context": context,
            "gq_file": str(gq_file),
            "generated_at": datetime.now().isoformat(),
            "results": [
                {
                    **asdict(r),
                    "model": asdict(r.model) if r.model else None,
                }
                for r in results
            ],
        }
        output_json = Path(output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return results


__all__ = [
    "House004TypeResult",
    "ModelFit",
    "RatioStats",
    "analyze_house004",
    "run_house004_from_file",
]
