# Workflow ID: mbppplus_100_0
# Benchmark: mbppplus
# Data Indices: [335, 127]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for algorithmic problem-solving in Python.
        Handles list operations, tuple manipulations, arithmetic, and more.
        Dynamically adapts strategy based on problem type and inferred constraints.
        """
        import asyncio
        import re

        # Step 1: Classify problem type and extract key constraints
        problem_analysis = await self.generate(
            instruction="""Analyze the programming problem in depth:

1. Problem Type Classification:
   - Is this a list/tuple operation, string manipulation, mathematical computation, or data structure algorithm?
   - Does it involve mapping, filtering, transformation, or arithmetic?

2. Key Constraints Inference:
   - What are the expected input types and structures?
   - What is the required return type (list, tuple, set, etc.)?
   - Are there implied edge cases (empty inputs, duplicates, type mismatches)?
   - What assumptions are safe vs. risky?

3. Solution Strategy Options:
   - List 2-3 different approaches (e.g., dictionary mapping vs. list comprehension vs. imperative loop)
   - For each, note pros/cons regarding edge case handling and efficiency

4. Critical Edge Cases:
   - What boundary conditions must the solution handle?
   - What would cause the solution to fail?

Output your analysis in structured format with clear sections.""",
            context=""
        )

        # Step 2: Generate multiple solution candidates in parallel
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function solution based on this analysis:
{problem_analysis}

Requirements:
- Use EXACT function name and signature from problem
- Include necessary imports at top of function body
- Handle edge cases identified in analysis
- Return correct data type
- Code must be clean, efficient, and readable
- Add minimal comments only if essential for clarity

Output ONLY the function implementation in the required format.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an ALTERNATIVE Python function solution using a different approach:
{problem_analysis}

Requirements:
- Same function signature as original problem
- Different algorithmic strategy than first solution
- Explicitly handle edge cases mentioned in analysis
- Ensure type consistency and robustness
- Prioritize correctness over brevity

Output ONLY the function implementation in the required format.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a DEFENSIVE Python function solution focused on edge case handling:
{problem_analysis}

Requirements:
- Same function signature
- Add explicit checks for edge cases (empty inputs, type mismatches, etc.)
- Use try-except only if absolutely necessary
- Document assumptions with comments
- Prioritize robustness over elegance

Output ONLY the function implementation in the required format.""",
                context=""
            )
        )

        # Step 3: Revise each candidate against edge case checklist
        revised_candidates = []
        for i, candidate in enumerate(solution_candidates):
            revision = await self.revise(
                instruction=f"""Critically revise this solution:

{candidate}

Revision Checklist:
1. Does it match the EXACT function signature from the problem?
2. Does it handle empty inputs gracefully?
3. Does it preserve required data types (list vs tuple vs set)?
4. Does it handle duplicates correctly?
5. Does it work with single-element inputs?
6. Are there any type conversion errors?
7. Is the return type exactly as expected?
8. Are there any off-by-one errors or index issues?
9. Does it handle negative numbers or special values if applicable?
10. Is the code defensive against unexpected inputs?

If any issues are found, fix them while preserving the core logic.
Output ONLY the revised function implementation.""",
                context=candidate
            )
            revised_candidates.append(revision)

        # Step 4: Ensemble - select best solution or synthesize
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below, or synthesize a hybrid solution:

Evaluation Criteria:
1. Correctness: Most likely to pass all test cases including edge cases
2. Robustness: Best handling of boundary conditions and unexpected inputs
3. Simplicity: Cleanest, most readable code without unnecessary complexity
4. Type Safety: Strict adherence to required input/output types
5. Efficiency: Reasonable performance without premature optimization

If one solution is clearly superior, select it unchanged.
If multiple solutions have complementary strengths, create a synthesized version that combines the best elements.

Output ONLY the final function implementation in the required format (function name, imports, code).""",
            contexts_list=revised_candidates
        )

        # Step 5: Final sanitization - ensure output matches required format
        sanitized_solution = await self.revise(
            instruction="""Ensure this code matches the EXACT required output format:

Requirements:
- Must contain ONLY the function implementation
- Must include any necessary imports at the top of the function body
- Must use the EXACT function name from the original problem
- Must preserve parameter names and order
- Must not be wrapped in any class or outer function
- Must return the correct data type
- Remove any explanatory text, markdown, or extra formatting

If the code is already in correct format, return it unchanged.
If not, fix the formatting while preserving functionality.

Output ONLY the sanitized function code.""",
            context=final_solution
        )

        # Extract just the code block if it's wrapped in markdown
        code_match = re.search(r'