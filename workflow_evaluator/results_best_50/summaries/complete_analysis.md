# 📊 Workflow评估完整报告

**生成时间**: 2025-09-24 04:01:43

---

## 📋 执行摘要

本报告包含Workflow测试的完整分析结果，按以下维度组织：
1. 整体统计 - 所有测试的汇总指标
2. Data Source分析 - 按benchmark分类的详细统计
3. Operators分析 - 按operator组合分类的表现
4. 最佳表现 - 表现最好的组合排名
5. 错误分析 - 失败案例的分类和分析

---

## 📊 整体统计

### 基本指标

- **总测试数**: 45
- **成功数**: 45
- **失败数**: 0
- **成功率**: 100.0%
- **平均分数**: 0.605
- **分数标准差**: 0.313
- **最高分**: 0.980
- **最低分**: 0.060

### ⚡ 执行性能

- **平均执行时间**: 212.19秒
- **总执行时间**: 9548.60秒

### 📈 覆盖范围

- **Data Sources数量**: 12
- **Operators组合数**: 4


---

## 📁 按Data Source分类统计

### simpleqa

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.110
- 分数标准差: 0.042
- 最高分: 0.160
- 最低分: 0.060
- 平均执行时间: 144.67秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.160 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.120 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.060 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.100 |

---

### aime2024

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.156
- 分数标准差: 0.021
- 最高分: 0.167
- 最低分: 0.125
- 平均执行时间: 105.28秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.125 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.167 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.167 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.167 |

---

### humanevalplus

#### 基本统计
- 测试总数: 1
- 成功: 1
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.727
- 平均执行时间: 234.17秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.727 |

---

### math500

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.530
- 分数标准差: 0.077
- 最高分: 0.620
- 最低分: 0.440
- 平均执行时间: 538.03秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.500 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.440 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.560 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.620 |

---

### aime2025

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.229
- 分数标准差: 0.054
- 最高分: 0.292
- 最低分: 0.167
- 平均执行时间: 117.66秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.292 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.250 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.208 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.167 |

---

### humaneval

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.825
- 分数标准差: 0.089
- 最高分: 0.920
- 最低分: 0.740
- 平均执行时间: 65.01秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.880 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.760 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.920 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.740 |

---

### mgsmde

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.715
- 分数标准差: 0.344
- 最高分: 0.900
- 最低分: 0.200
- 平均执行时间: 440.63秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.200 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.900 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.900 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.860 |

---

### hotpotqa

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.895
- 分数标准差: 0.019
- 最高分: 0.920
- 最低分: 0.880
- 平均执行时间: 38.24秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.880 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.920 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.880 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.900 |

---

### gsm8k

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.920
- 分数标准差: 0.049
- 最高分: 0.980
- 最低分: 0.880
- 平均执行时间: 55.60秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.980 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.880 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.880 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.940 |

---

### mgsmbn

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.865
- 分数标准差: 0.034
- 最高分: 0.900
- 最低分: 0.820
- 平均执行时间: 344.46秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.900 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.860 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.880 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.820 |

---

### mbpp

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.550
- 分数标准差: 0.123
- 最高分: 0.660
- 最低分: 0.400
- 平均执行时间: 448.21秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.660 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.500 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.400 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.640 |

---

### drop

#### 基本统计
- 测试总数: 4
- 成功: 4
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.825
- 分数标准差: 0.030
- 最高分: 0.860
- 最低分: 0.800
- 平均执行时间: 30.81秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 1 | 100.0% | 0.860 |
| ensemble_generate_revise_summarize | 1 | 100.0% | 0.800 |
| ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.800 |
| decompose_ensemble_generate_programmer_revise_summarize | 1 | 100.0% | 0.840 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 11
- 成功: 11
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.585
- 分数标准差: 0.338
- 平均执行时间: 256.05秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 1 | 100.0% | 0.160 |
| aime2024 | 1 | 100.0% | 0.125 |
| math500 | 1 | 100.0% | 0.500 |
| aime2025 | 1 | 100.0% | 0.292 |
| humaneval | 1 | 100.0% | 0.880 |
| mgsmde | 1 | 100.0% | 0.200 |
| hotpotqa | 1 | 100.0% | 0.880 |
| gsm8k | 1 | 100.0% | 0.980 |
| mgsmbn | 1 | 100.0% | 0.900 |
| mbpp | 1 | 100.0% | 0.660 |
| drop | 1 | 100.0% | 0.860 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 11
- 成功: 11
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.600
- 分数标准差: 0.313
- 平均执行时间: 166.33秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 1 | 100.0% | 0.120 |
| aime2024 | 1 | 100.0% | 0.167 |
| math500 | 1 | 100.0% | 0.440 |
| aime2025 | 1 | 100.0% | 0.250 |
| humaneval | 1 | 100.0% | 0.760 |
| mgsmde | 1 | 100.0% | 0.900 |
| hotpotqa | 1 | 100.0% | 0.920 |
| gsm8k | 1 | 100.0% | 0.880 |
| mgsmbn | 1 | 100.0% | 0.860 |
| mbpp | 1 | 100.0% | 0.500 |
| drop | 1 | 100.0% | 0.800 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 11
- 成功: 11
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.605
- 分数标准差: 0.338
- 平均执行时间: 201.85秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 1 | 100.0% | 0.060 |
| aime2024 | 1 | 100.0% | 0.167 |
| math500 | 1 | 100.0% | 0.560 |
| aime2025 | 1 | 100.0% | 0.208 |
| humaneval | 1 | 100.0% | 0.920 |
| mgsmde | 1 | 100.0% | 0.900 |
| hotpotqa | 1 | 100.0% | 0.880 |
| gsm8k | 1 | 100.0% | 0.880 |
| mgsmbn | 1 | 100.0% | 0.880 |
| mbpp | 1 | 100.0% | 0.400 |
| drop | 1 | 100.0% | 0.800 |

---

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 12
- 成功: 12
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.627
- 分数标准差: 0.307
- 平均执行时间: 223.51秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 1 | 100.0% | 0.100 |
| aime2024 | 1 | 100.0% | 0.167 |
| humanevalplus | 1 | 100.0% | 0.727 |
| math500 | 1 | 100.0% | 0.620 |
| aime2025 | 1 | 100.0% | 0.167 |
| humaneval | 1 | 100.0% | 0.740 |
| mgsmde | 1 | 100.0% | 0.860 |
| hotpotqa | 1 | 100.0% | 0.900 |
| gsm8k | 1 | 100.0% | 0.940 |
| mgsmbn | 1 | 100.0% | 0.820 |
| mbpp | 1 | 100.0% | 0.640 |
| drop | 1 | 100.0% | 0.840 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | gsm8k | decompose_ensemble_generate_revise_summarize | 0.980 | 100.0% | 1 |
| 2 | gsm8k | decompose_ensemble_generate_programmer_revise_summarize | 0.940 | 100.0% | 1 |
| 3 | humaneval | ensemble_generate_programmer_revise_summarize | 0.920 | 100.0% | 1 |
| 4 | hotpotqa | ensemble_generate_revise_summarize | 0.920 | 100.0% | 1 |
| 5 | mgsmde | ensemble_generate_revise_summarize | 0.900 | 100.0% | 1 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | simpleqa | decompose_ensemble_generate_revise_summarize | 0.160 | 100.0% | 1 |
| 2 | aime2024 | decompose_ensemble_generate_revise_summarize | 0.125 | 100.0% | 1 |
| 3 | simpleqa | ensemble_generate_revise_summarize | 0.120 | 100.0% | 1 |
| 4 | simpleqa | decompose_ensemble_generate_programmer_revise_summarize | 0.100 | 100.0% | 1 |
| 5 | simpleqa | ensemble_generate_programmer_revise_summarize | 0.060 | 100.0% | 1 |

---

## 📝 结论

基于以上分析，可以得出以下结论：

1. ✅ 整体成功率较高 (100.0%)，表明workflow执行稳定
2. ⚠️ 平均分数中等 (0.605)，可以进一步优化

---

*报告结束*