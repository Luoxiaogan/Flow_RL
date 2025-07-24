"""
InternBootcamp操作符的提示词定义
"""

# Standard prompts from GSM8K pattern
SC_ENSEMBLE_PROMPT = """
Given the question described as follows: {problem}
Several solutions have been generated to address the given question. Carefully go through every solutions, then determine the most accurate answer. They are as follows:
{solutions}

In the "thought" field, provide a detailed explanation of your thought process. In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the most accurate solution. Do not include any additional text or explanation in the "solution_letter" field.
"""

REVIEW_PROMPT = """
Given the question described as follows: {problem}
We already have one solution as follow: 
{solution}

Now you need to evaluate this solution very carefully, then give the revised solution. When you evaluate, you need to critique this solution based on four dimensions: "Logical correctness", "Accuracy of calculation", "Potential misunderstanding of the problem", and "Level of Detail". Unless the given solution is absolutely perfect, you should rewrite the solution based on your revision and given solution.

Provide a critique for each dimension in the "thought" field, and provide the revised answer in your "revised_solution" field.
"""

REFLECT_PROMPT = """
Given the question described as follows: {problem}
And a proposed solution:
{solution}

Your task is to act as a critical but constructive reviewer. Do not solve the problem or rewrite the solution. Instead, provide a critical reflection on the given solution.

Consider the following aspects in your reflection:
- **Clarity and Simplicity**: Is the solution easy to understand? Could it be explained more simply?
- **Hidden Assumptions**: Does the solution make any unstated assumptions? Are these assumptions valid?
- **Potential Pitfalls**: Are there any edge cases or scenarios where this solution might fail?
- **Alternative Methods**: Can you think of a completely different way to approach this problem? Briefly describe it.

In the "thought" field, explain your reasoning. In the "reflection_text" field, provide your structured reflection.
"""

PYTHON_CODE_VERIFIER_PROMPT = """
You are a professional Python programmer. Your task is to write complete, self-contained code based on a given problem and output the answer. The code should include all necessary imports and dependencies, and be ready to run without additional setup or environment configuration.

Problem description: {problem}
Other analysis: {analysis}
{feedback}

Your code should:
1. Implement the calculation steps described in the problem.
2. Define a function named `solve` that performs the calculation and returns the result. The `solve` function should not require any input parameters; instead, it should obtain all necessary inputs from within the function or from globally defined variables.
3. `solve` function return the final calculation result.

Please ensure your code is efficient, well-commented, and follows Python best practices. The output should be limited to basic data types such as strings, integers, and floats. It is prohibited to transmit images or other file formats. The code output is intended for a text-based language model.
"""

FLEXIBLE_CUSTOM_PROMPT = """
Given the problem: {problem}

{custom_instruction}

Configuration: {config}
{previous_context}

Apply the specified reasoning pattern and steps to solve this problem. 

In the "thought" field, explain your reasoning process according to the configured pattern and steps.
In the "solution" field, provide your solution.
In the "needs_iteration" field, indicate if this pattern requires another iteration (only for iterative patterns).
In the "intermediate_results" field, capture any important intermediate findings or calculations.

Remember to follow the reasoning pattern strictly and work through each configured step systematically.
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