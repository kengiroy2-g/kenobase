"""Unit tests for kenobase.core.parsing."""

from __future__ import annotations

import pytest

from kenobase.core.parsing import parse_float_mixed_german, parse_int_mixed_german


@pytest.mark.unit
def test_parse_int_mixed_german_handles_float_string() -> None:
    assert parse_int_mixed_german("275.0") == 275


@pytest.mark.unit
def test_parse_int_mixed_german_handles_thousand_groups() -> None:
    assert parse_int_mixed_german("3.462") == 3462


@pytest.mark.unit
def test_parse_int_mixed_german_handles_two_decimal_group_with_dropped_zero() -> None:
    # common artifact when "2.910" is round-tripped as a number -> "2.91"
    assert parse_int_mixed_german("2.91") == 2910
    assert parse_int_mixed_german("1.04") == 1040


@pytest.mark.unit
def test_parse_float_mixed_german_handles_german_decimal() -> None:
    assert parse_float_mixed_german("1.234,56") == pytest.approx(1234.56)

