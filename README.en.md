# Plumbotectonics

**English** | [简体中文](README.md)

Python implementation and validation of the lead-isotope evolution models of
Zartman & Doe (1981) and Haines & Zartman (1988).

Plumbotectonics is a family of mass-balance models: the shallow Earth is
divided into long-lived reservoirs (mantle, upper and lower crust, subcrustal
lithosphere, mid-ocean ridge), and the exchange of matter and isotopes between
them is described by discrete orogenic cycles. Each cycle extracts material
from the mantle and the existing crust, homogenises it inside an orogene, and
redistributes it among the reservoirs; between cycles only radioactive decay
occurs.

## Features

- Pure-Python implementations (no third-party dependency beyond NumPy) of
  **Version I** (Zartman & Doe, 1981) and
  **Version IV** (Haines & Zartman, 1988) plus the **China continental regional
  model** (Li et al., 2001);
- Reproduces all 24 present-day values of Haines & Zartman (1988), Table 4
  (worst absolute deviation **0.00993**, test tolerance 0.02); two of those
  targets come from scan-OCR misreads and are **not yet corrected**, see
  [`docs/en/validation.md`](docs/en/validation.md) section 4.8;
- Reproduces all 126 growth-curve values of Zartman & Doe (1981), Table IV
  (worst absolute deviation **0.00509**, the two-decimal printing limit);
- Publication-style growth curves for Version I and Version IV (600 dpi PNG +
  vector PDF).

## Models

| Module | Model | Reference |
|---|---|---|
| `plumbotectonics.version1` | Version I | Zartman & Doe (1981) |
| `plumbotectonics.version4` | Version IV | Haines & Zartman (1988) |
| `plumbotectonics.china` | China continental regional model | Li et al. (2001) |

Version I is a two-reservoir (mantle + crust) mass balance in which orogene
material is split between the returning mantle and the new upper/lower crust
by fixed partition ratios (`F_PB`/`F_U`/`F_TH`) weighted by the mass of each
returning increment. Version IV adds the mid-ocean-ridge (MOR)
reservoir, the subcrustal lithosphere, a three-component orogene
(distal / proximal / wedge) and explicit mass-exchange gates.

The physical picture behind the bi-directional transport between the orogene
and the subcrustal lithosphere comes from Zartman & Haines (1988).

`china` is a **regional variant of Version I**: the algorithm follows Zartman &
Doe (1981) exactly and only replaces the two tables the paper prints itself,
Table 1 (4.0 Ga initial ratios) and Table 2 (partition ratios), and changes the
lower-crust retention to $p^l=0.95$, with 90 % of the residual orogene returning
to the mantle. Everything the paper does not give (initial element abundances,
new-crustal mass, decay constants, $k_i$) is inherited from ZD1981, so the model
has **zero free parameters**. It reproduces Table 4 to 0.47 but does **not**
reproduce Table 3 (worst deviation 0.62) - the reason is in
[`docs/en/validation.md`](docs/en/validation.md) section 5.

## Install

This project uses [uv](https://docs.astral.sh/uv/) for its environment and
dependencies; Python >= 3.10 is required:

```bash
uv sync              # create .venv and install runtime dependencies
uv sync --extra dev  # add the dev dependencies (pytest)
```

Runtime dependencies are `numpy`, `pandas` and `matplotlib`. **The three models
use NumPy only** (`version1.py` and `version4.py` both `import numpy as np`,
with the state held in arrays and each cycle applied to whole slices):
`pandas` serves the comparison statistics in `scripts/` and `matplotlib` only
the plotting. See [`docs/en/usage.md`](docs/en/usage.md).

## Run

```bash
uv run python scripts/run_version1.py        # Version I growth history (stdout)
uv run python scripts/run_version4.py        # Table 4 comparison -> outputs/results/
uv run python scripts/run_china.py           # paper Table 3/Table 4 comparison -> outputs/results/
uv run python scripts/plot_growth_curves.py  # growth-curve figures -> outputs/figures/
```

Generated tables and figures are written to `outputs/`.

## Documentation

Full documentation is available in both languages:

| English | Chinese | Contents |
|---|---|---|
| [`docs/en/theory.md`](docs/en/theory.md) | [`docs/theory.md`](docs/theory.md) | Theory: mass and isotope transfer, partition functions and decay for each model |
| [`docs/en/usage.md`](docs/en/usage.md) | [`docs/usage.md`](docs/usage.md) | Install, CLI, Python API and troubleshooting |
| [`docs/en/api.md`](docs/en/api.md) | [`docs/api.md`](docs/api.md) | Modules, functions, parameters and return structures |
| [`docs/en/validation.md`](docs/en/validation.md) | [`docs/validation.md`](docs/validation.md) | Table IV / Table 4 comparison, source images, calibration notes, reproduction conclusions for the China model and known issues |
| [`docs/en/correctness.md`](docs/en/correctness.md) | [`docs/correctness.md`](docs/correctness.md) | Correctness guarantees: three layers, invariants, CI |

## Layout

- `src/plumbotectonics/` - model implementations (`constants.py`,
  `version1.py`, `version4.py`, `china.py`, `plotting.py`)
- `scripts/` - command-line entry points
- `tests/` - pytest validation suite
- `papers/` - source papers
- `outputs/` - generated tables and figures; `outputs/results/literature/` holds
  the **source images** of the literature values the two comparison tables quote
  (not generated)
- `docs/` - documentation (Chinese), `docs/en/` (English)

## Tests

```bash
uv run pytest
```

Coverage: all 126 Table IV rows of Version I (11 cycles x 4 reservoirs x 3
ratios, tolerance 0.006) and the 12 element abundances of Table II section
III.B, the 24 Table 4 ratios of the four Version IV reservoirs
(`abs(diff) < 0.02`), the mass-conservation and structural invariants of all
three models (`tests/test_conservation.py`), the element conservation and
qualitative ordering of the China model (`tests/test_china.py`) plus the figure
layout and PDF reproducibility (`tests/test_plotting.py`: no titled overlap, no
embedded timestamp) and the post-migration dependency boundary and public
return structure (`tests/test_conservation.py`). Current status: **33/33
passing**.

## Validation

Version IV is calibrated against the present-day values of Haines & Zartman
(1988), Table 4. The lower-crust `238U/204Pb` used for validation is the value
printed in the scan, **6.4903** (the PDF text layer's OCR misreads it as
6.1903).

Worst deviation from Table 4 at `dp=0.14` over 46 cycles:

| Reservoir | worst `abs(diff)` | ratio |
|---|---|---|
| mantle | 0.00049 | 208Pb/204Pb |
| upper crust | 0.00017 | 207Pb/204Pb |
| lower crust | 0.00033 | 232Th/204Pb |
| subcrustal | 0.00993 | 232Th/204Pb |

> **Caveat**: the subcrustal `207Pb/204Pb` and `232Th/204Pb` targets are
> themselves text-layer misreads (the image prints 15.44000 / 35.54200, this
> table uses 15.110 / 35.512), so those two rows do not actually pass. See
> [`docs/en/validation.md`](docs/en/validation.md) section 4.8.

See [`docs/en/validation.md`](docs/en/validation.md) for the full table.

Version I is validated against the growth curves of Zartman & Doe (1981),
Table IV: the worst deviation over all 126 rows (11 cycles x 4 reservoirs x 3
ratios) is **0.00509**, which is the two-decimal printing limit of that table,
and all 12 element abundances of Table II section III.B land within 1 %.

The China regional model (Li et al. 2001) is validated against the paper's
Tables 3 and 4:

| Data | max absolute difference | mean | RMSE |
|---|---|---|---|
| paper Table 3 (99 growth-curve values) | 0.5998 | 0.1322 | 0.2016 |
| paper Table 4 (6 present-day values) | 0.6031 | 0.2550 | 0.3481 |

> **Table 3 is not reproduced** (the table is printed to 0.01 and only 11/99
> fall inside +-0.005). The new-crustal masses inverted from the two tables
> differ by about 13 sigma, showing that **the paper's two tables are mutually
> incompatible**; the paper also has 5 further inconsistencies between its text
> and its tables. See [`docs/en/validation.md`](docs/en/validation.md) section 5.

## Correctness guarantees

Results are pinned by three independent layers; see
[`docs/en/correctness.md`](docs/en/correctness.md):

1. **Baseline validation** - Version IV reproduces all 24 present-day values
   of Haines & Zartman (1988), Table 4 (`abs(diff) < 0.02`); Version I
   reproduces all 126 values of Zartman & Doe (1981), Table IV (worst 0.00509,
   the printing precision) and the 12 element abundances of Table II section
   III.B (within 1 %); the China model reproduces the paper's Table 4 (worst
   0.6031) - Table 3 is explicitly listed as **not reproduced** and is pinned by
   regression ceilings in `tests/test_china.py`.
2. **Invariants** - total mass is conserved exactly in all three models
   (Version I: 800; Version IV: 1050; China model: 800), and the China model
   conserves its element inventory (204Pb, 238U, 232Th), pinned by
   `tests/test_conservation.py` and `tests/test_china.py` together with
   structural checks.
3. **Regression tests** - `uv run pytest` reruns both layers on every change.

> Total *mole* numbers are **not** conserved, by design: the published models
> hold the parent isotopes (238U, 232Th) constant across each decay interval,
> so Pb grows without depleting them. That is a modelling convention, not an
> implementation bug - see [`docs/en/correctness.md`](docs/en/correctness.md) section 4.
>
> The China model also offers a switchable conservation parameterisation
> (`decay_parents=True`, paper eqs. 9-10), in which the parents really decay and
> 235U is tracked separately; the "daughter + parent" sums are then conserved
> exactly. The two forms are **equivalent digit for digit**.

## References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. Li, L., Zheng, Y., & Zhou, J. (2001). Dynamic model for Pb isotope evolution in the continental crust of China. *Acta Petrologica Sinica*, *17*(1), 61–68.

Reference 3 gives the physical basis for the bi-directional transport
implemented by this project's gates; reference 4 is the source of the China
regional model (`plumbotectonics.china`).

`papers/` bundles the PDFs of all four references:

| Reference | Local file |
|---|---|
| 1 Haines & Zartman (1988) | `papers/Haines_Zartman_1988_PLUMBO.pdf` |
| 2 Zartman & Doe (1981) | `papers/Zartman_Doe_1981_Plumbotectonics.pdf` |
| 3 Zartman & Haines (1988) | `papers/Zartman_Haines_1988_Bidirectional.pdf` |
| 4 Li et al. (2001) | `papers/Dynamic+model+for+Pb+isotope+evolution+in+the+continental+crust+of+China..pdf` |