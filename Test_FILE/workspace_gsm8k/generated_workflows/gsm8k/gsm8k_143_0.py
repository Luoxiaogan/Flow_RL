# Workflow ID: gsm8k_143_0
# Benchmark: gsm8k
# Data Indices: [428, 829]

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
        Step 1: Generate multiple candidate solutions (Parallel Ensemble).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect critically on that solution to uncover hidden assumptions or errors.
        Step 4: Use the reflection to guide a new, improved solution via FlexibleCustom in iterative mode.
        """
        # --- PARALLEL ENSEMBLE ---
        solution_candidates = []
        for i in range(3):  # Generate 3 independent attempts
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Focus on identifying what is given and what needs to be found."
            )
            solution_candidates.append(candidate)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO GENERATE A BETTER SOLUTION ---
        improved_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve again with more attention to potential oversights.",
            reasoning_pattern="iterative",
            steps=["analyze", "identify_assumptions", "refine_reasoning", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return improved_solution