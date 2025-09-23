# Workflow ID: mbpp_10_0
# Benchmark: mbpp
# Data Indices: [9]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Function name from test cases
            - Input and output examples
            - Task description and requirements
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Direct translation strategy:
                - Translate the natural language description into Python code.
                - Ensure the function name matches '{analysis}'.
                - Include all necessary imports and handle edge cases.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Decomposition-based strategy:
                - Break the task into smaller sub-tasks.
                - Solve each sub-task independently.
                - Combine the solutions into a single function matching '{analysis}'.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Standard library utilization strategy:
                - Leverage Python's built-in functions or modules.
                - Ensure the function name matches '{analysis}'.
                - Optimize for readability and efficiency.""",
                context=analysis
            )
        )

        # Step 3: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="""Refine the solution:
                - Ensure it passes all test cases.
                - Improve clarity and readability.
                - Handle edge cases and validate logic.""",
                context=solution
            ) for solution in strategies]
        )

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Must pass all test cases.
            - Prioritize simplicity and readability.
            - Ensure efficient use of Python features.""",
            contexts_list=refined_solutions
        )

        # Step 5: Iterative Improvement (if needed)
        validation = await self.generate(
            instruction="Validate the final solution against all test cases.",
            context=final_solution
        )
        if "error" in validation.lower():
            final_solution = await self.revise(
                instruction=f"Fix issues: {validation}",
                context=final_solution
            )

        return final_solution