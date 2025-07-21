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
from .operator_an import CodeGenerateOp, ScEnsembleOp, CodeFixOp, CodeRunnerResult, ReviewOp, FlexibleCustomCodeOp
from .op_prompt import SC_ENSEMBLE_PROMPT, CODE_FIX_PROMPT, CUSTOM_CODE_GENERATE_INSTRUCTION, REVIEW_PROMPT, FLEXIBLE_CUSTOM_PROMPT

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


class Review(Operator):
    """
    审查和改进生成的代码。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None):
        super().__init__(llm, problem)
        self.entry_point = self.problem.get("entry_point", "")

    async def __call__(self, solution: str) -> str:
        """
        :param solution: 需要审查的代码。
        :return: 审查并可能改进后的代码。
        """
        problem_description = self.problem.get("text", "")
        prompt = REVIEW_PROMPT.format(
            problem=problem_description,
            entry_point=self.entry_point,
            solution=solution
        )
        
        response = await self._fill_node(ReviewOp, prompt, mode="xml_fill")
        final_code = response.get("final_code", "")
        
        # Clean up XML tags if present  
        if "</final_code>" in final_code:
            final_code = final_code.replace("</final_code>", "").strip()
        if "<final_code>" in final_code:
            start = final_code.find("<final_code>") + len("<final_code>")
            final_code = final_code[start:].strip()
        
        return final_code


class FlexibleCustom(Operator):
    """
    灵活的自定义代码生成 Operator，支持各种代码生成模式。
    允许工作流定义自定义逻辑而不需要在提示中嵌入问题信息。
    """
    def __init__(self, llm: LLM, problem: Dict[str, Any] = None,
                 generation_pattern: str = "incremental",
                 strategies: List[str] = None,
                 max_refinements: int = 1,
                 use_structured_output: bool = True):
        """
        Args:
            llm: 语言模型实例
            problem: 包含 text 和 entry_point 的问题字典
            generation_pattern: 生成类型 (incremental, test_driven, modular, recursive)
            strategies: 生成过程中应用的自定义策略
            max_refinements: 最大优化迭代次数
            use_structured_output: 是否使用结构化输出格式
        """
        super().__init__(llm, problem)
        self.entry_point = self.problem.get("entry_point", "")
        self.generation_pattern = generation_pattern
        self.strategies = strategies or ["analyze_requirements", "handle_edge_cases", "optimize_solution"]
        self.max_refinements = max_refinements
        self.use_structured_output = use_structured_output
    
    async def __call__(self, custom_instruction: str = "", previous_results: List[str] = None,
                       generation_pattern: str = None, strategies: List[str] = None, 
                       max_refinements: int = None, use_structured_output: bool = None) -> str:
        """
        执行灵活的自定义 Operator。
        
        Args:
            custom_instruction: 来自工作流的额外自定义指令
            previous_results: 用于迭代/分支模式的先前结果
            generation_pattern: 覆盖构造函数中设置的生成模式
            strategies: 覆盖构造函数中设置的策略
            max_refinements: 覆盖构造函数中设置的最大优化次数
            use_structured_output: 覆盖构造函数中设置的结构化输出
            
        Returns:
            生成的代码解决方案
        """
        # 使用传入的参数或默认值
        pattern = generation_pattern or self.generation_pattern
        strat = strategies or self.strategies
        max_ref = max_refinements if max_refinements is not None else self.max_refinements
        
        problem_description = self.problem.get("text", "")
        
        # 准备先前结果的文本
        prev_results_text = ""
        if previous_results:
            prev_results_text = "\n\n".join([f"### Previous Attempt {i+1}\n```python\n{result}\n```" 
                                             for i, result in enumerate(previous_results)])
        
        prompt = FLEXIBLE_CUSTOM_PROMPT.format(
            problem=problem_description,
            entry_point=self.entry_point,
            custom_instruction=custom_instruction,
            generation_pattern=pattern,
            strategies=", ".join(strat),
            previous_results=prev_results_text
        )
        
        response = await self._fill_node(FlexibleCustomCodeOp, prompt, mode="xml_fill")
        code = response.get("code", "")
        needs_refinement = response.get("needs_refinement", False)
        
        # 处理优化迭代
        refinement_count = 0
        refined_results = [code] if code else []
        
        while needs_refinement and refinement_count < max_ref:
            refinement_count += 1
            logger.info(f"FlexibleCustom: 执行第 {refinement_count} 次优化迭代")
            
            # 使用先前的结果进行优化
            prompt = FLEXIBLE_CUSTOM_PROMPT.format(
                problem=problem_description,
                entry_point=self.entry_point,
                custom_instruction=f"{custom_instruction}\n\nRefinement iteration {refinement_count}: Please improve upon the previous solutions.",
                generation_pattern=pattern,
                strategies=", ".join(strat),
                previous_results="\n\n".join([f"### Attempt {i+1}\n```python\n{r}\n```" 
                                              for i, r in enumerate(refined_results)])
            )
            
            response = await self._fill_node(FlexibleCustomCodeOp, prompt, mode="xml_fill")
            code = response.get("code", "")
            needs_refinement = response.get("needs_refinement", False)
            
            if code:
                refined_results.append(code)
        
        # 返回最终的代码（最后一次迭代的结果）
        return refined_results[-1] if refined_results else ""