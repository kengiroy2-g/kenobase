#!/usr/bin/env python3
"""HYP_013: Overlap-Birthday-Anteil nach Phase.

Berechnet pro Ziehung:
- overlap_count = |numbers_t ∩ numbers_{t-1}| (Erwartung 20*20/70 = 5.714)
- birthday_ratio = Anteil der Geburtstagszahlen (1-31) im Overlap (Erwartung 31/70)

Phasen-Schema gemaess classify_cycle_phase:
- PRE_JACKPOT: 7 Tage vor Jackpot
- POST_JACKPOT: 1-7 Tage nach Jackpot
- COOLDOWN: 8-30 Tage nach Jackpot
- NORMAL: sonst

Output:
- JSON mit Statistiken pro Phase, z-Tests gg. Erwartung, KW/MW Tests mit Bonferroni + BH
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

BIRTHDAY_SET = set(range(1, 32))
PHASES = ["PRE_JACKPOT", "POST_JACKPOT", "COOLDOWN", "NORMAL"]
EXPECTED_OVERLAP = 20 * 20 / 70  # 5.714285...
EXPECTED_BIRTHDAY_RATIO = 31 / 70  # 0.442857...
ALPHA = 0.05


@dataclass
class PhaseStats:
    n: int
    mean: Optional[float]
    std: Optional[float]
    z: Optional[float]
    p: Optional[float]
    verification: str


def classify_cycle_phase(
    date: pd.Timestamp,
    jackpot_dates: list[pd.Timestamp],
    cooldown_days: int = 30,
    pre_jackpot_days: int = 7,
) -> str:
    """Map a date to a phase relative to jackpot dates."""
    for jp_date in jackpot_dates:
        days_diff = (date.normalize() - jp_date).days

        if 1 <= days_diff <= 7:
            return "POST_JACKPOT"
        if 8 <= days_diff <= cooldown_days:
            return "COOLDOWN"
        if -pre_jackpot_days <= days_diff <= -1:
            return "PRE_JACKPOT"
    return "NORMAL"


def load_draws(draw_path: Path) -> pd.DataFrame:
    """Load draw data and attach numbers_set."""
    df = pd.read_csv(draw_path, sep=";", encoding="utf-8", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Datum"]).sort_values("Datum").reset_index(drop=True)

    number_cols = [col for col in df.columns if col.startswith("Keno_Z")]
    df["numbers_set"] = df[number_cols].apply(
        lambda row: set(int(x) for x in row.dropna().astype(int).tolist()),
        axis=1,
    )
    return df


def load_jackpot_dates(timeline_path: Path, draws: pd.DataFrame) -> tuple[list[pd.Timestamp], str]:
    """Load jackpot dates from timeline file, fallback to GK1 column."""
    jackpot_dates: list[pd.Timestamp] = []
    source = "none"

    if timeline_path.exists():
        timeline = pd.read_csv(timeline_path)
        if "datum" in timeline.columns and "keno_jackpot" in timeline.columns:
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates.extend(jackpots["datum"].dt.normalize().tolist())
            source = "timeline"

    if not jackpot_dates:
        for gk_col in ["GK1", "Gewinnklasse_1"]:
            if gk_col in draws.columns:
                hits = draws[draws[gk_col].fillna(0) > 0]
                jackpot_dates.extend(hits["Datum"].dt.normalize().tolist())
                source = f"draws_{gk_col}"
                break

    jackpot_dates = sorted(set(jackpot_dates))
    return jackpot_dates, source


def compute_overlap_features(
    draws: pd.DataFrame, jackpot_dates: list[pd.Timestamp]
) -> list[dict]:
    """Compute overlap_count and birthday_ratio per draw."""
    records: list[dict] = []
    previous_set: Optional[set[int]] = None

    for _, row in draws.iterrows():
        draw_date: pd.Timestamp = row["Datum"]
        phase = classify_cycle_phase(draw_date, jackpot_dates)

        if previous_set is None:
            records.append(
                {
                    "date": str(draw_date.date()),
                    "phase": phase,
                    "overlap_count": None,
                    "birthday_ratio": None,
                }
            )
            previous_set = row["numbers_set"]
            continue

        current_set = row["numbers_set"]
        overlap = previous_set & current_set
        overlap_count = len(overlap)
        birthday_hits = sum(1 for n in overlap if n in BIRTHDAY_SET)
        birthday_ratio = birthday_hits / overlap_count if overlap_count > 0 else None

        records.append(
            {
                "date": str(draw_date.date()),
                "phase": phase,
                "overlap_count": overlap_count,
                "birthday_ratio": birthday_ratio,
            }
        )
        previous_set = current_set

    return records


def summarize_metric(values: list[float], expected: float) -> PhaseStats:
    if not values:
        return PhaseStats(0, None, None, None, None, "UNVERIFIED")

    n = len(values)
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0
    verification = "OK" if n >= 50 else "UNVERIFIED"

    if std == 0 or n == 0:
        return PhaseStats(n, mean, std, None, None, verification)

    se = std / math.sqrt(n)
    if se == 0:
        return PhaseStats(n, mean, std, None, None, verification)

    z = (mean - expected) / se
    p = float(2 * stats.norm.sf(abs(z)))
    return PhaseStats(n, mean, std, float(z), p, verification)


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg FDR correction."""
    m = len(p_values)
    if m == 0:
        return []
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    bh = np.empty(m)
    for rank, p in enumerate(sorted_p, start=1):
        bh[rank - 1] = min(p * m / rank, 1.0)
    # Ensure monotonicity
    for i in range(m - 2, -1, -1):
        bh[i] = min(bh[i], bh[i + 1])
    corrected = np.empty(m)
    corrected[sorted_indices] = bh
    return corrected.tolist()


def collect_phase_stats(records: list[dict]) -> tuple[dict, dict, dict]:
    phase_results: dict[str, dict] = {}
    overlap_groups: dict[str, list[float]] = {p: [] for p in PHASES}
    birthday_groups: dict[str, list[float]] = {p: [] for p in PHASES}

    for rec in records:
        phase = rec["phase"]
        overlap_val = rec["overlap_count"]
        bday_val = rec["birthday_ratio"]
        if overlap_val is not None:
            overlap_groups[phase].append(overlap_val)
        if bday_val is not None:
            birthday_groups[phase].append(bday_val)

    # Per-phase stats
    for phase in PHASES:
        overlap_stats = summarize_metric(overlap_groups[phase], EXPECTED_OVERLAP)
        bday_stats = summarize_metric(birthday_groups[phase], EXPECTED_BIRTHDAY_RATIO)
        phase_results[phase] = {
            "overlap": overlap_stats.__dict__,
            "birthday_ratio": bday_stats.__dict__,
        }

    # Multiple-testing corrections for per-phase expectation tests
    overlap_pvals = [
        phase_results[p]["overlap"]["p"]
        for p in PHASES
        if phase_results[p]["overlap"]["p"] is not None
    ]
    birthday_pvals = [
        phase_results[p]["birthday_ratio"]["p"]
        for p in PHASES
        if phase_results[p]["birthday_ratio"]["p"] is not None
    ]

    def apply_corrections(metric_key: str, p_list: list[float]) -> None:
        if not p_list:
            return
        bonf = [min(p * len(p_list), 1.0) for p in p_list]
        bh = benjamini_hochberg(p_list)
        idx = 0
        for phase in PHASES:
            p_val = phase_results[phase][metric_key]["p"]
            if p_val is None:
                continue
            phase_results[phase][metric_key]["p_bonferroni"] = bonf[idx]
            phase_results[phase][metric_key]["p_bh"] = bh[idx]
            phase_results[phase][metric_key]["significant"] = (
                bonf[idx] < ALPHA or bh[idx] < ALPHA
            )
            idx += 1

    apply_corrections("overlap", overlap_pvals)
    apply_corrections("birthday_ratio", birthday_pvals)

    # Global tests
    global_tests = {}
    overlap_data = [vals for vals in overlap_groups.values() if len(vals) > 1]
    birthday_data = [vals for vals in birthday_groups.values() if len(vals) > 1]
    if len(overlap_data) >= 2:
        kw_stat, kw_p = stats.kruskal(*overlap_data)
        global_tests["kruskal_overlap"] = {"stat": float(kw_stat), "p": float(kw_p)}
    if len(birthday_data) >= 2:
        kw_stat, kw_p = stats.kruskal(*birthday_data)
        global_tests["kruskal_birthday_ratio"] = {
            "stat": float(kw_stat),
            "p": float(kw_p),
        }

    pairwise_tests = {"overlap": [], "birthday_ratio": []}
    for metric, groups in [("overlap", overlap_groups), ("birthday_ratio", birthday_groups)]:
        comparisons = []
        for i, phase_a in enumerate(PHASES):
            for phase_b in PHASES[i + 1 :]:
                a_vals = groups[phase_a]
                b_vals = groups[phase_b]
                if len(a_vals) < 2 or len(b_vals) < 2:
                    continue
                stat, p_val = stats.mannwhitneyu(a_vals, b_vals, alternative="two-sided")
                comparisons.append(
                    {
                        "comparison": f"{phase_a} vs {phase_b}",
                        "n_a": len(a_vals),
                        "n_b": len(b_vals),
                        "u_stat": float(stat),
                        "p": float(p_val),
                    }
                )
        if comparisons:
            pvals = [c["p"] for c in comparisons]
            bonf = [min(p * len(pvals), 1.0) for p in pvals]
            bh = benjamini_hochberg(pvals)
            for idx, comp in enumerate(comparisons):
                comp["p_bonferroni"] = bonf[idx]
                comp["p_bh"] = bh[idx]
                comp["significant"] = bonf[idx] < ALPHA or bh[idx] < ALPHA
        pairwise_tests[metric] = comparisons

    return phase_results, global_tests, pairwise_tests


def hypothesis_decision(phase_results: dict, global_tests: dict, pairwise_tests: dict) -> dict:
    """Derive support/reject flag based on significance after corrections."""
    significant_phase = any(
        (
            phase_results[p][metric].get("significant")
            for p in PHASES
            for metric in ["overlap", "birthday_ratio"]
        )
    )
    significant_global = any(
        v.get("p") is not None and v["p"] < ALPHA for v in global_tests.values()
    )
    significant_pairwise = any(
        comp.get("significant") for tests in pairwise_tests.values() for comp in tests
    )

    support = significant_phase or significant_global or significant_pairwise
    reason = "Signifikante Abweichung nach Korrektur gefunden" if support else "Keine signifikanten Abweichungen nach Korrektur"
    return {"hypothesis": "HYP_013", "support": support, "reason": reason}


def save_json(output_path: Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Test HYP_013: Overlap-Birthday-Anteil nach Phase")
    parser.add_argument("--draws", type=Path, default=Path("data/raw/keno/KENO_ab_2022_bereinigt.csv"))
    parser.add_argument("--jackpots", type=Path, default=Path("data/processed/ecosystem/timeline_2025.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/hyp013_overlap_birthday_phase.json"))
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md"),
        help="Optional Markdown summary output",
    )
    args = parser.parse_args()

    draws = load_draws(args.draws)
    jackpot_dates, jackpot_source = load_jackpot_dates(args.jackpots, draws)
    records = compute_overlap_features(draws, jackpot_dates)
    phase_results, global_tests, pairwise_tests = collect_phase_stats(records)

    overall_overlap = [r["overlap_count"] for r in records if r["overlap_count"] is not None]
    overall_birthday = [r["birthday_ratio"] for r in records if r["birthday_ratio"] is not None]
    decision = hypothesis_decision(phase_results, global_tests, pairwise_tests)

    payload = {
        "metadata": {
            "draws_file": str(args.draws),
            "jackpots_file": str(args.jackpots),
            "jackpot_source": jackpot_source,
            "total_draws": len(draws),
            "date_range": {
                "start": str(draws["Datum"].min().date()) if not draws.empty else None,
                "end": str(draws["Datum"].max().date()) if not draws.empty else None,
            },
            "jackpots_used": len(jackpot_dates),
        },
        "expectation": {
            "overlap_count": EXPECTED_OVERLAP,
            "birthday_ratio": EXPECTED_BIRTHDAY_RATIO,
        },
        "phase_stats": phase_results,
        "global_tests": global_tests,
        "pairwise_tests": pairwise_tests,
        "overall": {
            "overlap": {
                "n": len(overall_overlap),
                "mean": float(np.mean(overall_overlap)) if overall_overlap else None,
                "std": float(np.std(overall_overlap, ddof=1)) if len(overall_overlap) > 1 else None,
            },
            "birthday_ratio": {
                "n": len(overall_birthday),
                "mean": float(np.mean(overall_birthday)) if overall_birthday else None,
                "std": float(np.std(overall_birthday, ddof=1)) if len(overall_birthday) > 1 else None,
            },
        },
        "decision": decision,
    }

    save_json(args.output, payload)

    # Optional Markdown summary (keeps console output short)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# HYP_013 Overlap-Birthday-Anteil nach Phase",
            f"- Draws: {args.draws}",
            f"- Jackpots: {args.jackpots} (source={jackpot_source}, count={len(jackpot_dates)})",
            f"- Zeitraum: {payload['metadata']['date_range']['start']} bis {payload['metadata']['date_range']['end']}",
            f"- Entscheidung: {'SUPPORT' if decision['support'] else 'REJECT'} ({decision['reason']})",
            "",
            "## Phase-Stats",
        ]
        for phase in PHASES:
            stats_overlap = phase_results[phase]["overlap"]
            stats_bday = phase_results[phase]["birthday_ratio"]
            lines.append(
                f"- {phase}: overlap n={stats_overlap['n']} mean={stats_overlap['mean']} z={stats_overlap['z']} p={stats_overlap.get('p_bh', stats_overlap['p'])}; "
                f"birthday n={stats_bday['n']} mean={stats_bday['mean']} z={stats_bday['z']} p={stats_bday.get('p_bh', stats_bday['p'])} "
                f"verif={stats_overlap['verification']}"
            )
        args.markdown.write_text("\n".join(lines), encoding="utf-8")

    print(f"JSON written to {args.output}")
    if args.markdown:
        print(f"Markdown summary written to {args.markdown}")
    print(f"Hypothesis decision: {'SUPPORT' if decision['support'] else 'REJECT'}")


if __name__ == "__main__":
    main()
