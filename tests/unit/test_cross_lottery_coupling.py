"""Unit tests for kenobase.analysis.cross_lottery_coupling."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np

from kenobase.analysis.cross_lottery_coupling import (
    GameDraws,
    bh_fdr,
    conditional_lifts_number_triggers,
    conditional_lifts_ordered_value_triggers,
)


def test_bh_fdr_basic():
    p = np.asarray([0.01, 0.02, 0.5], dtype=float)
    q = bh_fdr(p)
    assert q.shape == p.shape
    assert float(q[0]) == 0.03
    assert float(q[1]) == 0.03
    assert float(q[2]) == 0.5


def test_conditional_lifts_simple_signal_detected():
    # 10 daily draws.
    dates = [date(2025, 1, 1) + timedelta(days=i) for i in range(10)]

    # source pool=3, target pool=3
    # Rule: whenever source has number 1, target has number 2.
    src = np.zeros((10, 4), dtype=np.int8)
    trg = np.zeros((10, 4), dtype=np.int8)

    for i in range(10):
        if i % 2 == 0:
            src[i, 1] = 1
            trg[i, 2] = 1
        else:
            # Make sure base rate for target 2 is low outside the trigger.
            pass

    source = GameDraws(
        name="SRC",
        pool_max=3,
        draw_size=1,
        dates=dates,
        presence=src,
        ordered_numbers=None,
        jackpot_winners=None,
    )
    target = GameDraws(
        name="TRG",
        pool_max=3,
        draw_size=1,
        dates=dates,
        presence=trg,
        ordered_numbers=None,
        jackpot_winners=None,
    )

    lifts = conditional_lifts_number_triggers(
        source=source,
        target=target,
        lag_days=0,
        min_support=2,
        max_results=10,
        alpha_fdr=0.05,
        filter_by_alpha=True,
    )
    assert len(lifts) >= 1
    best = lifts[0]
    assert best.trigger == "1"
    assert best.target_number == 2
    assert best.lift > 1.0
    assert best.q_value <= 0.05


def test_ordered_value_triggers_simple_signal_detected():
    # 20 daily draws.
    dates = [date(2025, 2, 1) + timedelta(days=i) for i in range(20)]

    # Trigger: whenever source has P1=7, target has number 2.
    ordered: list[list[int]] = []
    trg = np.zeros((20, 4), dtype=np.int8)  # pool_max=3
    for i in range(20):
        if i < 10:
            ordered.append([7, 0])
            trg[i, 2] = 1
        else:
            ordered.append([1, 0])

    source = GameDraws(
        name="SRC",
        pool_max=1,
        draw_size=0,
        dates=dates,
        presence=np.zeros((20, 2), dtype=np.int8),
        ordered_numbers=ordered,
        jackpot_winners=None,
    )
    target = GameDraws(
        name="TRG",
        pool_max=3,
        draw_size=1,
        dates=dates,
        presence=trg,
        ordered_numbers=None,
        jackpot_winners=None,
    )

    lifts = conditional_lifts_ordered_value_triggers(
        source=source,
        target=target,
        lag_days=0,
        position_labels=["P1", "P2"],
        min_support=5,
        max_results=10,
        alpha_fdr=0.05,
        filter_by_alpha=True,
    )
    assert len(lifts) >= 1
    best = lifts[0]
    assert best.trigger == "P1=7"
    assert best.target_number == 2
    assert best.lift > 1.0
    assert best.q_value <= 0.05
