# 文档索引

> [English](en/README.md) | **简体中文**

| 中文 | English | 内容 |
|---|---|---|
| [theory.md](theory.md) | [en/theory.md](en/theory.md) | 计算原理：总体框架、Version I、Version IV、中国区域模型、版本对照 |
| [usage.md](usage.md) | [en/usage.md](en/usage.md) | 环境要求、安装、命令行、Python API、故障排查 |
| [api.md](api.md) | [en/api.md](en/api.md) | 模块、函数、参数与返回数据结构 |
| [validation.md](validation.md) | [en/validation.md](en/validation.md) | Table IV / Table 4 校验数据、文献原图、标定说明、中国模型的复现结论、已知问题 |
| [correctness.md](correctness.md) | [en/correctness.md](en/correctness.md) | 结果正确性保证：三层保证体系、守恒不变量、CI |

## 快速导航

- 想理解模型公式 → [theory.md](theory.md)
- 想跑起来 → [usage.md](usage.md)
- 想在代码里调用 → [api.md](api.md)
- 想看模型准不准 → [validation.md](validation.md)
- 想知道结果为什么可信 → [correctness.md](correctness.md)

## 文档与源码对应

| 文档小节 | 源码 |
|---|---|
| `theory.md` §2 | `src/plumbotectonics/version1.py` |
| `theory.md` §3 | `src/plumbotectonics/version4.py` |
| `theory.md` §4 | `src/plumbotectonics/china.py` |
| `api.md` | `src/plumbotectonics/*.py` |
| `validation.md` | `tests/`、`scripts/run_version1.py`、`scripts/run_version4.py`、`scripts/run_china.py`、`outputs/results/literature/` |

返回项目首页：[`../README.md`](../README.md)。
