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

# 工作流生成的开始提示
START_PROMPT = """Based on the following problem examples, create a general workflow using MetaGPT ActionNodes that can solve similar problems:

{prompt_text}

Create a workflow class called `InternBootcampWorkflow` that:
1. Uses appropriate operators to analyze and solve the problem
2. Handles different problem types flexibly
3. Ensures correct output format
4. Can be executed with MetaGPT

The workflow should inherit from the base Workflow class and use the predefined operators.
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

# Python执行的开始模板
PYTHON_START = """
# InternBootcamp Problem Solving Workflow
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from metagpt.workflow import Workflow
from metagpt.actions import ActionNode
"""

# Python执行的结束模板
PYTHON_END = """
# The workflow is ready to solve InternBootcamp problems
"""

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