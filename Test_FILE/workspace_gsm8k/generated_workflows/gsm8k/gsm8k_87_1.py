# Workflow ID: gsm8k_87_1
# Benchmark: gsm8k
# Data Indices: [122, 708]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' hybrid pattern.
        It generates multiple independent solutions (parallel), then uses reflection on the best one to produce a final improved answer.
        This approach combines robustness from ensembling with meta-cognitive refinement — fundamentally different from the existing single-path flow.
        """
        # Step 1: Generate 3 independent solutions in parallel via flexible custom with "parallel" reasoning pattern
        solution_pool = []
        for _ in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem using a clear, step-by-step method.",
                reasoning_pattern="parallel",
                steps=["understand", "analyze", "solve", "verify"]
            )
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to guide a fresh, targeted generation of the final answer
        final_answer = await self.custom(
            instruction=f"Based on the following solution and its reflection, provide an improved final answer: {reflection}"
        )

        return final_answer