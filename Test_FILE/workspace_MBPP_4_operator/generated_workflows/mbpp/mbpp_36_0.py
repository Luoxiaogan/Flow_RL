# Workflow ID: mbpp_36_0
# Benchmark: mbpp
# Data Indices: [320]

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

        # Step 1: Extract function name and inputs
        extraction = await self.generate(
            instruction="""Extract the function name, input types, and expected outputs from the test cases. 
            Provide structured output in the format:
            Function Name: [name]
            Input Types: [types]
            Expected Outputs: [outputs]""",
            context=""
        )

        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the following information:
            {extraction}
            Categories: List/Array Operations, Mathematical Computations, String Manipulation, Data Structures, Standard Library Usage.
            Provide reasoning for the classification.""",
            context=extraction
        )

        # Step 3: Parallel solution generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using list comprehensions:
                Problem Details: {extraction}
                Classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using iterative loops:
                Problem Details: {extraction}
                Classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using built-in functions:
                Problem Details: {extraction}
                Classification: {classification}""",
                context=classification
            )
        )

        # Step 4: Synthesize and validate solutions
        best_solution = await self.ensemble(
            instruction=f"""Evaluate the following candidate solutions against the test cases:
            Candidate 1: {candidates[0]}
            Candidate 2: {candidates[1]}
            Candidate 3: {candidates[2]}
            Select the most robust and efficient solution.""",
            contexts_list=candidates
        )

        # Step 5: Refine the solution
        refined_solution = await self.revise(
            instruction=f"""Refine the selected solution to improve clarity, handle edge cases, and ensure adherence to Python standards:
            Selected Solution: {best_solution}
            Problem Details: {extraction}
            Classification: {classification}""",
            context=best_solution
        )

        # Step 6: Final output
        final_code = f"""