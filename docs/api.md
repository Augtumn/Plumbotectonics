# API 参考

> [English](en/api.md) | **简体中文**

## 包 `plumbotectonics`

`src/plumbotectonics/__init__.py` 暴露：

| 名称 | 说明 |
|---|---|
| `constants` | 常量模块 |
| `run_version1` | `version1.run` |
| `run_version4` | `version4.run` |
| `v4_ratios` | `version4.ratios` |

## `plumbotectonics.constants`

| 常量 | 值 | 说明 |
|---|---|---|
| `LAMBDA_238` / `LAMBDA_235` / `LAMBDA_232` | 0.155125 / 0.98485 / 0.049475 | 衰变常数（Ga$^{-1}$） |
| `LAMBDA_87RB` / `LAMBDA_147SM` | 0.0142 / 0.00654 | 保留常量，当前模型未使用 |
| `U8U5` | 137.88 | $^{238}\mathrm{U}/^{235}\mathrm{U}$ |
| `V1_MASS0` … `V1_NEW_LOWER` | 见文件 | Version I 初始条件 |
| `V4_MASS0` … `V4_CYCLES` | 见文件 | Version IV 初始条件与开关 |

> 注意：`version1.py` 与 `version4.py` 目前各自硬编码了这些常量，
> 修改 `constants.py` 不会影响三个模型（见 [`validation.md`](validation.md) §4.2）。

## `plumbotectonics.version1`

### `run()`

运行 Version I 的 11 个旋回。

每个旋回按论文的 eq. 14–16 抽取、eq. 17–19 再分配（分配比 `F_PB`/`F_U`/`F_TH`
按返回增量质量加权，见 [`theory.md`](theory.md) §2.5）、eq. 20–22 衰变。
`history` 记录的是**每次造山之前**的状态，与 Table IV 的时刻约定一致。

内部状态用 NumPy 数组承载：每个储库是 `(n_segs, 6)` 的数组，列顺序为模块常量
`ISO_KEYS = ("204","206","207","208","232","238")`，抽取、再分配与衰变都作用于
整段切片。**返回结构未变**，仍是下面这些纯 `dict`。

**返回**：`(history, mantle, upper_segs, lower_segs)`

- `history`：`list[dict]`，每个旋回一项：
  `{"t": float, "mantle": dict|None, "orogene": dict|None, "upper": dict|None, "lower": dict|None}`
- `mantle`：`dict`，键 `mass`、`204`、`206`、`207`、`208`、`232`、`238`
- `upper_segs` / `lower_segs`：`list[dict]`，每个旋回新增一段，键同上

### `ratios(res)`

把储库字典换成 `{"206/204", "207/204", "208/204"}`；
`res["204"] == 0` 时返回 `None`。也可直接传入内部的长度 6 的 NumPy 行向量。

### `avg_res(segs)`

对一组段求和后返回 `ratios(...)`；空列表返回 `None`。

### `row_to_dict(row, mass)`

把内部的长度 6 行向量与质量转换成上面那种段字典（`run()` 在返回前调用它）。

### 模块常量

`L238`、`L235`、`L232`、`U8U5`、`MASS0`、`PB2040`、`U2380`、`TH2320`、
`R2060`、`R2070`、`R2080`、`NEW_U`、`NEW_L`、`ERO_U`、`ERO_L`、`ISO_KEYS`、
`F_PB`、`F_U`、`F_TH`、`E_M`、`E_U`、`E_L`。

## `plumbotectonics.version4`

### `run(dp=0.14, double_eroded=False)`

运行 46 个旋回。

**参数**

| 参数 | 默认 | 说明 |
|---|---|---|
| `dp` | 0.14 | 外板（outboard）比例 |
| `double_eroded` | `False` | 是否在同位素阶段重复扣减 `U_eroded` |

**返回**：`dict`

| 键 | 类型 | 说明 |
|---|---|---|
| `mantle` / `upper` / `lower` / `sub` | `dict[int, float]` | 最终摩尔数，键 1–6 = 204/206/207/208/232/238 |
| `total` | `dict[int, float]` | 四储库之和 |
| `masses` | `dict[str, float]` | `mantle`/`upper`/`lower`/`sub`/`total` |
| `last_upper` / `last_lower` / `last_sub` | `dict[int, float]` | 最年轻段 |
| `history` | `list[dict]` | 见下 |

`history` 每项：

```python
{
  "cycle": 1,            # 1..46
  "time_Ga": 4.4,        # 4.4 .. 0.0
  "mantle": {...},       # ratios() 结果
  "upper": {...},
  "lower": {...},
  "sub": {...},
  "orogene": {...},
}
```

### `ratios(d)`

`d` 为键 1–6 的字典，返回：

| 键 | 公式 |
|---|---|
| `206/204` | `d[2]/d[1]` |
| `207/204` | `d[3]/d[1]` |
| `208/204` | `d[4]/d[1]` |
| `238U/204Pb` | `d[6]/d[1]` |
| `232Th/238U` | `d[5]/d[6]` |
| `232Th/204Pb` | `d[5]/d[1]` |

分母为 0 时对应值为 `None`。

### `FNEmoles(N, Mass1, Mass2, Bias)`

Version IV 的摩尔分配函数（见 [`theory.md`](theory.md) §3.6）。**逐元素运算**，
所以可以一次性传入整条同位素轴（长度 6 的数组），`run()` 就是这么用的。
`Bias <= 0` 或 `Mass1*Bang + Mass2*(1-Bang) == 0` 时返回 `0`：迁移前是分支
（返回 `0.0`），现在是掩码 + `np.divide(..., where=...)`，取值完全相同，
且不会产生 `RuntimeWarning`。

### 模块常量与数组

`CYCLES`、`A2`、`A3`、`B1`、`B2`、`B3`、`Bs`、`H0`、`L1`、`L2`、`L3`、
`U8U5`、`INIT_RATIOS`、`ISO`、`A1`、`A4`、`A5`、`A6`、`U`、`L`、`S`、
`E_a2`、`F_a3`、`E_b1`、`E_b2`、`E_b3`、`F_c3`、`E_up`、`E_low`、`E_sub`
（`A*`/`U`/`L`/`S`/`E_*` 现为 `np.ndarray`，索引方式不变）。

## `plumbotectonics.china`

李龙等 (2001) 中国大陆区域模型。算法沿用 Zartman & Doe (1981)（即 `version1`），
只替换论文的表 1 与表 2，并把下地壳保留比例改为 $p^l=0.95$、残余造山带按 90 %
返回地幔。**零自由参数**（未给出的量全部继承 ZD1981）。

### `run(decay_parents=False, melt_model="zd1981", strict=True)`

| 参数 | 默认 | 含义 |
|---|---|---|
| `decay_parents` | `False` | `False` = ZD1981 母体常数化；`True` = 论文 eqs. (9)(10) 母体真衰变（²³⁵U 独立跟踪）。**两者逐位等价** |
| `melt_model` | `"zd1981"` | `"zd1981"` = $E_m$ 恒为 4；`"batch"` = 批式熔融 $E=1/f_m$ |
| `strict` | `True` | 结束时断言元素总量守恒，违反则抛 `AssertionError` |

返回 `(history, mantle, upper_segs, lower_segs)`：

- `history`：11 个 dict，键为 `t`、`mantle`、`orogene`、`upper`、`lower`；
  前三个储库的值为 `{'206/204', '207/204', '208/204'}`，**t=4.0 Ga 时
  `upper`/`lower` 为 `None`**（该次造山前尚无地壳）；
- `mantle`：dict，含 `mass` 与 `ISO_KEYS` 各项；
- `upper_segs` / `lower_segs`：list of dict，每层一个（含 10 % 沉积岩层，
  计入上地壳）。

### `present_day(mantle, upper_segs, lower_segs)`

返回 `{'mantle'|'upper'|'lower': {'238U/204Pb': float, 'Th/U': float}}`，
即论文表 4 的两个量。

### `check_conservation(mantle, upper, lower, decay_parents=False, rtol=1e-9)`

校验元素总量。`decay_parents=False` 时检查 ²⁰⁴Pb、²³⁸U、²³²Th；`True` 时检查
²⁰⁴Pb 与三个"子体+母体"之和（²³⁸U 本身会衰变到今天的 349，不再守恒）。
返回各相对偏差的 dict，超限则抛 `AssertionError`。

### `e_mantle(f_m, melt_model="zd1981")`

地幔贡献物质的富集因子：`"zd1981"` 返回 4；`"batch"` 返回 $1/f_m$；
其它取值抛 `ValueError`。

### `ratios(res)` / `row_to_dict(row, mass)`

与 `version1` 同名函数语义一致。

### 模块常量

| 常量 | 值 | 出处 |
|---|---|---|
| `R2060`/`R2070`/`R2080` | 10.17 / 12.07 / 30.56 | 论文表 1 |
| `F_PB`/`F_U`/`F_TH` | (0.038, 0.727, 0.235) / (0.024, 0.865, 0.111) / (0.021, 0.817, 0.162) | 论文表 2，已换成 ZD1981 的 (幔, 上, 下) 列序 |
| `P_UPPER`/`P_LOWER` | 0.63 / 0.95 | 论文 eq. (2) |
| `E_M`/`E_U`/`E_L` | 4.0 / 1.0 / 1.0 | 论文 eq. (5) |
| `RETURN` | 0.9 | 论文 eqs. (7)(8) |
| `PB2040`/`U2380`/`TH2320` | 38 / 349 / 1335 | ZD1981 表 II（继承） |
| `MASS0`/`NEW_U`/`NEW_L` | 800 / 2.6 / 2.6 | ZD1981 表 II（继承） |
| `ISO_KEYS` | `("204","206","207","208","232","238","235")` | 比 `version1` 多带 ²³⁵U |

## `plumbotectonics.plotting`

### `plot_version1_growth_curves(history, out_png, out_pdf=None)`

三面板图：207–206、208–206、206–t。

### `plot_version4_growth_curves(result, out_png, out_pdf=None)`

四面板图：207–206、208–206、206–t、238U/204Pb–t。

两者都会自动创建输出目录，并以 600 dpi 保存 PNG；传入 `out_pdf` 时
同时保存矢量 PDF。
