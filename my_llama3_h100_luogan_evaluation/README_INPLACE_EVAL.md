# SFT训练原地评估系统

## 概述

本项目实现了一个**原地评估（In-Place Evaluation）**系统，能够在SFT（Supervised Fine-Tuning）训练过程中，直接使用当前分布式GPU上的模型权重进行评估，无需频繁保存和加载checkpoint。

### 核心特性

- 🚀 **原地评估**：直接使用训练中的模型权重，避免checkpoint I/O开销
- 🎯 **分布式支持**：兼容DeepSpeed ZeRO-3分片模型
- 🔄 **实时反馈**：每N步自动评估，实时监控训练效果
- 📊 **Workflow评分**：通过Reward Server执行和评分生成的workflow代码
- 🛠️ **灵活配置**：支持自定义评估间隔、批次大小等参数

## 快速开始

### 1. 环境准备

```bash
# 激活conda环境
conda activate verl

# 确保在正确的目录
cd /Users/luogan/Code/workflow_generation/Flow_RL/my_llama3_h100_luogan_evaluation
```

### 2. 启动Reward Server

```bash
# 在另一个终端启动Reward Server
cd ../New_evaluation_and_RL/reward_server
python scoreflow_reward_server.py --port 8897
```

### 3. 开始训练

```bash
# 训练Llama模型
bash run_finetune_with_inplace_eval.sh

# 或训练Qwen模型（修改脚本中的MODEL_TYPE）
MODEL_TYPE="qwen" bash run_finetune_with_inplace_eval.sh
```

## 系统架构

### 数据流程

```
训练步骤 → 触发评估 → 读取test.jsonl → 应用chat_template 
    ↓
生成workflow → 提取代码 → 发送到Reward Server → 获取分数
    ↓
生成报告 → 保存结果 → 继续训练
```

### 关键组件

1. **InPlaceEvaluationCallback** (`src/evaluation/inplace_evaluation_callback.py`)
   - 训练回调，管理评估触发和流程

2. **InPlaceModelEvaluator** (`src/evaluation/inplace_model_evaluator.py`)
   - 使用当前模型权重生成workflow解决方案

3. **ScoreCollector** (`src/evaluation/score_collector.py`)
   - 与Reward Server通信，获取评估分数

4. **ReportGenerator** (`src/evaluation/report_generator.py`)
   - 生成评估报告（JSON和Markdown格式）

## 配置说明

### 主要配置文件

- **run_finetune_with_inplace_eval.sh**：训练启动脚本
- **configs/evaluation_config.yaml**：评估参数配置
- **accelerate_config.yaml**：Accelerate/DeepSpeed配置

### 关键参数

```bash
# 原地评估配置
ENABLE_INPLACE_EVAL=true  # 启用原地评估
EVAL_INTERVAL=50          # 每50步评估一次
EVAL_BATCH_SIZE=4         # 评估批次大小
MAX_EVAL_SAMPLES=20       # 最大评估样本数（测试用）

# Reward Server配置
CONFIG_FILE="/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/config.yaml"
# 从config.yaml自动读取端口（默认8897）
```

## 常见问题解答

### Q1: 评估时是重新加载checkpoint还是使用分布式权重？

**A**: 使用当前分布式GPU上的权重，不需要保存和重新加载checkpoint。这是"原地评估"的核心优势。

### Q2: Reward Server的URL从哪里读取？

**A**: 从硬编码路径 `/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/config.yaml` 读取。具体端口配置在 `services.scoreflow_reward.port` 字段。

### Q3: 评估使用哪个API端点？

**A**: 使用 `http://localhost:8897/compute_score` 端点。请求格式：
```json
{
    "data_source": "workflow_mbpp",
    "solution_str": "<生成的workflow代码>",
    "ground_truth": "default",
    "extra_info": {...}
}
```

### Q4: test.jsonl中的prompt字段是什么格式？

**A**: 是一个messages数组，包含system和user角色：
```json
"prompt": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]
```

### Q5: 为什么apply_chat_template时设置tokenize=False？

**A**: 这是两步处理策略：
1. 第一步：apply_chat_template只做格式转换（messages → 格式化字符串）
2. 第二步：批量tokenization，确保padding策略一致，提高效率

### Q6: generation_config.json会被使用吗？

**A**: 会。系统首先尝试加载模型的generation_config.json，然后覆盖某些参数（如temperature=0.7）以保证评估一致性。

### Q7: 如何从生成的文本中提取workflow代码？

**A**: 系统支持多种格式：
1. Markdown代码块：````python...````（已禁用，避免误提取）
2. HTML标签：`<code>...</code>`
3. 纯文本：如果没有代码块标记，整个响应视为workflow

### Q8: 评估会阻塞训练吗？

**A**: 是的，评估会短暂暂停训练。这是原地评估的设计特点，确保使用的是"此时此刻"的精确模型权重。评估时间通常很短，对整体训练影响较小。

## 文件结构

```
my_llama3_h100_luogan_evaluation/
├── run_finetune_with_inplace_eval.sh   # 主启动脚本
├── test_config_reading.py              # 配置测试工具
├── compare_chat_templates.py           # Chat template对比工具
├── accelerate_config.yaml              # Accelerate配置
├── configs/
│   ├── deepspeed_config_z3.json       # DeepSpeed ZeRO-3配置
│   └── evaluation_config.yaml         # 评估配置
└── src/
    ├── train.py                        # 训练主脚本
    ├── data_collator.py                # 数据整理器
    ├── utils.py                        # 工具函数
    └── evaluation/                     # 评估模块
        ├── __init__.py
        ├── inplace_evaluation_callback.py   # 评估回调
        ├── inplace_model_evaluator.py       # 模型评估器
        ├── score_collector.py               # 分数收集器
        ├── report_generator.py              # 报告生成器
        └── reward_server_checker.py         # 服务器检查器
```

## 技术细节

### DeepSpeed ZeRO-3集成

- 模型在8个GPU上分片
- 评估时直接使用分片权重
- 无需gather到单个GPU

### Chat Template处理

```python
# 自动检测并应用正确的格式
if isinstance(sample['prompt'], list):
    # messages数组格式，应用chat template
    prompt = tokenizer.apply_chat_template(
        sample['prompt'],
        tokenize=False,
        add_generation_prompt=True
    )
```

### 评估触发机制

```python
# 在训练回调中
def on_step_end(self, ...):
    if state.global_step % self.eval_interval == 0:
        # 触发评估
        self._run_evaluation_sync(model, tokenizer, ...)
```

## 调试工具

### 测试配置读取

```bash
python test_config_reading.py
```

### 比较Chat Template输出

```bash
python compare_chat_templates.py
```

## 注意事项

1. **Reward Server必须运行**：评估前确保Reward Server在端口8897运行
2. **测试数据格式**：test.jsonl必须是prompt-only格式（无assistant回复）
3. **GPU内存**：原地评估会占用额外GPU内存，建议减小评估批次大小
4. **评估间隔**：生产环境建议设置更大的间隔（如500步）

## 性能优化

- 使用`torch.no_grad()`减少内存使用
- 定期清理GPU缓存
- 批量处理提高效率
- 异步请求Reward Server

## 未来改进

- [ ] 支持多个benchmark同时评估
- [ ] 添加早停机制
- [ ] 支持保存最佳模型
- [ ] 添加TensorBoard集成
- [ ] 支持自定义评估指标

## 联系方式

如有问题，请联系项目维护者或查看主项目文档。