# Workflow ID: gsm8k_103_0
# Benchmark: gsm8k
# Data Indices: [163, 209]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate multiple initial solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect critically on its reasoning flaws or assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_pool = []
        for _ in range(4):  # Generate 4 independent attempts
            sol = await self.custom(
                instruction="Solve the problem step-by-step, focusing on clear logical progression. Do not skip any intermediate steps."
            )
            solution_pool.append(sol)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Using Reflection as Guidance ---
        final_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection: " + reflection +
                               " Now, solve the problem again using an iterative approach to refine your answer.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_solution