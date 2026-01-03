# Workflow ID: mbppplus_99_0
# Benchmark: mbppplus
# Data Indices: [144, 113, 362]

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

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving.
        Dynamically adapts strategy based on problem classification.
        Uses parallel generation, revision, and ensemble selection.
        """
        import asyncio
        import re

        # Step 1: Deep problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Identify:
            1. Problem type: Is it mathematical, iterative/filtering, string-based, or algorithmic?
            2. Key operations: What core computations or transformations are required?
            3. Data types: What input/output types are involved (int, list, tuple, str, etc.)?
            4. Edge cases: What boundary conditions must be handled (empty inputs, zeros, negatives, etc.)?
            5. Output format: What exact return type and structure is expected?
            6. Algorithmic complexity: Is this a direct formula, a loop, recursion, or combinatorial problem?
            Provide a structured, detailed classification that will guide solution generation.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a Python solution using a FUNCTIONAL approach (list comprehensions, map/filter, etc.).
                Focus on conciseness and Pythonic style.
                Handle all identified edge cases.
                Match the exact function signature and return type specified.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a Python solution using an IMPERATIVE approach (explicit loops, conditionals).
                Focus on clarity and step-by-step logic.
                Handle all identified edge cases.
                Match the exact function signature and return type specified.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a Python solution using a MATHEMATICAL/DIRECT approach (formulas, minimal iteration).
                Focus on efficiency and mathematical insight.
                Handle all identified edge cases.
                Match the exact function signature and return type specified.""",
                context=problem_analysis
            )
        )

        # Step 3: Revise each solution for robustness and correctness
        revised_solutions = []
        for i, solution in enumerate(solution_attempts):
            revised = await self.revise(
                instruction=f"""Critically review and improve this solution:
                - Verify it handles ALL edge cases mentioned in the analysis
                - Ensure return type and structure exactly match requirements
                - Check for off-by-one errors, division by zero, type mismatches
                - Improve code clarity and add inline comments if helpful
                - Ensure imports are included if needed (inside function)
                - Remove any markdown, explanations, or extra text - keep ONLY the function implementation
                Original problem analysis: {problem_analysis}""",
                context=solution
            )
            revised_solutions.append(revised)

        # Step 4: Ensemble - select the best solution
        best_solution = await self.ensemble(
            instruction="""Select the single best solution from the candidates based on:
            1. Correctness: Most likely to pass all test cases including edge conditions
            2. Robustness: Best handling of boundary cases and error conditions
            3. Efficiency: Most computationally efficient approach
            4. Clarity: Most readable and maintainable code
            5. Format compliance: Strict adherence to required function signature and return type
            Return ONLY the selected solution code - no explanations or markdown.""",
            contexts_list=revised_solutions
        )

        # Step 5: Final validation and cleanup
        final_solution = await self.revise(
            instruction="""Final cleanup and validation:
            - Ensure output is ONLY the function implementation (no markdown, no explanations)
            - Verify function name and parameters exactly match specification
            - Confirm all necessary imports are included inside the function if used
            - Remove any test cases, print statements, or extra code
            - Ensure perfect Python syntax and PEP8 compliance
            - If any part is missing or malformed, reconstruct it based on problem requirements
            Return ONLY the clean, runnable Python function code.""",
            context=best_solution
        )

        # Step 6: Extract just the code block if wrapped in markdown
        # Use regex to extract code between