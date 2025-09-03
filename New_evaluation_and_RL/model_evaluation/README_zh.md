# 模型评估模块

一个全面的批量模型评估系统，用于测试多个模型在workflow生成任务上的表现并生成对比报告。

## 🌟 功能特点

- **批量评估**：在同一数据集上测试多个模型
- **异步处理**：高效的并发评估与内存管理
- **全面报告**：支持JSON、Markdown、CSV格式，包含对比图表
- **灵活配置**：基于YAML的配置，支持参数覆盖
- **错误处理**：优雅处理模型失败情况
- **内存管理**：模型间自动清理GPU缓存

## 🚀 快速开始

### 1. 前置条件

```bash
# 激活conda环境
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow

# 启动reward服务器（必需）
bash ../servers_and_proxy/start_scoreflow_reward.sh
```

### 2. 基本使用

```bash
# 使用默认配置运行
bash evaluate_models.sh

# 快速测试（10个样本）
bash evaluate_models.sh -n 10 -y

# 使用自定义配置
bash evaluate_models.sh -c example_config.yaml
```

### 3. Python API

```python
import asyncio
from model_evaluation import BatchModelEvaluator

# 配置
config = {
    'test_data_path': 'test_data.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'output_dir': 'evaluation_reports',
    'eval_batch_size': 8,
    'max_samples': 100
}

# 模型列表
models = [
    {'name': 'Model-1', 'path': 'path/to/model1'},
    {'name': 'Model-2', 'path': 'path/to/model2'}
]

# 运行评估
evaluator = BatchModelEvaluator(config)
results = asyncio.run(evaluator.evaluate_models(models))
```

## ⚙️ 配置说明

### 主配置文件

编辑 `evaluation_config.yaml`：

```yaml
test_data:
  path: "path/to/test_data.jsonl"
  max_samples: null  # null表示使用所有样本

reward_server:
  url: "http://localhost:8899"

evaluation:
  batch_size: 8
  output_dir: "./evaluation_reports"
  generation_params:
    max_new_tokens: 4096
    temperature: 0.7
    top_p: 0.9

models:
  - name: "模型名称"
    path: "模型路径"
    type: "huggingface"  # 或 "checkpoint", "local"
    generation_params:  # 可选的参数覆盖
      temperature: 0.8
```

### 模型类型

- **huggingface**：来自HuggingFace Hub的模型
- **checkpoint**：本地微调的检查点
- **local**：本地模型目录

## 📁 输出结构

```
evaluation_reports/
├── model_*.json            # 单个模型报告
├── model_*.md              # Markdown格式报告
├── model_comparison.json   # 对比数据
├── model_comparison.md     # 对比报告
├── detailed_results.csv    # 详细CSV数据
├── charts/
│   ├── overall_scores.png  # 分数对比图
│   └── benchmark_heatmap.png # 性能热力图
└── evaluation_*.log        # 执行日志
```

## 📊 报告内容

### 单个模型报告
- 总体分数和成功率
- 每个基准测试的性能指标
- 统计分析（平均值、最大值、最小值、标准差）
- 详细的错误追踪

### 对比报告
- 按总体分数的模型排名
- 特定基准测试的对比
- 最佳/最差模型识别
- 便于对比的可视化图表

## 🔧 命令行选项

```bash
run_evaluation.py [选项]

选项:
  --config, -c 文件      配置文件（默认：evaluation_config.yaml）
  --test-data, -t 文件   测试数据文件（覆盖配置）
  --max-samples, -n N    最大评估样本数
  --output-dir, -o 目录  输出目录
  --batch-size, -b N     批处理大小
  --log-level, -l 级别   日志级别（DEBUG/INFO/WARNING/ERROR）
  --yes, -y              跳过确认提示
```

## 🎯 高级用法

### 自定义测试数据

创建JSONL格式的测试数据：

```json
{"data_source": "workflow_gsm8k", "prompt": [...], "reward_model": {...}}
{"data_source": "workflow_mbpp", "prompt": [...], "reward_model": {...}}
```

### 添加新模型

1. 编辑 `evaluation_config.yaml`
2. 添加模型配置：
   ```yaml
   - name: "我的自定义模型"
     path: "/path/to/model"
     type: "checkpoint"
     generation_params:
       temperature: 0.75
   ```
3. 运行评估

## 🔍 故障排查

### 常见问题

1. **Reward服务器未运行**
   ```bash
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   ```

2. **内存不足**
   - 在配置中减小batch_size
   - 使用--max-samples处理更少的样本
   - 模型在评估后会自动清理

3. **找不到测试数据**
   - 首先生成测试数据：
     ```bash
     cd ../generate_parquet_and_jsonl
     python generate_verl_training_data.py
     ```

4. **模型加载错误**
   - 验证模型路径存在
   - 检查CUDA/PyTorch兼容性
   - 确保足够的GPU内存

## 🔄 与训练集成

此模块与训练管道集成：

1. 使用SFT/RL训练模型
2. 从基准测试生成测试数据
3. 评估训练的检查点
4. 与基准模型对比
5. 选择最佳模型

## ⚡ 性能提示

- 使用较小的max_samples进行快速测试
- 根据GPU内存调整batch_size
- 仅在需要时生成图表
- 使用example_config.yaml进行测试

## 💡 使用示例

### 示例1：评估微调模型

```yaml
# fine_tuned_eval.yaml
models:
  - name: "基础模型"
    path: "Qwen/Qwen2.5-7B-Instruct"
  - name: "微调-1000步"
    path: "./checkpoints/checkpoint-1000"
  - name: "微调-5000步"
    path: "./checkpoints/checkpoint-5000"
```

```bash
bash evaluate_models.sh -c fine_tuned_eval.yaml
```

### 示例2：快速对比测试

```bash
# 仅使用10个样本快速对比
bash evaluate_models.sh -n 10 -o quick_test/ -y
```

### 示例3：生产环境评估

```bash
# 完整评估，所有样本
bash evaluate_models.sh -c production_config.yaml -o production_results/
```

## 📝 注意事项

1. **服务依赖**：必须先启动Reward服务器
2. **路径配置**：确保测试数据路径正确
3. **GPU资源**：评估大模型需要足够的GPU内存
4. **并发限制**：默认并发数为8，可根据服务器性能调整
5. **结果保存**：所有结果自动保存，支持断点续传

## 🛠️ 开发指南

### 扩展新功能

1. 继承 `ModelEvaluator` 类实现自定义评估器
2. 扩展 `ReportGenerator` 添加新的报告格式
3. 修改 `ScoreCollector` 支持新的评分方式

### 贡献代码

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

作为Flow_RL项目的一部分。请参见主项目LICENSE文件。