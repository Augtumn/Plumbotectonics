# -*- coding: utf-8 -*-
"""Continental-crust Pb isotope evolution model for China (Li et al., 2001).

Reference
---------
Li Long, Zheng Yongfei and Zhou Jianbo (2001). Dynamic model for Pb isotope
evolution in the continental crust of China. *Acta Petrologica Sinica*,
17(1), 61-68.  (李龙, 郑永飞, 周建波. 中国大陆地壳铅同位素演化的动力学模型.
岩石学报 17(1): 61-68)

What comes from the paper
-------------------------
* three reservoirs -- upper mantle (topmost 500 km), upper crust, lower crust;
* 11 orogenies, the first at 4.0 Ga and then every 0.4 Ga, each instantaneous;
* the two retention factors of eq. (2): ``P_UPPER = 0.63`` and
  ``P_LOWER = 0.95``, so the eroded fractions are 0.37 and 0.05;
* enrichment factors ``E_m = 4`` and ``E_u = E_l = 1`` (eq. 5);
* 90 % of the residual orogene returns to the mantle (eqs. 7-8); the other
  10 % "remains at the crustal margin or is eroded to become sedimentary
  rock" (assumption 3d) and is therefore added to the UPPER crust as its own
  layer.  Discarding it instead loses about 2.5 % of the system mass over the
  run and breaks mass balance;
* the starting Pb isotope ratios of Table 1 (10.17 / 12.07 / 30.56) and the
  partitioning ratios of Table 2;
* decay of the parents between orogenies (eqs. 9-10).

What is inherited from Zartman & Doe (1981)
-------------------------------------------
The paper states that its algorithm is Zartman & Doe's and defers to it for the
parameters it does not print: the 4.0 Ga element abundances (204Pb 38,
238U 349, 232Th 1335 per 1e15 mol), the masses (mantle 800, new upper and lower
crust 2.6 each per 1e24 g), the decay constants, 238U/235U = 137.88, the
mantle-contribution series k_i, and the enrichment convention.  With these the
model has no tuned parameters.

Two physical caveats worth knowing
----------------------------------
1. **E_m = 4 against a falling f_m.**  The paper explains E_m = 4 as "25 %
   melting of the average mantle with all the melt entering the orogene",
   while ``K_MANTLE`` falls from 1/8 to 1/128.  A melt fraction F carrying a
   perfectly incompatible element (D = 0) would have E = 1/F, i.e. 8 at
   f_m = 1/8 and 128 at f_m = 1/128.  Fixing E at 4 is Zartman & Doe's
   simplification, not a batch-melting result.  ``melt_model="batch"`` gives
   E = 1/f_m instead; the default keeps the published convention.

2. **The two decay parameterisations.**  ``decay_parents=False`` (default)
   follows Zartman & Doe: the parents sit at their modern-equivalent abundance,
   the daughters grow as ``e^{lt} - e^{lt'}``, and 207Pb is fed by
   238U/137.88, so 235U is never carried as a species.  ``decay_parents=True``
   follows the paper's eqs. (9)-(10): the parents really decay, 235U is carried
   separately (4.0 Ga 238U/235U = 4.9897, i.e. 27.6x today's), and the starting
   abundances are the ACTUAL 4.0 Ga values obtained by back-correcting
   Zartman & Doe's.  The two produce identical Pb ratios (agreement ~1e-14);
   only the second has a literal 235U budget.

Known limitations (inherited from the framework, not bugs)
----------------------------------------------------------
* Pb is treated as a refractory element: only the partitioning ratios separate
  it from U and Th, and no distinction is made between its behaviour during
  partial melting and during orogene differentiation.
* The mantle is a single well-mixed reservoir, so each orogeny implicitly
  assumes convective homogenisation within the 0.4 Ga between orogenies.
* The orogene is homogenised instantaneously (the paper's assumption 3a).

Accuracy against the paper (no tuned parameters)
------------------------------------------------
Table 4 (present-day 238U/204Pb and Th/U): worst absolute deviation 0.47.
Table 3 (99 growth-curve values): worst 0.62, mean 0.22, RMSE 0.27, and 12 of
99 values inside the table's printed precision of +-0.005.  The table is NOT
reproduced; see ``docs/validation.md`` for the residual structure, the internal
inconsistencies found in the paper, and the inversion result showing that
Tables 3 and 4 demand incompatible crustal masses.
"""
import numpy as np

# ---- Table 1: starting conditions of the mantle at 4.0 Ga ----
R2060, R2070, R2080 = 10.17, 12.07, 30.56

# ---- inherited from Zartman & Doe (1981), Table II ----
PB2040 = 38.0
U2380 = 349.0
TH2320 = 1335.0
MASS0 = 800.0
NEW_U = 2.6
NEW_L = 2.6

L238 = 0.155125
L235 = 0.98485
L232 = 0.049475
U8U5 = 137.88

CYCLES = 11
DT = 0.4
K_MANTLE = (1/8, 1/16, 1/32, 1/64) + (1/128,) * 7

# ---- eq. (2): retention factors ----
P_UPPER = 0.63
P_LOWER = 0.95
ERO_U = 1.0 - P_UPPER     # 0.37
ERO_L = 1.0 - P_LOWER     # 0.05

# ---- eq. (5): enrichment factors ----
E_M, E_U, E_L = 4.0, 1.0, 1.0

# ---- eqs. (7)-(8): fraction of the residual orogene returning to the mantle ----
RETURN = 0.9

# ---- Table 2 partitioning ratios, restated in Zartman & Doe's column order ----
# The paper prints (mantle, LOWER crust, UPPER crust), the opposite of
# Zartman & Doe Table II, so the upper- and lower-crust entries are swapped here
# relative to the printed table.
F_PB = (0.038, 0.727, 0.235)
F_U = (0.024, 0.865, 0.111)
F_TH = (0.021, 0.817, 0.162)

ISO_KEYS = ("204", "206", "207", "208", "232", "238", "235")
_I204, _I206, _I207, _I208, _I232, _I238, _I235 = range(7)
_F_RET = np.array([F_PB[0]] * 4 + [F_TH[0], F_U[0], F_U[0]])
_F_UP = np.array([F_PB[1]] * 4 + [F_TH[1], F_U[1], F_U[1]])
_F_LOW = np.array([F_PB[2]] * 4 + [F_TH[2], F_U[2], F_U[2]])

# 4.0 Ga 238U/235U such that it reaches today's 137.88
U8U5_0 = U8U5 * np.exp(-(L235 - L238) * 4.0)
U2380_ACTUAL = U2380 * np.exp(L238 * 4.0)
TH2320_ACTUAL = TH2320 * np.exp(L232 * 4.0)


def e_mantle(f_m, melt_model="zd1981"):
    """Enrichment factor of the material the mantle contributes.

    ``"zd1981"`` keeps the published constant E_m = 4.  ``"batch"`` uses the
    batch-melting value for a perfectly incompatible element, E = 1/f_m.
    """
    if melt_model == "zd1981":
        return E_M
    if melt_model == "batch":
        return 1.0 / f_m
    raise ValueError(f"unknown melt_model {melt_model!r}")


def ratios(res):
    """{'206/204', '207/204', '208/204'} of a reservoir row or dict."""
    pb204 = res[_I204] if isinstance(res, np.ndarray) else res["204"]
    if pb204 == 0:
        return None
    get = (lambda i, k: res[i]) if isinstance(res, np.ndarray) else (lambda i, k: res[k])
    return {"206/204": get(_I206, "206") / pb204,
            "207/204": get(_I207, "207") / pb204,
            "208/204": get(_I208, "208") / pb204}


def row_to_dict(row, mass):
    out = {"mass": float(mass)}
    for key, value in zip(ISO_KEYS, row):
        out[key] = float(value)
    return out


def _bulk(rows):
    """Bulk composition of a stack of layers: the ratio of summed amounts.

    A reservoir's Pb isotope ratio is Sum(N_i)/Sum(N_204), NOT a mass-weighted
    average of the individual ratios -- ratios are not additive quantities.
    """
    return None if len(rows) == 0 else ratios(rows.sum(axis=0))


def _initial_row(decay_parents):
    if decay_parents:
        u238, th232, u235 = U2380_ACTUAL, TH2320_ACTUAL, U2380_ACTUAL / U8U5_0
    else:
        u238, th232, u235 = U2380, TH2320, 0.0
    return np.array([PB2040, PB2040 * R2060, PB2040 * R2070, PB2040 * R2080,
                     th232, u238, u235], dtype=float)


def _as_row(res):
    """Accept either a length-7 array or one of the dicts run() returns."""
    if isinstance(res, np.ndarray):
        return res
    return np.array([res[k] for k in ISO_KEYS], dtype=float)


def _inventory(mantle, upper, lower):
    """Total moles of each species over the whole system."""
    total = np.zeros(7)
    for row in [mantle] + list(upper) + list(lower):
        total = total + _as_row(row)
    return total


def check_conservation(mantle, upper, lower, decay_parents=False, rtol=1e-9):
    """Assert that the run conserved what it must.

    204Pb is conserved in both parameterisations.  Under Zartman & Doe's
    constant-parent convention so are 238U and 232Th, because the parents are
    held at their modern-equivalent abundance by construction.  In the
    decaying-parent parameterisation 238U instead falls to 349 = 649 x
    e^{-lambda*4 Ga}, which is exactly today's value, so what is conserved is
    the daughter-plus-parent sum: 206Pb + 238U, 207Pb + 235U, 208Pb + 232Th.

    Returns the relative deviations, raising AssertionError if any exceeds
    ``rtol``.
    """
    start = _initial_row(decay_parents)
    end = _inventory(mantle, upper, lower)
    if decay_parents:
        pairs = [(_I204, None), (_I206, _I238), (_I207, _I235), (_I208, _I232)]
    else:
        pairs = [(_I204, None), (_I238, None), (_I232, None)]
    dev = {}
    for daughter, parent in pairs:
        want = start[daughter] + (start[parent] if parent is not None else 0.0)
        got = end[daughter] + (end[parent] if parent is not None else 0.0)
        rel = abs(got - want) / want
        label = ISO_KEYS[daughter] + (f"+{ISO_KEYS[parent]}" if parent is not None else "")
        dev[label] = rel
        assert rel < rtol, (
            f"{label} not conserved: got {got:.6f}, want {want:.6f} "
            f"(relative deviation {rel:.3e})")
    return dev


def run(decay_parents=False, melt_model="zd1981", strict=True):
    """Run the 11 orogenies.

    ``decay_parents`` selects between Zartman & Doe's constant-parent
    convention (default) and the paper's decaying-parent eqs. (9)-(10);
    ``melt_model`` between the published E_m = 4 and batch melting.  With
    ``strict`` the element inventory is asserted at the end.
    """
    mantle = _initial_row(decay_parents)
    mantle_mass = MASS0
    upper = np.zeros((0, 7))
    upper_mass = np.zeros(0)
    lower = np.zeros((0, 7))
    lower_mass = np.zeros(0)
    history = []
    times = [((40 - 4 * i) / 10, K_MANTLE[i]) for i in range(CYCLES)]

    for j, (t, f_m) in enumerate(times):
        history.append({"t": t, "mantle": ratios(mantle), "orogene": None,
                        "upper": _bulk(upper), "lower": _bulk(lower)})

        # --- eqs. (1)-(2): masses contributed to the orogene ---
        dm = mantle_mass * f_m
        du = upper_mass * ERO_U
        dl = lower_mass * ERO_L
        d_or = dm + du.sum() + dl.sum()

        # --- eq. (5): elements entering the orogene ---
        # The material the mantle gives up has a concentration E_m times its
        # own -- which is what partial melting does: a small mass fraction
        # carries a large incompatible-element fraction.  The mantle therefore
        # loses f_m*E_m*N_m, exactly what the orogene receives.  Losing only
        # f_m*N_m while the orogene still received f_m*E_m*N_m would create
        # (E_m-1)*f_m*N_m of every element each cycle.
        e_m = e_mantle(f_m, melt_model)
        inc = mantle * (f_m * e_m)
        if len(upper):
            inc = inc + (upper * (du / upper_mass)[:, None] * E_U).sum(axis=0)
        if len(lower):
            inc = inc + (lower * (dl / lower_mass)[:, None] * E_L).sum(axis=0)
        history[-1]["orogene"] = ratios(inc)

        # --- eqs. (5b)-(6): mass-weighted redistribution ---
        # The first weight is the RESIDUAL orogene mass, which is how the paper
        # glosses dM_o^t.  It is also the only choice that keeps the mass and
        # element apportionments on the same basis.
        m_ret = d_or - NEW_U - NEW_L
        s = m_ret * _F_RET + NEW_U * _F_UP + NEW_L * _F_LOW
        if np.all(s > 0):
            ret_m = inc * (m_ret * _F_RET) / s
            new_u = inc * (NEW_U * _F_UP) / s
            new_l = inc * (NEW_L * _F_LOW) / s
        else:   # degenerate parameters only
            safe = np.where(s > 0, s, 1.0)
            keep = s > 0
            ret_m = np.where(keep, inc * (m_ret * _F_RET) / safe, 0.0)
            new_u = np.where(keep, inc * (NEW_U * _F_UP) / safe, 0.0)
            new_l = np.where(keep, inc * (NEW_L * _F_LOW) / safe, 0.0)

        # --- eqs. (7)-(8) and assumption (3d) ---
        # 90 % of the residual returns to the mantle; the other 10 % becomes
        # sediment at the crustal margin and joins the UPPER crust.
        m_back = RETURN * m_ret
        left_mass = (1.0 - RETURN) * m_ret
        left_elems = (1.0 - RETURN) * ret_m

        mantle_mass = mantle_mass - dm + m_back
        mantle = mantle - mantle * (f_m * e_m) + RETURN * ret_m
        upper = upper * (1 - ERO_U)
        upper_mass = upper_mass * (1 - ERO_U)
        lower = lower * (1 - ERO_L)
        lower_mass = lower_mass * (1 - ERO_L)
        upper = np.vstack([upper, new_u])
        upper_mass = np.append(upper_mass, NEW_U)
        lower = np.vstack([lower, new_l])
        lower_mass = np.append(lower_mass, NEW_L)
        if left_mass > 0:
            upper = np.vstack([upper, left_elems])
            upper_mass = np.append(upper_mass, left_mass)

        # --- eqs. (9)-(10), or Zartman & Doe's equivalent ---
        if j < CYCLES - 1:
            if decay_parents:
                d238 = 1.0 - np.exp(-L238 * DT)
                d235 = 1.0 - np.exp(-L235 * DT)
                d232 = 1.0 - np.exp(-L232 * DT)

                def decay(res):
                    u8 = res[..., _I238].copy()
                    u5 = res[..., _I235].copy()
                    th = res[..., _I232].copy()
                    res[..., _I206] += u8 * d238
                    res[..., _I207] += u5 * d235
                    res[..., _I208] += th * d232
                    res[..., _I238] = u8 * np.exp(-L238 * DT)
                    res[..., _I235] = u5 * np.exp(-L235 * DT)
                    res[..., _I232] = th * np.exp(-L232 * DT)
            else:
                t_next = times[j + 1][0]
                g238 = np.exp(L238 * t) - np.exp(L238 * t_next)
                g235 = np.exp(L235 * t) - np.exp(L235 * t_next)
                g232 = np.exp(L232 * t) - np.exp(L232 * t_next)

                def decay(res):
                    res[..., _I206] += res[..., _I238] * g238
                    res[..., _I207] += (res[..., _I238] / U8U5) * g235
                    res[..., _I208] += res[..., _I232] * g232

            decay(mantle)
            if len(upper):
                decay(upper)
            if len(lower):
                decay(lower)

    if strict:
        check_conservation(mantle, upper, lower, decay_parents)

    return history, row_to_dict(mantle, mantle_mass), \
        [row_to_dict(r, m) for r, m in zip(upper, upper_mass)], \
        [row_to_dict(r, m) for r, m in zip(lower, lower_mass)]


def present_day(mantle, upper_segs, lower_segs):
    """Table 4 quantities: 238U/204Pb and Th/U for the three reservoirs."""
    out = {}
    for name, segs in (("mantle", [mantle]), ("upper", upper_segs), ("lower", lower_segs)):
        pb = sum(s["204"] for s in segs)
        uu = sum(s["238"] for s in segs)
        th = sum(s["232"] for s in segs)
        out[name] = {"238U/204Pb": uu / pb, "Th/U": th / uu}
    return out


if __name__ == "__main__":
    vals = {}
    for melt in ("zd1981", "batch"):
        hist, mant, ups, los = run(melt_model=melt)
        pd_ = present_day(mant, ups, los)
        vals[melt] = (hist, pd_)
    hist, pd_ = vals["zd1981"]
    print("t     Mantle                 Orogene                Upper                  Lower")
    for h in hist:
        def fmt(d):
            return "-" if not d else f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"
        print(f"{h['t']:.1f}  {fmt(h['mantle'])}  {fmt(h['orogene'])}  "
              f"{fmt(h['upper'])}  {fmt(h['lower'])}")
    print()
    print(f"{'model':<8s} {'238U/204Pb m/l/u':<24s} {'Th/U m/l/u':<20s} upper 206/204")
    print(f"{'paper':<8s} {'8.44/5.63/14.98':<24s} {'3.60/5.48/3.47':<20s} 19.86")
    for melt, (h, p) in vals.items():
        print(f"{melt:<8s} "
              f"{p['mantle']['238U/204Pb']:.2f}/{p['lower']['238U/204Pb']:.2f}/"
              f"{p['upper']['238U/204Pb']:.2f}".ljust(24)
              + f"{p['mantle']['Th/U']:.2f}/{p['lower']['Th/U']:.2f}/"
               f"{p['upper']['Th/U']:.2f}".ljust(20)
              + f"{h[10]['upper']['206/204']:.2f}")
    print()
    print("element inventory is asserted inside run(); no violation was raised.")
