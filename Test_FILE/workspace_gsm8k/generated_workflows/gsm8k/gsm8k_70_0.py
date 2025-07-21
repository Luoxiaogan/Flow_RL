# Workflow ID: gsm8k_70_0
# Benchmark: gsm8k
# Data Indices: [220, 191, 608]

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
        It generates three distinct solutions via different reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # --- Step 1: Generate 3 independent solutions using varied approaches ---
        solution_list = []
        
        # Solution 1: Sequential breakdown (step-by-step logic)
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into clear steps: identify knowns, unknowns, operations, and verify.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_operations", "verify"]
        )
        
        # Solution 2: Iterative refinement (start with estimation, improve)
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an approximate approach, then refine iteratively for accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration (consider multiple angles)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore alternative interpretations or methods to solve the problem.",
            reasoning_pattern="parallel",
            steps=["analyze_alternatives", "compare_approaches", "select_best"]
        )
        
        solution_list.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer