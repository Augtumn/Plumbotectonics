# 文献原图（对比表的数据来源）

本目录存放 `../version1_comparison.csv`、`../version4_comparison.csv` 与
`../china_comparison.csv` 中 `literature` 列的**原始出处截图**，便于逐格核对。
全部由 `papers/` 中的论文 PDF 直接渲染裁切，不含任何重绘。

## 文件

| 文件 | 出处 | 对应 |
|---|---|---|
| `zartman_doe_1981_table_ii.png` | Zartman & Doe (1981) 印刷页 142（PDF 第 8 页） | Version I 的初始条件、旋回参数（第二节）、分配比（第二节 C）与**终态元素丰度**（第三节 B） |
| `zartman_doe_1981_table_iv.png` | 同上，印刷页 149（PDF 第 15 页） | **Version I 对比表的 126 个目标值**（Table IV 生长曲线） |
| `zartman_doe_1981_eq_17_19.png` | 同上，印刷页 147（PDF 第 14 页） | 造山带再分配公式 eq. 17–19（`run()` 的实现依据，见 [`../../../docs/theory.md`](../../../docs/theory.md) §2.5） |
| `haines_zartman_1988_table_4_page1.png` | Haines & Zartman (1988) PLUMBO 报告 Table 4 第 1 页（PDF 第 21 页） | Version IV 终态质量与元素丰度 |
| `haines_zartman_1988_table_4_page2.png` | 同上，Table 4 第 2 页（PDF 第 22 页） | **Version IV 对比表的 24 个目标值**（"ENDING ISOTOPIC RATIOS FOR THE MAJOR RESERVOIRS" 区块） |
| `li_2001_table_1_2.png` | 李龙等 (2001) 印刷页 64（PDF 第 4 页） | 中国模型的**初始比值**（表 1）与**分配系数**（表 2） |
| `li_2001_table_3.png` | 同上，同页（通栏） | **中国模型对比表的 99 个目标值**（表 3 生长曲线） |
| `li_2001_table_4.png` | 同上，印刷页 65（PDF 第 5 页） | 中国模型对比表的 **6 个现今值**（表 4）；该表脚注"全球平均\*"引自 Zartman and Haines (1988)，**不是**校验目标 |
| `li_2001_eq_3_6.png` | 同上，印刷页 63（PDF 第 3 页） | eqs. (3)–(6)：侵蚀求和、造山带质量、元素带入与再分配归一化 |

## 复现命令

```bash
pdftoppm -png -gray -r 220 -f <page> -l <page> papers/<paper>.pdf out   # poppler / TeXLive
# 再按页面内容自动裁掉白边（PIL：阈值 200 后取 getbbox，四周留 14 px）
```

`papers/` 中四篇文献的 PDF 均在仓库内，上述命令可完全复现。

> 李龙等 (2001) 的**表 3 通栏跨两列**，裁切时须用整页宽度，不能按单栏框取。
> 该 PDF 的文本层字体映射已损坏（`pdftotext` 输出乱码），只能按图像核对。

## 核对提示（重要）

**不要用 PDF 的文本层做转录。** PLUMBO 报告的文本层是扫描 OCR，存在系统性
的 **`4` → `1`** 混淆。已发现的实例（左为扫描图上的真实字符，右为文本层输出）：

| 位置 | 图上实际值 | 文本层/OCR | 仓库当前取值 |
|---|---|---|---|
| Version IV lower `238U/204Pb` | `6.49030` | `6.19030` | 6.4903（已修正） |
| Version IV upper `232Th/204Pb` | `43.01600` | `13.01600` | 43.016（已修正） |
| Version IV **sub `207Pb/204Pb`** | **`15.44000`** | `15.11000` | **15.110（未修正）** |
| Version IV **sub `232Th/204Pb`** | **`35.54200`** | `35.51200` | **35.512（未修正）** |

`15.440` 与 `35.542` 同时被 Zartman & Haines (1988) Table 1（Subcrustal
Lithosphere 列：207Pb/204Pb = 15.44）独立印证。

因此 `version4_comparison.csv` 的 sub 储库两项目标值仍偏小；按图上真值，
模型的 sub `207Pb/204Pb`（15.109975）偏差应为 **0.33**，而不是表中记的
0.00003。这一问题尚未修复——它牵涉 Version IV 的 sub 储库本身，需要单独
定性，见 [`../../../docs/validation.md`](../../../docs/validation.md) §4.8。

Version I 的两张表未使用文本层转录（Table IV 由图像人工核对，且已由修正后的
模型独立复算验证），不受此影响。

李龙等 (2001) 的表 3 同样存在转录问题：其"全球平均\*"行注**据 Zartman and
Haines (1988)**，但下地壳 `238U/204Pb` 印成 `6.94`，而该文献实为 `6.49`
（数位颠倒）；三个 `Th/U` 也都与 Zartman & Haines 不符。该行不是校验目标，
但说明**这篇论文的表格本身有转录错误**，见
[`../../../docs/validation.md`](../../../docs/validation.md) §5.4。
