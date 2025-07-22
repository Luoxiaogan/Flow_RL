# ScoreFlow/scripts/mbpp/conditions.py

import random

# 为代码生成任务定制的多样化策略
META_PROMPTS = [
    # 1. 强调测试和修复
    "Your main goal is correctness. Use the 'Generate-Test-Fix' pattern. First, generate a single code solution. Then, use the CodeRunner operator to test it. If it fails, use the CodeFix operator with the error message to create a corrected version.",
    # 2. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble & Test' pattern. Generate at least two different code solutions using varied instructions, use ScEnsemble to select the best one, and then use CodeRunner to verify the final choice.",
    # 3. 强调迭代修复
    "Your main goal is iterative refinement. Use a loop with the 'Test-Fix' pattern. Generate an initial solution, then loop 2-3 times, using CodeRunner to test and CodeFix to repair it until it passes or the loop ends.",
    # 4. 强调简单高效
    "Your main goal is efficiency. Create the simplest possible effective workflow. This is likely a single, well-crafted `CustomCodeGenerate` call followed by a single `CodeRunner` test. This is a baseline strategy.",
    # 5. 强调深思熟虑的生成
    "Your main goal is thoughtful generation. Before generating the final code, use a `CustomCodeGenerate` call with an instruction to first outline the plan, algorithm, and edge cases in natural language. Then, use this plan to guide a second `CustomCodeGenerate` call to write the actual code."
]

# 为 MBPP 任务定制的 SFT System Prompt
SYSTEM_PROMPT = "You are an expert at creating Python workflow graphs to solve code generation problems. Your task is to generate Python code for a workflow using the provided operators like CustomCodeGenerate, CodeRunner, CodeFix, and ScEnsemble to produce a correct code solution."

# Python 脚本模板保持不变
PYTHON_START = '''import asyncio
from typing import List, Literal
from ScoreFlow.scripts.mbpp.operator_an import CodeRunnerResult
import ScoreFlow.scripts.mbpp.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''


# 主 Prompt，现在完全为代码生成和新 Operators 定制
START_PROMPT = '''You are an expert in designing AI workflows for code generation. Your objective is to generate a diverse and effective workflow graph in Python to solve a given programming problem. Instead of generating the same simple graph every time, you must explore different problem-solving structures using the operators provided.

**Workflow Design Patterns (for inspiration):**

To encourage diversity, consider these patterns. You can use them directly, combine them, or create your own novel structures.

1.  **Generate-Test-Fix:**
    *   The most fundamental pattern for code. Generate a single solution, test it, and if it fails, use the error to guide a fix.
    *   *Example*: 
        ```python
        code = await self.code_generate(instruction="Provide a straightforward solution.")
        test_result = await self.code_runner(code_to_test=code)
        if not test_result.is_correct:
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        return code
        ```

2.  **Iterative Refinement (Test-Fix Loop):**
    *   For complex problems, one fix may not be enough. Loop the Test-Fix cycle a few times.
    *   *Example*:
        ```python
        code = await self.code_generate(instruction="Initial attempt to solve the problem.")
        for _ in range(2): # Loop for refinement
            test_result = await self.code_runner(code_to_test=code)
            if test_result.is_correct:
                break
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        return code
        ```

3.  **Parallel Ensemble & Test:**
    *   Generate multiple independent solutions to guard against flawed initial reasoning. Select the best, then test it.
    *   *Example*:
        ```python
        solutions = [
            await self.code_generate(instruction="Solve using a recursive approach."),
            await self.code_generate(instruction="Solve using an iterative approach.")
        ]
        best_code = await self.sc_ensemble(solutions=solutions)
        # Optional: Test the winner
        # test_result = await self.code_runner(code_to_test=best_code)
        return best_code
        ```

**Base Template:**

<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        # --- Initialize your chosen operators here ---
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for code generation.
        The final return value of this function should be a string containing the correct Python code.
        """
        # --- YOUR DIVERSE WORKFLOW LOGIC GOES HERE ---
        # For example, a simple Generate-Test pattern:
        solution_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")
        test_result = await self.code_runner(code_to_test=solution_code)
        if not test_result.is_correct:
            # Handle failure if necessary
            pass
        return solution_code
</graph>

**Available Operators:**

Here are the operators you MUST use. Do not create new ones.

1.  **CustomCodeGenerate**:
    *   **Usage**: Generates Python code based on an instruction.
    *   **Signature**: `code_generate(instruction: str) -> str`
    *   **Example**: `initial_code = await self.code_generate(instruction="Generate a Python function to solve the problem.")`

2.  **CodeRunner**:
    *   **Usage**: Executes the provided code against a hidden set of test cases.
    *   **Signature**: `code_runner(code_to_test: str) -> CodeRunnerResult`
    *   **Returns**: An object `result` where you can check `result.is_correct` (boolean) and access `result.error_message` (string) if it fails.
    *   **Example**: `test_result = await self.code_runner(code_to_test=initial_code)`

3.  **CodeFix**:
    *   **Usage**: Takes a failing piece of code and its error message, then generates a corrected version.
    *   **Signature**: `code_fix(code: str, error_message: str) -> str`
    *   **Example**: `fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)`

4.  **ScEnsemble**:
    *   **Usage**: Evaluates multiple code solutions and selects the best one.
    *   **Signature**: `sc_ensemble(solutions: List[str]) -> str`
    *   **Example**: `best_code = await self.sc_ensemble(solutions=[code1, code2])`

5.  **FlexibleCustom (Advanced Operator)**:
    *   **Usage**: A flexible operator that supports various code generation patterns (incremental, test_driven, modular, recursive) with customizable strategies. Perfect for exploring diverse approaches without embedding problem-specific information.
    *   **Signature**: `flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str`
    *   **Configuration Options**:
        - `generation_pattern`: "incremental", "test_driven", "modular", or "recursive"
        - `strategies`: List of generation strategies like ["analyze_requirements", "handle_edge_cases", "optimize_solution"]
        - `max_refinements`: Maximum refinement iterations (default: 1)
        - `use_structured_output`: Whether to use structured output format (default: True)
    *   **Example 1 (Test-Driven)**:
        ```python
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem, 
                                                      generation_pattern="test_driven",
                                                      strategies=["understand_tests", "implement_minimum", "refactor"])
        code = await self.flexible_custom(custom_instruction="Focus on passing tests incrementally")
        ```
    *   **Example 2 (Modular)**:
        ```python
        self.flexible_custom_mod = operator.FlexibleCustom(self.config, self.problem,
                                                          generation_pattern="modular", 
                                                          strategies=["decompose_problem", "implement_helpers", "combine_solution"])
        modular_code = await self.flexible_custom_mod(custom_instruction="Break down into reusable functions")
        ```
    *   **Use Cases**:
        - Test-Driven: Write code to pass tests incrementally
        - Incremental: Build solution step by step
        - Modular: Decompose into helper functions
        - Recursive: Solve with recursive approaches

**Problem Input:**
The programming problem will be provided. Your generated graph **must not** contain any specific information from this problem (e.g., function names, variable values). The graph should be a general-purpose solver.

TASK: '''

END_PROMPT = '''

**Final Instructions:**

1.  **Embrace Diversity**: Your primary goal is to create a workflow that is **different** from a simple, single `code_generate` call. Use the design patterns as inspiration.
2.  **Be Logical**: The flow must be logical. The `CodeFix` operator requires an `error_message` from a failed `CodeRunner` call. Use `if not test_result.is_correct:` blocks correctly.
3.  **Use Control Flow**: You **must** use Python's `for` loops and `if/else` statements to create intelligent, reactive workflows. The complexity of the logic should match the pattern you are trying to implement.
4.  **Final Output**: The `run_workflow` function must always return a string containing the final Python code.
5.  **No Problem-Specifics**: Your final graph must be completely generic.

Now, output the optimized and diverse graph. Remember to enclose it in `<graph>` and `</graph>` tags.
'''