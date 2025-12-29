"""Unit tests for the position-based rule layer."""

from __future__ import annotations

import numpy as np

from kenobase.prediction.position_rule_layer import (
    BASE_PRESENCE,
    RollingPositionRuleMiner,
    RuleFiring,
    apply_rule_layer_to_scores,
    index_to_trigger,
    trigger_index,
)


def test_trigger_index_roundtrip():
    idx = trigger_index(1, 1)
    assert idx == 0
    assert index_to_trigger(idx) == (1, 1)

    idx = trigger_index(70, 20)
    assert idx == (20 - 1) * 70 + (70 - 1)
    assert index_to_trigger(idx) == (70, 20)

    for number in (1, 7, 38, 49, 70):
        for position in (1, 5, 11, 20):
            idx = trigger_index(number, position)
            assert index_to_trigger(idx) == (number, position)


def test_miner_support_and_eviction():
    miner = RollingPositionRuleMiner(window_size=2)

    today1 = list(range(1, 21))
    tomorrow1 = list(range(1, 21))
    miner.add_transition(today_ordered=today1, tomorrow_numbers=tomorrow1)
    assert miner.trigger_support(1, 1) == 1

    # With n=1, Wilson-LB for success=1 is ~0.206 (z=1.96). Threshold 0.2 selects present numbers.
    inc = miner.inclusion_candidates(
        trigger_number=1,
        trigger_position=1,
        max_candidates=70,
        min_support=1,
        min_lower_bound=0.2,
    )
    assert any(c.number == 1 for c in inc)

    # Exclusion candidates: absent tomorrow for (1@1) should start at 21 when tomorrow is 1..20.
    ex = miner.exclusion_candidates(
        trigger_number=1,
        trigger_position=1,
        max_candidates=3,
        min_support=1,
        min_lower_bound=0.2,
    )
    assert [c.number for c in ex] == [21, 22, 23]

    today2 = list(range(21, 41))
    tomorrow2 = list(range(21, 41))
    miner.add_transition(today_ordered=today2, tomorrow_numbers=tomorrow2)
    assert miner.trigger_support(1, 1) == 1
    assert miner.trigger_support(21, 1) == 1

    today3 = list(range(41, 61))
    tomorrow3 = list(range(41, 61))
    miner.add_transition(today_ordered=today3, tomorrow_numbers=tomorrow3)
    # window_size=2 -> first transition evicted
    assert miner.trigger_support(1, 1) == 0
    assert miner.trigger_support(21, 1) == 1
    assert miner.trigger_support(41, 1) == 1


def test_apply_rule_layer_boost_and_hard_exclude():
    base_scores = np.full(71, float(BASE_PRESENCE), dtype=float)

    inclusions = [
        RuleFiring(
            trigger_number=10,
            trigger_position=1,
            kind="include",
            predicted_number=5,
            probability=0.5,
            lower_bound=0.5,
            support=100,
        )
    ]
    exclusions = [
        RuleFiring(
            trigger_number=10,
            trigger_position=1,
            kind="exclude",
            predicted_number=6,
            probability=0.95,
            lower_bound=0.95,
            support=100,
        )
    ]

    adjusted, excluded, included = apply_rule_layer_to_scores(
        base_scores,
        exclusions=exclusions,
        inclusions=inclusions,
        hard_exclude=True,
        hard_exclude_lb=0.95,
    )

    assert 5 in included
    assert 6 in excluded
    assert float(adjusted[6]) < -1e8  # hard excluded
    assert float(adjusted[5]) > float(adjusted[4])  # boosted vs baseline

