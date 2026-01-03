# Workflow ID: limr_46_0
# Benchmark: limr
# Data Indices: [73, 87]

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

        # Step 1: Initial Analysis - Decompose the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key variables, constants, and relationships.
            - Classify the problem type (e.g., geometry, number theory, algebra).
            - Highlight constraints and boundary conditions.
            - Determine the expected answer format (integer between 000 and 999).""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution approach based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution approach based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution approach based on: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement - Validate and improve intermediate results
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Verify calculations, check logical consistency, and improve clarity.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Dynamic Adaptation - Prioritize promising paths
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"Validate the following solution: {strategy}",
                context=strategy
            ) for strategy in refined_strategies]
        )

        # Dynamically select the best strategy based on validation feedback
        best_strategy = await self.ensemble(
            instruction="Select the most promising strategy based on validation feedback.",
            contexts_list=validation_results
        )

        # Step 5: Final Synthesis - Combine insights and present the solution
        final_solution = await self.generate(
            instruction=f"""Synthesize the final solution based on: {best_strategy}
            - Ensure all steps are clearly explained.
            - Verify the final answer meets the required format (integer between 000 and 999).
            - Double-check calculations and logical consistency.""",
            context=best_strategy
        )

        return final_solution