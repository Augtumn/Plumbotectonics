# 计算原理

> [English](en/theory.md) | **简体中文**

本文档说明本仓库中三个模型（Version I、Version IV 与中国区域模型）的计算流程，
与 `src/plumbotectonics/version1.py`、`version4.py` 的实现逐行对应。

## 1. 总体框架

Plumbotectonics 把地球浅部划分为若干长期存在的**储库**（reservoir），
用离散的**造山旋回**（orogeny）描述储库之间的物质与同位素交换。
每个旋回分三步：

1. **取出**：从地幔与已有地壳中取出一部分物质；
2. **均一化**：取出的物质在造山带（orogene）内完全混合；
3. **再分配**：造山带物质重新分配为新上地壳、新下地壳（Version IV
   还有次地壳），以及返回地幔。

两次旋回之间，储库内部只发生放射性衰变，不发生物质交换。

**时间约定**

- 地质时间 $t$ 从现今向过去计（$t=0$ 为现今），单位 Ga；
- 旋回从最老到最新编号；
- 衰变常数单位 Ga$^{-1}$。

**记号**：$^{204}\mathrm{Pb}$ 记作 204，$^{206}\mathrm{Pb}$ 记作 206，
$^{207}\mathrm{Pb}$ 记作 207，$^{208}\mathrm{Pb}$ 记作 208，
$^{232}\mathrm{Th}$ 记作 232，$^{238}\mathrm{U}$ 记作 238。

---

## 2. Version I：Zartman & Doe (1981)

实现：`plumbotectonics.version1.run()`

### 2.1 初始条件

| 量 | 键 | 数值 |
|---|---|---|
| 起始时间 | — | 4.0 Ga |
| 旋回数 | — | 11（每 0.4 Ga 一次） |
| 地幔质量 | `mass` | $800\times10^{24}$ g |
| 204 | `204` | $38\times10^{15}$ mol |
| 238 | `238` | $349\times10^{15}$ mol |
| 232 | `232` | $1335\times10^{15}$ mol |
| 206/204 | — | 10.36 |
| 207/204 | — | 12.12 |
| 208/204 | — | 30.55 |

衰变常数：$\lambda_{238}=0.155125$，$\lambda_{235}=0.98485$，
$\lambda_{232}=0.049475$ Ga$^{-1}$；$^{238}\mathrm{U}/^{235}\mathrm{U}=137.88$。

### 2.2 旋回时间表

第 $j$ 次旋回（$j=0,\dots,10$）时间 $t_j = 4.0 - 0.4j$，
地幔贡献自身质量的比例为

$$
f_m=\begin{cases}
1/8, & j=0\\
1/16, & j=1\\
1/32, & j=2\\
1/64, & j=3\\
1/128, & j\ge 4
\end{cases}
$$

即前四次按 2 的幂递减，之后固定为 $1/128$。

### 2.3 造山带物质来源（质量）

上地壳的垂向剥蚀函数 $f_v=0.3$，面积剥蚀函数 $f_h=0.1$，
因此每个老上地壳段被取走

$$
\Delta M_u^{(i)} = (f_v+f_h-f_vf_h)\,M_u^{(i)} = 0.37\,M_u^{(i)} .
$$

下地壳只受面积剥蚀：

$$
\Delta M_l^{(i)} = f_h M_l^{(i)} = 0.10\,M_l^{(i)} .
$$

地幔贡献 $\Delta M_m = f_m M_m$。造山带总质量

$$
M_{or} = \Delta M_m + \sum_i \Delta M_u^{(i)} + \sum_i \Delta M_l^{(i)} .
$$

### 2.4 同位素增量

对每个同位素 $X\in\{204,206,207,208,232,238\}$：

$$
\Delta X_m = f_m E_m X_m ,\qquad
\Delta X_u^{(i)} = 0.37\,E_u X_u^{(i)} ,\qquad
\Delta X_l^{(i)} = 0.10\,E_l X_l^{(i)} ,
$$

其中地幔富集因子 $E_m=4$，上、下地壳 $E_u=E_l=1$。造山带内该同位素总量

$$
X_{or} = \Delta X_m + \sum_i \Delta X_u^{(i)} + \sum_i \Delta X_l^{(i)} .
$$

### 2.5 造山带再分配

每个旋回形成新的上、下地壳各

$$
M_u^{\mathrm{new}} = M_l^{\mathrm{new}} = 2.6\times10^{24}\ \mathrm{g},
$$

剩余造山带物质返回地幔，返回质量为

$$
M_{\mathrm{ret}} = M_{or} - 2.6 - 2.6 .
$$

Pb、U、Th 在三个**返回增量**（返回地幔 / 新上地壳 / 新下地壳）之间的
分配比为

| 元素 | $F^m$（地幔） | $F^u$（上地壳） | $F^l$（下地壳） |
|---|---|---|---|
| Pb | 0.028 | 0.754 | 0.218 |
| U | 0.024 | 0.854 | 0.122 |
| Th | 0.020 | 0.788 | 0.192 |

即代码中的 `F_PB`、`F_U`、`F_TH`。**这三个数是浓度比，不是份额**：每个
返回增量分到的造山带含量正比于「自身质量 × 分配比」，再除以归一化因子
$s$。这就是论文 eq. 17–19：

$$
s = M_{\mathrm{ret}}F^m + M_u^{\mathrm{new}}F^u + M_l^{\mathrm{new}}F^l,
$$

$$
X_m^{\mathrm{ret}} = X_{or}\frac{M_{\mathrm{ret}}F^m}{s},\qquad
X_u^{\mathrm{new}} = X_{or}\frac{M_u^{\mathrm{new}}F^u}{s},\qquad
X_l^{\mathrm{new}} = X_{or}\frac{M_l^{\mathrm{new}}F^l}{s}.
$$

三者之和恰为 $X_{or}$，因此再分配过程本身不产生也不损失任何元素。

> **为什么不能把分配比直接当份额用。** 返回地幔的质量（首轮 $M_{\mathrm{ret}}
> = 94.8$）比每个新地壳段（2.6）大一到两个数量级，因此地幔首轮实际拿到
> 造山带 Pb 的 $94.8\times0.028/s = 51.3\%$，而不是 $2.8\%$。把 `F_PB[0]`
> 当作造山带含量的分数会抽干地幔、喂饱地壳，这正是本仓库早先 1.5 % 偏差的
> 来源；修正前后的对照见 [`validation.md`](validation.md) §2.1。

地幔的该元素总量更新为

$$
X_m \leftarrow X_m - \Delta X_m + X_m^{\mathrm{ret}},
$$

地幔质量更新为

$$
M_m \leftarrow M_m - \Delta M_m + M_{\mathrm{ret}}.
$$

老上、下地壳段分别按 $M\leftarrow 0.63M$、$M\leftarrow 0.90M$ 收缩。

### 2.6 放射性衰变

旋回之间母体视为常数，子体按

$$
\begin{aligned}
^{206}\mathrm{Pb}(t') &= ^{206}\mathrm{Pb}(t'') + ^{238}\mathrm{U}\left(e^{\lambda_{238}t'}-e^{\lambda_{238}t''}\right),\\
^{207}\mathrm{Pb}(t') &= ^{207}\mathrm{Pb}(t'') + \frac{^{238}\mathrm{U}}{137.88}\left(e^{\lambda_{235}t'}-e^{\lambda_{235}t''}\right),\\
^{208}\mathrm{Pb}(t') &= ^{208}\mathrm{Pb}(t'') + ^{232}\mathrm{Th}\left(e^{\lambda_{232}t'}-e^{\lambda_{232}t''}\right),
\end{aligned}
$$

其中 $t'=t_j$，$t''=t_{j+1}=t_j-0.4$。

### 2.7 输出

`run()` 返回四元组 `(history, mantle, upper_segs, lower_segs)`。

`history` 每个旋回一项：

```python
{
  "t": 4.0,                        # Ga
  "mantle":  {"206/204": ..., "207/204": ..., "208/204": ...},
  "orogene": {...},                # 该旋回造山带混合后的比值
  "upper":   {...} | None,         # 所有上地壳段的摩尔加权平均
  "lower":   {...} | None,
}
```

> 第一次旋回时还没有老地壳，`upper`/`lower` 为 `None`；
> 段储库按质量加权求和后再取比值（`avg_res`）。

---

## 3. Version IV：Haines & Zartman (1988)

> 本章描述 Version IV 的实现（Haines & Zartman, 1988）。造山带三分量与双向物质交换（bi-directional transport，即 §3.5 的 gates）的物理依据另见 Zartman & Haines (1988)。

实现：`plumbotectonics.version4.run()`

### 3.1 储库与状态数组

| 索引 $j$ | 储库 |
|---|---|
| 0 | 地幔 |
| 1 | 上地壳段 |
| 2 | 下地壳段 |
| 3 | 次地壳（subcrustal lithosphere） |

状态数组 `M[h][i][k][j]`（实现中是 NumPy 数组 `M[h, i, k, j]`，形状
`(7, 3, 48, 4)`）：

- `h`：0 = 质量，1–4 = 204/206/207/208，5 = 232，6 = 238；
- `i`：1 = 旋回开始（造山前），2 = 旋回结束（造山后）；
- `k`：旋回序号 1–46（地幔另存 `k+1`）；
- `j`：储库（见上表）。

初始条件（`k=1, i=1, j=0`）：质量 $1050\times10^{24}$ g，
204 $=19\times10^{15}$ mol，232 $=758\times10^{15}$ mol，
238 $=177\times10^{15}$ mol，
$^{206}\mathrm{Pb}/^{204}\mathrm{Pb}=9.0668$，
$^{207}\mathrm{Pb}/^{204}\mathrm{Pb}=9.9367$，
$^{208}\mathrm{Pb}/^{204}\mathrm{Pb}=28.6528$。

> 这三个初始比值是**标定值**（校准到 Table 4），不是 Table 3 的印刷值。

### 3.2 时间与旋回

$$
T_k = 4.5 - 0.1(k-1),\qquad \Delta T = 0.1\ \mathrm{Ga},
$$

`history` 中记录的时间为 $T_k-\Delta T$，即 4.4 → 0.0 Ga，共 46 个旋回。
每个旋回结束后按区间 $[T_k-\Delta T,\ T_k]$ 做衰变。

### 3.3 时间相关参数（Table 3）

按旋回号 $k$ 查表：

| 数组 | 含义 |
|---|---|
| `A1[k]` | 地幔被取出的质量比例 |
| `A4[k]` | 上地壳剥蚀系数 |
| `A5[k]` | 下地壳剥蚀系数（代码中 `A5 = A4[:]`） |
| `A6[k]` | 次地壳剥蚀系数 |
| `U[k]` | 新上地壳质量 |
| `L[k]` | 新下地壳质量 |
| `S[k]` | 新次地壳质量 |

在本数据集中 Table 3 的 A4、A6 两列相同，且 `U == L`，因此
`A4 = A5 = A6`。

其他固定参数：`A2=0.2`（MOR 比例），`A3=0.05`（垂向剥蚀），
`B1=1.0`，`B2=0.01`，`B3=0.0`，`Bs=0.001`，`H0=35/Bs=35000`，
`dp=0.14`（默认）。

### 3.4 质量传输（每个旋回 $k$）

对每个较老的上地壳段 $j<k$：

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

对较老的下地壳段：$L_h = M_l A_5$，$M_l\leftarrow M_l-L_h$。

对较老的次地壳段：$S_h = M_s A_6$，$M_s\leftarrow M_s-S_h$。

汇总：

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

其中 $S_{re}=\sum S_h$，$S_{mant}$ 见 §3.5。

### 3.5 门（gates）

> 门的符号与顺序取自 Haines & Zartman (1988) 的 BASIC 程序；造山带与次地壳/地幔之间双向交换的物理依据见 Zartman & Haines (1988)。

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

三元组（远端 $D$、近端 $P$、楔形 $W$）按顺序扣除/加入：

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

新储库：

$$
M_u^{\mathrm{new}} = U_k,\qquad
M_l^{\mathrm{new}} = L_k,\qquad
M_s^{\mathrm{new}} = S_k,
$$

$$
M_m^{\mathrm{new}} = M_m - A_1 M_m + D^{(2)} - S_{mant} + R_{mor}.
$$

### 3.6 同位素传输：`FNEmoles`

把“元素偏好”转换成两端的摩尔分配：

$$
\mathrm{Bang} = \frac{\mathrm{Bias}}{1+\mathrm{Bias}},\qquad
\mathrm{Denom} = \mathrm{Mass}_1\,\mathrm{Bang} + \mathrm{Mass}_2(1-\mathrm{Bang}),
$$

$$
\mathrm{Moles} = N\,\frac{\mathrm{Mass}_1\,\mathrm{Bang}}{\mathrm{Denom}} .
$$

参数：$N$ 为待分配总摩尔数；$\mathrm{Mass}_1,\mathrm{Mass}_2$ 为两端质量；
$\mathrm{Bias}$ 为富集因子。$\mathrm{Bias}\le0$ 或 $\mathrm{Denom}=0$ 时返回 0。

Version IV 使用的富集/分配系数（按 204/206/207/208/232/238 排列）：

| 数组 | 作用 |
|---|---|
| `E_a2` | 地幔 → MOR |
| `F_a3` | 垂向剥蚀物质 → 远端/近端 |
| `E_b1` | 远端 → 近端（gate b1） |
| `E_b2` | 远端 → 楔形（gate b2） |
| `E_b3` | 楔形 → 近端（gate b3） |
| `F_c3` | 近端 → 新上/下地壳 |

这些数值是**校准到 Table 4** 的（`version4.py` 中有注释），
与 Table 3 的印刷整数（如 Pb 的 `E_a2=80`、`F_a3=1.00` 等）不同；印刷值仅作
量级参考。

### 3.7 同位素传输

几何结构与 §3.4/§3.5 完全一致，只是每个分配步骤用 `FNEmoles`，
并把质量换成对应同位素的摩尔数；此外：

- 上/下/次地壳的取出分别乘以 `E_up`、`E_low`、`E_sub`（本实现均为 1）；
- $S_{mant}$ 按质量比例分配到同位素：
  $S_{mant}^{(h)} = \dfrac{S_{mant}}{M_m-M_{or}}\left(M_m^{(h)}-M_{or}^{(h)}\right)$；
- 新上地壳由 `FNEmoles(P_oro, U_k, L_k, F_c3[h])` 得到，其余给新下地壳：
  $M_u^{new(h)} = \mathrm{FNEmoles}(P_{oro}^{(h)}, U_k, L_k, F_{c3}[h])$，
  $M_l^{new(h)} = P_{oro}^{(h)} - M_u^{new(h)}$；
- 新次地壳取楔形组分 $W^{(2)}$。

### 3.8 衰变

旋回 $k$ 结束后，对地幔与所有地壳段执行

$$
\begin{aligned}
^{206}\mathrm{Pb} &\mathrel{+}= ^{238}\mathrm{U}\left(e^{\lambda_{238}T}-e^{\lambda_{238}(T-\Delta T)}\right),\\
^{207}\mathrm{Pb} &\mathrel{+}= \frac{^{238}\mathrm{U}}{137.88}\left(e^{\lambda_{235}T}-e^{\lambda_{235}(T-\Delta T)}\right),\\
^{208}\mathrm{Pb} &\mathrel{+}= ^{232}\mathrm{Th}\left(e^{\lambda_{232}T}-e^{\lambda_{232}(T-\Delta T)}\right),
\end{aligned}
$$

其中 $T=T_k$，$\Delta T=0.1$ Ga。

### 3.9 输出

`run(dp=0.14, double_eroded=False)` 返回字典：

| 键 | 内容 |
|---|---|
| `mantle` / `upper` / `lower` / `sub` | 最终各储库的同位素摩尔数（键 1–6） |
| `total` | 四储库之和 |
| `masses` | 最终质量（`mantle`/`upper`/`lower`/`sub`/`total`） |
| `last_upper` / `last_lower` / `last_sub` | 最年轻地壳段 |
| `history` | 每个旋回一条记录（`cycle`、`time_Ga`、`mantle`、`upper`、`lower`、`sub`、`orogene`） |

`ratios(d)` 把键 1–6 的字典换算成
`206/204`、`207/204`、`208/204`、`238U/204Pb`、`232Th/238U`、`232Th/204Pb`。

### 3.10 可调参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `dp` | 0.14 | 垂向剥蚀物质中“外板”（outboard）的比例 |
| `double_eroded` | `False` | 为 `True` 时在同位素阶段再对 `U_eroded` 乘一次 $(1-A_4)$ |

---

## 4. 中国区域模型：李龙等 (2001)

### 4.1 定位

论文以「铅构造模式」为基础为中国大陆建区域模型（先例：Godwin & Sinclair (1982)
为加拿大西部建过区域模型）。它的核心论点是**中国大陆由一个相对贫 U 而富 Th 的
体系演化而来，且上、下地壳分异更彻底**；判定依据是定性的两条——花岗岩长石数据
在模式曲线上指示源区的自洽性，以及模式年龄与其它方法的吻合。论文**没有**声明
复现任何数值表。

本实现取：**算法沿用 Zartman & Doe (1981)**（即 `version1`），只替换论文自己印出
的两张表。

### 4.2 与 Version I 的差异

| 项目 | Version I | 中国模型 |
|---|---|---|
| 4.0 Ga 初始比值 | 10.36 / 12.12 / 30.55 | **10.17 / 12.07 / 30.56**（论文表 1） |
| 分配系数 | Pb 0.028/0.754/0.218 等 | **论文表 2**：Pb 0.038/0.235/0.727、U 0.024/0.111/0.865、Th 0.021/0.162/0.817 |
| 下地壳保留比例 $p^l$ | 0.90（侵蚀 0.10） | **0.95**（侵蚀 0.05）（论文 eq. 2） |
| 残余造山带 | 100 % 返回地幔 | **90 %** 返回，10 % 成为上地壳沉积岩（论文 eqs. 7-8、假设 3d） |
| 初始丰度、质量、$k_i$、衰变常数 | ZD1981 | **继承 ZD1981**（论文未给出） |

分配系数的列序要注意：论文表 2 印的是 **(地幔, 下地壳, 上地壳)**，与 ZD1981
表 II 的 (地幔, 上地壳, 下地壳) 相反，故 `china.py` 中 `F_PB[2]` 是上地壳。

### 4.3 第 10 % 残余造山带的去向

论文假设 (3d)：残余造山带的绝大部分很快返回地幔，但"有一部分仍然残留在地壳边缘
或被剥蚀成为沉积岩"。设该量为造山带总量的 10 %，则地幔得到

$$\Delta M_m = 0.9 \times \Delta M_o$$

**这 10 % 不能丢弃**——丢弃会使系统总质量从 800 掉到 780.2（×10²⁴ g）。按论文
语义它成为沉积岩，属上地壳，故作为独立一层加入上地壳，此后随其它上地壳层
一起按 $p^u$ 被侵蚀。

### 4.4 $E_m$ 作用于哪一端

论文 eq. (5) 写的是"**进入造山带**的化学元素"：

$$\Delta^\alpha N_r^i = \frac{\Delta M_r^i}{M_r^i} \cdot {}^\alpha N_r^i \cdot {}^\alpha E^r$$

它规定了造山带的**增益**，没有单独写地幔的**亏损**。从物理上二者必须相等：地幔
发生部分熔融时，被抽走的质量是 $f_m M_m$，而抽走物质的浓度是地幔自身的 $E_m$ 倍
（$E_m=4$ 对应 25 % 熔融），所以

$$\Delta N_{\text{亏损}} = f_m M_m \times E_m \frac{N_m}{M_m} = f_m E_m N_m$$

**这与造山带收到的量恰好相同。** 若地幔只亏损 $f_m N_m$ 而造山带仍收 $f_m E_m N_m$，
差额 $(E_m-1) f_m N_m$ 每次造山都**凭空产生**；实测末态／初始为
²⁰⁴Pb 1.965、²³⁸U 1.926、²³²Th 1.914，即全系统元素翻倍。因此本实现取
**地幔亏损带 $E_m$**，守恒检验见 `docs/validation.md` §5.5。

### 4.5 两种等价的衰变参数化

| | 母体常数化（默认） | 母体真衰变（论文 eqs. 9-10） |
|---|---|---|
| 母体 | 固定在现代等效丰度（238U = 349） | 实际 4.0 Ga 丰度（238U = 649.09） |
| 子体增量 | $e^{\lambda t} - e^{\lambda t'}$ | $1 - e^{-\lambda \Delta t}$ |
| ²⁰⁷Pb 母体 | $^{238}\text{U}/137.88$ | 独立跟踪的 ²³⁵U |
| ²³⁸U/²³⁵U(4.0 Ga) | 隐含 137.88 | **4.9897**（今天的 27.6 倍） |

**两者逐位等价**（最大差 2.1×10⁻¹⁴）：因为「常数化母体 + 349/1335」与「母体衰变 +
反推的实际丰度 649/1627」是同一件事的两种写法。`decay_parents` 开关用于在两者间
切换，默认取 ZD1981 的写法。

### 4.6 $E_m=4$ 与递减的 $f_m$

论文把 $E_m=4$ 解释为"模拟平均地幔 25 % 熔融的熔体全部进入造山带"，而
$k_i$ 从 1/8 递减到 1/128。批式熔融下，完全不相容元素（$D=0$）的富集因子为

$$E = \frac{1}{D + F(1-D)} = \frac{1}{F}$$

即 $f_m=1/8$ 时 $E=8$、$f_m=1/128$ 时 $E=128$。固定 $E=4$ 是 ZD1981 的简化约定，
不是批式熔融的结果。`melt_model="batch"` 提供 $E=1/f_m$ 的备选；实测它反而更差
（表 3 最大偏差 1.18 对 0.62），故默认保持论文约定。

### 4.7 精度

| 数据 | 最大绝对偏差 | 平均 | RMSE |
|---|---|---|---|
| 论文表 3（99 项） | 0.6211 | 0.2199 | 0.2719 |
| 论文表 4（6 项） | 0.4715 | 0.1793 | 0.2353 |

**表 3 没有复现**（表印到 0.01）。从表 3 与表 4 分别反演初始值得到的新成地壳质量
相差约 13σ，说明**论文这两张表互不相容**。详见 `docs/validation.md` §5。

---

## 5. 两版本对照

| 项目 | Version I | Version IV |
|---|---|---|
| 储库 | 地幔、上/下地壳 | + 次地壳、MOR、造山带三分量 |
| 旋回 | 11 × 0.4 Ga | 46 × 0.1 Ga |
| 分配方式 | 分配比 `F_PB`/`F_U`/`F_TH` 按返回增量质量加权（eq. 17–19） | `FNEmoles` + 富集系数数组 |
| 时间参数 | 无表 | Table 3 的 `A1`/`A4`/`A6`/`U`/`L`/`S` |
| 校验目标 | Table IV 全部 126 项 + Table II 第三节（印刷精度内） | Table 4 精确值（< 0.02） |

中国模型与 Version I 的关系见 §4.2：同一算法，只换两张表。

## 6. 参考文献

1. Haines, S. M., & Zartman, R. E. (1988). PLUMBO; a Hewlett-Packard Series 200 BASIC language program for version IV of plumbotectonics. In *Open-File Report* (Nos. 88–269). U.S. Geological Survey. https://doi.org/10.3133/ofr88269
2. Zartman, R. E., & Doe, B. R. (1981). Plumbotectonics—The model. *Tectonophysics*, *75*(1–2), 135–162. https://doi.org/10.1016/0040-1951(81)90213-4
3. Zartman, R. E., & Haines, S. M. (1988). The plumbotectonic model for Pb isotopic systematics among major terrestrial reservoirs—A case for bi-directional transport. *Geochimica et Cosmochimica Acta*, *52*(6), 1327–1339. https://doi.org/10.1016/0016-7037(88)90204-9
4. 李龙, 郑永飞, 周建波 (2001). 中国大陆地壳铅同位素演化的动力学模型. *岩石学报*, *17*(1), 61–68.
