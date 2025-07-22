# Workflow ID: gsm8k_67_0
# Benchmark: gsm8k
# Data Indices: [42, 96]

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
        It generates 3 independent solutions with varied reasoning approaches,
        then selects the most consistent one via ScEnsemble. Finally, it reviews
        the best solution for clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using different FlexibleCustom configurations ---
        solutions = []
        
        # Solution 1: Sequential reasoning — step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )
        
        # Solution 2: Iterative refinement — start with estimation, refine
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an approximate approach, then improve accuracy through iteration.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Parallel thinking — multiple angles (e.g., unit-based, formula-based)
        sol3 = await self.flexible_custom(
            custom_instruction="Consider at least two different ways to solve this problem.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_results"]
        )

        solutions.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to select the best solution based on consistency and logic ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final review to polish clarity and catch any overlooked issues ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer