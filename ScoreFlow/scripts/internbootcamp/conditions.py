"""
InternBootcamp工作流生成条件和模板
"""

# 元提示列表 - 用于生成多样化的工作流
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

# 系统提示 - 用于SFT训练
SYSTEM_PROMPT = "You are an expert at creating Python workflow graphs to solve multi-step mathematical reasoning problems. Given a problem, generate the Python code for an effective workflow using provided operators like Custom, Review, and Reflect."


# 工作流生成的开始提示 - 使用预定义操作符
START_PROMPT_PREDEFINED = """Based on the following problem examples, create a general workflow using MetaGPT ActionNodes that can solve similar problems:

{prompt_text}

Create a workflow class called `InternBootcampWorkflow` that:
1. Uses the predefined operators (Custom, Review, Reflect, Programmer, ScEnsemble) to analyze and solve the problem
2. Combines multiple operators for better results
3. Handles different problem types flexibly
4. Ensures correct output format
5. Can be executed with MetaGPT

Available operators:
- Custom: General-purpose operator for custom instructions
- Review: Reviews and revises a solution
- Reflect: Provides critical reflection on a solution
- Programmer: Generates and executes Python code
- ScEnsemble: Selects the best solution from multiple candidates

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

The FlexibleCustom operator supports:
- Different reasoning patterns: sequential, parallel, iterative, branching
- Custom steps for each pattern
- Structured or unstructured output
- Iterative refinement of solutions

The workflow should inherit from the base Workflow class and leverage FlexibleCustom's flexibility.
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
from ScoreFlow.scripts.internbootcamp.operator import Custom, Review, Reflect, Programmer, ScEnsemble
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

# Python执行的结束模板
PYTHON_END = """
# The workflow is ready to solve InternBootcamp problems
"""

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

# 任务特定的条件配置
TASK_CONDITIONS = {
    "default": {
        "focus": "General problem solving with emphasis on understanding requirements and applying appropriate strategies",
        "key_points": [
            "Problem analysis and comprehension",
            "Constraint identification", 
            "Strategy selection",
            "Solution validation"
        ]
    },
    "logic_puzzle": {
        "focus": "Logical reasoning and constraint satisfaction",
        "key_points": [
            "Grid or state representation",
            "Constraint propagation",
            "Deductive reasoning",
            "Solution verification"
        ]
    },
    "math_puzzle": {
        "focus": "Mathematical computation and optimization",
        "key_points": [
            "Numerical constraints",
            "Equation solving",
            "Optimization strategies",
            "Answer validation"
        ]
    },
    "algorithm_problem": {
        "focus": "Algorithmic thinking and implementation",
        "key_points": [
            "Algorithm design",
            "Complexity analysis",
            "Edge case handling",
            "Output formatting"
        ]
    }
}