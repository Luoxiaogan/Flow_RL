# ScoreFlow 新任务快速录入指南（简化版）

## 🚀 快速开始

本指南专注于核心实现，让您能够快速添加新的 benchmark 并进行单元测试，无需修改 Test_FILE 中的执行脚本。

## 📁 最小实现结构

```
ScoreFlow/
├── scripts/
│   └── [your_benchmark]/
│       ├── handler.py       # 核心：数据处理逻辑
│       └── conditions.py    # 核心：提示模板
└── benchmark_mapping.jsonl  # 注册新任务
```

## 步骤 1：创建 Benchmark 目录

```bash
# 在 ScoreFlow/scripts/ 下创建新目录
mkdir ScoreFlow/scripts/[your_benchmark]
```

## 步骤 2：实现 handler.py

创建 `ScoreFlow/scripts/[your_benchmark]/handler.py`：

```python
from typing import List, Dict, Any
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class [YourBenchmark]Handler(BenchmarkHandler):
    """
    [Your Benchmark] 数据集的处理器。
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        提取问题文本，格式化为 Markdown。
        
        这个方法用于：
        - 从数据集中提取指定索引的问题
        - 格式化成统一的 Markdown 格式
        - 返回给 LLM 生成工作流
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 根据你的数据集结构提取字段
                question = problem.get('question', '')  # 修改为你的字段名
                
                # 统一使用 Markdown 格式
                formatted_problem = f"""---
**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            # 多个问题用两个换行分隔
            return "\n\n".join(formatted_problems)
            
        except (KeyError, IndexError) as e:
            raise ValueError(f"从数据中提取问题时出错: {e}")
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取用于验证的完整数据。
        
        直接返回指定索引的完整数据记录即可。
        """
        return self._get_problem_by_index(index)
    
    # 可选：自定义判断逻辑
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        判断答案是否正确。
        
        默认使用基类的 LLM 智能判断。
        如需自定义逻辑，可以覆盖此方法。
        """
        # 使用基类的 LLM 判断（推荐）
        return await self.llm_judge(model_output, ground_truth_data)
```

## 步骤 3：创建 conditions.py（骨架）

创建 `ScoreFlow/scripts/[your_benchmark]/conditions.py`：

```python
# 任务描述
TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is **[Your Benchmark Name]**.

**Core Characteristics:**
- **Input:** [描述输入格式]
- **Output:** [描述输出格式]
- **Skills:** [所需技能]
'''

# 系统提示
SYSTEM_PROMPT = '''Your fundamental purpose is to act as an expert problem solver.
You translate problem specifications into Python solution blueprints.

Your response MUST follow this format:
1. A `<think>...</think>` block with your reasoning
2. A Python code block with the solution
'''

# Python 代码头部
PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

# Python 代码尾部（固定模板）
PYTHON_END = '''
    async def __call__(self):
        """
        Main entry point that executes the workflow.
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

# 操作符说明
START_PROMPT = '''### 2. Available Operators

**1. Generate:** `await self.generate(instruction: str, context: str = "") -> str`
**2. Revise:** `await self.revise(instruction: str, context: str) -> str`
**3. Summarize:** `await self.summarize(instruction: str, context: str) -> str`
**4. Ensemble:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`

### 3. Your Task

Create a workflow to solve the problem using the operators above.

<think>
[Your reasoning here...]
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
        import asyncio
        # YOUR WORKFLOW LOGIC HERE
        pass
```
'''
```

## 步骤 4：更新 benchmark_mapping.jsonl

在 `ScoreFlow/benchmark_mapping.jsonl` 文件末尾添加一行：

```json
{"benchmark": "[your_benchmark]", "handler_class": "[YourBenchmark]Handler", "handler_dir": "ScoreFlow/scripts/[your_benchmark]", "data_train_dir": "D:/temp/Flow_RL/Processed_dataset/[your_benchmark]/train.jsonl", "data_test_dir": "D:/temp/Flow_RL/Processed_dataset/[your_benchmark]/test.jsonl"}
```

## 步骤 5：单元测试 Handler

创建测试脚本 `test_[your_benchmark]_handler.py`：

```python
#!/usr/bin/env python3
"""
Handler 单元测试脚本
用于测试新 benchmark 的基本功能
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 替换为你的 benchmark 名称
BENCHMARK_NAME = "[your_benchmark]"
HANDLER_CLASS_NAME = "[YourBenchmark]Handler"
(请你注意,HANDLER_CLASS_NAME必须是BENCHMARK_NAME的名称,仅将首字母的大写)

def test_data_loading():
    """测试数据加载功能"""
    print("\n" + "="*60)
    print("测试 1：数据加载")
    print("="*60)
    
    try:
        # 动态导入 handler
        handler_module = __import__(
            f"ScoreFlow.scripts.{BENCHMARK_NAME}.handler",
            fromlist=[HANDLER_CLASS_NAME]
        )
        HandlerClass = getattr(handler_module, HANDLER_CLASS_NAME)
        
        # 创建 handler 实例
        dataset_path = f"Processed_dataset/{BENCHMARK_NAME}/test.jsonl"
        handler = HandlerClass(dataset_path=dataset_path)
        
        print(f"✅ 成功加载 {len(handler.data)} 条数据")
        
        # 显示前 3 条数据的结构
        print("\n前 3 条数据示例：")
        for i in range(min(3, len(handler.data))):
            data = handler.data[i]
            print(f"\n数据 {i}:")
            for key in list(data.keys())[:5]:  # 只显示前 5 个字段
                value = str(data[key])[:100]  # 限制长度
                print(f"  {key}: {value}...")
        
        return handler
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_prompt_generation(handler):
    """测试提示生成功能"""
    print("\n" + "="*60)
    print("测试 2：提示生成")
    print("="*60)
    
    if not handler:
        print("⚠️ 跳过：Handler 未初始化")
        return
    
    try:
        # 测试单个问题
        prompt_single = handler.get_prompt_text([0])
        print("单个问题的提示：")
        print("-" * 40)
        print(prompt_single[:500] + "..." if len(prompt_single) > 500 else prompt_single)
        
        # 测试多个问题
        indices = [0, 1, 2] if len(handler.data) >= 3 else list(range(len(handler.data)))
        prompt_multiple = handler.get_prompt_text(indices)
        print(f"\n{len(indices)} 个问题的提示长度: {len(prompt_multiple)} 字符")
        
        # 验证格式
        if "---" in prompt_multiple and "**QUESTION:**" in prompt_multiple:
            print("✅ 提示格式正确（包含 Markdown 分隔符）")
        else:
            print("⚠️ 提示格式可能需要调整")
        
    except Exception as e:
        print(f"❌ 提示生成失败: {e}")
        import traceback
        traceback.print_exc()

def test_verification_data(handler):
    """测试验证数据获取"""
    print("\n" + "="*60)
    print("测试 3：验证数据获取")
    print("="*60)
    
    if not handler:
        print("⚠️ 跳过：Handler 未初始化")
        return
    
    try:
        # 获取第一个问题的验证数据
        verify_data = handler.get_verification_data(0)
        
        print("验证数据结构：")
        print("-" * 40)
        for key, value in verify_data.items():
            value_str = str(value)[:100]
            print(f"{key}: {value_str}...")
        
        # 检查关键字段
        required_fields = ['answer']  # 根据需要调整
        missing_fields = [f for f in required_fields if f not in verify_data]
        
        if not missing_fields:
            print(f"\n✅ 包含所有必需字段")
        else:
            print(f"\n⚠️ 缺少字段: {missing_fields}")
        
    except Exception as e:
        print(f"❌ 验证数据获取失败: {e}")
        import traceback
        traceback.print_exc()

async def test_judge_logic(handler):
    """测试判断逻辑（可选）"""
    print("\n" + "="*60)
    print("测试 4：判断逻辑（需要配置 LLM）")
    print("="*60)
    
    if not handler:
        print("⚠️ 跳过：Handler 未初始化")
        return
    
    # 检查是否配置了 LLM
    if not handler.config:
        print("⚠️ 跳过：未配置 LLM（需要设置 config 参数）")
        print("\n如需测试 judge 功能，请配置 LLM：")
        print("handler.config = {'api_key': 'xxx', 'model': 'gpt-4', ...}")
        return
    
    try:
        # 获取测试数据
        verify_data = handler.get_verification_data(0)
        ground_truth = verify_data.get('answer', 'N/A')
        
        # 测试正确答案
        result_correct = await handler.judge(ground_truth, verify_data)
        print(f"判断正确答案: {result_correct}")
        
        # 测试错误答案
        result_wrong = await handler.judge("错误答案", verify_data)
        print(f"判断错误答案: {result_wrong}")
        
        if result_correct and not result_wrong:
            print("✅ 判断逻辑正常")
        else:
            print("⚠️ 判断逻辑可能需要调整")
        
    except Exception as e:
        print(f"❌ 判断逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_conditions_file():
    """检查 conditions.py 文件"""
    print("\n" + "="*60)
    print("测试 5：检查 conditions.py")
    print("="*60)
    
    try:
        # 导入 conditions 模块
        conditions_module = __import__(
            f"ScoreFlow.scripts.{BENCHMARK_NAME}.conditions",
            fromlist=['TASK_PROMPT', 'SYSTEM_PROMPT', 'PYTHON_START', 'PYTHON_END', 'START_PROMPT']
        )
        
        required_vars = [
            'TASK_PROMPT',
            'SYSTEM_PROMPT', 
            'PYTHON_START',
            'PYTHON_END',
            'START_PROMPT'
        ]
        
        print("检查必需的变量：")
        all_present = True
        for var in required_vars:
            if hasattr(conditions_module, var):
                content = getattr(conditions_module, var)
                print(f"✅ {var}: {len(content)} 字符")
            else:
                print(f"❌ {var}: 缺失")
                all_present = False
        
        if all_present:
            print("\n✅ conditions.py 包含所有必需变量")
        else:
            print("\n⚠️ conditions.py 缺少某些变量")
        
    except ImportError as e:
        print(f"❌ 无法导入 conditions.py: {e}")
    except Exception as e:
        print(f"❌ 检查 conditions.py 时出错: {e}")

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print(f"ScoreFlow Handler 单元测试")
    print(f"Benchmark: {BENCHMARK_NAME}")
    print("="*60)
    
    # 1. 测试数据加载
    handler = test_data_loading()
    
    # 2. 测试提示生成
    test_prompt_generation(handler)
    
    # 3. 测试验证数据
    test_verification_data(handler)
    
    # 4. 测试判断逻辑（异步）
    # asyncio.run(test_judge_logic(handler))
    
    # 5. 检查 conditions.py
    check_conditions_file()
    
    # 总结
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n下一步：")
    print("1. 根据测试结果调整 handler.py")
    print("2. 完善 conditions.py 中的提示内容")
    print("3. 确保数据集格式正确")
    print("4. 运行完整的工作流测试（可选）")

if __name__ == "__main__":
    main()
```

## 🎯 快速实现示例

### 示例：添加简单的问答任务

假设你有一个名为 "simple_qa" 的问答数据集：

#### 1. 创建目录
```bash
mkdir ScoreFlow/scripts/simple_qa
```

#### 2. 实现 handler.py
```python
from typing import List, Dict, Any
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class SimpleqaHandler(BenchmarkHandler):
    
    def get_prompt_text(self, indices: List[int]) -> str:
        problems = [self._get_problem_by_index(i) for i in indices]
        formatted = []
        
        for p in problems:
            formatted.append(f"""---
**QUESTION:**
{p.get('question', '')}

**CONTEXT:**
{p.get('context', 'No context provided.')}
---""")
        
        return "\n\n".join(formatted)
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        return self._get_problem_by_index(index)
```

#### 3. 创建 conditions.py（最小化）
```python
TASK_PROMPT = '''### Simple Question Answering
Answer questions based on provided context.
'''

SYSTEM_PROMPT = '''You are an expert question answering system.'''

PYTHON_START = '''import asyncio
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create
'''

PYTHON_END = '''
    async def __call__(self):
        TIMEOUT = {time}
        try:
            return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
        except:
            return "Error occurred"
'''

START_PROMPT = '''Create a workflow to answer the question.'''
```

#### 4. 更新 benchmark_mapping.jsonl
```json
{"benchmark": "simple_qa", "handler_class": "SimpleqaHandler", "handler_dir": "ScoreFlow/scripts/simple_qa", "data_train_dir": "D:/temp/Flow_RL/Processed_dataset/simple_qa/train.jsonl", "data_test_dir": "D:/temp/Flow_RL/Processed_dataset/simple_qa/test.jsonl"}
```

#### 5. 运行测试
```bash
# 修改测试脚本中的 benchmark 名称
BENCHMARK_NAME = "simple_qa"
HANDLER_CLASS_NAME = "SimpleqaHandler"

# 运行测试
python test_simple_qa_handler.py
```

## ✅ 检查清单

- [ ] 创建了 `ScoreFlow/scripts/[your_benchmark]/` 目录
- [ ] 实现了 `handler.py` 的三个核心方法
- [ ] 创建了 `conditions.py` 骨架文件
- [ ] 在 `benchmark_mapping.jsonl` 中注册了新任务
- [ ] 数据集已放在 `Processed_dataset/[your_benchmark]/` 目录
- [ ] 运行了单元测试并通过

## 📝 注意事项

`★ Insight ─────────────────────────────────────`
1. handler.py 的核心是 get_prompt_text 方法，它决定了 LLM 看到的问题格式
2. conditions.py 可以先用最简骨架，后续根据需要逐步完善提示内容
3. 单元测试能快速验证实现是否正确，无需运行完整的工作流系统
`─────────────────────────────────────────────────`

### 数据集格式要求

JSONL 格式，每行一个 JSON 对象：
```json
{"index": 0, "question": "...", "answer": "...", ...}
{"index": 1, "question": "...", "answer": "...", ...}
```

### 字段映射

在 `get_prompt_text` 中根据你的数据集调整字段名：
```python
# 常见字段映射示例
question = problem.get('question', '')      # 或 'text', 'prompt'
context = problem.get('context', '')        # 或 'passage', 'background'  
answer = problem.get('answer', '')          # 或 'solution', 'output'
```

### 调试技巧

1. **打印数据结构**：在 handler 中添加 print 语句查看数据
2. **逐步测试**：先测试数据加载，再测试其他功能
3. **查看现有实现**：参考 gsm8k 或 mbpp 的实现

## 🚀 下一步（可选）

如果单元测试通过，你可以：

1. 完善 conditions.py 中的提示内容
2. 添加自定义的 judge 逻辑（如需要）
3. 使用现有的运行脚本测试完整工作流：
   ```bash
   # 使用类似的现有脚本测试
   bash run_workflow_system_gsm8k.sh
   # 修改其中的 BENCHMARK 变量为你的 benchmark 名称
   ```

---

**文档版本**: 1.0 (简化版)  
**最后更新**: 2025-01-06  
**特点**: 专注核心实现，快速上手，独立测试