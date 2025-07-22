# Workflow Test V2

这是一个改进版的workflow测试系统，用于从internbootcamp中动态提取任务，生成测试用例，并执行workflow测试。

## 功能特点

1. **动态任务加载**: 自动从internbootcamp目录中发现和加载可用的bootcamp任务
2. **智能描述提取**: 从源代码中提取任务描述（截取到"Here is a reference code"之前）
3. **自动语法修复**: 检测并修复文件开头注释的语法问题
4. **泛化的Workflow测试**: 
   - 使用上游模型生成指导性system_prompt
   - 下游模型基于system_prompt解决问题
   - 验证解答正确性

## 文件说明

- `process_dataset.py`: 数据集处理脚本，从internbootcamp中提取任务并生成测试用例
- `execute_workflow.py`: Workflow执行脚本，实现系统提示生成和任务解答验证
- `bootcamp_dataset.jsonl`: 生成的数据集文件（运行process_dataset.py后产生）
- `workflow_results.jsonl`: Workflow测试结果（运行execute_workflow.py后产生）

## 使用方法

### 1. 生成数据集
```bash
python process_dataset.py
```

这会：
- 扫描internbootcamp目录，发现可用任务
- 选择代表性任务（默认5个）
- 提取任务描述
- 生成测试用例
- 输出到`bootcamp_dataset.jsonl`

### 2. 执行Workflow测试
```bash
python execute_workflow.py
```

这会：
- 加载生成的数据集
- 为每个任务生成通用的system_prompt
- 使用下游模型解决测试用例
- 验证解答正确性
- 输出结果到`workflow_results.jsonl`

## 配置说明

LLM配置在`execute_workflow.py`中：
```python
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "your-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}
```

## 输出格式

### 数据集格式 (bootcamp_dataset.jsonl)
```json
{
    "id": 0,
    "task_name": "game24",
    "task_type": "arithmetic_puzzle",
    "task_description": "...",
    "test_cases": [
        {
            "case": {...},
            "prompt": "..."
        }
    ]
}
```

### 结果格式 (workflow_results.jsonl)
```json
{
    "task_id": 0,
    "task_name": "game24",
    "task_type": "arithmetic_puzzle", 
    "task_description": "...",
    "system_prompt": "...",
    "test_results": [
        {
            "test_case_id": 0,
            "prompt": "...",
            "solution": "...",
            "is_correct": true,
            "expected_case": {...}
        }
    ]
}
```

## 特点

- **最小化实现**: 代码简洁，专注核心功能
- **泛用性**: 不包含任务特定信息，动态加载任务
- **自动修复**: 处理internbootcamp中损坏的文件格式
- **完整验证**: 使用原始bootcamp类进行解答验证

## 依赖

- openai (用于LLM API调用)
- 标准Python库 