# Workflow ID: mbpp_1_0
# Benchmark: mbpp
# Data Indices: [316, 346]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the task description:
            - Identify the function name and its arguments.
            - Parse the natural language description to understand the requirements.
            - Note any specific constraints or expected outputs.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct implementation based on the analysis:
                {analysis}
                Use basic Python constructs and ensure proper indentation.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution leveraging Python's standard library:
                {analysis}
                Use modules like re, math, or itertools if applicable.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using advanced techniques:
                {analysis}
                Consider edge cases and optimize for performance.""",
                context=analysis
            )
        )

        # Step 3: Validation and Refinement
        validated_candidates = []
        for candidate in candidates:
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                {candidate}
                Ensure it passes all assertions and handle any errors.""",
                context=candidate
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    {validation}""",
                    context=candidate
                )
                validated_candidates.append(refined)
            else:
                validated_candidates.append(candidate)

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness: Passes all test cases.
            - Simplicity: Uses straightforward logic.
            - Pythonic Style: Follows best practices.""",
            contexts_list=validated_candidates
        )

        # Step 5: Return the Final Code
        return final_solution