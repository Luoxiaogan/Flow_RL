# ScoreFlow/scripts/mbpp/op_prompt.py

# 这个 Prompt 保持不变，因为它在不同任务中是通用的。
SC_ENSEMBLE_PROMPT = """
You are an expert code reviewer. Given a code generation task and several Python code solutions, your job is to determine the best one.
The code generation task is: {problem}

Here are the proposed solutions:
{solutions}

Carefully evaluate each solution based on correctness (passes all edge cases), efficiency (algorithmic complexity), and clarity (readability and Pythonic style).

In the "thought" field, provide a detailed explanation of your evaluation process and justify your choice.
In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the best code solution. Do not include any other text.
"""
# ----------------- 以下是新增/修改的内容 -----------------

# 用于 CodeFixOperator 的新 Prompt
CODE_FIX_PROMPT = """
You are an expert Python debugger. You are given a programming problem, a piece of code that failed to solve it, and the error message from the test execution. Your task is to analyze the error, identify the bug, and provide a corrected version of the code.
### Programming Problem
{problem}

### Flawed Code
```python
{code}
```

### Execution Error
```
{error_message}
```

### Your Task
1. In the "thought" field, provide a step-by-step analysis of the bug. Explain what caused the error and how your proposed fix will solve it.

2. In the "fixed_code" field, provide the complete, corrected Python code. The code must be a drop-in replacement for the original, containing only the function definition and necessary imports. Do not include any test cases or example usage.

Remember to maintain the original function name and signature.
"""

CUSTOM_CODE_GENERATE_INSTRUCTION = """
Please provide a complete and correct Python code solution.
Ensure the function name matches the problem's entry point.
Think step-by-step about potential edge cases and requirements.
"""

# 用于 Review Operator 的 Prompt
REVIEW_PROMPT = """
You are an expert code reviewer. Your task is to review the given code solution and identify any potential issues, bugs, or improvements needed.

### Programming Problem
{problem}

### Entry Point
The solution must use the function name: {entry_point}

### Code to Review
```python
{solution}
```

### Your Task
1. In the "thought" field, provide a comprehensive review including:
   - Analysis of correctness for all edge cases
   - Code quality and readability
   - Potential performance improvements
   - Any bugs or logical errors

2. In the "final_code" field, provide the reviewed and improved code. If the code is already perfect, return it as-is. Otherwise, fix any issues you identified.

Remember to maintain the original function signature.
"""

# 用于 FlexibleCustom Operator 的 Prompt  
FLEXIBLE_CUSTOM_PROMPT = """
You are an expert Python programmer implementing a custom code generation approach.

### Programming Problem
{problem}

### Entry Point
The solution must use the function name: {entry_point}

### Custom Instructions
{custom_instruction}

### Generation Pattern: {generation_pattern}
### Custom Strategies: {strategies}

### Previous Results (if any)
{previous_results}

### Your Task
1. In the "thought" field, explain your reasoning process following the specified generation pattern and strategies.

2. In the "code" field, provide the complete Python code solution following the custom approach.

3. In the "needs_refinement" field, indicate whether additional refinement iterations are needed (true/false).

4. In the "approach_notes" field, document any insights or notes about the approach taken.

Remember to follow the specified generation pattern and custom strategies while solving the problem.
"""