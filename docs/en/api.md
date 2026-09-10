# API reference

> **English** | [简体中文](../api.md)

## Package `plumbotectonics`

`src/plumbotectonics/__init__.py` exposes:

| Name | Meaning |
|---|---|
| `constants` | constants module |
| `run_version1` | `version1.run` |
| `run_version4` | `version4.run` |
| `v4_ratios` | `version4.ratios` |

## `plumbotectonics.constants`

| Constant | Value | Meaning |
|---|---|---|
| `LAMBDA_238` / `LAMBDA_235` / `LAMBDA_232` | 0.155125 / 0.98485 / 0.049475 | decay constants (Ga$^{-1}$) |
| `LAMBDA_87RB` / `LAMBDA_147SM` | 0.0142 / 0.00654 | kept for reference, unused |
| `U8U5` | 137.88 | $^{238}\mathrm{U}/^{235}\mathrm{U}$ |
| `V1_MASS0` ... `V1_NEW_LOWER` | see file | Version I initial conditions |
| `V4_MASS0` ... `V4_CYCLES` | see file | Version IV initial conditions and switches |

> Note: `version1.py` and `version4.py` currently hard-code their own copies of
> these values, so editing `constants.py` does not affect either model (see
> [`validation.md`](validation.md) section 3.2).

## `plumbotectonics.version1`

### `run()`

Runs the 11 cycles of Version I.

**Returns**: `(history, mantle, upper_segs, lower_segs)`

- `history`: `list[dict]`, one entry per cycle:
  `{"t": float, "mantle": dict|None, "orogene": dict|None, "upper": dict|None, "lower": dict|None}`
- `mantle`: `dict` with keys `mass`, `204`, `206`, `207`, `208`, `232`, `238`
- `upper_segs` / `lower_segs`: `list[dict]`, one new segment per cycle, same keys

### `ratios(res)`

Maps a reservoir dictionary to `{"206/204", "207/204", "208/204"}`; returns
`None` when `res["204"] == 0`.

### `avg_res(segs)`

Sums a list of segments and returns `ratios(...)`; returns `None` for an empty
list.

### Module constants

`L238`, `L235`, `L232`, `U8U5`, `MASS0`, `PB2040`, `U2380`, `TH2320`,
`R2060`, `R2070`, `R2080`, `NEW_U`, `NEW_L`, `F_PB`, `F_U`, `F_TH`, `E_M`,
`E_U`, `E_L`.

## `plumbotectonics.version4`

### `run(dp=0.14, double_eroded=False)`

Runs the 46 cycles.

**Parameters**

| Parameter | Default | Meaning |
|---|---|---|
| `dp` | 0.14 | outboard fraction |
| `double_eroded` | `False` | apply the `U_eroded` reduction a second time in the isotope stage |

**Returns**: `dict`

| Key | Type | Meaning |
|---|---|---|
| `mantle` / `upper` / `lower` / `sub` | `dict[int, float]` | final mole numbers, keys 1-6 = 204/206/207/208/232/238 |
| `total` | `dict[int, float]` | sum of the four reservoirs |
| `masses` | `dict[str, float]` | `mantle`/`upper`/`lower`/`sub`/`total` |
| `last_upper` / `last_lower` / `last_sub` | `dict[int, float]` | youngest segment |
| `history` | `list[dict]` | see below |

Each `history` entry:

```python
{
  "cycle": 1,            # 1..46
  "time_Ga": 4.4,        # 4.4 .. 0.0
  "mantle": {...},       # output of ratios()
  "upper": {...},
  "lower": {...},
  "sub": {...},
  "orogene": {...},
}
```

### `ratios(d)`

`d` is keyed 1-6 and the result is:

| Key | Formula |
|---|---|
| `206/204` | `d[2]/d[1]` |
| `207/204` | `d[3]/d[1]` |
| `208/204` | `d[4]/d[1]` |
| `238U/204Pb` | `d[6]/d[1]` |
| `232Th/238U` | `d[5]/d[6]` |
| `232Th/204Pb` | `d[5]/d[1]` |

A zero denominator gives `None`.

### `FNEmoles(N, Mass1, Mass2, Bias)`

The PLUMBO mole-split function (see [`theory.md`](theory.md) section 3.6).
Returns `0.0` when `Bias <= 0` or `Mass1*Bang + Mass2*(1-Bang) == 0`.

### Module constants and arrays

`CYCLES`, `A2`, `A3`, `B1`, `B2`, `B3`, `Bs`, `H0`, `L1`, `L2`, `L3`, `U8U5`,
`INIT_RATIOS`, `A1`, `A4`, `A5`, `A6`, `U`, `L`, `S`, `E_a2`, `F_a3`, `E_b1`,
`E_b2`, `E_b3`, `F_c3`, `E_up`, `E_low`, `E_sub`.

## `plumbotectonics.plotting`

### `plot_version1_growth_curves(history, out_png, out_pdf=None)`

Three panels: 207-206, 208-206, 206-t.

### `plot_version4_growth_curves(result, out_png, out_pdf=None)`

Four panels: 207-206, 208-206, 206-t, 238U/204Pb-t.

Both create the output directory, save a 600 dpi PNG and, when `out_pdf` is
given, a vector PDF.