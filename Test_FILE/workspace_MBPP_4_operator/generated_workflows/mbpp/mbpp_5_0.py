# Workflow ID: mbpp_5_0
# Benchmark: mbpp
# Data Indices: [271]

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

        # Step 1: Extract function name and analyze problem
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the problem:
            - Identify the function name precisely
            - Summarize the task requirements
            - Highlight key operations and constraints
            - Note any ambiguities or edge cases""",
            context=""
        )

        # Step 2: Generate multiple solution candidates
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on simplicity and clarity:
                Problem Analysis: {initial_analysis}
                - Use basic Python constructs
                - Ensure readability
                - Handle edge cases explicitly""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on efficiency and compactness:
                Problem Analysis: {initial_analysis}
                - Optimize for performance
                - Use advanced Python features if applicable
                - Maintain correctness""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on robustness and error handling:
                Problem Analysis: {initial_analysis}
                - Include comprehensive error checks
                - Handle unexpected inputs gracefully
                - Ensure reliability""",
                context=initial_analysis
            )
        )

        # Step 3: Refine candidates
        refined_candidates = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity, correctness, and completeness. Address any ambiguities.",
                context=candidate
            ) for candidate in candidates]
        )

        # Step 4: Select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness: Must pass all test cases
            - Readability: Clear and maintainable code
            - Efficiency: Optimal performance without unnecessary complexity
            - Robustness: Handles edge cases effectively""",
            contexts_list=refined_candidates
        )

        # Step 5: Validate the final solution iteratively
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution against all test cases:
                Solution: {final_solution}
                - Check for syntax errors
                - Verify correctness
                - Identify missing edge cases""",
                context=final_solution
            )
            if "error" in validation.lower() or "fail" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix issues identified during validation: {validation}",
                    context=final_solution
                )
            else:
                break

        return final_solution