# Workflow ID: humaneval_41_0
# Benchmark: humaneval
# Data Indices: [101, 139]

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
        Universal workflow for code generation from specifications.
        Uses parallel hypothesis generation, simulated validation, and ensemble synthesis.
        """
        import asyncio
        import re

        # Step 1: Deep structural analysis - extract function signature, examples, and classify problem
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of the code generation problem:
            1. Extract the exact function name and parameters from the signature.
            2. List all examples from the docstring with input-output pairs.
            3. Infer the core transformation rule from input to output.
            4. Identify potential edge cases (empty input, single element, boundaries, malformed input).
            5. Classify the problem type (string, mathematical, list processing, algorithmic, etc.).
            6. Suggest 2-3 distinct implementation strategies (e.g., regex vs manual parsing, iterative vs recursive).
            7. Note any type constraints (int vs float, list vs tuple) from examples.
            8. Highlight any implicit requirements not explicitly stated.
            Format as a structured markdown report with clear sections.""",
            context=""
        )

        # Step 2: Parallel generation of solution hypotheses using different strategies
        strategy_prompts = [
            """Implement the solution using the most straightforward, readable approach.
            Prioritize clarity and direct mapping to examples. Handle edge cases explicitly.
            Use built-in functions and standard library where appropriate.
            Ensure function name and return type match exactly.""",
            
            """Implement the solution using an optimized or clever approach that minimizes operations.
            Look for patterns that allow mathematical shortcuts or efficient data structures.
            Still handle all edge cases and match examples exactly.""",
            
            """Implement the solution using a robust, defensive programming style.
            Add explicit checks for edge cases and input validation.
            Use verbose variable names and comments to explain logic.
            Ensure perfect alignment with all examples."""
        ]

        # Generate multiple solution hypotheses in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on the problem analysis:
                {analysis}

                {prompt}

                Return ONLY the Python function code with correct signature.
                No explanations, no imports, no extra text.""",
                context=analysis
            ) for prompt in strategy_prompts]
        )

        # Step 3: Simulated validation and revision for each solution
        validated_solutions = []
        for i, solution in enumerate(solution_attempts):
            # Revise each solution by simulating test validation
            validated = await self.revise(
                instruction=f"""Act as a strict test validator for the generated code:
                1. Check if function name matches ENTRY POINT exactly.
                2. Verify return type matches examples (int vs float, list vs tuple, etc.).
                3. Mentally execute against all provided examples - does output match exactly?
                4. Test edge cases: empty input, single element, boundary values, malformed input.
                5. Fix any discrepancies found. Add necessary edge case handling.
                6. Ensure no over-engineering - implement exactly what's specified.
                7. Return ONLY the corrected Python function code, nothing else.
                
                Problem Analysis for context:
                {analysis}""",
                context=solution
            )
            validated_solutions.append(validated)

        # Step 4: Ensemble synthesis - select or merge the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates based on:
            1. Correctness: Must handle all examples and edge cases perfectly.
            2. Simplicity: Prefer straightforward, readable implementations.
            3. Robustness: Explicit edge case handling is valuable.
            4. Efficiency: When correctness is equal, prefer more efficient solutions.
            5. Exact match: Function name and return type must be perfect.
            
            If one solution is clearly superior, select it. If multiple are good, 
            merge the best aspects into a single optimal solution.
            
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=validated_solutions
        )

        # Step 5: Final polish and type verification
        polished_solution = await self.revise(
            instruction="""Final verification and polish:
            1. Double-check function name matches ENTRY POINT exactly.
            2. Verify return type matches all examples precisely.
            3. Ensure no extra imports or code outside the function.
            4. Remove any unnecessary comments or debug code.
            5. Format code cleanly with proper indentation.
            6. Return ONLY the final Python function code, nothing else.""",
            context=final_solution
        )

        return polished_solution