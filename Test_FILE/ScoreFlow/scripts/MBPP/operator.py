# ScoreFlow/scripts/mbpp/operator.py

import sys
import traceback
from typing import List, Dict, Any
# ### 修改点 1: 增加从共享 utils 模块的导入 ###
import multiprocessing
from ScoreFlow.scripts.utils.code_executor import unsafe_execute

from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM
from metagpt.logs import logger

# 从同一目录导入新的 Pydantic 模型和 Prompt 模板
from .operator_an import CodeGenerateOp, ScEnsembleOp, CodeFixOp, CodeRunnerResult
from .op_prompt import SC_ENSEMBLE_PROMPT, CODE_FIX_PROMPT, CUSTOM_CODE_GENERATE_INSTRUCTION

class Operator:
    """
    所有 Operator 的基类，与 metagpt ActionNode 集成。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None):
        self.llm = llm
        self.problem = problem or {} # 确保 problem 是一个字典

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        fill_kwargs.update(extra_kwargs)
        node = await ActionNode.from_pydantic(op_class).fill(**fill_kwargs)
        return node.instruct_content.model_dump()


class CustomCodeGenerate(Operator):
    """
    根据指令生成 Python 代码。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None):
        super().__init__(llm, problem)
        self.entry_point = self.problem.get("entry_point", "")

    async def __call__(self, instruction: str) -> str:
        """
        :param instruction: 鼓励模型思考的指令, e.g., "Solve the problem step-by-step..."
        :return: 生成的纯 Python 代码字符串。
        """
        # problem["text"] 包含问题描述
        problem_description = self.problem.get("text", "")
        # 将用户指令、问题描述和补充提示拼接在一起
        prompt = f"{instruction}\n\n### Problem Description\n{problem_description}\n\n{CUSTOM_CODE_GENERATE_INSTRUCTION}"
        
        # 使用 code_fill 模式让 metagpt 更好地生成代码
        response = await self._fill_node(CodeGenerateOp, prompt, mode="code_fill", function_name=self.entry_point)
        return response.get("code", "")


class ScEnsemble(Operator):
    """
    从多个代码解决方案中选择最好的一个。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None):
        super().__init__(llm, problem)

    async def __call__(self, solutions: List[str]) -> str:
        if not solutions:
            return ""
        if len(solutions) == 1:
            return solutions[0]

        answer_mapping = {chr(65 + i): i for i, _ in enumerate(solutions)}
        solution_text = "\n\n".join(
            f"### Solution {chr(65 + i)}\n```python\n{s}\n```" for i, s in enumerate(solutions)
        )
        
        problem_description = self.problem.get("text", "")
        prompt = SC_ENSEMBLE_PROMPT.format(problem=problem_description, solutions=solution_text)
        
        response = await self._fill_node(ScEnsembleOp, prompt, mode="xml_fill")
        selected_letter = response.get("solution_letter", "").strip().upper()
        
        if selected_letter in answer_mapping:
            return solutions[answer_mapping[selected_letter]]
        
        # 如果LLM返回了无效字母，则默认返回第一个
        logger.warning(f"ScEnsemble returned an invalid letter '{selected_letter}'. Defaulting to the first solution.")
        return solutions[0]


class CodeFix(Operator):
    """
    根据测试失败的错误信息，反思并修复代码。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None):
        super().__init__(llm, problem)

    async def __call__(self, code: str, error_message: str) -> str:
        """
        :param code: 失败的代码。
        :param error_message: 来自 CodeRunner 的错误信息。
        :return: 修复后的代码字符串。
        """
        problem_description = self.problem.get("text", "")
        prompt = CODE_FIX_PROMPT.format(
            problem=problem_description,
            code=code,
            error_message=error_message
        )
        
        response = await self._fill_node(CodeFixOp, prompt, mode="xml_fill")
        return response.get("fixed_code", "")


# ----------------- 这是拆分出的新 Operator -----------------

class CodeRunner(Operator):
    """
    执行代码并根据测试用例进行验证。
    这个 Operator 不调用 LLM，只执行本地代码。
    """
    def __init__(self, llm: LLM = None, problem: Dict[str, Any] = None):
        # 注意：这个 operator 理论上不需要 LLM，但为保持接口一致性而保留。
        super().__init__(llm, problem)

    async def __call__(self, code_to_test: str) -> CodeRunnerResult:
        """
        执行代码并返回结构化的测试结果。
        :param code_to_test: 需要被测试的 Python 代码字符串。
        :return: 一个包含测试结果的 CodeRunnerResult 对象。
        """
        # 从 self.problem (完整的MBPP数据条目) 中获取测试列表
        test_list = self.problem.get("test_list")
        
        if not code_to_test or not test_list:
            return CodeRunnerResult(
                is_correct=False, 
                error_message="Generated code or test list is empty."
            )
        
        ### 修改点 2: 移除本地和临时的导入语句 ###
        # 旧代码: from ScoreFlow.scripts.mbpp.handler import unsafe_execute
        # 旧代码: import multiprocessing

        result_queue = multiprocessing.Queue()
        # 直接使用在文件顶部导入的 unsafe_execute 和 multiprocessing
        process = multiprocessing.Process(
            target=unsafe_execute,
            args=(code_to_test, test_list, result_queue)
        )
        
        timeout = 10 # 执行超时时间
        process.start()
        process.join(timeout=timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            return CodeRunnerResult(
                is_correct=False,
                error_message=f"Execution timed out after {timeout} seconds."
            )

        if process.exitcode != 0:
            # 尝试从队列中获取更详细的错误
            try:
                status, message = result_queue.get_nowait()
                return CodeRunnerResult(is_correct=False, error_message=message)
            except multiprocessing.queues.Empty:
                return CodeRunnerResult(
                    is_correct=False,
                    error_message=f"Execution process exited with non-zero code: {process.exitcode}."
                )
        
        try:
            status, message = result_queue.get_nowait()
            is_correct = (status == "success")
            return CodeRunnerResult(
                is_correct=is_correct,
                error_message=None if is_correct else message
            )
        except multiprocessing.queues.Empty:
            return CodeRunnerResult(
                is_correct=False, 
                error_message="Result queue was empty despite process success. Unknown execution error."
            )