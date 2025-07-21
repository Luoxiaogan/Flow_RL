# Workflow ID: gsm8k_99_0
# Benchmark: gsm8k
# Data Indices: [592, 586, 975]

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
        It generates three distinct solutions via varied reasoning strategies,
        then selects the best one using ScEnsemble. A final Review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 independent solutions using different approaches ---
        solution_list = []
        
        # Solution 1: Sequential breakdown (step-by-step logic)
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear, sequential steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "apply_formula", "compute"]
        )
        
        # Solution 2: Iterative refinement (start with estimate, improve)
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an approximate answer, then refine iteratively for accuracy.",
            reasoning_pattern="iterative",
            steps=["estimate", "check", "refine"],
            max_iterations=2
        )
        
        # Solution 3: Parallel thinking (consider multiple interpretations or methods)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore at least two alternative ways to solve this problem, then synthesize the best approach.",
            reasoning_pattern="parallel",
            steps=["method_a", "method_b", "compare_and_choose"]
        )
        
        solution_list.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review to polish clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer