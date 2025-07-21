SC_ENSEMBLE_PROMPT = """
Given the question described as follows: {problem}
Several solutions have been generated to address the given question. Carefully go through every solutions, then determine the most accurate answer. They are as follows:
{solutions}

In the "thought" field, provide a detailed explanation of your thought process. In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the most accurate solution. Do not include any additional text or explanation in the "solution_letter" field.
"""

CustomCodeGenerate_PROMPT = """Note that you should think carefully based on four dimensions: "Logical correctness", "Consideration of all situations", "Potential misunderstanding of the problem", and "If the function name is the given entry_point"."""

REVIEW_PROMPT = """
Given the code problem and an initial solution, review the code to identify any logical errors, edge cases not handled, or improvements needed.

### Problem
{problem}

### Entry Point
The solution must use the function name: {entry_point}

### Initial Solution
{solution}

Analyze the solution across multiple dimensions:
1. Logical correctness
2. Handling of edge cases
3. Code efficiency
4. Following the problem requirements exactly
5. Using the correct function name (entry_point)

Provide your thought process and then the improved code.
"""

CODE_FIX_PROMPT = """
Given a code problem, a failed solution, and the error message from testing, analyze what went wrong and provide a corrected solution.

### Problem
{problem}

### Entry Point
The solution must use the function name: {entry_point}

### Failed Solution
{solution}

### Error Message
{error_message}

Please analyze:
1. What caused the error/test failure
2. What specific part of the code needs to be fixed
3. Any edge cases that weren't handled properly

Provide your analysis in the "analysis" field, and the corrected code in the "fixed_code" field. The fixed code should address all identified issues and pass the tests.
"""

REFLECTION_ON_PUBLIC_TEST_PROMPT = """
Given a code problem and a python code solution which failed to pass test or execute, you need to analyze the reason for the failure and propose a better code solution.: 
### problem
{problem}

### Code Solution
{solution}

### Execution Result
{exec_pass}

#### Failed Test Case
{test_fail}

Please provide a reflection on the failed test cases and code solution, followed by a better code solution without any additional text or test cases. Remember to keep the entry_point function name: {entry_point}. You MUST NOT give a code with dead loop!
"""

FLEXIBLE_CUSTOM_CODE_PROMPT = """
Given the problem: {problem}

Entry point function name: {entry_point}

{custom_approach}

Configuration: {config}
{previous_context}

Apply the specified generation pattern and strategies to create a code solution.

In the "thought" field, explain your reasoning process according to the configured pattern and strategies.
In the "code" field, provide your complete Python code solution with the correct function name.
In the "needs_refinement" field, indicate if this pattern requires another iteration (only for incremental patterns).
In the "approach_notes" field, capture insights about the approach and any design decisions.

Remember to:
1. Use the exact function name: {entry_point}
2. Follow the generation pattern strictly
3. Apply each strategy systematically
4. Write clean, efficient, and well-structured code
"""