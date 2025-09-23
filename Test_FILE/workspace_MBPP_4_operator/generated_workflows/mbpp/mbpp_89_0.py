# Workflow ID: mbpp_89_0
# Benchmark: mbpp
# Data Indices: [94, 87]

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
            instruction="""Extract key information:
            - Function name and signature from test cases.
            - Input/output types and expected behavior.
            - Key operations or constraints from the natural language description.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using a mathematical approach:
                Problem Summary: {analysis}
                - Focus on numerical computations or formulas.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using a logical approach:
                Problem Summary: {analysis}
                - Focus on conditional logic or algorithmic steps.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                Problem Summary: {analysis}
                - Leverage Python's built-in modules where applicable.""",
                context=analysis
            )
        )

        # Step 3: Validation and Ensemble
        validated_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate this solution against the test cases: {candidate}",
                context=candidate
            ) for candidate in candidates]
        )
        best_solution = await self.ensemble(
            instruction="Select the most robust and efficient solution.",
            contexts_list=validated_candidates
        )

        # Step 4: Final Refinement
        refined_solution = await self.revise(
            instruction="""Refine the solution:
            - Ensure proper indentation and syntax.
            - Add necessary imports.
            - Handle edge cases explicitly.""",
            context=best_solution
        )

        # Step 5: Final Validation
        final_validation = await self.generate(
            instruction=f"Verify the final solution against all test cases: {refined_solution}",
            context=refined_solution
        )

        return refined_solution