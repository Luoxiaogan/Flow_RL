# Workflow ID: gsm8k_36_0
# Benchmark: gsm8k
# Data Indices: [884, 608, 265]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect critically on the best solution to uncover hidden flaws or assumptions.
        4. Use reflection to guide a new Custom call for an improved final answer.
        """
        # Step 1: Parallel Ensemble — generate multiple initial solutions
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on identifying key quantities and operations."
            )
            solution_candidates.append(candidate)

        # Step 2: Select the most accurate solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect — critique the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate based on reflection — use reflection to guide a more thoughtful solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, provide a revised, more robust solution that addresses any identified issues or assumptions."
        )

        return final_answer