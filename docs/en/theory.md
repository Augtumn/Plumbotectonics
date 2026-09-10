# Theory

> **English** | [简体中文](../theory.md)

This document describes the calculation flow of the three models (Version I,
Version IV and the China regional model) and maps it onto
`src/plumbotectonics/version1.py` and `version4.py`.

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

and the rest returns to the mantle, with mass

$$
M_{\mathrm{ret}} = M_{or} - 2.6 - 2.6 .
$$

Pb, U and Th are partitioned between the three **returning increments**
(returned mantle / new upper crust / new lower crust) as

| Element | $F^m$ (mantle) | $F^u$ (upper) | $F^l$ (lower) |
|---|---|---|---|
| Pb | 0.028 | 0.754 | 0.218 |
| U | 0.024 | 0.854 | 0.122 |
| Th | 0.020 | 0.788 | 0.192 |

(`F_PB`, `F_U`, `F_TH`). These are **concentration ratios, not shares**: each
returning increment receives a part of the orogene content proportional to
*its own mass times its partitioning ratio*, divided by the normalising factor
$s$. This is eqs. 17-19 of the paper:

$$
s = M_{\mathrm{ret}}F^m + M_u^{\mathrm{new}}F^u + M_l^{\mathrm{new}}F^l,
$$

$$
X_m^{\mathrm{ret}} = X_{or}\frac{M_{\mathrm{ret}}F^m}{s},\qquad
X_u^{\mathrm{new}} = X_{or}\frac{M_u^{\mathrm{new}}F^u}{s},\qquad
X_l^{\mathrm{new}} = X_{or}\frac{M_l^{\mathrm{new}}F^l}{s}.
$$

The three add up to exactly $X_{or}$, so the redistribution itself neither
creates nor loses any element.

> **Why the ratios cannot be used as shares.** The mass returning to the mantle
> (94.8 in the first cycle) exceeds each new crustal increment (2.6) by one to
> two orders of magnitude, so the mantle actually receives
> $94.8\times0.028/s = 51.3\ \%$ of the orogene lead in that cycle, not
> $2.8\ \%$. Treating `F_PB[0]` as a fraction of the orogene content strips the
> mantle and over-feeds the crust -- the source of this repository's earlier
> 1.5 % deviation; see [`validation.md`](validation.md) section 2.1.

The mantle inventory of each element becomes

$$
X_m \leftarrow X_m - \Delta X_m + X_m^{\mathrm{ret}},
$$

and the mantle mass

$$
M_m \leftarrow M_m - \Delta M_m + M_{\mathrm{ret}},
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

State array `M[h][i][k][j]` (a NumPy array `M[h, i, k, j]` of shape
`(7, 3, 48, 4)` in the implementation):

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

## 4. China regional model: Li et al. (2001)

### 4.1 Positioning

The paper builds a regional model for continental China on the basis of the
"plumbotectonic model" (a precedent being Godwin & Sinclair (1982) for western
Canada). Its central claim is that **continental China evolved from a system
that is relatively U-poor and Th-rich, and whose upper and lower crust
differentiated more thoroughly**; the argument rests on two qualitative points
-- the self-consistency of the source region indicated by granite feldspar data
on the model curves, and the agreement of the model ages with other methods.
The paper does **not** claim to reproduce any numerical table.

This implementation takes: **the algorithm follows Zartman & Doe (1981)** (i.e.
`version1`), replacing only the two tables the paper prints itself.

### 4.2 Differences from Version I

| Aspect | Version I | China model |
|---|---|---|
| 4.0 Ga initial ratios | 10.36 / 12.12 / 30.55 | **10.17 / 12.07 / 30.56** (paper Table 1) |
| Partition ratios | Pb 0.028/0.754/0.218 etc. | **paper Table 2**: Pb 0.038/0.235/0.727, U 0.024/0.111/0.865, Th 0.021/0.162/0.817 |
| Lower-crust retention $p^l$ | 0.90 (erosion 0.10) | **0.95** (erosion 0.05) (paper eq. 2) |
| Residual orogene | 100 % returned to the mantle | **90 %** returned, 10 % becomes upper-crust sediment (paper eqs. 7-8, assumption 3d) |
| Initial abundances, masses, $k_i$, decay constants | ZD1981 | **inherited from ZD1981** (not given by the paper) |

Mind the column order of the partition ratios: the paper's Table 2 prints them
as **(mantle, LOWER crust, UPPER crust)**, the opposite of the (mantle, upper
crust, lower crust) order of ZD1981 Table II, so `F_PB[2]` in `china.py` is the
upper crust.

### 4.3 Where the residual 10 % of the orogene goes

Paper assumption (3d): the bulk of the residual orogene returns to the mantle
quickly, but "part of it still remains at the crustal edge or is eroded to
become sedimentary rock". Taking that amount to be 10 % of the orogene total,
the mantle receives

$$\Delta M_m = 0.9 \times \Delta M_o$$

**That 10 % cannot be discarded** -- discarding it drops the total mass of the
system from 800 to 780.2 ($\times10^{24}$ g). By the paper's semantics it
becomes sedimentary rock, which belongs to the upper crust, so it joins the
upper crust as its own layer and is subsequently eroded at $p^u$ along with the
other upper-crust layers.

### 4.4 Which side $E_m$ acts on

Paper eq. (5) speaks of "the chemical elements **entering the orogene**":

$$\Delta^\alpha N_r^i = \frac{\Delta M_r^i}{M_r^i} \cdot {}^\alpha N_r^i \cdot {}^\alpha E^r$$

It specifies the orogene's **gain** and does not separately write the mantle's
**loss**. Physically the two must be equal: when the mantle partially melts, the
mass taken out is $f_m M_m$ and the concentration of the extracted material is
$E_m$ times the mantle's own ($E_m=4$ corresponds to 25 % melting), so

$$\Delta N_{\text{loss}} = f_m M_m \times E_m \frac{N_m}{M_m} = f_m E_m N_m$$

**This is exactly the amount the orogene receives.** If the mantle lost only
$f_m N_m$ while the orogene still received $f_m E_m N_m$, the difference
$(E_m-1) f_m N_m$ would be **created out of nothing** at every orogeny;
measured, final/initial is 1.965 for 204Pb, 1.926 for 238U and 1.914 for 232Th,
i.e. the element inventory of the whole system doubles. This implementation
therefore makes **the mantle loss carry $E_m$**; the conservation check is in
`validation.md` section 5.5.

### 4.5 Two equivalent decay parameterisations

| | constant parents (default) | parents really decay (paper eqs. 9-10) |
|---|---|---|
| parents | fixed at modern-equivalent abundances (238U = 349) | actual 4.0 Ga abundances (238U = 649.09) |
| daughter increment | $e^{\lambda t} - e^{\lambda t'}$ | $1 - e^{-\lambda \Delta t}$ |
| 207Pb parent | $^{238}\text{U}/137.88$ | separately tracked 235U |
| 238U/235U (4.0 Ga) | implicitly 137.88 | **4.9897** (27.6 times today's) |

**The two are equivalent digit for digit** (maximum difference
$2.1\times10^{-14}$): because "constant parents + 349/1335" and "decaying
parents + back-calculated actual abundances 649/1627" are two ways of writing
the same thing. The `decay_parents` switch selects between them and defaults to
the ZD1981 form.

### 4.6 $E_m=4$ with a falling $f_m$

The paper explains $E_m=4$ as "simulating 25 % melting of the average mantle,
with all the melt entering the orogene", while $k_i$ falls from 1/8 to 1/128.
Under batch melting the enrichment factor of a perfectly incompatible element
($D=0$) is

$$E = \frac{1}{D + F(1-D)} = \frac{1}{F}$$

i.e. $E=8$ at $f_m=1/8$ and $E=128$ at $f_m=1/128$. A fixed $E=4$ is a
simplifying convention of ZD1981, not a batch-melting result.
`melt_model="batch"` provides the alternative $E=1/f_m$; measured, it is
actually worse (Table 3 worst deviation 1.18 against 0.62), so the default
keeps the paper's convention.

### 4.7 Accuracy

| Data | max absolute difference | mean | RMSE |
|---|---|---|---|
| paper Table 3 (99 values) | 0.6211 | 0.2199 | 0.2719 |
| paper Table 4 (6 values) | 0.4715 | 0.1793 | 0.2353 |

**Table 3 is not reproduced** (the table is printed to 0.01). The new-crustal
masses inverted from Table 3 and from Table 4 differ by about 13 sigma, which
shows that **the paper's two tables are mutually incompatible**. See
`validation.md` section 5.

---

## 5. Comparison of the two versions

| Aspect | Version I | Version IV |
|---|---|---|
| Reservoirs | mantle, upper/lower crust | + subcrustal, MOR, three orogene components |
| Cycles | 11 x 0.4 Ga | 46 x 0.1 Ga |
| Partitioning | `F_PB`/`F_U`/`F_TH` weighted by returning-increment mass (eqs. 17-19) | `FNEmoles` + enrichment arrays |
| Time parameters | none | Table 3 `A1`/`A4`/`A6`/`U`/`L`/`S` |
| Validation target | all 126 Table IV values + Table II section III, to print precision | Table 4 exact values (< 0.02) |

The relationship between the China model and Version I is described in
section 4.2: the same algorithm with only the two tables replaced.

## 6. References

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. Li, L., Zheng, Y., & Zhou, J. (2001). Dynamic model for Pb isotope evolution in the continental crust of China. *Acta Petrologica Sinica*, *17*(1), 61–68.