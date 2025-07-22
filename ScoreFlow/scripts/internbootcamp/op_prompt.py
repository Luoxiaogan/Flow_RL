"""
InternBootcamp操作符的提示词定义
"""

# 任务分析器提示词
TASK_ANALYZER_PROMPT = """Please analyze the following problem and identify its type, constraints, and requirements:

Problem:
{problem}

Analyze and provide:
1. Task type (logic_puzzle/math_puzzle/algorithm_problem/graph_theory/unknown)
2. A brief description of what the problem asks
3. List all constraints mentioned in the problem
4. List all output format requirements
5. Extract key elements like grid size, number ranges, etc.

Be thorough and precise in your analysis."""

# 策略规划器提示词
STRATEGY_PLANNER_PROMPT = """Based on the task analysis, create a solving strategy for this {task_type} problem:

Problem:
{problem}

Constraints:
{constraints}

Requirements:
{requirements}

Please provide:
1. Overall approach to solve this type of problem
2. Step-by-step solving procedure
3. Algorithms or techniques that should be used
4. Important considerations or edge cases

Make the strategy specific to this problem type while being systematic."""

# 问题求解器提示词
PROBLEM_SOLVER_PROMPT = """Solve the following problem using the provided strategy:

Problem:
{problem}

Approach:
{approach}

Steps to follow:
{steps}

Execute the solution step by step, showing your reasoning and intermediate results.
Provide the complete solution along with detailed explanation of your solving process."""

# 格式提取器提示词
FORMAT_EXTRACTOR_PROMPT = """Extract and format the answer according to the specified requirements:

Original Problem:
{problem}

Solution:
{solution}

Reasoning:
{reasoning}

Format Requirements:
{format_requirements}

Extract the final answer and format it exactly as required. Common formats include:
- [answer]content[/answer] for general answers
- Matrix format for grids (space-separated numbers)
- Dictionary format for coordinate-based answers
- List format for sequences

Ensure the answer is complete and follows the exact format specified."""

# 验证器提示词
VALIDATION_PROMPT = """Validate the solution against the problem constraints:

Problem:
{problem}

Solution:
{solution}

Formatted Answer:
{answer}

Constraints to check:
{constraints}

Verify that:
1. The solution satisfies all constraints
2. The answer is complete (no missing parts)
3. The format is correct
4. There are no logical errors

Report any issues found during validation."""

# 特定任务类型的额外提示
TASK_SPECIFIC_PROMPTS = {
    "sudoku": """Pay special attention to:
- Each row must contain all numbers 1-N exactly once
- Each column must contain all numbers 1-N exactly once
- Each region must contain all numbers 1-N exactly once
- The grid must be completely filled""",
    
    "kakuro": """Pay special attention to:
- Sum constraints for each run (horizontal and vertical)
- No repeated digits within the same run
- Only digits 1-9 are allowed
- All white cells must be filled""",
    
    "minesweeper": """Pay special attention to:
- Adjacent mine counts for each cell
- Total number of mines matches the given count
- Logical deduction from revealed numbers
- All mine positions must be identified""",
    
    "algorithm": """Pay special attention to:
- Algorithm correctness and efficiency
- Edge cases handling
- Output format requirements
- Problem-specific constraints""",
    
    "graph": """Pay special attention to:
- Graph properties (directed/undirected, weights)
- Connectivity constraints
- Valid edge definitions
- Output format for graph structures"""
}