# 结果正确性保证

> [English](en/correctness.md) | **简体中文**

本文档说明"结果可信"的依据：**校验基准**、**不变量**、**回归测试**三层保证，
以及模型的已知约定与适用范围。校验数据本身见 [`validation.md`](validation.md)。

## 1. 三层保证体系

| 层 | 手段 | 产物 |
|---|---|---|
| ① 基准校验 | 与论文印刷值逐项对比 | `tests/test_version1.py`、`tests/test_version4.py`、`tests/test_china.py` |
| ② 不变量校验 | 守恒量与结构约束 | `tests/test_conservation.py`、`tests/test_china.py` |
| ③ 回归测试 | 每次改动重跑 ①+② | `pytest`（含 `tests/test_plotting.py` 的图形布局与 PDF 无时间戳检查） |

三层全部通过，才认为结果"在模型定义下正确"。当前实测：**33/33 通过**。

## 2. ① 基准校验

### 2.1 Version IV → Haines & Zartman (1988) Table 4

Table 4 给出 4 个储库 × 6 个比值的现今值，共 24 项。模型以 `dp=0.14`、
46 个旋回运行，逐项比较，判据 `abs(diff) < 0.02`：

- 实测最差偏差 **0.00993**（sub 库 `232Th/204Pb`），24 项全部通过；
- 完整对照表见 [`validation.md`](validation.md) §1。

### 2.2 Version I → Zartman & Doe (1981)

- 初始地幔：206/204 = 10.36、207/204 = 12.12、208/204 = 30.55（精确匹配）；
- 全表复现：11 个旋回 × 4 个储库 × 3 个比值共 **126 项**逐项对比 Table IV，
  最大偏差 **0.00509**（t = 1.6 Ga 地幔 `207/204`），即该表两位小数的印刷极限；
  最大相对误差 0.0349 %，RMSE 0.002729；
- 现今地幔：18.0782 / 15.4156 / 37.6804，对应 Table IV 的 18.08 / 15.42 / 37.68；
- 元素丰度：Table II 第三节 B 的 12 项（质量与 204Pb/238U/232Th）全部落在
  1 % 以内。

完整对照表见 [`validation.md`](validation.md) §2。

> 2026-09 之前该项校验只做到"现今地幔 1 % 量级"，根因是造山带再分配
> （论文 eq. 17–19）把分配比误用为直接分数；修复记录见
> [`validation.md`](validation.md) §2.1。

### 2.3 中国模型 → 李龙等 (2001) 表 3、表 4

| 数据 | 项数 | 最大绝对偏差 | 平均 | RMSE | 判据 |
|---|---|---|---|---|---|
| 论文表 4（现今 `238U/204Pb`、`Th/U`） | 6 | 0.4715 | 0.1793 | 0.2353 | `abs < 0.5` / `abs < 0.10`（`Th/U`） |
| 论文表 3（生长曲线） | 99 | 0.6211 | 0.2199 | 0.2719 | **未复现**，仅以回归上限 0.65 / 0.25 钉住 |

该模型**零自由参数**：论文未印的初始丰度、新成地壳质量、$k_i$ 与衰变常数全部
继承 Zartman & Doe (1981)。

> **表 3 明确列为未复现**，理由是论文这两张结果表互相矛盾：从表 3 反演得到的新成
> 地壳质量为 $15.15 \pm 0.96$，从表 4 反演得到 $1.28 \pm 0.48$，相差约 13σ。
> 因此 `tests/test_china.py` 不去断言"复现"，而是钉住偏差上限，防止将来悄悄
> 变坏。完整分析与论文自身的 5 处内部不一致见
> [`validation.md`](validation.md) §5。

## 3. ② 不变量校验

### 3.1 质量守恒（精确，最强回归信号）

三个模型的物质再分配都是"取出 → 混合 → 再分配"，既不产生也不损失质量：

| 模型 | 初始质量 | 实测终态 | 偏差 |
|---|---|---|---|
| Version I | 800.0 | 800.000000000 | 0 |
| Version IV | 1050.0 | 1050.000000000 | 0 |
| 中国模型 | 800.0 | 800.000000000 | 0 |

Version IV 四储库终态（$10^{24}$ g）：

| 地幔 | 上地壳 | 下地壳 | 次地壳 | 合计 |
|---|---|---|---|---|
| 1000.1118 | 6.6957 | 15.9128 | 27.2797 | **1050.0000** |

任何一个分配系数写错，都会立刻破坏这条恒等式，因此它比"比值接近论文值"
更灵敏。

中国模型另有一层更细的元素守恒：²⁰⁴Pb、²³⁸U、²³²Th 的**摩尔总量**在 11 个旋回
后相对初始值的偏差为 **0**（`strict=True` 时由 `run()` 内部断言，超限即抛
`AssertionError`）。切换到 `decay_parents=True` 后，守恒的是"子体 + 母体"之和
（²⁰⁶Pb + ²³⁸U 等），因为母体本身会衰变到今天的 349。

> 这条不变量抓出过一个真实错误：残余造山带中不返回地幔的那 10 % 曾被直接丢弃，
> 使系统总质量从 800 掉到 780.2。按论文假设 (3d) 它应成为上地壳沉积岩，修正后
> 恢复 800.000000000。它还抓出过另一处：$E_m$ 若只作用于造山带增益而不作用于
> 地幔亏损，每跑一次全系统元素翻倍（末态／初始 1.96 / 1.93 / 1.91）。详见
> [`validation.md`](validation.md) §5.5。

### 3.2 结构不变量

- Version I 每个旋回恰好新增 1 个上地壳段 + 1 个下地壳段，共 11 + 11 个；
- Version I 所有段的质量与同位素摩尔数始终为正（不出现负储库）；
- Version IV `history` 恰好 46 条，`cycle` 为 1–46，时间为 4.4 → 0.0 Ga；
- Version IV `total[h] == mantle[h] + upper[h] + lower[h] + sub[h]`（h = 1..6）；
- Version IV 地幔 `206Pb/204Pb` 随地质时间单调递增（放射性成因 Pb 只增不减）；
- 中国模型每个旋回恰好新增 1 个上地壳段 + 1 个下地壳段 + 1 个沉积岩段（10 %
  残余造山带）与 1 个下地壳段，共 11 × 3 段上地壳侧、11 段下地壳侧；
- 中国模型地幔、上地壳、下地壳的 `238U/204Pb`（现今）满足
  上地壳 > 地幔 > 下地壳，且 `206Pb/204Pb` 满足同样的顺序——这是论文全部源区
  判别论证的前提，一旦顺序反转，论文的图 2／图 3 解释即不成立。

## 4. 总摩尔数**不**守恒（模型约定，不是缺陷）

实测总摩尔数（204 + 206 + 207 + 208 + 232 + 238）：

| 模型 | 初始 | 终态 | 变化 |
|---|---|---|---|
| Version I | 3737.14 | 4456.92 | **+719.78** |
| Version IV | 1859.47 | 2340.48 | **+481.01** |

原因是论文模型的约定：**衰变区间内把母体当作常数**。子体按

$$
^{206}\mathrm{Pb} \mathrel{+}= ^{238}\mathrm{U}\left(e^{\lambda_{238}t}-e^{\lambda_{238}t'}\right)
$$

增加，而 $^{238}\mathrm{U}$ 本身并不减少；207 与 208 同理。于是 Pb 在
账面上是"凭空"增加的，总摩尔数必然上升。

这是 **Version I 与 Version IV 的建模约定**，不是实现错误：

- 质量守恒仍然成立（质量与摩尔数是两套独立的账）；
- 模型的主要输出是 204 归一化的**比值**，母体常数化是论文定义的一部分；
- 因此**回归测试只能断言质量守恒，不能断言总摩尔数守恒**；
- 若改为严格原子守恒（衰变同时扣减母体），会得到另一套数值、无法复现
  Table 4，属于"另一个模型"，不在本项目范围。

## 5. 数值稳健性

代码对退化输入有显式保护，避免 `ZeroDivisionError` / `NaN` 扩散：

| 位置 | 保护 |
|---|---|
| `version4.FNEmoles` | `Bias <= 0` 或 `Denom == 0` → 掩码置 `0`（迁移前是分支返回 `0.0`，取值相同） |
| `version4.run` 的 `V0` | 段质量为 0 → `V0 = 0` |
| `version4.run` 的 `S_mant` 同位素分配 | 分母 `M_m - M_or == 0` → 跳过 |
| `version1.ratios` / `version4.ratios` | 分母为 0 → 返回 `None` |
| `version1.run` 的再分配份额 `s` | `s <= 0` → 该同位素份额取 0（退化参数专用，Table II 下不可达） |
| `plotting._extract_version4_series` | 跳过比值为 `None` 的条目 |

`tests/test_conservation.py` 覆盖了 `FNEmoles` 的两个守卫分支与 `ratios` 的
零分母分支。

**浮点精度实测**（各模型均用 NumPy 数组承载状态，`np.exp` 做衰变）：

| 项 | 实测 |
|---|---|
| 整模型 vs 60 位十进制重算（Version I 全流程） | 最大相对差 **8.4e-16**（约 4 ulp） |
| 终态 204Pb、238U | **逐位相同** |
| 22 项段求和：`np.sum`（成对）vs `math.fsum`（精确） | 204 逐位相同；238 相对差 1.6e-16 |
| **迁移前后**：stdlib 版 vs NumPy 版 | Version I **6.5e-16**、Version IV **8.9e-16** |
| `np.exp` vs `math.exp`（模型实际用到的 342 个指数参数） | **逐位相同**（0 个不同） |

即浮点误差比 Table IV 的 0.005 容差低 12 个数量级；模型精度的实际限制是
论文的印刷位数与参数本身，不是数值格式。迁移到 NumPy 后与迁移前的结果差异
只有 3–4 ulp（全部来自 `np.sum` 的成对求和），**Table IV / Table 4 对比表中
没有任何一位数字发生变化**——两份 CSV 与迁移前逐字节相同。

> 注意：numpy 的超越函数**不保证正确舍入**。本机实测 `np.exp` 与 `math.exp`
> 在这 342 个参数上逐位一致，但这是平台相关的；换平台后 `np.exp` 可能差
> ~1 ulp，届时上表最后一行的结论需要重测。

## 6. 可复现性

- **依赖边界**：三个模型只用 **NumPy**（`version1.py`、`version4.py`、`china.py` 均
  `import numpy as np`），不再需要 `math`，也不读任何外部数据文件；
  `pandas` 只用于 `scripts/` 的对比统计，`matplotlib` 只用于绘图；
- **完全确定性**：全流程无随机数、无时间戳、无并行归约顺序不确定；
  `plotting.py` 显式清空 PDF 元数据里的 `CreationDate`，否则 matplotlib 会写入
  生成时刻，PDF 图便无法逐位复现；
- **输入内联**：初始条件与 Table 3 参数以常量/数组写在源码中，并注明出处；
- **版本可追溯**：`pyproject.toml` 声明 `version = "0.1.0"` 与依赖下界。

同一环境下同一版本，结果逐位一致。

## 7. 已知不一致的显式处理

| 问题 | 处理 |
|---|---|
| PLUMBO Table 4 的 PDF **文本层**是扫描 OCR，把 `4` 误读成 `1` | 一律以**图像**为准；两个 sub 库目标值仍沿用误读值，见 [`validation.md`](validation.md) §4.8 |
| Table 3 的印刷富集系数（整数）无法复现 Table 4 | 采用**标定值**（`version4.py` 的 `E_a2`…`F_c3`、`INIT_RATIOS`），印刷值仅作量级参考 |
| Table IV 两处 orogene `208Pb/204Pb` 为 OCR 错误 | 采用修正值（30.55 / 35.77），并已由修正后的模型独立证实，见 [`validation.md`](validation.md) §4.6 |
| `history['orogene']` 曾漏掉近端 + 楔形分量 | 已修复，见 [`validation.md`](validation.md) §4.1 |
| 曾把 Version I 的 1.5 % 偏差归因于"论文不自洽" | 结论错误，已撤回；真因是 eq. 17–19 的实现方式，已修复，见 [`validation.md`](validation.md) §2.1 |

这些不一致都在文档中显式记录，而不是靠"调参凑数"掩盖。

## 8. 如何自查

```bash
uv sync --extra dev
uv run pytest -q                      # 三层一起跑
uv run pytest -q tests/test_conservation.py   # 只跑不变量
```

不想用 pytest 时，也可以直接用解释器运行测试函数：

```python
import sys
sys.path[:0] = ["src", "tests"]
import test_conservation as t
for name in dir(t):
    if name.startswith("test_"):
        getattr(t, name)()
        print("ok", name)
```

`scripts/run_version1.py` 把 126 项 Table IV 对比写入
`outputs/results/version1_comparison.csv`，`scripts/run_version4.py` 把 24 项
Table 4 对比写入 `outputs/results/version4_comparison.csv`，便于人工复核。

## 9. 局限与适用范围

**保证的是"实现正确"**：本仓库忠实复现 Zartman & Doe (1981) 与
Haines & Zartman (1988) 的模型定义、参数与标定。

**不保证"地质真实"**：模型本身是对地球浅部演化的简化——长期稳态储库、
离散造山旋回、母体常数化、造山带内部完全均一化等。把输出当作真实地球
的预测，需要独立的地质论证，超出本文档范围。

## 10. CI 建议

```yaml
# .github/workflows/tests.yml   （建议内容，本仓库尚未创建该文件）
name: tests
on: [push, pull_request]
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.12"
      - run: uv sync --extra dev
      - run: uv run pytest -q
```

## 11. 参考文献

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. 李龙, 郑永飞, 周建波 (2001). 中国大陆地壳铅同位素演化的动力学模型. *岩石学报*, *17*(1), 61–68.

基准校验目标（Table 4）出自文献 1；Version I 的定义出自文献 2；gates 的物理依据出自文献 3；
中国区域模型的来源与校验目标（表 3、表 4）出自文献 4。
