# Workflow ID: mbpp_7_0
# Benchmark: mbpp
# Data Indices: [129]

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
        import re

        # Step 1: Extract function name and analyze task description
        analysis = await self.generate(
            instruction="""Extract the function name from the test cases and summarize the task:
            - Function name: What appears before parentheses in the assert statements
            - Task summary: Briefly describe the task in one sentence
            - Input/Output: Identify input types and expected output format""",
            context=""
        )

        # Step 2: Generate multiple solution hypotheses
        hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an iterative solution for the task:
                {analysis}
                - Use loops and basic constructs
                - Avoid recursion""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a recursive solution for the task:
                {analysis}
                - Use recursion and helper functions if needed
                - Avoid loops""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                {analysis}
                - Leverage Python's built-in modules (e.g., itertools, math)
                - Optimize for readability and efficiency""",
                context=analysis
            )
        )

        # Step 3: Validate hypotheses against test cases
        validations = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the solution against the test cases:
                Solution:
                {hypothesis}
                - Does it pass all assertions?
                - Are there any edge cases it might fail?""",
                context=hypothesis
            ) for hypothesis in hypotheses]
        )

        # Step 4: Select the best solution
        best_solution = await self.ensemble(
            instruction="""Select the most robust and efficient solution:
            - Passes all test cases
            - Handles edge cases gracefully
            - Is concise and readable""",
            contexts_list=validations
        )

        # Step 5: Refine the selected solution
        refined_solution = await self.revise(
            instruction=f"""Refine the selected solution:
            - Add necessary imports
            - Ensure proper indentation and syntax
            - Improve clarity and documentation""",
            context=best_solution
        )

        return refined_solution