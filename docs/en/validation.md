# Validation and known issues

> **English** | [简体中文](../validation.md)

> This document holds the **validation data**. The full correctness argument is
> in [`correctness.md`](correctness.md).

## 1. Version IV: Table 4 validation

> The original source of the target values is reproduced in
> [`outputs/results/literature/`](../../outputs/results/literature/) (PLUMBO
> Table 4, pages 1-2); transcription caveats in section 4.8.

Run:

```bash
uv run python scripts/run_version4.py
```

Targets are the present-day values of Haines & Zartman (1988), Table 4; the
model runs at `dp=0.14` over 46 cycles. Results:

| Reservoir | 206/204 | 207/204 | 208/204 | 238U/204Pb | 232Th/238U | 232Th/204Pb |
|---|---|---|---|---|---|---|
| mantle model | 18.4727 | 15.4822 | 37.7295 | 10.0059 | 2.7276 | 27.2922 |
| mantle table | 18.473 | 15.482 | 37.729 | 10.006 | 2.7276 | 27.29188 |
| **diff** | -0.00026 | +0.00021 | +0.00049 | -0.00010 | +0.00001 | +0.00034 |
| upper model | 19.3250 | 15.7268 | 39.0708 | 11.0770 | 3.8833 | 43.0159 |
| upper table | 19.325 | 15.727 | 39.071 | 11.077 | 3.8833 | 43.016 |
| **diff** | +0.00003 | -0.00017 | -0.00015 | +0.00005 | +0.00004 | -0.00007 |
| lower model | 17.6232 | 15.3511 | 38.7530 | 6.4903 | 6.0517 | 39.2777 |
| lower table | 17.623 | 15.351 | 38.753 | 6.4903 | 6.0518 | 39.278 |
| **diff** | +0.00017 | +0.00005 | -0.00004 | +0.00003 | -0.00008 | -0.00033 |
| sub model | 18.3180 | 15.1100 | 38.1010 | 9.1266 | 3.8921 | 35.5219 |
| sub table | 18.318 | 15.110 | 38.101 | 9.1292 | 3.8932 | 35.512 |
| **diff** | -0.00003 | -0.00003 | -0.00001 | -0.00258 | -0.00108 | **+0.00993** |

**Conclusion**: all 24 ratios satisfy `abs(diff) < 0.02` (the tolerance of
`tests/test_version4.py`); the worst case is subcrustal `232Th/204Pb`
(+0.00993).

Final masses ($10^{24}$ g):

| Reservoir | Mass |
|---|---|
| mantle | 1000.11 |
| upper | 6.70 |
| lower | 15.91 |
| sub | 27.28 |
| **total** | **1050.00** |

> Mass conservation: the four reservoirs sum to the initial mass, 1050 (to two
> decimal places).

### 1.1 About the lower-crust 6.4903

The **PDF text layer** of Table 4 reads the lower-crust `238U/204Pb` as
**6.1903**, which is inconsistent with the rest of the row; the **scan actually
prints `6.49030`**. This repository uses the value in the image, **6.4903**, as
the target, and the model gives 6.4903 (diff +0.00003).

The misread comes from the text layer being scan OCR with a systematic `4` ->
`1` confusion; for the related entries that are still uncorrected see
section 4.8.

### 1.2 Calibration

`E_a2`, `F_a3`, `E_b1`, `E_b2`, `E_b3`, `F_c3` and the initial ratios
`INIT_RATIOS = (9.0668, 9.9367, 28.6528)` in `version4.py` are **calibrated to
Table 4**, not the printed Table 3 integers. The printed values (for Pb:
`E_a2=80`, `F_a3=1.00`, `E_b1=40`, `E_b2=25`, `E_b3=25`, `F_c3=3.67`) are kept
as an order-of-magnitude reference.

## 2. Version I: comparison with Table IV of Zartman & Doe (1981)

> The original source of the target values is reproduced in
> [`outputs/results/literature/`](../../outputs/results/literature/)
> (Table II, Table IV and eqs. 17-19).

`scripts/run_version1.py` compares 11 cycles x 4 reservoirs x 3 ratios (126
rows) against Table IV and writes
`outputs/results/version1_comparison.csv`:

| Metric | Value |
|---|---|
| max absolute difference | 0.005089 (mantle `207/204`, t = 1.6) |
| max percentage error | **0.0349 %** (mantle `207/204`, t = 3.6) |
| RMSE | 0.002729 |

Table IV is printed to two decimals, so 0.005 is that table's precision limit.
The only one of the 126 rows past it is mantle `207/204` at t = 1.6 Ga (model
15.1551 against a printed 15.15, difference 0.00509) -- a rounding-boundary
case.

Present day (t = 0), model / Table IV:

| Reservoir | 206/204 | 207/204 | 208/204 |
|---|---|---|---|
| mantle | 18.0782 / 18.08 | 15.4156 / 15.42 | 37.6804 / 37.68 |
| orogene | 18.8783 / 18.88 | 15.6261 / 15.63 | 38.8248 / 38.82 |
| upper crust | 19.3335 / 19.33 | 15.7273 / 15.73 | 39.0648 / 39.06 |
| lower crust | 17.2911 / 17.29 | 15.2991 / 15.30 | 38.5580 / 38.56 |

**Conclusion**: Version I reproduces all 126 Table IV values to the precision
printed in the paper (worst 0.00509, 0.035 % relative) -- the same order as
Version IV's 0.028 % against Table 4.

### 2.1 The former 1.5 % deviation: root cause and fix

Before the fix, Version I differed from Table IV by up to **0.5901 (1.5303 %)**
with RMSE 0.1965, and this document attributed that to "the paper's parameter
text being inconsistent with its own result tables". **That conclusion was
wrong**: the paper is self-consistent and the deviation came from this
repository.

The root cause was the **orogene redistribution**
([`theory.md`](theory.md) section 2.5, eqs. 17-19 of the paper):

| Approach | Mantle share of orogene Pb, first cycle |
|---|---|
| Before: `F_PB` used directly as fractions of the orogene content | 2.8 % |
| Paper eqs. 17-19: weighted by returning-increment mass, over $s=\sum M_iF_i$ | $94.8\times0.028/5.1816$ = **51.3 %** |

In the first cycle the mantle contributes 100 mass units and takes back 94.8,
while each new crustal increment receives only 2.6 -- so the mantle must get
the bulk of the orogene. Splitting by 2.8 % instead strips the mantle and
over-feeds the crust:

| Quantity ($10^{15}$ mol) | before: model / Table II | after: model / Table II |
|---|---|---|
| mantle 204Pb | **11.46** / 19.5 | **19.48** / 19.5 |
| upper 204Pb | **14.44** / 10.3 | **10.35** / 10.3 |
| lower 204Pb | **12.10** / 8.2 | **8.17** / 8.2 |
| mantle 238U | **104.4** / 174 | **173.5** / 174 |
| upper 238U | **174.7** / 127 | **127.1** / 127 |
| lower 238U | **69.9** / 48 | **48.5** / 48 |
| mantle 232Th | **383.6** / 619 | **619.2** / 619 |
| upper 232Th | **560.8** / 430 | **429.6** / 430 |
| lower 232Th | **390.6** / 286 | **286.3** / 286 |

All 12 entries of Table II section III.B now land within 1 % (worst 0.94 %,
lower-crust 238U: 48.45 / 48).

> **The two tables use different instants.** The absolute abundances of
> Table II section III.B are the state **after** the final orogeny (masses
> 775.18 / 6.98 / 17.84 against 775.2 / 7.0 / 17.8), while Table IV and
> section III.A give the state **before** it (18.078 / 19.333 / 17.291 against
> 18.08 / 19.33 / 17.29). `history` records the latter; the segment
> reservoirs returned by `run()` are the former.

### 2.2 Parameter check

Every printed parameter was checked against the implementation and all of them
match -- and they are **sufficient to reproduce both tables**: the $f_m$
sequence (1/8, 1/16, 1/32, 1/64, then 1/128), 3/10 upper-crust erosion plus
1/10 total-crust areal erosion (combining to 0.37), $2.6\times10^{24}$ g of new
upper and lower crust per cycle, $E_m=4$, $E_u=E_l=1$, the Pb/U/Th partition
ratios (0.028, 0.754, 0.218) / (0.024, 0.854, 0.122) / (0.020, 0.788, 0.192),
the decay equations, and the convention that parents are not depleted.

There is therefore **no "paper inconsistency" to work around**: the Table II
parameters plus eqs. 17-19 reproduce Table IV and Table II section III
simultaneously. The supposedly unreadable fraction in eq. 14 (OCR gives
`(~~/~~)`) is no longer a gap either -- the prose reading "mass ratio of magma
to total mantle" together with $E_m=4$ gives the right answer once eqs. 17-19
are used.

## 3. Conservation and invariants

| Quantity | Version I | Version IV |
|---|---|---|
| total mass (exactly conserved) | 800.000000000 | 1050.000000000 |
| total moles | 3737.14 -> 4456.92 (**not** conserved) | 1859.47 -> 2340.48 (**not** conserved) |
| segments | 11 upper + 11 lower | - |
| `history` entries | 11 | 46 (4.4 -> 0.0 Ga) |
| mantle `206/204` monotonic | - | yes |

> **Mass conservation can be used as a regression test; total moles cannot.**
> The increase is a modelling convention (the parents $^{238}\mathrm{U}$ and
> $^{232}\mathrm{Th}$ are held constant over each decay interval), not an
> implementation error. See [`correctness.md`](correctness.md) section 4.

## 4. Known issues

### 4.1 `history['orogene']` used to contain the distal component only (fixed)

`version4.py` used to evaluate

```python
oro_moles[h] = D_oro_h[0][2] + P_oro_h[0][1] + W_oro_h[0][2]
```

before `P_oro_h[0][1]` and `W_oro_h[0][2]` were assigned, so both terms were
still 0 and `history[...]['orogene']` only held the distal component $D^{(2)}$,
missing the proximal and wedge parts.

**Impact**: only `history['orogene']` (used for plotting); reservoir results and
the Table 4 match were unaffected.

**Status**: fixed - the sum now happens after `P_oro_h[0][1]` is assigned.

### 4.2 `constants.py` and the model implementations are not a single source

- `version1.py` re-declares `L238`, `MASS0`, `F_PB`, ...;
- `version4.py` re-declares `CYCLES`, `A2`, `INIT_RATIOS`, ....

Editing `constants.py` therefore does **not** affect the models. Consolidating
would touch both modules and is better done as its own change.

### 4.3 Module docstring placement (fixed)

`version4.py` used to start with `INIT_RATIOS = (...)`, before the module
docstring, so the string was not a real `__doc__`. `INIT_RATIOS` now sits after
the docstring and the imports.

### 4.4 `pyproject.toml` dev extra lists an unused `scipy`

`scipy` is in `[project.optional-dependencies].dev` but nothing imports it; keep
it for future fitting work or drop it.

### 4.5 `tests/test_version1.py` used the wrong reference values

The test used to compare against 18.25 / 15.48 / 38.06 and label them as Table
IV, but Table IV actually gives **18.08 / 15.42 / 37.68**; 18.25 / 15.48 /
38.06 is this implementation's own output. The tolerances (0.5 / 0.3 / 0.5)
accept both, which is why the mistake never failed the suite.

**Current state**: the assertions use the real Table IV values and now cover all
**126 rows** (11 cycles x 4 reservoirs x 3 ratios) with the tolerance tightened
to `0.006`; the 12 Table II section III.B abundances and a regression assertion
that the partition ratios must be mass-weighted were added as well, so neither
mistake can hide behind a loose tolerance again.

### 4.6 Two orogene `208Pb/204Pb` cells in Table IV are OCR errors

Extracting Table IV from the text layer of
`papers/Zartman_Doe_1981_Plumbotectonics.pdf` gives two orogene values that
contradict the physical trend:

| t (Ga) | Extracted | Used | Evidence |
|---|---|---|---|
| 4.0 | 30.65 | **30.55** | the other three reservoirs and the initial value are 30.55 |
| 1.6 | 36.77 | **35.77** | breaks monotonicity (34.95 -> 36.77 -> 36.56) |

`TABLE_IV` in `scripts/run_version1.py` uses the corrected values; the raw
extraction is recorded here for checking. Every other column passes a
monotonicity check.

**The corrections are confirmed independently by the model**: the corrected
implementation gives 30.550 at t = 4.0 and 35.769 at t = 1.6, within 0.000 and
0.001 of the adopted values, while 36.77 cannot be produced by any parameter
combination.

### 4.7 Environment

`scripts/run_version4.py` needs `pandas`; if `pandas` and `pytz` versions are
mismatched it raises `ImportError: Can't determine version for pytz`. The model
itself (`version4.py`) does not depend on pandas and needs only NumPy.

### 4.8 Two sub-reservoir targets in the Version IV table come from OCR misreads (**not fixed**)

`outputs/results/literature/` now holds the source images of both comparison
tables. Checking `haines_zartman_1988_table_4_page2.png` (PLUMBO Table 4, page
2) shows that the report's PDF **text layer** is scan OCR with a systematic
`4` -> `1` confusion:

| Cell | value in the image | text-layer OCR | value used here |
|---|---|---|---|
| lower `238U/204Pb` | `6.49030` | `6.19030` | 6.4903 (corrected) |
| upper `232Th/204Pb` | `43.01600` | `13.01600` | 43.016 (corrected) |
| **sub `207Pb/204Pb`** | **`15.44000`** | `15.11000` | **15.110 (still the misread)** |
| **sub `232Th/204Pb`** | **`35.54200`** | `35.51200` | **35.512 (still the misread)** |

`15.440` and `35.542` are independently corroborated by the Subcrustal
Lithosphere column of Zartman & Haines (1988), Table 1 (207Pb/204Pb = 15.44).

**Impact**: the "all 24 ratios satisfy `abs(diff) < 0.02`" conclusion of
section 1 does not hold for subcrustal `207Pb/204Pb` -- the model's 15.109975 is
**0.33** away from the printed 15.44000, not the 0.00003 recorded in the table.
(Fixing `35.512` -> `35.542` would likewise turn that row's +0.00993 into
-0.0201, past the 0.02 tolerance.)

**Status**: not fixed. This is no longer a transcription question: the Version IV
subcrustal reservoir itself (`207Pb/204Pb` low by 0.33, while 206/204, 208/204
and 238U/204Pb of the same reservoir all match) needs its own diagnosis. The
targets are deliberately left untouched until that is done, so the gap is not
papered over by tuning.

> Lesson: **literature values must be read off the image, not transcribed from
> the text layer of a scanned PDF.** Version I's two tables were verified
> against the image and recomputed independently, so they are unaffected.

## 5. Li et al. (2001): China regional model

Li Long, Zheng Yongfei and Zhou Jianbo (2001) built a regional model for
continental China on the basis of the "plumbotectonic model".
`src/plumbotectonics/china.py` implements its criterion as: **the algorithm
follows Zartman & Doe (1981) (this repository's `version1`) and only replaces
the two tables the paper prints itself**.

### 5.1 Given by the paper vs inherited

| Quantity | Value | Source |
|---|---|---|
| 4.0 Ga 206/207/208Pb ratios | 10.17 / 12.07 / 30.56 | paper Table 1 |
| Partition ratios (mantle/lower crust/upper crust) | Pb 0.038/0.235/0.727, U 0.024/0.111/0.865, Th 0.021/0.162/0.817 | paper Table 2 |
| Upper/lower crustal retention $p^u$, $p^l$ | 0.63, 0.95 (erosion 0.37, 0.05) | paper eq. (2) |
| Enrichment factors | $E_m=4$, $E_u=E_l=1$ | paper eq. (5) |
| Residual orogene returned to the mantle | 90 %, the other 10 % becomes upper-crust sediment | paper eqs. (7)(8), assumption (3d) |
| Initial abundances 204Pb/238U/232Th | 38 / 349 / 1335 ($10^{15}$ mol) | **inherited from ZD1981 Table II** |
| Masses mantle / new upper and lower crust | 800 / 2.6 / 2.6 ($10^{24}$ g) | **inherited from ZD1981 Table II** |
| $k_i$, decay constants, 238U/235U | 1/8...1/128, 0.155125/0.98485/0.049475, 137.88 | **inherited from ZD1981** |

The paper **does not give** the 4.0 Ga element abundances, nor the specific
number in "the new upper and lower crust have equal mass" -- they can only be
inherited. This implementation therefore has **zero free parameters**.

### 5.2 Current accuracy

| Data | max absolute difference | mean | RMSE | max relative |
|---|---|---|---|---|
| paper Table 3 (99 growth-curve values) | **0.5998** | 0.1322 | 0.2016 | 3.099 % |
| paper Table 4 (6 present-day values) | **0.6031** | 0.2550 | 0.3481 | 6.225 % |

Table 3 is printed to 0.01, and only **11/99** fall inside +-0.005. **Table 3 is
not reproduced.**

The qualitative features (on which the whole argument of the paper rests) do
hold: upper crust 19.90 > mantle 17.32 > lower crust 17.14 (paper
19.86 > 17.92 > 17.10).

### 5.3 Inverting the unpublished values: the new-crust mass

The paper prints "**assume the upper and lower crust masses are equal**" but
never prints the number, so it can only be inherited from ZD1981's
2.6 x 10^24 g.  Freeing the quantities the four tables do not give (`mass_u`,
`mass_l`, `mu0`, `kappa0`; Jacobian condition numbers 22-46, parameter
correlations <= 0.65, so the inverse problem is well posed):

| Data | $\mu_0$ | $\kappa_0$ | $m_{upper}$ | $m_{lower}$ | Table 3 max | Table 3 mean |
|---|---|---|---|---|---|---|
| Table 3 only | 9.933 +- 0.034 | 3.818 +- 0.025 | **7.478 +- 0.408** | **2.273 +- 0.388** | **0.2465** | **0.0422** |
| Table 4 only | 9.953 +- 0.022 | 3.752 +- 0.006 | 2.255 +- 0.066 | 1.808 +- 0.064 | 0.7014 | 0.1794 |
| **Tables 3 + 4 jointly** | 9.551 +- 0.047 | 3.862 +- 0.027 | **5.755 +- 0.652** | **5.209 +- 0.637** | **0.3304** | **0.0949** |
| ZD1981 inherited (current default) | 9.184 | 3.825 | 2.600 | 2.600 | 0.5998 | 0.1322 |

($\mu_0$ and $\kappa_0$ are MODERN-EQUIVALENT ratios, the same convention as
ZD1981's 9.184 / 3.825; five different starting points all converge on the same
solution, so it is not a local minimum.)

Three conclusions:

1. **The initial abundances are right** -- inverting Table 3 and Table 4
   separately both put $\mu_0$ at **9.93-9.95** (about 8 % above ZD1981's 9.184)
   and $\kappa_0$ at 3.75-3.82 (ZD1981: 3.825).  The two tables agree about the
   initial abundances, which supports inheriting ZD1981's order of magnitude.
2. **The crustal mass is about twice the inherited value** -- the joint
   inversion gives $m \approx 5.5 \pm 0.65$ (upper) and $5.2 \pm 0.64$ (lower),
   **2.1x** ZD1981's 2.6.
3. **The paper's "equal masses" assumption contradicts Table 3** -- inverting
   Table 3 alone gives $m_{upper} = 7.48$ against $m_{lower} = 2.27$, the upper
   layer being **3.3x** the lower, 9 sigma apart.  Freeing that one degree of
   freedom cuts the Table 3 mean deviation from 0.094 to **0.042**.

**The crustal mass and the initial abundances are degenerate**: pinning the
abundances at ZD1981's values and varying only the mass never takes the Table 3
worst deviation below 0.45 (at $m \approx 8$), while the mean deviation is in
fact best near $m \approx 2.6$.  **So "the crustal mass is wrong" is neither
the only reason Table 3 resists reproduction nor even the main one.**

Adopting the joint inversion improves **both** tables at once (the only
configuration that does):

| Configuration | Table 3 max | Table 3 mean | Table 4 max | Table 4 upper/mantle/lower `238U/204Pb` |
|---|---|---|---|---|
| ZD1981 default (no tuned parameters) | 0.5998 | 0.1322 | 0.6031 | 7.91 / 5.34 / 14.38 |
| **Joint inversion (4 calibrated parameters)** | **0.3304** | **0.0949** | **0.3979** | 8.51 / 5.40 / 14.58 |
| Table 3 first | 0.2465 | 0.0422 | 2.4733 | 8.59 / 4.81 / 12.51 |

The default keeps ZD1981's inherited values (everything the paper does not print
is inherited, so the model has **no tuned parameters**); the second row is
reproducible with
`china.run(mu0=9.5505, kappa0=3.8623, mass_u=5.755, mass_l=5.209)` and is
**calibration**, not inheritance.

### 5.4 eq. (6) conflicts with its own gloss (readings A and B)

The paper prints eq. (6) with **three** terms:

$$s = \Delta M_o^t \cdot F^o + M_u^t \cdot F^u + M_l^t \cdot F^l$$

but its gloss defines $F^o$ as the coefficient of "the residual orogene, i.e.
the part returning to the mantle", while eq. (7) sends only **90 %** of that
residual back to the mantle.  The paper never says whether the remaining 10 %
should be weighted with $F^o$ or with $F^u$.  Two readings:

| | `share_model="paper"` (A) | `share_model="four_bin"` (B, **default**) |
|---|---|---|
| $s$ | three terms, the whole residual weighted with $F^o$ | four terms: $0.9M_{res}F^o + 0.1M_{res}F^u + M_u F^u + M_l F^l$ |
| coefficient for the 10 % | $F^o$ (the mantle's) | $F^u$ (the upper crust's) |
| physically self-consistent | no -- material that is stated to become sediment is shared out with the mantle's coefficient | yes -- every destination uses its own coefficient |
| when `RETURN = 1` | the two **coincide exactly** (the fourth bin is empty) | same |

Both conserve mass and elements exactly, so the conservation check cannot tell
them apart; only physical judgement and the quality of the fit can.

**Measured** (no tuned parameters, everything else identical):

| | Table 3 max | Table 3 mean | Table 3 RMSE | Table 4 max | upper/mantle/lower 206Pb/204Pb |
|---|---|---|---|---|---|
| A `"paper"` | 0.6211 | 0.2199 | 0.2719 | **0.4715** | 20.42 / 17.49 / 17.25 |
| **B `"four_bin"`** | **0.5998** | **0.1322** | **0.2016** | 0.6031 | **19.90** / 17.32 / **17.14** |
| paper | — | — | — | — | 19.86 / 17.92 / 17.10 |

B is better across Table 3 (mean deviation improved by 40 %) and moves the
**upper crust's 206Pb/204Pb from 20.42 to 19.90** against the paper's 19.86.
Upper/lower crust differentiation is the paper's central claim, and A misses the
upper crust by 0.56.  **This implementation therefore takes B as the default**:
the authors' own code most likely used B's logic and the printed eq. (6) simply
dropped the fourth term.  A remains available as a switch.

### 5.5 Internal inconsistencies in the paper (5 located)

| # | Location | What it says | Evidence |
|---|---|---|---|
| 1 | eq. (3) | prints `Σ p^j` (j=1..i-1) where `p^(j-1)` is required | read literally, the present-day upper-crust 238U/204Pb of Table 4 comes out 9.76, whereas the paper prints 14.98 |
| 2 | $p^l$ | printed as 0.95 | fitting with 0.95 is worse than with ZD1981's 0.90 |
| 3 | $E_m$ in eq. (5) | says only "entering the orogene", not how much the mantle loses | if it also acted on the mantle loss, the Table 4 deviation would rise from 0.47 to 0.78 |
| 4 | Table 4 footnote | lower crust 6.94 | Zartman & Haines (1988) actually give 6.49, a **digit transposition** |
| 5 | body text vs Table 4 footnote | the text compares against Zartman and Doe (1981), the footnote cites Z&H (1988) | the values (10.01, 11.08) are digit-for-digit Z&H's version IV; and only against Z&H does the "Th-rich" claim hold (3.60 vs 2.73; against ZD1981's 3.57 the difference is only 0.03) |

### 5.6 Two physics bugs fixed during development

Both used to give **better-looking but wrong** accuracy; they are recorded here
so they are not repeated:

| Bug | Symptom | Fix |
|---|---|---|
| **the residual 10 % of the orogene was discarded** | final total mass of the system 780.2 (initial 800), violating mass conservation | the paper says it "remains at the crustal edge ... becomes sedimentary rock", so it enters the **upper crust** as its own layer. After the fix the total mass is 800.0 |
| **$E_m$ applied to the orogene gain only** | the mantle lost only $f_m N_m$ while the orogene received $f_m E_m N_m$, so the whole system's Pb/U/Th **doubled every run** (final/initial = 1.96 / 1.93 / 1.91) | the mantle loss must carry $E_m$: the extracted material has a concentration $E_m$ times its own, so its element content is $= f_m M \times E_m (N/M) = f_m E_m N$. After the fix, $E_m$ on the loss and $E_m$ on the gain only conserve all **six nuclides** exactly |

> Lesson: **goodness of fit must not be used to choose between physical
> assumptions.** The two wrong configurations above gave Table 4 deviations of
> 0.097 and 0.285, both better than the correct configuration's 0.472 -- but
> they were bought by breaking conservation. The conservation checks are
> `tests/test_china.py::test_element_inventory_is_conserved` and
> `::test_the_mass_of_the_system_is_constant`.

### 5.7 Two switchable physical conventions

| Switch | Default | Alternative | Notes |
|---|---|---|---|
| `decay_parents` | `False` (ZD1981: constant parents, $\Delta d = e^{\lambda t}-e^{\lambda t'}$, 207 fed by 238U/137.88) | `True` (paper eqs. 9-10: parents really decay, 235U tracked separately, 4.0 Ga 238U/235U = 4.9897) | **the two are equivalent digit for digit** (maximum difference $2.1\times10^{-14}$), because "constant + 349/1335" and "decaying + back-calculated 649/1627" are the same thing |
| `melt_model` | `"zd1981"` ($E_m$ fixed at 4) | `"batch"` ($E=1/f_m$) | the paper says $E_m=4$ corresponds to "25 % melting", while $f_m$ falls from 1/8 to 1/128 -- the two are inconsistent; under batch melting a perfectly incompatible element should have $E=1/f_m$ (8...128). Measured, batch is actually worse (Table 3 max 1.18), so the default keeps the paper's convention |

### 5.8 Known limitations (of the framework itself, not implementation bugs)

- **Pb is treated as a refractory element**: it is separated from U and Th only
  by the partition ratios, with no distinction between its behaviour in partial
  melting and in orogene differentiation (Pb is moderately volatile).
- **The mantle is a single well-mixed reservoir**: implicitly homogenised by
  convection within the 0.4 Ga interval.
- **The orogene homogenises instantaneously**: this is the paper's assumption
  (3a), not an implementation choice.

### 5.9 Reproduction

```bash
uv run python scripts/run_china.py     # print growth curves and comparison statistics, write outputs/results/china_comparison.csv
uv run pytest -q tests/test_china.py   # 11 tests
```

## 6. How to reproduce

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/run_version4.py
uv run python scripts/run_china.py
```

Or without installing anything, and without pandas:

```python
import sys
sys.path.insert(0, "src")
from plumbotectonics.version4 import run, ratios

TARGETS = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper":  [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower":  [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub":    [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]

res = run(dp=0.14)
for name, target in TARGETS.items():
    got = [ratios(res[name])[k] for k in KEYS]
    print(name, max(abs(g - t) for g, t in zip(got, target)))
```

## 7. References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9

The Table 4 targets come from reference 1, Version I is defined by reference 2,
and the physical basis of the gates is reference 3.