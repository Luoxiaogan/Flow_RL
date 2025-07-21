# Workflow ID: gsm8k_56_1
# Benchmark: gsm8k
# Data Indices: [694, 621, 117]

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
        Diverse workflow combining Parallel Ensemble + Reflect + Iterative Refinement.
        1. Generate 3 independent solutions using parallel reasoning.
        2. Select the best one via ScEnsemble.
        3. Reflect on it to uncover hidden assumptions or errors.
        4. Use reflection to guide a targeted iterative refinement (2 passes).
        This approach leverages diversity in initial thinking and meta-cognition for robustness.
        """

        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_pool = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve this problem using a unique strategy—focus on clarity and logical steps.",
                reasoning_pattern="sequential",
                steps=["identify", "plan", "execute", "validate"]
            )
            solution_pool.append(solution)

        # Step 2: Choose the strongest solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the chosen solution — no rewriting yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to drive iterative refinement (2 rounds of review)
        current = best_solution
        for _ in range(2):  # Two refinement iterations
            # Use reflection to inform next step
            refined_instruction = f"Based on the following reflection: '{reflection}'. Now improve the solution by addressing these points."
            current = await self.review(pre_solution=current)
        
        return current