# common/operator.py

import os
import sys
import ast
import asyncio
import traceback
import logging
from typing import Any, Dict, List, Union
import concurrent.futures

from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM

from .operator_an import (
    EnsembleOp,
    GenerateOp,
    ReviseOp,
    CodeGenerateOp,
    DecomposeOp,
    FormatAnswerOp
)

logger = logging.getLogger(__name__)


class Operator:
    """
    通用Operator基类。
    传入的'problem'已经被外部处理器(Handler)预处理成干净的字符串。
    """
    def __init__(self, llm, problem_text: str = ""):
        """
        Initializes the operator.

        Args:
            llm: The language model instance to be used for operations.
            problem_text: A pre-processed, clean string representing the core problem text.
                          This is expected to be handled by an external BenchmarkHandler.
        """
        self.llm = llm
        self.problem_text = str(problem_text) if problem_text else ""

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("每个子类必须实现 __call__ 方法。")

    async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
        """通用的LLM调用和Pydantic模型填充方法。"""
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        fill_kwargs.update(extra_kwargs)
        try:
            node = await ActionNode.from_pydantic(op_class).fill(**fill_kwargs)
            return node.instruct_content.model_dump()
        except Exception as e:
            logger.error(f"在 _fill_node 中调用LLM或Pydantic填充时失败: {e}", exc_info=True)
            # 返回空字典，由调用方处理后续逻辑
            return {}


class Generate(Operator):
    """
    核心算子：创造。
    根据指令和上下文，生成新的、非结构化的文本。
    """
    async def __call__(self, instruction: str = "", context: str = "") -> str:
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Generate")
        prompt = f"""You are a helpful assistant. Follow the instruction to generate a response.

**Instruction:**
{instruction}

**Context from previous step:**
{context if context else "No context provided."}

**Original Problem:**
{self.problem_text}

**Your Response:**
"""
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        # 由于Pydantic模型是严格的，如果成功，'response'键必然存在
        return response["response"]


class Revise(Operator):
    """
    核心算子：改进。
    根据指令，对一个已有的文本（草稿）进行审查和修订。
    """
    async def __call__(self, instruction: str = "", context: str = "") -> str:
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Revise")
        prompt = f"""You are an expert editor. Your task is to revise the provided text based on the given instruction, and the goal is to improve the performance on answering the original problem.

**Instruction on how to revise:**
{instruction}

**Original Text to Revise:**
---
{context if context else "No context provided."}
---

**Original Problem:**
{self.problem_text}

Your response MUST be a valid XML format with two fields: 'think' and 'revised_context'.
- In the "think" field, explain your step-by-step revision process.
- In the "revised_context" field, provide ONLY the final, improved version of the text.

**EXAMPLE:**
<think>The user asked to make the tone more formal. I will change 'guys' to 'team' and 'awesome' to 'excellent'.</think>
<revised_context>The team's performance was excellent.</revised_context>

**notice that the revise should not change the original meaning, but rather improve clarity, correctness, or style.**
"""
        response = await self._fill_node(ReviseOp, prompt, mode="xml_fill")
        return response["revised_context"]


class Summarize(Operator):
    """
    核心算子：压缩。
    将长文本缩减为核心要点。
    """
    async def __call__(self, instruction: str = "", context: str = "") -> str:
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Summarize")
        prompt = f"""You are an expert summarizer. Your task is to read the following text and summarize its key points, especially those relevant to the original problem.

**Instruction on how to summarize:**
{instruction}

**Text to Summarize:**
---
{context if context else "No context provided."}
---

**Original Problem:**
{self.problem_text}

**Your Summary:**
"""
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        return response["response"]


class Ensemble(Operator):
    """
    核心算子：决策。
    根据指令，从多个候选项中选择或融合。
    """
    async def __call__(self, instruction: str = "", contexts_list: List[str] = []) -> str:
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Ensemble")
        formatted_contexts = ""
        for i, context in enumerate(contexts_list):
            formatted_contexts += f"<option index='{i+1}'>\n{context}\n</option>\n\n"

        prompt = f"""You are an expert at evaluating, comparing, and synthesizing information from multiple sources. Your task is to follow the given strategic instruction to process a list of options.

**Original Problem:**
{self.problem_text}

**Strategic Instruction:**
{instruction}

**Options to Process:**
{formatted_contexts}

Your response MUST be a valid XML format with two fields: 'think' and 'result'.
- In the "think" field, explain your step-by-step reasoning process based on the instruction.
- In the "result" field, provide the final output of your operation. This could be one of the original options or a newly synthesized result.

**EXAMPLE:**
If the instruction is "Choose the option with the most recent date." and the options are "<option index='1'>Event A happened on 2023-05-10.</option>" and "<option index='2'>Event B occurred on 2024-01-22.</option>", your response should be:
<think>The instruction is to find the most recent date. Comparing the two options, 2024-01-22 is later than 2023-05-10. Therefore, I will select the content of option 2.</think>
<result>Event B occurred on 2024-01-22.</result>

so notice that here in the <result></result> **is not the index, but the content of the option itself, and you should put all the selected text, not simplified.**.
"""
        response = await self._fill_node(EnsembleOp, prompt, mode="xml_fill")
        return response["result"]      

def check_code_safety(code: str, disallowed_imports: list) -> tuple:
    """使用AST解析检查代码安全性"""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # 检查 import 语句
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(lib) for lib in disallowed_imports):
                        return False, f"Prohibited import: {alias.name}"
            # 检查 from ... import 语句
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(node.module.startswith(lib) for lib in disallowed_imports):
                    return False, f"Prohibited import: {node.module}"
            # 检查 __import__ 调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == '__import__':
                    return False, "Dynamic import detected"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    return True, None

def run_code(code: str, timeout: int = 30):
    """
    Execute Python code safely in an isolated namespace.
    
    Args:
        code: Python code string to execute
        timeout: Maximum execution time (handled by caller)
    
    Returns:
        Tuple[str, str]: (status, result/error_message)
    """
    try:
        # Create isolated namespace
        global_namespace = {}
        
        # Prohibited imports for safety
        disallowed_imports = [
            "os", "sys", "subprocess", "multiprocessing",
            "matplotlib", "seaborn", "plotly", "bokeh", "ggplot",
            "pylab", "tkinter", "PyQt5", "wx", "pyglet"
        ]
        
        # AST安全检查
        is_safe, error_msg = check_code_safety(code, disallowed_imports)
        if not is_safe:
            logger.info(f"Code safety check failed: {error_msg}")
            return "Error", error_msg
        
        # Execute code
        exec(code, global_namespace)
        
        # Look for 'solve' function
        if 'solve' in global_namespace and callable(global_namespace['solve']):
            result = global_namespace['solve']()
            return "Success", str(result)
        else:
            return "Error", "Function 'solve' not found"
            
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_str = traceback.format_exception(exc_type, exc_value, exc_traceback)
        return "Error", f"Execution error: {str(e)}\n{''.join(tb_str)}"
    
class Programmer(Operator):
    """
    核心算子：编程。
    根据指令和上下文, 生成并执行Python代码来解决问题。
    """
    
    async def __call__(self, instruction: str = "", context: str = "", max_retries: int = 3) -> str:
        """
        生成并执行代码，支持自动重试和错误修正。
        
        Args:
            instruction: 编程任务的具体指令
            context: 之前步骤的上下文或分析结果
            max_retries: 最大重试次数
            
        Returns:
            执行结果的字符串描述
        """
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Programmer")
        
        feedback = ""
        code = None
        output = None
        
        for attempt in range(max_retries):
            # 生成代码
            code_response = await self._generate_code(instruction, context, feedback)
            code = code_response.get("code", "")
            
            if not code:
                return "Error: No code generated"
            
            # 执行代码
            status, output = await self._exec_code(code)
            
            if status == "Success":
                return f"""Successfully executed the generated code.

**Generated Code:**
```python
{code}
```

**Output:**
{output}"""
            
            # 准备下一轮的反馈
            if attempt < max_retries - 1:
                logger.info(f"Execution failed on attempt {attempt + 1}, retrying...")
                feedback = f"""
Previous attempt failed with error:
Status: {status}
Error: {output}

Please fix the code and try again."""
        
        # 所有重试都失败
        return f"""Code execution failed after {max_retries} attempts.

**Last Generated Code:**
```python
{code}
```

**Error:**
{output}"""
    
    async def _generate_code(self, instruction: str, context: str, feedback: str) -> dict:
        """生成Python代码"""
        prompt = f"""You are an expert Python programmer. Generate code to solve the given problem.

**Original Problem:**
{self.problem_text}

**Programming Instruction:**
{instruction}

**Context/Analysis from Previous Steps:**
{context if context else "No previous context."}

{feedback if feedback else ""}

Your response MUST be a valid XML format with two fields: 'think' and 'code'.
- In the "think" field, explain your approach to solving the problem.
- In the "code" field, provide complete, executable Python code.

**IMPORTANT REQUIREMENTS:**
1. Your code MUST define a function named 'solve()' that returns the answer
2. The solve() function should take no arguments
3. Do not use any prohibited libraries (os, sys, subprocess, plotting libraries, etc.)
4. The code should be self-contained and runnable

**EXAMPLE FORMAT:**
<think>I need to calculate the sum of numbers from 1 to 10. I'll use a simple loop.</think>
<code>
def solve():
    total = sum(range(1, 11))
    return total
</code>"""
        
        response = await self._fill_node(CodeGenerateOp, prompt, mode="xml_fill")
        return response
    
    async def _exec_code(self, code: str, timeout: int = 30) -> tuple:
        """异步执行代码并处理超时"""
        loop = asyncio.get_running_loop()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            try:
                # 提交执行任务到进程池
                future = loop.run_in_executor(executor, run_code, code)
                # 等待完成或超时
                result = await asyncio.wait_for(future, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                # 超时处理
                executor.shutdown(wait=False, cancel_futures=True)
                return "Error", f"Code execution timed out after {timeout} seconds"
            except Exception as e:
                return "Error", f"Unexpected error: {str(e)}"
            
class Decompose(Operator):
    """
    核心算子：分解。
    将复杂问题分解为可管理的子问题。
    """
    async def __call__(self, instruction: str = "", context: str = "") -> List[Dict[str, str]]:
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Decompose")
        
        prompt = f"""You are an expert at problem decomposition. Break down the complex problem into manageable subproblems.

**Instruction on decomposition strategy:**
{instruction}

**Problem/Context to Decompose:**
{context if context else "No context provided."}

**Original Problem:**
{self.problem_text}

Your response MUST be valid XML with 'think' and 'subproblems' fields.
- In "think", explain your decomposition strategy
- In "subproblems", provide a list where each item has:
  - id: unique identifier (e.g., "sub1", "sub2")
  - description: clear description of the subproblem
  - dependencies: comma-separated IDs of prerequisite subproblems (empty string if none)

**EXAMPLE:**
<think>This math problem requires finding area then volume. I'll break it into geometric calculations.</think>
<subproblems>
[
  {{"id": "sub1", "description": "Calculate the radius of the circle", "dependencies": ""}},
  {{"id": "sub2", "description": "Calculate the area using the radius", "dependencies": "sub1"}},
  {{"id": "sub3", "description": "Calculate the volume using the area", "dependencies": "sub2"}}
]
</subproblems>"""
        
        response = await self._fill_node(DecomposeOp, prompt, mode="xml_fill")
        return response["subproblems"]