# common/operator.py

import asyncio
import logging
from typing import Any, Dict, List, Union

from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM

from .operator_an import (
    EnsembleOp,
    GenerateOp,
    ReviseOp,
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
    async def __call__(self, instruction: str = "", contexts: List[str] = []) -> str:
        print("=" * 60)
        print("\n🚀 执行 operator: Ensemble")
        formatted_contexts = ""
        for i, context in enumerate(contexts):
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