# 📊 Workflow评估完整报告

**生成时间**: 2025-09-23 22:32:24

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

- **总测试数**: 266
- **成功数**: 266
- **失败数**: 0
- **成功率**: 100.0%
- **平均分数**: 0.553
- **分数标准差**: 0.366
- **最高分**: 1.000
- **最低分**: 0.000

### ⚡ 执行性能

- **平均执行时间**: 56.19秒
- **总执行时间**: 14946.36秒

### 📈 覆盖范围

- **Data Sources数量**: 14
- **Operators组合数**: 5


---

## 📁 按Data Source分类统计

### simpleqa

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.120
- 分数标准差: 0.151
- 最高分: 0.400
- 最低分: 0.000
- 平均执行时间: 20.34秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.040 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.200 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.160 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.080 |

---

### aime2024

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.150
- 分数标准差: 0.143
- 最高分: 0.400
- 最低分: 0.000
- 平均执行时间: 125.03秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.080 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.240 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.080 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.200 |

---

### humanevalplus

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.710
- 分数标准差: 0.200
- 最高分: 1.000
- 最低分: 0.400
- 平均执行时间: 76.97秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.840 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.800 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.680 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.520 |

---

### math500

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.600
- 分数标准差: 0.195
- 最高分: 1.000
- 最低分: 0.200
- 平均执行时间: 62.13秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.600 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.520 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.720 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.560 |

---

### aime2025

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.260
- 分数标准差: 0.260
- 最高分: 0.800
- 最低分: 0.000
- 平均执行时间: 116.69秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.440 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.240 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.160 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.200 |

---

### imo

#### 基本统计
- 测试总数: 6
- 成功: 6
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 0.30秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| ensemble_generate_refiner_verifier | 6 | 100.0% | 0.000 |

---

### humaneval

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.670
- 分数标准差: 0.357
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 54.56秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.880 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.840 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.520 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.440 |

---

### mgsmde

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.800
- 分数标准差: 0.234
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 47.21秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.680 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.840 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.760 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.920 |

---

### hotpotqa

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.860
- 分数标准差: 0.235
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 24.66秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.720 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.840 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 1.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.880 |

---

### gsm8k

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.890
- 分数标准差: 0.121
- 最高分: 1.000
- 最低分: 0.600
- 平均执行时间: 39.17秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.800 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.880 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.960 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.920 |

---

### mgsmbn

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.870
- 分数标准差: 0.187
- 最高分: 1.000
- 最低分: 0.400
- 平均执行时间: 42.32秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.880 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.880 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.920 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.800 |

---

### mbpp

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.350
- 分数标准差: 0.336
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 64.68秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.600 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.520 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.080 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.200 |

---

### drop

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.780
- 分数标准差: 0.289
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 20.31秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.640 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 1.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.920 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.560 |

---

### mbppplus

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.290
- 分数标准差: 0.200
- 最高分: 0.600
- 最低分: 0.000
- 平均执行时间: 53.16秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.200 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.280 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.400 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.280 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 65
- 成功: 65
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.569
- 分数标准差: 0.361
- 平均执行时间: 64.20秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 5 | 100.0% | 0.040 |
| aime2024 | 5 | 100.0% | 0.080 |
| humanevalplus | 5 | 100.0% | 0.840 |
| math500 | 5 | 100.0% | 0.600 |
| aime2025 | 5 | 100.0% | 0.440 |
| humaneval | 5 | 100.0% | 0.880 |
| mgsmde | 5 | 100.0% | 0.680 |
| hotpotqa | 5 | 100.0% | 0.720 |
| gsm8k | 5 | 100.0% | 0.800 |
| mgsmbn | 5 | 100.0% | 0.880 |
| mbpp | 5 | 100.0% | 0.600 |
| drop | 5 | 100.0% | 0.640 |
| mbppplus | 5 | 100.0% | 0.200 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 65
- 成功: 65
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.622
- 分数标准差: 0.339
- 平均执行时间: 55.56秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 5 | 100.0% | 0.200 |
| aime2024 | 5 | 100.0% | 0.240 |
| humanevalplus | 5 | 100.0% | 0.800 |
| math500 | 5 | 100.0% | 0.520 |
| aime2025 | 5 | 100.0% | 0.240 |
| humaneval | 5 | 100.0% | 0.840 |
| mgsmde | 5 | 100.0% | 0.840 |
| hotpotqa | 5 | 100.0% | 0.840 |
| gsm8k | 5 | 100.0% | 0.880 |
| mgsmbn | 5 | 100.0% | 0.880 |
| mbpp | 5 | 100.0% | 0.520 |
| drop | 5 | 100.0% | 1.000 |
| mbppplus | 5 | 100.0% | 0.280 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 65
- 成功: 65
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.566
- 分数标准差: 0.375
- 平均执行时间: 51.68秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 5 | 100.0% | 0.160 |
| aime2024 | 5 | 100.0% | 0.080 |
| humanevalplus | 5 | 100.0% | 0.680 |
| math500 | 5 | 100.0% | 0.720 |
| aime2025 | 5 | 100.0% | 0.160 |
| humaneval | 5 | 100.0% | 0.520 |
| mgsmde | 5 | 100.0% | 0.760 |
| hotpotqa | 5 | 100.0% | 1.000 |
| gsm8k | 5 | 100.0% | 0.960 |
| mgsmbn | 5 | 100.0% | 0.920 |
| mbpp | 5 | 100.0% | 0.080 |
| drop | 5 | 100.0% | 0.920 |
| mbppplus | 5 | 100.0% | 0.400 |

---

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 65
- 成功: 65
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.505
- 分数标准差: 0.364
- 平均执行时间: 58.47秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| simpleqa | 5 | 100.0% | 0.080 |
| aime2024 | 5 | 100.0% | 0.200 |
| humanevalplus | 5 | 100.0% | 0.520 |
| math500 | 5 | 100.0% | 0.560 |
| aime2025 | 5 | 100.0% | 0.200 |
| humaneval | 5 | 100.0% | 0.440 |
| mgsmde | 5 | 100.0% | 0.920 |
| hotpotqa | 5 | 100.0% | 0.880 |
| gsm8k | 5 | 100.0% | 0.920 |
| mgsmbn | 5 | 100.0% | 0.800 |
| mbpp | 5 | 100.0% | 0.200 |
| drop | 5 | 100.0% | 0.560 |
| mbppplus | 5 | 100.0% | 0.280 |

---

### ensemble_generate_refiner_verifier

#### 基本统计
- 测试总数: 6
- 成功: 6
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 0.30秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| imo | 6 | 100.0% | 0.000 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | hotpotqa | ensemble_generate_programmer_revise_summarize | 1.000 | 100.0% | 5 |
| 2 | drop | ensemble_generate_revise_summarize | 1.000 | 100.0% | 5 |
| 3 | gsm8k | ensemble_generate_programmer_revise_summarize | 0.960 | 100.0% | 5 |
| 4 | mgsmde | decompose_ensemble_generate_programmer_revise_summarize | 0.920 | 100.0% | 5 |
| 5 | gsm8k | decompose_ensemble_generate_programmer_revise_summarize | 0.920 | 100.0% | 5 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | aime2024 | decompose_ensemble_generate_revise_summarize | 0.080 | 100.0% | 5 |
| 2 | aime2024 | ensemble_generate_programmer_revise_summarize | 0.080 | 100.0% | 5 |
| 3 | mbpp | ensemble_generate_programmer_revise_summarize | 0.080 | 100.0% | 5 |
| 4 | simpleqa | decompose_ensemble_generate_revise_summarize | 0.040 | 100.0% | 5 |
| 5 | imo | ensemble_generate_refiner_verifier | 0.000 | 100.0% | 6 |

---

## 📝 结论

基于以上分析，可以得出以下结论：

1. ✅ 整体成功率较高 (100.0%)，表明workflow执行稳定
2. ❌ 平均分数较低 (0.553)，需要改进workflow设计

---

*报告结束*