# Workflow ID: gsm8k_59_0
# Benchmark: gsm8k
# Data Indices: [980, 969, 735]

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
        4. Use that reflection to guide a final Custom call for an improved solution.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Avoid assumptions not stated in the problem."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the Best Solution (Meta-cognitive critique) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate with Reflection Guidance ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection on possible weaknesses or missing elements: '{reflection}'. "
                        "Now, produce a refined, more accurate, and logically complete answer based on this insight."
        )

        return final_answer