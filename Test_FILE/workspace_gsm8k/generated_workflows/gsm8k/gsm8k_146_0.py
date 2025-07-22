# Workflow ID: gsm8k_146_0
# Benchmark: gsm8k
# Data Indices: [883, 842]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble (robustness).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on its potential flaws or assumptions (meta-cognition).
        Step 4: Use reflection to guide a new Custom call for an improved final answer.
        This creates a hybrid structure that balances exploration and refinement.
        """

        # --- PARALLEL ENSEMBLE: Generate multiple initial solutions ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step. Break it into clear logical parts. Do not rush—ensure each step is justified."
            )
            solutions.append(sol)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO GENERATE A FINAL IMPROVED SOLUTION ---
        final_answer = await self.custom(
            instruction=f"Given the following solution:\n{best_solution}\n\nAnd this reflection on possible weaknesses or missed cases:\n{reflection}\n\nNow, provide a refined, more complete, and logically sound solution based on both."
        )

        return final_answer