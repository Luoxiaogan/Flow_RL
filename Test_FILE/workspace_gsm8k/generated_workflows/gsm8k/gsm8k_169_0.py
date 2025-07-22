# Workflow ID: gsm8k_169_0
# Benchmark: gsm8k
# Data Indices: [602, 218, 363]

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
        It generates 3 distinct solutions via different reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # --- Step 1: Generate 3 diverse solutions using different FlexibleCustom configurations ---
        solution_list = []
        
        # Solution 1: Sequential approach – clear step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem logically and solve each part in order.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )
        
        # Solution 2: Iterative refinement – start with estimation, improve
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an approximate answer, then refine it through multiple passes.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Branching logic – consider multiple interpretations before deciding
        sol3 = await self.flexible_custom(
            custom_instruction="Explore alternative ways to interpret the problem and choose the most consistent path.",
            reasoning_pattern="branching",
            steps=["identify_options", "evaluate", "select_best"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to pick the most accurate solution from the three ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review to ensure clarity, correctness, and completeness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer