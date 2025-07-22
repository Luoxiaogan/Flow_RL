# Workflow ID: gsm8k_175_0
# Benchmark: gsm8k
# Data Indices: [790, 516]

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
        Step 1: Generate 3 independent solutions using parallel ensemble (fan-out).
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect critically on the best solution to uncover potential flaws or missed angles.
        Step 4: Use reflection to guide a new Custom call for a refined final answer.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solutions = []
        for i in range(3):  # Generate 3 different reasoning paths
            solution = await self.custom(
                instruction="Solve the problem step-by-step. Break it into parts: identify knowns, unknowns, and apply operations logically."
            )
            solutions.append(solution)

        # --- SCENSEMBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT (Critical Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION (Reflect & Regenerate Pattern) ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised, improved, and more accurate solution."
        )

        return final_answer