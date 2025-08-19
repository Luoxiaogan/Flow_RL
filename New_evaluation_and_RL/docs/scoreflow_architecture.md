# ScoreFlow 现有架构详解

## 1. 系统概述

ScoreFlow是一个用于生成训练数据和计算workflow执行分数的系统，主要用于强化学习（VERL）训练。系统分为两个主要部分：
- **数据生成器**：生成VERL格式的训练/测试数据
- **Reward服务器**：执行workflow并计算reward分数

## 2. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         New_evaluation_and_RL/                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      config.yaml                          │  │
│  │  - 统一配置文件                                           │  │
│  │  - 项目路径、服务配置、模型配置等                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           generate_parquet_and_jsonl/                     │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │     generate_verl_training_data.py               │    │  │
│  │  │  - VERL数据生成器主类                             │    │  │
│  │  │  - 加载benchmark handler                         │    │  │
│  │  │  - 构建HuggingFace chat格式prompt                │    │  │
│  │  │  - 生成train/test parquet文件                    │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    reward_server/                         │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │        scoreflow_reward_utils.py                 │    │  │
│  │  │  - ScoreFlowRewardCalculator类                    │    │  │
│  │  │  - workflow代码提取                               │    │  │
│  │  │  - MetaGPT执行环境管理                           │    │  │
│  │  │  - 并行执行+All-Reduce模式                       │    │  │
│  │  │  - WorkflowExecutionManager                      │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │       scoreflow_reward_server.py                 │    │  │
│  │  │  - Flask REST API服务器                          │    │  │
│  │  │  - /compute_score端点                            │    │  │
│  │  │  - /batch_compute端点                            │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

外部依赖：
┌──────────────────────────────────────────────────────────┐
│                     ScoreFlow/                            │
│  - benchmark_mapping.jsonl                                │
│  - scripts/{benchmark}/handler.py                         │
│  - scripts/{benchmark}/conditions.py                      │
│  - scripts/common/operator.py                             │
└──────────────────────────────────────────────────────────┘
```

## 3. 核心组件详解

### 3.1 配置管理 (config.yaml)

**关键特性**：
- 统一配置文件，所有组件共享
- 支持本地/服务器环境切换（只需修改project_root）
- 分层配置结构，清晰易维护

**主要配置项**：
```yaml
project_root: "D:/temp/Flow_RL"  # 项目根目录

services:
  metagpt_api_proxy:    # MetaGPT执行时的API代理
    port: 5009
    target_url: "API端点"
    
  scoreflow_reward:     # Reward服务配置
    port: 8899
    timeout: 300
    workspace: "workspace路径"

paths:
  scoreflow_handlers: "."  # ScoreFlow根目录
  benchmark_mapping: "映射文件路径"
  processed_dataset: "数据集路径"
```

### 3.2 数据生成器 (generate_verl_training_data.py)

**核心类**：`VerlTrainingDataGenerator`

**主要功能**：
1. **Benchmark Handler加载**
   - 动态加载不同benchmark的handler
   - 支持benchmark_mapping.jsonl映射
   - 智能路径解析（相对路径转Python模块路径）

2. **Prompt构建**
   - 加载conditions.py中的模板
   - 构建HuggingFace chat格式
   - 支持system/user消息格式

3. **数据生成流程**
   ```python
   # 1. 加载handler
   handler = self._get_benchmark_handler(benchmark_name, dataset_path)
   
   # 2. 构建prompt
   messages, problem_text = self._construct_prompt(handler, data_indices, benchmark_name)
   
   # 3. 生成VERL记录
   record = {
       'data_source': f"workflow_{benchmark_name}",
       'prompt': messages,  # HuggingFace chat格式
       'ability': 'workflow',
       'reward_model': {'ground_truth': 'default'},
       'extra_info': {
           'raw_data': idx,
           'test_cases': test_case_indices,
           'data_path': data_path
       }
   }
   ```

4. **输出格式**
   - Parquet格式（高效存储）
   - JSONL格式（人类可读）
   - 自动train/test分割

### 3.3 Reward计算器 (scoreflow_reward_utils.py)

**核心类**：`ScoreFlowRewardCalculator`

**关键创新**：

1. **WorkflowExecutionManager（工作流执行管理器）**
   - 独立日志管理（每个test case一个日志文件）
   - 并行执行+All-Reduce汇总模式
   - 避免I/O冲突的安全设计

2. **并行执行策略**
   ```python
   # 并行执行所有test cases
   tasks = []
   for test_case_index in self.test_cases:
       task = self._execute_single_test_case_isolated(
           calculator, workflow_code, test_case_index, dataset_path
       )
       tasks.append(task)
   
   # 并行执行
   results = await asyncio.gather(*tasks, return_exceptions=True)
   
   # All-Reduce汇总
   final_score = self._finalize_and_save_summary(total_duration)
   ```

3. **MetaGPT集成**
   - 动态加载operator模块
   - 构建执行环境
   - 支持超时控制
   - Handler judge方法验证结果

4. **日志管理机制**
   - IndividualTestCaseLogger：单个test case独立日志
   - SafeTeeOutput：安全的双向输出（终端+文件）
   - 结构化输出（CSV结果、JSON汇总）

### 3.4 REST API服务器 (scoreflow_reward_server.py)

**API端点**：

1. `/compute_score` - 单个workflow评分
   ```json
   请求: {
       "data_source": "gsm8k",
       "solution_str": "<workflow代码>",
       "ground_truth": "default",
       "extra_info": {
           "test_cases": [0, 1, 2],
           "data_path": "path/to/data.jsonl"
       }
   }
   响应: {
       "success": true,
       "score": 0.85
   }
   ```

2. `/batch_compute` - 批量评分
3. `/config` - 获取配置信息
4. `/health` - 健康检查

## 4. 执行流程

### 4.1 数据生成流程
```
1. 读取config.yaml配置
2. 加载benchmark_mapping.jsonl
3. 对每个benchmark：
   a. 加载对应的handler
   b. 读取数据集
   c. 生成prompt（HuggingFace格式）
   d. 创建VERL记录
4. 保存为parquet/jsonl格式
```

### 4.2 Reward计算流程
```
1. 接收workflow代码
2. 提取workflow类
3. 创建WorkflowExecutionManager
4. 并行执行test cases：
   a. 每个test case独立日志文件
   b. MetaGPT环境执行workflow
   c. Handler验证结果
5. All-Reduce汇总：
   a. 收集所有结果
   b. 计算平均分数
   c. 生成CSV/JSON报告
6. 返回最终分数
```

## 5. 关键特性

### 5.1 配置驱动
- 所有路径通过config.yaml配置
- 支持环境切换（本地/服务器）
- 服务配置集中管理

### 5.2 并行执行优化
- 信号量控制并发数
- asyncio.gather并行执行
- All-Reduce模式汇总结果

### 5.3 日志隔离
- 每个test case独立日志文件
- 避免并发I/O冲突
- 结构化输出（CSV+JSON）

### 5.4 错误处理
- 超时控制（workflow执行）
- 异常捕获和记录
- Debug模式支持

### 5.5 扩展性
- 动态加载handler
- 支持新benchmark添加
- 模块化设计

## 6. 文件输出结构

```
workspace/
└── {benchmark_name}/
    └── workflow_{timestamp}_{random_id}/
        ├── workflow.py              # workflow代码
        ├── metadata.json            # 元数据
        ├── test_case_0.log         # 独立执行日志
        ├── test_case_1.log
        ├── ...
        ├── results.csv             # 执行结果表格
        ├── summary.json            # 汇总统计
        └── global_execution.log   # 全局执行日志
```

## 7. 性能优化

1. **并行处理**：使用asyncio并发执行多个test cases
2. **内存优化**：Parquet格式高效存储
3. **I/O优化**：独立日志文件避免锁竞争
4. **缓存机制**：Handler缓存避免重复加载

## 8. 与旧版本对比

| 特性 | 旧版本 (Test_FILE) | 新版本 (New_evaluation_and_RL) |
|------|-------------------|--------------------------------|
| 配置 | config.json | config.yaml |
| 日志 | 单一日志文件 | 独立日志文件 |
| 执行 | 串行执行 | 并行+All-Reduce |
| 路径 | 硬编码 | 配置驱动 |
| 输出 | 简单JSON | 结构化CSV+JSON |