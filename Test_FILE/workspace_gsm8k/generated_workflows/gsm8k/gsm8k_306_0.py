# Workflow ID: gsm8k_306_0
# Benchmark: gsm8k
# Data Indices: [501, 422, 530]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate multiple solutions in parallel (fan-out).
        2. Select the best one using ScEnsemble.
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new solution via Custom with targeted instruction.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 independent solutions
            candidate = await self.custom(
                instruction="Solve the problem step-by-step using a clear reasoning process. Do not assume anything beyond what's given."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Select Best Candidate ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Conditional Regeneration Based on Reflection ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            # If reflection indicates flaws, regenerate with targeted instruction
            final_solution = await self.custom(
                instruction=f"Based on the following reflection about the previous solution: '{reflection}'. Now solve the problem again, focusing on correcting any logical gaps or incorrect assumptions."
            )
        else:
            # If no major issues found, use the best solution as-is
            final_solution = best_solution

        return final_solution