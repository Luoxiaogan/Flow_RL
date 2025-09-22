# 快速开始指南

## 系统概述

本系统评估两种Workflow策略的性能：
- **CoT (Chain-of-Thought)**: 链式思考，引导模型逐步推理
- **Self-Consistency**: 自一致性，生成多个解决方案并选择最佳

## 前置要求

1. **启动 Reward Server** (必须)
   ```bash
   # 在新终端窗口
   cd New_evaluation_and_RL/reward_server
   python scoreflow_reward_server.py --port 7788
   ```
   注意：服务器现在运行在端口 7788

2. **确认数据文件存在**
   - `Processed_dataset/gsm8k/test.jsonl`
   - `Processed_dataset/mbpp/test.jsonl`
   - `Processed_dataset/human_eval/test.jsonl`

## 运行评估

```bash
# 进入baseline目录
cd D:/temp/Flow_RL/baseline

# 运行评估（确保reward_server已启动）
python test_workflows.py
```

## 文件说明

- `workflow_templates.py` - CoT和Self-consistency的workflow实现
- `test_workflows.py` - 主测试脚本
- `config.yaml` - 配置文件（可调整样本数量）
- `results/` - 结果保存目录

## 配置调整

编辑 `config.yaml` 可以调整：
```yaml
test:
  samples_per_benchmark: 50  # 减少到10-20可加快测试
```

## 预期输出

系统会顺序测试三个benchmark，输出类似：
```
[1/3] GSM8K
  CoT准确率: 70.0%
  Self-Consistency准确率: 76.0%
  提升: +6.0%

[2/3] MBPP
  CoT准确率: 60.0%
  Self-Consistency准确率: 66.0%
  提升: +6.0%

[3/3] HumanEval
  CoT准确率: 56.0%
  Self-Consistency准确率: 62.0%
  提升: +6.0%
```

## 快速测试

使用较少样本进行快速验证：
```bash
python quick_test.py
```
这将只测试GSM8K的5个样本，用于快速验证系统是否正常工作。

## 故障排除

1. **Reward Server连接失败**
   - 确认服务运行在 http://localhost:7788 (注意端口是7788)
   - 检查端口是否被占用

2. **文件找不到**
   - 检查 `Processed_dataset/` 目录位置
   - 确认test.jsonl文件存在

3. **超时错误**
   - 减少样本数量（修改config.yaml）
   - 增加timeout设置