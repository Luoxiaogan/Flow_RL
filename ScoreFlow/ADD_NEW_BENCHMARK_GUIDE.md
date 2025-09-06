# ScoreFlow 新任务录入完整指南

## 📚 目录

1. [概述](#概述)
2. [准备工作](#准备工作)
3. [实现步骤](#实现步骤)
4. [文件详解](#文件详解)
5. [集成配置](#集成配置)
6. [测试验证](#测试验证)
7. [常见问题](#常见问题)
8. [最佳实践](#最佳实践)

## 概述

ScoreFlow 是一个模块化的基准测试执行框架，通过 LLM 驱动的算子系统生成和执行工作流来解决各类问题。本指南将详细介绍如何向 ScoreFlow 系统添加新的 benchmark 任务。

### 核心架构原则

- **统一抽象接口**：所有 benchmark 继承自 `BenchmarkHandler`
- **算子工作流系统**：使用 Generate/Revise/Summarize/Ensemble 四个核心算子
- **多策略验证**：支持 LLM 智能判断和规则验证

## 准备工作

### 1. 数据集准备

将你的数据集转换为 JSONL 格式，每行一个 JSON 对象：

```json
{"index": 0, "question": "问题文本", "answer": "答案", "其他字段": "..."}
{"index": 1, "question": "问题文本", "answer": "答案", "其他字段": "..."}
```

推荐的数据集位置：
- 训练集：`Processed_dataset/[benchmark_name]/train.jsonl`
- 测试集：`Processed_dataset/[benchmark_name]/test.jsonl`

### 2. 确定任务类型

分析你的任务属于哪种类型：
- **数学推理**（如 GSM8K）：需要多步计算
- **代码生成**（如 MBPP）：需要生成可执行代码
- **阅读理解**（如 DROP）：需要从文本中提取信息
- **知识问答**（如 HotpotQA）：需要多跳推理

## 实现步骤

### 步骤 1：创建 Benchmark 目录

```bash
mkdir ScoreFlow/scripts/[benchmark_name]
cd ScoreFlow/scripts/[benchmark_name]
```

### 步骤 2：实现 handler.py

创建 `handler.py` 文件，实现数据处理和验证逻辑：

```python
from typing import List, Dict, Any
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class [BenchmarkName]Handler(BenchmarkHandler):
    """
    [Benchmark名称] 数据集的处理器。
    
    处理 [任务类型] 任务，需要 [具体功能描述]。
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从数据中提取问题文本，格式化为用于生成工作流的提示。
        
        Args:
            indices: 要提取的问题索引列表
            
        Returns:
            格式化的问题文本字符串
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题相关字段
                question = problem.get('question', '')
                # 可以添加其他相关信息
                context = problem.get('context', '')
                
                # 使用 Markdown 格式化
                formatted_problem = f"""---
**QUESTION:**
{question}

**CONTEXT:**
{context if context else "No additional context."}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从{self.benchmark_name}数据中提取问题时出错: {e}")
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个问题的完整数据，用于执行和验证。
        
        Args:
            index: 问题索引
            
        Returns:
            包含完整问题和答案的字典
        """
        return self._get_problem_by_index(index)
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        判断模型输出是否正确。
        
        可以使用基类的 LLM 判断，或实现自定义逻辑。
        
        Args:
            model_output: 模型生成的答案
            ground_truth_data: 包含正确答案的完整数据
            
        Returns:
            True 如果答案正确，否则 False
        """
        # 选项 1：使用基类的 LLM 智能判断（推荐）
        return await self.llm_judge(model_output, ground_truth_data)
        
        # 选项 2：实现自定义判断逻辑
        # ground_truth = ground_truth_data.get('answer', '')
        # return self.custom_judge_logic(model_output, ground_truth)
```

### 步骤 3：创建 conditions.py

创建 `conditions.py` 文件，定义所有提示和配置：

```python
# Task-specific prompts and configuration for [benchmark_name]

TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **[Benchmark Name]** benchmark. [详细描述任务领域]

**Core Characteristics:**
- **Input:** [输入格式描述]
- **Required Skills:** [所需技能列表]
- **Answer Type:** [答案类型说明]

**Common Problem Types:**
- **Type 1:** [问题类型1描述]
- **Type 2:** [问题类型2描述]
- ...

**Key Success Factors:**
- [成功因素1]
- [成功因素2]
- ...
'''

SYSTEM_PROMPT = '''Your fundamental purpose is to act as an expert **[Domain] Problem Solver**. 
You translate problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve specific instances. You will receive:
1. A high-level description of the problem domain
2. A set of callable software "Operators" as building blocks
3. Example instances to understand the reasoning pattern

**Your response MUST follow this format:**

**1. A `<think>...</think>` block:**
Articulate your reasoning for creating a general solution for the problem class.

**2. A Python Code Block:**
Provide the complete reusable Python solution in markdown fences.
'''

PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''
    async def __call__(self):
        """
        Main entry point that executes the workflow.
        Returns the raw result from workflow execution.
        """
        TIMEOUT = {time}

        try:
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred. Details: {{escaped_error_details}}"
'''

START_PROMPT = '''### 2. Available Operators & Building Blocks

All operators are pre-initialized with the problem text and available as `self.operator_name`.

#### Core Operators

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information

**4. Ensemble: DECIDE between options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple solutions

### 3. Key Design Principles

**Dynamic Instruction Construction:**
Extract information early, then incorporate into subsequent instructions.

**Parallel Execution:**
Use `asyncio.gather()` for independent operations.

### 4. Your Task

Create a robust, reusable workflow for solving [benchmark_name] problems.

**Base Template:**

<think>
[Your reasoning for the general problem class...]
</think>
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        """
        import asyncio
        # YOUR WORKFLOW LOGIC HERE
```
'''
```

### 步骤 4：更新 benchmark_mapping.jsonl

在 `ScoreFlow/benchmark_mapping.jsonl` 中添加新任务的配置：

```json
{"benchmark": "[benchmark_name]", "handler_class": "[BenchmarkName]Handler", "handler_dir": "ScoreFlow/scripts/[benchmark_name]", "data_train_dir": "D:/temp/Flow_RL/Processed_dataset/[benchmark_name]/train.jsonl", "data_test_dir": "D:/temp/Flow_RL/Processed_dataset/[benchmark_name]/test.jsonl"}
```

### 步骤 5：创建运行脚本

创建 `Test_FILE/run_workflow_system_[benchmark_name].sh`：

```bash
#!/bin/bash

# 配置参数
BENCHMARK="[benchmark_name]"
DATASET_PATH="./Processed_dataset/${BENCHMARK}/train.jsonl"
OUTPUT_DIR="./workspace_${BENCHMARK}"
NUM_WORKERS=5
MAX_CONCURRENT_TASKS=10
BATCH_SIZE=20
TIMEOUT=180

# API 配置
export API_POOL='[
    {"api_key": "sk-xxx", "model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    {"api_key": "sk-yyy", "model": "gpt-4", "base_url": "https://api.openai.com/v1"}
]'

export EXEC_LLM='{"api_key": "sk-xxx", "model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"}'

# 运行主程序
python master_runner.py \
    --benchmark $BENCHMARK \
    --dataset-path $DATASET_PATH \
    --output-dir $OUTPUT_DIR \
    --num-workers $NUM_WORKERS \
    --max-concurrent-tasks $MAX_CONCURRENT_TASKS \
    --batch-size $BATCH_SIZE \
    --timeout $TIMEOUT
```

## 文件详解

### handler.py 核心方法

1. **get_prompt_text(indices)**
   - 用途：提取问题文本用于工作流生成
   - 输入：问题索引列表
   - 输出：格式化的问题文本
   - 注意：使用 Markdown 格式保持一致性

2. **get_verification_data(index)**
   - 用途：获取验证所需的完整数据
   - 输入：单个问题索引
   - 输出：包含问题和答案的字典

3. **judge(model_output, ground_truth_data)**
   - 用途：判断答案是否正确
   - 可选：使用基类 LLM 判断或自定义逻辑

### conditions.py 提示结构

1. **TASK_PROMPT**
   - 领域概述
   - 问题特征
   - 解决策略

2. **SYSTEM_PROMPT**
   - LLM 角色定义
   - 输出格式要求

3. **PYTHON_START/END**
   - 工作流执行模板
   - 错误处理逻辑

4. **START_PROMPT**
   - 算子文档
   - 设计原则
   - 示例模板

## 集成配置

### 1. 验证文件结构

```
ScoreFlow/
├── scripts/
│   ├── base_handler.py
│   ├── common/
│   │   ├── operator.py
│   │   └── operator_an.py
│   └── [benchmark_name]/
│       ├── handler.py
│       └── conditions.py
├── benchmark_mapping.jsonl (已更新)
└── ...

Processed_dataset/
└── [benchmark_name]/
    ├── train.jsonl
    └── test.jsonl

Test_FILE/
├── run_workflow_system_[benchmark_name].sh
└── ...
```

### 2. 环境变量设置

```bash
# 设置 Python 路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 设置 MetaGPT 配置路径
export METAGPT_CONFIG="./Test_FILE/config2.yaml"

# 可选：静默模式
export SCOREFLOW_SILENT=false
```

## 测试验证

### 1. 单元测试 Handler

创建测试脚本 `test_handler.py`：

```python
import asyncio
import sys
sys.path.append('.')

from ScoreFlow.scripts.[benchmark_name].handler import [BenchmarkName]Handler

async def test_handler():
    # 初始化 handler
    handler = [BenchmarkName]Handler(
        dataset_path="Processed_dataset/[benchmark_name]/test.jsonl"
    )
    
    # 测试数据加载
    print(f"Loaded {len(handler.data)} samples")
    
    # 测试 prompt 生成
    prompt = handler.get_prompt_text([0, 1, 2])
    print(f"Generated prompt:\n{prompt[:500]}...")
    
    # 测试验证数据获取
    verify_data = handler.get_verification_data(0)
    print(f"Verification data: {verify_data}")
    
    # 测试判断逻辑（需要配置 LLM）
    # result = await handler.judge("test answer", verify_data)
    # print(f"Judge result: {result}")

if __name__ == "__main__":
    asyncio.run(test_handler())
```

### 2. 测试工作流生成

```bash
# 生成单个工作流
python workflow_generator.py \
    --benchmark [benchmark_name] \
    --dataset-path Processed_dataset/[benchmark_name]/train.jsonl \
    --num-problems 3 \
    --output-dir test_output

# 检查生成的工作流
ls test_output/[benchmark_name]_workflow_*.py
```

### 3. 测试工作流执行

```bash
# 执行生成的工作流
python workflow_executor.py \
    --benchmark [benchmark_name] \
    --workflow-path test_output/[benchmark_name]_workflow_001.py \
    --dataset-path Processed_dataset/[benchmark_name]/test.jsonl \
    --test-indices 0 1 2
```

### 4. 完整系统测试

```bash
# 运行完整的工作流系统
bash run_workflow_system_[benchmark_name].sh
```

## 常见问题

### Q1: 如何处理特殊的答案格式？

对于特殊答案格式（如代码、数学公式），可以在 handler.py 中实现自定义的 judge 方法：

```python
async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
    # 提取并规范化答案
    predicted = self.extract_answer(model_output)
    ground_truth = ground_truth_data.get('answer', '')
    
    # 自定义比较逻辑
    if self.is_math_problem(ground_truth_data):
        return self.compare_math_answers(predicted, ground_truth)
    else:
        return await self.llm_judge(model_output, ground_truth_data)
```

### Q2: 如何优化工作流生成质量？

1. **提供详细的 TASK_PROMPT**：包含领域特征、常见模式、解决策略
2. **使用示例问题**：在 START_PROMPT 中包含 1-2 个典型示例
3. **调整算子组合**：根据任务特点选择合适的算子序列

### Q3: 如何处理超时问题？

```python
# 在 conditions.py 的 PYTHON_END 中调整超时时间
TIMEOUT = {time}  # 默认 180 秒，可以增加

# 或在运行脚本中设置
--timeout 300  # 5 分钟
```

### Q4: 如何调试执行错误？

1. 设置详细日志：
```bash
export SCOREFLOW_SILENT=false
export LOG_LEVEL=DEBUG
```

2. 查看工作流代码：
```bash
cat workspace_[benchmark_name]/[benchmark_name]_workflow_*.py
```

3. 单独执行问题工作流：
```python
python workflow_executor.py --workflow-path [path] --test-indices [index] --debug
```

## 最佳实践

### 1. 数据预处理

- **统一格式**：确保所有数据字段命名一致
- **清理文本**：去除多余空白、特殊字符
- **验证完整性**：检查必需字段是否存在

### 2. Prompt 工程

- **明确任务定义**：在 TASK_PROMPT 中清晰描述任务目标
- **提供上下文**：包含领域知识和背景信息
- **示例驱动**：提供具体但通用的示例

### 3. 答案验证

- **多策略结合**：LLM 判断 + 规则验证
- **容错处理**：处理答案格式变化
- **日志记录**：记录判断过程便于调试

### 4. 性能优化

- **并行处理**：使用 asyncio.gather() 并行执行独立操作
- **批量处理**：合理设置 batch_size 和 num_workers
- **缓存机制**：复用生成的工作流

### 5. 错误处理

```python
try:
    result = await self.run_workflow()
except asyncio.TimeoutError:
    return "Timeout error"
except Exception as e:
    logger.error(f"Workflow execution failed: {e}")
    return f"Error: {str(e)}"
```

## 示例：添加新的数学推理任务

假设要添加一个名为 "algebra" 的代数任务：

### 1. 创建目录
```bash
mkdir ScoreFlow/scripts/algebra
```

### 2. 实现 handler.py
```python
from typing import List, Dict, Any
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class AlgebraHandler(BenchmarkHandler):
    def get_prompt_text(self, indices: List[int]) -> str:
        problems = [self._get_problem_by_index(i) for i in indices]
        formatted = []
        for p in problems:
            formatted.append(f"""---
**PROBLEM:**
{p.get('problem', '')}

**EQUATION:**
{p.get('equation', '')}
---""")
        return "\n\n".join(formatted)
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        return self._get_problem_by_index(index)
```

### 3. 创建 conditions.py
```python
TASK_PROMPT = '''### Algebra Problem Solving
Solve algebraic equations and word problems requiring symbolic manipulation.
...
'''

# ... 其他配置 ...
```

### 4. 更新 benchmark_mapping.jsonl
```json
{"benchmark": "algebra", "handler_class": "AlgebraHandler", ...}
```

### 5. 测试运行
```bash
python workflow_generator.py --benchmark algebra --dataset-path Processed_dataset/algebra/train.jsonl
```

## 总结

成功添加新 benchmark 的关键步骤：

1. ✅ 准备 JSONL 格式的数据集
2. ✅ 创建 benchmark 目录结构
3. ✅ 实现 handler.py（数据处理）
4. ✅ 创建 conditions.py（提示配置）
5. ✅ 更新 benchmark_mapping.jsonl
6. ✅ 创建运行脚本
7. ✅ 测试和验证

遵循这个指南，你可以轻松地将新的任务集成到 ScoreFlow 系统中。如有问题，请参考现有的 benchmark 实现（如 gsm8k、mbpp）作为参考。

---

**文档版本**: 1.0  
**最后更新**: 2025-01-06  
**作者**: ScoreFlow Team