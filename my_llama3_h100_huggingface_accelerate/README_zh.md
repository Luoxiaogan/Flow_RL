# Llama3 H100 Hugging Face Accelerate 训练系统

从复杂的7+1卡架构迁移而来的简化训练系统，使用标准8卡Accelerate分布式训练。

## 🚀 项目概述

本项目提供了基于Hugging Face Accelerate的流水线化训练方案，具有以下特点：

- **架构简化**：标准8卡分布式训练，替代复杂的7+1卡设置
- **原地评估**：训练过程中的暂停-评估-恢复工作流
- **损失掩码**：可选功能，仅对助手回复计算损失
- **奖励服务器集成**：使用现有奖励基础设施进行自动评估
- **综合报告**：多种格式的详细评估报告

## 📁 项目结构

```
my_llama3_h100_huggingface_accelerate/
├── src/
│   ├── train.py                    # 主要的基于Accelerate的训练脚本
│   ├── data_utils.py              # 数据加载和处理工具
│   ├── data_collator.py           # 损失掩码数据整理器
│   └── evaluation/
│       ├── simple_evaluator.py    # 简化的原地评估器
│       ├── score_collector.py     # 奖励服务器接口（100%复用）
│       └── report_generator.py    # 报告生成器（100%复用）
├── configs/
│   ├── accelerate_config.yaml     # 8卡Accelerate配置
│   └── evaluation_config.yaml    # 简化的评估设置
├── logs/                          # 训练和评估日志
├── run_training.sh               # 主启动脚本
└── README_zh.md                  # 本文件
```

## 🛠️ 环境要求

- Python 3.8+
- 支持CUDA的PyTorch
- Hugging Face Accelerate
- Transformers
- Datasets
- wandb（可选，用于日志记录）

## ⚙️ 配置说明

### Accelerate配置 (`configs/accelerate_config.yaml`)
```yaml
compute_environment: LOCAL_MACHINE
distributed_type: MULTI_GPU
mixed_precision: bf16
num_processes: 8  # 8卡分布式训练
```

### 评估配置 (`configs/evaluation_config.yaml`)
关键设置：
- `schedule.interval`: 评估频率（默认：20步）
- `generation.max_new_tokens`: 最大生成token数（默认：1024）
- `reward_server`: 工作流解决方案评分配置

## 🚀 快速开始

### 1. 基础训练（无评估）
```bash
# 首先编辑run_training.sh中的路径
./run_training.sh
```

### 2. 带原地评估的训练
```bash
# 在脚本中启用评估
ENABLE_EVAL=true ./run_training.sh
```

### 3. 自定义配置
```bash
accelerate launch \
    --config_file configs/accelerate_config.yaml \
    src/train.py \
    --model_name_or_path /path/to/llama3-8b \
    --dataset_path /path/to/training.jsonl \
    --enable_inplace_eval true \
    --eval_interval 20 \
    --eval_test_data_path /path/to/test.jsonl \
    --output_dir ./outputs \
    --num_train_epochs 3 \
    --per_device_train_batch_size 2 \
    --learning_rate 2e-5
```

## 📊 评估功能

### 原地评估
- **暂停-评估-恢复**：在指定间隔暂停训练进行评估
- **当前模型权重**：使用最新的模型状态进行评估
- **批量处理**：可配置的评估批次大小
- **综合指标**：整体分数、成功率和基准特定结果

### 支持的数据格式
测试数据应为JSONL格式：
```json
{
    "data_source": "workflow_gsm8k",
    "prompt": [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "解决这个问题..."}
    ],
    "extra_info": {"test_cases": [1, 2, 3]},
    "reward_model": {"ground_truth": "expected_answer"}
}
```

### 报告生成
评估生成多种报告格式：
- **JSON**：机器可读的详细结果
- **Markdown**：人类可读的表格摘要
- **CSV**：用于分析的单个样本结果

## 🔄 从复杂系统的迁移

本项目简化了原始的7+1卡架构：

### 移除的内容 ❌
- 复杂的GPU设备管理（7个训练卡+1个推理卡）
- DeepSpeed ZeRO-3权重同步逻辑
- 手动GPU内存优化
- 复杂的回调系统

### 保留的功能 ✅
- 所有评估功能（score_collector、report_generator）
- SFT训练的损失掩码
- 奖励服务器集成
- 报告生成和指标跟踪
- 数据处理管道

### 收益 📈
- **代码复杂度减少70%**
- **稳定性提升** - 无GPU内存管理问题
- **标准模式** - 遵循Accelerate约定
- **调试更容易** - 清晰的训练流程
- **可维护性更好** - 社区支持的架构

## 🏗️ 架构详情

### 训练流程
1. **初始化**：使用Accelerate加载模型、分词器和数据集
2. **分布式**：自动在8个GPU上分布模型
3. **训练循环**：标准梯度累积和优化
4. **评估**：暂停训练，评估当前模型，恢复训练
5. **报告**：生成综合评估报告

### 评估过程
1. **模型准备**：将模型设为评估模式
2. **解决方案生成**：为测试样本生成工作流解决方案
3. **分数收集**：将解决方案发送到奖励服务器进行评分
4. **报告生成**：创建详细报告和日志指标
5. **训练恢复**：将模型返回到训练模式

### 内存管理
- **BF16混合精度**：H100原生支持的高效训练
- **梯度检查点**：可选的内存节约功能
- **自动缓存清理**：防止评估期间的OOM

## 📝 关键参数

### 训练参数
- `per_device_train_batch_size`: 每个GPU的批次大小（默认：2）
- `gradient_accumulation_steps`: 优化器更新前的步数（默认：2）
- `learning_rate`: AdamW学习率（默认：2e-5）
- `max_seq_length`: 最大序列长度（默认：4096）

### 评估参数
- `eval_interval`: 评估间隔步数（默认：20）
- `eval_batch_size`: 评估批次大小（默认：1）
- `max_eval_samples`: 最大测试样本数（测试时默认：5）

### 模型参数
- `model_type`: "llama" 或 "qwen"
- `use_flash_attention_2`: 启用Flash Attention（默认：true）
- `use_loss_mask`: 仅对助手token计算损失（默认：false）

## 🐛 故障排除

### 常见问题

1. **CUDA OOM**：减少批次大小或启用梯度检查点
2. **评估慢**：减少`max_eval_samples`或增加`eval_batch_size`
3. **奖励服务器连接**：检查评估配置中的服务器URL
4. **导入错误**：确保`PYTHONPATH`包含`src`目录

### 调试模式
```bash
# 启用调试日志
ACCELERATE_LOG_LEVEL=DEBUG ./run_training.sh

# 单独测试评估
python -c "
from src.evaluation.simple_evaluator import test_simple_evaluator
import asyncio
asyncio.run(test_simple_evaluator())
"
```

## 📊 监控

### W&B集成
设置Weights & Biases进行综合监控：
```bash
export WANDB_PROJECT="llama3-8b-accelerate-training"
export WANDB_API_KEY="your-api-key"
```

### 记录的指标
- 训练损失和学习率
- 评估分数和成功率
- GPU内存使用
- 训练速度（步数/秒）

## 🔧 高级用法

### 自定义数据整理器
用于特殊的损失掩码或数据格式：
```python
from src.data_collator import DataCollatorForChatML

collator = DataCollatorForChatML(
    tokenizer=tokenizer,
    model_type="llama",
    pad_to_multiple_of=8
)
```

### 自定义评估
用于特殊的评估逻辑：
```python
from src.evaluation.simple_evaluator import SimpleEvaluator

evaluator = SimpleEvaluator(eval_config)
solutions = await evaluator.evaluate_during_training(
    model, tokenizer, test_samples, batch_size=4
)
```

## 🤝 贡献

1. 遵循现有代码风格和模式
2. 添加适当的日志记录和错误处理
3. 为新功能更新文档
4. 在完整训练运行之前用小数据集测试

## 📄 许可证

本项目继承父级Flow_RL存储库的许可证。

## 🎯 使用建议

### 本地测试
1. 使用小数据集和少量样本进行快速测试
2. 设置`MAX_EVAL_SAMPLES=1`进行快速验证
3. 使用较短的训练轮数（如1轮）验证流程

### 服务器部署
1. 修改`run_training.sh`中的路径为服务器路径
2. 确保奖励服务器正在运行
3. 根据GPU内存调整批次大小
4. 设置适当的检查点保存间隔

### 性能优化
1. 使用Flash Attention 2以提高效率
2. 启用BF16混合精度训练
3. 根据数据长度调整`max_seq_length`
4. 使用梯度检查点节省内存（如果需要）