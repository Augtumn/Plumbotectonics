# 校验与已知问题

> 本文档给出**校验数据**；保证体系的完整说明见
> [`correctness.md`](correctness.md)（结果正确性保证）。

## 1. Version IV：Table 4 校验

运行：

```bash
python scripts/run_version4.py
```

目标值为 Haines & Zartman (1988) Table 4 的最终值；模型取 `dp=0.14`、
46 个旋回。下表为实测结果。

| 储库 | 206/204 | 207/204 | 208/204 | 238U/204Pb | 232Th/238U | 232Th/204Pb |
|---|---|---|---|---|---|---|
| mantle 模型 | 18.4727 | 15.4822 | 37.7295 | 10.0059 | 2.7276 | 27.2922 |
| mantle 表值 | 18.473 | 15.482 | 37.729 | 10.006 | 2.7276 | 27.29188 |
| **偏差** | −0.00026 | +0.00021 | +0.00049 | −0.00010 | +0.00001 | +0.00034 |
| upper 模型 | 19.3250 | 15.7268 | 39.0708 | 11.0770 | 3.8833 | 43.0159 |
| upper 表值 | 19.325 | 15.727 | 39.071 | 11.077 | 3.8833 | 43.016 |
| **偏差** | +0.00003 | −0.00017 | −0.00015 | +0.00005 | +0.00004 | −0.00007 |
| lower 模型 | 17.6232 | 15.3511 | 38.7530 | 6.4903 | 6.0517 | 39.2777 |
| lower 表值 | 17.623 | 15.351 | 38.753 | 6.4903 | 6.0518 | 39.278 |
| **偏差** | +0.00017 | +0.00005 | −0.00004 | +0.00003 | −0.00008 | −0.00033 |
| sub 模型 | 18.3180 | 15.1100 | 38.1010 | 9.1266 | 3.8921 | 35.5219 |
| sub 表值 | 18.318 | 15.110 | 38.101 | 9.1292 | 3.8932 | 35.512 |
| **偏差** | −0.00003 | −0.00003 | −0.00001 | −0.00258 | −0.00108 | **+0.00993** |

**结论**：全部 24 个比值满足 `|偏差| < 0.02`（即 `tests/test_version4.py`
的容差）；最差为 sub 库的 `232Th/204Pb`（+0.00993）。

最终质量（$10^{24}$ g）：

| 储库 | 质量 |
|---|---|
| mantle | 1000.11 |
| upper | 6.70 |
| lower | 15.91 |
| sub | 27.28 |
| **total** | **1050.00** |

> 质量守恒：四储库之和等于初始质量 1050（保留两位小数）。

### 1.1 关于 lower 库的 6.4903

部分版本的 Table 4 把 lower 库 `238U/204Pb` 印成 **6.1903**，与同一行其它
数值不自洽；本仓库使用自洽值 **6.4903** 作为校验目标，模型实测 6.4903，
偏差 +0.00003。

### 1.2 标定说明

`version4.py` 中的 `E_a2`、`F_a3`、`E_b1`、`E_b2`、`E_b3`、`F_c3`
以及初始比值 `INIT_RATIOS = (9.0668, 9.9367, 28.6528)` 是**校准到
Table 4** 的数值，不是 Table 3 的印刷整数。Table 3 的印刷值（Pb：
`E_a2=80`、`F_a3=1.00`、`E_b1=40`、`E_b2=25`、`E_b3=25`、`F_c3=3.67`
等）保留在论文中作为量级参考。

## 2. Version I：量级校验

`tests/test_version1.py` 检查：

- 初始地幔 206/204 = 10.36、207/204 = 12.12、208/204 = 30.55（精确）；
- 现今地幔约 18.25 / 15.48 / 38.06（容差 0.5 / 0.3 / 0.5）。

实测现今地幔：

| 比值 | 模型 |
|---|---|
| 206/204 | 18.2525 |
| 207/204 | 15.4801 |
| 208/204 | 38.0631 |

## 3. 守恒量与不变量

| 量 | Version I | Version IV |
|---|---|---|
| 总质量（精确守恒） | 800.000000000 | 1050.000000000 |
| 总摩尔数 | 3737.14 → 4456.92（**不守恒**） | 1859.47 → 2340.48（**不守恒**） |
| 段数 | 上/下各 11 | — |
| `history` 条数 | 11 | 46（4.4 → 0.0 Ga） |
| 地幔 `206/204` 单调递增 | — | 是 |

> **质量守恒可用于回归测试，总摩尔数不能**：后者增加是模型约定
> （衰变区间内母体 $^{238}\mathrm{U}$、$^{232}\mathrm{Th}$ 视为常数），
> 不是实现错误。完整说明见 [`correctness.md`](correctness.md) §4。

## 4. 已知问题

### 4.1 `history['orogene']` 曾只含远端组分（Version IV，已修复）

`version4.py` 原先在

```python
oro_moles[h] = D_oro_h[0][2] + P_oro_h[0][1] + W_oro_h[0][2]
```

处求和，但该行位于 `P_oro_h[0][1]` 与 `W_oro_h[0][2]` 赋值之前，此时两者
仍为 0，因此 `history[...]['orogene']` 实际只等于远端组分 $D^{(2)}$，
缺少近端与楔形分量。

**影响**：仅影响 `history['orogene']`（绘图用）；储库结果与 Table 4
校验不受影响。

**状态**：已修复——把该行移到 `P_oro_h[0][1]` 赋值之后。

### 4.2 `constants.py` 与模型实现不同源

- `version1.py` 重复定义了 `L238`、`MASS0`、`F_PB` 等；
- `version4.py` 重复定义了 `CYCLES`、`A2`、`INIT_RATIOS` 等。

因此修改 `constants.py` **不会**影响模型。若要让常量集中管理，应改为从
`constants.py` 导入并删除重复定义（会牵动两个模块，建议单独提交）。

### 4.3 文档字符串位置（已修复）

`version4.py` 原先第 1 行是 `INIT_RATIOS = (...)`，位于模块文档字符串
之前，导致该字符串不是真正的 `__doc__`。已把 `INIT_RATIOS` 移到
docstring 与 `import math` 之后。

### 4.4 `pyproject.toml` 的 dev extra 含未使用的 `scipy`

`scipy` 在 `[project.optional-dependencies].dev` 中，但源码未导入；
可保留（便于后续拟合），也可移除。

### 4.5 环境依赖

`scripts/run_version4.py` 依赖 `pandas`；若环境中 `pandas` 与 `pytz`
版本不匹配，会抛 `ImportError: Can't determine version for pytz`。
模型本身（`version4.py`）不依赖 pandas，可只用标准库调用。

## 5. 如何复现校验

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/run_version4.py
```

或不安装、不依赖 pandas：

```python
import sys
sys.path.insert(0, "src")
from plumbotectonics.version4 import run, ratios

TARGETS = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper":  [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower":  [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub":    [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]

res = run(dp=0.14)
for name, target in TARGETS.items():
    got = [ratios(res[name])[k] for k in KEYS]
    print(name, max(abs(g - t) for g, t in zip(got, target)))
```

## 6. 参考文献

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9

Table 4 的校验目标出自文献 1；Version I 的定义出自文献 2；文献 3 给出双向物质交换（gates）的物理依据。
