import random

META_PROMPTS = [
    # 1. 强调深度推理和证明
    "Your main goal is rigorous mathematical reasoning. Use the 'Deep Analysis' pattern. Focus on formal proofs, theorem application, and step-by-step derivations. Multiple reflection cycles are encouraged for complex problems.",
    # 2. 强调多角度求解
    "Your main goal is comprehensive problem-solving. Use the 'Multi-Approach' pattern. Generate solutions using different mathematical techniques (algebraic, geometric, computational), then synthesize insights from all approaches.",
    # 3. 强调分解和构建
    "Your main goal is systematic decomposition. Use the 'Hierarchical Breakdown' pattern. Break complex problems into sub-problems, solve each component rigorously, then construct the final solution from these pieces.",
    # 4. 强调验证和检查
    "Your main goal is solution verification. Use the 'Prove and Verify' pattern. After solving, verify your answer through alternative methods, boundary conditions, or special cases. Mathematical rigor is paramount.",
    # 5. 强调创新和洞察
    "Your main goal is mathematical insight. Create elegant solutions by identifying key patterns or transformations. Use the 'Insight-Driven' approach: explore the problem structure before diving into calculations.",
]

# 为High Level Math任务定制的SFT System Prompt
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
from typing import Literal
import ScoreFlow.scripts.gsm8k.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''


START_PROMPT = '''You objective is to generate a sophisticated and effective workflow graph for solving advanced mathematical problems. These problems often require deep mathematical insight, formal reasoning, and multiple solution strategies.

**Workflow Design Patterns (for advanced mathematics):**

Consider these patterns tailored for high-level mathematical problem-solving:

1.  **Iterative Refinement:**
    *   Generate an initial solution, then use the `Review` operator one or more times to progressively improve it. This is good for complex problems where the first attempt might miss details.
    *   *Example*: `solution = Custom -> Review -> Review`

2.  **Parallel Ensemble (Fan-out/Fan-in):**
    *   Generate multiple independent solutions using loops and the `Custom` operator. Then, use `ScEnsemble` to pick the best one. This is robust against single-point failures in reasoning.
    *   *Example*: `solutions = [Custom, Custom, ...] -> ScEnsemble`

3.  **Reflect and Regenerate:**
    *   Generate a solution, use the new `Reflect` operator to critique it, and then use that reflection to guide a `Custom` or `Review` operator for a better solution. This mimics a meta-cognitive loop.
    *   *Example*: `solution = Custom -> reflection = Reflect -> final_solution = Custom(instruction="... based on the reflection: " + reflection)`

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
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        # --- YOUR DIVERSE WORKFLOW LOGIC GOES HERE ---
        # For example, a simple one:
        solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
        return solution
</graph>

**Available Operators:**

Here's an introduction to the operators you can use. Do not create new operators beyond this list.

1.  **Custom**:
    *   **Usage**: Generates a response based on a flexible instruction. This is your main tool for generating initial solutions or reasoning steps.
    *   **Format**: `custom(instruction: str) -> str`
    *   **Example**: `initial_solution = await self.custom(instruction="Solve the problem by breaking it down into smaller, manageable steps.")`

2.  **ScEnsemble**:
    *   **Usage**: Evaluates multiple solutions and selects the most accurate one.
    *   **Format**: `sc_ensemble(solutions: List[str]) -> str`
    *   **Example**: `best_solution = await self.sc_ensemble(solutions=solution_list)`

3.  **Review**:
    *   **Usage**: Critiques and rewrites a given solution to improve it.
    *   **Format**: `review(pre_solution: str) -> str`
    *   **Example**: `revised_solution = await self.review(pre_solution=initial_solution)`

4.  **Reflect (New Operator)**:
    *   **Usage**: Critically reflects on a solution's potential flaws, assumptions, or alternatives *without* rewriting it. The output is a piece of text that can be used to guide subsequent steps.
    *   **Format**: `reflect(pre_solution: str) -> str`
    *   **Example**: `reflection_text = await self.reflect(pre_solution=initial_solution)`
    *   **Use Case**: `final_answer = await self.custom(instruction=f"Given the initial solution and the following reflection: {reflection_text}. Now, provide a new, improved solution.")`

5.  **FlexibleCustom (Advanced Operator)**:
    *   **Usage**: A flexible operator that supports various reasoning patterns (sequential, parallel, iterative, branching) with customizable steps. Allows for more diverse workflow generation without embedding problem-specific information.
    *   **Format**: `flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str`
    *   **Configuration Options**:
        - `reasoning_pattern`: "sequential", "parallel", "iterative", or "branching"
        - `steps`: List of reasoning steps like ["analyze", "plan", "solve", "verify"]
        - `max_iterations`: Maximum iterations for iterative patterns (default: 1)
        - `use_structured_output`: Whether to use structured output format (default: True)
    *   **Example 1 (Sequential)**: 
        ```python
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem, 
                                                      reasoning_pattern="sequential",
                                                      steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"])
        solution = await self.flexible_custom(custom_instruction="Focus on systematic problem decomposition")
        ```
    *   **Example 2 (Iterative)**: 
        ```python
        self.flexible_custom_iter = operator.FlexibleCustom(self.config, self.problem,
                                                           reasoning_pattern="iterative", 
                                                           steps=["initial_approach", "refine", "finalize"],
                                                           max_iterations=3)
        refined_solution = await self.flexible_custom_iter(custom_instruction="Start with estimation then refine")
        ```
    *   **Use Cases**: 
        - Sequential: Step-by-step problem solving with defined stages
        - Parallel: Consider multiple approaches simultaneously
        - Iterative: Progressive refinement through multiple passes
        - Branching: Conditional reasoning based on intermediate results

**Problem Input:**
We have the problem input below. Your generated graph **must not** contain any specific information from this problem. The graph should be a general-purpose solver.

Question: '''

END_PROMPT = '''

You need to notice:

**Final Instructions for High-Level Mathematics:**

1.  **Mathematical Rigor**: Ensure your workflow promotes formal mathematical reasoning, not just numerical computation.
2.  **Proof Strategies**: Consider incorporating proof techniques like induction, contradiction, construction, or exhaustion.
3.  **Multiple Perspectives**: High-level problems often benefit from viewing them through different mathematical lenses.
4.  **Verification Focus**: Include steps to verify solutions through alternative methods or special case checking.
5.  **Complexity**: Workflows should be sophisticated enough to handle advanced topics (3-10 operators recommended).
6.  **Instruction Quality**: Your operator instructions should encourage:
    - Formal mathematical language
    - Clear logical progression
    - Explicit statement of theorems/lemmas used
    - Rigorous justification of each step
7.  **No Problem-Specifics**: Keep the workflow general and applicable to various high-level mathematical problems.

Now, output the optimized and sophisticated graph for high-level mathematical problem-solving. Remember to enclose it in `<graph>` and `</graph>` tags.

Here is the graph without any problem information: '''


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
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.custom(instruction="Solve this mathematical problem.")

        return solution'''

TEST_PROMPT = "Prove that sqrt(2) is irrational."

NO_EXCEPTION_LIST = ['''.split(' ')''', '''int(''', '''self.loop.append''']

TIME_LIMIT_TEST = 90
TIME_LIMIT = 180
sim_threshold = 0.8