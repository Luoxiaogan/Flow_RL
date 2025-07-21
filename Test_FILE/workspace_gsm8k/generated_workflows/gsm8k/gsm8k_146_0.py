# Workflow ID: gsm8k_146_0
# Benchmark: gsm8k
# Data Indices: [927, 642, 610]

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
        Generates 3 different solutions via varied reasoning strategies,
        then selects the best one with ScEnsemble. Final review ensures clarity.
        """
        # --- STEP 1: Generate 3 diverse solutions using different FlexibleCustom configurations ---
        solution_list = []

        # Solution 1: Sequential reasoning (step-by-step breakdown)
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "compute", "verify"]
        )
        solution_list.append(sol1)

        # Solution 2: Iterative refinement (start rough, improve)
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an estimate or initial approach, then refine iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solution_list.append(sol2)

        # Solution 3: Parallel exploration (multiple angles at once)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations or methods simultaneously.",
            reasoning_pattern="parallel",
            steps=["method_a", "method_b", "compare_results"]
        )
        solution_list.append(sol3)

        # --- STEP 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for clarity, correctness, and completeness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer