# Workflow ID: limr_59_0
# Benchmark: limr
# Data Indices: [96, 34]

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
            instruction="""Analyze the problem comprehensively:
            - Identify all variables, constants, and relationships.
            - Classify the problem type (e.g., algebraic, geometric, combinatorial).
            - Extract explicit and implicit constraints.
            - Determine the expected answer format (e.g., integer, equation).""",
            context=""
        )

        # Step 2: Parallel Exploration
        approaches = ["algebraic", "geometric", "combinatorial", "numerical"]
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the problem using {approach} reasoning:
                - Apply relevant techniques and principles.
                - Show all steps clearly.
                - Ensure the solution satisfies all constraints.""",
                context=analysis
            ) for approach in approaches]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for attempt in solution_attempts:
            validation = await self.revise(
                instruction="""Critique the solution:
                - Check for logical consistency.
                - Verify calculations and constraints.
                - Highlight any errors or gaps.""",
                context=attempt
            )
            refined = await self.revise(
                instruction=f"""Refine the solution based on critique:
                - Address identified issues.
                - Clarify ambiguous steps.
                - Ensure precision and correctness.""",
                context=validation
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Compare all refined solutions.
            - Select the most rigorous and complete approach.
            - Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=refined_solutions
        )

        return final_solution