# LLaMA3/Qwen2.5 H100训练系统（含自动评估）

## 概述

本目录包含用于H100/L20Z GPU的LLaMA-3.1-8B和Qwen-2.5-7B模型生产级训练配置，集成了训练过程中的自动评估功能。系统会在训练期间自动使用ScoreFlow奖励服务器评估模型检查点，实时跟踪性能提升。

## 核心功能

### 主要特性

- **多模型支持**：支持LLaMA-3.1-8B-Instruct和Qwen-2.5-7B-Instruct模型
- **自动评估**：训练期间使用ScoreFlow奖励服务器自动评估检查点
- **损失掩码**：可选功能，仅在助手响应上计算损失以提高训练质量
- **分布式训练**：跨8个GPU的DeepSpeed ZeRO-3优化
- **实时监控**：训练过程中跟踪模型在基准测试上的表现
- **异步评估**：非阻塞评估，不会中断训练

### 评估系统

集成的评估系统提供：

1. **检查点监控**：自动检测并评估新检查点
2. **奖励服务器集成**：与ScoreFlow奖励服务器接口进行评分
3. **基准测试**：在GSM8K、MBPP、HumanEval等基准上评估
4. **性能报告**：生成详细的JSON和Markdown报告
5. **趋势分析**：跟踪训练步骤中的性能指标

## 快速开始

### 环境准备

```bash
# 激活训练环境
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow

# 安装依赖
pip install -r requirements.txt
```

### 带评估的基础训练

```bash
# 进入目录
cd my_llama3_h100_with_eval/

# 运行带自动评估的训练
bash scripts/train_with_eval.sh

# 或运行不带评估的训练
bash scripts/train.sh
```

### 配置选项

编辑训练脚本进行自定义：

```bash
# 模型选择
MODEL_TYPE="llama"  # 或 "qwen"

# 评估设置
ENABLE_AUTO_EVAL=true   # 启用/禁用评估
EVAL_INTERVAL=1         # 每N个检查点评估一次
EVAL_BATCH_SIZE=4       # 评估批次大小
MAX_EVAL_SAMPLES=50     # 限制测试样本数
```

## 目录结构

```
my_llama3_h100_with_eval/
├── configs/                    # 配置文件
│   ├── evaluation/            # 评估配置
│   │   └── eval_config.yaml
│   └── training/              # 训练配置
│       ├── accelerate_config.yaml
│       └── deepspeed_z3.json
├── docs/                      # 文档
│   ├── evaluation.md         # 评估系统设计
│   └── guides/               # 设置指南
├── scripts/                   # 训练脚本
│   ├── train_with_eval.sh   # 带评估的训练
│   ├── train.sh              # 基础训练
│   └── utils/                # 工具脚本
├── src/                       # 源代码
│   ├── evaluation/           # 评估模块
│   │   ├── evaluation_callback.py
│   │   ├── model_evaluator.py
│   │   └── score_collector.py
│   └── training/             # 训练模块
│       ├── data_collator.py
│       └── trainer.py
├── tests/                     # 测试套件
│   ├── benchmarks/           # 基准测试
│   ├── integration/          # 集成测试
│   └── unit/                 # 单元测试
└── outputs/                   # 训练输出
    ├── checkpoints/          # 模型检查点
    ├── logs/                 # 训练日志
    └── reports/              # 评估报告
```

## 训练配置

### 硬件要求

- **GPU**：8x NVIDIA L20Z（每个80GB）或H100
- **总GPU内存**：640GB
- **CPU内存**：建议256GB
- **存储**：检查点和数据需要2TB+

### 训练参数

#### LLaMA-3.1-8B
```yaml
批次大小: 每设备4
梯度累积: 4步
全局批次大小: 128
学习率: 1e-5
最大序列长度: 4096
精度: bfloat16
```

#### Qwen-2.5-7B
```yaml
批次大小: 每设备4
梯度累积: 4步
全局批次大小: 128
学习率: 2e-5
最大序列长度: 8192
精度: bfloat16
```

### DeepSpeed配置

系统使用DeepSpeed ZeRO-3进行高效分布式训练：

- **Stage 3优化**：跨GPU的完整模型分片
- **BF16精度**：原生H100支持
- **无CPU卸载**：GPU内存充足
- **梯度检查点**：内存优化

## 评估系统

### 工作原理

1. **检查点检测**：监控训练中的新检查点
2. **模型加载**：加载检查点进行评估
3. **测试数据处理**：为测试问题生成解决方案
4. **奖励服务器评分**：将解决方案发送到ScoreFlow服务器
5. **报告生成**：创建性能报告

### 评估流程

```
训练 → 保存检查点 → 评估回调 → 加载模型 → 生成解决方案 → 奖励服务器评分 → 生成报告 → 继续训练
```

### 报告格式

评估报告包括：

- 总体准确率分数
- 每个基准的性能
- 成功/失败率
- 性能趋势
- 详细错误分析

报告结构示例：
```json
{
  "checkpoint": "checkpoint-1000",
  "timestamp": "2024-01-15T10:30:00",
  "overall_score": 0.75,
  "benchmark_scores": {
    "gsm8k": 0.82,
    "mbpp": 0.68
  }
}
```

## 损失掩码

损失掩码通过仅在助手响应上计算损失来改进训练：

### 启用损失掩码

```bash
# 在训练脚本中
USE_LOSS_MASK=true

# 或通过环境变量
USE_LOSS_MASK_OVERRIDE=true bash scripts/train_with_eval.sh
```

### 优势

- 更好的泛化能力
- 专注于实际输出的学习
- 防止在提示上过拟合
- 改善下游性能

## 测试

### 运行测试

```bash
# 单元测试
python -m pytest tests/unit/

# 集成测试
python -m pytest tests/integration/

# 基准测试
python -m pytest tests/benchmarks/

# 测试评估系统
python tests/integration/test_evaluation_system.py
```

### 测试损失掩码

```bash
python tests/unit/test_loss_mask.py
```

## 监控

### 训练指标

使用以下工具监控训练进度：

- **WandB**：实时指标仪表板
- **TensorBoard**：本地可视化
- **日志文件**：详细训练日志
- **评估报告**：性能跟踪

### 关键指标

- 训练损失
- 评估准确率
- 基准分数
- Token统计
- GPU利用率

## 故障排除

### 常见问题

1. **GPU内存溢出错误**
   - 减少批次大小
   - 启用梯度检查点
   - 减少评估批次大小

2. **奖励服务器连接失败**
   - 检查服务器是否运行：`curl http://localhost:8899/health`
   - 验证网络连接
   - 检查防火墙设置

3. **评估速度慢**
   - 减少MAX_EVAL_SAMPLES进行测试
   - 启用ASYNC_EVAL
   - 增加EVAL_INTERVAL

4. **DeepSpeed错误**
   - 验证CUDA和PyTorch版本
   - 检查DeepSpeed配置
   - 确保所有GPU可用

### 调试模式

启用调试日志：

```bash
export TORCH_DISTRIBUTED_DEBUG=DETAIL
export CUDA_LAUNCH_BLOCKING=1
bash scripts/train_with_eval.sh
```

## 高级用法

### 自定义评估数据

```bash
# 指定自定义测试数据
EVAL_TEST_DATA="path/to/custom_test.jsonl"
bash scripts/train_with_eval.sh
```

### 分布式训练

```bash
# 多节点训练
deepspeed --num_nodes=2 \
          --hostfile=hostfile \
          src/train.py --config configs/training/config.yaml
```

### 恢复训练

```bash
# 从检查点恢复
python src/train.py \
  --resume_from_checkpoint outputs/checkpoints/checkpoint-5000 \
  --enable_auto_eval true
```

## 性能优化

### 训练速度

- 使用Flash Attention 2加速注意力机制
- 在H100上启用BF16精度
- 优化批次大小以适应GPU内存
- 合理使用梯度累积

### 评估速度

- 批量评估请求
- 使用异步评估
- 在评估之间缓存模型
- 开发期间限制评估样本

## 最佳实践

1. **从小开始**：先用有限样本测试
2. **监控内存**：关注GPU内存使用
3. **定期检查点**：频繁保存
4. **版本控制**：跟踪配置更改
5. **备份数据**：保留训练数据备份

## 贡献指南

贡献时请：

1. 为新功能编写测试
2. 更新文档
3. 遵循代码风格指南
4. 先在小数据集上测试
5. 创建详细的拉取请求

## 许可证

本项目是Flow_RL系统的一部分。请参阅主仓库了解许可证详情。

## 支持

如有问题或疑问：

1. 查看`docs/`中的文档
2. 查看`tests/`中的测试示例
3. 参考CLAUDE.md了解AI辅助指南
4. 提交包含详细信息的issue

## 相关文档

- [评估系统设计](docs/evaluation.md)
- [H100设置指南](docs/guides/h100_setup.md)
- [损失掩码指南](docs/guides/loss_masking.md)
- [主项目README](../README.md)