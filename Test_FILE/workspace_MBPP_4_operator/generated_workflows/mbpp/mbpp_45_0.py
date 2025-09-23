# Workflow ID: mbpp_45_0
# Benchmark: mbpp
# Data Indices: [61]

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

        # Phase 1: Analyze and classify the problem
        analysis = await self.generate(
            instruction="""Analyze the problem description and classify it:
            - Identify the function name from the test cases
            - Determine the input/output types and relationships
            - Classify the problem type (e.g., list operations, math, string manipulation)
            - Highlight any ambiguities or missing details""",
            context=""
        )

        # Phase 2: Extract function name and infer input/output patterns
        function_details = await self.generate(
            instruction=f"""From the test cases, extract:
            - The exact function name
            - Input types and their structures
            - Expected output types and formats
            Based on analysis: {analysis}""",
            context=analysis
        )

        # Phase 3: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using Python's standard library:
                - Use built-in functions where applicable
                - Ensure the function name matches the test cases
                - Validate against the inferred input/output patterns
                Analysis: {analysis}
                Function Details: {function_details}""",
                context=function_details
            ),
            self.generate(
                instruction=f"""Generate a custom implementation:
                - Avoid using built-in functions if possible
                - Focus on algorithmic clarity
                - Ensure the function name matches the test cases
                Analysis: {analysis}
                Function Details: {function_details}""",
                context=function_details
            )
        )

        # Phase 4: Validate and select the best solution
        best_solution = await self.ensemble(
            instruction="""Evaluate the candidate solutions:
            - Check correctness against test cases
            - Prefer simpler, more Pythonic solutions
            - Ensure proper handling of edge cases
            Select the best-performing solution.""",
            contexts_list=candidates
        )

        # Phase 5: Iterative refinement if needed
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution against test cases:
                - Identify any errors or mismatches
                - Highlight missing edge cases
                Current solution: {best_solution}""",
                context=best_solution
            )
            if "error" not in validation.lower():
                break  # Exit loop if solution is valid
            best_solution = await self.revise(
                instruction=f"""Revise the solution to address issues:
                - Fix logical errors
                - Add missing edge case handling
                Issues: {validation}
                Current solution: {best_solution}""",
                context=best_solution
            )

        # Return the final solution
        return best_solution