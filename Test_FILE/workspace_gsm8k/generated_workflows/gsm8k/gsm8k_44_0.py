# Workflow ID: gsm8k_44_0
# Benchmark: gsm8k
# Data Indices: [797, 674]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 different solutions via varied instructions and FlexibleCustom patterns,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # --- Parallel Ensemble: Generate 3 distinct solutions ---
        solution_list = []
        
        # Solution 1: Step-by-step breakdown (Sequential pattern)
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, sequential steps.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        
        # Solution 2: Estimation-first approach (Iterative pattern)
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an estimation, then refine iteratively.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Multiple perspective analysis (Parallel pattern)
        sol3 = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations or methods.",
            reasoning_pattern="parallel",
            steps=["identify_approaches", "evaluate", "select_best"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Final Review for refinement ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer