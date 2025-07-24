"""
InternBootcamp工作流生成条件和模板
"""

# 元提示列表 - 用于生成多样化的工作流
META_PROMPTS = [
    """You are designing a general problem-solving workflow for various types of puzzles and challenges.
The workflow should be able to handle logic puzzles, math problems, algorithms, and other computational tasks.
Focus on creating a flexible approach that can adapt to different problem types.""",
    
    """Create a systematic workflow that can solve complex problems by:
1. Understanding the problem requirements
2. Identifying the problem type and constraints
3. Applying appropriate solving strategies
4. Formatting the answer correctly
The workflow should be modular and reusable.""",
    
    """Design a multi-step reasoning workflow that:
- Analyzes the given problem thoroughly
- Breaks down complex problems into manageable steps
- Uses appropriate algorithms or logical reasoning
- Validates the solution before returning
Make it general enough to handle various puzzle types.""",
    
    """Build a workflow that combines:
- Problem comprehension and analysis
- Strategic planning and execution
- Answer extraction and formatting
- Self-verification mechanisms
The workflow should work for puzzles, algorithms, and mathematical problems.""",
    
    """Create an adaptive problem-solving workflow that can:
- Recognize different types of challenges (logic, math, algorithm, etc.)
- Apply domain-specific solving techniques
- Handle various input/output formats
- Ensure answer correctness through validation."""
]

# 系统提示 - 用于SFT训练
SYSTEM_PROMPT = """You are an expert problem solver capable of handling various types of puzzles and challenges including logic puzzles (Sudoku, Minesweeper), mathematical puzzles (Kakuro), algorithmic problems, and graph theory problems. 

Your approach should be:
1. Carefully analyze the problem description and requirements
2. Identify the problem type and key constraints
3. Apply appropriate solving strategies
4. Format your answer according to the specified format
5. Verify your solution meets all requirements

Always pay attention to the exact output format required and ensure your answer is complete and correct."""

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