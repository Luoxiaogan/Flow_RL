import random

META_PROMPTS = [
    # 1. 强调反思
    "Your main goal is deep reflection. Use the 'Reflect and Regenerate' pattern. It's crucial to first create a solution, then critically reflect on it, and use that reflection to create a superior final answer.",
    # 2. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble' pattern. Generate at least three different solutions using varied custom instructions, then use sc_ensemble to select the most consistent one. A final review is a good practice.",
    # 3. 强调迭代
    "Your main goal is iterative improvement. Use the 'Iterative Refinement' pattern. Create a simple initial solution, then apply the `review` operator at least twice to progressively enhance it.",
    # 4. 强调混合与创新
    "Your main goal is creativity and complexity. Combine at least two different design patterns. For example, start with a 'Parallel Ensemble', reflect on the winner, and then regenerate. Or, use conditional logic based on the reflection's content.",
    # 5. 强调效率 (生成简单工作流)
    "Your main goal is efficiency. Create the simplest possible effective workflow. This might be a single, well-crafted `custom` call, or a `custom` followed by a single `review`. Avoid unnecessary complexity.",
]

# 新增：为GSM8K任务定制的SFT System Prompt
SYSTEM_PROMPT = "You are an expert at creating Python workflow graphs to solve multi-step mathematical reasoning problems. Given a problem, generate the Python code for an effective workflow using provided operators like Custom, Review, and Reflect."


PYTHON_START = '''import asyncio
from typing import Literal
import ScoreFlow.scripts.GSM8K.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''


START_PORMPT = '''You objective is to generate a diverse and effective workflow graph for solving mathematical problems. Instead of generating the same simple graph every time, you should explore different reasoning structures.

**Workflow Design Patterns (for inspiration):**

To encourage diversity, consider these patterns. You can use them directly, combine them, or create your own novel structures.

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

**Problem Input:**
We have the problem input below. Your generated graph **must not** contain any specific information from this problem. The graph should be a general-purpose solver.

Question: '''

END_PROMPT = '''

You need to notice:

**Final Instructions:**

1.  **Embrace Diversity**: Your primary goal is to create a workflow that is **different** from a simple, single-step call. Use the design patterns as inspiration. Combine operators in novel ways.
2.  **Be Logical**: The flow of your graph must be logical. The output of one operator should be a valid input for the next. For example, `ScEnsemble` requires a list of strings.
3.  **Use Loops and Control Flow**: Don't forget you can use Python's `for` loops (e.g., `for i in range(3)`) to generate multiple solutions for ensembling, or `if/else` for conditional logic.
4.  **Complexity**: The graph complexity should be between 3 and 8 operators/steps. A more complex graph might yield better results but risks information loss if not carefully designed.
5.  **Instruction Prompts**: Your `custom` operator prompts should encourage step-by-step thinking. **Do not** ask for multiple different answers in a single `custom` call; use a loop for that.
6.  **No Problem-Specifics**: Your final graph must be completely generic and free of any details from the problem description provided above.

Now, output the optimized and diverse graph. Remember to enclose it in `<graph>` and `</graph>` tags.

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
        solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        return solution'''

TEST_PROMPT = "A is 1, B is 2, What's A + B?"

NO_EXCEPTION_LIST = ['''.split(' ')''', '''int(''', '''self.loop.append''']

TIME_LIMIT_TEST = 60
TIME_LIMIT = 120
sim_threshold = 0.8

