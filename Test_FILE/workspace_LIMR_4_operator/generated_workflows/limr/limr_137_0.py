# Workflow ID: limr_137_0
# Benchmark: limr
# Data Indices: [20, 102]

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
            instruction="""Analyze the problem thoroughly:
            - Identify key components (variables, equations, constraints).
            - Classify the problem type (geometry, algebra, etc.).
            - Extract explicit and implicit constraints.
            - Define the expected answer format.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve using algebraic methods:
                - Perform symbolic manipulation.
                - Simplify expressions.
                - Solve equations step-by-step.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve using geometric reasoning:
                - Visualize the problem.
                - Apply geometric theorems.
                - Calculate lengths, angles, areas.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve using combinatorial techniques:
                - Count possibilities.
                - Apply permutations and combinations.
                - Use recursive reasoning.""",
                context=analysis
            )
        )

        # Step 3: Intermediate Validation and Refinement
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this solution:
                - Check for logical consistency.
                - Address calculation errors.
                - Improve clarity and rigor.""",
                context=path
            ) for path in paths]
        )

        # Step 4: Synthesize Results
        synthesis = await self.ensemble(
            instruction=f"""Synthesize the best solution:
            - Compare the refined paths.
            - Select the most accurate and complete solution.
            - Combine complementary insights if necessary.""",
            contexts_list=refined_paths
        )

        # Step 5: Final Verification
        final_solution = await self.revise(
            instruction=f"""Verify the final solution:
            - Ensure all constraints are satisfied.
            - Double-check calculations.
            - Confirm the answer format is correct.""",
            context=synthesis
        )

        return final_solution