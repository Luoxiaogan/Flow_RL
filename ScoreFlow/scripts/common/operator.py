# common/operator.py

import os
import platform
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
    FormatAnswerOp,
    VerifierOp,
    RefinerOp
)

# Import the lightweight executor at module level to avoid re-importing in subprocess
from .code_executor import run_code as execute_code

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
    
class VerifyAndRefine(Operator):
    """
    一个强大的、高级别的组合算子，它将一个完整的“验证-修正”循环封装成一个单一的、
    对工作流友好的调用。

    它的核心设计理念是向负责生成工作流的LLM隐藏所有内部复杂性。LLM只需要知道
    将一个可能有问题的解决方案（context）输入此算子，就能得到一个经过验证和修正后
    的、更高质量的解决方案（返回的字符串）。

    它内部处理了从Verifier获取结构化数据、进行条件判断、格式化反馈、调用Refiner
    等所有步骤。
    """
    def __init__(self, llm, problem_text: str = ""):
        """
        # 初始化VerifyAndRefine算子。
        # 它会创建其自身所需的内部Verifer和Refiner实例，作为其执行逻辑的“积木”。
        """
        super().__init__(llm, problem_text)
        # 这些是实现细节，被封装在此类内部，不会暴露给工作流。
        self._internal_verifier = Verifier(llm, problem_text)
        self._internal_refiner = Refiner(llm, problem_text)

    def _format_feedback_for_prompt(self, verification_output: Dict[str, Any]) -> str:
        """
        # 一个内部辅助方法，用于将Verifier返回的结构化字典转换为一个清晰、高质量、
        # 适合作为Prompt一部分的英文文本。
        """
        verdict = verification_output.get("verdict", "No verdict provided.")
        findings = verification_output.get("findings", [])

        if not findings:
            return f"The verifier's overall verdict is '{verdict}', but no specific findings were listed."

        # 精心设计的英文格式，能最好地引导Refiner LLM的注意力
        formatted_str = f"The verifier's verdict is '{verdict}'. You MUST address the following specific issues:\n"
        for i, finding in enumerate(findings):
            formatted_str += f"\nIssue #{i+1}:\n"
            # 使用 .get() 方法确保即使某些键缺失也不会导致程序崩溃
            location = finding.get('location', 'Not specified')
            issue_type = finding.get('issue_type', 'Unknown Type')
            description = finding.get('description', 'No description provided.')
            formatted_str += f"- Issue Type: {issue_type}\n"
            formatted_str += f"- Location in Text: \"{location}\"\n"
            formatted_str += f"- Detailed Description: {description}\n"
        return formatted_str

    async def __call__(self, instruction: str = "Fix all errors and improve the rigor of the solution.", context: str = "") -> str:
        """
        # 执行完整的验证-修正流程。
        # @param instruction: 一个高层次的指令，描述了修正的最终目标（例如，"让解决方案更易于理解"）。
        # @param context: 需要被验证和修正的初始解决方案文本。
        # @return: 一个经过修正的解决方案字符串；如果原始方案正确或修正失败，则返回原始方案。
        """
        # 遵循项目中的日志/打印惯例，增加可观察性
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("=" * 60)
            print("\n🚀 Executing high-level operator: VerifyAndRefine")
            print("--- Step 1: Verifying the provided solution ---")

        # 1. 调用内部验证器，获取结构化的字典输出以供程序化决策
        try:
            # 这里使用高质量的英文Prompt来调用内部的Verifier
            verification_output = await self._internal_verifier(
                instruction="Perform a comprehensive verification of the provided solution for mathematical rigor and logical correctness. Identify all critical errors and justification gaps.",
                context=context
            )
        except Exception as e:
            logger.error(f"Internal Verifier step in VerifyAndRefine failed: {e}", exc_info=True)
            # 如果验证步骤本身就失败了，无法继续，返回原始上下文是最安全的选择
            return context

        # 健壮性检查：确保我们得到了有效的结果
        if not verification_output or 'verdict' not in verification_output:
            logger.warning("Verification step did not return a valid result. Returning the original solution.")
            return context

        verdict = verification_output.get('verdict', '').lower()
        findings = verification_output.get('findings', [])
        
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print(f"Verifier Verdict: {verdict.upper()}")

        # 2. 核心决策逻辑：基于验证结果决定下一步行动
        if verdict == 'correct' and not findings:
            if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
                print("--- Solution is correct. No refinement needed. ---")
            # 解决方案已经很好了，直接返回原始版本
            return context

        # 如果代码执行到这里，意味着需要进行修正
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
            print("--- Step 2: Refining the solution based on feedback ---")

        # 3. 准备调用修正器 (Refiner)
        # 使用辅助方法将结构化反馈转换为高质量的英文文本
        feedback_for_refiner = self._format_feedback_for_prompt(verification_output)

        # 组合指令：将用户传入的顶层目标与具体的修正要求结合，形成一个强大的英文Prompt
        refinement_instruction = f"""Your high-level goal is: "{instruction}"

To achieve this, you MUST improve the original solution by addressing ALL of the following issues identified by a rigorous verifier:
---
{feedback_for_refiner}
---
"""
        # 4. 调用内部修正器
        try:
            refinement_output = await self._internal_refiner(
                instruction=refinement_instruction,
                context=context,
                verification_feedback=feedback_for_refiner # 尽管指令中已包含，但保留此参数以符合Refiner的原始接口
            )
        except Exception as e:
            logger.error(f"Internal Refiner step in VerifyAndRefine failed: {e}", exc_info=True)
            return context # 修正步骤失败，安全地返回原始方案

        # 5. 安全地提取结果并返回
        # 使用 .get() 提供一个回退值，如果refinement_output为空或没有'refined_solution'键，
        # 就安全地返回原始的context，确保工作流不会中断。
        refined_solution = refinement_output.get('refined_solution', context)
        
        if os.environ.get('SCOREFLOW_SILENT', 'false').lower() != 'true':
             if refined_solution != context:
                 print("--- Refinement complete. Returning improved solution. ---")
             else:
                 print("--- Refinement step did not produce a new solution. Returning original. ---")
        
        return refined_solution