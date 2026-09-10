# Theory

> **English** | [简体中文](../theory.md)

This document describes the calculation flow of the two models (Version I and
Version IV) and maps it onto `src/plumbotectonics/version1.py` and
`version4.py`.

## 1. Overall framework

Plumbotectonics divides the shallow Earth into long-lived **reservoirs** and
describes the exchange of matter and isotopes between them with discrete
**orogenic cycles**. Each cycle has three steps:

1. **Extraction** - material is taken from the mantle and the existing crust;
2. **Homogenisation** - the extracted material is fully mixed inside an orogene;
3. **Redistribution** - the orogene material is partitioned into new upper
   crust, new lower crust (plus, in Version IV, subcrustal lithosphere) and
   material returned to the mantle.

Between cycles only radioactive decay occurs inside a reservoir.

**Time convention**

- geological time $t$ runs from the present into the past ($t=0$ is today), in
  Ga;
- cycles are numbered from the oldest to the youngest;
- decay constants are in Ga$^{-1}$.

**Notation**: $^{204}\mathrm{Pb}$ is written 204, $^{206}\mathrm{Pb}$ 206,
$^{207}\mathrm{Pb}$ 207, $^{208}\mathrm{Pb}$ 208, $^{232}\mathrm{Th}$ 232 and
$^{238}\mathrm{U}$ 238.

---

## 2. Version I: Zartman & Doe (1981)

Implementation: `plumbotectonics.version1.run()`

### 2.1 Initial conditions

| Quantity | Key | Value |
|---|---|---|
| start time | - | 4.0 Ga |
| number of cycles | - | 11 (one every 0.4 Ga) |
| mantle mass | `mass` | $800\times10^{24}$ g |
| 204 | `204` | $38\times10^{15}$ mol |
| 238 | `238` | $349\times10^{15}$ mol |
| 232 | `232` | $1335\times10^{15}$ mol |
| 206/204 | - | 10.36 |
| 207/204 | - | 12.12 |
| 208/204 | - | 30.55 |

Decay constants: $\lambda_{238}=0.155125$, $\lambda_{235}=0.98485$,
$\lambda_{232}=0.049475$ Ga$^{-1}$; $^{238}\mathrm{U}/^{235}\mathrm{U}=137.88$.

### 2.2 Cycle schedule

Cycle $j$ ($j=0,\dots,10$) is at $t_j = 4.0 - 0.4j$, and the mantle
contributes this fraction of its own mass:

$$
f_m=\begin{cases}
1/8, & j=0\\
1/16, & j=1\\
1/32, & j=2\\
1/64, & j=3\\
1/128, & j\ge 4
\end{cases}
$$

i.e. it halves four times and then stays at $1/128$.

### 2.3 Material extracted into the orogene (mass)

With a vertical erosion function $f_v=0.3$ and an areal one $f_h=0.1$, each
older upper-crust segment loses

$$
\Delta M_u^{(i)} = (f_v+f_h-f_vf_h)\,M_u^{(i)} = 0.37\,M_u^{(i)} .
$$

Lower crust is affected by areal erosion only:

$$
\Delta M_l^{(i)} = f_h M_l^{(i)} = 0.10\,M_l^{(i)} .
$$

The mantle contributes $\Delta M_m = f_m M_m$, so the orogene mass is

$$
M_{or} = \Delta M_m + \sum_i \Delta M_u^{(i)} + \sum_i \Delta M_l^{(i)} .
$$

### 2.4 Isotope increments

For every isotope $X\in\{204,206,207,208,232,238\}$:

$$
\Delta X_m = f_m E_m X_m ,\qquad
\Delta X_u^{(i)} = 0.37\,E_u X_u^{(i)} ,\qquad
\Delta X_l^{(i)} = 0.10\,E_l X_l^{(i)} ,
$$

with the mantle enrichment factor $E_m=4$ and $E_u=E_l=1$ for the crust. The
amount of that isotope inside the orogene is

$$
X_{or} = \Delta X_m + \sum_i \Delta X_u^{(i)} + \sum_i \Delta X_l^{(i)} .
$$

### 2.5 Redistribution of the orogene

Each cycle creates new upper and lower crust of

$$
M_u^{\mathrm{new}} = M_l^{\mathrm{new}} = 2.6\times10^{24}\ \mathrm{g},
$$

and the rest returns to the mantle. Pb, U and Th are partitioned between
(returned mantle, new upper crust, new lower crust) as

| Element | Mantle | Upper crust | Lower crust |
|---|---|---|---|
| Pb | 0.028 | 0.754 | 0.218 |
| U | 0.024 | 0.854 | 0.122 |
| Th | 0.020 | 0.788 | 0.192 |

(`F_PB`, `F_U`, `F_TH`; each row sums to 1). Hence

$$
X_m \leftarrow X_m - \Delta X_m + f^{\mathrm{Pb/U/Th}}_{\mathrm{mantle}} X_{or},
$$

and the new upper/lower segments take $f_{\mathrm{upper}}X_{or}$ and
$f_{\mathrm{lower}}X_{or}$.

The mantle mass becomes

$$
M_m \leftarrow M_m - \Delta M_m + (M_{or} - 2.6 - 2.6),
$$

while older upper and lower segments shrink by factors 0.63 and 0.90.

### 2.6 Radioactive decay

Between cycles the parents are treated as constant and the daughters grow as

$$
\begin{aligned}
^{206}\mathrm{Pb}(t') &= ^{206}\mathrm{Pb}(t'') + ^{238}\mathrm{U}\left(e^{\lambda_{238}t'}-e^{\lambda_{238}t''}\right),\\
^{207}\mathrm{Pb}(t') &= ^{207}\mathrm{Pb}(t'') + \frac{^{238}\mathrm{U}}{137.88}\left(e^{\lambda_{235}t'}-e^{\lambda_{235}t''}\right),\\
^{208}\mathrm{Pb}(t') &= ^{208}\mathrm{Pb}(t'') + ^{232}\mathrm{Th}\left(e^{\lambda_{232}t'}-e^{\lambda_{232}t''}\right),
\end{aligned}
$$

with $t'=t_j$ and $t''=t_{j+1}=t_j-0.4$.

### 2.7 Output

`run()` returns the tuple `(history, mantle, upper_segs, lower_segs)`.

Each `history` entry:

```python
{
  "t": 4.0,                        # Ga
  "mantle":  {"206/204": ..., "207/204": ..., "208/204": ...},
  "orogene": {...},                # mixed orogene ratio for that cycle
  "upper":   {...} | None,         # mole-weighted average over upper segments
  "lower":   {...} | None,
}
```

> In the first cycle there is no pre-existing crust yet, so `upper`/`lower`
> are `None`. Segment reservoirs are summed before taking ratios (`avg_res`).

---

## 3. Version IV: Haines & Zartman (1988)

Implementation: `plumbotectonics.version4.run()`

> This chapter describes the Version IV implementation. The physical basis of the
> three-component orogene and of the bi-directional transport (the gates of
> section 3.5) is given in Zartman & Haines (1988).

### 3.1 Reservoirs and state array

| Index $j$ | Reservoir |
|---|---|
| 0 | mantle |
| 1 | upper-crust segment |
| 2 | lower-crust segment |
| 3 | subcrustal lithosphere |

State array `M[h][i][k][j]`:

- `h`: 0 = mass, 1-4 = 204/206/207/208, 5 = 232, 6 = 238;
- `i`: 1 = start of cycle (before the orogeny), 2 = end of cycle;
- `k`: cycle index 1-46 (the mantle also stores `k+1`);
- `j`: reservoir (table above).

Initial state (`k=1, i=1, j=0`): mass $1050\times10^{24}$ g,
204 $=19\times10^{15}$ mol, 232 $=758\times10^{15}$ mol,
238 $=177\times10^{15}$ mol,
$^{206}\mathrm{Pb}/^{204}\mathrm{Pb}=9.0668$,
$^{207}\mathrm{Pb}/^{204}\mathrm{Pb}=9.9367$,
$^{208}\mathrm{Pb}/^{204}\mathrm{Pb}=28.6528$.

> Those three initial ratios are **calibrated** values (calibrated to Table 4),
> not the printed values of Table 3.

### 3.2 Time and cycles

$$
T_k = 4.5 - 0.1(k-1),\qquad \Delta T = 0.1\ \mathrm{Ga},
$$

`history` records $T_k-\Delta T$, i.e. 4.4 down to 0.0 Ga over 46 cycles.
After each cycle the model decays over $[T_k-\Delta T,\ T_k]$.

### 3.3 Time-dependent parameters (Table 3)

Indexed by cycle $k$:

| Array | Meaning |
|---|---|
| `A1[k]` | fraction of the mantle mass that is extracted |
| `A4[k]` | upper-crust erosion coefficient |
| `A5[k]` | lower-crust erosion coefficient (`A5 = A4[:]`) |
| `A6[k]` | subcrustal erosion coefficient |
| `U[k]` | new upper-crust mass |
| `L[k]` | new lower-crust mass |
| `S[k]` | new subcrustal mass |

In this dataset the A4 and A6 columns of Table 3 are identical and `U == L`,
so `A4 = A5 = A6`.

Other fixed parameters: `A2=0.2` (MOR fraction), `A3=0.05` (vertical erosion),
`B1=1.0`, `B2=0.01`, `B3=0.0`, `Bs=0.001`, `H0=35/Bs=35000`,
`dp=0.14` (default).

### 3.4 Mass transfer (per cycle $k$)

For each older upper-crust segment $j<k$:

$$
V_0 = \frac{M_u - U_{\mathrm{eroded}}/H_0}{M_u},\qquad
U_v = M_u V_0 A_3,
$$

$$
U_h = M_u\left[V_0 A_4(1-A_3) + (1-V_0)A_4\right],
$$

$$
U_{\mathrm{eroded}} \leftarrow U_{\mathrm{eroded}}(1-A_4),\qquad
M_u \leftarrow M_u - U_v - U_h .
$$

For older lower-crust segments: $L_h = M_l A_5$, $M_l\leftarrow M_l-L_h$.

For older subcrustal segments: $S_h = M_s A_6$, $M_s\leftarrow M_s-S_h$.

Aggregates:

$$
V = \sum U_v,\qquad
H_z = \sum U_h + \sum L_h,\qquad
\mathrm{Outboard}=d_p V,\qquad
\mathrm{Inboard}=(1-d_p)V,
$$

$$
P_{oro} = \mathrm{Inboard} + H_z,\qquad
M_{or} = A_2 A_1 M_m,\qquad
R_{mor} = (1-A_2)A_1 M_m,
$$

$$
D_{oro} = M_{or} + \mathrm{Outboard},\qquad
W_{oro} = S_{re} + S_{mant},
$$

where $S_{re}=\sum S_h$ and $S_{mant}$ comes from section 3.5.

### 3.5 Gates

$$
\mathrm{Gate}_{b3} = B_3(U_k + L_k - P_{oro}),
$$

$$
\mathrm{Gate}_{b2} = B_2 S_k + \mathrm{Gate}_{b3},
$$

$$
\mathrm{Gate}_{b1} = B_1(U_k + L_k - P_{oro}),
$$

$$
S_{mant} = S_k - S_{re} - \mathrm{Gate}_{b2} + \mathrm{Gate}_{b3}.
$$

> The signs and the order of the gates follow the BASIC listing of
> Haines & Zartman (1988); the physical basis of the bi-directional exchange
> between orogene and subcrustal lithosphere is Zartman & Haines (1988).

The three components (distal $D$, proximal $P$, wedge $W$) are then adjusted:

$$
D^{(1)} = D^{(0)} - \mathrm{Gate}_{b2},\qquad
D^{(2)} = D^{(1)} - \mathrm{Gate}_{b1},
$$

$$
W^{(1)} = W^{(0)} + \mathrm{Gate}_{b2},\qquad
W^{(2)} = W^{(1)} - \mathrm{Gate}_{b3},
$$

$$
P^{(1)} = P^{(0)} + \mathrm{Gate}_{b1} + \mathrm{Gate}_{b3}.
$$

New reservoirs:

$$
M_u^{\mathrm{new}} = U_k,\qquad
M_l^{\mathrm{new}} = L_k,\qquad
M_s^{\mathrm{new}} = S_k,
$$

$$
M_m^{\mathrm{new}} = M_m - A_1 M_m + D^{(2)} - S_{mant} + R_{mor}.
$$

### 3.6 Isotope transfer: `FNEmoles`

The element preference is converted into a two-way mole split:

$$
\mathrm{Bang} = \frac{\mathrm{Bias}}{1+\mathrm{Bias}},\qquad
\mathrm{Denom} = \mathrm{Mass}_1\,\mathrm{Bang} + \mathrm{Mass}_2(1-\mathrm{Bang}),
$$

$$
\mathrm{Moles} = N\,\frac{\mathrm{Mass}_1\,\mathrm{Bang}}{\mathrm{Denom}} .
$$

$N$ is the total number of moles to split, $\mathrm{Mass}_1,\mathrm{Mass}_2$
are the masses of the two receivers and $\mathrm{Bias}$ is the enrichment
factor. The function returns 0 when $\mathrm{Bias}\le0$ or
$\mathrm{Denom}=0$.

Enrichment factors (index order 204/206/207/208/232/238):

| Array | Role |
|---|---|
| `E_a2` | mantle -> MOR |
| `F_a3` | vertical erosion -> distal / proximal |
| `E_b1` | distal -> proximal (gate b1) |
| `E_b2` | distal -> wedge (gate b2) |
| `E_b3` | wedge -> proximal (gate b3) |
| `F_c3` | proximal -> new upper / lower crust |

These numbers are **calibrated to Table 4** (see the comments in
`version4.py`) and differ from the printed Table 3 integers (for Pb:
`E_a2=80`, `F_a3=1.00`, ...), which are kept as an order-of-magnitude
reference.

### 3.7 Isotope transfer

The geometry is exactly that of sections 3.4/3.5; every split uses `FNEmoles`
and masses are replaced by the corresponding isotope mole numbers. In
addition:

- the extraction from upper/lower/subcrustal segments is multiplied by
  `E_up`, `E_low`, `E_sub` (all 1 in this implementation);
- $S_{mant}$ is distributed over isotopes in proportion to mass:
  $S_{mant}^{(h)} = \dfrac{S_{mant}}{M_m-M_{or}}\left(M_m^{(h)}-M_{or}^{(h)}\right)$;
- the new upper crust is
  $M_u^{new(h)} = \mathrm{FNEmoles}(P_{oro}^{(h)}, U_k, L_k, F_{c3}[h])$ and
  the rest goes to the new lower crust,
  $M_l^{new(h)} = P_{oro}^{(h)} - M_u^{new(h)}$;
- the new subcrustal reservoir takes the wedge component $W^{(2)}$.

### 3.8 Decay

After cycle $k$, the mantle and every crustal segment are updated with

$$
\begin{aligned}
^{206}\mathrm{Pb} &\mathrel{+}= ^{238}\mathrm{U}\left(e^{\lambda_{238}T}-e^{\lambda_{238}(T-\Delta T)}\right),\\
^{207}\mathrm{Pb} &\mathrel{+}= \frac{^{238}\mathrm{U}}{137.88}\left(e^{\lambda_{235}T}-e^{\lambda_{235}(T-\Delta T)}\right),\\
^{208}\mathrm{Pb} &\mathrel{+}= ^{232}\mathrm{Th}\left(e^{\lambda_{232}T}-e^{\lambda_{232}(T-\Delta T)}\right),
\end{aligned}
$$

where $T=T_k$ and $\Delta T=0.1$ Ga.

### 3.9 Output

`run(dp=0.14, double_eroded=False)` returns a dictionary:

| Key | Contents |
|---|---|
| `mantle` / `upper` / `lower` / `sub` | final isotope mole numbers (keys 1-6) |
| `total` | sum of the four reservoirs |
| `masses` | final masses (`mantle`/`upper`/`lower`/`sub`/`total`) |
| `last_upper` / `last_lower` / `last_sub` | youngest crustal segment |
| `history` | one record per cycle (`cycle`, `time_Ga`, `mantle`, `upper`, `lower`, `sub`, `orogene`) |

`ratios(d)` converts a 1-6 keyed dictionary into `206/204`, `207/204`,
`208/204`, `238U/204Pb`, `232Th/238U` and `232Th/204Pb`.

### 3.10 Tunable parameters

| Parameter | Default | Meaning |
|---|---|---|
| `dp` | 0.14 | fraction of the vertically eroded material that is "outboard" |
| `double_eroded` | `False` | when `True`, `U_eroded` is multiplied by $(1-A_4)$ a second time in the isotope stage |

---

## 4. Comparison of the two versions

| Aspect | Version I | Version IV |
|---|---|---|
| Reservoirs | mantle, upper/lower crust | + subcrustal, MOR, three orogene components |
| Cycles | 11 x 0.4 Ga | 46 x 0.1 Ga |
| Partitioning | fixed fractions `F_PB`/`F_U`/`F_TH` | `FNEmoles` + enrichment arrays |
| Time parameters | none | Table 3 `A1`/`A4`/`A6`/`U`/`L`/`S` |
| Validation target | Table IV order of magnitude | Table 4 exact values (< 0.02) |

## 5. References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9