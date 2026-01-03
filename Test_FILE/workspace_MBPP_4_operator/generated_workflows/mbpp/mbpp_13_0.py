# Workflow ID: mbpp_13_0
# Benchmark: mbpp
# Data Indices: [281, 77]

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
            instruction="""Extract the function name, parameters, and expected behavior:
            - Identify the function name from the test cases.
            - Determine input types, output types, and operations to be performed.
            - Classify the problem type (e.g., mathematical computation, string manipulation).""",
            context=""
        )

        # Step 2: Parallel Exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using direct computation:
                - Use the extracted function name and parameters.
                - Implement the required behavior based on the task description.
                - Include necessary imports and ensure proper indentation.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using Python's standard library:
                - Use the extracted function name and parameters.
                - Leverage appropriate standard library functions.
                - Include necessary imports and ensure proper indentation.""",
                context=analysis
            )
        )

        # Step 3: Ensemble Evaluation
        best_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate each candidate against the test cases.
            - Choose the solution that is most accurate and efficient.""",
            contexts_list=candidates
        )

        # Step 4: Refinement
        refined_solution = await self.revise(
            instruction="""Critique and improve the solution:
            - Ensure the code is clean and efficient.
            - Handle edge cases and validate against all test cases.
            - Add comments and improve readability if necessary.""",
            context=best_solution
        )

        # Step 5: Final Validation
        validation = await self.generate(
            instruction=f"""Validate the solution:
            - Ensure the code passes all test cases.
            - Check for proper indentation, complete imports, and clean syntax.""",
            context=refined_solution
        )

        return validation