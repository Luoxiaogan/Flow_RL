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