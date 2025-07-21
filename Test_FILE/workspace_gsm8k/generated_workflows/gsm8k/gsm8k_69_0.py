# Workflow ID: gsm8k_69_0
# Benchmark: gsm8k
# Data Indices: [658, 90, 464]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its potential flaws or missed assumptions.
        4. Use that reflection to guide a new solution generation (regeneration).
        5. Optionally review the regenerated solution for final polish.
        """

        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Break it into parts, compute each part, then combine."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ensemble to pick the strongest solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the chosen solution — don't rewrite yet!
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate based on reflection — this mimics meta-cognitive improvement
        improved_instruction = (
            f"Given the following initial solution:\n{best_solution}\n\n"
            f"And the following reflection on possible weaknesses or missing aspects:\n{reflection}\n\n"
            "Now, generate a revised solution that addresses these points while maintaining clarity and correctness."
        )
        final_solution = await self.custom(instruction=improved_instruction)

        # Optional: Final refinement pass
        final_answer = await self.review(pre_solution=final_solution)

        return final_answer