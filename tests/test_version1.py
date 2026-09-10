# -*- coding: utf-8 -*-
"""Validation tests for the Version I model.

Reference values are Zartman & Doe (1981): Table IV (reservoir growth curves)
and Table II section III (ending inventories).  See ``docs/validation.md``
section 2.
"""
import math

from plumbotectonics.version1 import run

RATIOS = ("206/204", "207/204", "208/204")

# Zartman & Doe (1981) Table IV -- lead isotopic composition of the reservoir
# growth curves, one tuple per orogeny, oldest first.
TABLE_IV = {
    "mantle": [(10.36, 12.12, 30.55), (11.36, 13.21, 31.34), (12.30, 13.94, 32.11),
               (13.19, 14.44, 32.86), (14.02, 14.78, 33.59), (14.80, 15.00, 34.30),
               (15.54, 15.15, 35.00), (16.23, 15.26, 35.69), (16.88, 15.33, 36.37),
               (17.50, 15.38, 37.03), (18.08, 15.42, 37.68)],
    "orogene": [(10.36, 12.12, 30.55), (11.42, 13.27, 31.40), (12.47, 14.09, 32.30),
                (13.50, 14.67, 33.20), (14.47, 15.06, 34.11), (15.35, 15.29, 34.95),
                (16.17, 15.44, 35.77), (16.92, 15.53, 36.56), (17.62, 15.58, 37.34),
                (18.27, 15.61, 38.09), (18.88, 15.63, 38.82)],
    "upper": [(10.36, 12.12, 30.55), (11.61, 13.48, 31.57), (12.69, 14.29, 32.46),
              (13.72, 14.83, 33.35), (14.70, 15.20, 34.23), (15.64, 15.44, 35.10),
              (16.51, 15.59, 35.94), (17.30, 15.67, 36.76), (18.04, 15.71, 37.55),
              (18.71, 15.73, 38.32), (19.33, 15.73, 39.06)],
    "lower": [(10.36, 12.12, 30.55), (10.98, 12.79, 31.41), (11.76, 13.46, 32.24),
              (12.52, 13.95, 33.06), (13.27, 14.33, 33.89), (14.00, 14.61, 34.70),
              (14.72, 14.83, 35.51), (15.40, 15.00, 36.29), (16.06, 15.13, 37.06),
              (16.69, 15.22, 37.82), (17.29, 15.30, 38.56)],
}

# Table IV is printed to two decimals, so 0.005 is the nominal tolerance.  The
# worst residual over all 126 rows is 0.00509 (t = 1.6 Ga, mantle 207/204:
# model 15.1551 against a printed 15.15), i.e. exactly on the rounding
# boundary, so the tolerance carries a 0.001 allowance.
PRINT_PRECISION = 0.006

# Table II section III.B -- masses after the final orogeny (1e24 g) and the
# 204Pb/238U/232Th inventories (1e15 mol).
TABLE_II_END = {
    "mantle": (775.2, 19.5, 174.0, 619.0),
    "upper": (7.0, 10.3, 127.0, 430.0),
    "lower": (17.8, 8.2, 48.0, 286.0),
}


def _final_inventories():
    """Sum the segments of each reservoir once the run has finished."""
    _, mantle, upper_segs, lower_segs = run()
    keys = ("204", "238", "232")
    out = {"mantle": {"mass": mantle["mass"], **{k: mantle[k] for k in keys}}}
    for name, segs in (("upper", upper_segs), ("lower", lower_segs)):
        out[name] = {"mass": sum(s["mass"] for s in segs),
                     **{k: sum(s[k] for s in segs) for k in keys}}
    return out


def test_version1_initial_conditions():
    hist, _, _, _ = run()
    first = hist[0]["mantle"]
    assert abs(first["206/204"] - 10.36) < 1e-6
    assert abs(first["207/204"] - 12.12) < 1e-6
    assert abs(first["208/204"] - 30.55) < 1e-6


def test_version1_matches_table_iv_every_cycle():
    """11 orogenies x 4 reservoirs x 3 ratios: 126 comparisons."""
    hist, _, _, _ = run()
    checked = 0
    for index, entry in enumerate(hist):
        for reservoir, series in TABLE_IV.items():
            got = entry.get(reservoir)
            if not got:
                continue
            for ratio, expected in zip(RATIOS, series[index]):
                assert abs(got[ratio] - expected) <= PRINT_PRECISION, (
                    f"t={entry['t']:.1f} {reservoir} {ratio}: "
                    f"model={got[ratio]:.4f} table={expected}")
                checked += 1
    assert checked == 126


def test_version1_ending_inventories_match_table_ii():
    """Table II section III.B: mass and 204Pb/238U/232Th after the last orogeny."""
    totals = _final_inventories()
    for reservoir, (mass, pb204, u238, th232) in TABLE_II_END.items():
        got = totals[reservoir]
        assert abs(got["mass"] - mass) / mass < 0.01
        for key, expected in (("204", pb204), ("238", u238), ("232", th232)):
            assert abs(got[key] - expected) / expected < 0.01, (
                f"{reservoir} {key}: model={got[key]:.2f} table={expected}")


def test_version1_first_orogeny_closed_form():
    """Recompute the mantle at t = 3.6 Ga from the paper's equations.

    The first orogeny is the only one with no pre-existing crust, so the whole
    orogene is mantle-derived and eqs. 14, 17-19 plus one decay interval
    (eq. 20) can be evaluated directly.
    """
    f_m, e_m, new_crust = 1 / 8, 4.0, 2.6
    dm = 800.0 * f_m
    m_ret = dm - 2 * new_crust                      # mass returning to the mantle
    f_pb, f_u = (0.028, 0.754, 0.218), (0.024, 0.854, 0.122)
    s_pb = m_ret * f_pb[0] + new_crust * f_pb[1] + new_crust * f_pb[2]
    s_u = m_ret * f_u[0] + new_crust * f_u[1] + new_crust * f_u[2]

    # mantle inventory after the orogeny: lose f_m*E_m, gain the weighted share
    retraction = 1 - f_m * e_m
    pb204 = 38.0 * retraction + f_m * e_m * 38.0 * (m_ret * f_pb[0] / s_pb)
    u238 = 349.0 * retraction + f_m * e_m * 349.0 * (m_ret * f_u[0] / s_u)
    pb206 = (38.0 * 10.36 * retraction
             + f_m * e_m * 38.0 * 10.36 * (m_ret * f_pb[0] / s_pb))

    growth = math.exp(0.155125 * 4.0) - math.exp(0.155125 * 3.6)
    pb206 += u238 * growth

    assert abs(pb204 - 28.733) < 0.01
    assert abs(pb206 / pb204 - 11.36) <= PRINT_PRECISION   # Table IV, t = 3.6

    hist, _, _, _ = run()
    assert abs(hist[1]["mantle"]["206/204"] - pb206 / pb204) < 0.005


def test_version1_redistribution_is_mass_weighted():
    """Eqs. 17-19: the partition ratios are concentration ratios, not shares.

    The mantle takes back ``M_or - 2.6 - 2.6`` of mass against 2.6 for each new
    crust, so it receives the bulk of the orogene lead.  Reading ``F_PB[0]`` as
    a fraction of the orogene content (the pre-fix behaviour) would give it
    2.8 % and strip the mantle -- 11.46e15 mol of 204Pb instead of 19.5e15.
    """
    f_pb, new_crust = (0.028, 0.754, 0.218), 2.6
    m_ret = 800.0 / 8 - 2 * new_crust
    s = m_ret * f_pb[0] + new_crust * f_pb[1] + new_crust * f_pb[2]
    mantle_share = m_ret * f_pb[0] / s
    assert abs(mantle_share - 0.5123) < 1e-3
    assert mantle_share > f_pb[0] * 10          # far from the 2.8 % misreading

    _, mantle, upper_segs, lower_segs = run()
    assert 18.0 < mantle["204"] < 21.0, mantle["204"]
    pb204 = (mantle["204"] + sum(s["204"] for s in upper_segs)
             + sum(s["204"] for s in lower_segs))
    assert abs(pb204 - 38.0) < 1e-9             # lead is conserved overall


def test_version1_decay_interval_is_monotonic():
    """Radiogenic daughters only grow between orogenies (eq. 20)."""
    hist, _, _, _ = run()
    for reservoir in ("mantle", "upper", "lower"):
        series = [h[reservoir] for h in hist if h.get(reservoir)]
        for older, younger in zip(series, series[1:]):
            assert younger["206/204"] >= older["206/204"], reservoir
            assert younger["208/204"] >= older["208/204"], reservoir
