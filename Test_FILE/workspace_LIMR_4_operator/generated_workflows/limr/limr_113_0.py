# Workflow ID: limr_113_0
# Benchmark: limr
# Data Indices: [237, 155]

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

        # Step 1: Initial Analysis - Classify the problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (geometry, number theory, algebra, combinatorics, etc.)
            - Extract key variables, constraints, and relationships
            - Highlight any special cases or edge conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies in Parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution using algebraic techniques:
                - Focus on equations, transformations, and symbolic manipulation
                - Ensure all steps are mathematically rigorous
                Problem Analysis: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a solution using combinatorial reasoning:
                - Focus on counting principles, permutations, and probability
                - Ensure all cases are considered
                Problem Analysis: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a solution using geometric insights:
                - Focus on spatial relationships, coordinates, and transformations
                - Ensure visual intuition is translated into formal arguments
                Problem Analysis: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Validate and Refine Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine the solution. Correct any errors and ensure precision.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarize Key Insights from Each Strategy
        summarized_strategies = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the solution into key insights and critical steps.",
                context=strategy
            ) for strategy in refined_strategies]
        )

        # Step 5: Synthesize the Best Solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the available strategies:
            - Select the most rigorous and insightful approach
            - Combine complementary insights if necessary
            - Ensure the final answer is an exact integer between 000 and 999""",
            contexts_list=summarized_strategies
        )

        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction="""Verify the final solution:
            - Check all steps for logical consistency
            - Ensure the answer meets the problem's requirements
            - Cross-validate with alternative methods if possible""",
            context=final_solution
        )

        return verified_solution