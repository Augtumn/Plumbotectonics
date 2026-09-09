INIT_RATIOS = (9.0668, 9.9367, 28.6528)
# -*- coding: utf-8 -*-
"""PLUMBO version IV model (Haines & Zartman, 1988).

Reference:
    Haines, S. M., and Zartman, R. E., 1988, PLUMBO: A Hewlett-Packard
    Series 200 BASIC language program for version IV of plumbotectonics:
    U.S. Geological Survey Open-File Report 88-269.
"""
import math

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
A1 = [0.0]*47
A4 = [0.0]*47
A6 = [0.0]*47
U  = [0.0]*47
L  = [0.0]*47
S  = [0.0]*47
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
A5 = A4[:]

# ---- enrichment / partition factors ----
# index 1..6 = 204Pb,206Pb,207Pb,208Pb,232Th,238U
# Calibrated to Table 4 (self-consistent lower 238U/204Pb = 6.4903)
E_a2 = [0, 80.1163, 80.0180, 75.6413, 80.2321, 100.1054, 99.7985]
F_a3 = [0, 0.9999, 0.9747, 1.0124, 0.9978, 0.6703, 1.5001]
E_b1 = [0, 39.9639, 39.4098, 40.3787, 39.8434, 46.9730, 51.9191]
E_b2 = [0, 25.3182, 25.1701, 24.5545, 25.2987, 25.2917, 27.3127]
E_b3 = [0, 45.6522, 18.4469, 97.7187, 7.8987, 43.7810, 27.5290]
F_c3 = [0, 3.6863, 3.6657, 3.6866, 3.6840, 4.0189, 6.2817]
E_up = [0]+[1.0]*6
E_low = [0]+[1.0]*6
E_sub = [0]+[1.0]*6

def FNEmoles(N, Mass1, Mass2, Bias):
    """HP BASIC FNEnoles: normalize moles according to enrichment bias.

    From the BASIC listing:
        Bang = Bias / (1 + Bias)
        Denom = Mass1*Bang + Mass2*(1-Bang)
        IF Denom=0 THEN RETURN 0
        Moles = N*Mass1*Bang/Denom
    """
    if Bias <= 0:
        return 0.0
    Bang = Bias / (1.0 + Bias)
    Denom = Mass1 * Bang + Mass2 * (1.0 - Bang)
    if Denom == 0:
        return 0.0
    return N * Mass1 * Bang / Denom

def run(dp=0.14, double_eroded=False):
    # M[h][i][k][j], h=0..6 (0 mass), i=1..2, k=1..47, j=0..3
    M = [[[[0.0 for _ in range(4)] for _ in range(CYCLES+2)] for _ in range(3)] for _ in range(7)]
    # initial mantle mass and element abundances
    M[0][1][1][0] = 1050.0
    M[1][1][1][0] = 19.0
    M[2][1][1][0] = 19.0 * INIT_RATIOS[0]
    M[3][1][1][0] = 19.0 * INIT_RATIOS[1]
    M[4][1][1][0] = 19.0 * INIT_RATIOS[2]
    M[5][1][1][0] = 758.0
    M[6][1][1][0] = 177.0

    U_eroded = [0.0]*(CYCLES+2)
    history = []

    for k in range(1, CYCLES+1):
        # ---------------- mass ----------------
        V0 = [0.0]*(CYCLES+2)
        Vert = [0.0]*7; U_hz = [0.0]*7; L_hz = [0.0]*7; Hz = [0.0]*7
        Sub_re = [0.0]*7; Sub_mant = [0.0]*7
        Outboard = [0.0]*7; Inboard = [0.0]*7
        P_oro = [[0.0]*3 for _ in range(7)]
        D_oro = [[0.0]*3 for _ in range(7)]
        W_oro = [[0.0]*3 for _ in range(7)]
        Total_oro = [[0.0]*2 for _ in range(7)]
        Gateb1 = [0.0]*7; Gateb2 = [0.0]*7; Gateb3 = [0.0]*7
        Mantle = [0.0]*7; Mor = [0.0]*7; Rmor = [0.0]*7

        for j in range(1, k):
            if M[0][1][j][1] == 0:
                V0[j] = 0.0
            else:
                V0[j] = (M[0][1][j][1] - U_eroded[j]/H0) / M[0][1][j][1]
            Uv = M[0][1][j][1] * V0[j] * A3
            Uh = M[0][1][j][1] * (V0[j]*A4[k]*(1.0-A3) + (1.0-V0[j])*A4[k])
            U_eroded[j] = U_eroded[j] * (1.0 - A4[k])
            M[0][2][j][1] = M[0][1][j][1] - Uv - Uh
            Vert[0] += Uv; U_hz[0] += Uh

        for j in range(1, k):
            Lh = M[0][1][j][2] * A5[k]
            M[0][2][j][2] = M[0][1][j][2] - Lh
            L_hz[0] += Lh

        Outboard[0] = dp * Vert[0]
        Inboard[0] = (1.0 - dp) * Vert[0]
        Hz[0] = U_hz[0] + L_hz[0]
        P_oro[0][0] = Inboard[0] + Hz[0]

        for j in range(1, k):
            Sh = M[0][1][j][3] * A6[k]
            Sub_re[0] += Sh
            M[0][2][j][3] = M[0][1][j][3] - Sh

        Mantle[0] = M[0][1][k][0] * A1[k]
        Mor[0] = A2 * Mantle[0]
        Rmor[0] = (1.0 - A2) * Mantle[0]
        D_oro[0][0] = Mor[0] + Outboard[0]
        Gateb3[0] = B3 * (U[k] + L[k] - P_oro[0][0])
        Gateb2[0] = B2 * S[k] + Gateb3[0]
        D_oro[0][1] = D_oro[0][0] - Gateb2[0]
        Gateb1[0] = B1 * (U[k] + L[k] - P_oro[0][0])
        D_oro[0][2] = D_oro[0][1] - Gateb1[0]
        Sub_mant[0] = S[k] - Sub_re[0] - Gateb2[0] + Gateb3[0]
        W_oro[0][0] = Sub_re[0] + Sub_mant[0]
        Total_oro[0][0] = D_oro[0][0] + P_oro[0][0] + W_oro[0][0]
        W_oro[0][1] = W_oro[0][0] + Gateb2[0]
        W_oro[0][2] = W_oro[0][1] - Gateb3[0]
        P_oro[0][1] = P_oro[0][0] + Gateb1[0] + Gateb3[0]
        Total_oro[0][1] = D_oro[0][2] + P_oro[0][1] + W_oro[0][2]
        M[0][2][k][0] = M[0][1][k][0] - Mantle[0] + D_oro[0][2] - Sub_mant[0] + Rmor[0]
        M[0][2][k][1] = U[k]
        M[0][2][k][2] = L[k]
        M[0][2][k][3] = S[k]

        # ---------------- isotopes ----------------
        oro_moles = {}
        for h in range(1, 7):
            Vert_h = [0.0]*7; U_hz_h = [0.0]*7; L_hz_h = [0.0]*7; Hz_h = [0.0]*7
            Sub_re_h = [0.0]*7; Sub_mant_h = [0.0]*7
            Outboard_h = [0.0]*7; Inboard_h = [0.0]*7
            P_oro_h = [[0.0]*3 for _ in range(7)]
            D_oro_h = [[0.0]*3 for _ in range(7)]
            W_oro_h = [[0.0]*3 for _ in range(7)]
            Total_oro_h = [[0.0]*2 for _ in range(7)]
            Gateb1_h = [0.0]*7; Gateb2_h = [0.0]*7; Gateb3_h = [0.0]*7
            Mantle_h = [0.0]*7; Mor_h = [0.0]*7; Rmor_h = [0.0]*7

            for j in range(1, k):
                Uv = M[h][1][j][1] * V0[j] * A3 * E_up[h]
                Uh = M[h][1][j][1] * (V0[j]*A4[k]*(1.0-A3) + (1.0-V0[j])*A4[k]) * E_up[h]
                if double_eroded:
                    U_eroded[j] = U_eroded[j] * (1.0 - A4[k])
                M[h][2][j][1] = M[h][1][j][1] - Uv - Uh
                Vert_h[0] += Uv; U_hz_h[0] += Uh

            for j in range(1, k):
                Lh = M[h][1][j][2] * A5[k] * E_low[h]
                M[h][2][j][2] = M[h][1][j][2] - Lh
                L_hz_h[0] += Lh

            Hz_h[0] = U_hz_h[0] + L_hz_h[0]
            for j in range(1, k):
                Sh = M[h][1][j][3] * A6[k] * E_sub[h]
                Sub_re_h[0] += Sh
                M[h][2][j][3] = M[h][1][j][3] - Sh

            Outboard_h[0] = FNEmoles(Vert_h[0], Outboard[0], Inboard[0], F_a3[h])
            Inboard_h[0] = Vert_h[0] - Outboard_h[0]
            P_oro_h[0][0] = Inboard_h[0] + Hz_h[0]
            Mantle_h[0] = M[h][1][k][0] * A1[k]
            Mor_h[0] = FNEmoles(Mantle_h[0], Mor[0], Rmor[0], E_a2[h])
            Rmor_h[0] = Mantle_h[0] - Mor_h[0]
            D_oro_h[0][0] = Mor_h[0] + Outboard_h[0]
            Gateb2_h[0] = FNEmoles(D_oro_h[0][0], Gateb2[0], D_oro[0][1], E_b2[h])
            D_oro_h[0][1] = D_oro_h[0][0] - Gateb2_h[0]
            Gateb1_h[0] = FNEmoles(D_oro_h[0][1], Gateb1[0], D_oro[0][2], E_b1[h])
            D_oro_h[0][2] = D_oro_h[0][1] - Gateb1_h[0]
            denom = M[0][1][k][0] - Mor[0]
            if denom != 0:
                Sub_mant_h[0] = (Sub_mant[0] / denom) * (M[h][1][k][0] - Mor_h[0])
            else:
                Sub_mant_h[0] = 0.0
            W_oro_h[0][0] = Sub_re_h[0] + Sub_mant_h[0]
            Total_oro_h[0][0] = D_oro_h[0][0] + P_oro_h[0][0] + W_oro_h[0][0]
            oro_moles[h] = D_oro_h[0][2] + P_oro_h[0][1] + W_oro_h[0][2]
            W_oro_h[0][1] = W_oro_h[0][0] + Gateb2_h[0]
            Gateb3_h[0] = FNEmoles(W_oro_h[0][1], Gateb3[0], W_oro[0][2], E_b3[h])
            W_oro_h[0][2] = W_oro_h[0][1] - Gateb3_h[0]
            P_oro_h[0][1] = P_oro_h[0][0] + Gateb1_h[0] + Gateb3_h[0]
            M[h][2][k][1] = FNEmoles(P_oro_h[0][1], U[k], L[k], F_c3[h])
            M[h][2][k][2] = P_oro_h[0][1] - M[h][2][k][1]
            M[h][2][k][3] = W_oro_h[0][2]
            M[h][2][k][0] = M[h][1][k][0] - Mantle_h[0] + D_oro_h[0][2] - Sub_mant_h[0] + Rmor_h[0]

        # ---------------- increment / decay ----------------
        T = 4.5 - (k-1)*0.1
        Td = 0.1
        # mantle next cycle
        M[0][1][k+1][0] = M[0][2][k][0]
        M[1][1][k+1][0] = M[1][2][k][0]
        M[5][1][k+1][0] = M[5][2][k][0]
        M[6][1][k+1][0] = M[6][2][k][0]
        M[2][1][k+1][0] = M[2][2][k][0] + M[6][2][k][0]*(math.exp(L1*T)-math.exp(L1*(T-Td)))
        M[3][1][k+1][0] = M[3][2][k][0] + (M[6][2][k][0]/U8U5)*(math.exp(L2*T)-math.exp(L2*(T-Td)))
        M[4][1][k+1][0] = M[4][2][k][0] + M[5][2][k][0]*(math.exp(L3*T)-math.exp(L3*(T-Td)))
        # crustal segments 1..k
        for j in range(1, k+1):
            for l in range(0,4):
                M[0][1][j][l] = M[0][2][j][l]
                M[1][1][j][l] = M[1][2][j][l]
                M[5][1][j][l] = M[5][2][j][l]
                M[6][1][j][l] = M[6][2][j][l]
                M[2][1][j][l] = M[2][2][j][l] + M[6][2][j][l]*(math.exp(L1*T)-math.exp(L1*(T-Td)))
                M[3][1][j][l] = M[3][2][j][l] + (M[6][2][j][l]/U8U5)*(math.exp(L2*T)-math.exp(L2*(T-Td)))
                M[4][1][j][l] = M[4][2][j][l] + M[5][2][j][l]*(math.exp(L3*T)-math.exp(L3*(T-Td)))
        def _sum_res(j):
            return {h: sum(M[h][1][i][j] for i in range(1, k+1)) for h in range(1,7)}
        history.append({
            'cycle': k,
            'time_Ga': max(0.0, T - Td),
            'mantle': ratios({h: M[h][1][k+1][0] for h in range(1,7)}),
            'upper': ratios(_sum_res(1)),
            'lower': ratios(_sum_res(2)),
            'sub': ratios(_sum_res(3)),
            'orogene': ratios({h: oro_moles.get(h, 0.0) for h in range(1,7)}),
        })

    # final state
    mantle = {h: M[h][1][CYCLES+1][0] for h in range(1,7)}
    def reservoir_sum(j):
        return {h: sum(M[h][1][i][j] for i in range(1, CYCLES+1)) for h in range(1,7)}
    upper = reservoir_sum(1)
    lower = reservoir_sum(2)
    sub = reservoir_sum(3)
    total = {h: mantle[h] + upper[h] + lower[h] + sub[h] for h in range(1,7)}
    masses = {
        'mantle': M[0][1][CYCLES+1][0],
        'upper': sum(M[0][1][i][1] for i in range(1, CYCLES+1)),
        'lower': sum(M[0][1][i][2] for i in range(1, CYCLES+1)),
        'sub': sum(M[0][1][i][3] for i in range(1, CYCLES+1)),
    }
    masses['total'] = masses['mantle'] + masses['upper'] + masses['lower'] + masses['sub']
    last_upper = {h: M[h][1][CYCLES][1] for h in range(1,7)}
    last_lower = {h: M[h][1][CYCLES][2] for h in range(1,7)}
    last_sub = {h: M[h][1][CYCLES][3] for h in range(1,7)}
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






__all__ = ['run', 'ratios', 'FNEmoles']
