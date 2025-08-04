SC_ENSEMBLE_PROMPT = """
Given the mathematical problem described as follows: {problem}
Several solutions have been generated using different approaches or proof techniques. Carefully analyze each solution for mathematical rigor, correctness, and completeness. They are as follows:
{solutions}

In the "thought" field, provide a detailed mathematical analysis comparing the solutions, noting their strengths, weaknesses, and validity. Consider factors like:
- Logical correctness and proof structure
- Mathematical rigor and formality
- Completeness of the argument
- Elegance and insight of the approach

In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the most mathematically sound solution. Do not include any additional text or explanation in the "solution_letter" field.
"""

SC_ENSEMBLE_PROCESS_PROMPT = """
Several mathematical solutions have been generated to address the given problem. They are as follows:
{solutions}

Now we carefully evaluate these solutions from a mathematical perspective and identify the most rigorous and correct answer.
"""

REVIEW_PROMPT = """
Given the mathematical problem described as follows: {problem}
We already have one solution as follows: 
{solution}

Now you need to perform a rigorous mathematical review of this solution. Evaluate it based on the following dimensions:
1. **Logical Correctness**: Are all logical steps valid? Are there any gaps in reasoning?
2. **Mathematical Rigor**: Is the proof/solution formally correct? Are all cases considered?
3. **Clarity and Structure**: Is the mathematical exposition clear and well-organized?
4. **Completeness**: Are all aspects of the problem addressed? Are edge cases handled?
5. **Computational Accuracy**: Are all calculations correct? (if applicable)

Unless the given solution is mathematically perfect, you should provide an improved version that addresses any identified issues.

Provide a detailed critique in the "thought" field, and provide the mathematically rigorous revised solution in your "revised_solution" field.
"""

REFLECT_PROMPT = """
Given the mathematical problem described as follows: {problem}
And a proposed solution:
{solution}

Your task is to act as a mathematical critic and provide deep insights without solving the problem yourself. Focus on the mathematical aspects of the solution.

Consider the following in your reflection:
- **Mathematical Assumptions**: What assumptions (stated or unstated) does the solution make? Are they valid?
- **Alternative Approaches**: What other mathematical techniques or theorems could be applied to this problem?
- **Generalizations**: Can this solution be generalized to a broader class of problems?
- **Special Cases**: Are there special cases or boundary conditions that might challenge this solution?
- **Mathematical Connections**: How does this problem/solution relate to other areas of mathematics?
- **Proof Strategy**: If it's a proof, is the strategy optimal? Could a different approach be more elegant?

In the "thought" field, explain your mathematical analysis. In the "reflection_text" field, provide your structured mathematical reflection.
"""

PYTHON_CODE_VERIFIER_PROMPT = """
You are an expert mathematical programmer. Your task is to write complete, self-contained Python code to solve or verify a mathematical problem. The code should include all necessary imports and be ready to run without additional setup.

Problem description: {problem}
Mathematical analysis: {analysis}
{feedback}

Your code should:
1. Implement the mathematical solution algorithmically when possible
2. Define a function named `solve` that performs the calculation and returns the result
3. Use appropriate mathematical libraries (math, numpy, scipy, sympy) as needed
4. Include comments explaining the mathematical reasoning behind each step
5. Handle edge cases and provide meaningful outputs
6. For proofs or theoretical problems, implement verification procedures or computational examples

Mathematical libraries available:
- math: Basic mathematical functions
- numpy: Numerical computations
- scipy: Scientific computing
- sympy: Symbolic mathematics
- fractions: Exact fraction arithmetic
- decimal: High-precision decimal arithmetic
- itertools: Combinatorial functions

Please ensure your code is mathematically sound and follows best practices for mathematical computation.
"""

FLEXIBLE_CUSTOM_PROMPT = """
Given the mathematical problem: {problem}

{custom_instruction}

Configuration: {config}
{previous_context}

Apply the specified mathematical reasoning pattern and steps to solve this problem. 

Based on your configuration:
- If using "sequential" pattern: Work through each mathematical step methodically
- If using "parallel" pattern: Explore multiple mathematical approaches simultaneously
- If using "iterative" pattern: Refine your mathematical understanding progressively
- If using "branching" pattern: Consider different cases or conditions systematically

In the "thought" field, explain your mathematical reasoning process according to the configured pattern and steps.
In the "solution" field, provide your mathematical solution with appropriate rigor.
In the "needs_iteration" field, indicate if this pattern requires another iteration (only for iterative patterns).
In the "intermediate_results" field, capture any important mathematical insights, lemmas, or intermediate theorems.

Remember to:
- Use formal mathematical language where appropriate
- State any theorems or lemmas you apply
- Justify each significant step in your reasoning
- Maintain mathematical rigor throughout
"""