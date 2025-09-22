# ✅ CoT vs Self-Consistency 评估系统实现完成

## 系统已实现功能

### 1. 核心组件
- ✅ **workflow_templates.py**: 包含CoT和Self-consistency的固定workflow模板
- ✅ **test_workflows.py**: 主评估脚本，支持顺序测试多个benchmark
- ✅ **config.yaml**: 配置文件，可调整测试参数
- ✅ **test_connection.py**: 系统连接检查工具

### 2. 关键特性
- ✅ 自动从`ScoreFlow/benchmark_mapping.jsonl`加载正确的数据路径
- ✅ 支持随机采样（每个benchmark默认50个样本）
- ✅ 通过reward_server执行workflow并获取评估分数
- ✅ 生成详细的对比报告和结果保存

### 3. 数据集验证
已确认以下数据集可用：
- **GSM8K**: 1319个测试样本
- **MBPP**: 500个测试样本
- **HumanEval**: 164个测试样本

## 如何运行

### 步骤1: 启动Reward Server
```bash
# 在新的终端窗口
cd ../New_evaluation_and_RL/reward_server
python scoreflow_reward_server.py
```

### 步骤2: 运行评估
```bash
cd baseline
python test_workflows.py
```

## 系统工作流程

```
1. 加载配置和benchmark映射
   ↓
2. 对每个benchmark（gsm8k, mbpp, humaneval）：
   a. 从test.jsonl随机选择50个样本
   b. 发送CoT workflow到reward_server评估
   c. 发送Self-consistency workflow到reward_server评估
   d. 记录并对比两种方法的准确率
   ↓
3. 生成汇总报告
   - 各benchmark的详细结果
   - 平均性能对比
   - 改进百分比
```

## 预期输出示例

```
[1/3] GSM8K
  加载50个随机样本...
  测试 CoT workflow...
    CoT准确率: 70.0%
  测试 Self-consistency workflow...
    Self-consistency准确率: 76.0%
  提升: +6.0%

[2/3] MBPP
  加载50个随机样本...
  测试 CoT workflow...
    CoT准确率: 60.0%
  测试 Self-consistency workflow...
    Self-consistency准确率: 66.0%
  提升: +6.0%

[3/3] HumanEval
  加载50个随机样本...
  测试 CoT workflow...
    CoT准确率: 56.0%
  测试 Self-consistency workflow...
    Self-consistency准确率: 62.0%
  提升: +6.0%

总体统计:
平均CoT准确率: 62.0%
平均Self-consistency: 68.0%
平均提升: +6.0%
```

## 关键设计改进

1. **使用benchmark_mapping.jsonl**: 确保数据路径的正确性和一致性
2. **固定workflow模板**: 避免动态生成复杂代码，提高稳定性
3. **顺序执行**: 一次测试一个benchmark，便于监控和调试
4. **随机采样**: 每次运行使用不同样本，提高结果可靠性

## 配置调整建议

### 快速测试（减少样本数）
编辑 `config.yaml`:
```yaml
test:
  samples_per_benchmark: 10  # 快速测试用10个样本
```

### 增加超时时间
```yaml
reward_server:
  timeout: 600  # 增加到10分钟
```

## 系统状态

- ✅ 代码实现完成
- ✅ 数据路径验证通过
- ✅ 依赖模块检查通过
- ⏸️ 等待Reward Server启动后即可运行

## 总结

系统已完全实现并准备就绪。通过使用ScoreFlow的benchmark_mapping.jsonl，系统能够自动找到正确的数据文件路径，并通过reward_server评估两种workflow策略的性能差异。这个简洁的实现专注于核心功能，易于理解和维护。