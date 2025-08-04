import random

# 文件: ScoreFlow/scripts/gsm8k/conditions.py

META_PROMPTS = [
    # 1. 强调分步计算 (最核心的策略)
    "Your main goal is meticulous step-by-step calculation. Use the ArithmeticReasoning operator as the core of your workflow. Break down the problem into sequential calculation steps using Custom or FlexibleCustom.",
    # 2. 强调鲁棒性 (通用策略，但措辞本地化)
    "Your main goal is robustness. Use a 'Parallel Ensemble' pattern. Generate solutions using different numerical extraction or calculation ordering strategies, then use ScEnsemble to find the most consistent numerical answer.",
    # 3. 强调验证与审查 (通用策略，但措辞本地化)
    "Your main goal is solution verification. Generate an initial solution with ArithmeticReasoning, then use Review to double-check the logic, the numbers extracted, and the final calculation.",
    # 4. 强调高级模式 (通用策略)
    "Your main goal is comprehensive reasoning. Use FlexibleCustom with a sequential pattern like ['extract_variables', 'formulate_equation', 'solve_step_by_step', 'final_check'] to create a robust calculation chain.",
    # 5. 强调效率 (通用策略)
    "Your main goal is efficiency. Create a direct workflow that uses ArithmeticReasoning to solve the problem in the fewest steps possible."
]

# System prompt for DROP tasks
SYSTEM_PROMPT = """
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1.  A high-level description of the problem domain.
2.  A strictly defined set of callable software "Operators" that serve as your only building blocks.
3.  An illustrative example instance, provided solely to help you understand the abstract reasoning pattern.

Your generated output **must** be a single, parameterized Python function that represents a generic workflow. This function must be robust enough to work for any problem instance within the described domain.

Crucially, the skill you are developing must be transferable. You should be prepared to receive specifications for **entirely new problem domains and new sets of operators** in the future and apply the same rigorous process of abstraction and generalization.
"""

PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.drop.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It wraps the user-defined logic in `run_workflow` with a system-level
        formatter to ensure a standardized output.
        """
        TIMEOUT = {time}

        try:
            # 1. Execute the LLM-generated workflow to get the raw, logical result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)

            # 2. Instantiate and call the system-level FormatAnswer operator.
            formatter = operator.FormatAnswer(self.llm, self.problem)
            formatted_result = await formatter(raw_result=raw_result)
            
            return formatted_result

        except asyncio.TimeoutError:
            # Handle workflow execution timeout gracefully.
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            # Handle other potential errors during workflow execution.
            import traceback
            # 错误详情在这里被定义和使用，不暴露给外部.format()
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{escaped_error_details}}"
'''

START_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **GSM8k benchmark**. These are grade-school math word problems. The task requires understanding the problem statement, extracting numerical values and their relationships, and performing a sequence of arithmetic calculations to arrive at a final numerical answer.

### 2. Available Operators & Building Blocks
Here's an introduction to the operators you must use. These are all you can use; do not create new operators.

**1. Custom:**
- **Description:** A highly flexible operator for executing a specific, non-standard instruction as a single step within a larger workflow. Use it for intermediate tasks like reformatting text, summarizing, or when no other specialized operator fits.
- **Example Usage:** To get a general solution, you can use `await self.custom(instruction="Think step-by-step and solve the problem.")`
- **Format:** `await self.custom(instruction: str) -> str`

**2. CountingReasoning:**
- **Description:** A specialized expert for **counting** tasks.
- **Output:** A structured response containing a 'thought' process and a final integer 'count'.
- **Format:** `await self.counting_reasoning() -> str`

**3. ArithmeticReasoning:**
- **Description:** A specialized expert for **arithmetic** tasks.
- **Output:** A structured response containing a 'thought' process, the 'equation', and the final numerical 'result'.
- **Format:** `await self.arithmetic_reasoning() -> str`

**4. ComparisonReasoning:**
- **Description:** A specialized expert for **comparison** and **sorting** tasks.
- **Output:** A structured response containing a 'thought' process and a 'result' (which can be a single item or an ordered list).
- **Format:** `await self.comparison_reasoning() -> str`

**5. Review:**
- **Description:** A meta-operator that **critiques and refines** a previous solution to improve its quality and correctness.
- **Format:** `await self.review(pre_solution: str) -> str`

**6. ScEnsemble:**
- **Description:** A meta-operator that **evaluates multiple solutions** and selects the most consistent one through voting. Used to improve robustness.
- **Format:** `await self.sc_ensemble(solutions: List[str]) -> str`

**7. FlexibleCustom (Advanced Operator):**
- **Description:** A powerful **logic configurator** that executes a multi-step reasoning process without writing Python control flow. Define the logic by providing a list of `steps` and a `reasoning_pattern`.
- **Format:** `await self.flexible_custom(...)`
- **Key Parameters:** `reasoning_pattern`, `steps`, `custom_instruction`.


### 3. Your Task: Complete the `run_workflow` Method
Your task is to write the Python code for the `run_workflow` method within the provided template. You must **only** modify the logic inside this method. **Do not** change the `__init__` method or any other part of the class structure.

**Base Template:**
<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem = problem
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        
        # Create LLM instance from config
        self.llm = create(self.config)

        # All available operators are initialized here for your use.
        self.custom = operator.Custom(self.llm, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.llm, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.llm, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.llm, self.problem)
        self.review = operator.Review(self.llm, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.llm, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.llm, self.problem)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        # --- REPLACE THE EXAMPLE LOGIC BELOW WITH YOUR OWN ---
        # For example, a simple step-by-step solution:
        initial_thought = await self.custom(instruction="First, break down the problem and identify the main task.")
        final_result = await self.custom(instruction=f"Based on the initial thought: {initial_thought}, now solve the problem.")
        return final_result
</graph>

### 4. Critical Rules & Constraints

- **Structure & Syntax:**
    - The entire output must be a single Python code block wrapped in `<graph>...</graph>` tags.
    - The code **must** define a class: `class Workflow:`.
    - Do **not** write `import` statements. They are handled externally.
    - Do **not** define an `__call__` method. The execution framework handles this.
    - Do **not** write any code outside of the `class Workflow:` definition.

- **`__init__` Method:**
    - The class **must** contain an `__init__(self, config, problem)` method.
    - Inside `__init__`, you **must** initialize all the operators you intend to use in `run_workflow`.
    - **Efficiency Rule:** Only initialize the operators that are actually called in `run_workflow`.

- **`run_workflow` Method:**
    - The class **must** contain an `async def run_workflow(self):` method containing the core logic.
    - The value returned by this method should be the direct result (e.g., a number, a string). It will be automatically formatted by the system.

- **Logic & Strategy: The Principle of "Strategic Templates"**
    - The workflow you generate is a **strategic template**. It defines the **steps** and **high-level logic** to solve a class of problems.
    - **ALLOWED**: The `instruction` strings passed to operators (like `Custom`) **should** contain keywords and phrases distilled from the problem **type** or the illustrative **question**. This is how you define the strategy. For example, for a question about counting touchdowns, `instruction="Count the touchdowns"` is a GOOD, strategic instruction.
    - **FORBIDDEN**: The workflow **must not** contain any hardcoded **answers** or specific data copied directly from the problem's **passage/context**. For example, `return "2"` or `instruction="The passage mentions Calvin Johnson scored, so..."` are BAD, non-generic instructions.

- **Custom Operator Guideline:**
    - The `instruction` for the `Custom` operator should guide step-by-step thinking. Do not ask for multiple different answers in a single call (e.g., avoid "generate a few options").

### 5. Illustrative Example
Here are one or more concrete examples to illustrate the problem type. Your generated workflow should be a generic solution for this *type* of problem, not just the specific instances provided.
'''

# 实际上END_PROMPT没用了
END_PROMPT = '''

You need to notice:

**Ensure your graph is based on the given template and is correct to avoid runtime failures.** Do NOT import the modules operator and create, which have already been automatically imported. Do not load the operators not provided.

**Introducing multiple operators at appropriate points can enhance performance.** Consider Python's loops (for, list comprehensions) to generate multiple solutions to ensemble.

**Every operator(agent)'s output should contribute to the final return output, otherwise, do not use them.**

**The graph complexity may corelate with the problem complexity.** The graph complexity must between 3 and 8. Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution.

**AVOID conditional logic in your workflow!** Do not use if/elif statements checking problem content like 'if "count" in self.problem.lower()'. The specialized operators (CountingReasoning, ArithmeticReasoning, etc.) already handle problem type detection internally. Just use them directly or combine multiple operators and let ScEnsemble select the best result.

**As for the instruction prompt for custom operator. Your instruction prompt should focus on encouraging agent to think step by step. Do not ask agent to generate multiple (a few, some, etc) answers in one operator's instruction. Also note that different agents are independent, so do not use prompts like "generate another/alternative/different answer", "generate the first/second answer", etc.**

**Your output graph must be optimized and different from the given template graph. Do not output graph without modification!**

**Your output graph can not contain any information of the given problem due to project requirement. All the information of this problem will be given as input "problem" (self.problem) and other agents will execute this workflow.**

Only output the optimized Python code graph (remember to add <graph> and </graph> tags around your Python code, and the output can not contain any information of the given problem).

Your output must be valid Python code that can be executed. Do not output XML or any other format.

Here is the optimized Python workflow graph without any problem information: '''


# TEMP_AVOID = '''class Workflow:
#     def __init__(
#         self,
#         config,
#         problem
#     ) -> None:
#         self.problem = problem  # IMPORTANT: problem is a dictionary, not a string!
#         # If you need the problem as text, use self.problem_text:
#         self.problem_text = str(problem) if isinstance(problem, dict) else problem
#         self.config = create(config)
#         self.custom = operator.Custom(self.config, self.problem)
#         self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
#         self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
#         self.review = operator.Review(self.config, self.problem)
#         self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
#         self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
#         self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
#         self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

#     async def run_workflow(self):
#         """
#         This is a workflow graph.
#         """
#         solution = await self.answer_generate()
        
#         return solution'''


# TEST_PROMPT = "How many children are there? Note that you are given context: there are 3 children playing."

# NO_EXCEPTION_LIST = ['''.split(' ')''', '''int(''']

# TIME_LIMIT_TEST = 60
# TIME_LIMIT = 120
# sim_threshold = 0.75

