# Plumbotectonics

Python implementation and validation of the plumbotectonics lead-isotope models.

## Papers

- Zartman, R. E., and Doe, B. R., 1981, *Plumbotectonics-the model*: Tectonophysics, 75, 135-162.
- Haines, S. M., and Zartman, R. E., 1988, *PLUMBO: A Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics*: U.S. Geological Survey Open-File Report 88-269.

The two papers are stored in `papers/`.

## Models

| Module | Model | Reference |
|---|---|---|
| `plumbotectonics.version1` | Version I | Zartman & Doe (1981) |
| `plumbotectonics.version4` | PLUMBO version IV | Haines & Zartman (1988) |

The version IV implementation is calibrated against the ending values printed in
Haines & Zartman (1988), Table 4.  The lower-crust `238U/204Pb` value used for
validation is the self-consistent value **6.4903** (not the inconsistent 6.1903
printed in some copies of the table).

## Install

```bash
pip install -e .
# or
uv pip install -e .
```

## Run

```bash
python scripts/run_version1.py
python scripts/run_version4.py
python scripts/plot_growth_curves.py
```

## Tests

```bash
pytest
```

## Layout

```
src/plumbotectonics/
├── constants.py   # physical constants and initial conditions
├── version1.py    # Zartman & Doe (1981) version I
├── version4.py    # PLUMBO version IV
└── plotting.py    # growth-curve figures
```
