# Workflow ID: gsm8k_81_0
# Benchmark: gsm8k
# Data Indices: [878, 55]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three different solutions via varied reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for refinement.
        """
        # --- Generate 3 distinct solutions using different FlexibleCustom configurations ---
        solution1 = await self.flexible_custom(
            custom_instruction="Use a step-by-step analytical approach to solve math problems.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "execute", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Apply a parallel thinking strategy: consider multiple interpretations of the problem simultaneously.",
            reasoning_pattern="parallel",
            steps=["analyze", "compare", "synthesize"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Solve using iterative refinement: start with an initial estimate and improve it over time.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "refine"],
            max_iterations=2
        )

        # --- Combine all solutions into a list for ensemble selection ---
        solutions = [solution1, solution2, solution3]

        # --- Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Final Review Step: Improve the selected solution based on general critique ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer