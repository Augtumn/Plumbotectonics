# Usage

> **English** | [简体中文](../usage.md)

## 1. Requirements

- Python >= 3.10
- Runtime: `numpy`, `pandas`, `matplotlib`
  - **the three models themselves use only `numpy`** (state held in ndarrays,
    each cycle applied to whole slices);
  - `pandas` is used only by the comparison statistics in
    `scripts/run_version*.py`;
  - `matplotlib` is used only for plotting in `plotting.py`.
- Development: `pytest` (the dev extra in `pyproject.toml` also lists `scipy`,
  which the current source does not use)

## 2. Install

This project uses [uv](https://docs.astral.sh/uv/) for its environment and
dependencies:

```bash
uv sync              # create .venv and install runtime dependencies
uv sync --extra dev  # add the dev dependencies (pytest)
```

> `scripts/*.py` import `plumbotectonics` directly, so run them with `uv run`
> (or activate `.venv` after `uv sync`). Otherwise they fail with
> `ModuleNotFoundError: No module named 'plumbotectonics'`.

## 3. Command line

### 3.1 Version I

```bash
uv run python scripts/run_version1.py
```

Prints the `206/204`, `207/204` and `208/204` ratios of the mantle, orogene,
upper crust and lower crust for all 11 cycles. The same result is compared
cycle by cycle against Table IV of Zartman & Doe (1981) (11 cycles x 4
reservoirs x 3 ratios, 126 rows) and written to
`outputs/results/version1_comparison.csv`.

CSV columns: `t_Ga`, `reservoir`, `ratio`, `model`, `literature`, `abs_diff`
and `rel_error_pct`. At t = 4.0 no crustal segment exists yet, so those rows
are omitted.

### 3.2 Version IV (Table 4 comparison)

```bash
uv run python scripts/run_version4.py
```

Compares the `dp=0.14` model against the 24 values of Haines & Zartman (1988),
Table 4, writes `outputs/results/version4_comparison.csv` (UTF-8 with BOM) and
prints the table to the terminal.

CSV columns are identical to `version1_comparison.csv`: `t_Ga`, `reservoir`,
`ratio`, `model`, `literature`, `abs_diff` and `rel_error_pct` (`t_Ga` is
always 0.0 here, i.e. present day).

### 3.3 China regional model (Li et al. 2001, Table 3 / Table 4 comparison)

```bash
uv run python scripts/run_china.py
```

Prints the mantle, orogene, upper-crust and lower-crust ratios of the 11 cycles,
then the comparison statistics against the paper's Table 3 (99 growth-curve
values) and Table 4 (6 present-day values), the qualitative-ordering check and
the conservation deviation, and writes `outputs/results/china_comparison.csv`.

CSV columns are the same as in the other two comparison tables (`t_Ga`,
`reservoir`, `ratio`, `model`, `literature`, `abs_diff`, `rel_error_pct`); the
six Table 4 rows have `t_Ga` 0.0 and `ratio` either `238U/204Pb` or `Th/U`.

> **Table 3 is not reproduced** (worst absolute deviation 0.5998, against a
> table printed to 0.01). This is not a script failure: the paper's Tables 3 and
> 4 contradict each other, and the new-crustal masses inverted from them differ
> by about 13 sigma. See [`validation.md`](validation.md) section 5.

### 3.4 Growth curves

```bash
uv run python scripts/plot_growth_curves.py
```

Writes into `outputs/figures/`:

| File | Contents |
|---|---|
| `version1_growth_curves.png` / `.pdf` | Version I: three panels (207-206, 208-206, 206-t) |
| `version4_growth_curves.png` / `.pdf` | Version IV (calibrated parameters): four panels (207-206, 208-206, 206-t, 238U/204Pb-t) |

PNG output is 600 dpi, PDF is vector. All figure text is English, so no CJK font is required.

## 4. Python API

### 4.1 Version I

```python
from plumbotectonics.version1 import run, ratios

history, mantle, upper_segs, lower_segs = run()

print(history[0]["t"], history[0]["mantle"])   # 4.0 Ga initial state
print(history[-1]["mantle"])                   # present-day mantle
print(ratios(mantle))
```

### 4.2 Version IV

```python
from plumbotectonics.version4 import run, ratios

result = run(dp=0.14)

print(ratios(result["mantle"]))
print(ratios(result["upper"]))
print(result["masses"])
print(result["history"][-1]["time_Ga"])         # 0.0

# cycle-by-cycle evolution
for h in result["history"]:
    print(h["cycle"], h["time_Ga"], h["upper"])
```

### 4.3 China regional model

```python
from plumbotectonics import china

history, mantle, upper_layers, lower_layers = china.run()

for entry in history:
    print(entry["t"], entry["mantle"], entry["upper"], entry["lower"])

print(china.present_day(mantle, upper_layers, lower_layers))
# {'mantle': {'238U/204Pb': ..., 'Th/U': ...}, 'upper': {...}, 'lower': {...}}

# the two physical conventions (the default follows the paper / ZD1981)
china.run(decay_parents=True)   # paper eqs. (9)-(10), parents really decay, 235U tracked separately
china.run(melt_model="batch")   # batch melting, E = 1/f_m
```

`history[0]` (t = 4.0 Ga) has `upper` / `lower` equal to `None`: no crust
existed before that orogeny. Besides the newly formed layer of each cycle,
`upper_layers` also contains the 10 % sediment layer of each cycle.

`run(strict=True)` (the default) asserts element conservation at the end,
raising `AssertionError` on violation.

### 4.4 Plotting

```python
from plumbotectonics.version1 import run as run_v1
from plumbotectonics.version4 import run as run_v4
from plumbotectonics.plotting import (
    plot_version1_growth_curves,
    plot_version4_growth_curves,
)

hist1, *_ = run_v1()
plot_version1_growth_curves(hist1, "v1.png", "v1.pdf")

res4 = run_v4(dp=0.14)
plot_version4_growth_curves(res4, "v4.png", "v4.pdf")
```

### 4.5 Top-level imports

```python
import plumbotectonics as pt

pt.run_version1()
pt.run_version4(dp=0.14)
pt.v4_ratios(pt.run_version4()["mantle"])
pt.china.run()
```

## 5. Output directory

```
outputs/
|-- figures/   # version1_growth_curves.{png,pdf}, version4_growth_curves.{png,pdf}
`-- results/   # version1_comparison.csv, version4_comparison.csv, china_comparison.csv
    `-- literature/   # source images of the literature values quoted by the tables (static, not generated)
```

`figures/` and `results/*.csv` are created automatically at run time;
`results/literature/` holds static images committed with the repository (see its
`README.md`). All three CSVs have exactly the same column layout, so they can be
concatenated directly.

## 6. Tests

```bash
uv run pytest
```

`pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]`, so
running from the repository root is enough.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: plumbotectonics` | `uv sync` not run, or not using `uv run` | `uv sync` and run through `uv run` |
| `No module named pytest` | dev dependencies not installed | `uv sync --extra dev` |
| `ImportError: Can't determine version for pytz` | pandas / pytz version mismatch | `uv pip install -U --force-reinstall pytz pandas` |
| `run_version4.py` is slow | 46 cycles x 6 isotopes | expected, usually a few seconds |
| `china.run()` raises `AssertionError: ... not conserved` | the element inventory has been broken (most likely when changing partition ratios or the destination of the residual orogene) | use `china.check_conservation()` to locate which nuclide; `run(strict=False)` bypasses it temporarily, but should not be committed |

> `plotting.py` sets `matplotlib.use("Agg")`, so it also runs headless
> (servers, CI).