# Workflow ID: mbpp_34_0
# Benchmark: mbpp
# Data Indices: [305, 278]

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

        # Step 1: Extract function name and signature
        func_info = await self.generate(
            instruction="""Extract the function name and infer its signature from the test cases.
            Format the result as:
            Function Name: <name>
            Parameters: <param1>, <param2>, ...
            Return Type: <type>""",
            context=""
        )

        # Step 2: Analyze task description
        analysis = await self.generate(
            instruction=f"""Analyze the task description to understand the computational requirements.
            Context: {func_info}
            Identify:
            - Type of operation (e.g., list manipulation, regex matching)
            - Required libraries (e.g., re, math)
            - Implicit constraints or edge cases""",
            context=func_info
        )

        # Step 3: Generate candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a candidate solution focusing on direct implementation.
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a candidate solution focusing on edge cases and robustness.
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a candidate solution leveraging Python's standard library.
                Context: {analysis}""",
                context=analysis
            )
        )

        # Step 4: Validate and refine solutions
        MAX_ITERATIONS = 3
        best_solution = None
        for iteration in range(MAX_ITERATIONS):
            validations = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Validate this solution against the test cases.
                    Provide feedback if it fails.
                    Context: {candidate}""",
                    context=candidate
                ) for candidate in candidates]
            )

            # Check for valid solution
            valid_solutions = [c for c, v in zip(candidates, validations) if "error" not in v.lower()]
            if valid_solutions:
                best_solution = await self.ensemble(
                    instruction="Select the best solution based on validation results.",
                    contexts_list=valid_solutions
                )
                break

            # Refine candidates based on feedback
            candidates = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Refine this solution based on feedback: {feedback}.
                    Context: {candidate}""",
                    context=candidate
                ) for candidate, feedback in zip(candidates, validations)]
            )

        # Step 5: Finalize solution
        if best_solution:
            return best_solution
        else:
            raise ValueError("No valid solution found after maximum iterations.")