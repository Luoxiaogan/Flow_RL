# 📊 Workflow评估完整报告

**生成时间**: 2025-09-24 18:33:53

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

- **总测试数**: 40
- **成功数**: 40
- **失败数**: 0
- **成功率**: 100.0%
- **平均分数**: 0.305
- **分数标准差**: 0.312
- **最高分**: 0.880
- **最低分**: 0.000

### ⚡ 执行性能

- **平均执行时间**: 178.15秒
- **总执行时间**: 7125.99秒

### 📈 覆盖范围

- **Data Sources数量**: 2
- **Operators组合数**: 4


---

## 📁 按Data Source分类统计

### humaneval

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.305
- 分数标准差: 0.374
- 最高分: 0.880
- 最低分: 0.000
- 平均执行时间: 171.03秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.788 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.432 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |

---

### mbpp

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.305
- 分数标准差: 0.245
- 最高分: 0.720
- 最低分: 0.000
- 平均执行时间: 185.27秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.420 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.396 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.176 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.228 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 10
- 成功: 10
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.210
- 分数标准差: 0.290
- 平均执行时间: 106.11秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| humaneval | 5 | 100.0% | 0.000 |
| mbpp | 5 | 100.0% | 0.420 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 10
- 成功: 10
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.592
- 分数标准差: 0.269
- 平均执行时间: 215.08秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| humaneval | 5 | 100.0% | 0.788 |
| mbpp | 5 | 100.0% | 0.396 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 10
- 成功: 10
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.304
- 分数标准差: 0.302
- 平均执行时间: 173.98秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| humaneval | 5 | 100.0% | 0.432 |
| mbpp | 5 | 100.0% | 0.176 |

---

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 10
- 成功: 10
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.114
- 分数标准差: 0.182
- 平均执行时间: 217.43秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| humaneval | 5 | 100.0% | 0.000 |
| mbpp | 5 | 100.0% | 0.228 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | humaneval | ensemble_generate_revise_summarize | 0.788 | 100.0% | 5 |
| 2 | humaneval | ensemble_generate_programmer_revise_summarize | 0.432 | 100.0% | 5 |
| 3 | mbpp | decompose_ensemble_generate_revise_summarize | 0.420 | 100.0% | 5 |
| 4 | mbpp | ensemble_generate_revise_summarize | 0.396 | 100.0% | 5 |
| 5 | mbpp | decompose_ensemble_generate_programmer_revise_summarize | 0.228 | 100.0% | 5 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | mbpp | ensemble_generate_revise_summarize | 0.396 | 100.0% | 5 |
| 2 | mbpp | decompose_ensemble_generate_programmer_revise_summarize | 0.228 | 100.0% | 5 |
| 3 | mbpp | ensemble_generate_programmer_revise_summarize | 0.176 | 100.0% | 5 |
| 4 | humaneval | decompose_ensemble_generate_revise_summarize | 0.000 | 100.0% | 5 |
| 5 | humaneval | decompose_ensemble_generate_programmer_revise_summarize | 0.000 | 100.0% | 5 |

---

## 📝 结论

基于以上分析，可以得出以下结论：

1. ✅ 整体成功率较高 (100.0%)，表明workflow执行稳定
2. ❌ 平均分数较低 (0.305)，需要改进workflow设计

---

*报告结束*