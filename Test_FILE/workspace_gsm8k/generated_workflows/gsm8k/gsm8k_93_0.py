# Workflow ID: gsm8k_93_0
# Benchmark: gsm8k
# Data Indices: [974, 74, 125]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom (iterative pattern).
        """

        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on clarity and correctness."
            )
            solution_candidates.append(candidate)

        # Step 2: Ensembe the best solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the chosen solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate with guidance from reflection using iterative FlexibleCustom
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Improve the solution by addressing potential flaws or missed steps.",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_approach", "recompute"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_solution