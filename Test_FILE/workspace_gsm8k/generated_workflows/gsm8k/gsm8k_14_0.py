# Workflow ID: gsm8k_14_0
# Benchmark: gsm8k
# Data Indices: [311, 656]

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
        This is a robust, diverse workflow using the Parallel Ensemble pattern.
        It generates three independent solutions via different reasoning strategies,
        then selects the best one using ScEnsemble. Finally, it reviews the chosen solution
        for clarity and correctness — a key step in ensuring robustness.
        """
        # --- Generate 3 diverse solutions using different FlexibleCustom configurations ---
        solutions = []

        # Solution 1: Sequential reasoning — clear step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Solution 2: Iterative refinement — start with an estimate, then improve
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an initial estimate and refine your answer through multiple iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_consistency", "refine"],
            max_iterations=2
        )

        # Solution 3: Parallel approach — consider multiple interpretations or methods simultaneously
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple potential solution paths concurrently and compare them.",
            reasoning_pattern="parallel",
            steps=["path_a", "path_b", "compare_paths"]
        )

        solutions.extend([sol1, sol2, sol3])

        # --- Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Final review to ensure clarity, correctness, and completeness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer