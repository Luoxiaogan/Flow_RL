# Workflow ID: gsm8k_327_0
# Benchmark: gsm8k
# Data Indices: [210, 774, 919]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple solutions in parallel (fan-out).
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect critically on the selected solution.
        Step 4: Use reflection to guide a new, improved solution (regenerate).
        This structure ensures robustness (via ensemble) and meta-cognition (via reflection).
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 independent attempts
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Break it into logical parts: identify knowns, unknowns, apply relevant math, then verify."
            )
            solution_candidates.append(candidate)

        # --- SCENSBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT (Critical Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION (Reflect & Regenerate Pattern) ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a new, improved solution that addresses potential flaws or assumptions in the original approach."
        )

        return final_answer