# -*- coding: utf-8 -*-
"""Tests for the Li et al. (2001) China model.

The model is checked against:

* the paper's own Table 1 (4.0 Ga initial Pb ratios) and Table 2 (partitioning
  ratios), which it prints, and Table 4 (present-day 238U/204Pb and Th/U);
* mass and element conservation, which is an invariant of the scheme;
* the qualitative ordering the paper's interpretation rests on, namely
  upper crust > mantle > lower crust in 206Pb/204Pb;
* the equivalence of the two decay parameterisations.

Table 3 (the 99 growth-curve values) is deliberately NOT asserted: its
unpublished inputs cannot be recovered, and the model misses it by up to 0.62.
See docs/validation.md.
"""
import numpy as np
import pytest

from plumbotectonics import china

KEYS = ("206/204", "207/204", "208/204")

# Li et al. (2001) Table 3, columns (mantle, lower crust, upper crust)
TABLE3 = [
    (4.0, (10.17, 12.07, 30.56), (10.17, 12.07, 30.56), (10.17, 12.07, 30.56)),
    (3.6, (11.21, 13.20, 31.34), (10.67, 12.62, 31.17), (11.44, 13.45, 31.55)),
    (3.2, (12.18, 13.95, 32.23), (11.54, 13.40, 31.96), (12.55, 14.26, 32.49)),
    (2.8, (13.06, 14.45, 33.01), (12.38, 13.98, 32.77), (13.61, 14.80, 33.44)),
    (2.4, (13.89, 14.78, 33.76), (13.14, 14.36, 33.56), (14.64, 15.16, 34.39)),
    (2.0, (14.66, 15.01, 34.49), (13.86, 14.63, 34.34), (15.66, 15.42, 35.35)),
    (1.6, (15.39, 15.17, 35.20), (14.55, 14.84, 35.11), (16.60, 15.57, 36.27)),
    (1.2, (16.09, 15.28, 35.90), (15.22, 14.99, 35.87), (17.46, 15.66, 37.16)),
    (0.8, (16.73, 15.35, 36.57), (15.87, 15.11, 36.63), (18.33, 15.72, 38.09)),
    (0.4, (17.34, 15.40, 37.23), (16.50, 15.20, 37.39), (19.13, 15.75, 38.98)),
    (0.0, (17.92, 15.44, 37.88), (17.10, 15.27, 38.14), (19.86, 15.75, 39.83)),
]
# Table 4, ordered (mantle, upper crust, lower crust)
TABLE4_U = (8.44, 14.98, 5.63)
TABLE4_TH = (3.60, 3.47, 5.48)


@pytest.fixture(scope="module")
def result():
    return china.run()


def test_table1_initial_ratios(result):
    """Table 1: the 4.0 Ga mantle ratios must come out exactly."""
    hist = result[0]
    assert hist[0]["t"] == 4.0
    got = hist[0]["mantle"]
    assert got["206/204"] == pytest.approx(10.17, abs=1e-12)
    assert got["207/204"] == pytest.approx(12.07, abs=1e-12)
    assert got["208/204"] == pytest.approx(30.56, abs=1e-12)


def test_table2_columns_are_mantle_lower_upper():
    """The paper prints (mantle, LOWER, UPPER); F must be stored swapped."""
    assert china.F_PB[0] < china.F_PB[2] < china.F_PB[1]      # 0.038 < 0.235 < 0.727
    assert china.F_U[0] < china.F_U[2] < china.F_U[1]         # 0.024 < 0.111 < 0.865
    assert china.F_TH[0] < china.F_TH[2] < china.F_TH[1]      # 0.021 < 0.162 < 0.817


def test_table4_present_day(result):
    """Table 4 to within 0.65 on 238U/204Pb and 0.10 on Th/U."""
    pd = china.present_day(*result[1:])
    for name, want_u, want_th in zip(("mantle", "upper", "lower"), TABLE4_U, TABLE4_TH):
        assert pd[name]["238U/204Pb"] == pytest.approx(want_u, abs=0.65)
        assert pd[name]["Th/U"] == pytest.approx(want_th, abs=0.10)


def test_upper_crust_is_most_radiogenic(result):
    """The ordering the whole paper rests on: upper > mantle > lower."""
    hist = result[0]
    last = hist[-1]
    assert last["upper"]["206/204"] > last["mantle"]["206/204"] > last["lower"]["206/204"]


def test_table3_is_not_reproduced_but_is_close(result):
    """Table 3 is NOT reproduced; this pins the size of the gap so that a
    regression cannot silently make it much worse."""
    hist = result[0]
    diffs = []
    for idx, (_t, m_t, l_t, u_t) in enumerate(TABLE3):
        for name, want in (("mantle", m_t), ("lower", l_t), ("upper", u_t)):
            got = hist[idx].get(name) or hist[idx]["orogene"]
            diffs += [got[k] - w for k, w in zip(KEYS, want)]
    diffs = np.array(diffs)
    assert len(diffs) == 99
    assert np.abs(diffs).max() < 0.62
    assert np.abs(diffs).mean() < 0.15


def test_element_inventory_is_conserved():
    """204Pb, 238U and 232Th are conserved exactly under the constant-parent
    convention; check_conservation raises otherwise."""
    hist, mantle, upper, lower = china.run(strict=False)
    dev = china.check_conservation(mantle, upper, lower)
    for key in ("204", "238", "232"):
        assert dev[key] < 1e-12


def test_decaying_parents_conserve_the_daughters_too():
    hist, mantle, upper, lower = china.run(decay_parents=True, strict=False)
    dev = china.check_conservation(mantle, upper, lower, decay_parents=True)
    for key in ("204", "206+238", "207+235", "208+232"):
        assert dev[key] < 1e-12


def test_the_two_decay_parameterisations_agree(result):
    """Zartman & Doe's constant parents and the paper's eqs. (9)-(10) must give
    the same Pb ratios.  (They differ only by ~1e-14, since 206 + 238 is
    conserved in one and 238 alone in the other.)"""
    hist_a = result[0]
    hist_b = china.run(decay_parents=True)[0]
    for a, b in zip(hist_a, hist_b):
        for res in ("mantle", "upper", "lower"):
            if a[res] is None:
                continue
            for key in KEYS:
                assert a[res][key] == pytest.approx(b[res][key], abs=1e-12)


def test_share_model_switch():
    """four_bin is the default; paper reproduces the printed three-term eq. (6).

    The two coincide when everything returns to the mantle, which is the check
    that four_bin really is a strict completion of the printed equation.
    """
    assert china.run(share_model="paper")[0][-1]["upper"]["206/204"] == pytest.approx(
        20.42, abs=0.01)
    assert china.run()[0][-1]["upper"]["206/204"] == pytest.approx(19.90, abs=0.01)
    with pytest.raises(ValueError):
        china.run(share_model="nope")
    # RETURN = 1 makes the fourth bin empty, so the two readings must agree
    four = china.run(share_model="four_bin", strict=False)
    paper = china.run(share_model="paper", strict=False)
    saved = china.RETURN
    try:
        china.RETURN = 1.0
        a = china.run(share_model="four_bin", strict=False)[0]
        b = china.run(share_model="paper", strict=False)[0]
    finally:
        china.RETURN = saved
    for x, y in zip(a, b):
        for res in ("mantle", "upper", "lower"):
            if x[res] is None:
                continue
            for key in KEYS:
                assert x[res][key] == pytest.approx(y[res][key], abs=1e-12)
    del four, paper


def test_batch_melt_switch_changes_the_e_mantle():
    assert china.e_mantle(1 / 8, "zd1981") == 4.0
    assert china.e_mantle(1 / 8, "batch") == 8.0
    assert china.e_mantle(1 / 128, "batch") == 128.0
    with pytest.raises(ValueError):
        china.e_mantle(1 / 8, "nope")


def test_bulk_composition_is_ratio_of_sums():
    """_bulk must be Sum(N)/Sum(N204), not a weighted average of ratios."""
    layer_a = np.array([10.0, 50.0, 60.0, 150.0, 0.0, 0.0, 0.0])
    layer_b = np.array([90.0, 900.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    got = china._bulk(np.vstack([layer_a, layer_b]))
    assert got["206/204"] == pytest.approx(950.0 / 100.0)
    # a mass-weighted average of the ratios would give a different number
    assert got["206/204"] != pytest.approx((1 * 5.0 + 100 * 10.0) / 101)


def test_the_mass_of_the_system_is_constant():
    """No material may be created or destroyed: the 10 % of the residual
    orogene that does not return to the mantle has to land in the crust."""
    _hist, mantle, upper, lower = china.run()
    total = mantle["mass"] + sum(s["mass"] for s in upper) + sum(s["mass"] for s in lower)
    assert total == pytest.approx(china.MASS0, rel=1e-12)
