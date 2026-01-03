# Workflow ID: mbppplus_80_0
# Benchmark: mbppplus
# Data Indices: [257, 40, 29]

import asyncio

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Deep problem analysis - extract semantics, types, patterns
        analysis = await self.generate(
            instruction="""Perform a comprehensive semantic analysis of this programming problem. Extract:
            1. Primary operation type (mathematical formula, recursive generation, iterative processing, pattern recognition, etc.)
            2. Input and output data types (list, tuple, int, bool, etc.) with nesting levels if applicable
            3. Key verbs and nouns in the task description that hint at the solution strategy
            4. Potential edge cases (empty inputs, single elements, extreme values, type boundaries)
            5. Any mathematical sequences, combinatorial patterns, or known formula references
            6. Whether this might be a 'trick' problem where the literal interpretation is misleading
            7. Expected computational complexity or efficiency constraints
            Structure your analysis as a detailed, categorized report.""",
            context=""
        )

        # Step 2: Parallel strategy generation - 4 specialized approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis: {analysis}
                Generate a solution assuming this is a MATHEMATICAL/FORMULAIC problem.
                - Look for closed-form expressions, algebraic identities, or number sequences
                - Consider polynomial, arithmetic, or geometric relationships
                - If parameters suggest sequence indices (like n), derive the general term
                - Return only the function implementation with necessary imports""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {analysis}
                Generate a solution assuming this is a RECURSIVE/COMBINATORIAL problem.
                - Consider tree traversal, backtracking, or Cartesian product generation
                - Handle nested structures with recursive helper functions if needed
                - Use generators or accumulators for combinatorial outputs
                - Return only the function implementation with necessary imports""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {analysis}
                Generate a solution assuming this is an ITERATIVE/DATA-STRUCTURE problem.
                - Use loops, comprehensions, or built-in methods for processing collections
                - Consider filtering, mapping, reducing, or set operations
                - Handle edge cases explicitly in code
                - Return only the function implementation with necessary imports""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {analysis}
                Generate a solution assuming this is a TRICK/PATTERN-RECOGNITION problem.
                - Question literal interpretations of function names or descriptions
                - Look for meta-patterns (e.g., output depends on input length rather than content)
                - Consider mathematical coincidences or structural properties
                - Return only the function implementation with necessary imports""",
                context=analysis
            )
        ]
        
        # Execute all strategies in parallel
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Step 3: Ensemble selection - choose best candidate based on multiple criteria
        selected_solution = await self.ensemble(
            instruction="""Select the single best solution from the candidates based on:
            1. TYPE CONSISTENCY: Does it match inferred input/output types from analysis?
            2. EDGE CASE HANDLING: Does it explicitly or implicitly handle empty/single/boundary cases?
            3. SIMPLICITY: Prefer solutions with fewer operations and clearer logic (Occam's Razor)
            4. SEMANTIC ALIGNMENT: Does the approach match the problem's core operation type?
            5. ROBUSTNESS: Does it avoid assumptions about input validity?
            Return ONLY the selected solution code, nothing else.""",
            contexts_list=strategy_candidates
        )

        # Step 4: Self-validation revision - simulate test cases mentally
        validated_solution = await self.revise(
            instruction=f"""Revise this solution by mentally simulating edge cases:
            1. If input is empty (e.g., [], (), 0, ""), what does the code return? Is it correct?
            2. If input is single element, does it handle correctly?
            3. For numerical inputs, test with 0, 1, negative numbers if applicable
            4. For collections, test with nested structures, mixed types, duplicates
            5. Does the return type exactly match expectations (list vs tuple vs set)?
            6. Are there any potential division by zero, index out of bounds, or type errors?
            Fix any issues found. If no issues, return the solution unchanged.
            Return ONLY the final function implementation with necessary imports.""",
            context=selected_solution
        )

        # Step 5: Final summarization - ensure pure function format
        final_code = await self.summarize(
            instruction="""Extract ONLY the function implementation from this text.
            Requirements:
            - Must start with 'def function_name(...):'
            - Include any necessary imports at the top
            - No explanatory text, comments, or markdown
            - Preserve exact function signature from problem
            - Return the raw code as a string""",
            context=validated_solution
        )

        return final_code