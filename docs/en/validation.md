# Validation and known issues

> **English** | [简体中文](../validation.md)

> This document holds the **validation data**. The full correctness argument is
> in [`correctness.md`](correctness.md).

## 1. Version IV: Table 4 validation

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

`scripts/run_version1.py` compares 11 cycles x 4 reservoirs x 3 ratios (126
rows) against Table IV and writes
`outputs/results/version1_comparison.csv`:

| Metric | Value |
|---|---|
| max absolute difference | 0.590072 (lower `208/204`, t = 0) |
| max percentage error | **1.5303 %** (lower `208/204`, t = 0) |
| RMSE | 0.196491 |

Present day (t = 0), model / Table IV:

| Reservoir | 206/204 | 207/204 | 208/204 |
|---|---|---|---|
| mantle | 18.2525 / 18.08 | 15.4801 / 15.42 | 38.0631 / 37.68 |
| orogene | 18.8099 / 18.88 | 15.5998 / 15.63 | 38.4603 / 38.82 |
| upper crust | 19.2296 / 19.33 | 15.6945 / 15.73 | 38.5937 / 39.06 |
| lower crust | 17.0545 / 17.29 | 15.2018 / 15.30 | 37.9699 / 38.56 |

**Conclusion**: Version I reproduces Table IV to about **1 %** (worst 1.53 %),
roughly 50x worse than the 0.028 % of Version IV; `208Pb/204Pb` deviates most
(lower crust -1.53 %, mantle +1.02 %).

### 2.1 Where the deviation comes from: masses and parameters match, element partitioning does not

Comparing the model's present-day inventories with Table II section III
(element abundances):

| Quantity | mantle model / paper | upper model / paper | lower model / paper | total |
|---|---|---|---|---|
| mass ($10^{24}$ g) | 775.176 / 775.2 | 6.983 / 7.0 | 17.841 / 17.8 | 800 / 800 ok |
| 204Pb ($10^{15}$ mol) | **11.46 / 19.5** | **14.44 / 10.3** | **12.10 / 8.2** | 38 / 38 ok |
| 238U | **104.40 / 174** | **174.71 / 127** | **69.88 / 48** | 349 / 349 ok |
| 232Th | **383.61 / 619** | **560.77 / 430** | **390.62 / 286** | 1335 / 1335 ok |

**The mass bookkeeping is exact**: the 0.63 / 0.90 shrink factors reproduce Table
III (2.600 -> 4.238 -> 5.270 ... -> 6.983 and 2.600 -> 4.940 -> 7.046 ... ->
17.841).

**But the mantle keeps only 0.59-0.62 of the paper's amount while the crust gets
30-48 % more**: the model strips too much out of the mantle and feeds too much
into the crust. The 1.53 % Pb-isotope deviation is a downstream consequence.

Every printed parameter checked so far matches the implementation: the $f_m$
sequence (1/8, 1/16, 1/32, 1/64, then 1/128), 3/10 upper-crust erosion plus 1/10
total-crust areal erosion (combining to 0.37), 2.6e24 g of new upper and lower
crust per cycle, $E_m=4$, $E_u=E_l=1$, the Pb/U/Th partition ratios, the decay
equations and the convention that parents are not depleted.

The deviation therefore sits in the **mantle-to-orogene element extraction**,
i.e. eq. 14:

> $\Delta^{\alpha}N_{m} = (\Delta M_m / M_{?}) \cdot {}^{\alpha}N_m \cdot {}^{\alpha}E_m$

The fraction is **unreadable in the scan** (OCR gives `(~~/~~)`), and the prose is
itself contradictory - "the mantle contributes 1/8 of itself" versus
"$E_m=4$ simulates complete extraction into a 25 % melt". Numerically, the two
readings give 11.5 (the $f_m \cdot E_m$ reading used here) and 28.1 (the $f_m$
reading) for the final mantle 204Pb, **neither matching the 19.5 of Table II**.
That is an inconsistency between the paper's parameter text and its result
tables, not something the implementation can fix on its own.

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
accept both, which is why the mistake never failed the suite. The assertions now
use the real Table IV values and the comment is corrected.

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

### 4.7 Environment

`scripts/run_version4.py` needs `pandas`; if `pandas` and `pytz` versions are
mismatched it raises `ImportError: Can't determine version for pytz`. The model
itself (`version4.py`) does not depend on pandas and can be driven from the
standard library alone.

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