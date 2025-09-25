# 📊 Workflow评估完整报告

**生成时间**: 2025-09-24 04:44:28

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

- **总测试数**: 622
- **成功数**: 622
- **失败数**: 0
- **成功率**: 100.0%
- **平均分数**: 0.236
- **分数标准差**: 0.363
- **最高分**: 1.000
- **最低分**: 0.000

### ⚡ 执行性能

- **平均执行时间**: 24.09秒
- **总执行时间**: 14986.69秒

### 📈 覆盖范围

- **Data Sources数量**: 14
- **Operators组合数**: 5


---

## 📁 按Data Source分类统计

### mbppplus

#### 基本统计
- 测试总数: 50
- 成功: 50
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.116
- 分数标准差: 0.190
- 最高分: 0.600
- 最低分: 0.000
- 平均执行时间: 21.33秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.140 |
| ensemble_generate_revise_summarize | 15 | 100.0% | 0.093 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.200 |
| decompose_ensemble_generate_revise_summarize | 15 | 100.0% | 0.067 |

---

### humaneval

#### 基本统计
- 测试总数: 60
- 成功: 60
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.223
- 分数标准差: 0.377
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 18.28秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.147 |
| ensemble_generate_revise_summarize | 15 | 100.0% | 0.280 |
| ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.173 |
| decompose_ensemble_generate_revise_summarize | 15 | 100.0% | 0.293 |

---

### mgsmde

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.400
- 分数标准差: 0.437
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 23.66秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.460 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.420 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.380 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.340 |

---

### mgsmbn

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.435
- 分数标准差: 0.459
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 21.22秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.400 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.440 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.460 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.440 |

---

### math500

#### 基本统计
- 测试总数: 60
- 成功: 60
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.200
- 分数标准差: 0.306
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 20.77秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.187 |
| ensemble_generate_revise_summarize | 15 | 100.0% | 0.173 |
| ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.240 |
| decompose_ensemble_generate_revise_summarize | 15 | 100.0% | 0.200 |

---

### hotpotqa

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.430
- 分数标准差: 0.465
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 12.38秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.440 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.420 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.500 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.360 |

---

### simpleqa

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.060
- 分数标准差: 0.122
- 最高分: 0.400
- 最低分: 0.000
- 平均执行时间: 10.23秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.040 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.100 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.080 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.020 |

---

### drop

#### 基本统计
- 测试总数: 60
- 成功: 60
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.260
- 分数标准差: 0.406
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 6.83秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.187 |
| ensemble_generate_revise_summarize | 15 | 100.0% | 0.333 |
| ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.307 |
| decompose_ensemble_generate_revise_summarize | 15 | 100.0% | 0.213 |

---

### imo

#### 基本统计
- 测试总数: 12
- 成功: 12
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 0.18秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| ensemble_generate_refiner_verifier | 12 | 100.0% | 0.000 |

---

### gsm8k

#### 基本统计
- 测试总数: 60
- 成功: 60
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.297
- 分数标准差: 0.429
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 13.14秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.307 |
| ensemble_generate_revise_summarize | 15 | 100.0% | 0.293 |
| ensemble_generate_programmer_revise_summarize | 15 | 100.0% | 0.320 |
| decompose_ensemble_generate_revise_summarize | 15 | 100.0% | 0.267 |

---

### humanevalplus

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.355
- 分数标准差: 0.386
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 38.54秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.260 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.400 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.340 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.420 |

---

### mbpp

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.175
- 分数标准差: 0.294
- 最高分: 1.000
- 最低分: 0.000
- 平均执行时间: 32.41秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.100 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.260 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.040 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.300 |

---

### aime2025

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.130
- 分数标准差: 0.224
- 最高分: 0.800
- 最低分: 0.000
- 平均执行时间: 58.40秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.100 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.120 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.080 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.220 |

---

### aime2024

#### 基本统计
- 测试总数: 40
- 成功: 40
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.075
- 分数标准差: 0.126
- 最高分: 0.400
- 最低分: 0.000
- 平均执行时间: 62.57秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.100 |
| ensemble_generate_revise_summarize | 10 | 100.0% | 0.120 |
| ensemble_generate_programmer_revise_summarize | 10 | 100.0% | 0.040 |
| decompose_ensemble_generate_revise_summarize | 10 | 100.0% | 0.040 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 150
- 成功: 150
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.219
- 分数标准差: 0.346
- 平均执行时间: 25.41秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| mbppplus | 10 | 100.0% | 0.140 |
| humaneval | 15 | 100.0% | 0.147 |
| mgsmde | 10 | 100.0% | 0.460 |
| mgsmbn | 10 | 100.0% | 0.400 |
| math500 | 15 | 100.0% | 0.187 |
| hotpotqa | 10 | 100.0% | 0.440 |
| simpleqa | 10 | 100.0% | 0.040 |
| drop | 15 | 100.0% | 0.187 |
| gsm8k | 15 | 100.0% | 0.307 |
| humanevalplus | 10 | 100.0% | 0.260 |
| mbpp | 10 | 100.0% | 0.100 |
| aime2025 | 10 | 100.0% | 0.100 |
| aime2024 | 10 | 100.0% | 0.100 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 155
- 成功: 155
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.261
- 分数标准差: 0.378
- 平均执行时间: 23.36秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| mbppplus | 15 | 100.0% | 0.093 |
| humaneval | 15 | 100.0% | 0.280 |
| mgsmde | 10 | 100.0% | 0.420 |
| mgsmbn | 10 | 100.0% | 0.440 |
| math500 | 15 | 100.0% | 0.173 |
| hotpotqa | 10 | 100.0% | 0.420 |
| simpleqa | 10 | 100.0% | 0.100 |
| drop | 15 | 100.0% | 0.333 |
| gsm8k | 15 | 100.0% | 0.293 |
| humanevalplus | 10 | 100.0% | 0.400 |
| mbpp | 10 | 100.0% | 0.260 |
| aime2025 | 10 | 100.0% | 0.120 |
| aime2024 | 10 | 100.0% | 0.120 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 150
- 成功: 150
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.245
- 分数标准差: 0.374
- 平均执行时间: 22.46秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| mbppplus | 10 | 100.0% | 0.200 |
| humaneval | 15 | 100.0% | 0.173 |
| mgsmde | 10 | 100.0% | 0.380 |
| mgsmbn | 10 | 100.0% | 0.460 |
| math500 | 15 | 100.0% | 0.240 |
| hotpotqa | 10 | 100.0% | 0.500 |
| simpleqa | 10 | 100.0% | 0.080 |
| drop | 15 | 100.0% | 0.307 |
| gsm8k | 15 | 100.0% | 0.320 |
| humanevalplus | 10 | 100.0% | 0.340 |
| mbpp | 10 | 100.0% | 0.040 |
| aime2025 | 10 | 100.0% | 0.080 |
| aime2024 | 10 | 100.0% | 0.040 |

---

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 155
- 成功: 155
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.239
- 分数标准差: 0.365
- 平均执行时间: 26.99秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| mbppplus | 15 | 100.0% | 0.067 |
| humaneval | 15 | 100.0% | 0.293 |
| mgsmde | 10 | 100.0% | 0.340 |
| mgsmbn | 10 | 100.0% | 0.440 |
| math500 | 15 | 100.0% | 0.200 |
| hotpotqa | 10 | 100.0% | 0.360 |
| simpleqa | 10 | 100.0% | 0.020 |
| drop | 15 | 100.0% | 0.213 |
| gsm8k | 15 | 100.0% | 0.267 |
| humanevalplus | 10 | 100.0% | 0.420 |
| mbpp | 10 | 100.0% | 0.300 |
| aime2025 | 10 | 100.0% | 0.220 |
| aime2024 | 10 | 100.0% | 0.040 |

---

### ensemble_generate_refiner_verifier

#### 基本统计
- 测试总数: 12
- 成功: 12
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 0.18秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| imo | 12 | 100.0% | 0.000 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | hotpotqa | ensemble_generate_programmer_revise_summarize | 0.500 | 100.0% | 10 |
| 2 | mgsmde | decompose_ensemble_generate_programmer_revise_summarize | 0.460 | 100.0% | 10 |
| 3 | mgsmbn | ensemble_generate_programmer_revise_summarize | 0.460 | 100.0% | 10 |
| 4 | mgsmbn | ensemble_generate_revise_summarize | 0.440 | 100.0% | 10 |
| 5 | mgsmbn | decompose_ensemble_generate_revise_summarize | 0.440 | 100.0% | 10 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | mbpp | ensemble_generate_programmer_revise_summarize | 0.040 | 100.0% | 10 |
| 2 | aime2024 | ensemble_generate_programmer_revise_summarize | 0.040 | 100.0% | 10 |
| 3 | aime2024 | decompose_ensemble_generate_revise_summarize | 0.040 | 100.0% | 10 |
| 4 | simpleqa | decompose_ensemble_generate_revise_summarize | 0.020 | 100.0% | 10 |
| 5 | imo | ensemble_generate_refiner_verifier | 0.000 | 100.0% | 12 |

---

## 📝 结论

基于以上分析，可以得出以下结论：

1. ✅ 整体成功率较高 (100.0%)，表明workflow执行稳定
2. ❌ 平均分数较低 (0.236)，需要改进workflow设计

---

*报告结束*