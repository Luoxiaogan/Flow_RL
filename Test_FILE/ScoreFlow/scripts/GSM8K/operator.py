import concurrent
import sys
import traceback
from typing import List, Union, Dict, Any
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

# ### 修改点：将所有硬编码的 'GSM8K' 改为小写的 'gsm8k' ###
from ScoreFlow.scripts.gsm8k.operator_an import (
    GenerateOp, CodeGenerateOp, ScEnsembleOp, ReviewOp, ReflectOp, FlexibleCustomOp
)
from ScoreFlow.scripts.gsm8k.op_prompt import (
    SC_ENSEMBLE_PROMPT, REVIEW_PROMPT, PYTHON_CODE_VERIFIER_PROMPT, REFLECT_PROMPT, FLEXIBLE_CUSTOM_PROMPT
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


class FlexibleCustom(Operator):
    """
    Flexible custom operator that supports various reasoning patterns and configurations.
    Allows workflows to define custom logic without embedding problem information in prompts.
    """
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None, 
                 reasoning_pattern: str = "sequential", 
                 steps: List[str] = None,
                 max_iterations: int = 1,
                 use_structured_output: bool = True):
        """
        Args:
            llm: Language model instance
            problem: Problem to solve
            reasoning_pattern: Type of reasoning (sequential, parallel, iterative, branching)
            steps: Custom steps to apply during reasoning
            max_iterations: Maximum iterations for iterative patterns
            use_structured_output: Whether to use structured output format
        """
        super().__init__(llm, problem)
        self.reasoning_pattern = reasoning_pattern
        self.steps = steps or ["analyze", "plan", "solve", "verify"]
        self.max_iterations = max_iterations
        self.use_structured_output = use_structured_output
    
    async def __call__(self, custom_instruction: str = "", previous_results: List[str] = None,
                       reasoning_pattern: str = None, steps: List[str] = None, 
                       max_iterations: int = None, use_structured_output: bool = None):
        """
        Execute the flexible custom operator.
        
        Args:
            custom_instruction: Additional custom instruction from workflow
            previous_results: Previous results for iterative/branching patterns
            reasoning_pattern: Override the reasoning pattern set in constructor
            steps: Override the steps set in constructor
            max_iterations: Override the max iterations set in constructor
            use_structured_output: Override the structured output setting
        """
        # Use passed parameters or fall back to instance attributes
        actual_reasoning_pattern = reasoning_pattern if reasoning_pattern is not None else self.reasoning_pattern
        actual_steps = steps if steps is not None else self.steps
        actual_max_iterations = max_iterations if max_iterations is not None else self.max_iterations
        actual_use_structured_output = use_structured_output if use_structured_output is not None else self.use_structured_output
        
        # Build configuration dictionary for prompt
        config = {
            "reasoning_pattern": actual_reasoning_pattern,
            "steps": actual_steps,
            "iteration": len(previous_results) + 1 if previous_results else 1,
            "max_iterations": actual_max_iterations
        }
        
        # Format previous results if any
        previous_context = ""
        if previous_results:
            previous_context = "\n\nPrevious analysis:\n" + "\n---\n".join(previous_results)
        
        # Create prompt using the flexible template
        prompt = FLEXIBLE_CUSTOM_PROMPT.format(
            problem=self.problem_text,
            custom_instruction=custom_instruction,
            config=str(config),
            previous_context=previous_context
        )
        
        # Use appropriate response model
        if actual_use_structured_output:
            response = await self._fill_node(FlexibleCustomOp, prompt, mode="xml_fill")
            
            # Handle different reasoning patterns
            if actual_reasoning_pattern == "iterative" and response.get("needs_iteration", False):
                # Recursive call for iterative patterns
                if len(previous_results or []) < actual_max_iterations - 1:
                    new_results = (previous_results or []) + [response.get("solution", "")]
                    return await self.__call__(custom_instruction, new_results, reasoning_pattern, steps, max_iterations, use_structured_output)
            
            return response.get("solution", "")
        else:
            # Use simple generation for non-structured output
            response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
            return response["response"]