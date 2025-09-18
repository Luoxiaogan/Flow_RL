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
    FormatAnswerOp,
    VerifierOp,
    RefinerOp
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

    # async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
    #     """通用的LLM调用和Pydantic模型填充方法。"""
    #     fill_kwargs = {"context": prompt, "llm": self.llm}
    #     if mode:
    #         fill_kwargs["mode"] = mode
    #     fill_kwargs.update(extra_kwargs)
    #     try:
    #         node = await ActionNode.from_pydantic(op_class).fill(**fill_kwargs)
    #         return node.instruct_content.model_dump()
    #     except Exception as e:
    #         logger.error(f"在 _fill_node 中调用LLM或Pydantic填充时失败: {e}", exc_info=True)
    #         # 返回空字典，由调用方处理后续逻辑
    #         return {}

    async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
        """通用的LLM调用和Pydantic模型填充方法，增强了JSON数组的处理"""
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        fill_kwargs.update(extra_kwargs)
        
        try:
            # 对于Decompose操作，使用特殊的解析模式
            if op_class == DecomposeOp and mode == "xml_fill":
                # 直接获取LLM响应
                raw_response = await self.llm.aask(prompt)
                
                # 手动解析XML并处理JSON
                import re
                import json
                
                result = {}
                
                # 提取think标签
                think_match = re.search(r'<think>(.*?)</think>', raw_response, re.DOTALL)
                if think_match:
                    result['think'] = think_match.group(1).strip()
                
                # 提取并解析subproblems标签
                subproblems_match = re.search(r'<subproblems>(.*?)</subproblems>', raw_response, re.DOTALL)
                if subproblems_match:
                    json_str = subproblems_match.group(1).strip()
                    try:
                        result['subproblems'] = json.loads(json_str)
                    except json.JSONDecodeError:
                        # 如果JSON解析失败，保持为字符串
                        result['subproblems'] = json_str
                
                return result
            else:
                # 对于其他操作，使用标准流程
                node = await ActionNode.from_pydantic(op_class).fill(**fill_kwargs)
                return node.instruct_content.model_dump()
                
        except Exception as e:
            logger.error(f"在 _fill_node 中调用LLM或Pydantic填充时失败: {e}", exc_info=True)
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
</code>

for example, when you meet:
**TASK DESCRIPTION:(THE PROBLEM YOU SHOULD SOLVE BY WRITING THE PYTHON CODE USING THE FUNCTION SIGNATURE BELOW)**
Write a python function to set the left most unset bit.

**FUNCTION SIGNATURE(THE OUTPUT SOLUTION OF PYTHON CODE SHOULD IN THIS FUNCTION NAME):**
```python
def set_left_most_unset_bit(n):
```

**BASIC TEST CASES:**
```python
assert set_left_most_unset_bit(10) == 14
assert set_left_most_unset_bit(12) == 14
assert set_left_most_unset_bit(15) == 15
```

and you can write:
def solve():
    def set_left_most_unset_bit(n):
        pass
    assert set_left_most_unset_bit(10) == 14
    assert set_left_most_unset_bit(12) == 14
    assert set_left_most_unset_bit(15) == 15
    return 1"""
        
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
        response = DecomposeOp(**response) 
        return [sub.dict() for sub in response.subproblems]


class Verifier(Operator):
    """
    核心算子：验证。
    基于IMO Guard Agent的设计理念，严格验证解答的逻辑正确性和严谨性。
    作为验证者而非解决者，专注于发现和报告问题。
    """
    async def __call__(self, instruction: str = "", context: str = "") -> Dict[str, Any]:
        """
        对提供的解答进行严格的逐步验证。
        
        Args:
            instruction: 验证的具体指令或关注点
            context: 需要验证的解答文本
            
        Returns:
            包含verdict、findings和verification_log的字典
        """
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Verifier")
        
        prompt = f"""You are an expert mathematician and a meticulous verifier for rigorous mathematical solutions. Your primary task is to verify the provided solution with the same standards as an International Mathematical Olympiad (IMO) grader. A solution is correct only if every step is rigorously justified.

**Core Instructions:**
- Your sole task is to find and report ALL issues in the provided solution. You are a **verifier**, NOT a solver.
- Perform a **step-by-step** check of the entire solution.
- Do NOT attempt to correct errors or fill gaps you find.

**Error Classification:**
When you identify an issue, classify it as one of the following:

1. **Critical Error**: Any error that breaks the logical chain of proof, including:
   - Logical fallacies (e.g., invalid inference steps)
   - Factual errors (e.g., calculation mistakes)
   - **Procedure**: Explain the error and state it invalidates the reasoning. Do not check dependent steps, but scan for independent parts.

2. **Justification Gap**: Steps where conclusion may be correct but argument lacks rigor:
   - Incomplete reasoning
   - Hand-wavy explanations
   - Missing logical connections
   - **Procedure**: Explain the gap, assume the step is true for argument's sake, then continue verification.

**Verification Task:**
{instruction if instruction else "Verify the mathematical rigor and logical correctness of the provided solution."}

**Original Problem:**
{self.problem_text}

**Solution to Verify:**
---
{context if context else "No solution provided for verification."}
---

Your response MUST be in valid XML format with three fields:
- **verdict**: Overall validity assessment (e.g., "correct", "invalid due to critical error", "contains justification gaps")
- **findings**: JSON array where each finding has "location" (quoted text), "issue_type", and "description"
- **verification_log**: Detailed step-by-step verification explaining your reasoning

**EXAMPLE FORMAT:**
<verdict>The solution is invalid due to a Critical Error.</verdict>
<findings>
[
  {{"location": "From A > B and C > D, it follows that A-C > B-D", "issue_type": "Critical Error", "description": "This is a logical fallacy. Subtracting inequalities in this manner is not mathematically valid."}},
  {{"location": "By interchanging the limit and integral", "issue_type": "Justification Gap", "description": "The solution does not provide justification for this interchange, such as proving uniform convergence."}}
]
</findings>
<verification_log>
Step 1: The solution begins with... [detailed analysis]
Step 2: Here the author claims... [detailed analysis of each logical step]
...
</verification_log>"""
        
        response = await self._fill_node(VerifierOp, prompt, mode="xml_fill")
        return {
            "verdict": response.get("verdict", ""),
            "findings": response.get("findings", []),
            "verification_log": response.get("verification_log", "")
        }


class Refiner(Operator):
    """
    核心算子：改进。
    基于IMO系统的改进机制，根据验证反馈优化和完善解答质量。
    专注于解决验证中发现的问题并提高解答的严谨性。
    """
    async def __call__(self, instruction: str = "", context: str = "", verification_feedback: str = "") -> Dict[str, str]:
        """
        基于验证反馈改进解答质量。
        
        Args:
            instruction: 改进的具体指令或目标
            context: 原始解答文本
            verification_feedback: 验证过程的反馈信息
            
        Returns:
            包含analysis和refined_solution的字典
        """
        # 检查SILENT模式环境变量
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 执行 operator: Refiner")
        
        prompt = f"""You are an expert mathematician specializing in refining and improving mathematical solutions. Your task is to provide a refined solution that addresses ALL issues identified in the verification feedback while maintaining mathematical rigor.

**Core Refinement Principles:**
- **Rigor is Paramount**: Every step must be logically sound and clearly justified
- **Address All Issues**: Fix critical errors and fill justification gaps identified by the verifier
- **Maintain Clarity**: Ensure the solution is complete, coherent, and easy to follow
- **Preserve Correctness**: If unsure about a complete solution, provide only rigorously provable partial results

**Refinement Instructions:**
{instruction if instruction else "Improve the solution by addressing all verification feedback and enhancing mathematical rigor."}

**Original Problem:**
{self.problem_text}

**Original Solution to Improve:**
---
{context if context else "No original solution provided."}
---

**Verification Feedback to Address:**
---
{verification_feedback if verification_feedback else "No verification feedback provided."}
---

Your response MUST be in valid XML format with two fields:
- **analysis**: Your step-by-step analysis of the feedback and improvement strategy
- **refined_solution**: The complete improved solution addressing all identified issues

**Requirements for Refined Solution:**
1. Use proper mathematical notation (TeX format where appropriate: $x$, $\\frac{{a}}{{b}}$)
2. Provide clear justification for every logical step
3. Address each critical error and justification gap mentioned in the feedback
4. Structure the solution with clear logical flow
5. If a complete solution cannot be rigorously proven, clearly state what has been established

**EXAMPLE FORMAT:**
<analysis>
The verification feedback identified two main issues: 
1. A critical error in step 3 where inequalities were incorrectly combined
2. A justification gap in the limit interchange
I will address these by... [detailed improvement plan]
</analysis>
<refined_solution>
**Solution:**

Let me provide a rigorous solution to this problem.

**Step 1**: [Clear statement and justification]
Since we are given that... we can conclude that... because [rigorous reasoning].

**Step 2**: [Next logical step with justification]
From Step 1, we have established... Now, to proceed further... [detailed justification].

[Continue with complete, rigorous solution...]

**Final Answer**: [Clear, concise answer]
</refined_solution>"""
        
        response = await self._fill_node(RefinerOp, prompt, mode="xml_fill")
        return {
            "analysis": response.get("analysis", ""),
            "refined_solution": response.get("refined_solution", "")
        }