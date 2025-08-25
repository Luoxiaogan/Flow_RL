# LLaMA3 H100 训练与评估系统

## 项目概述

本项目是一个完整的大语言模型训练与自动评估框架，专门为H100/L20Z GPU集群优化。系统集成了监督微调（SFT）、实时评估和工作流奖励计算功能。

### 主要特性

- **多模型支持**：支持LLaMA-3.1和Qwen-2.5系列模型
- **自动评估**：训练过程中自动评估模型性能
- **奖励服务器集成**：通过HTTP API与奖励服务器通信（端口8899）
- **分布式训练**：DeepSpeed ZeRO-3优化，支持8卡并行
- **Loss Masking**：可选的损失掩码功能，仅在助手回复上计算损失
- **实时监控**：WandB集成，实时跟踪训练指标

## 目录结构

```
my_llama3_h100_with_eval/
├── src/                          # 源代码
│   ├── training/                 # 训练相关模块
│   │   ├── trainer.py           # 主训练脚本
│   │   ├── data_collator.py     # 数据整理器（含Loss Masking）
│   │   └── utils.py             # 工具函数
│   └── evaluation/               # 评估相关模块
│       ├── evaluation_callback.py   # 训练回调
│       ├── model_evaluator.py       # 模型评估器
│       ├── score_collector.py       # 分数收集器（端口8899）
│       ├── reward_server_checker.py # 服务器检查
│       └── report_generator.py      # 报告生成器
├── configs/                      # 配置文件
│   ├── training/                 # 训练配置
│   │   ├── accelerate_config.yaml
│   │   └── deepspeed_z3.json
│   └── evaluation/               # 评估配置
│       └── eval_config.yaml
├── scripts/                      # 运行脚本
│   ├── run_finetune.sh          # 主训练脚本
│   ├── train_llama.sh           # LLaMA训练脚本
│   ├── train_qwen.sh            # Qwen训练脚本
│   └── train_with_eval.sh      # 带评估的训练脚本
├── tests/                        # 测试文件
│   ├── unit/                    # 单元测试
│   └── integration/             # 集成测试
│       └── test_evaluation_system.py
├── outputs/                      # 输出目录
│   ├── logs/                    # 训练日志
│   └── reports/                 # 评估报告
└── requirements.txt             # 依赖包
```

## 环境要求

### 硬件要求
- GPU: NVIDIA H100/L20Z (推荐) 或 A100
- 显存: 至少80GB (单卡)
- 内存: 256GB+
- 存储: 500GB+ SSD

### 软件要求
- Python 3.9+
- CUDA 11.8+
- PyTorch 2.0+
- Windows 10/11 或 Linux

## 安装指南

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/my_llama3_h100_with_eval.git
cd my_llama3_h100_with_eval
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
# 模型路径
MODEL_PATH=/path/to/models
OUTPUT_DIR=/path/to/output

# 奖励服务器（重要：端口8899）
REWARD_SERVER_URL=http://localhost:8899

# WandB (可选)
WANDB_PROJECT=llama3_training
WANDB_API_KEY=your_api_key

# Windows编码设置（重要）
PYTHONIOENCODING=utf-8
PYTHONLEGACYWINDOWSSTDIO=1
```

## 配置说明

### 训练配置 (configs/training/)

#### accelerate_config.yaml
```yaml
compute_environment: LOCAL_MACHINE
deepspeed_config:
  deepspeed_config_file: configs/training/deepspeed_z3.json
  zero3_init_flag: true
distributed_type: DEEPSPEED
num_processes: 8
```

#### deepspeed_z3.json
```json
{
  "bf16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 3,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "sub_group_size": 1e9,
    "reduce_bucket_size": "auto",
    "stage3_prefetch_bucket_size": "auto",
    "stage3_param_persistence_threshold": "auto",
    "stage3_max_live_parameters": 1e9,
    "stage3_max_reuse_distance": 1e9
  }
}
```

### 评估配置 (configs/evaluation/eval_config.yaml)

```yaml
evaluation:
  enabled: true
  test_data_path: "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
  reward_server_url: "http://localhost:8899"  # 奖励服务器端口
  eval_batch_size: 8
  eval_interval: 500  # 每500步评估一次
  max_samples: 100    # 最多评估100个样本
  output_dir: "outputs/reports"
  async_eval: true    # 异步评估，不阻塞训练
```

## 使用指南

### 1. 基础训练

```bash
# LLaMA-3.1-8B训练
bash scripts/train_llama.sh

# Qwen-2.5-7B训练
bash scripts/train_qwen.sh
```

### 2. 带Loss Masking的训练

```bash
# 启用Loss Masking（仅在助手回复上计算损失）
USE_LOSS_MASK_OVERRIDE=true bash scripts/train_llama.sh
```

### 3. 带自动评估的训练

```bash
# 步骤1：启动奖励服务器（端口8899）
cd ../New_evaluation_and_RL/reward_server
python scoreflow_reward_server.py

# 步骤2：确认服务器运行
curl http://localhost:8899/health

# 步骤3：运行训练
cd my_llama3_h100_with_eval
bash scripts/train_with_eval.sh
```

### 4. 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行集成测试（需要奖励服务器在8899端口运行）
python tests/integration/test_evaluation_system.py
```

## 数据格式

### 训练数据格式 (JSONL)

```json
{
  "messages": [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户问题"},
    {"role": "assistant", "content": "助手回答"}
  ]
}
```

### 评估数据格式

```json
{
  "data_source": "workflow_gsm8k",
  "prompt": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "extra_info": {
    "test_cases": [0, 1, 2],
    "data_path": "Processed_dataset/gsm8k/train.jsonl",
    "raw_data": 10
  },
  "reward_model": {
    "ground_truth": "default"
  }
}
```

## 评估系统

### 工作流程

1. **模型加载**：从checkpoint加载模型
2. **数据加载**：从JSONL文件读取测试数据
3. **工作流生成**：模型生成工作流代码
4. **奖励计算**：发送到8899端口的奖励服务器评分
5. **报告生成**：生成JSON/Markdown/CSV报告

### 奖励服务器API

#### 健康检查
```bash
GET http://localhost:8899/health
```

#### 计算分数
```bash
POST http://localhost:8899/compute_score
Content-Type: application/json

{
  "data_source": "workflow_gsm8k",
  "solution_str": "<code>...</code>",
  "ground_truth": "default",
  "extra_info": {
    "test_cases": [0, 1, 2],
    "data_path": "path/to/data.jsonl"
  }
}
```

### 评估报告示例

```markdown
# Evaluation Report - Checkpoint 5000

**时间**: 2024-12-25 12:00:00
**总体分数**: 85.3%
**成功率**: 92.0%

## 基准测试分数
- workflow_gsm8k: 87.5%
- workflow_mbpp: 83.1%
- workflow_drop: 85.2%
- workflow_hotpotqa: 84.7%
```

## Windows 特殊注意事项

### 1. 编码问题解决

```python
# 在Python脚本开头添加
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 2. 路径处理

```python
from pathlib import Path

# 使用Path对象处理跨平台路径
config_path = Path("configs") / "training" / "config.yaml"
```

### 3. 控制台输出

避免使用特殊Unicode字符，使用ASCII替代：
- 使用 `[OK]` 代替 `✓`
- 使用 `[FAIL]` 代替 `✗`
- 使用 `[INFO]` 代替 `ℹ`

### 4. 环境变量设置

```batch
:: Windows批处理脚本
@echo off
chcp 65001
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1
python your_script.py
```

## 常见问题

### Q1: Windows下中文乱码问题

**解决方案**：
1. 设置系统环境变量：
   ```batch
   setx PYTHONIOENCODING utf-8
   setx PYTHONLEGACYWINDOWSSTDIO 1
   ```
2. 在VSCode中设置：文件 > 首选项 > 设置 > 搜索 "encoding" > 设置为UTF-8
3. 保存文件时选择 "UTF-8 with BOM" 编码

### Q2: 奖励服务器连接失败（端口8899）

**解决方案**：
1. 确认服务器已启动：
   ```batch
   netstat -an | findstr 8899
   ```
2. 检查Windows防火墙：
   ```batch
   netsh advfirewall firewall add rule name="Reward Server" dir=in action=allow protocol=TCP localport=8899
   ```
3. 清除代理设置：
   ```batch
   set NO_PROXY=localhost,127.0.0.1
   set no_proxy=localhost,127.0.0.1
   ```

### Q3: 显存不足错误

**解决方案**：
1. 减小批量大小：
   ```bash
   --per_device_train_batch_size 2
   ```
2. 启用梯度累积：
   ```bash
   --gradient_accumulation_steps 8
   ```
3. 使用梯度检查点：
   ```bash
   --gradient_checkpointing
   ```

### Q4: DeepSpeed初始化失败

**解决方案**：
1. 确认所有GPU可用：
   ```batch
   nvidia-smi
   ```
2. 设置NCCL环境变量：
   ```batch
   set NCCL_DEBUG=INFO
   set NCCL_IB_DISABLE=1
   ```
3. 使用正确的启动命令：
   ```bash
   accelerate launch --config_file configs/training/accelerate_config.yaml src/training/trainer.py
   ```

## 性能优化建议

### 训练优化

1. **批量大小调整**
   - H100: batch_size=8, gradient_accumulation=2
   - A100: batch_size=4, gradient_accumulation=4
   - V100: batch_size=2, gradient_accumulation=8

2. **学习率设置**
   - LLaMA: 1e-5 到 2e-5
   - Qwen: 2e-5 到 5e-5

3. **序列长度**
   - 标准训练: 2048
   - 长文本: 4096或8192（需要更多显存）

### 评估优化

1. **异步评估**：使用 `async_eval=true` 避免阻塞训练
2. **批量评估**：增大 `eval_batch_size` 提高吞吐量
3. **采样策略**：使用 `max_samples` 限制评估样本数
4. **并发控制**：奖励服务器支持最多5个并发请求

## 监控与日志

### WandB集成

```python
# 自动记录的指标
- loss (训练损失)
- learning_rate (学习率)
- eval_score (评估分数)
- eval_success_rate (成功率)
- tokens_per_second (训练速度)
```

### 日志文件

- 训练日志：`outputs/logs/train_YYYYMMDD_HHMMSS.log`
- 评估报告：`outputs/reports/eval_checkpoint_STEP.json`
- 错误日志：`outputs/logs/error.log`

## 开发指南

### 添加新的评估指标

```python
# src/evaluation/custom_metric.py
class CustomMetric:
    def compute(self, predictions, references):
        # 实现你的指标计算
        score = calculate_score(predictions, references)
        return score
```

### 自定义数据处理

```python
# src/training/custom_collator.py
class CustomDataCollator:
    def __call__(self, features):
        # 实现自定义数据处理逻辑
        batch = process_features(features)
        return batch
```

### 扩展奖励服务器

```python
# 添加新的评分端点
@app.route('/custom_score', methods=['POST'])
def custom_score():
    data = request.json
    # 实现自定义评分逻辑
    score = compute_custom_score(data)
    return jsonify({'score': score})
```

## 故障排查

### 启用调试模式

```bash
# 设置日志级别
export TRANSFORMERS_VERBOSITY=debug
export ACCELERATE_LOG_LEVEL=debug

# Windows
set TRANSFORMERS_VERBOSITY=debug
set ACCELERATE_LOG_LEVEL=debug
```

### 检查系统状态

```python
# 运行诊断脚本
python scripts/diagnose.py

# 输出示例
System Diagnostics:
- Python: 3.9.16
- PyTorch: 2.0.1+cu118
- CUDA: 11.8
- GPUs: 8x NVIDIA H100
- Memory: 512GB
- Reward Server: Running on port 8899
```

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

### 提交规范

- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试相关
- chore: 构建/工具

### 代码规范

1. 使用Black格式化Python代码
2. 遵循PEP 8规范
3. 添加类型注解
4. 编写单元测试

## 联系方式

- 项目维护者：[Your Name]
- Email: your.email@example.com
- Issue追踪：[GitHub Issues](https://github.com/your-repo/issues)

## 致谢

- MetaGPT团队 - 工作流执行框架
- Hugging Face团队 - Transformers库
- Microsoft团队 - DeepSpeed优化
- OpenAI团队 - 评估基准
- 所有贡献者

## 更新日志

### v1.0.0 (2024-12-25)
- 初始版本发布
- 支持LLaMA-3.1和Qwen-2.5模型
- 集成奖励服务器（端口8899）
- 添加Loss Masking功能
- Windows兼容性优化

---

最后更新：2024-12-25