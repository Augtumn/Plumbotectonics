# Initial Pb isotope ratios are defined below the module docstring.
# -*- coding: utf-8 -*-
"""Version IV plumbotectonics model (Haines & Zartman, 1988).

References:
    Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series
    200 BASIC language program for version IV of plumbotectonics (Open-File
    Report 88-269). U.S. Geological Survey.
    https://doi.org/10.3133/ofr88269

    Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb
    isotopic systematics among major terrestrial reservoirs - a case for
    bi-directional transport. Geochimica et Cosmochimica Acta, 52(6),
    1327-1339. https://doi.org/10.1016/0016-7037(88)90204-9

    The bi-directional transport implemented by the gates is described in
    the second reference.

Implementation notes:
    The reservoir state is a NumPy array ``M[h, i, k, j]`` and every per-cycle
    stage is applied to whole slices, so the loops that used to run over the
    isotope channels (6) and the crustal segments (up to 46) are gone.  The
    public return value is unchanged: plain dicts keyed 1-6.
"""
import numpy as np

# Initial 206Pb/204Pb, 207Pb/204Pb, 208Pb/204Pb (calibrated to Table 4).
INIT_RATIOS = (9.0668, 9.9367, 28.6528)

CYCLES = 46

# ---- constants ----
A2 = 0.2
A3 = 0.05
B1 = 1.0
B2 = 0.01
B3 = 0.0
Bs = 0.001
H0 = 35.0 / Bs
L1 = 0.155125   # 238U per Ga
L2 = 0.98485    # 235U per Ga
L3 = 0.049475   # 232Th per Ga
U8U5 = 137.88

# ---- time-dependent arrays (1-based, index 1..46) ----
# From Table 3 continued; OCR-corrected.
A1 = np.zeros(47)
A4 = np.zeros(47)
A6 = np.zeros(47)
U  = np.zeros(47)
L  = np.zeros(47)
S  = np.zeros(47)
raw = [
(1,0.000000,1.000000,1.000000,0.000000,0.000000,0.000000),
(2,0.000000,1.000000,1.000000,0.000000,0.000000,0.000000),
(3,0.000000,1.000000,1.000000,0.000000,0.000000,0.000000),
(4,0.071909,1.000000,1.000000,0.172570,0.172570,0.295844),
(5,0.133802,1.000000,1.000000,0.321103,0.321103,0.550483),
(6,0.185972,0.500000,0.500000,0.446301,0.446301,0.765115),
(7,0.228708,0.250000,0.250000,0.548863,0.548863,0.940941),
(8,0.262305,0.125000,0.125000,0.529489,0.629489,1.079162),
(9,0.287052,0.062500,0.062500,0.688879,0.688879,1.180977),
(10,0.303243,0.026195,0.026195,0.727733,0.727733,1.247587),
(11,0.311168,0.026880,0.026880,0.746752,0.746752,1.280192),
(12,0.311119,0.026876,0.026876,0.746635,0.746635,1.279992),
(13,0.303389,0.026208,0.026208,0.728083,0.728083,1.248187),
(14,0.292012,0.025225,0.025225,0.700780,0.700780,1.201380),
(15,0.280829,0.024259,0.024259,0.673944,0.673944,1.155373),
(16,0.273487,0.023625,0.023625,0.656325,0.656325,1.125169),
(17,0.305820,0.026418,0.026418,0.733917,0.733917,1.258189),
(18,0.408165,0.035259,0.035259,0.979529,0.979529,1.679252),
(19,0.402574,0.034776,0.034776,0.966110,0.966110,1.656248),
(20,0.362462,0.031311,0.031311,0.869849,0.869849,1.491224),
(21,0.323323,0.027930,0.027930,0.775922,0.775922,1.330199),
(22,0.268382,0.023184,0.023184,0.644374,0.644374,1.104166),
(23,0.224819,0.019421,0.019421,0.533528,0.539525,0.924939),
(24,0.214998,0.018572,0.018572,0.515959,0.515959,0.884533),
(25,0.202162,0.017464,0.017464,0.485155,0.485155,0.831725),
(26,0.211740,0.018291,0.018291,0.508141,0.508141,0.871131),
(27,0.326726,0.028224,0.028224,0.784090,0.784090,1.344202),
(28,0.367567,0.031752,0.031752,0.882101,0.882101,1.512227),
(29,0.315516,0.027342,0.027342,0.759587,0.759587,1.302195),
(30,0.252095,0.021777,0.021777,0.604986,0.604986,1.037156),
(31,0.175032,0.015120,0.015120,0.420048,0.420048,0.720108),
(32,0.223749,0.019328,0.019328,0.536961,0.536961,0.920538),
(33,0.156378,0.014372,0.014372,0.399279,0.399279,0.684503),
(34,0.180137,0.015561,0.015561,0.432299,0.432299,0.741111),
(35,0.196036,0.016934,0.016934,0.470454,0.470454,0.806521),
(36,0.168468,0.014553,0.014553,0.404296,0.404296,0.693104),
(37,0.136525,0.011794,0.011794,0.327637,0.327637,0.561684),
(38,0.128843,0.011130,0.011130,0.309202,0.309202,0.530080),
(39,0.136525,0.011794,0.011794,0.327637,0.327637,0.561684),
(40,0.143818,0.012424,0.012424,0.345139,0.345139,0.591689),
(41,0.121550,0.010500,0.010500,0.291700,0.291700,0.500075),
(42,0.171531,0.014818,0.014818,0.411647,0.411647,0.705706),
(43,0.175032,0.015120,0.015120,0.420048,0.420048,0.720108),
(44,0.125683,0.010857,0.010857,0.301618,0.301618,0.517078),
(45,0.165502,0.014297,0.014297,0.397179,0.397179,0.680902),
(46,0.153153,0.013230,0.013230,0.367542,0.367542,0.630095),
]
for row in raw:
    k,a1,a4,a6,u,l,s = row
    A1[k]=a1; A4[k]=a4; A6[k]=a6; U[k]=u; L[k]=l; S[k]=s
A5 = A4.copy()

# ---- enrichment / partition factors ----
# index 1..6 = 204Pb,206Pb,207Pb,208Pb,232Th,238U
# Calibrated to Table 4 (self-consistent lower 238U/204Pb = 6.4903)
E_a2 = np.array([0, 80.1163, 80.0180, 75.6413, 80.2321, 100.1054, 99.7985])
F_a3 = np.array([0, 0.9999, 0.9747, 1.0124, 0.9978, 0.6703, 1.5001])
E_b1 = np.array([0, 39.9639, 39.4098, 40.3787, 39.8434, 46.9730, 51.9191])
E_b2 = np.array([0, 25.3182, 25.1701, 24.5545, 25.2987, 25.2917, 27.3127])
E_b3 = np.array([0, 45.6522, 18.4469, 97.7187, 7.8987, 43.7810, 27.5290])
F_c3 = np.array([0, 3.6863, 3.6657, 3.6866, 3.6840, 4.0189, 6.2817])
E_up = np.ones(7)
E_low = np.ones(7)
E_sub = np.ones(7)

# the six isotope channels, as a slice of the h axis
ISO = slice(1, 7)


def FNEmoles(N, Mass1, Mass2, Bias):
    """HP BASIC FNEnoles: normalize moles according to enrichment bias.

    From the BASIC listing:
        Bang = Bias / (1 + Bias)
        Denom = Mass1*Bang + Mass2*(1-Bang)
        IF Denom=0 THEN RETURN 0
        Moles = N*Mass1*Bang/Denom

    Works elementwise, so the whole isotope axis can be passed at once.  The
    two guards of the BASIC listing are applied with a mask rather than a
    branch; they return 0 exactly as before.
    """
    N = np.asarray(N, dtype=float)
    Bias = np.asarray(Bias, dtype=float)
    Mass1 = np.asarray(Mass1, dtype=float)
    Mass2 = np.asarray(Mass2, dtype=float)
    Bang = Bias / (1.0 + Bias)
    Denom = Mass1 * Bang + Mass2 * (1.0 - Bang)
    ok = (Bias > 0) & (Denom != 0)
    out = np.zeros(np.broadcast(N, Bang, Denom).shape)
    np.divide(N * Mass1 * Bang, Denom, out=out, where=ok)
    return out


def _res_dict(vec):
    """{1..6: value} -- the dict shape the rest of the project expects."""
    return {h: float(vec[h - 1]) for h in range(1, 7)}


def run(dp=0.14, double_eroded=False):
    # M[h, i, k, j]: h = 0 mass, 1..6 = 204Pb,206Pb,207Pb,208Pb,232Th,238U;
    #                i = 1 start of cycle, 2 end of cycle; k = 1..CYCLES+1;
    #                j = 0 mantle, 1 upper crust, 2 lower crust, 3 subcrustal
    M = np.zeros((7, 3, CYCLES + 2, 4))
    # initial mantle mass and element abundances
    M[0, 1, 1, 0] = 1050.0
    M[1, 1, 1, 0] = 19.0
    M[2, 1, 1, 0] = 19.0 * INIT_RATIOS[0]
    M[3, 1, 1, 0] = 19.0 * INIT_RATIOS[1]
    M[4, 1, 1, 0] = 19.0 * INIT_RATIOS[2]
    M[5, 1, 1, 0] = 758.0
    M[6, 1, 1, 0] = 177.0

    U_eroded = np.zeros(CYCLES + 2)
    history = []

    for k in range(1, CYCLES + 1):
        seg = slice(1, k)          # the older crustal segments, 1..k-1
        # ---------------- mass ----------------
        m_u = M[0, 1, seg, 1]
        V0 = np.zeros(CYCLES + 2)
        nz = m_u != 0
        V0[1:k][nz] = (m_u[nz] - U_eroded[seg][nz] / H0) / m_u[nz]
        v0 = V0[seg]
        Uv = m_u * v0 * A3
        Uh = m_u * (v0 * A4[k] * (1.0 - A3) + (1.0 - v0) * A4[k])
        U_eroded[seg] = U_eroded[seg] * (1.0 - A4[k])
        M[0, 2, seg, 1] = m_u - Uv - Uh
        Vert = Uv.sum()
        U_hz = Uh.sum()

        m_l = M[0, 1, seg, 2]
        Lh = m_l * A5[k]
        M[0, 2, seg, 2] = m_l - Lh
        L_hz = Lh.sum()

        Outboard = dp * Vert
        Inboard = (1.0 - dp) * Vert
        Hz = U_hz + L_hz
        P_oro = Inboard + Hz

        m_s = M[0, 1, seg, 3]
        Sh = m_s * A6[k]
        Sub_re = Sh.sum()
        M[0, 2, seg, 3] = m_s - Sh

        Mantle = M[0, 1, k, 0] * A1[k]
        Mor = A2 * Mantle
        Rmor = (1.0 - A2) * Mantle
        D0_oro0 = Mor + Outboard
        Gateb3 = B3 * (U[k] + L[k] - P_oro)
        Gateb2 = B2 * S[k] + Gateb3
        D0_oro1 = D0_oro0 - Gateb2
        Gateb1 = B1 * (U[k] + L[k] - P_oro)
        D0_oro2 = D0_oro1 - Gateb1
        Sub_mant = S[k] - Sub_re - Gateb2 + Gateb3
        W0_oro0 = Sub_re + Sub_mant
        W0_oro1 = W0_oro0 + Gateb2
        W0_oro2 = W0_oro1 - Gateb3
        P0_oro1 = P_oro + Gateb1 + Gateb3
        M[0, 2, k, 0] = M[0, 1, k, 0] - Mantle + D0_oro2 - Sub_mant + Rmor
        M[0, 2, k, 1] = U[k]
        M[0, 2, k, 2] = L[k]
        M[0, 2, k, 3] = S[k]

        # ---------------- isotopes ----------------
        # Every stage below is the same algebra as the original per-isotope
        # loop, applied to the whole (6, k-1) slice at once.
        e_up = E_up[1:7][:, None]
        e_low = E_low[1:7][:, None]
        e_sub = E_sub[1:7][:, None]

        m_iu = M[ISO, 1, seg, 1]
        Uv_h = m_iu * v0 * A3 * e_up
        Uh_h = m_iu * (v0 * A4[k] * (1.0 - A3) + (1.0 - v0) * A4[k]) * e_up
        if double_eroded:
            # Kept bug-for-bug with the loop this replaces: the flag sat inside
            # both the isotope loop and the segment loop, so it multiplied
            # U_eroded by (1 - A4[k]) 6*(k-1) times per cycle on top of the
            # once already applied above.  Repeated multiplication, not a
            # power, so the result stays bit-identical.
            for _ in range(6 * (k - 1)):
                U_eroded[seg] = U_eroded[seg] * (1.0 - A4[k])
        M[ISO, 2, seg, 1] = m_iu - Uv_h - Uh_h
        Vert_h = Uv_h.sum(axis=1)
        U_hz_h = Uh_h.sum(axis=1)

        m_il = M[ISO, 1, seg, 2]
        Lh_h = m_il * A5[k] * e_low
        M[ISO, 2, seg, 2] = m_il - Lh_h
        L_hz_h = Lh_h.sum(axis=1)

        m_is = M[ISO, 1, seg, 3]
        Sh_h = m_is * A6[k] * e_sub
        M[ISO, 2, seg, 3] = m_is - Sh_h
        Sub_re_h = Sh_h.sum(axis=1)

        Hz_h = U_hz_h + L_hz_h
        Outboard_h = FNEmoles(Vert_h, Outboard, Inboard, F_a3[1:7])
        Inboard_h = Vert_h - Outboard_h
        P_oro_h0 = Inboard_h + Hz_h
        Mantle_h = M[ISO, 1, k, 0] * A1[k]
        Mor_h = FNEmoles(Mantle_h, Mor, Rmor, E_a2[1:7])
        Rmor_h = Mantle_h - Mor_h
        D_oro_h0 = Mor_h + Outboard_h
        Gateb2_h = FNEmoles(D_oro_h0, Gateb2, D0_oro1, E_b2[1:7])
        D_oro_h1 = D_oro_h0 - Gateb2_h
        Gateb1_h = FNEmoles(D_oro_h1, Gateb1, D0_oro2, E_b1[1:7])
        D_oro_h2 = D_oro_h1 - Gateb1_h
        denom = M[0, 1, k, 0] - Mor
        if denom != 0:
            Sub_mant_h = (Sub_mant / denom) * (M[ISO, 1, k, 0] - Mor_h)
        else:
            Sub_mant_h = np.zeros(6)
        W_oro_h0 = Sub_re_h + Sub_mant_h
        W_oro_h1 = W_oro_h0 + Gateb2_h
        Gateb3_h = FNEmoles(W_oro_h1, Gateb3, W0_oro2, E_b3[1:7])
        W_oro_h2 = W_oro_h1 - Gateb3_h
        P_oro_h1 = P_oro_h0 + Gateb1_h + Gateb3_h
        # Total orogene moles = distal + proximal + wedge.
        oro_moles = D_oro_h2 + P_oro_h1 + W_oro_h2
        M[ISO, 2, k, 1] = FNEmoles(P_oro_h1, U[k], L[k], F_c3[1:7])
        M[ISO, 2, k, 2] = P_oro_h1 - M[ISO, 2, k, 1]
        M[ISO, 2, k, 3] = W_oro_h2
        M[ISO, 2, k, 0] = M[ISO, 1, k, 0] - Mantle_h + D_oro_h2 - Sub_mant_h + Rmor_h

        # ---------------- increment / decay ----------------
        # integer tenths: 4.5 ... 0.0 without binary-float drift
        T = (45 - (k - 1)) / 10       # end of the interval
        T_0 = (44 - (k - 1)) / 10     # start of the interval
        g238 = np.exp(L1 * T) - np.exp(L1 * T_0)
        g235 = np.exp(L2 * T) - np.exp(L2 * T_0)
        g232 = np.exp(L3 * T) - np.exp(L3 * T_0)
        # mantle next cycle
        M[0, 1, k+1, 0] = M[0, 2, k, 0]
        M[1, 1, k+1, 0] = M[1, 2, k, 0]
        M[5, 1, k+1, 0] = M[5, 2, k, 0]
        M[6, 1, k+1, 0] = M[6, 2, k, 0]
        M[2, 1, k+1, 0] = M[2, 2, k, 0] + M[6, 2, k, 0] * g238
        M[3, 1, k+1, 0] = M[3, 2, k, 0] + (M[6, 2, k, 0] / U8U5) * g235
        M[4, 1, k+1, 0] = M[4, 2, k, 0] + M[5, 2, k, 0] * g232
        # crustal segments 1..k, all four reservoirs in one shot
        live = slice(1, k + 1)
        M[0, 1, live, :] = M[0, 2, live, :]
        M[1, 1, live, :] = M[1, 2, live, :]
        M[5, 1, live, :] = M[5, 2, live, :]
        M[6, 1, live, :] = M[6, 2, live, :]
        M[2, 1, live, :] = M[2, 2, live, :] + M[6, 2, live, :] * g238
        M[3, 1, live, :] = M[3, 2, live, :] + (M[6, 2, live, :] / U8U5) * g235
        M[4, 1, live, :] = M[4, 2, live, :] + M[5, 2, live, :] * g232

        def _sum_res(j):
            return _res_dict(M[ISO, 1, live, j].sum(axis=1))

        history.append({
            'cycle': k,
            'time_Ga': max(0.0, T_0),
            'mantle': ratios(_res_dict(M[ISO, 1, k+1, 0])),
            'upper': ratios(_sum_res(1)),
            'lower': ratios(_sum_res(2)),
            'sub': ratios(_sum_res(3)),
            'orogene': ratios(_res_dict(oro_moles)),
        })

    # final state
    everything = slice(1, CYCLES + 1)
    mantle = _res_dict(M[ISO, 1, CYCLES+1, 0])
    upper = _res_dict(M[ISO, 1, everything, 1].sum(axis=1))
    lower = _res_dict(M[ISO, 1, everything, 2].sum(axis=1))
    sub = _res_dict(M[ISO, 1, everything, 3].sum(axis=1))
    total = {h: mantle[h] + upper[h] + lower[h] + sub[h] for h in range(1, 7)}
    masses = {
        'mantle': float(M[0, 1, CYCLES+1, 0]),
        'upper': float(M[0, 1, everything, 1].sum()),
        'lower': float(M[0, 1, everything, 2].sum()),
        'sub': float(M[0, 1, everything, 3].sum()),
    }
    masses['total'] = masses['mantle'] + masses['upper'] + masses['lower'] + masses['sub']
    last_upper = _res_dict(M[ISO, 1, CYCLES, 1])
    last_lower = _res_dict(M[ISO, 1, CYCLES, 2])
    last_sub = _res_dict(M[ISO, 1, CYCLES, 3])
    return dict(mantle=mantle, upper=upper, lower=lower, sub=sub, total=total, masses=masses, last_upper=last_upper, last_lower=last_lower, last_sub=last_sub, history=history)

def ratios(d):
    """Return Pb/U/Th ratios; use None for empty reservoirs."""
    out = {}
    out['206/204'] = d[2]/d[1] if d.get(1,0) else None
    out['207/204'] = d[3]/d[1] if d.get(1,0) else None
    out['208/204'] = d[4]/d[1] if d.get(1,0) else None
    out['238U/204Pb'] = d[6]/d[1] if d.get(1,0) else None
    out['232Th/238U'] = d[5]/d[6] if d.get(6,0) else None
    out['232Th/204Pb'] = d[5]/d[1] if d.get(1,0) else None
    return out

if __name__ == '__main__':
    for dp in [0.14, 0.11]:
        for de in [False, True]:
            res = run(dp=dp, double_eroded=de)
            print('='*70)
            print(f'Dp={dp}  double_eroded={de}')
            for name in ['mantle','upper','lower','sub','total']:
                print(f'{name:>6}:', {k: round(v,4) for k,v in ratios(res[name]).items()})
