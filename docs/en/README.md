# Documentation

> **English** | [简体中文](../README.md)

| Document | Contents |
|---|---|
| [theory.md](theory.md) | Theory: framework, Version I, Version IV, China regional model, comparison |
| [usage.md](usage.md) | Requirements, install, CLI, Python API, troubleshooting |
| [api.md](api.md) | Modules, functions, parameters and return structures |
| [validation.md](validation.md) | Table IV / Table 4 comparison, source images, calibration notes, reproduction conclusions for the China model, known issues |
| [correctness.md](correctness.md) | Correctness guarantees: three layers, invariants, CI |

## Quick navigation

- Want the equations? -> [theory.md](theory.md)
- Want to run it? -> [usage.md](usage.md)
- Want to call it from code? -> [api.md](api.md)
- Want to know how accurate it is? -> [validation.md](validation.md)
- Want to know why the results are trustworthy? -> [correctness.md](correctness.md)

## Documentation to source map

| Section | Source |
|---|---|
| `theory.md` section 2 | `src/plumbotectonics/version1.py` |
| `theory.md` section 3 | `src/plumbotectonics/version4.py` |
| `theory.md` section 4 | `src/plumbotectonics/china.py` |
| `api.md` | `src/plumbotectonics/*.py` |
| `validation.md` | `tests/`, `scripts/run_version1.py`, `scripts/run_version4.py`, `scripts/run_china.py`, `outputs/results/literature/` |

Back to the project home: [`../../README.en.md`](../../README.en.md).