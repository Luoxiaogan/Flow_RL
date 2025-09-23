# Workflow ID: mbpp_20_0
# Benchmark: mbpp
# Data Indices: [224]

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

        # Initial Analysis: Extract function name and task requirements
        initial_analysis = await self.generate(
            instruction="""Analyze the problem text to:
            1. Extract the function name from the assert statements.
            2. Identify the input parameters and expected output.
            3. Summarize the task requirements in natural language.
            Provide structured information.""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution attempts
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate a solution using list comprehensions.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate a solution using explicit loops.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate a solution using built-in functions.""",
                context=initial_analysis
            )
        )

        # Refinement and Validation: Improve and validate each candidate
        refined_candidates = []
        for candidate in candidates:
            refined = await self.revise(
                instruction=f"""Improve the following solution:
                - Ensure proper indentation and syntax.
                - Validate against the test cases.
                - Add necessary imports.
                Solution: {candidate}""",
                context=candidate
            )
            refined_candidates.append(refined)

        # Ensemble Selection: Choose the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Passing all test cases.
            2. Code clarity and readability.
            3. Efficient use of Python features.""",
            contexts_list=refined_candidates
        )

        return final_solution