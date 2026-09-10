# Correctness guarantees

> **English** | [简体中文](../correctness.md)

This document states why the results can be trusted: a **baseline validation**,
an **invariant** and a **regression** layer, plus the modelling conventions and
the scope of the guarantee. The raw validation data is in
[`validation.md`](validation.md).

## 1. Three-layer guarantee system

| Layer | Mechanism | Artefacts |
|---|---|---|
| 1. Baseline | compare against the printed values of the papers | `tests/test_version1.py`, `tests/test_version4.py`, `tests/test_china.py` |
| 2. Invariants | conservation laws and structural constraints | `tests/test_conservation.py`, `tests/test_china.py` |
| 3. Regression | rerun 1+2 on every change | `pytest` (includes the figure layout and PDF-timestamp checks in `tests/test_plotting.py`) |

Only when all three pass is a result considered "correct under the model
definition". Current status: **33/33 passing**.

## 2. Layer 1: baseline validation

### 2.1 Version IV -> Haines & Zartman (1988), Table 4

Table 4 lists 4 reservoirs x 6 ratios of present-day values, 24 numbers in
total. The model runs at `dp=0.14` over 46 cycles and each ratio is compared
with a tolerance of `abs(diff) < 0.02`:

- worst measured deviation **0.00993** (subcrustal `232Th/204Pb`), all 24 pass;
- full table in [`validation.md`](validation.md) section 1.

### 2.2 Version I -> Zartman & Doe (1981)

- initial mantle: 206/204 = 10.36, 207/204 = 12.12, 208/204 = 30.55 (exact);
- whole-table reproduction: all **126 rows** of Table IV (11 cycles x 4
  reservoirs x 3 ratios), worst difference **0.00509** (mantle `207/204` at
  t = 1.6 Ga), i.e. the two-decimal printing limit of that table; worst
  relative error 0.0349 %, RMSE 0.002729;
- present-day mantle: 18.0782 / 15.4156 / 37.6804 against 18.08 / 15.42 / 37.68;
- element abundances: all 12 entries of Table II section III.B (mass and
  204Pb/238U/232Th) land within 1 %.

Full comparison in [`validation.md`](validation.md) section 2.

> Before 2026-09 this check only reached "present-day mantle, order 1 %". The
> root cause was the orogene redistribution (eqs. 17-19) using the partition
> ratios as direct fractions; the fix is recorded in
> [`validation.md`](validation.md) section 2.1.

### 2.3 China model -> Li et al. (2001), Tables 3 and 4

| Data | Items | max absolute difference | mean | RMSE | Criterion |
|---|---|---|---|---|---|
| paper Table 4 (present-day `238U/204Pb`, `Th/U`) | 6 | 0.4715 | 0.1793 | 0.2353 | `abs < 0.65` / `abs < 0.10` (`Th/U`) |
| paper Table 3 (growth curves) | 99 | 0.6211 | 0.2199 | 0.2719 | **not reproduced**, pinned only by the regression ceilings 0.65 / 0.25 |

The model has **zero free parameters**: the initial abundances, the new-crustal
mass, $k_i$ and the decay constants that the paper does not print are all
inherited from Zartman & Doe (1981).

> **Table 3 is explicitly listed as not reproduced**, because the paper's two
> result tables contradict each other: inverting Table 3 gives a new-crustal
> mass of $15.15 \pm 0.96$ against $1.28 \pm 0.48$ from Table 4, about 13 sigma
> apart. `tests/test_china.py` therefore does not assert "reproduction" but
> pins deviation ceilings, so that the fit cannot quietly degrade later. The
> full analysis and the paper's five internal inconsistencies are in
> [`validation.md`](validation.md) section 5.

## 3. Layer 2: invariants

### 3.1 Mass conservation (exact, the strongest regression signal)

All three models only extract, mix and redistribute material, so mass is
neither created nor destroyed:

| Model | Initial mass | Measured final | Deviation |
|---|---|---|---|
| Version I | 800.0 | 800.000000000 | 0 |
| Version IV | 1050.0 | 1050.000000000 | 0 |
| China model | 800.0 | 800.000000000 | 0 |

Version IV final reservoirs ($10^{24}$ g):

| mantle | upper | lower | sub | total |
|---|---|---|---|---|
| 1000.1118 | 6.6957 | 15.9128 | 27.2797 | **1050.0000** |

A single wrong partition coefficient breaks this identity immediately, which
makes it more sensitive than "the ratios look close to the paper".

The China model has one finer layer of element conservation as well: after 11
orogenies the **total mole numbers** of 204Pb, 238U and 232Th deviate by **0**
relative to their initial values (asserted inside `run()` when `strict=True`,
raising `AssertionError` beyond the bound). Under `decay_parents=True` it is
instead the "daughter + parent" sums that are conserved (206Pb + 238U, etc.),
because the parents themselves decay to today's 349.

> This invariant caught two real bugs: the 10 % of the residual orogene that
> does not return to the mantle used to be discarded, dropping the total mass of
> the system from 800 to 780.2. By the paper's assumption (3d) it should become
> upper-crust sediment, and the fix restores 800.000000000. It also caught
> another one: if $E_m$ acted on the orogene gain only and not on the mantle
> loss, the whole system's elements doubled every run (final/initial
> 1.96 / 1.93 / 1.91). See [`validation.md`](validation.md) section 5.5.

### 3.2 Structural invariants

- Version I adds exactly one upper and one lower segment per cycle (11 + 11);
- all Version I segment masses and isotope mole numbers stay positive;
- Version IV `history` has exactly 46 entries, `cycle` 1-46, time 4.4 -> 0.0 Ga;
- Version IV `total[h] == mantle[h] + upper[h] + lower[h] + sub[h]` (h = 1..6);
- Version IV mantle `206Pb/204Pb` increases monotonically with geological time;
- the China model adds three layers per cycle: two on the upper-crust side (the
  newly formed upper crust and the sediment layer built from the 10 % residual
  orogene) and one on the lower-crust side (the newly formed lower crust), so
  33 layers over the 11 cycles;
- the China model's present-day `238U/204Pb` over mantle, upper and lower crust
  satisfies upper crust > mantle > lower crust, and `206Pb/204Pb` follows the
  same order -- this is the premise of all the paper's source-discrimination
  argument, and reversing the order would invalidate the interpretation of the
  paper's Figures 2 and 3.

## 4. Total moles are **not** conserved (by design)

Measured total moles (204 + 206 + 207 + 208 + 232 + 238):

| Model | Initial | Final | Change |
|---|---|---|---|
| Version I | 3737.14 | 4456.92 | **+719.78** |
| Version IV | 1859.47 | 2340.48 | **+481.01** |

The reason is the convention of the published models: **the parents are held
constant across each decay interval**. The daughters grow as

$$
^{206}\mathrm{Pb} \mathrel{+}= ^{238}\mathrm{U}\left(e^{\lambda_{238}t}-e^{\lambda_{238}t'}\right)
$$

while $^{238}\mathrm{U}$ itself is not depleted; 207 and 208 behave the same.
Pb therefore appears "out of nothing" on the books and total moles must rise.

This is a **modelling convention of Version I and Version IV**, not an
implementation error:

- mass conservation still holds (mass and moles are two separate ledgers);
- the primary output of the models is the 204-normalised **ratio**, and holding
  the parents constant is part of the published definition;
- consequently **a regression test may assert mass conservation but must not
  assert mole conservation**;
- switching to strict atom conservation (depleting the parents) yields a
  different model that no longer reproduces Table 4, which is out of scope
  here.

## 5. Numerical robustness

The code guards degenerate inputs explicitly, so `ZeroDivisionError` / `NaN`
cannot propagate:

| Location | Guard |
|---|---|
| `version4.FNEmoles` | `Bias <= 0` or `Denom == 0` -> masked to `0` (a branch returning `0.0` before the migration; same values) |
| `version4.run`, `V0` | zero segment mass -> `V0 = 0` |
| `version4.run`, isotope split of `S_mant` | denominator `M_m - M_or == 0` -> skipped |
| `version1.ratios` / `version4.ratios` | zero denominator -> `None` |
| `version1.run`, redistribution share `s` | `s <= 0` -> that isotope's share is 0 (degenerate parameters only; unreachable for Table II) |
| `plotting._extract_version4_series` | skips `None` ratios |

`tests/test_conservation.py` covers both `FNEmoles` guards and the zero
denominator branches of `ratios`.

**Measured floating-point accuracy** (all three models carry their state in
NumPy arrays and use `np.exp` for the decay):

| Item | Measured |
|---|---|
| whole model vs a 60-digit Decimal re-run (all of Version I) | worst relative difference **8.4e-16** (about 4 ulp) |
| final 204Pb, 238U | **bit-identical** |
| 22-term segment sums: `np.sum` (pairwise) vs `math.fsum` (exact) | 204 bit-identical; 238 relative 1.6e-16 |
| **before vs after the migration**: stdlib vs NumPy implementation | Version I **6.5e-16**, Version IV **8.9e-16** |
| `np.exp` vs `math.exp` over the 342 exponents the models use | **bit-identical** (0 differ) |

The floating-point error is 12 orders of magnitude below the 0.005 tolerance of
Table IV; what actually limits the model is the number of digits the paper
prints and the parameters themselves, not the numeric format.  The migration
moved results by 3-4 ulp only (all of it from `np.sum`'s pairwise summation) and
**changed no digit of either comparison table** -- both CSVs are byte-identical
to the pre-migration ones.

> Note: numpy's transcendental functions are **not guaranteed correctly
> rounded**.  On this machine `np.exp` matched `math.exp` bit for bit on all 342
> arguments, but that is platform-dependent; on another platform `np.exp` may
> differ by ~1 ulp, and the last row above would need re-measuring.

## 6. Reproducibility

- **Dependency boundary**: all three models use **NumPy** only (`version1.py`,
  `version4.py` and `china.py` all `import numpy as np`); they no longer need
  `math`, and read no external data files; `pandas` serves the comparison
  statistics in `scripts/` and `matplotlib` only the plotting;
- **Fully deterministic**: no random numbers, no timestamps, no
  order-dependent parallel reductions; `plotting.py` explicitly clears the
  `CreationDate` PDF metadata entry, which matplotlib would otherwise populate
  with the wall-clock time and make the PDF figures non-reproducible;
- **Inputs inline**: initial conditions and Table 3 parameters are declared as
  constants/arrays in the source, with their provenance;
- **Versioned**: `pyproject.toml` declares `version = "0.1.0"` and dependency
  lower bounds.

The same environment and version reproduce bit-identical results.

## 7. Explicit handling of known inconsistencies

| Issue | Handling |
|---|---|
| The PLUMBO Table 4 **text layer** is scan OCR that misreads `4` as `1` | the **image** is authoritative; two subcrustal targets still carry the misread values, see [`validation.md`](validation.md) section 4.8 |
| The printed Table 3 enrichment factors (integers) do not reproduce Table 4 | **calibrated** values are used (`E_a2` ... `F_c3`, `INIT_RATIOS`); the printed ones stay as an order-of-magnitude reference |
| Two orogene `208Pb/204Pb` cells of Table IV are OCR errors | corrected values (30.55 / 35.77) are used, and the corrected model now confirms them independently, see [`validation.md`](validation.md) section 4.6 |
| `history['orogene']` used to miss the proximal and wedge components | fixed, see [`validation.md`](validation.md) section 4.1 |
| The Version I 1.5 % deviation was once blamed on a "self-inconsistent paper" | that conclusion was wrong and has been retracted; the real cause was the implementation of eqs. 17-19, now fixed, see [`validation.md`](validation.md) section 2.1 |

Each inconsistency is recorded explicitly instead of being hidden behind
tuned parameters.

## 8. How to self-check

```bash
uv sync --extra dev
uv run pytest -q                      # all three layers
uv run pytest -q tests/test_conservation.py   # invariants only
```

If you prefer not to use pytest, run the test functions directly:

```python
import sys
sys.path[:0] = ["src", "tests"]
import test_conservation as t
for name in dir(t):
    if name.startswith("test_"):
        getattr(t, name)()
        print("ok", name)
```

`scripts/run_version1.py` writes the 126 Table IV comparisons to
`outputs/results/version1_comparison.csv` and `scripts/run_version4.py` writes
the 24 Table 4 comparisons to `outputs/results/version4_comparison.csv`, for
manual review.

## 9. Scope and limitations

**What is guaranteed is implementation correctness**: this repository
faithfully reproduces the model definitions, parameters and calibration of
Zartman & Doe (1981) and Haines & Zartman (1988).

**Geological truth is not guaranteed**: the models themselves simplify the
evolution of the shallow Earth - long-lived steady-state reservoirs, discrete
orogenic cycles, constant parents, complete homogenisation inside the orogene.
Treating the output as a prediction for the real Earth requires independent
geological argument, which is beyond this document.

## 10. CI suggestion

```yaml
# .github/workflows/tests.yml   (suggested content; this repository does not ship the file)
name: tests
on: [push, pull_request]
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.12"
      - run: uv sync --extra dev
      - run: uv run pytest -q
```

## 11. References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. Li, L., Zheng, Y., & Zhou, J. (2001). Dynamic model for Pb isotope evolution in the continental crust of China. *Acta Petrologica Sinica*, *17*(1), 61–68.

The baseline target (Table 4) comes from reference 1, Version I is defined by
reference 2, the gates follow reference 3, and the source and validation targets
(Tables 3 and 4) of the China regional model come from reference 4.