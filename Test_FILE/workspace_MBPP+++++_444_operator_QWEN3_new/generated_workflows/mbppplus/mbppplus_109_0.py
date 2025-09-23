# Workflow ID: mbppplus_109_0
# Benchmark: mbppplus
# Data Indices: [264, 350, 351]

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

        # Step 1: Classify problem and extract constraints
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Identify the problem category (list operations, string manipulation, mathematical computation, combinatorics, etc.)
            2. Extract explicit and implicit constraints from function signature and description
            3. Determine expected input/output types and edge cases (empty inputs, single elements, boundary values, type mismatches)
            4. Note any algorithmic patterns suggested (mapping, filtering, dynamic programming, modular arithmetic, etc.)
            5. List 5-7 potential edge cases not shown in examples
            Format as structured JSON-like text with clear sections.""",
            context=""
        )

        # Step 2: Parallel solution drafting - generate 3 variants
        solution_variants = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a LITERAL solution that follows the visible test cases exactly.
                Problem classification: {classification}
                Focus on direct implementation without extra robustness.
                Return ONLY the function implementation with correct signature and necessary imports inside the function.
                Do NOT add comments, type hints, or extra text.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a DEFENSIVE solution that handles edge cases and type safety.
                Problem classification: {classification}
                Add checks for empty inputs, invalid types, boundary conditions.
                Return ONLY the function implementation with correct signature and necessary imports inside the function.
                Do NOT add comments, type hints, or extra text.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an OPTIMIZED solution focusing on algorithmic efficiency and mathematical shortcuts.
                Problem classification: {classification}
                Use optimal algorithms, avoid unnecessary operations, consider mathematical properties.
                Return ONLY the function implementation with correct signature and necessary imports inside the function.
                Do NOT add comments, type hints, or extra text.""",
                context=""
            )
        )

        # Step 3: Generate edge cases for validation
        edge_cases = await self.generate(
            instruction=f"""Based on the problem classification:
            {classification}
            
            Generate 5 comprehensive edge case test assertions that are NOT in the provided examples.
            Consider: empty inputs, single elements, duplicates, negative numbers, boundary values, type mismatches.
            Format as Python assert statements, one per line.""",
            context=""
        )

        # Step 4: Validate each solution variant against edge cases (simulated)
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate this solution against the edge cases:
                Solution:
                {variant}
                
                Edge Cases:
                {edge_cases}
                
                For each edge case, explain whether the solution handles it correctly.
                If any case fails, explain why and what needs to be fixed.
                Be brutally honest - this is for quality assurance.""",
                context=variant
            ) for variant in solution_variants]
        )

        # Step 5: Synthesize best solution using ensemble
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these variants:
            - Prioritize CORRECTNESS above all else
            - Then prioritize ROBUSTNESS (edge case handling)
            - Then prioritize EFFICIENCY
            - Maintain exact function signature and output format requirements
            - Do NOT add extra text, comments, or type hints
            - Ensure all necessary imports are inside the function
            - Return ONLY the final function implementation""",
            contexts_list=solution_variants
        )

        # Step 6: Format and clean final solution
        formatted_solution = await self.revise(
            instruction="""Strictly format this code:
            - Return ONLY the function implementation
            - Exact function name and signature as specified
            - All imports must be inside the function (if any)
            - No extra text, comments, or type hints
            - No wrapping in classes or additional functions
            - Ensure proper indentation and Python syntax
            - Remove any markdown code block markers""",
            context=final_solution
        )

        # Step 7: Final validation
        final_check = await self.generate(
            instruction=f"""Final validation:
            Solution:
            {formatted_solution}
            
            Edge Cases:
            {edge_cases}
            
            Does this solution correctly handle ALL edge cases while maintaining the exact required format?
            If not, what minimal changes are needed? If yes, return the solution unchanged.
            Return ONLY the final function implementation.""",
            context=formatted_solution
        )

        return final_check