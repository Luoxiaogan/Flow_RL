# Workflow ID: gsm8k_354_0
# Benchmark: gsm8k
# Data Indices: [987, 445]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best solution using ScEnsemble.
        3. Reflect on its potential flaws or assumptions.
        4. Use that reflection to guide a new Custom call for an improved solution.
        """
        # --- Step 1: Generate multiple candidate solutions in parallel ---
        solutions = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on breaking down the math logically."
            )
            solutions.append(solution)

        # --- Step 2: Enforce quality via ensemble selection ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Critically reflect on the chosen solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate based on reflection (meta-cognitive loop) ---
        final_instruction = (
            "Given the initial solution and the following reflection: "
            f"{reflection}. Now, provide a revised, more accurate solution."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution