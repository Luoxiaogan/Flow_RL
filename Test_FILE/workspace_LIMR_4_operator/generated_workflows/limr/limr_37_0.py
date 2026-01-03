# Workflow ID: limr_37_0
# Benchmark: limr
# Data Indices: [212, 157]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (geometry, algebra, combinatorics, etc.)
            - Extract key components (equations, variables, constraints)
            - Determine potential solution strategies
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution based on: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement - Refine each strategy
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction=f"Refine the following solution: {strategy}. Ensure all steps are correct and complete.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble Decision - Select the best solution
        best_solution = await self.ensemble(
            instruction="""Evaluate and select the best solution:
            - Check for correctness and completeness
            - Consider elegance and simplicity
            - Ensure the solution meets all problem constraints""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Validation - Verify the selected solution
        final_validation = await self.revise(
            instruction=f"Perform final validation on: {best_solution}. Ensure it produces an exact integer answer between 000 and 999.",
            context=best_solution
        )

        # Return the final validated solution
        return final_validation