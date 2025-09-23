# Workflow ID: limr_67_0
# Benchmark: limr
# Data Indices: [110, 200]

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

        # Step 1: Initial Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Classify the problem type (e.g., algebraic, combinatorial, geometric).
            - Identify key components (e.g., variables, constraints, relationships).
            - Determine applicable solution strategies.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        approaches = ["algebraic", "combinatorial", "geometric", "probabilistic"]
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the problem using {approach} methods:
                - Show all steps clearly.
                - Maintain precision in calculations.
                - Highlight any assumptions or constraints.
                - Present intermediate results.""",
                context=analysis
            ) for approach in approaches]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for attempt in solution_attempts:
            validation = await self.revise(
                instruction="""Validate the solution:
                - Check for calculation errors.
                - Test edge cases and boundary conditions.
                - Ensure logical consistency.
                - Suggest improvements if needed.""",
                context=attempt
            )
            refined = await self.revise(
                instruction="Refine the solution based on validation feedback.",
                context=validation
            )
            refined_solutions.append(refined)

        # Step 4: Synthesis and Decision Making
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate the correctness and completeness of each approach.
            - Combine complementary insights if applicable.
            - Select the most robust and accurate solution.""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Answer Extraction
        answer = await self.generate(
            instruction="""Extract the final answer:
            - Ensure it is an exact integer between 000 and 999.
            - Verify precision and formatting requirements.
            - Present the final result.""",
            context=final_solution
        )

        return answer