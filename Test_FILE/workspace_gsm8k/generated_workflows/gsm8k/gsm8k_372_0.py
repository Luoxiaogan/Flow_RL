# Workflow ID: gsm8k_372_0
# Benchmark: gsm8k
# Data Indices: [120, 577, 875]

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
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect + Regenerate pattern to improve the best solution using meta-cognition
        3. Iterative Refinement on the regenerated solution for final polish
        """

        # Step 1: Generate 3 independent solutions via parallel ensemble
        solutions = []
        for _ in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step, focusing on clarity and logical progression."
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the best among them
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify potential flaws or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution via Custom
        improved_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, provide a new, more accurate and thorough solution that addresses all identified concerns."
        )

        # Step 5: Apply iterative refinement to polish the improved solution
        final_solution = improved_solution
        for _ in range(2):  # Two rounds of review for refinement
            revised = await self.review(pre_solution=final_solution)
            final_solution = revised

        return final_solution