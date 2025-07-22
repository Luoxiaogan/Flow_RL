SC_ENSEMBLE_PROMPT = """
Given the question described as follows: {problem}
Several solutions have been generated to address the given question. Carefully go through every solutions, then determine the most accurate answer. They are as follows:
{solutions}

In the "thought" field, provide a detailed explanation of your thought process. In the "solution_letter" field, output only the single letter ID (A, B, C, etc.) corresponding to the most accurate solution. Do not include any additional text or explanation in the "solution_letter" field.
"""

SC_ENSEMBLE_PROCESS_PROMPT = """
Several solutions have been generated to address the given question. They are as follows:
{solutions}

Now we carefully evaluate these solutions and identify the most accurate answer.
"""

REVIEW_PROMPT = """
Given the question described as follows: {problem}
We already have one solution as follow: 
{solution}

Now you need to evaluate this solution very carefully, then give the revised solution. When you evaluate, you need to critique this solution based on four dimensions: "Logical correctness", "Accuracy of calculation", "Potential misunderstanding of the problem", and "Level of Detail". Unless the given solution is absolutely perfect, you should rewrite the solution based on your revision and given solution.

Provide a critique for each dimension in the "thought" field, and provide the revised answer in your "revised_solution" field.
"""

ANSWER_GENERATION_PROMPT = """
Think step by step and solve the problem.
1. In the "thought" field, explain your thinking process in detail.
2. In the "answer" field, provide the final answer concisely and clearly. The answer should be a direct response to the question, without including explanations or reasoning.
Your task: {input}
"""


FLEXIBLE_CUSTOM_PROMPT = """
Given the question and context: {problem}

{custom_instruction}

Configuration: {config}
{previous_context}

Apply the specified reasoning pattern and steps to answer this multi-hop question.

For multi-hop reasoning, consider:
- Identifying key facts from different parts of the context
- Making connections between related information
- Following logical chains to reach the answer
- Verifying your answer against the provided context

In the "thought" field, explain your reasoning process according to the configured pattern and steps.
In the "solution" field, provide your answer with supporting evidence from the context.
In the "needs_iteration" field, indicate if this pattern requires another iteration (only for iterative patterns).
In the "intermediate_results" field, capture any important facts or connections you've identified.

Remember to follow the reasoning pattern strictly and work through each configured step systematically.
"""