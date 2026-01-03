# Workflow ID: mbpp_22_0
# Benchmark: mbpp
# Data Indices: [76, 164]

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

        # Step 1: Extract function name and parse task description
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and summarize the task requirements:
            - Identify the function name from the assert statements.
            - Parse the natural language description to understand the task.
            - Identify edge cases from the test examples.""",
            context=""
        )
        function_name = re.search(r"def (\w+)\(", analysis).group(1) if "def" in analysis else None

        # Step 2: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution for the task:
                - Use the function name: {function_name}
                - Include all necessary imports.
                - Ensure proper indentation and syntax.
                - Focus on list/array operations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution for the task:
                - Use the function name: {function_name}
                - Include all necessary imports.
                - Ensure proper indentation and syntax.
                - Focus on mathematical computations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution for the task:
                - Use the function name: {function_name}
                - Include all necessary imports.
                - Ensure proper indentation and syntax.
                - Focus on string manipulation.""",
                context=analysis
            )
        )

        # Step 3: Validate candidates and select the best one
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate this candidate solution against the test cases:
                - Check if it passes all assert statements.
                - Identify any errors or missing details.""",
                context=candidate
            ) for candidate in candidates]
        )
        best_candidate = await self.ensemble(
            instruction="Select the best candidate solution based on validation results.",
            contexts_list=validations
        )

        # Step 4: Iteratively refine the best candidate
        refined_solution = best_candidate
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate the refined solution against test cases.",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Refine the solution to fix errors: {validation}",
                    context=refined_solution
                )
            else:
                break

        return refined_solution