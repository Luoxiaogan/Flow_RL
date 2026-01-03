# Workflow ID: limr_74_0
# Benchmark: limr
# Data Indices: [179, 64]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the problem type (algebraic, geometric, combinatorial, etc.)
            - Identify key components (variables, equations, constraints)
            - Highlight any special cases or edge conditions
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        algebraic_solution = self.generate(
            instruction=f"""Solve using algebraic methods:
            - Perform symbolic manipulation
            - Solve equations step-by-step
            - Verify intermediate results
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        geometric_solution = self.generate(
            instruction=f"""Solve using geometric interpretation:
            - Visualize the problem
            - Apply geometric principles
            - Verify intermediate results
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        combinatorial_solution = self.generate(
            instruction=f"""Solve using combinatorial reasoning:
            - Count possibilities systematically
            - Apply combinatorial principles
            - Verify intermediate results
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        solutions = await asyncio.gather(algebraic_solution, geometric_solution, combinatorial_solution)

        # Step 3: Intermediate Validation
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the solution:
                - Check for logical consistency
                - Verify mathematical correctness
                - Address any identified edge cases
                Solution: {sol}""",
                context=sol
            ) for sol in solutions]
        )
        summarized_solutions = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the solution into key points.",
                context=sol
            ) for sol in refined_solutions]
        )

        # Step 4: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate correctness and elegance
            - Consider computational efficiency
            - Ensure all constraints are satisfied""",
            contexts_list=summarized_solutions
        )

        # Step 5: Final Refinement
        polished_solution = await self.revise(
            instruction="""Polish the final solution:
            - Ensure clarity and precision
            - Box the final answer
            - Include all necessary steps""",
            context=final_solution
        )

        return polished_solution