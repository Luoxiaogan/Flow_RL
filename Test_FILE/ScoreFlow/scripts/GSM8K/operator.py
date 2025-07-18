import concurrent
import sys
import traceback
from typing import List, Union, Dict, Any
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

# ### 修改点：将所有硬编码的 'GSM8K' 改为小写的 'gsm8k' ###
from ScoreFlow.scripts.gsm8k.operator_an import (
    GenerateOp, CodeGenerateOp, ScEnsembleOp, ReviewOp, ReflectOp
)
from ScoreFlow.scripts.gsm8k.op_prompt import (
    SC_ENSEMBLE_PROMPT, REVIEW_PROMPT, PYTHON_CODE_VERIFIER_PROMPT, REFLECT_PROMPT
)
from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM

logger = logging.getLogger(__name__)

class Operator:
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        self.llm = llm
        self.problem_data = problem

        if isinstance(problem, dict):
            self.problem_text = problem.get('question', '')
        elif isinstance(problem, str):
            self.problem_text = problem
        else:
            self.problem_text = ""

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _fill_node(self, op_class, prompt, mode=None, **extra_kwargs):
        fill_kwargs = {"context": prompt, "llm": self.llm}
        if mode:
            fill_kwargs["mode"] = mode
        fill_kwargs.update(extra_kwargs)
        node = await ActionNode.from_pydantic(op_class).fill(**fill_kwargs)
        return node.instruct_content.model_dump()


class Custom(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self, instruction):
        prompt = instruction + self.problem_text
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        return response["response"]


class Review(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self, pre_solution):
        prompt = REVIEW_PROMPT.format(problem=self.problem_text, solution=pre_solution)
        response = await self._fill_node(ReviewOp, prompt, mode="xml_fill")
        answer = response.get("revised_solution", "")
        return answer


class Reflect(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self, pre_solution: str):
        prompt = REFLECT_PROMPT.format(problem=self.problem_text, solution=pre_solution)
        response = await self._fill_node(ReflectOp, prompt, mode="xml_fill")
        reflection = response.get("reflection_text", "")
        return reflection


def run_code(code):
    try:
        global_namespace = {}
        disallowed_imports = [
            "os", "sys", "subprocess", "multiprocessing", "matplotlib", "seaborn", 
            "plotly", "bokeh", "ggplot", "pylab", "tkinter", "PyQt5", "wx", "pyglet"
        ]
        for lib in disallowed_imports:
            if f"import {lib}" in code or f"from {lib}" in code:
                return "Error", f"Prohibited import: {lib}"
        exec(code, global_namespace)
        if 'solve' in global_namespace and callable(global_namespace['solve']):
            result = global_namespace['solve']()
            return "Success", str(result)
        else:
            return "Error", "Function 'solve' not found"
    except Exception as e:
        tb_str = traceback.format_exc()
        return "Error", f"Execution error: {str(e)}\n{tb_str}"
    

class Programmer(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def exec_code(self, code, timeout=30):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            try:
                future = loop.run_in_executor(executor, run_code, code)
                result = await asyncio.wait_for(future, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                executor.shutdown(wait=False, cancel_futures=True)
                return "Error", "Code execution timed out"
            except Exception as e:
                return "Error", f"Unknown error: {str(e)}"

    async def code_generate(self, problem, analysis, feedback, mode):
        prompt = PYTHON_CODE_VERIFIER_PROMPT.format(
            problem=problem, analysis=analysis, feedback=feedback
        )
        response = await self._fill_node(CodeGenerateOp, prompt, mode, function_name="solve")
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def __call__(self, analysis: str = "None"):
        code = None
        output = None
        feedback = ""
        for i in range(3):
            code_response = await self.code_generate(self.problem_text, analysis, feedback, mode="code_fill")
            code = code_response.get("code")
            if not code:
                return "No code generated"
            status, output = await self.exec_code(code)
            if status == "Success":
                return f"After executing the following code written by llm agent.\n{code}\nWe have the following output: {output}"
            else:
                print(f"Execution error on attempt {i + 1}, error message: {output}")
                feedback = f"\nThe result of the error from the code you wrote in the previous round:\nCode: {code}\n\nStatus: {status}, {output}"
        return f"After executing the following code written by llm agent.\n{code}\nWe have the following output: {output}"


class ScEnsemble(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self, solutions: List[str]):
        answer_mapping = {}
        solution_text = ""
        for index, solution in enumerate(solutions):
            answer_mapping[chr(65 + index)] = index
            solution_text += f"{chr(65 + index)}: \n{str(solution)}\n\n\n"

        prompt = SC_ENSEMBLE_PROMPT.format(problem=self.problem_text, solutions=solution_text)
        response = await self._fill_node(ScEnsembleOp, prompt, mode="xml_fill")
        answer = response.get("solution_letter", "").strip().upper()
        
        if answer in answer_mapping:
            return solutions[answer_mapping[answer]]
        else:
            logger.warning(f"ScEnsemble returned an invalid letter '{answer}'. Defaulting to the first solution.")
            return solutions[0] if solutions else ""