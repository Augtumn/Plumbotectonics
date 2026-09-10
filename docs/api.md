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
> 修改 `constants.py` 不会影响两个模型（见 [`validation.md`](validation.md) §3.2）。

## `plumbotectonics.version1`

### `run()`

运行 Version I 的 11 个旋回。

**返回**：`(history, mantle, upper_segs, lower_segs)`

- `history`：`list[dict]`，每个旋回一项：
  `{"t": float, "mantle": dict|None, "orogene": dict|None, "upper": dict|None, "lower": dict|None}`
- `mantle`：`dict`，键 `mass`、`204`、`206`、`207`、`208`、`232`、`238`
- `upper_segs` / `lower_segs`：`list[dict]`，每个旋回新增一段，键同上

### `ratios(res)`

把储库字典换成 `{"206/204", "207/204", "208/204"}`；
`res["204"] == 0` 时返回 `None`。

### `avg_res(segs)`

对一组段求和后返回 `ratios(...)`；空列表返回 `None`。

### 模块常量

`L238`、`L235`、`L232`、`U8U5`、`MASS0`、`PB2040`、`U2380`、`TH2320`、
`R2060`、`R2070`、`R2080`、`NEW_U`、`NEW_L`、
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

Version IV 的摩尔分配函数（见 [`theory.md`](theory.md) §3.6）。
`Bias <= 0` 或 `Mass1*Bang + Mass2*(1-Bang) == 0` 时返回 `0.0`。

### 模块常量与数组

`CYCLES`、`A2`、`A3`、`B1`、`B2`、`B3`、`Bs`、`H0`、`L1`、`L2`、`L3`、
`U8U5`、`INIT_RATIOS`、`A1`、`A4`、`A5`、`A6`、`U`、`L`、`S`、
`E_a2`、`F_a3`、`E_b1`、`E_b2`、`E_b3`、`F_c3`、`E_up`、`E_low`、`E_sub`。

## `plumbotectonics.plotting`

### `plot_version1_growth_curves(history, out_png, out_pdf=None)`

三面板图：207–206、208–206、206–t。

### `plot_version4_growth_curves(result, out_png, out_pdf=None)`

四面板图：207–206、208–206、206–t、238U/204Pb–t。

两者都会自动创建输出目录，并以 600 dpi 保存 PNG；传入 `out_pdf` 时
同时保存矢量 PDF。
