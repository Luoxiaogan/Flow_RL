# Workflow ID: mbpp_72_0
# Benchmark: mbpp
# Data Indices: [194]

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
            - Function name from test cases.
            - Input and output types.
            - Required libraries (infer from task description and test cases).
            - Problem type (e.g., list manipulation, mathematical computation).
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Solution Exploration
        direct_solution = self.generate(
            instruction=f"""Generate a direct implementation based on the task description.
            Key information: {analysis}""",
            context=""
        )
        tdd_solution = self.generate(
            instruction=f"""Generate a solution using test-driven development.
            Derive the logic directly from the test cases.
            Key information: {analysis}""",
            context=""
        )
        library_solution = self.generate(
            instruction=f"""Generate a solution leveraging Python's standard library.
            Identify relevant functions and modules.
            Key information: {analysis}""",
            context=""
        )
        solutions = await asyncio.gather(direct_solution, tdd_solution, library_solution)

        # Step 3: Validation and Feedback
        validated_solutions = []
        for solution in solutions:
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases.
                Solution: {solution}
                If it fails, identify specific issues (e.g., missing imports, incorrect logic).""",
                context=""
            )
            if "error" not in validation.lower():
                validated_solutions.append(solution)
            else:
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback.
                    Issues: {validation}""",
                    context=solution
                )
                validated_solutions.append(refined)

        # Step 4: Iterative Refinement
        final_solutions = []
        for solution in validated_solutions:
            for _ in range(3):  # Limit iterations to avoid infinite loops
                validation = await self.generate(
                    instruction=f"""Re-validate the solution against the test cases.
                    Solution: {solution}""",
                    context=""
                )
                if "error" not in validation.lower():
                    final_solutions.append(solution)
                    break
                else:
                    solution = await self.revise(
                        instruction=f"""Further refine the solution based on new feedback.
                        Issues: {validation}""",
                        context=solution
                    )

        # Step 5: Final Synthesis
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness (all test cases pass).
            - Simplicity (fewer lines of code, fewer imports).
            - Readability (adherence to Pythonic conventions).""",
            contexts_list=final_solutions
        )

        return best_solution