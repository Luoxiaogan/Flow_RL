# Workflow ID: mbpp_49_0
# Benchmark: mbpp
# Data Indices: [289]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract the function name from assert statements.
            - Identify input/output patterns from test cases.
            - Infer the problem type (e.g., list operations, math computations).
            Provide structured output.""",
            context=""
        )

        # Step 2: Solution Exploration (Parallel)
        mathematical_solution = self.generate(
            instruction=f"""Solve using mathematical reasoning:
            - Derive equations or formulas.
            - Ensure alignment with test cases.
            Problem analysis: {analysis}""",
            context=""
        )
        logical_solution = self.generate(
            instruction=f"""Solve using logical reasoning:
            - Break down the problem step-by-step.
            - Ensure alignment with test cases.
            Problem analysis: {analysis}""",
            context=""
        )
        library_solution = self.generate(
            instruction=f"""Solve using Python standard library functions:
            - Leverage built-in functions like map, filter, etc.
            - Ensure alignment with test cases.
            Problem analysis: {analysis}""",
            context=""
        )
        solutions = await asyncio.gather(mathematical_solution, logical_solution, library_solution)

        # Step 3: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate clarity, correctness, and alignment with test cases.
            - Synthesize complementary insights if applicable.""",
            contexts_list=solutions
        )

        # Step 4: Iterative Refinement
        refined_solution = selected_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check against all test cases.
                - Identify discrepancies or errors.
                Current solution: {refined_solution}""",
                context=analysis
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix identified issues:
                    - Address discrepancies or errors.
                    - Improve clarity and efficiency.
                    Validation feedback: {validation}""",
                    context=refined_solution
                )
            else:
                break

        return refined_solution