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
SYSTEM_PROMPT = "You are an expert mathematician specializing in advanced problem-solving. Generate Python workflow graphs to solve complex mathematical problems requiring deep reasoning, formal proofs, and sophisticated techniques. Use provided operators like Custom, Review, Reflect, and FlexibleCustom to create comprehensive solution workflows."


PYTHON_START = '''import asyncio
from typing import Literal
import ScoreFlow.scripts.high_level_math.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''


START_PROMPT = '''You objective is to generate a sophisticated and effective workflow graph for solving advanced mathematical problems. These problems often require deep mathematical insight, formal reasoning, and multiple solution strategies.

**Workflow Design Patterns (for advanced mathematics):**

Consider these patterns tailored for high-level mathematical problem-solving:

1.  **Theorem-Based Reasoning:**
    *   Start with problem analysis to identify applicable theorems, then apply them systematically with formal proofs.
    *   *Example*: `analysis = Custom -> theorem_application = Custom -> proof = Review -> verification = Reflect`

2.  **Multi-Method Verification:**
    *   Solve using one method, then verify using a completely different approach (e.g., algebraic then geometric).
    *   *Example*: `algebraic_solution = Custom -> geometric_verification = Custom -> synthesis = ScEnsemble`

3.  **Constructive Proof Pattern:**
    *   Build solutions incrementally with rigorous justification at each step.
    *   *Example*: `base_case = Custom -> inductive_step = FlexibleCustom(iterative) -> generalization = Review`

4.  **Case Analysis Pattern:**
    *   Systematically analyze different cases or conditions in the problem.
    *   *Example*: `case_identification = Custom -> [case1, case2, case3] = parallel Custom -> case_synthesis = Review`

5.  **Mathematical Exploration:**
    *   Explore problem structure, identify patterns, then formalize the solution.
    *   *Example*: `exploration = FlexibleCustom(steps=["explore_structure", "identify_patterns", "formalize"]) -> proof = Custom`

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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for advanced mathematical problem-solving.
        """
        # --- YOUR SOPHISTICATED WORKFLOW LOGIC GOES HERE ---
        # Example for high-level math:
        initial_analysis = await self.custom(instruction="Analyze the problem structure, identify key mathematical concepts, theorems, and potential solution strategies.")
        return initial_analysis
</graph>

**Available Operators (with mathematical focus):**

1.  **Custom**:
    *   **Mathematical Usage**: Generate rigorous proofs, derive formulas, or perform specific calculations.
    *   **Example**: `proof = await self.custom(instruction="Provide a formal proof using mathematical induction.")`

2.  **ScEnsemble**:
    *   **Mathematical Usage**: Compare different solution methods or proof approaches.
    *   **Example**: `best_proof = await self.sc_ensemble(solutions=[algebraic_proof, geometric_proof, combinatorial_proof])`

3.  **Review**:
    *   **Mathematical Usage**: Enhance mathematical rigor, fix logical gaps, or improve clarity.
    *   **Example**: `rigorous_proof = await self.review(pre_solution=initial_proof)`

4.  **Reflect**:
    *   **Mathematical Usage**: Identify assumptions, edge cases, or alternative approaches.
    *   **Example**: `mathematical_insights = await self.reflect(pre_solution=solution)`

5.  **FlexibleCustom**:
    *   **Mathematical Usage**: Implement complex proof strategies or multi-step derivations.
    *   **Configuration Examples**:
        - For proofs: `reasoning_pattern="sequential", steps=["setup", "base_case", "inductive_hypothesis", "inductive_step", "conclusion"]`
        - For problem exploration: `reasoning_pattern="iterative", steps=["simplify", "generalize", "solve_special_cases"]`
        - For verification: `reasoning_pattern="parallel", steps=["algebraic_check", "geometric_interpretation", "numerical_verification"]`

**Problem Input:**
We have the problem input below. Your generated graph **must not** contain any specific information from this problem. The graph should be a general-purpose advanced mathematical solver.

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