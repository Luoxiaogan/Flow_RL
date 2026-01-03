# 📊 Workflow评估完整报告

**生成时间**: 2025-09-25 16:48:08

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
- **成功数**: 80
- **失败数**: 0
- **成功率**: 100.0%
- **平均分数**: 0.208
- **分数标准差**: 0.368
- **最高分**: 0.980
- **最低分**: 0.000

### ⚡ 执行性能

- **平均执行时间**: 175.90秒
- **总执行时间**: 14072.37秒

### 📈 覆盖范围

- **Data Sources数量**: 4
- **Operators组合数**: 4


---

## 📁 按Data Source分类统计

### math500

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 239.43秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |

---

### gsm8k

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.831
- 分数标准差: 0.128
- 最高分: 0.980
- 最低分: 0.500
- 平均执行时间: 179.71秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.764 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.888 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.900 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.772 |

---

### mbpp

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 95.85秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |

---

### drop

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.000
- 平均执行时间: 188.62秒

#### Operators组合表现

| Operators组合 | 测试数 | 成功率 | 平均分 |
|-------------|--------|--------|--------|
| decompose_ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_revise_summarize | 5 | 100.0% | 0.000 |
| ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |
| decompose_ensemble_generate_programmer_revise_summarize | 5 | 100.0% | 0.000 |

---


---

## 🔧 按Operators组合分类统计

### decompose_ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.191
- 分数标准差: 0.349
- 平均执行时间: 151.95秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 100.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.764 |
| mbpp | 5 | 100.0% | 0.000 |
| drop | 5 | 100.0% | 0.000 |

---

### ensemble_generate_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.222
- 分数标准差: 0.395
- 平均执行时间: 227.68秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 100.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.888 |
| mbpp | 5 | 100.0% | 0.000 |
| drop | 5 | 100.0% | 0.000 |

---

### ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.225
- 分数标准差: 0.401
- 平均执行时间: 161.96秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 100.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.900 |
| mbpp | 5 | 100.0% | 0.000 |
| drop | 5 | 100.0% | 0.000 |

---

### decompose_ensemble_generate_programmer_revise_summarize

#### 基本统计
- 测试总数: 20
- 成功: 20
- 失败: 0
- 成功率: 100.0%
- 平均分: 0.193
- 分数标准差: 0.349
- 平均执行时间: 162.03秒

#### 在不同Data Source上的表现

| Data Source | 测试数 | 成功率 | 平均分 |
|------------|--------|--------|--------|
| math500 | 5 | 100.0% | 0.000 |
| gsm8k | 5 | 100.0% | 0.772 |
| mbpp | 5 | 100.0% | 0.000 |
| drop | 5 | 100.0% | 0.000 |

---


---

## 🏆 最佳表现组合

### Top 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | gsm8k | ensemble_generate_programmer_revise_summarize | 0.900 | 100.0% | 5 |
| 2 | gsm8k | ensemble_generate_revise_summarize | 0.888 | 100.0% | 5 |
| 3 | gsm8k | decompose_ensemble_generate_programmer_revise_summarize | 0.772 | 100.0% | 5 |
| 4 | gsm8k | decompose_ensemble_generate_revise_summarize | 0.764 | 100.0% | 5 |
| 5 | math500 | decompose_ensemble_generate_revise_summarize | 0.000 | 100.0% | 5 |


### Bottom 5 (按平均分)

| 排名 | Data Source | Operators | 平均分 | 成功率 | 测试数 |
|------|------------|-----------|--------|--------|--------|
| 1 | mbpp | decompose_ensemble_generate_programmer_revise_summarize | 0.000 | 100.0% | 5 |
| 2 | drop | decompose_ensemble_generate_revise_summarize | 0.000 | 100.0% | 5 |
| 3 | drop | ensemble_generate_revise_summarize | 0.000 | 100.0% | 5 |
| 4 | drop | ensemble_generate_programmer_revise_summarize | 0.000 | 100.0% | 5 |
| 5 | drop | decompose_ensemble_generate_programmer_revise_summarize | 0.000 | 100.0% | 5 |

---

## 📝 结论

基于以上分析，可以得出以下结论：

1. ✅ 整体成功率较高 (100.0%)，表明workflow执行稳定
2. ❌ 平均分数较低 (0.208)，需要改进workflow设计

---

*报告结束*