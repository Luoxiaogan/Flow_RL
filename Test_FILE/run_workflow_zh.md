# 工作流系统参数说明文档

本文档详细说明了工作流生成与执行系统中各个参数的含义和使用方法。

## 核心参数说明

### 1. TOTAL_PROBLEMS
- **含义**: 数据集中问题的总数
- **示例**: `TOTAL_PROBLEMS=8`
- **说明**: 表示从数据集中总共要使用8个问题。系统会从数据集中随机选择这些问题。

### 2. MIN_SAMPLE_SIZE 和 MAX_SAMPLE_SIZE
- **含义**: 每个工作流使用的问题样本数的范围
- **示例**: 
  - `MIN_SAMPLE_SIZE=2` # 每个工作流最少使用2个问题
  - `MAX_SAMPLE_SIZE=2` # 每个工作流最多使用2个问题
- **说明**: 
  - 当MIN和MAX相等时，每个工作流都会使用固定数量的问题
  - 当MIN < MAX时，系统会在这个范围内随机选择问题数量
  - 例如：如果设置为2-4，某些工作流可能使用2个问题，某些使用3个，某些使用4个

### 3. PARALLELISM
- **含义**: 每个数据组合生成的工作流版本数
- **示例**: `PARALLELISM=2`
- **说明**: 
  - 对于同一组问题，系统会生成2个不同版本的工作流
  - 第一个版本独立生成
  - 第二个版本会参考第一个版本，尝试使用不同的解决方案
  - 这有助于增加训练数据的多样性

### 4. MAX_CONCURRENT_GROUPS
- **含义**: 生成阶段最大并发组数
- **示例**: `MAX_CONCURRENT_GROUPS=4`
- **说明**: 
  - 控制同时并行生成的组数上限
  - 组间并行执行，组内串行执行
  - 这样设计是因为组内的第二个工作流需要参考第一个工作流

### 5. BATCH_SIZE
- **含义**: 每批次处理的任务组数
- **示例**: `BATCH_SIZE=$MAX_CONCURRENT_GROUPS`
- **说明**: 
  - 通常设置为与MAX_CONCURRENT_GROUPS相同
  - 表示master_runner.py每次会处理多少个任务组
  - 如果总任务组数超过BATCH_SIZE，会分多个批次处理

### 6. MAX_CONCURRENT_EXECUTIONS
- **含义**: 执行阶段并行验证工作流的最大并发数
- **示例**: `MAX_CONCURRENT_EXECUTIONS=5`
- **说明**: 
  - 在验证阶段，最多同时运行5个工作流
  - 这个参数独立于生成阶段的并发控制
  - 可以根据系统资源调整

## 参数关系和计算示例

假设配置如下：
```bash
TOTAL_PROBLEMS=8
MIN_SAMPLE_SIZE=2
MAX_SAMPLE_SIZE=2
PARALLELISM=2
MAX_CONCURRENT_GROUPS=4
BATCH_SIZE=4
```

### 执行流程：

1. **问题分组**：
   - 8个问题随机打乱
   - 每组2个问题（因为MIN=MAX=2）
   - 总共形成4个组：[问题1,问题2], [问题3,问题4], [问题5,问题6], [问题7,问题8]

2. **工作流生成**：
   - 每组生成2个工作流版本（PARALLELISM=2）
   - 总共生成：4组 × 2版本 = 8个工作流
   - 生成ID格式：`benchmark_组索引_版本索引`
     - gsm8k_0_0, gsm8k_0_1 (第1组的2个版本)
     - gsm8k_1_0, gsm8k_1_1 (第2组的2个版本)
     - gsm8k_2_0, gsm8k_2_1 (第3组的2个版本)
     - gsm8k_3_0, gsm8k_3_1 (第4组的2个版本)

3. **并发控制**：
   - 生成阶段：4个组可以同时开始生成（MAX_CONCURRENT_GROUPS=4）
   - 每组内部：先生成版本0，完成后再生成版本1（串行）
   - 验证阶段：最多5个工作流同时验证（MAX_CONCURRENT_EXECUTIONS=5）

## 性能优化建议

1. **MAX_CONCURRENT_GROUPS**：
   - 设置过高可能导致API限流
   - 建议根据API配额和系统资源设置
   - 通常3-5个是合理的值

2. **BATCH_SIZE**：
   - 建议与MAX_CONCURRENT_GROUPS保持一致
   - 这样可以充分利用并发能力

3. **MAX_CONCURRENT_EXECUTIONS**：
   - 执行阶段通常比生成阶段耗时更长
   - 可以适当提高此值以加快整体处理速度
   - 但要注意系统内存和CPU资源

## 实际应用示例

### 小规模测试
```bash
TOTAL_PROBLEMS=10
MIN_SAMPLE_SIZE=2
MAX_SAMPLE_SIZE=3
PARALLELISM=2
MAX_CONCURRENT_GROUPS=2
BATCH_SIZE=2
```
- 适合快速测试系统功能
- 生成约6-10个工作流

### 中等规模运行
```bash
TOTAL_PROBLEMS=100
MIN_SAMPLE_SIZE=2
MAX_SAMPLE_SIZE=4
PARALLELISM=2
MAX_CONCURRENT_GROUPS=5
BATCH_SIZE=5
```
- 适合日常训练数据生成
- 生成约50-100个工作流

### 大规模生产
```bash
TOTAL_PROBLEMS=1000
MIN_SAMPLE_SIZE=2
MAX_SAMPLE_SIZE=5
PARALLELISM=3
MAX_CONCURRENT_GROUPS=10
BATCH_SIZE=10
```
- 适合大规模数据集准备
- 生成约600-1500个工作流

## 注意事项

1. **API限流**：确保并发数不超过API提供商的限制
2. **内存占用**：每个工作流执行都会占用一定内存，注意系统资源
3. **错误处理**：系统会自动跳过失败的工作流，不影响其他任务
4. **数据一致性**：同一批次内的所有工作流使用相同的问题分组，确保可重现性

## 数据文件格式和匹配

系统会生成两个重要的数据文件：

### 1. training_data_gsm8k.jsonl
训练数据文件，每行包含一个JSON对象：
```json
{
  "workflow_id": "gsm8k_0_0",
  "benchmark": "gsm8k",
  "data_indices": [1, 3],
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### 2. execution_results.csv
执行结果文件，包含以下列：
- **ID**: 工作流ID（如 gsm8k_0_0）
- **Benchmark**: 基准测试名称
- **Data_Indices**: 使用的数据索引（如 1_3）
- **Status**: 执行状态（verified_correct/verified_incorrect/execution_failed）
- **Error_Type**: 错误类型（如果有）

### 数据匹配方式
- 通过 `workflow_id` 字段可以精确匹配训练数据和执行结果
- 即使由于并行执行导致文件中的顺序不同，也能通过ID准确匹配
- 后续可以根据执行状态筛选成功的工作流用于训练