# 📊 Workflow评估完整报告

**生成时间**: 2025-09-25 14:54:59

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

- **总测试数**: 80
- **成功数**: 12
- **失败数**: 68
- **成功率**: 15.0%
- **平均分数**: 0.312
- **分数标准差**: 0.461
- **最高分**: 0.980
- **最低分**: 0.000

### ⚡ 执行性能

- **平均执行时间**: 5.78秒
- **总执行时间**: 462.50秒

### 📈 覆盖范围

- **Data Sources数量**: 4
- **Operators组合数**: 4


---

## 📁 按Data Source分类统计

### math500

#### 基本统计
- 测试总数: 20
- 成功: 0
- 失败: 20
- 成功率: 0.0%
- 平均分: 0.000
- 平均执行时间: 0.01秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |

---

### gsm8k

#### 基本统计
- 测试总数: 20
- 成功: 12
- 失败: 8
- 成功率: 60.0%
- 平均分: 0.312
- 分数标准差: 0.461
- 最高分: 0.980
- 最低分: 0.000
- 平均执行时间: 23.11秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.376 |
| ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 40.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.372 |

---

### mbpp

#### 基本统计
- 测试总数: 20
- 成功: 0
- 失败: 20
- 成功率: 0.0%
- 平均分: 0.000
- 平均执行时间: 0.01秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |

---

### drop

#### 基本统计
- 测试总数: 20
- 成功: 0
- 失败: 20
- 成功率: 0.0%
- 平均分: 0.000
- 平均执行时间: 0.00秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 0.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 0.0% | 0.000 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 5
- 失败: 15
- 成功率: 25.0%
- 平均分: 0.376
- 分数标准差: 0.515
- 平均执行时间: 8.39秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 0.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.376 |
| mbpp | 5 | 0.0% | 0.000 |
| drop | 5 | 0.0% | 0.000 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 0
- 失败: 20
- 成功率: 0.0%
- 平均分: 0.000
- 平均执行时间: 0.01秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 0.0% | 0.000 |
| gsm8k | 5 | 0.0% | 0.000 |
| mbpp | 5 | 0.0% | 0.000 |
| drop | 5 | 0.0% | 0.000 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 2
- 失败: 18
- 成功率: 10.0%
- 平均分: 0.000
- 平均执行时间: 4.22秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 0.0% | 0.000 |
| gsm8k | 5 | 40.0% | 0.000 |
| mbpp | 5 | 0.0% | 0.000 |
| drop | 5 | 0.0% | 0.000 |

---

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 5
- 失败: 15
- 成功率: 25.0%
- 平均分: 0.372
- 分数标准差: 0.511
- 平均执行时间: 10.51秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 0.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.372 |
| mbpp | 5 | 0.0% | 0.000 |
| drop | 5 | 0.0% | 0.000 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | gsm8k | decompose_ensemble_generate_revise_summarize | 0.376 | 100.0% | 5 |
| 2 | gsm8k | decompose_ensemble_generate_programmer_revise_summarize | 0.372 | 100.0% | 5 |
| 3 | math500 | decompose_ensemble_generate_revise_summarize | 0.000 | 0.0% | 5 |
| 4 | math500 | ensemble_generate_revise_summarize | 0.000 | 0.0% | 5 |
| 5 | math500 | ensemble_generate_programmer_revise_summarize | 0.000 | 0.0% | 5 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | mbpp | decompose_ensemble_generate_programmer_revise_summarize | 0.000 | 0.0% | 5 |
| 2 | drop | decompose_ensemble_generate_revise_summarize | 0.000 | 0.0% | 5 |
| 3 | drop | ensemble_generate_revise_summarize | 0.000 | 0.0% | 5 |
| 4 | drop | ensemble_generate_programmer_revise_summarize | 0.000 | 0.0% | 5 |
| 5 | drop | decompose_ensemble_generate_programmer_revise_summarize | 0.000 | 0.0% | 5 |

---

## ❌ 错误分析

**总错误数**: 68

### 错误类型分布

| 错误类型 | 数量 | 占比 |
|---------|------|------|
| other | 68 | 100.0% |


## 📝 结论

基于以上分析，可以得出以下结论：

1. ❌ 整体成功率较低 (15.0%)，需要重点优化
2. ❌ 平均分数较低 (0.312)，需要改进workflow设计

---

*报告结束*