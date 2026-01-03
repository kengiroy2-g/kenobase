#!/usr/bin/env python3
"""
OPTIMIERTER POOL-GENERATOR V3 (CORRECTION-AWARE)

Wissenschaftlicher Fokus:
  - A8 (Auszahlungs-Reaktion): Nach hohen Auszahlungen/JPs steigt die "Korrektur"
    und das System priorisiert Zahlen neu.
  - Anti-Pattern: BAD_PATTERNS aus DANCE-009 bleiben als Filter/Abwertung erhalten.
  - Ziel ist NICHT "Gewinn garantieren", sondern eine reproduzierbare,
    datengetriebene Pool-Selektion, die sich am beobachteten Systemzustand orientiert.

V3-Idee:
  - Bestimme eine Korrektur-Staerke aus Auszahlungs-/Einsatzdaten (GQ + Spieleinsatz).
  - Moduliere Pool-Mix + Zahl-Scoring mit dieser Korrektur-Staerke.
    -> Mehr Non-Birthday / weniger HOT in "Correction"-Phasen.

Usage:
  python scripts/generate_optimized_pool_v3.py
  python scripts/generate_optimized_pool_v3.py --pool-size 17 --popularity-source heuristic
  python scripts/generate_optimized_pool_v3.py --save results/optimized_pool_v3.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from kenobase.core.parsing import parse_float_mixed_german
from kenobase.analysis.popularity_correlation import calculate_popularity_scores_heuristic


# -----------------------------------------------------------------------------
# Constants / shared definitions (align with DANCE-006/009 scripts)
# -----------------------------------------------------------------------------

BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))

TOP_20_CORRECTION = {
    1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70
}

BAD_PATTERNS = {
    "0010010",  # 83.3% Miss
    "1000111",  # 82.1% Miss
    "0101011",  # 81.1% Miss
    "1010000",  # 80.4% Miss
    "0001101",  # 77.3% Miss
    "0001000",  # 77.1% Miss
    "0100100",  # 77.1% Miss
    "0001010",  # 77.0% Miss
    "0000111",  # 75.9% Miss
}

GOOD_PATTERNS = {
    "0011101",  # 55.6% Miss - BESTE!
    "1010011",  # 59.3% Miss
    "0001001",  # 60.3% Miss
    "1010101",  # 60.7% Miss
    "0010100",  # 62.1% Miss
    "1000001",  # 62.3% Miss
    "1000010",  # 63.1% Miss
    "0001011",  # 64.2% Miss
    "0010101",  # 64.9% Miss
}


@dataclass(frozen=True)
class DailyPayoutRow:
    date: datetime
    total_winners: float
    total_payout_eur: float
    stake_eur: float | None
    payout_ratio: float | None
    is_jackpot_10_10: bool


@dataclass(frozen=True)
class CorrectionState:
    """State proxy for payout-driven correction (A8)."""

    strength: float  # 0..1
    reason: str
    payout_z: float
    ratio_z: float
    days_since_jackpot_10_10: int | None


def load_keno_draws(filepath: Path) -> list[dict]:
    """Load KENO draws with numbers + optional stake."""
    df = pd.read_csv(filepath, sep=";", encoding="utf-8-sig")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["datum"]).sort_values("datum").reset_index(drop=True)

    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    draws: list[dict] = []
    for _, row in df.iterrows():
        nums = []
        for col in number_cols:
            v = row.get(col)
            if pd.isna(v):
                continue
            nums.append(int(v))
        if len(nums) != 20:
            continue

        stake_raw = row.get("Keno_Spieleinsatz", None)
        stake = parse_float_mixed_german(stake_raw, default=float("nan"))
        stake_eur = float(stake) if stake and np.isfinite(stake) and stake > 0 else None

        draws.append(
            {
                "datum": row["datum"].to_pydatetime(),
                "zahlen": set(nums),
                "stake_eur": stake_eur,
            }
        )
    return draws


def load_gq_daily_stats(paths: list[Path]) -> dict[datetime.date, DailyPayoutRow]:
    """Load Keno_GQ data and aggregate to daily payout stats."""
    frames: list[pd.DataFrame] = []
    for path in paths:
        frames.append(pd.read_csv(path, encoding="utf-8", engine="python"))

    gq = pd.concat(frames, ignore_index=True)
    gq["date"] = pd.to_datetime(gq["Datum"].astype(str).str.strip(), format="%d.%m.%Y", errors="coerce")
    gq = gq.dropna(subset=["date"]).reset_index(drop=True)

    gq["keno_type"] = gq["Keno-Typ"].astype(int)
    gq["matches"] = gq["Anzahl richtiger Zahlen"].astype(int)
    gq["winners"] = gq["Anzahl der Gewinner"].apply(parse_float_mixed_german)
    gq["prize_eur"] = gq["1 Euro Gewinn"].apply(parse_float_mixed_german)
    gq["payout_eur"] = gq["winners"] * gq["prize_eur"]

    jackpot_mask = (gq["keno_type"] == 10) & (gq["matches"] == 10) & (gq["winners"] > 0)
    jackpot_by_day = gq.loc[jackpot_mask].groupby("date").size()

    daily = gq.groupby("date", as_index=False).agg(
        total_winners=("winners", "sum"),
        total_payout_eur=("payout_eur", "sum"),
    )

    out: dict[datetime.date, DailyPayoutRow] = {}
    for _, row in daily.iterrows():
        date = row["date"].to_pydatetime()
        out[date.date()] = DailyPayoutRow(
            date=date,
            total_winners=float(row["total_winners"]),
            total_payout_eur=float(row["total_payout_eur"]),
            stake_eur=None,
            payout_ratio=None,
            is_jackpot_10_10=bool(jackpot_by_day.get(row["date"], 0) > 0),
        )
    return out


def attach_stake_and_ratio(
    *,
    draws: list[dict],
    daily_stats: dict[datetime.date, DailyPayoutRow],
) -> dict[datetime.date, DailyPayoutRow]:
    """Merge stake from draws into daily payout stats and compute payout_ratio."""
    updated: dict[datetime.date, DailyPayoutRow] = dict(daily_stats)

    for d in draws:
        date = d["datum"].date()
        stake = d.get("stake_eur")
        if date not in updated:
            continue
        base = updated[date]
        stake_eur = float(stake) if stake is not None else None
        ratio = None
        if stake_eur is not None and stake_eur > 0:
            ratio = base.total_payout_eur / stake_eur
        updated[date] = DailyPayoutRow(
            date=base.date,
            total_winners=base.total_winners,
            total_payout_eur=base.total_payout_eur,
            stake_eur=stake_eur,
            payout_ratio=ratio,
            is_jackpot_10_10=base.is_jackpot_10_10,
        )
    return updated


def _zscore(values: list[float]) -> float:
    if len(values) < 10:
        return 0.0
    mean = float(np.mean(values))
    std = float(np.std(values))
    if std <= 1e-9:
        return 0.0
    return (values[-1] - mean) / std


def compute_correction_state(
    *,
    train_draws: list[dict],
    daily_stats: dict[datetime.date, DailyPayoutRow],
    lookback_days: int = 60,
) -> CorrectionState:
    """Compute a simple payout-driven correction state proxy (0..1)."""
    if not train_draws:
        return CorrectionState(
            strength=0.0,
            reason="no_history",
            payout_z=0.0,
            ratio_z=0.0,
            days_since_jackpot_10_10=None,
        )

    last_date = train_draws[-1]["datum"].date()
    if last_date not in daily_stats:
        return CorrectionState(
            strength=0.0,
            reason="no_gq_data",
            payout_z=0.0,
            ratio_z=0.0,
            days_since_jackpot_10_10=None,
        )

    last_row = daily_stats[last_date]
    use_ratio = last_row.payout_ratio is not None and np.isfinite(last_row.payout_ratio)

    # collect last N days with available stats (lookback from train_draws chronology)
    dates: list[datetime.date] = [d["datum"].date() for d in train_draws[-lookback_days:]]
    payouts: list[float] = []
    ratios: list[float] = []
    for dt in dates:
        row = daily_stats.get(dt)
        if row is None:
            continue
        payouts.append(float(row.total_payout_eur))
        if use_ratio and row.payout_ratio is not None and np.isfinite(row.payout_ratio):
            ratios.append(float(row.payout_ratio))

    payout_z = _zscore(payouts) if payouts else 0.0
    ratio_z = _zscore(ratios) if ratios else 0.0

    # Days since 10/10 jackpot (proxy for strong events)
    days_since_jackpot: int | None = None
    for offset, d in enumerate(reversed(train_draws)):
        dt = d["datum"].date()
        row = daily_stats.get(dt)
        if row is None:
            continue
        if row.is_jackpot_10_10:
            days_since_jackpot = offset
            break

    # Strength: clamp positive z-scores into 0..1 (z=2 -> 1.0)
    raw = max(0.0, ratio_z) if use_ratio and ratios else max(0.0, payout_z)
    strength = min(1.0, raw / 2.0)

    reason = "normal"
    if days_since_jackpot is not None and days_since_jackpot <= 3:
        strength = max(strength, 0.9)
        reason = "post_jackpot_10_10"
    elif ratio_z >= 1.0 or payout_z >= 1.0:
        reason = "high_payout"

    return CorrectionState(
        strength=float(strength),
        reason=reason,
        payout_z=float(payout_z),
        ratio_z=float(ratio_z),
        days_since_jackpot_10_10=days_since_jackpot,
    )


# -----------------------------------------------------------------------------
# Feature helpers (similar to V2, but kept local to avoid drift-by-copy later)
# -----------------------------------------------------------------------------


def get_hot_numbers(draws: list[dict], lookback: int = 3) -> set[int]:
    """HOT Zahlen (>=2x in den letzten X Tagen)."""
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts: dict[int, int] = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_index(draws: list[dict], number: int) -> int:
    """Wann wurde die Zahl zuletzt gezogen (0 = heute)."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: list[dict], number: int, lookback: int = 30) -> int:
    """Wie oft wurde die Zahl in den letzten X Tagen gezogen."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_pattern_7(draws: list[dict], number: int) -> str:
    """7-Tage-Binaermuster (1=erschienen, 0=gefehlt)."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_streak(draws: list[dict], number: int) -> int:
    """Aktuelle Streak (positiv=erscheint, negativ=fehlt)."""
    if not draws:
        return 0
    streak = 0
    in_last = number in draws[-1]["zahlen"]
    for draw in reversed(draws):
        if (number in draw["zahlen"]) == in_last:
            streak += 1
        else:
            break
    return streak if in_last else -streak


def get_avg_gap(draws: list[dict], number: int, lookback: int = 60) -> float:
    """Durchschnittliche Luecke zwischen Erscheinungen."""
    gaps: list[int] = []
    last_seen: int | None = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return float(np.mean(gaps)) if gaps else 10.0


def score_number_v2(draws: list[dict], number: int, hot: set[int]) -> float:
    """V2 Scoring: Pattern, Streak, Gap, Index."""
    score = 50.0

    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    elif pattern in GOOD_PATTERNS:
        score += 15

    streak = get_streak(draws, number)
    if streak >= 3:
        score -= 10
    elif streak <= -5:
        score -= 5
    elif 0 < streak <= 2:
        score += 5

    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5

    index = get_index(draws, number)
    if index >= 10:
        score -= 5
    elif 3 <= index <= 6:
        score += 5

    ones = get_pattern_7(draws, number).count("1")
    if ones in {2, 3}:
        score += 5
    elif ones >= 5:
        score -= 5

    return score


def _build_popularity_scores(
    *,
    draws: list[dict],
    daily_stats: dict[datetime.date, DailyPayoutRow],
    source: str,
) -> dict[int, float]:
    if source == "heuristic":
        return calculate_popularity_scores_heuristic(range(1, 71))

    if source != "gq":
        raise ValueError(f"Unknown popularity source: {source}")

    # GQ-derived popularity proxy:
    # numbers that appear on days with many winners are treated as "popular".
    score_sum: dict[int, float] = defaultdict(float)
    count_sum: dict[int, int] = defaultdict(int)

    for d in draws:
        dt = d["datum"].date()
        row = daily_stats.get(dt)
        if row is None:
            continue
        winners = float(row.total_winners)
        for n in d["zahlen"]:
            score_sum[n] += winners
            count_sum[n] += 1

    scores: dict[int, float] = {}
    for n in range(1, 71):
        if count_sum.get(n, 0) <= 0:
            scores[n] = 0.0
        else:
            scores[n] = score_sum[n] / count_sum[n]

    mx = max(scores.values()) if scores else 1.0
    if mx > 0:
        scores = {k: float(v) / float(mx) for k, v in scores.items()}
    return scores


def score_number_v3(
    *,
    draws: list[dict],
    number: int,
    hot: set[int],
    correction: CorrectionState,
    popularity_scores: dict[int, float],
) -> float:
    """V3 score = V2 score + correction/popularity modulation."""
    base = score_number_v2(draws, number, hot)

    # Hard block: "Correction-HOT" (DANCE-004)
    if number in hot and number in TOP_20_CORRECTION:
        return -1e9

    strength = float(correction.strength)
    popularity = float(popularity_scores.get(number, 0.0))

    # Correction pressure: penalize popular + correction-list numbers more in high-correction regimes.
    corr_flag = 1.0 if number in TOP_20_CORRECTION else 0.0
    birthday_flag = 1.0 if number in BIRTHDAY_NUMBERS else 0.0

    penalty = 0.0
    penalty += strength * popularity * 12.0
    penalty += strength * corr_flag * 4.0
    penalty += strength * birthday_flag * 2.0

    # Small bonus for non-birthday when correction is high (anti-popularity).
    bonus = strength * (1.0 - birthday_flag) * 1.0

    return base - penalty + bonus


def _choose_segment_sizes(target_size: int, correction: CorrectionState) -> tuple[int, int, int]:
    """Decide how many numbers to take from HOT / COLD-BD / COLD-NBD."""
    strength = float(correction.strength)
    # Default: 5/6/6 at size 17. In correction phases: reduce HOT and birthdays.
    hot_target = int(round(5 - 2 * strength))
    hot_target = max(3, min(6, hot_target))

    remaining = max(0, target_size - hot_target)

    # Shift weight from Birthday -> Non-Birthday with correction strength.
    shift = int(round(strength * 2))  # 0..2
    cold_nbd_target = remaining // 2 + shift
    cold_bd_target = remaining - cold_nbd_target

    # Safety clamps
    cold_bd_target = max(0, cold_bd_target)
    cold_nbd_target = max(0, cold_nbd_target)
    if hot_target + cold_bd_target + cold_nbd_target != target_size:
        cold_nbd_target = max(0, target_size - hot_target - cold_bd_target)

    return hot_target, cold_bd_target, cold_nbd_target


def build_reduced_pool_v3(
    *,
    draws: list[dict],
    daily_stats: dict[datetime.date, DailyPayoutRow],
    popularity_scores: dict[int, float],
    target_size: int = 17,
    correction_lookback_days: int = 60,
) -> tuple[set[int], dict]:
    """
    V3: DANCE-006 + DANCE-009 + A8 (Auszahlungs-Reaktion).

    Returns:
        (pool_set, details_dict)
    """
    if not 1 <= target_size <= 70:
        raise ValueError(f"target_size muss zwischen 1 und 70 liegen (ist {target_size})")
    if len(draws) < 10:
        return set(), {"pool_size": 0, "reason": "not_enough_history"}

    correction = compute_correction_state(
        train_draws=draws,
        daily_stats=daily_stats,
        lookback_days=correction_lookback_days,
    )
    hot_target, cold_bd_target, cold_nbd_target = _choose_segment_sizes(target_size, correction)

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    patterns = {z: get_pattern_7(draws, z) for z in ALL_NUMBERS}
    bad_pattern_numbers = {z for z, p in patterns.items() if p in BAD_PATTERNS}

    # HOT selection (exclude Correction-HOT implicitly via score -1e9)
    hot_candidates = sorted(hot - TOP_20_CORRECTION)
    hot_scored = [
        (z, score_number_v3(draws=draws, number=z, hot=hot, correction=correction, popularity_scores=popularity_scores))
        for z in hot_candidates
    ]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, _ in hot_scored[: min(hot_target, len(hot_scored))])

    # COLD-Birthday selection
    cold_bd_scored = [
        (
            z,
            get_count(draws, z),
            score_number_v3(draws=draws, number=z, hot=hot, correction=correction, popularity_scores=popularity_scores),
        )
        for z in cold_birthday
    ]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [t for t in cold_bd_scored if patterns[t[0]] not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, _, _ in cold_bd_filtered[: min(cold_bd_target, len(cold_bd_filtered))])
    if cold_bd_target and len(cold_bd_keep) < cold_bd_target:
        fallback = [z for z, _, _ in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(fallback[: cold_bd_target - len(cold_bd_keep)])

    # COLD-Non-Birthday selection
    cold_nbd_scored = [
        (
            z,
            get_count(draws, z),
            score_number_v3(draws=draws, number=z, hot=hot, correction=correction, popularity_scores=popularity_scores),
        )
        for z in cold_nonbd
    ]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [t for t in cold_nbd_scored if patterns[t[0]] not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, _, _ in cold_nbd_filtered[: min(cold_nbd_target, len(cold_nbd_filtered))])
    if cold_nbd_target and len(cold_nbd_keep) < cold_nbd_target:
        fallback = [z for z, _, _ in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(fallback[: cold_nbd_target - len(cold_nbd_keep)])

    pool = set(hot_keep | cold_bd_keep | cold_nbd_keep)

    # If we underfill because of extreme constraints, fill by best V3 score overall.
    if len(pool) < target_size:
        remaining = sorted(list(ALL_NUMBERS - pool))
        scored = [
            (
                z,
                score_number_v3(draws=draws, number=z, hot=hot, correction=correction, popularity_scores=popularity_scores),
            )
            for z in remaining
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        for z, _ in scored:
            pool.add(z)
            if len(pool) >= target_size:
                break

    details = {
        "pool_size": len(pool),
        "pool": sorted(pool),
        "hot_all": sorted(hot),
        "hot_keep": sorted(hot_keep),
        "cold_birthday_keep": sorted(cold_bd_keep),
        "cold_nonbd_keep": sorted(cold_nbd_keep),
        "bad_pattern_count": len(bad_pattern_numbers),
        "bad_pattern_in_pool": sorted(pool & bad_pattern_numbers),
        "targets": {
            "hot": hot_target,
            "cold_birthday": cold_bd_target,
            "cold_non_birthday": cold_nbd_target,
        },
        "correction_state": {
            "strength": correction.strength,
            "reason": correction.reason,
            "payout_z": correction.payout_z,
            "ratio_z": correction.ratio_z,
            "days_since_jackpot_10_10": correction.days_since_jackpot_10_10,
        },
    }

    return pool, details


def _fmt_pct(x: float | None) -> str:
    if x is None or not np.isfinite(x):
        return "n/a"
    return f"{x*100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimierter Pool-Generator V3 (correction-aware)")
    parser.add_argument("--pool-size", type=int, default=17, help="Pool-Groesse (Default: 17)")
    parser.add_argument(
        "--popularity-source",
        choices=["heuristic", "gq"],
        default="heuristic",
        help="Popularity-Proxy (Default: heuristic)",
    )
    parser.add_argument(
        "--correction-lookback",
        type=int,
        default=60,
        help="Lookback fuer Correction-State (Default: 60 Tage)",
    )
    parser.add_argument(
        "--as-of",
        type=str,
        default="",
        help="Optional: Pool berechnen als-of Datum (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--save",
        type=str,
        default="",
        help="Optional: JSON output (Pfad relativ zum Repo-Root)",
    )
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"
    gq_paths = [
        base_path / "Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
        base_path / "Keno_GPTs/Keno_GQ_2025.csv",
    ]

    draws = load_keno_draws(keno_path)
    daily_stats = load_gq_daily_stats(gq_paths)
    daily_stats = attach_stake_and_ratio(draws=draws, daily_stats=daily_stats)

    if args.as_of:
        try:
            as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
        except ValueError as exc:
            raise SystemExit("--as-of muss YYYY-MM-DD sein") from exc
        draws = [d for d in draws if d["datum"].date() <= as_of]
        if not draws:
            raise SystemExit("Keine Ziehungen <= --as-of gefunden")

    popularity_scores = _build_popularity_scores(draws=draws, daily_stats=daily_stats, source=args.popularity_source)

    pool, details = build_reduced_pool_v3(
        draws=draws,
        daily_stats=daily_stats,
        popularity_scores=popularity_scores,
        target_size=args.pool_size,
        correction_lookback_days=args.correction_lookback,
    )

    last_draw = draws[-1]
    last_date = last_draw["datum"].date()
    last_stats = daily_stats.get(last_date)

    print("=" * 90)
    print("OPTIMIERTER POOL-GENERATOR V3 (CORRECTION-AWARE)")
    print("=" * 90)
    print(f"Letzte Ziehung: {last_date.isoformat()}")
    print(f"Gezogen: {sorted(last_draw['zahlen'])}")
    if last_stats is not None:
        print(
            "Tages-Stats:",
            f"payout={last_stats.total_payout_eur:,.0f} EUR,",
            f"stake={last_stats.stake_eur:,.0f} EUR" if last_stats.stake_eur else "stake=n/a,",
            f"ratio={_fmt_pct(last_stats.payout_ratio)}",
            f"JP10/10={'YES' if last_stats.is_jackpot_10_10 else 'NO'}",
        )
    print()
    print("CORRECTION-STATE (Proxy):")
    cs = details["correction_state"]
    print(f"  strength={cs['strength']:.2f} reason={cs['reason']} payout_z={cs['payout_z']:.2f} ratio_z={cs['ratio_z']:.2f}")
    print()
    print("POOL (V3):")
    print(f"  targets: HOT={details['targets']['hot']} BD={details['targets']['cold_birthday']} NBD={details['targets']['cold_non_birthday']}")
    print(f"  size:    {details['pool_size']}")
    print(f"  pool:    {details['pool']}")
    print(f"  bad_pattern_in_pool: {details['bad_pattern_in_pool']}")

    if args.save:
        out_path = Path(args.save)
        if not out_path.is_absolute():
            out_path = base_path / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now().isoformat(),
            "last_draw_date": last_date.isoformat(),
            "pool": sorted(pool),
            "details": details,
            "inputs": {
                "pool_size": args.pool_size,
                "popularity_source": args.popularity_source,
                "correction_lookback": args.correction_lookback,
            },
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"Gespeichert: {out_path}")


if __name__ == "__main__":
    main()
