# -*- coding: utf-8 -*-
"""Validation tests for the version I model."""
from plumbotectonics.version1 import run


def test_version1_initial_conditions():
    hist, _, _, _ = run()
    first = hist[0]
    assert abs(first["mantle"]["206/204"] - 10.36) < 1e-6
    assert abs(first["mantle"]["207/204"] - 12.12) < 1e-6
    assert abs(first["mantle"]["208/204"] - 30.55) < 1e-6


def test_version1_present_day_order_of_magnitude():
    hist, _, _, _ = run()
    last = hist[-1]
    # Table IV gives approximately 18.25 / 15.48 / 38.06 for the mantle
    assert abs(last["mantle"]["206/204"] - 18.25) < 0.5
    assert abs(last["mantle"]["207/204"] - 15.48) < 0.3
    assert abs(last["mantle"]["208/204"] - 38.06) < 0.5
