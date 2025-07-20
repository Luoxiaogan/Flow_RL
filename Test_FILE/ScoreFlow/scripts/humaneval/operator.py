import ast
import random
import sys
import traceback
from collections import Counter
from typing import Dict, List, Tuple

from ScoreFlow.scripts.humaneval.operator_an import *
from ScoreFlow.scripts.humaneval.op_prompt import *
from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM
from metagpt.logs import logger
import re
from enum import Enum
import json

class CodeDataset(Enum):
    HUMAN_EVAL = "HumanEval"
    MBPP = "MBPP"

def extract_test_cases_from_jsonl(entry_point: str, dataset: CodeDataset = CodeDataset.HUMAN_EVAL):
    if dataset == CodeDataset.HUMAN_EVAL.value:
        # This function is not needed for HumanEval as we'll use the test field from the problem
        return None
        # Retain the original hardcoded test cases
        hardcoded_cases = {
            "find_zero": "",
            "decode_cyclic": "",
            "decode_shift": "",
            "by_length": "",
            "add": "",
            "triangle_area": "",
            "correct_bracketing": "",
            "solve": "",
            "sum_squares": "",
            "starts_one_ends": "",
        }
    elif dataset == CodeDataset.MBPP.value:
        # This file path is not used in our implementation
        return None
        hardcoded_cases = {
            "remove_odd": "",
            "replace_spaces": "",
            "snake_to_camel": "",
            "Split": "",
            "swap_List": "",
            "square_Sum": "",
            "sort_sublists": "",
            "unique_sublists": "",
        }
    return None



def test_case_2_test_function(solution: str, test_case: str, entry_point: str):
    tester_function = f"""
{solution}


def check(candidate):
    {test_case}

def test_check():
    check({entry_point})

test_check()
"""
    return tester_function



class Operator:
    def __init__(self, llm: LLM):
        self.llm = llm

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
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = "You have the following task: " + problem["prompt"]

    async def __call__(self, instruction):
        prompt = instruction + self.problem
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        return response["response"]
    
class CustomCodeGenerate(Operator):
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = "You have the following task: " + problem["prompt"]
        self.entry_point = problem["entry_point"]

    async def __call__(self, instruction):
        prompt = instruction + self.problem + CustomCodeGenerate_PROMPT
        response = await self._fill_node(GenerateOp, prompt, mode="code_fill", function_name=self.entry_point)
        return response['response']

class CodeRunner(Operator):
    """Executes code against test cases and returns results."""
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.test_code = problem.get("test", "")
        self.entry_point = problem["entry_point"]

    def exec_code(self, solution, test_code):
        # Use the shared unsafe_execute function from utils
        from ScoreFlow.scripts.utils.code_executor import unsafe_execute
        import multiprocessing
        
        # Extract test assertions from the test code
        test_lines = test_code.strip().split('\n')
        test_assertions = [line.strip() for line in test_lines if line.strip().startswith('assert')]
        
        if not test_assertions:
            return {"error": "No test assertions found", "status": "failed"}
        
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=unsafe_execute,
            args=(solution, test_assertions, result_queue)
        )
        
        process.start()
        process.join(timeout=30)  # 30 second timeout
        
        if process.is_alive():
            process.terminate()
            process.join()
            return {"error": "Execution timed out", "status": "failed"}
        
        if process.exitcode != 0:
            return {"error": f"Process exited with code {process.exitcode}", "status": "failed"}
        
        try:
            status, message = result_queue.get_nowait()
            if status == "success":
                return {"status": "passed", "message": "All tests passed"}
            else:
                return {"error": message, "status": "failed"}
        except multiprocessing.queues.Empty:
            return {"error": "No result from execution", "status": "failed"}
    
    async def __call__(self, solution):
        result = self.exec_code(solution, self.test_code)
        if result["status"] == "passed":
            return "PASSED"
        else:
            # Return detailed error information for CodeFix to use
            return f"FAILED: {result['error']}"

class CodeFix(Operator):
    """Analyzes failed code and error messages to generate a corrected version."""
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = "You have the following task: " + problem["prompt"]
        self.entry_point = problem["entry_point"]

    async def __call__(self, solution, error_message):
        prompt = CODE_FIX_PROMPT.format(
            problem=self.problem,
            solution=solution,
            error_message=error_message,
            entry_point=self.entry_point
        )
        response = await self._fill_node(CodeFixOp, prompt, mode="xml_fill")
        return response.get("fixed_code", "")

class Review(Operator):
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem["prompt"]
        self.entry_point = problem["entry_point"]

    async def __call__(self, solution):
        
        prompt = REVIEW_PROMPT.format(problem=self.problem, entry_point=self.entry_point, solution=solution)
        response = await self._fill_node(ReviewOp, prompt, mode="xml_fill")
        answer = response.get("final_code", "")
        
        return answer

class ScEnsemble(Operator):

    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = "You have the following task: " + problem["prompt"]

    async def __call__(self, solutions: List[str]):
        answer_mapping = {}
        solution_text = ""
        for index, solution in enumerate(solutions):
            answer_mapping[chr(65 + index)] = index
            solution_text += f"{chr(65 + index)}: \n{str(solution)}\n\n\n"

        prompt = SC_ENSEMBLE_PROMPT.format(problem=self.problem, solutions=solution_text)
        response = await self._fill_node(ScEnsembleOp, prompt, mode="xml_fill")
        answer = response.get("solution_letter", "")
        answer = answer.strip().upper()
        
        return solutions[answer_mapping[answer]]