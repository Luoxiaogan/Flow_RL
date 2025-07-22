# Workflow ID: gsm8k_228_0
# Benchmark: gsm8k
# Data Indices: [850, 705]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect on its potential weaknesses or assumptions.
        4. Use that reflection to guide a new, improved solution via Custom.
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step, explaining each reasoning step clearly."
            )
            solutions.append(solution)

        # --- STEP 2: Choose Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution (Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        final_instruction = (
            f"Given the initial solution and the following reflection:\n"
            f"{reflection}\n\n"
            f"Based on this reflection, provide a refined, more accurate solution."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer