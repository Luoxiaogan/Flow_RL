# Workflow ID: gsm8k_158_0
# Benchmark: gsm8k
# Data Indices: [508, 346, 4]

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
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to identify potential flaws or missed assumptions.
        Step 4: Use that reflection to guide a targeted regeneration for improved accuracy.
        This mimics human meta-cognition: try multiple approaches → evaluate → critique → refine.
        """

        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on breaking down the problem into logical sub-steps."
            )
            solution_candidates.append(candidate)

        # --- SCENSEMBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT (Critical Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION (Reflect-and-Regenerate Pattern) ---
        final_instruction = (
            f"Given the initial solution and the following reflection:\n\n{reflection}\n\n"
            "Now, provide a new, improved solution that addresses the identified issues and ensures mathematical rigor."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer