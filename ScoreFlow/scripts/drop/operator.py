import ast
import random
import sys
import traceback
from collections import Counter
from typing import Dict, List, Tuple

from tenacity import retry, stop_after_attempt, wait_fixed

from ScoreFlow.scripts.drop.operator_an import *
from ScoreFlow.scripts.drop.op_prompt import *
from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM
from metagpt.logs import logger
import re


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
        self.problem = problem

    async def __call__(self, instruction):
        
        prompt = instruction + self.problem
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        
        return response["response"]


class CountingReasoning(Operator):
    """
    Specialized operator for counting tasks in DROP dataset.
    Handles counting occurrences, entities, events, etc.
    """
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

    async def __call__(self):
        instruction = """Analyze the given passage and question carefully to perform counting tasks.
        Focus on:
        1. Identifying what needs to be counted (events, entities, occurrences)
        2. Carefully scanning the passage for all instances
        3. Avoiding double-counting or missing instances
        4. Providing the exact count as the answer
        
        Problem: """
        
        prompt = instruction + self.problem
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        
        return response["response"]


class ArithmeticReasoning(Operator):
    """
    Specialized operator for arithmetic computations in DROP dataset.
    Handles addition, subtraction, and other mathematical operations.
    """
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

    async def __call__(self):
        instruction = """Solve this problem step by step using arithmetic reasoning.
        Focus on:
        1. Identifying all numerical values mentioned in the passage
        2. Understanding what arithmetic operation is needed (addition, subtraction, etc.)
        3. Performing calculations accurately
        4. Double-checking your arithmetic
        5. Providing the numerical result as the answer
        
        Problem: """
        
        prompt = instruction + self.problem
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        
        return response["response"]


class ComparisonReasoning(Operator):
    """
    Specialized operator for comparison tasks (max/min/sorting) in DROP dataset.
    Handles finding maximum, minimum, or ordering entities.
    """
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

    async def __call__(self):
        instruction = """Analyze the passage to perform comparison or sorting tasks.
        Focus on:
        1. Identifying all entities or values that need to be compared
        2. Extracting the comparison criteria (e.g., longest, highest, earliest)
        3. Systematically comparing all relevant entities
        4. Determining the maximum, minimum, or correct ordering
        5. Providing the answer clearly
        
        Problem: """
        
        prompt = instruction + self.problem
        response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
        
        return response["response"]

    
class AnswerGenerate(Operator):
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

    async def __call__(self) -> str:
        prompt = ANSWER_GENERATION_PROMPT.format(input=self.problem)
        response = await self._fill_node(AnswerGenerateOp, prompt, mode="xml_fill")
        answer = response.get("answer", "")
        thought = response.get("thought", "")
        final_response = thought + "\n So we have the final results: " +  answer  
        return final_response


class Review(Operator):
    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

    async def __call__(self, pre_solution):
        
        prompt = REVIEW_PROMPT.format(problem=self.problem, solution=pre_solution)
        response = await self._fill_node(ReviewOp, prompt, mode="xml_fill")
        answer = response.get("revised_solution", "")

        return answer


class ScEnsemble(Operator):

    def __init__(self, llm: LLM, problem: str = None):
        super().__init__(llm)
        self.problem = problem

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