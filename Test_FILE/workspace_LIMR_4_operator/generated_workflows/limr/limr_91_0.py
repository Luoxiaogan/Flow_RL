# Workflow ID: limr_91_0
# Benchmark: limr
# Data Indices: [210, 263]

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

        # Step 1: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction="""Analyze the problem to identify:
            - Type (geometry, algebra, combinatorics, etc.)
            - Key components (variables, constraints, relationships)
            - Expected answer format
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Attempt an algebraic solution using: {decomposition}",
                context=decomposition
            ),
            self.generate(
                instruction=f"Attempt a geometric solution using: {decomposition}",
                context=decomposition
            ),
            self.generate(
                instruction=f"Attempt a combinatorial solution using: {decomposition}",
                context=decomposition
            ),
            self.generate(
                instruction=f"Attempt a number-theoretic solution using: {decomposition}",
                context=decomposition
            )
        )

        # Step 3: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Critique and improve this solution. Ensure all steps are rigorous and clear.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble Synthesis
        synthesis = await self.ensemble(
            instruction="""Synthesize the best solution from the refined strategies:
            - Evaluate correctness and clarity
            - Resolve conflicts between approaches
            - Combine insights where applicable""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Validation
        final_solution = await self.revise(
            instruction="""Validate the final solution:
            - Verify all calculations
            - Check logical consistency
            - Confirm adherence to problem constraints
            - Ensure the answer is in the required format""",
            context=synthesis
        )

        return final_solution