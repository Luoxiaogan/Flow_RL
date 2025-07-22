# Workflow ID: gsm8k_48_0
# Benchmark: gsm8k
# Data Indices: [949, 377]

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
        Step 1: Generate multiple candidate solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on that solution to identify potential flaws or improvements.
        Step 4: Use reflection to guide a new, improved solution via Custom.
        """

        # --- PARALLEL ENSEMBLE: Generate 3 independent solutions ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into logical steps. Think carefully about each action's effect on the total quantity."
            )
            solution_candidates.append(candidate)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT: Critically analyze the best solution without rewriting it ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE: Use reflection to guide a refined solution ---
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{best_solution}\n\nAnd this reflection on its possible shortcomings or missed insights:\n{reflection}\n\nNow, provide a fully revised and improved solution based on this analysis."
        )

        return final_answer