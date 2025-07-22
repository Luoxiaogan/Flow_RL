import random

META_PROMPTS = [
    # 1. 强调多步推理
    "Your main goal is step-by-step reasoning. Use the specialized reasoning operators (CountingReasoning, ArithmeticReasoning, ComparisonReasoning) based on the problem type. Combine them with Custom for extraction and final answer formatting.",
    # 2. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble' pattern. Generate multiple solutions using different reasoning approaches, then use sc_ensemble to select the most consistent answer.",
    # 3. 强调迭代改进
    "Your main goal is iterative improvement. Start with AnswerGenerate for a quick solution, then use Review to refine it based on the problem's complexity.",
    # 4. 强调混合方法
    "Your main goal is comprehensive reasoning. Use FlexibleCustom with different reasoning patterns (sequential for step-by-step, parallel for multiple approaches) combined with specialized operators.",
    # 5. 强调效率
    "Your main goal is efficiency. Create a simple but effective workflow using the most appropriate specialized operator (CountingReasoning, ArithmeticReasoning, or ComparisonReasoning) based on the problem type.",
]

# System prompt for DROP tasks
SYSTEM_PROMPT = "You are an expert at creating Python workflow graphs to solve reading comprehension and discrete reasoning problems. Given a problem, generate the Python code for an effective workflow using provided operators like CountingReasoning, ArithmeticReasoning, ComparisonReasoning, Custom, and Review."

PYTHON_START = '''import asyncio
from typing import Literal
import ScoreFlow.scripts.drop.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''

START_PROMPT = '''Your objective is to generate a Python workflow graph for solving reading comprehension and discrete reasoning problems. You must output valid Python code based on the following template (but you must modify it):

<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.answer_generate()
        
        return solution
</graph>


Here's an introduction to operators you can use: (these are all you can use, do not create new operators)
1. Custom:
Usage: Generates anything based on fixed input problem and modifiable instruction.
Format MUST follow: custom(instruction: str) -> str
You can modify the instruction prompt, such like "Can you break down the problem into smaller steps?", "Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?", "Explain how to solve the problem with clear reasoning for each step", etc. For example:
solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
The output can serve as the input of next operators or the final output.
2. AnswerGenerate:
Usage: Directly generate answer (including thought) to the given problem.
Format MUST follow: answer_generate() -> str
For example:
solution = await self.answer_generate()
The output can serve as the input of next operators or the final output.
3. ScEnsemble:
Usage: Evaluate every solutions, then select the best solution in the solution list.
Format MUST follow: sc_ensemble(solutions: List[str]) -> str
You can ensemble few solutions, for example:
ensembled_solution = await self.sc_ensemble(solutions=solution_list)
The output can serve as the input of next operators or the final output.
4. Review:
Usage: Given previous solution, Review operator reviews the previous solution to regenerate the solution.
Format MUST follow: review(pre_solution: str) -> str
pre_solution should be solution from previous operator, for example
rev_solution = await self.review(pre_solution=pre_solution)
The output can serve as the input of next operators or the final output.
5. CountingReasoning:
Usage: Specialized for counting tasks (counting events, entities, occurrences).
Format MUST follow: counting_reasoning() -> str
For example:
count_result = await self.counting_reasoning()
Use this when the problem requires counting items, events, or occurrences.
6. ArithmeticReasoning:
Usage: Specialized for arithmetic computations (addition, subtraction, multiplication).
Format MUST follow: arithmetic_reasoning() -> str
For example:
arithmetic_result = await self.arithmetic_reasoning()
Use this when the problem requires numerical calculations.
7. ComparisonReasoning:
Usage: Specialized for comparison tasks (finding max/min, sorting, comparing values).
Format MUST follow: comparison_reasoning() -> str
For example:
comparison_result = await self.comparison_reasoning()
Use this when the problem requires finding maximum, minimum, or comparing entities.
8. FlexibleCustom (Advanced Operator):
Usage: A flexible operator that supports various reasoning patterns (sequential, parallel, iterative, branching) with customizable steps. Perfect for complex discrete reasoning without embedding problem-specific information.
Format: flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str
Configuration Options:
- reasoning_pattern: "sequential", "parallel", "iterative", or "branching"
- steps: List of reasoning steps like ["extract_values", "identify_operation", "perform_calculation", "verify_result"]
- max_iterations: Maximum iterations for iterative patterns (default: 1)
- use_structured_output: Whether to use structured output format (default: True)
Example 1 (Sequential calculation):
self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem, 
                                              reasoning_pattern="sequential",
                                              steps=["identify_numbers", "determine_operation", "calculate_step_by_step", "check_answer"])
solution = await self.flexible_custom(custom_instruction="Focus on careful numerical extraction and computation")
Example 2 (Iterative refinement):
self.flexible_custom_iter = operator.FlexibleCustom(self.agent, self.problem,
                                                   reasoning_pattern="iterative", 
                                                   steps=["initial_count", "verify_completeness", "refine_answer"],
                                                   max_iterations=3)
refined_answer = await self.flexible_custom_iter(custom_instruction="Count carefully and double-check for missed items")
Use Cases:
- Sequential: Step-by-step calculations with verification
- Parallel: Compare multiple approaches to the same problem
- Iterative: Progressive refinement of counts or calculations
- Branching: Different paths based on problem type (counting vs arithmetic)


We have the problem input as follow. But your output graph can not contain any specific information of the this problem.
Question: '''

END_PROMPT = '''

You need to notice:

**Ensure your graph is based on the given template and is correct to avoid runtime failures.** Do NOT import the modules operator and create, which have already been automatically imported. Do not load the operators not provided.

**Introducing multiple operators at appropriate points can enhance performance.** Consider Python's loops (for, list comprehensions) to generate multiple solutions to ensemble.

**Every operator(agent)'s output should contribute to the final return output, otherwise, do not use them.**

**The graph complexity may corelate with the problem complexity.** The graph complexity must between 3 and 8. Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution.

**As for the instruction prompt for custom operator. Your instruction prompt should focus on encouraging agent to think step by step. Do not ask agent to generate multiple (a few, some, etc) answers in one operator's instruction. Also note that different agents are independent, so do not use prompts like "generate another/alternative/different answer", "generate the first/second answer", etc.**

**Your output graph must be optimized and different from the given template graph. Do not output graph without modification!**

**Your output graph can not contain any information of the given problem due to project requirement. All the information of this problem will be given as input "problem" (self.problem) and other agents will execute this workflow.**

Only output the optimized Python code graph (remember to add <graph> and </graph> tags around your Python code, and the output can not contain any information of the given problem).

Your output must be valid Python code that can be executed. Do not output XML or any other format.

Here is the optimized Python workflow graph without any problem information: '''


TEMP_AVOID = '''class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.answer_generate()
        
        return solution'''


TEST_PROMPT = "How many children are there? Note that you are given context: there are 3 children playing."

NO_EXCEPTION_LIST = ['''.split(' ')''', '''int(''']

TIME_LIMIT_TEST = 60
TIME_LIMIT = 120
sim_threshold = 0.75

