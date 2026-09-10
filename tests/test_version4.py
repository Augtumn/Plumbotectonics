# -*- coding: utf-8 -*-
"""Validation tests for the calibrated Version IV model."""
from plumbotectonics.version4 import run, ratios

TARGETS = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper": [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower": [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub": [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]


def test_version4_matches_table4():
    result = run(dp=0.14)
    for name, target in TARGETS.items():
        values = [ratios(result[name])[k] for k in KEYS]
        for value, tgt in zip(values, target):
            assert abs(value - tgt) < 0.02, f"{name} {value} vs {tgt}"
