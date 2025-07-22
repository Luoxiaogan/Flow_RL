# Workflow ID: gsm8k_40_0
# Benchmark: gsm8k
# Data Indices: [341, 255, 611]

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
        This is a diverse and complex workflow combining:
        - Parallel Ensemble (fan-out) to generate 3 initial solutions
        - Reflect on the best solution from the ensemble
        - Regenerate using the reflection as guidance (Reflect + Custom)
        - Final Review to polish the improved solution
        """

        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_list = []
        for i in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to pick the best solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect critically on the best solution — identify flaws, assumptions, or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution based on the reflection
        improved_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Provide a revised, more accurate solution that addresses these points."
        )

        # Step 5: Final review to refine clarity, logic, and completeness
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer