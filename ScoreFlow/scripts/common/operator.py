# common/operator.py

import asyncio
import logging
from typing import Any, Dict, List, Union

from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM

# 动态地从同级目录导入所有Pydantic模型
# 确保 common/operator_an.py 文件已存在且内容正确
from .operator_an import (
    EnsembleOp,
    # ExtractOp,
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
    async def __call__(self, instruction: str, context: str = "") -> str:
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


# class Extract(Operator):
#     """
#     核心算子：提取。
#     从文本中提取结构化的JSON信息。
#     """
#     async def __call__(self, instruction: str, context: str) -> Dict[str, Any]:
#         prompt = f"""You are a precise Data Extraction Agent. Your task is to analyze the provided context and extract information according to the user's instruction, formatting it as a JSON object.

# **User's Extraction Instruction:**
# {instruction}

# **Context to Analyze:**
# ---
# {context}
# ---

# Your response MUST be a valid XML containing ONLY an `<extracted_data>` tag. The content inside the `<extracted_data>` tag MUST be a single, valid JSON object string.

# **EXAMPLE:**
# If the user instruction is "extract the names and ages of all people", your response should look like this:
# <extracted_data>
# {{
#   "people": [
#     {{"name": "John Doe", "age": 30}},
#     {{"name": "Jane Smith", "age": 25}}
#   ]
# }}
# </extracted_data>
# """
#         # 直接调用LLM而不是使用xml_fill，以便我们可以自定义JSON解析
#         llm_response = await self.llm.aask(prompt)
        
#         # 手动解析XML和JSON
#         import re
#         import json
        
#         pattern = r"<extracted_data>(.*?)</extracted_data>"
#         match = re.search(pattern, llm_response, re.DOTALL)
        
#         if match:
#             json_str = match.group(1).strip()
#             try:
#                 # 使用json.loads而不是eval来正确解析JSON
#                 extracted_data = json.loads(json_str)
#                 return extracted_data
#             except json.JSONDecodeError as e:
#                 logger.error(f"Failed to parse JSON from LLM response: {e}")
#                 logger.debug(f"JSON string that failed to parse: {json_str}")
#                 return {}
#         else:
#             logger.warning(f"No <extracted_data> tag found in LLM response")
#             logger.debug(f"LLM response: {llm_response}")
#             return {}


class Revise(Operator):
    """
    核心算子：改进。
    根据指令，对一个已有的文本（草稿）进行审查和修订。
    """
    async def __call__(self, instruction: str, context_to_revise: str) -> str:
        print("=" * 60)
        print("\n🚀 执行 operator: Revise")
        prompt = f"""You are an expert editor. Your task is to revise the provided text based on the given instruction, and the goal is to improve the performance on answering the original problem.

**Instruction on how to revise:**
{instruction}

**Original Text to Revise:**
---
{context_to_revise}
---

**Original Problem:**
{self.problem_text}

Your response MUST be a valid XML format with two fields: 'thought' and 'revised_context'.
- In the "thought" field, explain your step-by-step revision process.
- In the "revised_context" field, provide ONLY the final, improved version of the text.

**EXAMPLE:**
<thought>The user asked to make the tone more formal. I will change 'guys' to 'team' and 'awesome' to 'excellent'.</thought>
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
    async def __call__(self, context_to_summarize: str) -> str:
        print("=" * 60)
        print("\n🚀 执行 operator: Summarize")
        prompt = f"""You are an expert summarizer. Your task is to read the following text and summarize its key points, especially those relevant to the original problem.

**Original Problem:**
{self.problem_text}

**Text to Summarize:**
---
{context_to_summarize}
---

**Your Summary:**
"""
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        return response["response"]


class Ensemble(Operator):
    """
    核心算子：决策。
    根据指令，从多个候选项中选择或融合。
    """
    async def __call__(self, instruction: str, contexts_to_ensemble: List[str]) -> str:
        print("=" * 60)
        print("\n🚀 执行 operator: Ensemble")
        formatted_contexts = ""
        for i, context in enumerate(contexts_to_ensemble):
            formatted_contexts += f"<option index='{i+1}'>\n{context}\n</option>\n\n"

        prompt = f"""You are an expert at evaluating, comparing, and synthesizing information from multiple sources. Your task is to follow the given strategic instruction to process a list of options.

**Original Problem:**
{self.problem_text}

**Strategic Instruction:**
{instruction}

**Options to Process:**
{formatted_contexts}

Your response MUST be a valid XML format with two fields: 'thought' and 'result'.
- In the "thought" field, explain your step-by-step reasoning process based on the instruction.
- In the "result" field, provide the final output of your operation. This could be one of the original options or a newly synthesized result.

**EXAMPLE:**
If the instruction is "Choose the option with the most recent date." and the options are "<option index='1'>Event A happened on 2023-05-10.</option>" and "<option index='2'>Event B occurred on 2024-01-22.</option>", your response should be:
<thought>The instruction is to find the most recent date. Comparing the two options, 2024-01-22 is later than 2023-05-10. Therefore, I will select the content of option 2.</thought>
<result>Event B occurred on 2024-01-22.</result>

so notice that here in the <result><result> **is not the index, but the content of the option itself, and you should put all the selected text, not simplified.**.
"""
        response = await self._fill_node(EnsembleOp, prompt, mode="xml_fill")
        return response["result"]
    

class FormatAnswer(Operator):
    """
    一个通用的、由系统框架调用的智能格式化算子。
    它接收一个外部提供的Prompt模板，使其行为可以被特异化。
    """
    def __init__(self, llm: LLM, problem_text: str = ""):
        super().__init__(llm, problem_text)

    # 核心修改：__call__方法现在接收一个prompt_template
    async def __call__(self, raw_result: Any, prompt_template: str) -> str:
        """
        使用一个外部提供的、可能特异化的Prompt模板来提取和格式化答案。
        """
        raw_str = str(raw_result)
        
        # 使用传入的prompt_template
        prompt = prompt_template.format(
            problem=self.problem_text, 
            raw_result=raw_str
        )
        
        response = await self._fill_node(FormatAnswerOp, prompt, mode="xml_fill")
        
        core_answer = response.get('final_answer')
        
        if core_answer is not None:
            return f"Final Answer: {core_answer}"
        else:
            logger.error(f"FormatAnswer operator failed to extract a final answer from raw result: '{raw_str}'")
            return f"Final Answer: Error - Failed to format the final answer."       