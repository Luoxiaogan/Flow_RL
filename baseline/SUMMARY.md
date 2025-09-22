# CoT vs Self-Consistency 评估系统总结

## 系统架构

```
baseline/
├── workflow_templates.py     # Workflow模板定义
├── test_workflows.py         # 主评估脚本
├── config.yaml              # 配置文件
├── test_connection.py       # 系统检查工具
├── results/                 # 评估结果目录
├── README.md               # 使用文档
├── QUICK_START.md          # 快速开始指南
└── SUMMARY.md              # 本文档
```

## 核心实现

### 1. Workflow模板 (`workflow_templates.py`)

**CoT Workflow**:
- 使用Generate算子引导step-by-step思考
- 通过Refiner改进解决方案
- FormatAnswer格式化最终答案

**Self-Consistency Workflow**:
- 生成3个不同角度的解决方案
- 使用Ensemble选择最佳答案
- FormatAnswer格式化输出

### 2. 评估流程 (`test_workflows.py`)

1. **随机采样**: 从每个benchmark的test.jsonl随机选择50个样本
2. **Workflow执行**: 将workflow代码发送到reward_server
3. **分数收集**: reward_server通过MetaGPT执行并返回准确率
4. **结果对比**: 计算两种方法的性能差异

### 3. 与Reward Server交互

```python
请求格式:
{
    "data_source": "gsm8k",
    "solution_str": workflow_code,
    "ground_truth": "default",
    "extra_info": {
        "test_cases": [0, 1, 2, ...],
        "data_path": "path/to/test.jsonl"
    }
}

响应格式:
{
    "success": true,
    "score": 0.75,  # 准确率
    "message": "..."
}
```

## 测试的Benchmarks

1. **GSM8K**: 数学推理问题
2. **MBPP**: Python编程基础题
3. **HumanEval**: Python函数实现

## 关键设计决策

### 为什么使用固定的Workflow模板？
- 避免动态生成复杂workflow代码
- 确保评估的一致性和可重复性
- 简化系统实现和调试

### 为什么通过Reward Server评估？
- 利用现有的MetaGPT执行框架
- 确保与ScoreFlow系统的兼容性
- 复用已验证的评估逻辑

### 为什么随机采样？
- 提高评估的统计可靠性
- 避免对特定样本的过拟合
- 每次运行都能获得不同视角

## 预期结果

基于理论和实践经验：
- Self-Consistency通常比CoT提升3-6%的准确率
- 在数学推理任务(GSM8K)上提升最明显
- 代码生成任务也能获得稳定提升

## 使用建议

1. **快速测试**: 将samples_per_benchmark设置为10-20
2. **完整评估**: 使用默认的50个样本
3. **深度分析**: 查看results/目录中的详细JSON文件

## 扩展可能

- 添加更多benchmark支持
- 实现其他workflow策略（如Tree-of-Thoughts）
- 增加统计分析功能（如置信区间）
- 支持并行benchmark测试

## 总结

这个系统提供了一个简洁而有效的方式来比较CoT和Self-Consistency两种重要的推理策略。通过固定的workflow模板和reward_server的执行能力，我们能够在多个benchmark上获得可靠的性能对比数据。