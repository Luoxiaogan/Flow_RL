# 🎯 最简化Workflow设计说明

## 设计理念
极简主义 - 用最少的代码和最简单的提示词实现核心功能对比

## Workflow对比

### 1. CoT (Chain-of-Thought) - 极简版

**提示词**: `"Solve step by step."`

**执行逻辑**:
```python
instruction = "Solve step by step."
answer = await self.generate(instruction, "")
return answer
```

**特点**:
- 只用一个Generate调用
- 4个单词的提示词
- 引导模型逐步思考但不强制格式

### 2. Self-Consistency - 极简版

**提示词**: `"Solve this problem."` (运行3次)

**执行逻辑**:
```python
# 相同提示词运行3次
simple_instruction = "Solve this problem."
solution1 = await self.generate(simple_instruction, "")
solution2 = await self.generate(simple_instruction, "")
solution3 = await self.generate(simple_instruction, "")

# Ensemble选择
ensemble_instruction = "Select the best answer."
final_answer = await self.ensemble(ensemble_instruction, solutions)
```

**特点**:
- 使用完全相同的提示词3次
- 通过随机性产生不同答案
- Ensemble用最简指令选择

## 对比要点

| 方面 | CoT | Self-Consistency |
|------|-----|-----------------|
| Generate调用次数 | 1 | 3 |
| Ensemble调用 | 0 | 1 |
| 提示词复杂度 | 极简 (4词) | 极简 (3词) |
| 策略差异 | 引导逐步思考 | 多次采样+投票 |

## 预期效果

### CoT预期
- 通过"step by step"引导更结构化的推理
- 可能产生更详细的中间步骤
- 单次调用，速度快

### Self-Consistency预期
- 通过3次独立生成增加可靠性
- Ensemble可以过滤掉偶然错误
- 消耗更多token但可能更稳定

## 测试价值

这个极简设计能够：
1. **纯粹对比**: 排除复杂提示词的干扰，纯粹比较两种策略
2. **快速执行**: 最少的token消耗，最快的执行速度
3. **易于理解**: 代码极简，一目了然
4. **基准测试**: 作为更复杂workflow的性能基准

## 使用建议

```bash
# 测试单个样例（最快）
python minimal_test.py

# 测试5个样例（快速验证）
python quick_test.py

# 完整测试（统计显著性）
python test_workflows.py
```

## 注意事项

1. **提示词影响**: 极简提示词可能降低绝对准确率，但不影响相对比较
2. **随机性**: Self-consistency依赖模型的随机性产生不同答案
3. **Ensemble质量**: 极简的ensemble指令可能影响最终选择质量

## 总结

这个最简化设计专注于测试CoT vs Self-consistency的**核心差异**：
- CoT: 通过提示引导思考过程
- Self-consistency: 通过多次采样提高可靠性

去除所有复杂性后，我们可以更清楚地看到这两种策略的本质区别。