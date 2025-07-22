# Workflow ID: gsm8k_24_0
# Benchmark: gsm8k
# Data Indices: [963, 461, 247]

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
        1. Generate 3 independent solutions using parallel ensemble.
        2. Select the best one via ScEnsemble.
        3. Reflect critically on the selected solution to identify potential flaws or missed steps.
        4. Use that reflection to guide a targeted regenerative step for an improved final answer.
        This ensures robustness (from ensembling) and meta-cognitive refinement (from reflection).
        """
        # --- STEP 1: Parallel Ensemble ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Be thorough and avoid assumptions."
            )
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 2: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 3: Regenerate Based on Reflection ---
        final_instruction = (
            "Given the initial solution and the following reflection:\n"
            f"{reflection}\n\n"
            "Use this insight to produce a new, more accurate and logically sound solution."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer