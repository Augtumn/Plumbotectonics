# -*- coding: utf-8 -*-
"""Physical constants and default initial conditions used by the models."""

# Decay constants (per Ga)
LAMBDA_238 = 0.155125
LAMBDA_235 = 0.98485
LAMBDA_232 = 0.049475
LAMBDA_87RB = 0.0142
LAMBDA_147SM = 0.00654

# Natural isotope ratios
U8U5 = 137.88

# Version I initial conditions (Zartman & Doe, 1981, Table II)
V1_MASS0 = 800.0       # 1e24 g
V1_PB2040 = 38.0       # 1e15 mol
V1_U2380 = 349.0
V1_TH2320 = 1335.0
V1_R2060 = 10.36
V1_R2070 = 12.12
V1_R2080 = 30.55
V1_NEW_UPPER = 2.6     # 1e24 g
V1_NEW_LOWER = 2.6

# Version IV initial conditions (Haines & Zartman, 1988, Table 3)
V4_MASS0 = 1050.0
V4_PB2040 = 19.0
V4_U2380 = 177.0
V4_TH2320 = 758.0
V4_R2060 = 9.0668      # calibrated to Table 4
V4_R2070 = 9.9367
V4_R2080 = 28.6528

# Version IV model switches
V4_DP = 0.14
V4_A2 = 0.20
V4_A3 = 0.05
V4_B1 = 1.0
V4_B2 = 0.01
V4_B3 = 0.0
V4_BS = 0.001
V4_H0 = 35.0 / V4_BS
V4_CYCLES = 46
V4_U8U5 = U8U5
