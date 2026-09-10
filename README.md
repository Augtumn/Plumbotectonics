# Plumbotectonics

[English](README.en.md) | **简体中文**

Zartman & Doe (1981) 与 Haines & Zartman (1988) 铅同位素演化模型的
Python 实现与校验。

Plumbotectonics 是一类质量平衡模型：把地球浅部划分为若干长期存在的储库
（地幔、上/下地壳、次地壳岩石圈、洋中脊），用离散的造山旋回描述储库之间
的物质与同位素交换。每个旋回从地幔和已有地壳中取出物质，在造山带内混合
均一化，再重新分配到各储库；两次旋回之间只发生放射性衰变。

## 特性

- 纯 Python 实现（除 NumPy 外无第三方依赖）**Version I**（Zartman & Doe, 1981）与
  **Version IV**（Haines & Zartman, 1988）以及**中国大陆区域模型**（李龙等, 2001）；
- 复现 Haines & Zartman (1988) Table 4 的全部 24 个现今值
  （最差绝对偏差 **0.00993**，测试容差 0.02）；其中 sub 库两个目标值取自
  扫描 OCR 的误读，**尚未修正**，见 [`docs/validation.md`](docs/validation.md) §4.8；
- 复现 Zartman & Doe (1981) Table IV 的全部 126 个生长曲线值
  （最差绝对偏差 **0.00509**，即该表两位小数的印刷极限）；
- 内置 Version I 与 Version IV 的生长曲线绘图（600 dpi PNG + 矢量 PDF）。

## 模型

| 模块 | 模型 | 文献 |
|---|---|---|
| `plumbotectonics.version1` | Version I | Zartman & Doe (1981) |
| `plumbotectonics.version4` | Version IV | Haines & Zartman (1988) |
| `plumbotectonics.china` | 中国大陆区域模型 | 李龙等 (2001) |

Version I 是"地幔 + 地壳"的两储库质量平衡：造山带物质按固定分配比
（`F_PB`/`F_U`/`F_TH`）在返回地幔与新上/下地壳之间分配，且分配比按各返回
增量自身的质量加权；
Version IV 增加了洋中脊（MOR）储库、次地壳岩石圈、造山带的三组分
结构（远端 / 近端 / 楔形）以及显式的物质交换"门"（gates）。

其中造山带与次地壳之间双向物质交换（bi-directional transport）的物理依据来自 Zartman & Haines (1988)。

`china` 是 **Version I 的区域变体**：算法完全沿用 Zartman & Doe (1981)，
只替换论文自己印出的表 1（4.0 Ga 初始比值）与表 2（分配系数），并把下地壳
保留比例改为 $p^l=0.95$、残余造山带的 90 % 返回地幔。论文未给出的参数
（初始元素丰度、新成地壳质量、衰变常数、$k_i$）全部继承 ZD1981，因此
**零自由参数**。它复现表 4 到 0.47，但**没有复现表 3**（最大偏差 0.62）——
原因见 [`docs/validation.md`](docs/validation.md) §5。

## 安装

本项目用 [uv](https://docs.astral.sh/uv/) 管理环境与依赖，要求 Python >= 3.10：

```bash
uv sync              # 创建 .venv 并安装运行依赖
uv sync --extra dev  # 需要 pytest 时追加开发依赖
```

运行依赖为 `numpy`、`pandas`、`matplotlib`。**三个模型只用 NumPy**
（`version1.py`、`version4.py` 均 `import numpy as np`，状态存为数组、逐旋回
按切片运算）：`pandas` 仅用于 `scripts/` 的对比统计，`matplotlib` 仅用于
绘图。安装位置见 [`docs/usage.md`](docs/usage.md)。

## 运行

```bash
uv run python scripts/run_version1.py        # Version I 生长史（打印到终端）
uv run python scripts/run_version4.py        # 与 Table 4 对比 -> outputs/results/
uv run python scripts/run_china.py           # 与论文表 3/表 4 对比 -> outputs/results/
uv run python scripts/plot_growth_curves.py  # 生长曲线图 -> outputs/figures/
```

生成的表格与图形写入 `outputs/`。

## 文档

| 中文 | English | 内容 |
|---|---|---|
| [`docs/theory.md`](docs/theory.md) | [`docs/en/theory.md`](docs/en/theory.md) | 计算原理：各模型的质量/同位素传输、分配函数与衰变 |
| [`docs/usage.md`](docs/usage.md) | [`docs/en/usage.md`](docs/en/usage.md) | 安装、命令行、Python API 与故障排查 |
| [`docs/api.md`](docs/api.md) | [`docs/en/api.md`](docs/en/api.md) | 模块、函数、参数与返回数据结构 |
| [`docs/validation.md`](docs/validation.md) | [`docs/en/validation.md`](docs/en/validation.md) | Table IV / Table 4 校验数据、文献原图、标定说明、中国模型的复现结论与已知问题 |
| [`docs/correctness.md`](docs/correctness.md) | [`docs/en/correctness.md`](docs/en/correctness.md) | 结果正确性保证：三层保证体系、守恒不变量、CI |

## 目录结构

- `src/plumbotectonics/` — 模型实现（`constants.py`、`version1.py`、
  `version4.py`、`china.py`、`plotting.py`）
- `scripts/` — 命令行入口
- `tests/` — pytest 校验套件
- `papers/` — 原始论文
- `outputs/` — 生成的表格与图形；`outputs/results/literature/` 是两张对比表
  所引文献值的**原始出处截图**（非生成物）
- `docs/` — 中文文档，`docs/en/` — English documentation

## 测试

```bash
uv run pytest
```

覆盖范围：Version I 对 Table IV 全部 126 项（11 个旋回 × 4 个储库 × 3 个比值，
容差 0.006）与 Table II 第三节 B 的 12 项元素丰度、Version IV 四个储库对
Table 4 的 24 项比对（`abs(diff) < 0.02`）、三个模型的质量守恒与结构不变量
（`tests/test_conservation.py`）、中国模型的元素守恒与定性顺序
（`tests/test_china.py`）以及图形布局与 PDF 可复现性（标题不得与面板
标题重叠、PDF 不得带时间戳，`tests/test_plotting.py`）、迁移后的依赖边界与
公开返回结构（`tests/test_conservation.py`）。当前状态：**33/33 通过**。

## 校验

Version IV 以 Haines & Zartman (1988) Table 4 的现今值为标定目标。lower 库
用于校验的 `238U/204Pb` 取扫描图上的真值 **6.4903**（PDF 文本层的 OCR 把它
误读成 6.1903）。

`dp=0.14`、46 个旋回下与 Table 4 的最差偏差：

| 储库 | 最差 `abs(diff)` | 对应比值 |
|---|---|---|
| 地幔 | 0.00049 | 208Pb/204Pb |
| 上地壳 | 0.00017 | 207Pb/204Pb |
| 下地壳 | 0.00033 | 232Th/204Pb |
| 次地壳 | 0.00993 | 232Th/204Pb |

> **注意**：次地壳的 `207Pb/204Pb` 与 `232Th/204Pb` 两个目标值本身仍是文本层
> 的误读（图上为 15.44000 / 35.54200，本表用的是 15.110 / 35.512），因此这两
> 项的"通过"不成立。详见 [`docs/validation.md`](docs/validation.md) §4.8。

完整对照表见 [`docs/validation.md`](docs/validation.md)。

Version I 以 Zartman & Doe (1981) Table IV 的生长曲线为校验目标，11 个旋回 ×
4 个储库 × 3 个比值共 126 项的最差偏差为 **0.00509**（Table IV 只印两位小数，
0.005 即其精度极限）；Table II 第三节 B 的 12 项元素丰度全部在 1 % 以内。

中国区域模型（李龙等 2001）以论文表 3、表 4 为对照目标：

| 数据 | 最大绝对偏差 | 平均 | RMSE |
|---|---|---|---|
| 论文表 3（99 个生长曲线值） | 0.5998 | 0.1322 | 0.2016 |
| 论文表 4（6 个现今值） | 0.6031 | 0.2550 | 0.3481 |

> **表 3 没有复现**（该表印到 0.01，只有 11/99 落在 ±0.005 内）。从两张表分别
> 反演初始值得到的新成地壳质量相差约 13σ，说明**论文这两张表互不相容**；论文
> 自身还另有 5 处文字与表格不一致。详见
> [`docs/validation.md`](docs/validation.md) §5。

## 正确性保证

结果由三层相互独立的机制固定，详见
[`docs/correctness.md`](docs/correctness.md)：

1. **基准校验** — Version IV 复现 Haines & Zartman (1988) Table 4 全部 24 个
   现今值（`abs(diff) < 0.02`）；Version I 复现 Zartman & Doe (1981) Table IV
   全部 126 个值（最差 0.00509，即印刷精度）与 Table II 第三节 B 的
   12 项元素丰度（1 % 以内）；中国模型复现论文表 4（最差 0.6031）——表 3
   明确列为**未复现**，并在 `tests/test_china.py` 中以回归上限钉住。
2. **不变量** — 三个模型的总质量精确守恒（Version I：800；
   Version IV：1050；中国模型：800），且中国模型的元素总量守恒
   （²⁰⁴Pb、²³⁸U、²³²Th），由 `tests/test_conservation.py` 与
   `tests/test_china.py` 连同结构约束一并校验。
3. **回归测试** — 每次改动由 `uv run pytest` 重跑上述两层。

> 总**摩尔数**并不守恒，这是模型的有意约定：论文模型在每个衰变区间内把母体
> （238U、232Th）当作常数，Pb 因此增长而母体不减。这是建模约定而非实现缺陷，
> 详见 [`docs/correctness.md`](docs/correctness.md) 第 4 节。
>
> 中国模型还提供一个可切换的守恒参数化（`decay_parents=True`，论文 eqs. 9-10），
> 其中母体真衰变、²³⁵U 独立跟踪，此时"子体 + 母体"之和严格守恒。两种写法
> **逐位等价**。

## 参考文献

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. 李龙, 郑永飞, 周建波 (2001). 中国大陆地壳铅同位素演化的动力学模型. *岩石学报*, *17*(1), 61–68.

文献 3 给出造山带双向物质交换（bi-directional transport）的物理依据，对应本项目的 gates 实现；
文献 4 是中国区域模型（`plumbotectonics.china`）的来源。

`papers/` 收录了四篇文献的 PDF：

| 文献 | 本地文件 |
|---|---|
| 1 Haines & Zartman (1988) | `papers/Haines_Zartman_1988_PLUMBO.pdf` |
| 2 Zartman & Doe (1981) | `papers/Zartman_Doe_1981_Plumbotectonics.pdf` |
| 3 Zartman & Haines (1988) | `papers/Zartman_Haines_1988_Bidirectional.pdf` |
| 4 李龙等 (2001) | `papers/Dynamic+model+for+Pb+isotope+evolution+in+the+continental+crust+of+China..pdf` |