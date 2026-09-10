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

Some copies of Table 4 print the lower-crust `238U/204Pb` as **6.1903**, which
is inconsistent with the rest of the row; this repository uses the
self-consistent value **6.4903** as the target, and the model gives 6.4903
(diff +0.00003).

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
itself (`version4.py`) does not depend on pandas and can be driven from the
standard library alone.

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

## 5. How to reproduce

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/run_version4.py
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

## 6. References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9

The Table 4 targets come from reference 1, Version I is defined by reference 2,
and the physical basis of the gates is reference 3.