# Qwen3-Thinking LoRA 训练项目（带实时监控）

## 📋 项目说明

这是一个独立的 **Qwen3-8B-Thinking** 模型 LoRA 微调项目，集成了训练过程实时监控功能。该项目基于 LLaMA-Factory 框架，添加了样本生成监控补丁，可以在训练过程中实时观察模型的思维链生成质量。

## 🌟 核心特性

1. **Qwen3 Thinking 模式支持**：专门针对思维链（Chain of Thought）优化
2. **训练实时监控**：每隔指定步数自动生成样本，观察训练效果
3. **独立运行**：包含所有必要的补丁文件和训练脚本
4. **生成历史保存**：自动记录所有生成样本，便于后续分析

## 📁 项目结构

```
llama_factory_qwen3_thinking_lora/
├── src/                              # LLaMA-Factory 补丁文件
│   └── llamafactory/
│       ├── hparams/
│       │   └── finetuning_args.py   # 新增样本生成参数
│       └── train/
│           ├── callbacks.py         # 样本生成回调实现
│           └── sft/
│               └── workflow.py      # SFT训练流程集成
├── examples/                         # 示例配置
│   └── train_lora/
│       └── llama3_lora_sft_with_generation.yaml
├── lora_simp_e.sh                   # 主训练脚本
├── 更改说明.md                       # 补丁详细说明
└── README_zh.md                      # 本文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活conda环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate workflow

# 安装 LLaMA-Factory（如果还没有安装）
pip install llamafactory
```

### 2. 应用补丁到 LLaMA-Factory

```bash
# 找到你的 LLaMA-Factory 安装位置
# 通常在: $(python -c "import site; print(site.getsitepackages()[0])")/llamafactory
# 或者你的本地克隆目录

LLAMA_FACTORY_DIR="/path/to/llamafactory"  # 替换为实际路径

# 应用补丁
cp src/llamafactory/hparams/finetuning_args.py $LLAMA_FACTORY_DIR/src/llamafactory/hparams/
cp src/llamafactory/train/callbacks.py $LLAMA_FACTORY_DIR/src/llamafactory/train/
cp src/llamafactory/train/sft/workflow.py $LLAMA_FACTORY_DIR/src/llamafactory/train/sft/
```

### 3. 准备数据

确保你有 `sft_data_simple` 数据集在 `data/` 目录下。数据格式应为：

```json
{
  "messages": [
    {"role": "system", "content": "系统提示..."},
    {"role": "user", "content": "用户问题..."},
    {"role": "assistant", "content": "<Thinking>\n思考过程...\n</Thinking>\n\n最终回答..."}
  ]
}
```

### 4. 运行训练

```bash
# 直接运行训练脚本
bash lora_simp_e.sh

# 或者自定义参数
bash lora_simp_e.sh --sample_generation_steps 50 --sample_generation_num 3
```

## ⚙️ 关键参数说明

### 训练参数

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `model_name_or_path` | Qwen/Qwen3-8B | 基础模型 |
| `finetuning_type` | lora | 使用LoRA微调 |
| `lora_rank` | 8 | LoRA秩 |
| `cutoff_len` | 6500 | 支持长思维链 |
| `enable_thinking` | True | 启用思维模式 |
| `per_device_train_batch_size` | 4 | 每GPU批大小 |
| `gradient_accumulation_steps` | 4 | 梯度累积 |
| `learning_rate` | 5e-5 | 学习率 |

### 监控参数

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `sample_generation_steps` | 2 | 每2步生成一次（建议改为100） |
| `sample_generation_num` | 2 | 每次生成2个样本 |
| `sample_generation_max_tokens` | 4096 | 支持完整思维链 |
| `sample_generation_temperature` | 1.0 | 生成温度 |
| `save_generation_samples` | true | 保存生成历史 |

## 📊 输出示例

训练过程中会看到类似输出：

```
============================================================
Generating samples at step 100
============================================================

Sample 1/2:
Input: <|im_start|>user
请解释量子计算的基本原理<|im_end|>
<|im_start|>assistant
<Thinking>

Output: <Thinking>
量子计算是一个复杂的主题，让我分步骤解释：

1. 经典比特 vs 量子比特
   - 经典计算机使用比特，只能是0或1
   - 量子计算机使用量子比特（qubit），可以同时处于0和1的叠加态

2. 量子叠加原理
   - 这是量子计算的核心概念
   - 一个量子比特可以同时表示多个状态
   - n个量子比特可以同时表示2^n个状态

3. 量子纠缠
   - 多个量子比特可以相互关联
   - 测量一个会立即影响其他纠缠的量子比特
   
4. 量子算法的优势
   - 可以并行处理大量可能性
   - 某些问题上具有指数级加速
</Thinking>

量子计算利用量子力学的特性来处理信息。与传统计算机使用确定的0或1不同，量子计算机使用量子比特，它可以同时处于多个状态的叠加...

Sample 2/2:
...

============================================================
```

## 🔧 自定义配置

### 调整监控频率

编辑 `lora_simp_e.sh`：

```bash
# 降低监控频率以减少训练干扰
--sample_generation_steps 500 \  # 每500步生成一次

# 或者增加监控频率以更密切观察
--sample_generation_steps 50 \   # 每50步生成一次
```

### 修改生成参数

```bash
# 更保守的生成（用于调试）
--sample_generation_temperature 0.3 \
--sample_generation_max_tokens 2048 \

# 更多样化的生成（用于评估）
--sample_generation_temperature 0.8 \
--sample_generation_num 5 \
```

## 📈 监控和分析

### 查看生成历史

生成的样本会保存在输出目录：

```bash
# 查看生成的文件
ls saves/Qwen3-8B-Thinking/lora/train_with_generation_*/generation_samples*.jsonl

# 实时查看最新生成
tail -f saves/Qwen3-8B-Thinking/lora/train_with_generation_*/generation_samples*.jsonl
```

### 分析生成质量

```python
import json
import pandas as pd

# 加载生成历史
with open('generation_samples.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

# 转换为DataFrame
df = pd.DataFrame(data)

# 分析思维链长度趋势
df['thinking_length'] = df['output'].apply(
    lambda x: len(x.split('<Thinking>')[1].split('</Thinking>')[0]) 
    if '<Thinking>' in x else 0
)

# 绘制质量趋势
df.plot(x='step', y='thinking_length')
```

## 🐛 故障排查

### 问题1：找不到 llamafactory-cli

```bash
# 确认安装
pip show llamafactory

# 或使用Python模块方式
python -m llamafactory.cli train ...
```

### 问题2：CUDA OOM 错误

```bash
# 减少批大小
--per_device_train_batch_size 2 \

# 或减少生成长度
--sample_generation_max_tokens 2048 \
```

### 问题3：生成功能不工作

检查：
1. 补丁是否正确应用
2. `sample_generation_steps` 不是 None
3. 查看训练日志中是否有 "SampleGenerationCallback enabled" 信息

## 💡 最佳实践

1. **开始训练时**：使用较小的 `sample_generation_steps`（如50）密切监控
2. **稳定训练后**：增加到 500-1000 减少开销
3. **思维链训练**：确保 `sample_generation_max_tokens` 足够大（>2048）
4. **调试时**：设置 `temperature=0.1` 观察最可能的输出
5. **评估时**：使用多个样本（`sample_generation_num=5`）获得更全面的评估

## 📚 相关文档

- [补丁详细说明](更改说明.md)
- [LLaMA-Factory 官方文档](https://github.com/hiyouga/LLaMA-Factory)
- [Sample Generation Patch 完整文档](../Documentation/sample_generation_patch_zh.md)

## 🤝 贡献

欢迎提交问题和改进建议！这个项目是 Flow_RL 项目的一部分，专注于提升模型的思维链生成能力。

## 📝 许可

遵循 Apache 2.0 许可证。