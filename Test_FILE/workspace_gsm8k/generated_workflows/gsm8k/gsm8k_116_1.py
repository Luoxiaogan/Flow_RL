# Workflow ID: gsm8k_116_1
# Benchmark: gsm8k
# Data Indices: [188, 597]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a novel structure where each refinement step is informed by a critical reflection on the prior solution.
        It combines 'Reflect' (to diagnose flaws) and 'Review' (to improve), creating a meta-cognitive loop that ensures deeper reasoning.
        Unlike the existing workflow which just applies Review blindly, this one actively learns from its own mistakes.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into smaller parts."
        )

        # Step 2: Reflect on the initial solution — identify potential errors or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a revised solution via Custom (not just Review)
        first_refined = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again, focusing on addressing these points."
        )

        # Step 4: Reflect again on the refined solution to catch any remaining issues
        second_reflection = await self.reflect(pre_solution=first_refined)

        # Step 5: Final refinement using the new reflection — this time, use Review for mechanical improvement
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution