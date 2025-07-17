# Workflow测试脚本使用说明

## 概述

本项目将workflow测试分为两个独立的脚本：
1. **数据集生成**：从internbootcamp任务中提取描述并生成多任务测试数据集
2. **Workflow执行**：使用LLM生成system_prompt并测试下游模型解答能力

## 脚本文件说明

### 核心脚本
- `generate_dataset.py`: 数据集生成脚本，生成多任务JSONL数据集
- `execute_workflow.py`: Workflow执行脚本，执行LLM测试和验证

### 其他文件  
- `workflow_script.py`: 原始的完整版脚本（已废弃）
- `simple_workflow.py`: 原始的简化版脚本（已废弃）
- `plan.md`: 需求说明文档

## 支持的任务类型

当前支持4种不同类型的任务：

| 任务名称 | 任务类型 | 描述 |
|---------|---------|------|
| aalmostarithmeticalprogression | sequence_analysis | 几乎算术级数子序列分析 |
| game24 | arithmetic_puzzle | 24点算术谜题 |
| cipher | cryptography | 凯撒密码解密 |
| sudoku | logic_puzzle | 数独行填充 |

## 运行步骤

### 1. 依赖安装
```bash
pip install openai
```

### 2. 生成数据集
```bash
cd workflow_test
python generate_dataset.py
```

这将生成 `multi_task_dataset.jsonl` 文件，包含4个任务，每个任务3个测试用例。

### 3. 执行Workflow测试
```bash
python execute_workflow.py
```

这将读取数据集并执行完整的workflow测试，生成 `workflow_execution_results.jsonl` 文件。

## 输出文件

### 1. multi_task_dataset.jsonl
数据集文件，包含多个任务的测试数据：
```json
{
  "id": 0,
  "task_name": "aalmostarithmeticalprogression",
  "task_type": "sequence_analysis", 
  "task_description": "任务描述文本...",
  "test_cases": [
    {
      "case": {"n": 4, "b": [10, 20, 10, 30], "ans": 3},
      "prompt": "问题文本..."
    }
  ]
}
```

### 2. workflow_execution_results.jsonl
Workflow执行结果：
```json
{
  "task_id": 0,
  "task_name": "aalmostarithmeticalprogression",
  "task_type": "sequence_analysis",
  "task_description": "任务描述...",
  "system_prompt": "生成的系统提示...",
  "test_results": [
    {
      "test_case_id": 0,
      "prompt": "问题文本...",
      "solution": "模型解答...",
      "is_correct": true,
      "expected_case": {"n": 4, "b": [10, 20, 10, 30], "ans": 3}
    }
  ]
}
```

## 功能特点

### 数据集生成脚本
- 支持多种任务类型，测试框架的适应性
- 自动提取真实的aalmostarithmeticalprogression任务描述
- 为其他任务提供模拟的描述和测试用例
- 生成标准化的JSONL格式数据集

### Workflow执行脚本
- 根据任务类型生成专门的system_prompt
- 支持多任务混合测试
- 详细的统计信息和准确率分析
- 完整的测试过程记录

## 验证机制

每个任务都有专门的验证逻辑：
- **序列分析**: 验证数值答案的正确性
- **算术谜题**: 检查表达式中是否包含所有必需数字
- **密码学**: 验证解密后的明文
- **逻辑谜题**: 验证数字序列的完整性

## 扩展性

框架设计支持轻松添加新任务：
1. 在 `generate_dataset.py` 中添加新的bootcamp类
2. 在 `execute_workflow.py` 中添加对应的验证逻辑
3. 更新任务类型映射

## 配置说明

LLM配置在两个脚本中都有定义：
```python
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}
```

## 示例输出

运行 `execute_workflow.py` 后的统计信息示例：
```
============================================================
WORKFLOW测试统计结果
============================================================
总任务数: 4
总测试用例数: 12
总正确数: 8
总体准确率: 66.7%

任务名称                   类型                  准确率     详情
----------------------------------------------------------------------
aalmostarithmeticalprogression sequence_analysis       66.7%    2/3
game24                    arithmetic_puzzle          75.0%    3/4
cipher                    cryptography               100.0%   3/3
sudoku                    logic_puzzle                50.0%    1/2
```

## 注意事项

1. 确保有有效的API密钥和网络连接
2. 必须先运行数据集生成脚本，再运行执行脚本
3. 多任务设计可以测试框架对不同问题类型的适应能力
4. 所有输出文件保存在当前工作目录下 