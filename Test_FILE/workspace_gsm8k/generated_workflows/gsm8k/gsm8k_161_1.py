# Workflow ID: gsm8k_161_1
# Benchmark: gsm8k
# Data Indices: [195, 265, 104]

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
        This workflow combines Parallel Ensemble (fan-out/fan-in) with Reflect-and-Regenerate logic.
        It first generates 3 independent solutions using FlexibleCustom in parallel mode,
        then selects the best one via ScEnsemble, reflects on it, and finally regenerates a refined solution
        based on that reflection — creating a robust, meta-cognitive loop.
        """

        # Step 1: Generate multiple candidate solutions in parallel using FlexibleCustom
        # Each uses a different reasoning approach to avoid bias
        solutions = []
        for i in range(3):
            instruction = f"Use a unique reasoning strategy for this problem. Try {['step-by-step breakdown', 'visual analogy', 'formula-first approach'][i]}."
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final improved solution
        final_instruction = (
            f"Given the following reflection:\n{reflection}\n\n"
            "Re-solve the problem with this insight in mind. Focus on clarity, completeness, and avoiding prior blind spots."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution