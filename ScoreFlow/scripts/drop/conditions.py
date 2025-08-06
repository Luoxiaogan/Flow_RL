import random

META_PROMPTS = [
    # 2. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble' pattern. Generate multiple solutions using different reasoning approaches, then use sc_ensemble to select the most consistent answer.",
    # 3. 强调迭代改进
    "Your main goal is iterative improvement. Start with AnswerGenerate for a quick solution, then use Review to refine it based on the problem's complexity.",
    # 4. 强调混合方法
    "Your main goal is comprehensive reasoning. Use FlexibleCustom with different reasoning patterns (sequential for step-by-step, parallel for multiple approaches) combined with specialized operators.",
    # 5. 强调效率
    "Your main goal is efficiency. Create a simple but effective workflow using the most appropriate specialized operator (CountingReasoning, ArithmeticReasoning, or ComparisonReasoning) based on the problem type.",
]


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
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {time}

        try:
            # Execute the LLM-generated workflow to get the raw result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            
            # Return the raw result directly - answer extraction is now handled in handler
            return raw_result

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
The target domain is the **DROP benchmark**. Problems in this domain require both information extraction from a text passage and subsequent discrete reasoning. This reasoning often involves arithmetic (sums, differences), counting, and comparisons over numbers or items found in the text. The final answer can be a number, a date, or a specific span of text.

### 2. Available Operators & Building Blocks
Here's an introduction to the core reasoning operators you must use. They are all initialized and available as `self.operator_name`.

**1. Generate:**
- **Core Function:** **CREATE** information.
- **Description:** A general-purpose operator that generates new, unstructured text based on a strategic instruction and optional context from a previous step. It is the primary tool for analysis, reasoning, drafting solutions, and creative tasks.
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`

**2. Revise:**
- **Core Function:** **IMPROVE** information.
- **Description:** A meta-operator that critiques and refines a previous solution or text based on a specific instruction. It is essential for iterative improvement and self-correction.
- **Signature:** `await self.revise(instruction: str, context_to_revise: str) -> str`

**3. Summarize:**
- **Core Function:** **COMPRESS** information.
- **Description:** A specialized operator that condenses a potentially long text into its key points, focusing on aspects relevant to the original problem. Use this to manage context length and maintain focus in long reasoning chains.
- **Signature:** `await self.summarize(context_to_summarize: str) -> str`

**4. Ensemble:**
- **Core Function:** **DECIDE** on information.
- **Description:** A meta-operator that evaluates, compares, or synthesizes multiple candidate contexts based on a strategic instruction. It is the key to handling uncertainty and improving robustness.
- **Signature:** `await self.ensemble(instruction: str, contexts_to_ensemble: List[str]) -> str`


### 3. Your Task: Complete the `run_workflow` Method
Your task is to write the Python code for the `run_workflow` method within the provided template. You must **only** modify the logic inside this method. **Do not** change the `__init__` method.

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
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        # --- REPLACE THE EXAMPLE LOGIC BELOW WITH YOUR OWN DYNAMIC WORKFLOW ---
        # Example: A simple analysis and generation flow.
        analysis = await self.generate(instruction="First, analyze the original problem to understand its core requirements.")
        solution = await self.generate(instruction="Based on the analysis, now generate a step-by-step solution.", context=analysis)
        return solution
</graph>

### 4. Critical Rules & Constraints
Your generated workflow must be a robust, generic template. Adhere strictly to these rules:

**A. On Generality (The Core Principle):**
- **Your Goal:** You are creating a **strategic template**, not a one-off solution. The logic inside `run_workflow` must define the *steps* to solve a class of problems.
- **ALLOWED Content:** The `instruction` strings passed to operators **should** contain keywords and phrases distilled from the problem **type** or the illustrative **question**. This defines the strategy. (e.g., for a question about finding a difference, `instruction="Calculate the difference between the two values."` is GOOD).
- **FORBIDDEN Content:** The workflow **must not** contain hardcoded **answers** (e.g., `return "42"`) or specific data copied directly from the problem's **context/passage** (e.g., `instruction="Since the passage mentions John has 5 apples, ..."`).

**B. On Logic & Control Flow (Exposing the Topology):**
- **You ARE ENCOURAGED** to use Python's native control flow constructs (`if/else`, `for` loops, `asyncio.gather`) to build the logical topology of your solution.
- **Guideline for `if/else`:** Conditions for branching **must** be based on the **results of previous operator calls**. Do not parse `self.problem_text` directly in a condition.
    - **GOOD:** `analysis = await self.generate(...)` -> `if "math" in analysis:`
    - **BAD:** `if "how many" in self.problem_text:`
- **Guideline for Loops:** Consider using `for` loops to iterate a process (e.g., with `Revise`) or to process multiple items extracted from the context.

**C. On Operator Usage:**
- **Complexity:** The workflow should generally consist of **3 to 8 operator calls**.
- **Efficiency:** Ensure every operator call contributes meaningfully to the final returned value.

- **Final Output Rule:** Your response MUST contain **nothing** other than the Python code inside the `<graph>` tags. Do not add any introductory sentences, concluding remarks, or self-evaluations like "Why This Works". Your entire response should start with `<graph>` and end with `</graph>`.

---
**CODE TO COMPLETE**
---
<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        # --- YOUR PYTHON LOGIC GOES HERE. REPLACE THE EXAMPLE. ---
<graph>

### 5. Illustrative Example(s)
To help you understand the problem type, the following are one or more concrete examples.
Remember, your task is to create a workflow that solves this *class* of problem, not just these specific instances.

'''

END_PROMPT = '''.'''