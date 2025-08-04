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

Provide a structured critique for each dimension in the "thought" field, and provide the revised answer in your "revised_solution" field.

Example for the "thought" field:
- Logical correctness: [Your critique here]
- Accuracy of calculation: [Your critique here]
- Potential misunderstanding of the problem: [Your critique here]
- Level of Detail: [Your critique here]
"""

# ANSWER_GENERATION_PROMPT = """
# Think step by step and solve the problem.
# 1. In the "thought" field, explain your thinking process in detail.
# 2. In the "answer" field, provide the final answer concisely and clearly. The answer should be a direct response to the question, without including explanations or reasoning.
# Your task: {input}
# """


FLEXIBLE_CUSTOM_PROMPT = """
Given the question and passage: {problem}

{custom_instruction}

Configuration: {config}
{previous_context}

Apply the specified reasoning pattern and steps to solve this problem requiring discrete reasoning.

For discrete reasoning tasks, consider:
- Identifying numerical values and entities to count
- Determining what operations are needed (counting, arithmetic, comparison)
- Extracting relevant information systematically
- Performing calculations accurately
- Verifying your answer makes sense in context

In the "thought" field, explain your reasoning process according to the configured pattern and steps.
In the "solution" field, provide your numerical or textual answer clearly.
In the "needs_iteration" field, indicate if this pattern requires another iteration (only for iterative patterns).
In the "intermediate_results" field, capture any important calculations, counts, or comparisons made.

Remember to follow the reasoning pattern strictly and work through each configured step systematically.
"""

# 可以放在 op_prompt.py 中
FORMAT_ANSWER_PROMPT = """
You are a meticulous and precise Answer Formatting Agent.
Your task is to analyze the provided raw output from a problem-solving workflow and extract the single, core final answer.

You will be given the original problem for context, and the raw output from the workflow.

**Original Problem:**
{problem}

**Raw Workflow Output:**
---
{raw_result}
---

**Instructions:**
1.  Read the original problem to understand what is being asked.
2.  Analyze the "Raw Workflow Output" to find the information that directly answers the original problem.
3.  The raw output might contain thoughts, intermediate calculations, or multiple potential answers. Your job is to make the final, single best judgment.
4.  Your response MUST be a structured format. In the "final_answer" field, provide only the core answer, without any extra text, explanations, or pleasantries.

**Example 1:**
- Original Problem: "How many touchdowns were scored?"
- Raw Workflow Output: "Thought: I counted 4 touchdowns in the text. Final Count: 4"
- Your `final_answer` field should contain: "4"

**Example 2:**
- Original Problem: "Who won the game?"
- Raw Workflow Output: "The winner was the team from Boston, the Patriots."
- Your `final_answer` field should contain: "the Patriots"
"""