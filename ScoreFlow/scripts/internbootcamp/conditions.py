"""
InternBootcamp工作流生成条件和模板
"""

# 元提示列表 - 用于生成多样化的工作流
META_PROMPTS = [
    # 1. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble' pattern. Generate at least three different solutions using varied custom instructions, then use sc_ensemble to select the most consistent one. A final review is a good practice.",
    # 2. 强调迭代
    "Your main goal is iterative improvement. Use the 'Iterative Refinement' pattern. Create a simple initial solution, then apply the `review` operator at least twice to progressively enhance it.",
    # 3. 强调混合与创新
    "Your main goal is creativity and complexity. Combine at least two different design patterns. For example, start with a 'Parallel Ensemble', reflect on the winner, and then regenerate. Or, use conditional logic based on the reflection's content.",
    # 4. 强调效率 (生成简单工作流)
    "Your main goal is efficiency. Create the simplest possible effective workflow. This might be a single, well-crafted `custom` call, or a `custom` followed by a single `review`. Avoid unnecessary complexity.",
]

# 系统提示 - 用于SFT训练
SYSTEM_PROMPT = "You are an expert at creating Python workflow graphs to solve multi-step mathematical reasoning problems. Given a problem, generate the Python code for an effective workflow using provided operators like Custom, Review."


# 工作流生成的开始提示 - 使用预定义操作符
START_PROMPT_PREDEFINED = """Based on the following problem examples, create a general workflow using MetaGPT ActionNodes that can solve similar problems:

{prompt_text}

Create a workflow class called `InternBootcampWorkflow` that:
1. Uses the predefined operators (Custom, Review, ScEnsemble...) to analyze and solve the problem
2. Combines multiple operators for better results
3. Handles different problem types flexibly
4. Ensures correct output format
5. Can be executed with MetaGPT

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
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

4.  **FlexibleCustom (Advanced Operator)**:
    *   **Usage**: A flexible operator that supports various reasoning patterns (sequential, parallel, iterative, branching) with customizable steps. Allows for more diverse workflow generation without embedding problem-specific information.
    *   **Format**: `flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str`
    *   **Configuration Options**:
        - `reasoning_pattern`: "sequential", "parallel", "iterative", or "branching"
        - `steps`: List of reasoning steps like ["analyze", "plan", "solve", "verify"]
        - `max_iterations`: Maximum iterations for iterative patterns (default: 1)
        - `use_structured_output`: Whether to use structured output format (default: True)

The workflow should inherit from the base Workflow class and orchestrate these operators effectively.
"""

# 工作流生成的开始提示 - 使用FlexibleCustom操作符
START_PROMPT_FLEXIBLE = """Based on the following problem examples, create a general workflow using MetaGPT ActionNodes that can solve similar problems:

{prompt_text}

Create a workflow class called `InternBootcampWorkflow` that:
1. Uses the FlexibleCustom operator with custom reasoning patterns
2. Implements problem-specific logic through custom instructions
3. Can adapt reasoning patterns (sequential, iterative, parallel) based on problem type
4. Ensures correct output format
5. Can be executed with MetaGPT

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        # --- YOUR DIVERSE WORKFLOW LOGIC GOES HERE ---
        # For example, a simple one:
        solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
        return solution
</graph>

**Available Operators:**

**FlexibleCustom**:
    *   **Usage**: A flexible operator that supports various reasoning patterns (sequential, parallel, iterative, branching) with customizable steps. Allows for more diverse workflow generation without embedding problem-specific information.
    *   **Format**: `flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str`
    *   **Configuration Options**:
        - `reasoning_pattern`: "sequential", "parallel", "iterative", or "branching"
        - `steps`: List of reasoning steps like ["analyze", "plan", "solve", "verify"]
        - `max_iterations`: Maximum iterations for iterative patterns (default: 1)
        - `use_structured_output`: Whether to use structured output format (default: True)

The workflow should inherit from the base Workflow class and orchestrate these operators effectively.
"""

# 工作流生成的结束提示
END_PROMPT = """
Remember:
- The workflow should be general enough to handle various problem types
- Use the provided operators effectively
- Ensure proper error handling
- Format the output according to problem requirements
- The workflow will be executed in a MetaGPT environment
"""

# Python执行的开始模板 - 预定义操作符
PYTHON_START_PREDEFINED = """
# InternBootcamp Problem Solving Workflow with Predefined Operators
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.workflow import Workflow
from metagpt.actions import ActionNode
from ScoreFlow.scripts.internbootcamp.operator import Custom, Review, ScEnsemble, FlexibleCustom
"""

# Python执行的开始模板 - FlexibleCustom操作符
PYTHON_START_FLEXIBLE = """
# InternBootcamp Problem Solving Workflow with FlexibleCustom Operator
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.workflow import Workflow
from metagpt.actions import ActionNode
from ScoreFlow.scripts.internbootcamp.operator import FlexibleCustom
"""

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''

# 选择使用哪种工作流类型
def get_workflow_prompts(workflow_type="predefined"):
    """
    获取工作流生成的提示词
    
    Args:
        workflow_type: "predefined" 使用预定义操作符, "flexible" 使用FlexibleCustom操作符
    
    Returns:
        dict: 包含START_PROMPT和PYTHON_START的字典
    """
    if workflow_type == "predefined":
        return {
            "START_PROMPT": START_PROMPT_PREDEFINED,
            "PYTHON_START": PYTHON_START_PREDEFINED
        }
    elif workflow_type == "flexible":
        return {
            "START_PROMPT": START_PROMPT_FLEXIBLE,
            "PYTHON_START": PYTHON_START_FLEXIBLE
        }
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
