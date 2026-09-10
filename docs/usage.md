# 使用指南

## 1. 环境要求

- Python >= 3.10
- 运行依赖：`numpy`、`pandas`、`matplotlib`
- 开发依赖：`pytest`（`pyproject.toml` 的 dev extra 里还有 `scipy`，
  但当前源码未使用）

## 2. 安装

本项目用 [uv](https://docs.astral.sh/uv/) 管理环境与依赖：

```bash
uv sync              # 创建 .venv 并安装运行依赖
uv sync --extra dev  # 需要 pytest 时追加开发依赖
```

> `scripts/*.py` 直接 `import plumbotectonics`，所以请用 `uv run` 执行
> （`uv sync` 后激活 `.venv` 亦可），否则会报
> `ModuleNotFoundError: No module named 'plumbotectonics'`。

## 3. 命令行

### 3.1 Version I

```bash
uv run python scripts/run_version1.py
```

打印 11 个旋回在 `206/204`、`207/204`、`208/204` 上的
地幔、造山带、上地壳、下地壳比值。

### 3.2 Version IV（Table 4 对比）

```bash
uv run python scripts/run_version4.py
```

把 `dp=0.14` 的模型结果与 Haines & Zartman (1988) Table 4 的 24 个数值
逐项对比，输出 `outputs/results/version4_comparison.csv`（UTF-8-BOM），
并在终端打印表格。

CSV 列：`reservoir`、`ratio`、`model`、`table`、`abs_diff`。

### 3.3 生长曲线图

```bash
uv run python scripts/plot_growth_curves.py
```

生成到 `outputs/figures/`：

| 文件 | 内容 |
|---|---|
| `version1_growth_curves.png` / `.pdf` | Version I：三面板（207–206、208–206、206–t） |
| `version4_growth_curves.png` / `.pdf` | Version IV：四面板（207–206、208–206、206–t、238U/204Pb–t） |

PNG 为 600 dpi，PDF 为矢量图。

## 4. Python API

### 4.1 Version I

```python
from plumbotectonics.version1 import run, ratios

history, mantle, upper_segs, lower_segs = run()

print(history[0]["t"], history[0]["mantle"])   # 4.0 Ga 初始状态
print(history[-1]["mantle"])                    # 现今地幔
print(ratios(mantle))
```

### 4.2 Version IV

```python
from plumbotectonics.version4 import run, ratios

result = run(dp=0.14)

print(ratios(result["mantle"]))
print(ratios(result["upper"]))
print(result["masses"])
print(result["history"][-1]["time_Ga"])         # 0.0

# 逐旋回演化
for h in result["history"]:
    print(h["cycle"], h["time_Ga"], h["upper"])
```

### 4.3 绘图

```python
from plumbotectonics.version1 import run as run_v1
from plumbotectonics.version4 import run as run_v4
from plumbotectonics.plotting import (
    plot_version1_growth_curves,
    plot_version4_growth_curves,
)

hist1, *_ = run_v1()
plot_version1_growth_curves(hist1, "v1.png", "v1.pdf")

res4 = run_v4(dp=0.14)
plot_version4_growth_curves(res4, "v4.png", "v4.pdf")
```

### 4.4 顶层导入

```python
import plumbotectonics as pt

pt.run_version1()
pt.run_version4(dp=0.14)
pt.v4_ratios(pt.run_version4()["mantle"])
```

## 5. 输出目录

```
outputs/
├── figures/   # version1_growth_curves.{png,pdf}, version4_growth_curves.{png,pdf}
└── results/   # version4_comparison.csv
```

目录会在运行时自动创建。

## 6. 测试

```bash
uv run pytest
```

`pyproject.toml` 已配置 `pythonpath = ["src"]` 与 `testpaths = ["tests"]`，
因此在仓库根目录直接运行即可。

## 7. 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: plumbotectonics` | 未执行 `uv sync`，或未用 `uv run` | `uv sync`，并用 `uv run` 执行脚本 |
| `No module named pytest` | 未装开发依赖 | `uv sync --extra dev` |
| `ImportError: Can't determine version for pytz` | pandas 与 pytz 版本不匹配 | `uv pip install -U --force-reinstall pytz pandas` |
| 图中中文显示为方块 | 缺少中文字体 | 安装 `Microsoft YaHei`/`SimHei`，或修改 `plotting.py` 的字体列表 |
| `run_version4.py` 较慢 | 46 个旋回 × 6 种同位素 | 正常，通常几秒内完成 |

> `plotting.py` 已设置 `matplotlib.use("Agg")`，可在无显示环境（服务器/CI）运行。
