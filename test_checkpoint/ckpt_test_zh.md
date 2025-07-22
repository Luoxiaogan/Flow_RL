# 检查点测试系统

## 概述

检查点测试系统旨在通过测试微调后的语言模型生成和执行工作流的能力来评估模型性能。该系统使用vLLM服务检查点模型，并针对GSM8K和MBPP等已知基准测试生成的工作流。

## 架构

系统由四个主要组件组成：

1. **vLLM服务器 (`start_vllm_server.py`)**: 使用vLLM为检查点模型提供高效推理服务
2. **提示生成器 (`prompt_generator.py`)**: 构建提示并发送到vLLM服务器以生成工作流
3. **工作流测试器 (`workflow_tester.py`)**: 执行生成的工作流并根据真实答案验证结果
4. **主协调器 (`test_checkpoint.py`)**: 协调生成和测试流程
5. **Shell脚本 (`run_checkpoint_test.sh`)**: 提供运行完整流程的易用接口

## 系统流程

1. **服务器启动**: 使用指定的检查点启动vLLM服务器
2. **批处理**: 系统以批次方式处理工作流：
   - 创建基准问题的随机组合
   - 为每个组合生成多个工作流版本
   - 测试所有生成的工作流
3. **结果收集**: 保存详细的统计数据和日志

## 安装和设置

### 前置要求

- Python 3.8+
- 支持CUDA的GPU（默认：GPU 7）
- 已安装vLLM（`pip install vllm`）
- 必需的Python包：
  ```bash
  pip install aiohttp asyncio openai
  ```

### 目录结构

```
test_checkpoint/
├── start_vllm_server.py      # vLLM服务器启动脚本
├── prompt_generator.py       # 提示生成模块
├── workflow_tester.py        # 工作流测试模块
├── test_checkpoint.py        # 主协调脚本
├── run_checkpoint_test.sh    # 完整流程的Shell脚本
├── ScoreFlow/               # 从Test_FILE/ScoreFlow复制
├── config/                  # 从Test_FILE/config复制
└── checkpoint_test_results/ # 输出目录（运行时创建）
```

## 使用方法

### 快速开始

使用默认设置运行完整流程：

```bash
./run_checkpoint_test.sh /path/to/checkpoint gsm8k ../Processed_dataset/gsm8k.jsonl
```

### 详细使用

#### 1. 手动启动vLLM服务器

```bash
python start_vllm_server.py \
    --model-path /path/to/checkpoint \
    --port 8000 \
    --gpu-id 7 \
    --tensor-parallel-size 1 \
    --max-model-len 4096
```

#### 2. 手动运行测试

```bash
# 首先确保服务器正在运行，然后：
python test_checkpoint.py \
    --checkpoint-path /path/to/checkpoint \
    --benchmark gsm8k \
    --dataset-path ../Processed_dataset/gsm8k.jsonl \
    --server-url http://localhost:8000 \
    --exec-llm '{"provider": "openai", "model": "qwen2-72b-instruct", "api_key": "YOUR_KEY", "base_url": "https://api.siliconflow.cn/v1"}' \
    --num-batches 10 \
    --workflows-per-batch 15
```

### 配置参数

#### Shell脚本参数

1. `CHECKPOINT_PATH`: 模型检查点路径
2. `BENCHMARK`: 基准名称（gsm8k, mbpp）
3. `DATASET_PATH`: 数据集文件路径
4. `SERVER_PORT`: vLLM服务器端口（默认：8000）
5. `GPU_ID`: GPU设备ID（默认：7）
6. `TENSOR_PARALLEL_SIZE`: 张量并行的GPU数量（默认：1）
7. `MAX_MODEL_LEN`: 最大序列长度（默认：4096）

#### 测试参数（在shell脚本中）

- `NUM_BATCHES`: 要处理的批次数（默认：10）
- `WORKFLOWS_PER_BATCH`: 每批工作流数（默认：15）
- `PROBLEMS_PER_WORKFLOW`: 每个工作流的平均问题数（默认：3）
- `PARALLELISM`: 每个工作流组合的版本数（默认：2）

## 输出结构

```
checkpoint_test_results/
└── gsm8k_20240321_143052/
    ├── generated_workflows/
    │   ├── gsm8k_20240321_143052_1234.py
    │   ├── gsm8k_20240321_143052_1234.meta.json
    │   └── ...
    ├── test_results/
    │   └── test_results.csv
    └── test_summary.json
```

### 输出文件

- **工作流文件 (`.py`)**: 生成的工作流代码
- **元数据文件 (`.meta.json`)**: 工作流元数据，包括基准、问题索引
- **测试结果 (`test_results.csv`)**: 每个工作流的详细测试结果
- **测试摘要 (`test_summary.json`)**: 总体统计和性能指标

## 模块详情

### vLLM服务器模块

`start_vllm_server.py`脚本：
- 使用指定的检查点启动vLLM服务器
- 配置GPU分配和模型参数
- 提供健康检查端点以检测就绪状态

### 提示生成器模块

`prompt_generator.py`模块：
- 使用基准特定的模板构建提示
- 向vLLM服务器发送批量请求
- 通过参考工作流支持多样性
- 保存生成的工作流和元数据

关键方法：
- `construct_prompt()`: 从基准问题构建提示
- `send_to_server()`: 向vLLM服务器发送请求
- `generate_workflow_batch()`: 并行处理多个工作流

### 工作流测试器模块

`workflow_tester.py`模块：
- 加载生成的工作流和元数据
- 构建具有适当导入和环境的可执行脚本
- 使用超时保护执行工作流
- 使用基准特定的判断方法验证结果

关键方法：
- `build_executable_script()`: 创建包含工作流的可运行脚本
- `execute_workflow()`: 运行工作流并捕获输出
- `test_single_workflow()`: 一个工作流的完整测试流程

### 主协调器

`test_checkpoint.py`脚本：
- 管理完整的测试流程
- 创建随机问题批次
- 协调生成和测试阶段
- 收集和报告统计数据

## 基准支持

目前支持的基准：
- **GSM8K**: 小学数学问题
- **MBPP**: 基础Python编程问题

每个基准需要：
- 在`ScoreFlow/scripts/{benchmark}/handler.py`中实现处理器
- 在`ScoreFlow/scripts/{benchmark}/conditions.py`中定义条件模板
- 在`ScoreFlow/scripts/{benchmark}/operator.py`中定义操作符

## 性能考虑

1. **批处理**: 系统以批次方式处理工作流以优化吞吐量
2. **并行性**: 多个工作流并发生成和测试
3. **超时保护**: 每个工作流执行都有可配置的超时（默认：180秒）
4. **GPU利用**: vLLM服务器使用指定的GPU进行高效推理

## 故障排除

### 常见问题

1. **服务器无法启动**:
   - 使用`nvidia-smi`检查GPU可用性
   - 确保vLLM正确安装
   - 验证检查点路径存在

2. **生成失败**:
   - 检查服务器是否运行并可访问
   - 验证API端点URL
   - 检查服务器日志中的错误

3. **测试失败**:
   - 确保执行LLM配置有效
   - 检查MetaGPT依赖项
   - 查看日志中的工作流语法错误

### 调试模式

要进行详细调试，修改脚本以增加日志记录：
- 向Python脚本添加`--log-level DEBUG`
- 检查服务器日志以查找生成问题
- 查看单个工作流文件中的语法错误

## 未来改进

1. **RL训练集成**: 模块化设计便于与RL训练流程集成
2. **额外基准**: 支持HumanEval、HotpotQA、MATH、DROP
3. **分布式测试**: 多节点测试以进行更大规模的评估
4. **实时监控**: 用于跟踪测试进度的Web仪表板
5. **自适应采样**: 基于模型性能的智能问题选择

## API参考

### CheckpointTester类

```python
tester = CheckpointTester(
    checkpoint_path: str,
    benchmark: str,
    dataset_path: str,
    server_url: str,
    exec_llm_config: Dict[str, str],
    num_batches: int = 10,
    workflows_per_batch: int = 15,
    problems_per_workflow: int = 3,
    parallelism: int = 2,
    output_base_dir: str = "checkpoint_test_results"
)

await tester.run_full_test()
```

## 许可证

该系统是Flow_RL项目的一部分，遵循相同的许可条款。