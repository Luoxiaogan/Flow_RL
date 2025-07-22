# Workflow ID: gsm8k_190_1
# Benchmark: gsm8k
# Data Indices: [36, 413, 809]

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
        This workflow uses a novel combination of Parallel Ensemble + Reflect + Regenerate.
        It first generates multiple diverse solutions (parallel), selects the best one,
        then critically reflects on it to uncover hidden assumptions or errors,
        and finally regenerates a refined solution using that reflection — all in a single pass.
        
        Key differences from existing:
        - Uses parallel ensemble (fan-out) instead of sequential refinement
        - Applies reflection *after* selection (not before) to guide targeted improvement
        - Avoids iterative loops; instead, uses structured reasoning via FlexibleCustom for diversity
        """
        # Step 1: Generate 3 independent solutions using different flexible strategies
        # Each uses a unique reasoning pattern to ensure diverse approaches
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction="Solve this math word problem step-by-step. Be clear about what is given, what needs to be found, and how you connect them."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the strongest solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a focused regeneration — not an iteration!
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Revise the best solution to address any overlooked assumptions or logical gaps while maintaining clarity and correctness."
        )

        return final_solution