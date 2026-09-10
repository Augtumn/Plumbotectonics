# Usage

> **English** | [简体中文](../usage.md)

## 1. Requirements

- Python >= 3.10
- Runtime: `numpy`, `pandas`, `matplotlib`
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
upper crust and lower crust for all 11 cycles. The same table is written to
`outputs/results/version1_history.csv` (UTF-8 with BOM, stdlib `csv`, no pandas).

### 3.2 Version IV (Table 4 comparison)

```bash
uv run python scripts/run_version4.py
```

Compares the `dp=0.14` model against the 24 values of Haines & Zartman (1988),
Table 4, writes `outputs/results/version4_comparison.csv` (UTF-8 with BOM) and
prints the table to the terminal.

CSV columns: `reservoir`, `ratio`, `model`, `table`, `abs_diff`.

### 3.3 Growth curves

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

### 4.3 Plotting

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

### 4.4 Top-level imports

```python
import plumbotectonics as pt

pt.run_version1()
pt.run_version4(dp=0.14)
pt.v4_ratios(pt.run_version4()["mantle"])
```

## 5. Output directory

```
outputs/
|-- figures/   # version1_growth_curves.{png,pdf}, version4_growth_curves.{png,pdf}
`-- results/   # version1_history.csv, version4_comparison.csv
```

Directories are created automatically at run time.

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

> `plotting.py` sets `matplotlib.use("Agg")`, so it also runs headless
> (servers, CI).