# Correctness guarantees

> **English** | [简体中文](../correctness.md)

This document states why the results can be trusted: a **baseline validation**,
an **invariant** and a **regression** layer, plus the modelling conventions and
the scope of the guarantee. The raw validation data is in
[`validation.md`](validation.md).

## 1. Three-layer guarantee system

| Layer | Mechanism | Artefacts |
|---|---|---|
| 1. Baseline | compare against the printed values of the papers | `tests/test_version1.py`, `tests/test_version4.py` |
| 2. Invariants | conservation laws and structural constraints | `tests/test_conservation.py` |
| 3. Regression | rerun 1+2 on every change | `pytest` (includes the figure layout check in `tests/test_plotting.py`) |

Only when all three pass is a result considered "correct under the model
definition". Current status: **18/18 passing**.

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

## 3. Layer 2: invariants

### 3.1 Mass conservation (exact, the strongest regression signal)

Both models only extract, mix and redistribute material, so mass is neither
created nor destroyed:

| Model | Initial mass | Measured final | Deviation |
|---|---|---|---|
| Version I | 800.0 | 800.000000000 | 0 |
| Version IV | 1050.0 | 1050.000000000 | 0 |

Version IV final reservoirs ($10^{24}$ g):

| mantle | upper | lower | sub | total |
|---|---|---|---|---|
| 1000.1118 | 6.6957 | 15.9128 | 27.2797 | **1050.0000** |

A single wrong partition coefficient breaks this identity immediately, which
makes it more sensitive than "the ratios look close to the paper".

### 3.2 Structural invariants

- Version I adds exactly one upper and one lower segment per cycle (11 + 11);
- all Version I segment masses and isotope mole numbers stay positive;
- Version IV `history` has exactly 46 entries, `cycle` 1-46, time 4.4 -> 0.0 Ga;
- Version IV `total[h] == mantle[h] + upper[h] + lower[h] + sub[h]` (h = 1..6);
- Version IV mantle `206Pb/204Pb` increases monotonically with geological time.

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
| `version4.FNEmoles` | `Bias <= 0` or `Denom == 0` -> returns `0.0` |
| `version4.run`, `V0` | zero segment mass -> `V0 = 0` |
| `version4.run`, isotope split of `S_mant` | denominator `M_m - M_or == 0` -> skipped |
| `version1.ratios` / `version4.ratios` | zero denominator -> `None` |
| `plotting._extract_version4_series` | skips `None` ratios |

`tests/test_conservation.py` covers both `FNEmoles` guards and the zero
denominator branches of `ratios`.

## 6. Reproducibility

- **Pure Python**: the computation uses only the standard library plus
  NumPy/Pandas/Matplotlib, with no external data files;
- **Fully deterministic**: no random numbers, no timestamps, no
  order-dependent parallel reductions;
- **Inputs inline**: initial conditions and Table 3 parameters are declared as
  constants/arrays in the source, with their provenance;
- **Versioned**: `pyproject.toml` declares `version = "0.1.0"` and dependency
  lower bounds.

The same environment and version reproduce bit-identical results.

## 7. Explicit handling of known inconsistencies

| Issue | Handling |
|---|---|
| Some copies of Table 4 print lower-crust `238U/204Pb` as 6.1903, inconsistent with the row | the self-consistent **6.4903** is used as the target and documented |
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
# .github/workflows/tests.yml
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

The baseline target (Table 4) comes from reference 1, Version I is defined by
reference 2, and the gates follow reference 3.