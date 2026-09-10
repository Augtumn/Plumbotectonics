# -*- coding: utf-8 -*-
"""Invariant tests: mass conservation and structural regressions.

These do not re-check the published ending values (see ``test_version1.py`` /
``test_version4.py``); they pin the internal consistency of the two models.
"""
from plumbotectonics.version1 import ratios as v1_ratios
from plumbotectonics.version1 import run as run_v1
from plumbotectonics.version4 import FNEmoles, ratios as v4_ratios
from plumbotectonics.version4 import run as run_v4

INITIAL_MASS_V1 = 800.0
INITIAL_MASS_V4 = 1050.0
V1_KEYS = ("204", "206", "207", "208", "232", "238")


def test_version1_mass_is_conserved():
    _, mantle, upper_segs, lower_segs = run_v1()
    total = (mantle["mass"]
             + sum(s["mass"] for s in upper_segs)
             + sum(s["mass"] for s in lower_segs))
    assert abs(total - INITIAL_MASS_V1) < 1e-9


def test_version1_one_segment_per_cycle():
    _, _, upper_segs, lower_segs = run_v1()
    assert len(upper_segs) == 11
    assert len(lower_segs) == 11


def test_version1_segments_stay_positive():
    _, _, upper_segs, lower_segs = run_v1()
    for seg in upper_segs + lower_segs:
        assert seg["mass"] > 0.0
        for key in V1_KEYS:
            assert seg[key] >= 0.0


def test_version4_mass_is_conserved():
    result = run_v4(dp=0.14)
    parts = ("mantle", "upper", "lower", "sub")
    assert abs(result["masses"]["total"] - INITIAL_MASS_V4) < 1e-6
    assert abs(sum(result["masses"][p] for p in parts) - INITIAL_MASS_V4) < 1e-6


def test_version4_total_is_sum_of_reservoirs():
    result = run_v4(dp=0.14)
    for h in range(1, 7):
        expected = sum(result[name][h] for name in ("mantle", "upper", "lower", "sub"))
        assert abs(result["total"][h] - expected) < 1e-9


def test_version4_history_shape():
    result = run_v4(dp=0.14)
    hist = result["history"]
    assert len(hist) == 46
    assert [h["cycle"] for h in hist] == list(range(1, 47))
    assert abs(hist[0]["time_Ga"] - 4.4) < 1e-9
    assert abs(hist[-1]["time_Ga"] - 0.0) < 1e-9


def test_version4_mantle_206_204_is_monotonic():
    result = run_v4(dp=0.14)
    series = [h["mantle"]["206/204"] for h in result["history"]]
    assert all(a <= b for a, b in zip(series, series[1:]))


def test_ratios_returns_none_on_zero_denominator():
    empty = {1: 0.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0}
    out = v4_ratios(empty)
    assert out["206/204"] is None
    assert out["207/204"] is None
    assert out["208/204"] is None
    assert out["238U/204Pb"] is None
    assert out["232Th/204Pb"] is None
    assert out["232Th/238U"] == 1.0
    assert v1_ratios({"204": 0, "206": 1.0, "207": 1.0, "208": 1.0}) is None


def test_fnemoles_guards():
    assert FNEmoles(10.0, 1.0, 1.0, 0.0) == 0.0
    assert FNEmoles(10.0, 0.0, 0.0, 1.0) == 0.0
    assert FNEmoles(10.0, 1.0, 0.0, 1.0) > 0.0


def test_fnemoles_is_elementwise():
    """The numpy rewrite must accept a whole isotope axis at once."""
    import numpy as np

    N = np.array([10.0, 20.0, 30.0])
    bias = np.array([1.0, 0.0, 2.0])          # the middle one hits the guard
    got = FNEmoles(N, 1.0, 1.0, bias)
    assert got.shape == (3,)
    assert got[0] == FNEmoles(10.0, 1.0, 1.0, 1.0)
    assert got[1] == 0.0
    assert got[2] == FNEmoles(30.0, 1.0, 1.0, 2.0)


def test_models_compute_with_numpy():
    """Both cores carry their state in ndarrays and no longer use `math`."""
    import ast
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "src" / "plumbotectonics"
    for name in ("version1.py", "version4.py"):
        tree = ast.parse((src / name).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert imported == {"numpy"}, (name, imported)


def test_version1_returns_the_documented_dicts():
    """The numpy migration must not leak arrays into the public API."""
    import numpy as np

    hist, mantle, upper_segs, lower_segs = run_v1()
    for reservoir in [mantle] + upper_segs + lower_segs:
        assert type(reservoir) is dict
        for key in ("mass", "204", "206", "207", "208", "232", "238"):
            assert type(reservoir[key]) is float, (key, type(reservoir[key]))
    for entry in hist:
        assert type(entry["t"]) is float
        for name in ("mantle", "orogene", "upper", "lower"):
            if entry[name] is not None:
                assert type(entry[name]) is dict
    assert not any(isinstance(v, np.ndarray) for v in mantle.values())
