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

- Pure-Python implementations of **Version I** (Zartman & Doe, 1981) and
  **Version IV** (Haines & Zartman, 1988);
- Reproduces all 24 present-day values of Haines & Zartman (1988), Table 4
  (worst absolute deviation **0.00993**, test tolerance 0.02);
- Publication-style growth curves for both models (600 dpi PNG + vector PDF).

## Models

| Module | Model | Reference |
|---|---|---|
| `plumbotectonics.version1` | Version I | Zartman & Doe (1981) |
| `plumbotectonics.version4` | Version IV | Haines & Zartman (1988) |

Version I is a two-reservoir (mantle + crust) mass balance with fixed
partition coefficients. Version IV adds the mid-ocean-ridge (MOR)
reservoir, the subcrustal lithosphere, a three-component orogene
(distal / proximal / wedge) and explicit mass-exchange gates.

The physical picture behind the bi-directional transport comes from
Zartman & Haines (1988).

## Install

This project uses [uv](https://docs.astral.sh/uv/) for its environment and
dependencies; Python >= 3.10 is required:

```bash
uv sync              # create .venv and install runtime dependencies
uv sync --extra dev  # add the dev dependencies (pytest)
```

Runtime dependencies are `numpy`, `pandas` and `matplotlib`.

## Run

```bash
uv run python scripts/run_version1.py        # Version I growth history (stdout)
uv run python scripts/run_version4.py        # Table 4 comparison -> outputs/results/
uv run python scripts/plot_growth_curves.py  # growth-curve figures -> outputs/figures/
```

Generated tables and figures are written to `outputs/`.

## Documentation

Full documentation is available in both languages:

| English | Chinese | Contents |
|---|---|---|
| [`docs/en/theory.md`](docs/en/theory.md) | [`docs/theory.md`](docs/theory.md) | Theory: mass and isotope transfer, partition functions and decay |
| [`docs/en/usage.md`](docs/en/usage.md) | [`docs/usage.md`](docs/usage.md) | Install, CLI, Python API and troubleshooting |
| [`docs/en/api.md`](docs/en/api.md) | [`docs/api.md`](docs/api.md) | Modules, functions, parameters and return structures |
| [`docs/en/validation.md`](docs/en/validation.md) | [`docs/validation.md`](docs/validation.md) | Table 4 comparison, calibration notes and known issues |
| [`docs/en/correctness.md`](docs/en/correctness.md) | [`docs/correctness.md`](docs/correctness.md) | Correctness guarantees: three layers, invariants, CI |

## Layout

- `src/plumbotectonics/` - model implementations (`constants.py`,
  `version1.py`, `version4.py`, `plotting.py`)
- `scripts/` - command-line entry points
- `tests/` - pytest validation suite
- `papers/` - source papers
- `outputs/` - generated tables and figures
- `docs/` - documentation (Chinese), `docs/en/` (English)

## Tests

```bash
uv run pytest
```

Coverage: the initial and present-day mantle ratios of Version I, the 24
Table 4 ratios of the four Version IV reservoirs (`abs(diff) < 0.02`), and the
mass-conservation and structural invariants of both models
(`tests/test_conservation.py`) plus the figure layout (`tests/test_plotting.py`). Current status: **14/14 passing**.

## Validation

Version IV is calibrated against the present-day values of Haines & Zartman
(1988), Table 4. The lower-crust `238U/204Pb` used for validation is the
self-consistent value **6.4903** (some copies of the table print 6.1903,
which is inconsistent with the rest of the row).

Worst deviation from Table 4 at `dp=0.14` over 46 cycles:

| Reservoir | worst `abs(diff)` | ratio |
|---|---|---|
| mantle | 0.00049 | 208Pb/204Pb |
| upper crust | 0.00017 | 207Pb/204Pb |
| lower crust | 0.00033 | 232Th/204Pb |
| subcrustal | 0.00993 | 232Th/204Pb |

See [`docs/en/validation.md`](docs/en/validation.md) for the full table.

## Correctness guarantees

Results are pinned by three independent layers; see
[`docs/en/correctness.md`](docs/en/correctness.md):

1. **Baseline validation** - Version IV reproduces all 24 present-day values
   of Haines & Zartman (1988), Table 4 (`abs(diff) < 0.02`); Version I matches
   the initial and present-day mantle ratios of Zartman & Doe (1981).
2. **Invariants** - total mass is conserved exactly in both models
   (Version I: 800; Version IV: 1050), pinned by
   `tests/test_conservation.py` together with structural checks.
3. **Regression tests** - `uv run pytest` reruns both layers on every change.

> Total *mole* numbers are **not** conserved, by design: the published models
> hold the parent isotopes (238U, 232Th) constant across each decay interval,
> so Pb grows without depleting them. That is a modelling convention, not an
> implementation bug - see [`docs/en/correctness.md`](docs/en/correctness.md) section 4.

## References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9

Reference 3 gives the physical basis for the bi-directional transport
implemented by this project's gates.

`papers/` contains the PDFs of references 1 and 2; reference 3 is not bundled.