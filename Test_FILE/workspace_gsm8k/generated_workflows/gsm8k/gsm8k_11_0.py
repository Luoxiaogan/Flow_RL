# Workflow ID: gsm8k_11_0
# Benchmark: gsm8k
# Data Indices: [693, 8, 48]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        This structure first explores multiple reasoning paths in parallel, then uses reflection to guide a targeted refinement.
        """
        # Step 1: Generate multiple independent solutions via parallel ensemble (fan-out)
        solution_pool = []
        for _ in range(3):  # Run 3 different initial approaches
            sol = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Focus on identifying knowns, unknowns, and relationships."
            )
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the best candidate from the pool
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution — identify potential flaws or missed angles
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Conditional logic based on reflection content — if reflection suggests improvement is needed, regenerate
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # Regenerate with guided instruction using the reflection
            final_solution = await self.custom(
                instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, solve the problem again with improved clarity and rigor."
            )
        else:
            # If no major issues found, proceed with the original best solution
            final_solution = best_initial

        return final_solution