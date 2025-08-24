# Token费用惩罚系统使用指南

## 概述

Token费用惩罚系统基于实际API调用费用对workflow执行进行奖励调整，鼓励高效的prompt设计和资源利用。

## 快速开始

### 1. 启用Token惩罚

在 `config.yaml` 中配置：

```yaml
services:
  scoreflow_reward:
    token_penalty:
      enabled: true  # 启用token惩罚
      
      # API价格配置（每百万token的价格，美元）
      pricing:
        input_price_per_million: 0.5    # 输入token价格
        output_price_per_million: 1.5   # 输出token价格
      
      # 惩罚策略
      penalty_strategy:
        mode: "linear"           # 惩罚模式
        penalty_rate: 0.1        # 惩罚率
        max_penalty: 0.3         # 最大惩罚
```

### 2. 禁用Token惩罚

```yaml
token_penalty:
  enabled: false  # 关闭token惩罚
```

## 配置参数说明

### pricing（价格配置）

- **input_price_per_million**: 每百万输入token的价格（美元）
- **output_price_per_million**: 每百万输出token的价格（美元）

常见模型参考价格：
- Qwen-turbo: 输入$0.5/M, 输出$1.5/M
- GPT-3.5: 输入$0.5/M, 输出$1.5/M  
- GPT-4: 输入$10/M, 输出$30/M

### penalty_strategy（惩罚策略）

- **mode**: 惩罚计算模式
  - `linear`: 线性惩罚（费用 × penalty_rate）
  - `square`: 平方惩罚（费用² × penalty_rate）
  - `exponential`: 指数惩罚（(e^费用 - 1) × penalty_rate）

- **penalty_rate**: 惩罚系数
  - 建议范围：0.01 - 1.0
  - 越高惩罚越严格

- **max_penalty**: 最大惩罚限制
  - 建议范围：0.1 - 0.5
  - 防止过度惩罚

## 计算公式

1. **费用计算**
   ```
   输入费用 = (输入tokens / 1,000,000) × input_price_per_million
   输出费用 = (输出tokens / 1,000,000) × output_price_per_million
   总费用 = 输入费用 + 输出费用
   ```

2. **惩罚计算**
   - Linear: `惩罚 = 总费用 × penalty_rate`
   - Square: `惩罚 = 总费用² × penalty_rate`
   - Exponential: `惩罚 = (e^总费用 - 1) × penalty_rate`

3. **最终分数**
   ```
   最终分数 = 基础分数 × (1 - min(惩罚, max_penalty))
   ```

## 配置示例

### 开发环境（宽松）
```yaml
token_penalty:
  enabled: true
  pricing:
    input_price_per_million: 0.5
    output_price_per_million: 1.5
  penalty_strategy:
    mode: "linear"
    penalty_rate: 0.05    # 每$1扣5%
    max_penalty: 0.2      # 最多扣20%
```

### 测试环境（平衡）
```yaml
token_penalty:
  enabled: true
  pricing:
    input_price_per_million: 0.5
    output_price_per_million: 1.5
  penalty_strategy:
    mode: "square"
    penalty_rate: 0.05    # 平方惩罚
    max_penalty: 0.3      # 最多扣30%
```

### 生产环境（严格）
```yaml
token_penalty:
  enabled: true
  pricing:
    input_price_per_million: 0.5
    output_price_per_million: 1.5
  penalty_strategy:
    mode: "linear"
    penalty_rate: 0.2     # 每$1扣20%
    max_penalty: 0.5      # 最多扣50%
```

## 实际案例

假设workflow执行使用了2000个输入tokens和1500个输出tokens：

```
输入费用 = 2000 / 1,000,000 × 0.5 = $0.001
输出费用 = 1500 / 1,000,000 × 1.5 = $0.00225
总费用 = $0.00325
```

不同配置下的结果：

| 配置 | 模式 | penalty_rate | 惩罚值 | 基础分数0.8时的最终分数 |
|------|------|--------------|--------|------------------------|
| 宽松 | linear | 0.05 | 0.000163 | 0.7999 |
| 平衡 | square | 0.05 | 0.0000005 | 0.8000 |
| 严格 | linear | 0.2 | 0.00065 | 0.7995 |

## 监控和调试

系统会自动打印token使用和惩罚信息：

```
📊 Token统计 - Workflow: exec_gsm8k_0_20241224_abc123
  输入Token: 1,234
  输出Token: 567
  总计Token: 1,801

💰 Token费用惩罚计算:
  输入Tokens: 1,234
  输出Tokens: 567
  输入费用: $0.000617
  输出费用: $0.000851
  总费用: $0.001468
  基础分数: 1.000
  惩罚值: 0.000
  最终分数: 1.000
```

## 注意事项

1. **价格更新**：定期更新API价格配置以反映实际成本
2. **模式选择**：
   - linear适合大多数场景
   - square对高费用惩罚更严
   - exponential极其严格，谨慎使用
3. **penalty_rate调整**：先从小值开始，逐步调整
4. **监控效果**：定期查看日志，确保惩罚合理

## 故障排查

- **惩罚过重**：降低penalty_rate或提高max_penalty
- **Token统计为0**：检查MetaGPT配置，确保calc_usage=True
- **费用计算异常**：验证价格配置是否正确

## 版本记录

- v1.0.0 (2024-12-24): 初始版本，支持基于费用的token惩罚