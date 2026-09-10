# Plumbotectonics

Python implementation and validation of the plumbotectonics lead-isotope
models of Zartman & Doe (1981) and Haines & Zartman (1988).

Plumbotectonics is a family of mass-balance models that track Pb, U and Th
through Earth's major reservoirs (mantle, upper and lower crust, subcrustal
lithosphere, mid-ocean ridge) over discrete orogenic cycles. Each cycle
extracts material from the mantle and existing crust, homogenizes it in an
orogene, and redistributes it among the reservoirs; between cycles only
radioactive decay occurs.

> 中文文档见 [`docs/`](docs/)：计算原理、用法、API 与校验数据。

## Features

- Pure-Python implementations of **Version I** (Zartman & Doe, 1981) and
  **Version IV / PLUMBO** (Haines & Zartman, 1988).
- Reproduces the ending values of Haines & Zartman (1988), Table 4
  (worst absolute deviation **0.00993**, test tolerance 0.02).
- Publication-style growth-curve figures for both models.

## Models

| Module | Model | Reference |
|---|---|---|
| `plumbotectonics.version1` | Version I | Zartman & Doe (1981) |
| `plumbotectonics.version4` | PLUMBO version IV | Haines & Zartman (1988) |

Version I uses a two-reservoir (mantle + crust) mass balance with fixed
partition coefficients. Version IV (PLUMBO) adds the MOR reservoir, the
subcrustal lithosphere, a three-component orogene (distal / proximal / wedge)
and explicit mass-exchange gates.

## Install

```bash
pip install -e .
# or
uv pip install -e .
```

Requires Python >= 3.10 (`numpy`, `pandas`, `matplotlib`).

If you prefer not to install, run from the repository root with `src` on the
path:

```bash
# bash
PYTHONPATH=src python scripts/run_version1.py
```

```powershell
# PowerShell
$env:PYTHONPATH = "src"
python scripts\run_version1.py
```

## Run

```bash
python scripts/run_version1.py        # Version I growth history (stdout)
python scripts/run_version4.py        # Table 4 comparison -> outputs/results/
python scripts/plot_growth_curves.py  # figures -> outputs/figures/
```

Generated tables and figures are written to `outputs/`.

## Documentation

| Document | Contents |
|---|---|
| [`docs/theory.md`](docs/theory.md) | 计算原理：两版本的质量/同位素传输、分配函数与衰变 |
| [`docs/usage.md`](docs/usage.md) | 安装、命令行、Python API 与故障排查 |
| [`docs/api.md`](docs/api.md) | 模块、函数、返回数据结构参考 |
| [`docs/validation.md`](docs/validation.md) | Table 4 校验数据、标定说明与已知问题 |
| [`docs/correctness.md`](docs/correctness.md) | 结果正确性保证：三层保证体系、守恒不变量、CI |

## Layout

- `src/plumbotectonics/` - model implementations (`constants.py`,
  `version1.py`, `version4.py`, `plotting.py`)
- `scripts/` - command-line entry points
- `tests/` - pytest validation suite
- `papers/` - source papers
- `outputs/` - generated tables and figures
- `docs/` - documentation

## Tests

```bash
pytest
```

The suite checks the initial and present-day mantle ratios for Version I and
all four reservoirs of Version IV against Table 4 (`abs(diff) < 0.02`), and the
mass-conservation invariants of both models (`tests/test_conservation.py`).

## Validation

The version IV implementation is calibrated against the ending values printed
in Haines & Zartman (1988), Table 4. The lower-crust `238U/204Pb` value used
for validation is the self-consistent value **6.4903** (not the inconsistent
6.1903 printed in some copies of the table).

Measured worst deviation from Table 4 (`dp=0.14`, 46 cycles):

| Reservoir | worst `abs(diff)` | ratio |
|---|---|---|
| mantle | 0.00049 | 208Pb/204Pb |
| upper crust | 0.00017 | 207Pb/204Pb |
| lower crust | 0.00033 | 232Th/204Pb |
| subcrustal | 0.00993 | 232Th/204Pb |

See [`docs/validation.md`](docs/validation.md) for the full table.

## Correctness guarantees

Results are pinned by three independent layers; see
[`docs/correctness.md`](docs/correctness.md) for the full argument.

1. **Baseline validation** - Version IV reproduces all 24 ending values of
   Haines & Zartman (1988), Table 4 (`abs(diff) < 0.02`); Version I matches the
   initial and present-day mantle ratios of Zartman & Doe (1981).
2. **Invariants** - total mass is conserved exactly in both models
   (Version I: 800; Version IV: 1050), pinned by
   `tests/test_conservation.py` together with structural checks.
3. **Regression tests** - `pytest` reruns both layers on every change.

> Total *mole* numbers are **not** conserved, by design: the published models
> hold the parent isotopes (238U, 232Th) constant across each decay interval,
> so Pb grows without depleting them. That is a modelling convention, not an
> implementation bug - see [`docs/correctness.md`](docs/correctness.md) section 4.

## References

- Zartman, R. E., and Doe, B. R., 1981, *Plumbotectonics-the model*:
  Tectonophysics, 75, 135-162.
- Haines, S. M., and Zartman, R. E., 1988, *PLUMBO: A Hewlett-Packard Series
  200 BASIC language program for version IV of plumbotectonics*: U.S.
  Geological Survey Open-File Report 88-269.

Both papers are stored in `papers/`.
