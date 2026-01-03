# VERL格式工作流数据生成系统

这是一个专为VERL (Vectorized Environment for Reinforcement Learning) 设计的工作流数据生成系统，严格复用现有工作流生成与执行系统的核心逻辑。

## 🎯 系统目标

生成用于强化学习训练的VERL格式数据：
- **上游模型**: 根据prompt生成工作流代码
- **下游模型**: 执行生成的工作流
- **奖励函数**: 基于下游执行结果的准确率计算奖励

## 📁 文件结构

```
Test_FILE/verl_support/
├── README.md                    # 本说明文档
├── plan.md                      # 详细实施计划
├── config.json                  # 系统配置文件
├── utils.py                     # 工具函数 (复用现有系统组件)
├── generate_verl_data.py        # VERL数据生成器
├── workflow_reward.py           # 工作流奖励函数
├── test_verl_system.py          # 系统测试脚本
├── math.py                      # 数学评估函数 (参考)
└── data/                        # 生成的数据文件
    ├── gsm8k_verl_train.parquet    # GSM8K训练集
    ├── gsm8k_verl_test.parquet     # GSM8K测试集
    ├── mbpp_verl_train.parquet     # MBPP训练集
    └── mbpp_verl_test.parquet      # MBPP测试集
```

## 🚀 快速开始

### 1. 环境准备

确保已安装依赖：
```bash
pip install pandas pyarrow asyncio
```

### 2. 配置设置

编辑 `config.json` 配置文件：
- 设置数据集路径
- 配置API密钥
- 调整生成参数

### 3. 数据生成

生成所有benchmark的VERL数据：
```bash
cd Test_FILE/verl_support
python generate_verl_data.py
```

或生成指定benchmark：
```bash
python generate_verl_data.py --benchmark gsm8k
```

### 4. 系统测试

运行完整测试：
```bash
python test_verl_system.py
```

## 📊 VERL数据格式

生成的训练数据包含以下字段：

```json
{
    "data_source": "gsm8k",
    "prompt": "<|system|>\nYou are...<|user|>\n...<|end|>",
    "ability": "math_reasoning", 
    "reward_model": {
        "ground_truth": [1, 5, 8]
    },
    "extra_info": {
        "sample_id": 0,
        "num_problems": 3,
        "problem_indices": [1, 5, 8],
        "raw_problem_text": "..."
    }
}
```

## 🎁 奖励函数使用

### 简化接口 (推荐)

```python
from workflow_reward import compute_score

# 计算单个工作流的奖励
workflow_code = "class Workflow: ..."
score = compute_score(workflow_code, "gsm8k")
print(f"奖励分数: {score:.3f}")
```

### 批量计算

```python
from workflow_reward import batch_compute_rewards
import asyncio

workflow_codes = ["code1", "code2", "code3"]
scores = asyncio.run(batch_compute_rewards(workflow_codes, "gsm8k"))
```

### 高级用法

```python
from workflow_reward import WorkflowRewardCalculator
from utils import load_config

config = load_config()
calculator = WorkflowRewardCalculator(config)

# 自定义测试索引
test_indices = [10, 20, 30]
reward = asyncio.run(calculator.compute_workflow_reward(
    workflow_code, test_indices, "gsm8k"
))
```

## 🔧 核心特性

### ✅ 严格复用现有系统

- **数据生成**: 100%复用 `workflow_generator.py` 的逻辑
- **工作流执行**: 100%复用 `workflow_executor.py` 的逻辑  
- **批次调度**: 100%复用 `master_runner.py` 的机制

### ✅ 训练/测试集分离

- 训练集用于VERL强化学习训练
- 测试集用于奖励计算
- 保证完全不重叠

### ✅ 标准化接口

- 参考 `math.py` 提供简化接口
- 支持批量处理
- 异步执行优化

## 📈 配置参数

### Benchmark配置

```json
"benchmarks": {
    "gsm8k": {
        "ability": "math_reasoning",
        "dataset_path": "./data/gsm8k/train.jsonl",
        "total_problems": 7473,
        "train_ratio": 0.8
    }
}
```

### 生成配置

```json
"generation_config": {
    "min_sample_size": 2,
    "max_sample_size": 4,
    "batch_size": 10
}
```

### VERL配置

```json
"verl_config": {
    "train_samples_per_benchmark": 100,
    "test_samples_per_benchmark": 25
}
```

## 🧪 测试与验证

系统包含完整的测试套件：

1. **文件结构检查**: 验证所有必需文件存在
2. **数据生成测试**: 验证VERL数据格式正确
3. **奖励计算测试**: 验证奖励函数正常工作
4. **简化API测试**: 验证接口易用性

## ⚠️ 重要约束

### 必须复用的组件

- `get_benchmark_handler()` - Handler加载
- `_construct_generation_prompt()` - Prompt构建
- `execute_and_verify()` - 工作流执行
- `handler.judge()` - 结果验证

### 必须保持的格式

- 文件结构: `.py` + `.meta.json`
- CSV结果格式
- Handler接口
- API配置格式

## 🔍 故障排除

### 常见问题

1. **导入错误**: 确保ScoreFlow路径正确
2. **数据集路径**: 检查config.json中的路径设置
3. **API配置**: 验证API密钥和base_url
4. **权限问题**: 确保有写入data目录的权限

### 调试模式

启用详细日志：
```bash
python generate_verl_data.py --log-level DEBUG
```

## 📚 相关文档

- `plan.md`: 详细的实施计划和设计理念
- 现有工作流系统: `master_runner.py`, `workflow_generator.py`, `workflow_executor.py`
- V2版本文档: `V2版本.md`

## 🤝 贡献

本系统严格遵循现有工作流系统的架构和接口，确保最大兼容性和一致性。任何修改都应该优先考虑复用现有组件。 