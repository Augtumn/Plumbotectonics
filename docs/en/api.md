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
> these values, so editing `constants.py` does not affect any of the three
> models (see [`validation.md`](validation.md) section 4.2).

## `plumbotectonics.version1`

### `run()`

Runs the 11 cycles of Version I.

Each cycle extracts per eqs. 14-16, redistributes per eqs. 17-19 (the
`F_PB`/`F_U`/`F_TH` partition ratios are weighted by returning-increment mass,
see [`theory.md`](theory.md) section 2.5) and decays per eqs. 20-22.
`history` records the state **before** each orogeny, matching the instant used
by Table IV.

The internal state is carried in NumPy arrays: each reservoir is an
`(n_segs, 6)` array whose columns follow the module constant
`ISO_KEYS = ("204","206","207","208","232","238")`, and extraction,
redistribution and decay all act on whole slices.  **The return structure is
unchanged** -- the plain `dict`s below.

**Returns**: `(history, mantle, upper_segs, lower_segs)`

- `history`: `list[dict]`, one entry per cycle:
  `{"t": float, "mantle": dict|None, "orogene": dict|None, "upper": dict|None, "lower": dict|None}`
- `mantle`: `dict` with keys `mass`, `204`, `206`, `207`, `208`, `232`, `238`
- `upper_segs` / `lower_segs`: `list[dict]`, one new segment per cycle, same keys

### `ratios(res)`

Maps a reservoir dictionary to `{"206/204", "207/204", "208/204"}`; returns
`None` when `res["204"] == 0`.  An internal length-6 NumPy row may also be
passed directly.

### `avg_res(segs)`

Sums a list of segments and returns `ratios(...)`; returns `None` for an empty
list.

### `row_to_dict(row, mass)`

Converts an internal length-6 row plus its mass into the segment dict above
(`run()` calls it just before returning).

### Module constants

`L238`, `L235`, `L232`, `U8U5`, `MASS0`, `PB2040`, `U2380`, `TH2320`,
`R2060`, `R2070`, `R2080`, `NEW_U`, `NEW_L`, `ERO_U`, `ERO_L`, `ISO_KEYS`,
`F_PB`, `F_U`, `F_TH`, `E_M`, `E_U`, `E_L`.

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

The Version IV mole-split function (see [`theory.md`](theory.md) section 3.6).
It works **elementwise**, so a whole length-6 isotope axis can be passed at
once, which is what `run()` does.  It returns `0` when `Bias <= 0` or
`Mass1*Bang + Mass2*(1-Bang) == 0`: previously a branch returning `0.0`, now a
mask with `np.divide(..., where=...)` -- the same values, and no
`RuntimeWarning`.

### Module constants and arrays

`CYCLES`, `A2`, `A3`, `B1`, `B2`, `B3`, `Bs`, `H0`, `L1`, `L2`, `L3`, `U8U5`,
`INIT_RATIOS`, `ISO`, `A1`, `A4`, `A5`, `A6`, `U`, `L`, `S`, `E_a2`, `F_a3`,
`E_b1`, `E_b2`, `E_b3`, `F_c3`, `E_up`, `E_low`, `E_sub` (`A*`, `U`, `L`, `S`
and the `E_*` arrays are now `np.ndarray`; indexing is unchanged).

## `plumbotectonics.china`

The Li et al. (2001) China continental regional model. The algorithm follows
Zartman & Doe (1981) (i.e. `version1`) and only replaces the paper's Table 1 and
Table 2, changes the lower-crust retention to $p^l=0.95$ and returns 90 % of the
residual orogene to the mantle. **Zero free parameters** (everything not given
by the paper is inherited from ZD1981).

### `run(decay_parents=False, melt_model="zd1981", strict=True)`

| Parameter | Default | Meaning |
|---|---|---|
| `decay_parents` | `False` | `False` = ZD1981 constant parents; `True` = the paper's eqs. (9)(10), parents really decay (235U tracked separately). **The two are equivalent digit for digit** |
| `melt_model` | `"zd1981"` | `"zd1981"` = $E_m$ fixed at 4; `"batch"` = batch melting $E=1/f_m$ |
| `strict` | `True` | assert element-inventory conservation at the end, raising `AssertionError` on violation |

Returns `(history, mantle, upper_segs, lower_segs)`:

- `history`: 11 dicts keyed `t`, `mantle`, `orogene`, `upper`, `lower`; the
  first three reservoirs hold `{'206/204', '207/204', '208/204'}` and
  **`upper`/`lower` are `None` at t=4.0 Ga** (there is no crust before that
  orogeny);
- `mantle`: dict holding `mass` and the `ISO_KEYS` entries;
- `upper_segs` / `lower_segs`: list of dict, one per layer (including the 10 %
  sediment layer, counted as upper crust).

### `present_day(mantle, upper_segs, lower_segs)`

Returns `{'mantle'|'upper'|'lower': {'238U/204Pb': float, 'Th/U': float}}`,
i.e. the two quantities of the paper's Table 4.

### `check_conservation(mantle, upper, lower, decay_parents=False, rtol=1e-9)`

Checks the element inventory. With `decay_parents=False` it checks 204Pb, 238U
and 232Th; with `True` it checks 204Pb and the three "daughter + parent" sums
(238U itself decays to today's 349 and is no longer conserved). Returns a dict of
relative deviations and raises `AssertionError` when a bound is exceeded.

### `e_mantle(f_m, melt_model="zd1981")`

Enrichment factor of the material contributed by the mantle: `"zd1981"` returns
4; `"batch"` returns $1/f_m$; any other value raises `ValueError`.

### `ratios(res)` / `row_to_dict(row, mass)`

Same semantics as the functions of the same name in `version1`.

### Module constants

| Constant | Value | Source |
|---|---|---|
| `R2060`/`R2070`/`R2080` | 10.17 / 12.07 / 30.56 | paper Table 1 |
| `F_PB`/`F_U`/`F_TH` | (0.038, 0.727, 0.235) / (0.024, 0.865, 0.111) / (0.021, 0.817, 0.162) | paper Table 2, converted to the ZD1981 (mantle, upper, lower) column order |
| `P_UPPER`/`P_LOWER` | 0.63 / 0.95 | paper eq. (2) |
| `E_M`/`E_U`/`E_L` | 4.0 / 1.0 / 1.0 | paper eq. (5) |
| `RETURN` | 0.9 | paper eqs. (7)(8) |
| `PB2040`/`U2380`/`TH2320` | 38 / 349 / 1335 | ZD1981 Table II (inherited) |
| `MASS0`/`NEW_U`/`NEW_L` | 800 / 2.6 / 2.6 | ZD1981 Table II (inherited) |
| `ISO_KEYS` | `("204","206","207","208","232","238","235")` | one 235U more than `version1` |

## `plumbotectonics.plotting`

### `plot_version1_growth_curves(history, out_png, out_pdf=None)`

Three panels: 207-206, 208-206, 206-t.

### `plot_version4_growth_curves(result, out_png, out_pdf=None)`

Four panels: 207-206, 208-206, 206-t, 238U/204Pb-t.

Both create the output directory, save a 600 dpi PNG and, when `out_pdf` is
given, a vector PDF.