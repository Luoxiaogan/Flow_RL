# Workflow ID: limr_80_0
# Benchmark: limr
# Data Indices: [180, 85]

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

        # Step 1: Initial Problem Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key components (equations, constraints, variables)
            - Highlight any special cases or edge conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Parallel Solution Attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt algebraic solution:
                - Simplify equations
                - Solve for unknowns
                - Verify intermediate steps""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt geometric interpretation:
                - Visualize relationships
                - Apply coordinate geometry or trigonometry
                - Validate against constraints""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt combinatorial analysis:
                - Count possibilities
                - Apply permutations or combinations
                - Validate against total outcomes""",
                context=initial_analysis
            )
        )

        # Step 3: Validate and Revise Each Attempt
        revised_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {attempt}",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Ensure correctness and precision
            - Align with problem constraints
            - Choose the most efficient approach""",
            contexts_list=revised_attempts
        )

        # Step 5: Summarize Final Answer
        final_answer = await self.summarize(
            instruction="Condense the solution into a clear, precise answer.",
            context=final_solution
        )

        return final_answer