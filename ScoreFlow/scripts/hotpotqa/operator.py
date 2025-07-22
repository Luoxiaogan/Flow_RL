import ast
import random
import sys
import traceback
from collections import Counter
from typing import Dict, List, Tuple, Union, Any

from tenacity import retry, stop_after_attempt, wait_fixed

from ScoreFlow.scripts.hotpotqa.operator_an import *
from ScoreFlow.scripts.hotpotqa.op_prompt import *
from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM
from metagpt.logs import logger
import re


class Operator:
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        self.llm = llm
        self.problem = problem
        # Convert problem to text format if it's a dictionary
        if isinstance(problem, dict):
            self.problem_text = str(problem)
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
    
class AnswerGenerate(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self) -> Tuple[str, str]:
        prompt = ANSWER_GENERATION_PROMPT.format(input=self.problem_text)
        response = await self._fill_node(AnswerGenerateOp, prompt, mode="xml_fill")
        answer = response.get("answer", "")
        thought = response.get("thought", "")
        final_response = thought + "\n So we have the final results: " +  answer  
        
        return final_response

class Review(Operator):
    def __init__(self, llm: LLM, problem: Union[Dict[str, Any], str] = None):
        super().__init__(llm, problem)

    async def __call__(self, pre_solution):
        
        prompt = REVIEW_PROMPT.format(problem=self.problem_text, solution=pre_solution)
        response = await self._fill_node(ReviewOp, prompt, mode="xml_fill")
        answer = response.get("revised_solution", "")

        return answer


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
        answer = response.get("solution_letter", "")
        answer = answer.strip().upper()
        
        return solutions[answer_mapping[answer]]


class FlexibleCustom(Operator):
    """
    Flexible custom operator that supports various reasoning patterns for multi-hop QA.
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
        super().__init__(llm)
        self.problem = problem
        self.reasoning_pattern = reasoning_pattern
        self.steps = steps or ["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        self.max_iterations = max_iterations
        self.use_structured_output = use_structured_output
    
    async def __call__(self, custom_instruction: str = "", previous_results: List[str] = None,
                       reasoning_pattern: str = None, steps: List[str] = None, 
                       max_iterations: int = None, use_structured_output: bool = None):
        """
        Execute the flexible custom operator for multi-hop reasoning.
        
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
        
        # Build previous context if available
        previous_context = ""
        if previous_results:
            previous_context = "\n\nPrevious Results:\n" + "\n---\n".join(previous_results)
        
        # Create the prompt
        prompt = FLEXIBLE_CUSTOM_PROMPT.format(
            problem=self.problem,
            custom_instruction=custom_instruction,
            config=str(config),
            previous_context=previous_context
        )
        
        if actual_use_structured_output:
            # Use structured output with Pydantic model
            response = await self._fill_node(FlexibleCustomOp, prompt, mode="xml_fill")
            
            # Format the response
            result = f"Thought: {response.get('thought', '')}\n\nSolution: {response.get('solution', '')}"
            
            # Add intermediate results if available
            if response.get('intermediate_results'):
                result += f"\n\nIntermediate Results: {response.get('intermediate_results')}"
            
            # Handle iteration logic for iterative patterns
            if actual_reasoning_pattern == "iterative" and response.get('needs_iteration', False):
                # If more iterations are needed and we haven't reached max, the workflow can call again
                result += f"\n\n[Iteration {config['iteration']}/{actual_max_iterations}] - More iterations needed"
            
            return result
        else:
            # Use unstructured output
            response = await self._fill_node(GenerateOp, prompt, mode="single_fill")
            return response.get("response", "")