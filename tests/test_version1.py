# -*- coding: utf-8 -*-
"""Validation tests for the Version I model."""
from plumbotectonics.version1 import run


def test_version1_initial_conditions():
    hist, _, _, _ = run()
    first = hist[0]
    assert abs(first["mantle"]["206/204"] - 10.36) < 1e-6
    assert abs(first["mantle"]["207/204"] - 12.12) < 1e-6
    assert abs(first["mantle"]["208/204"] - 30.55) < 1e-6


def test_version1_present_day_matches_table_iv():
    """Present-day mantle against Zartman & Doe (1981), Table IV.

    Table IV gives 18.08 / 15.42 / 37.68 at t = 0; the model lands within
    0.4 of each (see docs/validation.md section 2).
    """
    hist, _, _, _ = run()
    last = hist[-1]
    assert abs(last["mantle"]["206/204"] - 18.08) < 0.5
    assert abs(last["mantle"]["207/204"] - 15.42) < 0.3
    assert abs(last["mantle"]["208/204"] - 37.68) < 0.5
